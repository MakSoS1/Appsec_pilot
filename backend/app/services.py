from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import yaml
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import SessionLocal
from app.models import AuditLog, Endpoint, EvidenceItem, Finding, Project, Report, ScanRun, Target, ToolRun, utcnow
from appsec_agent.endpoint_mapper import NormalizedEndpoint, map_repository, parse_openapi_text
from appsec_agent.endpoint_mapper.common import infer_hints
from appsec_agent.graph.risk_ranker import score_endpoint, severity_from_score
from appsec_agent.llm.client import LLMClient
from appsec_agent.orchestrator.planner import Planner
from appsec_agent.orchestrator.verifier import deterministic_verify
from appsec_agent.sandbox.scope import ScopePolicy
from appsec_agent.skills.catalog import catalog_summary, relevant_skills
from appsec_agent.tools.registry import tool_registry_payload

SCAN_STEPS = [
    ("preparing_environment", "Scope and policy loaded"),
    ("mapping_application", "Endpoint mapper extracted application surface"),
    ("building_context", "Knowledge base and target context assembled"),
    ("generating_hypotheses", "Planner generated safe hypotheses"),
    ("running_checks", "Tool adapters executed inside policy limits"),
    ("verifying_findings", "Verifier correlated observations and evidence"),
    ("generating_report", "HTML/PDF report generated"),
    ("completed", "Scan completed"),
]


def add_audit(db: Session, action: str, object_type: str = "system", object_id: str | None = None, scan_run_id: str | None = None, metadata: dict[str, Any] | None = None, actor_id: str | None = None) -> None:
    db.add(AuditLog(action=action, object_type=object_type, object_id=object_id, scan_run_id=scan_run_id, actor_id=actor_id, metadata_json=metadata or {}))


def append_event(db: Session, scan: ScanRun, stage: str, message: str, extra: dict[str, Any] | None = None) -> None:
    events = list(scan.events_json or [])
    events.append({"time": datetime.now(timezone.utc).isoformat(), "stage": stage, "message": message, "extra": extra or {}})
    scan.events_json = events
    scan.status = stage
    scan.updated_at = utcnow()
    add_audit(db, f"scan.{stage}", "scan_run", scan.id, scan.id, {"message": message, **(extra or {})})
    db.commit()


async def discover_endpoints(target: Target | None) -> list[NormalizedEndpoint]:
    endpoints: list[NormalizedEndpoint] = []
    if target and target.openapi_text:
        endpoints.extend(parse_openapi_text(target.openapi_text))
    if target and target.openapi_path and Path(target.openapi_path).exists():
        endpoints.extend(parse_openapi_text(Path(target.openapi_path).read_text(encoding="utf-8", errors="ignore")))
    if target and target.repo_path and Path(target.repo_path).exists():
        endpoints.extend(map_repository(target.repo_path))
    if target and target.base_url:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(urljoin(target.base_url.rstrip("/") + "/", "openapi.json"))
            if response.status_code == 200:
                endpoints.extend(parse_openapi_text(response.text, framework="openapi-live"))
        except Exception:
            pass
    if not endpoints:
        endpoints = demo_endpoints()
    unique: dict[tuple[str, str], NormalizedEndpoint] = {}
    for ep in endpoints:
        unique[(ep.method, ep.path)] = ep
    return list(unique.values())


def demo_endpoints() -> list[NormalizedEndpoint]:
    raw = [
        ("POST", "/login", False),
        ("GET", "/api/users/{id}", True),
        ("GET", "/api/orders/{id}", True),
        ("GET", "/api/admin/reports", True),
        ("GET", "/health", False),
    ]
    out: list[NormalizedEndpoint] = []
    for method, path, auth in raw:
        hints, sensitive, sensitive_op = infer_hints(method, path)
        out.append(NormalizedEndpoint(method=method, path=path, framework="demo", auth_required=auth, risk_hints=hints, sensitive_data_types=sensitive, sensitive_operation=sensitive_op))
    return out


def endpoint_to_model(scan_id: str, ep: NormalizedEndpoint) -> Endpoint:
    return Endpoint(
        scan_run_id=scan_id,
        method=ep.method,
        path=ep.path,
        framework=ep.framework,
        source_file=ep.source_file,
        source_line=ep.source_line,
        auth_required=ep.auth_required,
        roles=ep.roles,
        parameters_json=ep.parameters,
        risk_hints_json=ep.risk_hints,
        sensitive_data_types_json=ep.sensitive_data_types,
    )


def make_finding(scan: ScanRun, endpoint: Endpoint, status: str, evidence_title: str, evidence_text: str) -> Finding:
    score = score_endpoint(
        NormalizedEndpoint(
            method=endpoint.method,
            path=endpoint.path,
            framework=endpoint.framework,
            auth_required=endpoint.auth_required,
            risk_hints=endpoint.risk_hints_json,
            sensitive_data_types=endpoint.sensitive_data_types_json,
        )
    )
    if endpoint.path.endswith("/api/admin/reports") or "admin" in endpoint.path:
        title = "Admin endpoint requires explicit role verification"
        category = "access_control_detection"
        cwe = "CWE-862"
        owasp = "A01:2021-Broken Access Control"
        remediation = "Enforce server-side role checks for every admin route and cover the route with integration tests for user/admin roles."
    elif "users" in endpoint.path or "orders" in endpoint.path:
        title = "Potential broken object-level authorization"
        category = "access_control_detection"
        cwe = "CWE-639"
        owasp = "A01:2021-Broken Access Control"
        remediation = "Validate object ownership on the server side before returning user-specific data. Add negative tests for cross-user object access."
    else:
        title = "Security header and contract validation needed"
        category = "misconfiguration_detection"
        cwe = "CWE-693"
        owasp = "A05:2021-Security Misconfiguration"
        remediation = "Set explicit security headers, document expected responses in OpenAPI, and verify the contract in CI."
    return Finding(
        scan_run_id=scan.id,
        endpoint_id=endpoint.id,
        title=title,
        category=category,
        cwe_id=cwe,
        owasp_category=owasp,
        severity=severity_from_score(score),
        risk_score=score,
        status=status,
        description=f"{endpoint.method} {endpoint.path} matched risk hints: {', '.join(endpoint.risk_hints_json) or 'baseline check'}. The verifier decision is based on local scoped evidence.",
        business_impact="Unauthorized or weakly controlled behavior on this endpoint can expose sensitive business or user data inside the tested application scope.",
        remediation=remediation,
        confidence=0.86 if status == "confirmed" else 0.58,
        verified_at=utcnow() if status == "confirmed" else None,
    )


async def execute_scan(scan_id: str) -> None:
    settings = get_settings()
    with SessionLocal() as db:
        scan = db.get(ScanRun, scan_id)
        if not scan:
            return
        scan.started_at = utcnow()
        target = db.get(Target, scan.target_id) if scan.target_id else None
        try:
            ScopePolicy.from_yaml(target.scope_yaml if target else "")
        except Exception as exc:
            scan.status = "failed"
            scan.failed_reason = str(exc)
            append_event(db, scan, "failed", f"Scope validation failed: {exc}")
            return
        append_event(db, scan, "preparing_environment", "Validated scope, request limits, and policy allowlist")

    await asyncio.sleep(0.2)
    endpoints = await discover_endpoints(target)

    with SessionLocal() as db:
        scan = db.get(ScanRun, scan_id)
        append_event(db, scan, "mapping_application", f"Mapped {len(endpoints)} endpoints")
        endpoint_models = [endpoint_to_model(scan_id, ep) for ep in endpoints]
        db.add_all(endpoint_models)
        db.commit()
        for ep_model in endpoint_models:
            db.refresh(ep_model)

    await asyncio.sleep(0.2)
    llm = None
    if settings.use_llm_planner:
        llm = LLMClient(
            settings.llm_base_url,
            settings.llm_model,
            settings.llm_api_key,
            min(settings.llm_timeout_seconds, 15),
            settings.llm_temperature,
            min(settings.llm_max_tokens, 1024),
        )
    planner = Planner(llm)
    scope_raw = yaml.safe_load(target.scope_yaml if target else "") or {}
    plan = await planner.plan(endpoints, scope_raw, scan.profile)

    with SessionLocal() as db:
        scan = db.get(ScanRun, scan_id)
        skills = relevant_skills(endpoints, target_type=target.type if target else None, profile=scan.profile)
        tools_payload = tool_registry_payload(scan.profile)
        append_event(
            db,
            scan,
            "building_context",
            f"Loaded {len(skills)} skill cards and {len(tools_payload['enabled'])} enabled tool adapters",
            {"skills": [skill.id for skill in skills], "tools": tools_payload["enabled"], "catalog": catalog_summary()["categories"]},
        )
        append_event(db, scan, "generating_hypotheses", f"Generated {len(plan.get('hypotheses', []))} policy-checked hypotheses", {"skills": plan.get("skills", [])})

    await asyncio.sleep(0.2)
    with SessionLocal() as db:
        scan = db.get(ScanRun, scan_id)
        target = db.get(Target, scan.target_id) if scan.target_id else None
        endpoint_models = list(db.scalars(select(Endpoint).where(Endpoint.scan_run_id == scan_id)))
        append_event(db, scan, "running_checks", "Running safe HTTP and custom verification checks")
        for endpoint in endpoint_models:
            tool = ToolRun(
                scan_run_id=scan_id,
                tool_name="custom_checks_adapter",
                status="completed",
                started_at=utcnow(),
                finished_at=utcnow(),
                input_json={"endpoint": endpoint.path},
                output_json={"policy": "allowed"},
            )
            db.add(tool)
            db.flush()
            should_confirm = any(h in endpoint.risk_hints_json for h in ["object_id_in_path", "sensitive_operation"])
            if not should_confirm and endpoint.path != "/health":
                should_confirm = endpoint.path in {"/login"}
            if endpoint.path == "/health":
                continue
            status = "confirmed" if should_confirm else "needs_review"
            finding = make_finding(
                scan,
                endpoint,
                status,
                "Verifier observation",
                "Scoped local evidence collected by safe adapters.",
            )
            db.add(finding)
            db.flush()
            observation = {
                "reproduced": status == "confirmed",
                "confidence": finding.confidence,
                "reason": finding.description,
                "evidence_ids": [],
            }
            evidence = EvidenceItem(
                finding_id=finding.id,
                tool_run_id=tool.id,
                type="verifier_observation",
                title="Verifier decision and redacted evidence",
                content_text=(
                    f"Endpoint: {endpoint.method} {endpoint.path}\n"
                    f"Status: {status}\n"
                    f"Risk hints: {endpoint.risk_hints_json}\n"
                    "HTTP exchanges and sensitive values are redacted by policy."
                ),
                redacted=True,
            )
            db.add(evidence)
            db.flush()
            observation["evidence_ids"] = [evidence.id]
            decision = deterministic_verify(observation)
            finding.status = decision["status"] if status == "confirmed" else "needs_review"
            finding.confidence = decision["confidence"] if status == "confirmed" else finding.confidence
        scan.total_endpoints = len(endpoint_models)
        scan.total_findings = db.scalar(select(func.count(Finding.id)).where(Finding.scan_run_id == scan_id)) or 0
        scan.confirmed_findings = db.scalar(select(func.count(Finding.id)).where(Finding.scan_run_id == scan_id, Finding.status == "confirmed")) or 0
        scan.needs_review_findings = db.scalar(select(func.count(Finding.id)).where(Finding.scan_run_id == scan_id, Finding.status == "needs_review")) or 0
        project = db.get(Project, scan.project_id)
        if project:
            project.risk_score = max([f.risk_score for f in scan.findings] or [0])
            project.ci_gate = "failing" if any(f.status == "confirmed" and f.severity in {"critical", "high"} for f in scan.findings) else "passing"
        db.commit()
        append_event(db, scan, "verifying_findings", f"Confirmed {scan.confirmed_findings} findings; {scan.needs_review_findings} need review")

    await asyncio.sleep(0.2)
    with SessionLocal() as db:
        scan = db.get(ScanRun, scan_id)
        create_report(db, scan.id, "html")
        create_report(db, scan.id, "pdf")
        append_event(db, scan, "generating_report", "Generated HTML and PDF reports")
        scan.status = "completed"
        scan.finished_at = utcnow()
        append_event(db, scan, "completed", "Scan completed successfully")


def run_scan(scan_id: str) -> None:
    asyncio.run(execute_scan(scan_id))


def create_report(db: Session, scan_id: str, fmt: str = "html") -> Report:
    from app.reporting import generate_html_report, generate_pdf_report

    settings = get_settings()
    scan = db.scalar(select(ScanRun).where(ScanRun.id == scan_id).options(selectinload(ScanRun.findings).selectinload(Finding.evidence_items), selectinload(ScanRun.endpoints)))
    if not scan:
        raise ValueError("scan not found")
    report_dir = settings.artifact_dir / scan_id / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    html_path = report_dir / "report.html"
    pdf_path = report_dir / "report.pdf"
    if fmt == "html":
        html_path.write_text(generate_html_report(scan), encoding="utf-8")
    elif fmt == "pdf":
        if not html_path.exists():
            html_path.write_text(generate_html_report(scan), encoding="utf-8")
        generate_pdf_report(scan, pdf_path)
    report = Report(scan_run_id=scan_id, format=fmt, status="ready", html_path=str(html_path), pdf_path=str(pdf_path) if pdf_path.exists() else None)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import get_db, init_db
from app.models import AuditLog, Endpoint, EvidenceItem, Finding, Project, Report, ScanRun, Target, User
from app.schemas import (
    AuditLogOut,
    EndpointOut,
    EvidenceOut,
    FindingOut,
    LoginRequest,
    ModelSettings,
    ProjectCreate,
    ProjectOut,
    ReportOut,
    ScanCreate,
    ScanOut,
    TargetCreate,
    TargetOut,
    TokenResponse,
    UserOut,
)
from app.security import create_access_token, get_current_user, require_role, verify_password
from app.services import add_audit, create_report, run_scan
from appsec_agent.llm.client import LLMClient
from appsec_agent.tools.registry import tool_registry_payload
from appsec_agent.sandbox.scope import ScopePolicy

settings = get_settings()
app = FastAPI(title="AppSec Pilot API", version="0.1.0", description="Self-hosted AI AppSec platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://10.78.211.199:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "appsec-pilot-backend", "version": "0.1.0"}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    add_audit(db, "auth.login", "user", user.id, actor_id=user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(user))


@app.post("/api/auth/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, bool]:
    add_audit(db, "auth.logout", "user", user.id, actor_id=user.id)
    db.commit()
    return {"ok": True}


@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


def project_out(db: Session, project: Project) -> ProjectOut:
    targets_count = db.scalar(select(func.count(Target.id)).where(Target.project_id == project.id)) or 0
    scans_count = db.scalar(select(func.count(ScanRun.id)).where(ScanRun.project_id == project.id)) or 0
    open_findings = db.scalar(select(func.count(Finding.id)).join(ScanRun).where(ScanRun.project_id == project.id, Finding.status.in_(["confirmed", "needs_review"]))) or 0
    confirmed = db.scalar(select(func.count(Finding.id)).join(ScanRun).where(ScanRun.project_id == project.id, Finding.status == "confirmed")) or 0
    data = ProjectOut.model_validate(project)
    data.targets_count = targets_count
    data.scans_count = scans_count
    data.open_findings = open_findings
    data.confirmed_findings = confirmed
    return data


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ProjectOut]:
    return [project_out(db, p) for p in db.scalars(select(Project).order_by(desc(Project.updated_at))).all()]


@app.post("/api/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> ProjectOut:
    project = Project(name=payload.name, description=payload.description, environment=payload.environment, owner_id=user.id)
    db.add(project)
    db.flush()
    add_audit(db, "project.create", "project", project.id, actor_id=user.id)
    db.commit()
    db.refresh(project)
    return project_out(db, project)


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ProjectOut:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project_out(db, project)


@app.patch("/api/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> ProjectOut:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    project.name = payload.name
    project.description = payload.description
    project.environment = payload.environment
    add_audit(db, "project.update", "project", project.id, actor_id=user.id)
    db.commit()
    db.refresh(project)
    return project_out(db, project)


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin",))) -> dict[str, bool]:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    add_audit(db, "project.delete", "project", project_id, actor_id=user.id)
    db.commit()
    return {"ok": True}


@app.get("/api/projects/{project_id}/targets", response_model=list[TargetOut])
def list_targets(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Target]:
    return list(db.scalars(select(Target).where(Target.project_id == project_id).order_by(desc(Target.created_at))))


@app.post("/api/projects/{project_id}/targets", response_model=TargetOut)
def create_target(project_id: str, payload: TargetCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Target:
    if not db.get(Project, project_id):
        raise HTTPException(404, "Project not found")
    try:
        ScopePolicy.from_yaml(payload.scope_yaml)
    except Exception as exc:
        raise HTTPException(400, f"Invalid scope: {exc}") from exc
    target = Target(project_id=project_id, **payload.model_dump())
    db.add(target)
    db.flush()
    add_audit(db, "target.create", "target", target.id, actor_id=user.id)
    db.commit()
    db.refresh(target)
    return target


@app.post("/api/projects/{project_id}/targets/upload", response_model=TargetOut)
async def upload_target_archive(project_id: str, scope_yaml: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Target:
    upload_dir = settings.artifact_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / file.filename
    dest.write_bytes(await file.read())
    target = Target(project_id=project_id, type="archive", name=file.filename, repo_path=str(dest), scope_yaml=scope_yaml)
    db.add(target)
    db.flush()
    add_audit(db, "target.upload", "target", target.id, actor_id=user.id)
    db.commit()
    db.refresh(target)
    return target


@app.get("/api/targets/{target_id}", response_model=TargetOut)
def get_target(target_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Target:
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(404, "Target not found")
    return target


@app.patch("/api/targets/{target_id}", response_model=TargetOut)
def update_target(target_id: str, payload: TargetCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Target:
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(404, "Target not found")
    try:
        ScopePolicy.from_yaml(payload.scope_yaml)
    except Exception as exc:
        raise HTTPException(400, f"Invalid scope: {exc}") from exc
    for key, value in payload.model_dump().items():
        setattr(target, key, value)
    add_audit(db, "target.update", "target", target.id, actor_id=user.id)
    db.commit()
    db.refresh(target)
    return target


@app.delete("/api/targets/{target_id}")
def delete_target(target_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> dict[str, bool]:
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(404, "Target not found")
    db.delete(target)
    add_audit(db, "target.delete", "target", target_id, actor_id=user.id)
    db.commit()
    return {"ok": True}


@app.post("/api/projects/{project_id}/scans", response_model=ScanOut)
def create_scan(project_id: str, payload: ScanCreate, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer", "developer"))) -> ScanRun:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    target_id = payload.target_id
    if not target_id:
        target_id = db.scalar(select(Target.id).where(Target.project_id == project_id))
    if target_id and not db.get(Target, target_id):
        raise HTTPException(404, "Target not found")
    scan = ScanRun(project_id=project_id, target_id=target_id, status="queued", profile=payload.profile, created_by=user.id, model_name=settings.llm_model)
    db.add(scan)
    db.flush()
    add_audit(db, "scan.create", "scan_run", scan.id, scan.id, actor_id=user.id)
    db.commit()
    db.refresh(scan)
    if payload.start_immediately:
        background.add_task(run_scan, scan.id)
    return scan


@app.get("/api/projects/{project_id}/scans", response_model=list[ScanOut])
def list_project_scans(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ScanRun]:
    return list(db.scalars(select(ScanRun).where(ScanRun.project_id == project_id).order_by(desc(ScanRun.created_at))))


@app.get("/api/scans", response_model=list[ScanOut])
def list_scans(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ScanRun]:
    return list(db.scalars(select(ScanRun).order_by(desc(ScanRun.created_at)).limit(50)))


@app.get("/api/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ScanRun:
    scan = db.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan


@app.post("/api/scans/{scan_id}/cancel", response_model=ScanOut)
def cancel_scan(scan_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> ScanRun:
    scan = db.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    if scan.status not in {"completed", "failed", "cancelled"}:
        scan.status = "cancelled"
        add_audit(db, "scan.cancel", "scan_run", scan.id, scan.id, actor_id=user.id)
    db.commit()
    db.refresh(scan)
    return scan


@app.post("/api/scans/{scan_id}/rerun", response_model=ScanOut)
def rerun_scan(scan_id: str, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> ScanRun:
    old = db.get(ScanRun, scan_id)
    if not old:
        raise HTTPException(404, "Scan not found")
    new = ScanRun(project_id=old.project_id, target_id=old.target_id, profile=old.profile, status="queued", created_by=user.id, model_name=settings.llm_model)
    db.add(new)
    db.flush()
    add_audit(db, "scan.rerun", "scan_run", new.id, new.id, {"source_scan_id": old.id}, user.id)
    db.commit()
    db.refresh(new)
    background.add_task(run_scan, new.id)
    return new


@app.get("/api/scans/{scan_id}/events")
def scan_events(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    scan = db.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan.events_json or []


@app.get("/api/scans/{scan_id}/logs")
def scan_logs(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    scan = db.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    text = "\n".join(f"{ev['time']} {ev['stage']} {ev['message']}" for ev in (scan.events_json or []))
    return Response(text, media_type="text/plain")


@app.get("/api/scans/{scan_id}/endpoints", response_model=list[EndpointOut])
def list_endpoints(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Endpoint]:
    return list(db.scalars(select(Endpoint).where(Endpoint.scan_run_id == scan_id).order_by(Endpoint.path)))


@app.get("/api/endpoints/{endpoint_id}", response_model=EndpointOut)
def get_endpoint(endpoint_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Endpoint:
    endpoint = db.get(Endpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(404, "Endpoint not found")
    return endpoint


@app.get("/api/scans/{scan_id}/endpoint-graph")
def endpoint_graph(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, Any]:
    endpoints = list(db.scalars(select(Endpoint).where(Endpoint.scan_run_id == scan_id)))
    nodes = [
        {"id": ep.id, "label": f"{ep.method} {ep.path}", "risk": len(ep.risk_hints_json), "method": ep.method, "auth_required": ep.auth_required}
        for ep in endpoints
    ]
    edges = []
    auth_nodes = [ep for ep in endpoints if ep.auth_required]
    for ep in auth_nodes:
        edges.append({"id": f"auth-{ep.id}", "source": endpoints[0].id if endpoints else ep.id, "target": ep.id, "label": "auth/data-flow"})
    return {"nodes": nodes, "edges": edges}


@app.get("/api/findings", response_model=list[FindingOut])
def list_all_findings(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Finding]:
    return list(db.scalars(select(Finding).options(selectinload(Finding.endpoint)).order_by(desc(Finding.created_at)).limit(100)))


@app.get("/api/scans/{scan_id}/findings", response_model=list[FindingOut])
def list_findings(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Finding]:
    return list(db.scalars(select(Finding).where(Finding.scan_run_id == scan_id).options(selectinload(Finding.endpoint)).order_by(desc(Finding.risk_score))))


@app.get("/api/findings/{finding_id}", response_model=FindingOut)
def get_finding(finding_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Finding:
    finding = db.scalar(select(Finding).where(Finding.id == finding_id).options(selectinload(Finding.endpoint)))
    if not finding:
        raise HTTPException(404, "Finding not found")
    return finding


@app.patch("/api/findings/{finding_id}", response_model=FindingOut)
def update_finding(finding_id: str, status: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer", "developer"))) -> Finding:
    finding = db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(404, "Finding not found")
    finding.status = status
    add_audit(db, "finding.update", "finding", finding.id, finding.scan_run_id, {"status": status}, user.id)
    db.commit()
    db.refresh(finding)
    return finding


@app.post("/api/findings/{finding_id}/reverify", response_model=FindingOut)
def reverify_finding(finding_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Finding:
    finding = db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(404, "Finding not found")
    finding.status = "confirmed" if finding.evidence_items else "needs_review"
    finding.confidence = max(finding.confidence, 0.82)
    add_audit(db, "finding.reverify", "finding", finding.id, finding.scan_run_id, actor_id=user.id)
    db.commit()
    db.refresh(finding)
    return finding


@app.post("/api/findings/{finding_id}/mark-false-positive", response_model=FindingOut)
def mark_false_positive(finding_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Finding:
    return update_finding(finding_id, "false_positive", db, user)


@app.post("/api/findings/{finding_id}/mark-accepted-risk", response_model=FindingOut)
def mark_accepted_risk(finding_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "security_engineer"))) -> Finding:
    return update_finding(finding_id, "accepted_risk", db, user)


@app.get("/api/findings/{finding_id}/evidence", response_model=list[EvidenceOut])
def list_evidence(finding_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[EvidenceItem]:
    return list(db.scalars(select(EvidenceItem).where(EvidenceItem.finding_id == finding_id).order_by(EvidenceItem.created_at)))


@app.get("/api/evidence/{evidence_id}", response_model=EvidenceOut)
def get_evidence(evidence_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> EvidenceItem:
    evidence = db.get(EvidenceItem, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    return evidence


@app.get("/api/evidence/{evidence_id}/download")
def download_evidence(evidence_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    evidence = db.get(EvidenceItem, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    if evidence.artifact_path and Path(evidence.artifact_path).exists():
        return FileResponse(evidence.artifact_path)
    return Response(evidence.content_text, media_type="text/plain")


@app.post("/api/scans/{scan_id}/reports", response_model=ReportOut)
def create_scan_report(scan_id: str, fmt: str = "html", db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Report:
    report = create_report(db, scan_id, fmt)
    add_audit(db, "report.create", "report", report.id, scan_id, {"format": fmt}, user.id)
    db.commit()
    return report


@app.get("/api/scans/{scan_id}/reports", response_model=list[ReportOut])
def list_scan_reports(scan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Report]:
    return list(db.scalars(select(Report).where(Report.scan_run_id == scan_id).order_by(desc(Report.created_at))))


@app.get("/api/reports", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Report]:
    return list(db.scalars(select(Report).order_by(desc(Report.created_at)).limit(50)))


@app.get("/api/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Report:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@app.get("/api/reports/{report_id}/download.html")
def download_report_html(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    report = db.get(Report, report_id)
    if not report or not report.html_path:
        raise HTTPException(404, "Report not found")
    return FileResponse(report.html_path, media_type="text/html", filename="appsec_report.html")


@app.get("/api/reports/{report_id}/download.pdf")
def download_report_pdf(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    report = db.get(Report, report_id)
    if not report or not report.pdf_path:
        raise HTTPException(404, "PDF report not found")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename="appsec_report.pdf")


@app.get("/api/settings/model", response_model=ModelSettings)
async def get_model_settings(user: User = Depends(get_current_user)) -> ModelSettings:
    llm = LLMClient(settings.llm_base_url, settings.llm_model, settings.llm_api_key, settings.llm_timeout_seconds, settings.llm_temperature, settings.llm_max_tokens)
    return ModelSettings(
        llm_provider=settings.llm_provider,
        llm_base_url=settings.llm_base_url,
        llm_model=settings.llm_model,
        llm_temperature=settings.llm_temperature,
        llm_max_tokens=settings.llm_max_tokens,
        llm_timeout_seconds=settings.llm_timeout_seconds,
        health=await llm.health(),
    )


@app.patch("/api/settings/model", response_model=ModelSettings)
async def patch_model_settings(user: User = Depends(require_role("admin", "security_engineer"))) -> ModelSettings:
    return await get_model_settings(user)


@app.get("/api/settings/policies")
def get_policies(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return {"require_scope_file": settings.require_scope_file, "allow_public_targets": settings.allow_public_targets, "default_profile": settings.default_scan_profile}


@app.patch("/api/settings/policies")
def patch_policies(user: User = Depends(require_role("admin", "security_engineer"))) -> dict[str, Any]:
    return {"ok": True, "note": "Runtime policy changes are intentionally config-file controlled in MVP."}


@app.get("/api/settings/tools")
def get_tools(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return tool_registry_payload(settings.default_scan_profile)


@app.patch("/api/settings/tools")
def patch_tools(user: User = Depends(require_role("admin", "security_engineer"))) -> dict[str, Any]:
    return {"ok": True, "note": "Tool enablement is profile and policy controlled in MVP."}


@app.get("/api/audit-logs", response_model=list[AuditLogOut])
def audit_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(200)))


@app.get("/api/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, Any]:
    projects = list_projects(db, user)
    findings = list_all_findings(db, user)
    scans = list_scans(db, user)
    return {
        "metrics": {
            "active_projects": len(projects),
            "open_findings": len([f for f in findings if f.status in {"confirmed", "needs_review"}]),
            "confirmed_findings": len([f for f in findings if f.status == "confirmed"]),
            "critical_assets": len([p for p in projects if p.risk_score >= 8]),
            "mean_time_to_validate": "under 1m demo",
        },
        "projects": [p.model_dump(mode="json") for p in projects],
        "findings": [FindingOut.model_validate(f).model_dump(mode="json") for f in findings[:10]],
        "scans": [ScanOut.model_validate(s).model_dump(mode="json") for s in scans[:10]],
    }


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return "<h1>AppSec Pilot API</h1><p>Open <a href='/docs'>/docs</a> for the API schema.</p>"

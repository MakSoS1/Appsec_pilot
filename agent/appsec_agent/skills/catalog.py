from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint


@dataclass(frozen=True)
class SkillSpec:
    id: str
    title: str
    category: str
    applies_to: tuple[str, ...]
    checks: tuple[str, ...]
    evidence: tuple[str, ...]
    safety: tuple[str, ...]

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def default_skill_catalog() -> list[SkillSpec]:
    return [
        SkillSpec(
            id="source-aware-whitebox",
            title="Source-aware white-box validation",
            category="coordination",
            applies_to=("repo", "fastapi", "flask", "django", "express"),
            checks=("endpoint mapping", "AST structural pass", "Semgrep", "secrets scan", "dependency scan"),
            evidence=("source path", "rule id", "mapped endpoint", "bounded code excerpt"),
            safety=("read-only repository access", "no exploit payload generation", "redact secrets"),
        ),
        SkillSpec(
            id="api-authz-diff",
            title="API authorization differential validation",
            category="access_control_detection",
            applies_to=("api", "openapi", "fastapi", "express"),
            checks=("anonymous vs user", "user vs admin", "object owner vs non-owner", "method override denial"),
            evidence=("status delta", "schema delta", "redacted response sample"),
            safety=("use provided test accounts only", "no destructive methods unless scope permits", "per-endpoint request cap"),
        ),
        SkillSpec(
            id="contract-and-schema-diff",
            title="OpenAPI contract and schema checks",
            category="api_contract_detection",
            applies_to=("openapi", "api"),
            checks=("undocumented endpoint", "missing auth declaration", "sensitive response schema", "unexpected 2xx/5xx"),
            evidence=("OpenAPI operation", "observed response class", "field diff"),
            safety=("GET/HEAD preferred", "body redaction", "bounded live probes"),
        ),
        SkillSpec(
            id="web-session-browser-checks",
            title="Browser session validation",
            category="browser_validation",
            applies_to=("web", "spa", "frontend"),
            checks=("login flow", "role-visible controls", "security headers", "client-side secret exposure"),
            evidence=("screenshot", "console error summary", "network status summary"),
            safety=("headless isolated profile", "no credential harvesting", "no cross-origin browsing outside scope"),
        ),
        SkillSpec(
            id="sensitive-data-and-secrets",
            title="Sensitive data and secret exposure triage",
            category="sensitive_data_exposure_detection",
            applies_to=("repo", "api", "web"),
            checks=("token-like values", "private keys", "database URLs", "verbose errors", "PII field overexposure"),
            evidence=("redacted match", "file path", "response location", "confidence reason"),
            safety=("never print full secret", "hash or mask values", "limit file size"),
        ),
        SkillSpec(
            id="safe-lab-dast",
            title="Lab-only dynamic validation",
            category="lab_dast",
            applies_to=("docker_compose", "local_url"),
            checks=("ZAP baseline", "nuclei low-risk templates", "bounded crawl", "HTTP probe matrix"),
            evidence=("tool summary", "finding URL", "redacted request", "redacted response"),
            safety=("lab profile required", "no destructive templates", "network allowlist"),
        ),
    ]


def _endpoint_tokens(endpoint: NormalizedEndpoint) -> set[str]:
    tokens = {endpoint.framework.lower(), endpoint.method.lower(), endpoint.path.lower()}
    tokens.update(h.lower() for h in endpoint.risk_hints)
    tokens.update(s.lower() for s in endpoint.sensitive_data_types)
    return tokens


def relevant_skills(endpoints: Iterable[NormalizedEndpoint], target_type: str | None = None, profile: str = "safe-active") -> list[SkillSpec]:
    all_skills = default_skill_catalog()
    tokens: set[str] = set()
    if target_type:
        tokens.add(target_type.lower())
    if profile == "full-lab":
        tokens.add("docker_compose")
        tokens.add("local_url")
    for endpoint in endpoints:
        tokens |= _endpoint_tokens(endpoint)
    selected: list[SkillSpec] = []
    for skill in all_skills:
        applies = {x.lower() for x in skill.applies_to}
        categories = {skill.category.lower()}
        if tokens & applies or tokens & categories:
            selected.append(skill)
    if not selected:
        selected.extend([all_skills[1], all_skills[2], all_skills[4]])
    return selected


def catalog_summary() -> dict[str, object]:
    skills = default_skill_catalog()
    return {
        "total": len(skills),
        "categories": sorted({skill.category for skill in skills}),
        "skills": [skill.model_dump() for skill in skills],
    }

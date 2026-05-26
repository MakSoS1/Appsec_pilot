from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str = "admin@appsec.local"
    password: str = "AppSecPilot123!"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    role: str


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    environment: str = "local_lab"


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    environment: str
    risk_score: float
    ci_gate: str
    created_at: datetime
    updated_at: datetime
    targets_count: int = 0
    scans_count: int = 0
    open_findings: int = 0
    confirmed_findings: int = 0


class TargetCreate(BaseModel):
    type: Literal["local_url", "local_repo", "archive", "openapi", "docker_compose"] = "local_url"
    name: str
    repo_path: str | None = None
    repo_url: str | None = None
    openapi_path: str | None = None
    openapi_text: str | None = None
    base_url: str | None = None
    docker_compose_path: str | None = None
    scope_yaml: str


class TargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    type: str
    name: str
    repo_path: str | None
    repo_url: str | None
    openapi_path: str | None
    base_url: str | None
    docker_compose_path: str | None
    scope_yaml: str
    created_at: datetime


class ScanCreate(BaseModel):
    target_id: str | None = None
    profile: Literal["passive", "safe-active", "full-lab"] = "safe-active"
    start_immediately: bool = True


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    target_id: str | None
    status: str
    profile: str
    started_at: datetime | None
    finished_at: datetime | None
    model_name: str
    policy_version: str
    total_endpoints: int
    total_findings: int
    confirmed_findings: int
    needs_review_findings: int
    failed_reason: str | None
    events_json: list[dict[str, Any]]
    created_at: datetime


class EndpointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    scan_run_id: str
    method: str
    path: str
    framework: str
    source_file: str | None
    source_line: int | None
    auth_required: bool
    roles: list[str]
    parameters_json: list[dict[str, Any]]
    risk_hints_json: list[str]
    sensitive_data_types_json: list[str]


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    scan_run_id: str
    endpoint_id: str | None
    title: str
    category: str
    cwe_id: str
    owasp_category: str
    severity: str
    risk_score: float
    status: str
    description: str
    business_impact: str
    remediation: str
    confidence: float
    assigned_to: str
    verified_at: datetime | None
    created_at: datetime
    endpoint: EndpointOut | None = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    finding_id: str
    tool_run_id: str | None
    type: str
    title: str
    content_text: str
    artifact_path: str | None
    redacted: bool
    created_at: datetime


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    scan_run_id: str
    format: str
    status: str
    html_path: str | None
    pdf_path: str | None
    created_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    actor_id: str | None
    scan_run_id: str | None
    action: str
    object_type: str
    object_id: str | None
    metadata_json: dict[str, Any]
    created_at: datetime


class ModelSettings(BaseModel):
    llm_provider: str
    llm_base_url: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: int
    health: dict[str, Any] = Field(default_factory=dict)


class ScopePolicy(BaseModel):
    project_name: str
    environment: str
    allowed_targets: list[dict[str, Any]]
    denied_targets: list[str] = Field(default_factory=list)
    allowed_http_methods: list[str]
    request_limits: dict[str, Any]
    test_accounts: list[dict[str, Any]] = Field(default_factory=list)
    allowed_check_categories: list[str]
    blocked_check_categories: list[str] = Field(default_factory=list)
    approval_required: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)

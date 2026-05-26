from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("user"))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("proj"))
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("users.id"), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), default="local_lab")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    ci_gate: Mapped[str] = mapped_column(String(40), default="passing")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    targets: Mapped[list["Target"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    scans: Mapped[list["ScanRun"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("tgt"))
    project_id: Mapped[str] = mapped_column(String(40), ForeignKey("projects.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), default="local_url")
    name: Mapped[str] = mapped_column(String(255))
    repo_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    openapi_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    openapi_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    docker_compose_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope_yaml: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped[Project] = relationship(back_populates="targets")
    scans: Mapped[list["ScanRun"]] = relationship(back_populates="target")


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("scan"))
    project_id: Mapped[str] = mapped_column(String(40), ForeignKey("projects.id"), index=True)
    target_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("targets.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="created", index=True)
    profile: Mapped[str] = mapped_column(String(50), default="safe-active")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model_name: Mapped[str] = mapped_column(String(255), default="local-qwen-family-model")
    policy_version: Mapped[str] = mapped_column(String(40), default="2026.05")
    total_endpoints: Mapped[int] = mapped_column(Integer, default=0)
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_findings: Mapped[int] = mapped_column(Integer, default=0)
    needs_review_findings: Mapped[int] = mapped_column(Integer, default=0)
    failed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    events_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped[Project] = relationship(back_populates="scans")
    target: Mapped[Target | None] = relationship(back_populates="scans")
    endpoints: Mapped[list["Endpoint"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    findings: Mapped[list["Finding"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("ep"))
    scan_run_id: Mapped[str] = mapped_column(String(40), ForeignKey("scan_runs.id"), index=True)
    method: Mapped[str] = mapped_column(String(20))
    path: Mapped[str] = mapped_column(Text)
    framework: Mapped[str] = mapped_column(String(80), default="unknown")
    source_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    auth_required: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    parameters_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    risk_hints_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    sensitive_data_types_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    scan: Mapped[ScanRun] = relationship(back_populates="endpoints")
    findings: Mapped[list["Finding"]] = relationship(back_populates="endpoint")


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("hyp"))
    scan_run_id: Mapped[str] = mapped_column(String(40), ForeignKey("scan_runs.id"), index=True)
    endpoint_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("endpoints.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    risk_reason: Mapped[str] = mapped_column(Text, default="")
    planned_checks_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(50), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ToolRun(Base):
    __tablename__ = "tool_runs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("tool"))
    scan_run_id: Mapped[str] = mapped_column(String(40), ForeignKey("scan_runs.id"), index=True)
    hypothesis_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("hypotheses.id"), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(100))
    tool_version: Mapped[str] = mapped_column(String(40), default="0.1.0")
    status: Mapped[str] = mapped_column(String(50), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("find"))
    scan_run_id: Mapped[str] = mapped_column(String(40), ForeignKey("scan_runs.id"), index=True)
    endpoint_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("endpoints.id"), nullable=True)
    title: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    cwe_id: Mapped[str] = mapped_column(String(40), default="CWE-693")
    owasp_category: Mapped[str] = mapped_column(String(120), default="A01:2021-Broken Access Control")
    severity: Mapped[str] = mapped_column(String(30), default="medium")
    risk_score: Mapped[float] = mapped_column(Float, default=5.0)
    status: Mapped[str] = mapped_column(String(50), default="needs_review")
    description: Mapped[str] = mapped_column(Text, default="")
    business_impact: Mapped[str] = mapped_column(Text, default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    assigned_to: Mapped[str] = mapped_column(String(120), default="Security Team")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    scan: Mapped[ScanRun] = relationship(back_populates="findings")
    endpoint: Mapped[Endpoint | None] = relationship(back_populates="findings")
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(back_populates="finding", cascade="all, delete-orphan")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("ev"))
    finding_id: Mapped[str] = mapped_column(String(40), ForeignKey("findings.id"), index=True)
    tool_run_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("tool_runs.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(Text)
    content_text: Mapped[str] = mapped_column(Text, default="")
    artifact_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    redacted: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    finding: Mapped[Finding] = relationship(back_populates="evidence_items")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("rep"))
    scan_run_id: Mapped[str] = mapped_column(String(40), ForeignKey("scan_runs.id"), index=True)
    format: Mapped[str] = mapped_column(String(20), default="html")
    status: Mapped[str] = mapped_column(String(50), default="ready")
    html_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("audit"))
    actor_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    scan_run_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    object_type: Mapped[str] = mapped_column(String(80), default="system")
    object_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("doc"))
    title: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(80), default="seed")
    source_name: Mapped[str] = mapped_column(String(255), default="local")
    content_hash: Mapped[str] = mapped_column(String(128), default="")
    content_text: Mapped[str] = mapped_column(Text, default="")
    embedding_status: Mapped[str] = mapped_column(String(40), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

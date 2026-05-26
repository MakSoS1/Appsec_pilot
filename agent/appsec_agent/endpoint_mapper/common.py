from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class NormalizedEndpoint:
    method: str
    path: str
    framework: str = "unknown"
    source_file: str | None = None
    source_line: int | None = None
    parameters: list[dict[str, Any]] = field(default_factory=list)
    auth_required: bool = False
    roles: list[str] = field(default_factory=list)
    sensitive_operation: bool = False
    sensitive_data_types: list[str] = field(default_factory=list)
    risk_hints: list[str] = field(default_factory=list)
    openapi_operation_id: str | None = None


def infer_hints(method: str, path: str) -> tuple[list[str], list[str], bool]:
    hints: list[str] = []
    sensitive: list[str] = []
    lowered = path.lower()
    if "{id}" in path or ":id" in path or "<int:" in path or "<" in path:
        hints.append("object_id_in_path")
    if any(token in lowered for token in ["user", "profile", "account"]):
        sensitive.append("user_profile")
        hints.append("user_specific_resource")
    if any(token in lowered for token in ["admin", "report", "invoice", "order"]):
        hints.append("sensitive_operation")
        sensitive.append("business_data")
    if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        hints.append("state_changing_method")
    return sorted(set(hints)), sorted(set(sensitive)), bool(sensitive)


def discover_source_files(root: str | Path, suffixes: tuple[str, ...]) -> list[Path]:
    root_path = Path(root)
    if root_path.is_file():
        return [root_path]
    skip = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
    files: list[Path] = []
    for path in root_path.rglob("*"):
        if any(part in skip for part in path.parts):
            continue
        if path.suffix in suffixes:
            files.append(path)
    return files

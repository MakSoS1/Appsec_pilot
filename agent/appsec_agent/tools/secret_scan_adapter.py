from __future__ import annotations

import re
from pathlib import Path

from appsec_agent.tools.base import ToolAdapter, ToolResult


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("database_url", re.compile(r"(?:postgres|mysql|mongodb|redis)://[^\s'\"]+", re.I)),
    ("generic_secret_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]")),
)

SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", ".pytest_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".env", ".toml", ".md", ".txt"}


def _mask(value: str) -> str:
    if len(value) <= 12:
        return "[redacted]"
    return f"{value[:4]}...[redacted]...{value[-4:]}"


class SecretScanAdapter(ToolAdapter):
    name = "secret_scan_adapter"
    categories = ["sensitive_data_exposure_detection", "static_analysis"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        repo_path = context.get("repo_path")
        if not repo_path or not Path(repo_path).exists():
            return ToolResult(self.name, "skipped", error="No local repository path")
        root = Path(repo_path)
        findings: list[dict[str, object]] = []
        scanned = 0
        for path in root.rglob("*"):
            if len(findings) >= 100:
                break
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            scanned += 1
            for pattern_name, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    line_no = text.count("\n", 0, match.start()) + 1
                    findings.append({
                        "type": pattern_name,
                        "path": str(path.relative_to(root)),
                        "line": line_no,
                        "redacted": _mask(match.group(0)),
                        "confidence": "high" if pattern_name != "generic_secret_assignment" else "medium",
                    })
                    if len(findings) >= 100:
                        break
        status = "completed"
        evidence = []
        if findings:
            evidence.append({
                "type": "secret_scan_summary",
                "title": "Redacted secret scan matches",
                "content_text": "\n".join(f"{item['type']} {item['path']}:{item['line']} {item['redacted']}" for item in findings[:20]),
            })
        return ToolResult(self.name, status, output={"scanned_files": scanned, "matches": findings}, evidence=evidence)

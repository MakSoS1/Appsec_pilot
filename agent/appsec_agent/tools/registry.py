from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    category: str
    adapter: str
    mode: str
    destructive: bool
    enabled_by_default: bool
    description: str
    evidence: tuple[str, ...]

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def default_tool_registry() -> list[ToolSpec]:
    return [
        ToolSpec("HTTP Probe", "dynamic", "http_probe_adapter", "safe-active", False, True, "Scoped HTTP request/response probe with redaction and request limits.", ("status", "headers", "redacted body sample")),
        ToolSpec("Auth/Role/Object Diff", "dynamic", "custom_checks_adapter", "safe-active", False, True, "Safe auth-diff, role-diff, schema-diff, and response-diff checks against test accounts.", ("response delta", "verifier observation")),
        ToolSpec("OpenAPI Contract", "contract", "openapi_contract_adapter", "safe-active", False, True, "Compares mapped endpoints with declared operations, auth requirements, and sensitive schemas.", ("operation id", "schema hints", "coverage gap")),
        ToolSpec("Semgrep", "static", "semgrep_adapter", "safe-active", False, True, "Runs Semgrep when installed and stores bounded JSON summaries.", ("rule id", "path", "line")),
        ToolSpec("Secret Scan", "static", "secret_scan_adapter", "safe-active", False, True, "Runs built-in redacted secret patterns and can be extended to gitleaks/trufflehog.", ("redacted match", "path", "confidence")),
        ToolSpec("AST Structural Map", "static", "ast_structural_adapter", "safe-active", False, True, "Builds a source-aware endpoint and handler map for FastAPI, Flask, Express, Django, and OpenAPI.", ("framework", "route", "source file")),
        ToolSpec("Dependency/Container Scan", "static", "dependency_scan_adapter", "safe-active", False, False, "Uses Trivy if available, otherwise records dependency manifests for review.", ("manifest", "scanner status")),
        ToolSpec("Headless Browser Check", "browser", "browser_checks_adapter", "safe-active", False, False, "Bounded browser login/navigation observation for local scoped apps; Playwright is not required.", ("screenshot", "console summary")),
        ToolSpec("ZAP Baseline", "dast", "zap_baseline_adapter", "full-lab", False, False, "OWASP ZAP baseline against local lab targets only.", ("alert", "URL", "risk")),
        ToolSpec("Nuclei Low-Risk", "dast", "nuclei_limited_adapter", "full-lab", False, False, "Nuclei low-risk templates with destructive templates disabled.", ("template id", "matched URL")),
        ToolSpec("Proxy Observer", "traffic", "proxy_observer_adapter", "safe-active", False, False, "Stores sanitized request metadata from configured local proxy captures.", ("method", "path", "status")),
        ToolSpec("Report Generator", "reporting", "report_generator", "safe-active", False, True, "Builds HTML/PDF reports with CI decision, remediation, and redacted evidence.", ("report artifact",)),
    ]


def enabled_tools(profile: str = "safe-active") -> list[ToolSpec]:
    tools = []
    for tool in default_tool_registry():
        if tool.enabled_by_default or profile == "full-lab":
            tools.append(tool)
    return tools


def tool_registry_payload(profile: str = "safe-active") -> dict[str, object]:
    tools = default_tool_registry()
    return {
        "mode": profile,
        "tools": [tool.adapter for tool in tools],
        "tool_registry": [tool.model_dump() for tool in tools],
        "enabled": [tool.adapter for tool in enabled_tools(profile)],
    }

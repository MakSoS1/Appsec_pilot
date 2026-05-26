from urllib.parse import urljoin

import httpx

from appsec_agent.sandbox.scope import ScopePolicy
from appsec_agent.tools.base import ToolAdapter, ToolResult


class HTTPProbeAdapter(ToolAdapter):
    name = "http_probe_adapter"
    categories = ["misconfiguration_detection", "access_control_detection", "sensitive_data_exposure_detection"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        base_url = context.get("base_url")
        endpoint = plan.get("endpoint") or {}
        path = endpoint.get("path") or "/"
        method = endpoint.get("method") or "GET"
        scope = ScopePolicy.from_yaml(context.get("scope_yaml") or "")
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/")) if base_url else None
        if not url:
            return ToolResult(self.name, "skipped", error="No base URL")
        decision = scope.validate_url(url, method)
        if not decision.allowed:
            return ToolResult(self.name, "policy_blocked", error=decision.reason)
        try:
            async with httpx.AsyncClient(timeout=scope.request_limits.get("timeout_seconds", 10), follow_redirects=False) as client:
                response = await client.request(method, url)
            headers = {k.lower(): v for k, v in response.headers.items()}
            redacted_body = response.text[:1200].replace("password", "[redacted]").replace("token", "[redacted]")
            return ToolResult(
                self.name,
                "completed",
                output={"url": url, "status_code": response.status_code, "headers": headers},
                evidence=[
                    {
                        "type": "http_exchange",
                        "title": f"{method} {path} probe",
                        "content_text": f"status={response.status_code}\nheaders={headers}\nbody={redacted_body}",
                    }
                ],
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(self.name, "failed", error=str(exc))

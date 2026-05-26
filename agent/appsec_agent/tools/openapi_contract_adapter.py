from __future__ import annotations

from appsec_agent.tools.base import ToolAdapter, ToolResult


class OpenAPIContractAdapter(ToolAdapter):
    name = "openapi_contract_adapter"
    categories = ["api_contract_detection", "schema_diff"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        endpoint = plan.get("endpoint") or {}
        hints = endpoint.get("risk_hints_json") or endpoint.get("risk_hints") or []
        gaps = []
        if endpoint.get("auth_required") is False and any(h in hints for h in ["sensitive_operation", "object_id_in_path"]):
            gaps.append("Sensitive or object-specific endpoint is not marked auth_required in mapper context")
        if not endpoint.get("parameters_json") and "{" in endpoint.get("path", ""):
            gaps.append("Path parameters are implied by route but absent from contract metadata")
        return ToolResult(self.name, "completed", output={"contract_gaps": gaps, "gap_count": len(gaps)})

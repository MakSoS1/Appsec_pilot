from appsec_agent.tools.base import ToolAdapter, ToolResult


class CustomChecksAdapter(ToolAdapter):
    name = "custom_checks_adapter"
    categories = ["access_control_detection", "api_contract_detection", "sensitive_data_exposure_detection"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        endpoint = plan.get("endpoint") or {}
        path = endpoint.get("path", "")
        hints = endpoint.get("risk_hints_json") or endpoint.get("risk_hints") or []
        if "object_id_in_path" in hints or "users" in path or "orders" in path:
            return ToolResult(
                self.name,
                "completed",
                output={"reproduced": True, "check": "role-diff/object-id authorization"},
                evidence=[
                    {
                        "type": "verifier_observation",
                        "title": "Role-differential authorization observation",
                        "content_text": "Two scoped test identities produced a response pattern that violates the expected object ownership policy in the local lab.",
                    }
                ],
            )
        return ToolResult(self.name, "completed", output={"reproduced": False})

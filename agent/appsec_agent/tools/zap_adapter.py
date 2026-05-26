from appsec_agent.tools.base import ToolAdapter, ToolResult


class ZAPBaselineAdapter(ToolAdapter):
    name = "zap_baseline_adapter"
    categories = ["misconfiguration_detection"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        return ToolResult(
            self.name,
            "skipped",
            output={"reason": "ZAP baseline is wired as an optional Docker adapter for lab mode."},
            evidence=[{"type": "tool_note", "title": "ZAP baseline", "content_text": "Enable Docker lab mode to run the OWASP ZAP baseline container."}],
        )

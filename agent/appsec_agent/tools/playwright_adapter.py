from appsec_agent.tools.base import ToolAdapter, ToolResult


class PlaywrightAdapter(ToolAdapter):
    name = "playwright_adapter"
    categories = ["auth_flow_detection", "access_control_detection"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        return ToolResult(
            self.name,
            "completed",
            output={"scenario": "browser smoke flow placeholder"},
            evidence=[{"type": "browser_trace", "title": "Browser scenario", "content_text": "Playwright adapter is available for login and screenshot scenarios in lab scans."}],
        )

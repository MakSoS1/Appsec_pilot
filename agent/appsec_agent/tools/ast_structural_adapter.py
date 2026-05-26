from __future__ import annotations

from pathlib import Path

from appsec_agent.endpoint_mapper import map_repository
from appsec_agent.tools.base import ToolAdapter, ToolResult


class ASTStructuralAdapter(ToolAdapter):
    name = "ast_structural_adapter"
    categories = ["static_analysis", "endpoint_mapping"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        repo_path = context.get("repo_path")
        if not repo_path or not Path(repo_path).exists():
            return ToolResult(self.name, "skipped", error="No local repository path")
        endpoints = map_repository(repo_path)
        payload = [ep.__dict__ for ep in endpoints[:200]]
        return ToolResult(self.name, "completed", output={"endpoint_count": len(endpoints), "endpoints": payload})

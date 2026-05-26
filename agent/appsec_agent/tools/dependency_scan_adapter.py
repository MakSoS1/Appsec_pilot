from __future__ import annotations

from pathlib import Path

from appsec_agent.tools.base import ToolAdapter, ToolResult


MANIFESTS = ("pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Dockerfile")


class DependencyScanAdapter(ToolAdapter):
    name = "dependency_scan_adapter"
    categories = ["dependency_scan", "container_scan"]

    async def run(self, context: dict, plan: dict) -> ToolResult:
        repo_path = context.get("repo_path")
        if not repo_path or not Path(repo_path).exists():
            return ToolResult(self.name, "skipped", error="No local repository path")
        root = Path(repo_path)
        manifests = [str(path.relative_to(root)) for name in MANIFESTS for path in root.rglob(name) if ".venv" not in path.parts and "node_modules" not in path.parts]
        return ToolResult(self.name, "completed", output={"scanner": "manifest_inventory", "manifests": manifests[:200], "note": "Install Trivy to enrich this adapter with CVE results."})

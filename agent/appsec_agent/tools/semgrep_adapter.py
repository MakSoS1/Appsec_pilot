import asyncio
from pathlib import Path

from appsec_agent.tools.base import ToolAdapter, ToolResult


class SemgrepAdapter(ToolAdapter):
    name = "semgrep_adapter"
    categories = ["injection_detection", "misconfiguration_detection"]

    async def is_available(self) -> bool:
        proc = await asyncio.create_subprocess_shell("semgrep --version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        return proc.returncode == 0

    async def run(self, context: dict, plan: dict) -> ToolResult:
        repo_path = context.get("repo_path")
        if not repo_path or not Path(repo_path).exists():
            return ToolResult(self.name, "skipped", error="No local repository path")
        if not await self.is_available():
            return ToolResult(self.name, "skipped", error="Semgrep is not installed")
        cmd = f'semgrep scan --config auto --json "{repo_path}"'
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return ToolResult(self.name, "completed" if proc.returncode in {0, 1} else "failed", output={"json": stdout.decode(errors="ignore")[:20000]}, error=stderr.decode(errors="ignore")[:2000] or None)

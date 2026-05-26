from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    tool_name: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


class ToolAdapter:
    name = "base"
    version = "0.1.0"
    categories: list[str] = []

    async def is_available(self) -> bool:
        return True

    async def validate_policy(self, context: dict[str, Any], plan: dict[str, Any]) -> bool:
        return True

    async def run(self, context: dict[str, Any], plan: dict[str, Any]) -> ToolResult:
        return ToolResult(tool_name=self.name, status="skipped")

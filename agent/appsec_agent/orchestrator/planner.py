import json
from typing import Any

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint
from appsec_agent.llm.client import LLMClient
from appsec_agent.llm.prompts import PLANNER_SYSTEM


def fallback_plan(endpoints: list[NormalizedEndpoint]) -> dict[str, Any]:
    hypotheses = []
    for idx, ep in enumerate(endpoints[:20]):
        category = "access_control_detection" if "object_id_in_path" in ep.risk_hints else "misconfiguration_detection"
        hypotheses.append(
            {
                "title": f"Safe validation for {ep.method} {ep.path}",
                "category": category,
                "endpoint_index": idx,
                "risk_reason": ", ".join(ep.risk_hints) or "Endpoint should be checked against baseline policy.",
                "required_tools": ["http_probe_adapter", "verifier"],
                "approval_required": False,
                "safety_notes": "Use only scope allowlist, provided test accounts, and request limits.",
            }
        )
    return {"hypotheses": hypotheses}


class Planner:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    async def plan(self, endpoints: list[NormalizedEndpoint], scope: dict[str, Any]) -> dict[str, Any]:
        fallback = fallback_plan(endpoints)
        if not self.llm:
            return fallback
        endpoint_context = [ep.__dict__ for ep in endpoints[:30]]
        user = json.dumps({"scope": scope, "endpoints": endpoint_context}, ensure_ascii=False)
        return await self.llm.chat_json(PLANNER_SYSTEM, user, fallback=fallback)

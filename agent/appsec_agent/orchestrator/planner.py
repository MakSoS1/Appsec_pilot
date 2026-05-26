import json
from typing import Any

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint
from appsec_agent.llm.client import LLMClient
from appsec_agent.llm.prompts import PLANNER_SYSTEM
from appsec_agent.skills.catalog import relevant_skills
from appsec_agent.tools.registry import enabled_tools


def _tools_for_category(category: str, profile: str) -> list[str]:
    tools = enabled_tools(profile)
    selected = [tool.adapter for tool in tools if category in {tool.category, tool.adapter}]
    if category == "access_control_detection":
        selected.extend(["http_probe_adapter", "custom_checks_adapter", "openapi_contract_adapter"])
    elif category == "sensitive_data_exposure_detection":
        selected.extend(["http_probe_adapter", "secret_scan_adapter"])
    elif category == "misconfiguration_detection":
        selected.extend(["http_probe_adapter", "openapi_contract_adapter"])
    else:
        selected.extend(["http_probe_adapter", "custom_checks_adapter"])
    return sorted(dict.fromkeys(selected))


def fallback_plan(endpoints: list[NormalizedEndpoint], scope: dict[str, Any] | None = None, profile: str = "safe-active") -> dict[str, Any]:
    hypotheses = []
    target_type = None
    if scope:
        target_type = str(scope.get("environment") or "")
    skill_ids = [skill.id for skill in relevant_skills(endpoints, target_type=target_type, profile=profile)]
    for idx, ep in enumerate(endpoints[:30]):
        if any(h in ep.risk_hints for h in ["object_id_in_path", "sensitive_operation"]):
            category = "access_control_detection"
        elif ep.sensitive_data_types:
            category = "sensitive_data_exposure_detection"
        else:
            category = "misconfiguration_detection"
        hypotheses.append(
            {
                "title": f"Scoped validation for {ep.method} {ep.path}",
                "category": category,
                "endpoint_index": idx,
                "risk_reason": ", ".join(ep.risk_hints + ep.sensitive_data_types) or "Endpoint should be checked against baseline policy.",
                "required_tools": _tools_for_category(category, profile),
                "skill_ids": skill_ids[:6],
                "approval_required": False,
                "safety_notes": "Use only scope allowlist, provided test accounts, request limits, and redacted evidence.",
            }
        )
    return {"hypotheses": hypotheses, "skills": skill_ids, "profile": profile}


class Planner:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    async def plan(self, endpoints: list[NormalizedEndpoint], scope: dict[str, Any], profile: str = "safe-active") -> dict[str, Any]:
        fallback = fallback_plan(endpoints, scope, profile)
        if not self.llm:
            return fallback
        endpoint_context = [ep.__dict__ for ep in endpoints[:30]]
        user = json.dumps({"scope": scope, "endpoints": endpoint_context, "fallback": fallback}, ensure_ascii=False)
        return await self.llm.chat_json(PLANNER_SYSTEM, user, fallback=fallback)

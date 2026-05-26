from appsec_agent.endpoint_mapper.common import NormalizedEndpoint
from appsec_agent.orchestrator.planner import fallback_plan
from appsec_agent.skills.catalog import relevant_skills
from appsec_agent.tools.registry import tool_registry_payload


def test_skill_catalog_selects_authz_for_object_endpoint():
    endpoint = NormalizedEndpoint(method="GET", path="/api/users/{id}", framework="fastapi", risk_hints=["object_id_in_path"])
    skills = relevant_skills([endpoint], target_type="local_url")
    assert any(skill.id == "api-authz-diff" for skill in skills)


def test_fallback_plan_contains_tools_and_skills():
    endpoint = NormalizedEndpoint(method="GET", path="/api/users/{id}", framework="fastapi", risk_hints=["object_id_in_path"])
    plan = fallback_plan([endpoint], {"environment": "local_lab"})
    first = plan["hypotheses"][0]
    assert "custom_checks_adapter" in first["required_tools"]
    assert first["skill_ids"]


def test_tool_registry_payload_has_details():
    payload = tool_registry_payload("safe-active")
    assert "secret_scan_adapter" in payload["tools"]
    assert any(tool["adapter"] == "http_probe_adapter" for tool in payload["tool_registry"])

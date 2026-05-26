from appsec_agent.endpoint_mapper.openapi_parser import parse_openapi_text
from appsec_agent.llm.client import parse_json_response
from appsec_agent.sandbox.scope import ScopePolicy

SCOPE = """
project_name: demo
environment: local_lab
allowed_targets:
  - host: localhost
    ports: [8008]
    schemes: [http]
allowed_http_methods: [GET, POST]
request_limits:
  max_requests_total: 20
allowed_check_categories: [access_control_detection]
blocked_check_categories: [credential_theft]
"""


def test_scope_allows_localhost_and_blocks_metadata():
    policy = ScopePolicy.from_yaml(SCOPE)
    assert policy.validate_url("http://localhost:8008/health").allowed
    assert not policy.validate_url("http://169.254.169.254/latest").allowed


def test_openapi_parser_extracts_endpoint():
    endpoints = parse_openapi_text('{"openapi":"3.0.0","paths":{"/api/users/{id}":{"get":{"operationId":"getUser"}}}}')
    assert endpoints[0].method == "GET"
    assert "object_id_in_path" in endpoints[0].risk_hints


def test_parse_json_response_strips_fences():
    assert parse_json_response('```json\n{"ok": true}\n```')["ok"] is True

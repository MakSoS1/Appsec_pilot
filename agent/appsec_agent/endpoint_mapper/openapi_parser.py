import json
from typing import Any

import yaml

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint, infer_hints

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def parse_openapi_text(text: str, framework: str = "openapi") -> list[NormalizedEndpoint]:
    if not text.strip():
        return []
    try:
        spec: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        spec = yaml.safe_load(text) or {}
    paths = spec.get("paths", {}) or {}
    endpoints: list[NormalizedEndpoint] = []
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in HTTP_METHODS:
                continue
            operation = operation or {}
            parameters = list(operation.get("parameters") or [])
            if operation.get("requestBody"):
                parameters.append({"name": "requestBody", "location": "body", "required": False})
            hints, sensitive, sensitive_op = infer_hints(method.upper(), path)
            security = operation.get("security") or spec.get("security") or []
            endpoints.append(
                NormalizedEndpoint(
                    method=method.upper(),
                    path=path,
                    framework=framework,
                    parameters=parameters,
                    auth_required=bool(security),
                    risk_hints=hints,
                    sensitive_data_types=sensitive,
                    sensitive_operation=sensitive_op,
                    openapi_operation_id=operation.get("operationId"),
                )
            )
    return endpoints

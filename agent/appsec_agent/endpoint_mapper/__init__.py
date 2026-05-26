from pathlib import Path

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint
from appsec_agent.endpoint_mapper.django_mapper import map_django
from appsec_agent.endpoint_mapper.express_mapper import map_express
from appsec_agent.endpoint_mapper.fastapi_mapper import map_fastapi
from appsec_agent.endpoint_mapper.flask_mapper import map_flask
from appsec_agent.endpoint_mapper.openapi_parser import parse_openapi_text


def map_repository(root: str | Path) -> list[NormalizedEndpoint]:
    endpoints = []
    endpoints.extend(map_fastapi(root))
    endpoints.extend(map_flask(root))
    endpoints.extend(map_express(root))
    endpoints.extend(map_django(root))
    unique = {}
    for ep in endpoints:
        unique[(ep.method, ep.path, ep.framework, ep.source_file)] = ep
    return list(unique.values())


__all__ = ["NormalizedEndpoint", "map_repository", "parse_openapi_text"]

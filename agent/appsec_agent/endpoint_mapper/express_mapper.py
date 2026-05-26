import re
from pathlib import Path

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint, discover_source_files, infer_hints

ROUTE_RE = re.compile(r"(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]")


def map_express(root: str | Path) -> list[NormalizedEndpoint]:
    endpoints: list[NormalizedEndpoint] = []
    for file in discover_source_files(root, (".js", ".ts", ".mjs", ".cjs")):
        text = file.read_text(encoding="utf-8", errors="ignore")
        line_offsets = text.splitlines()
        for match in ROUTE_RE.finditer(text):
            method, path = match.group(1).upper(), match.group(2)
            line = text[: match.start()].count("\n") + 1
            hints, sensitive, sensitive_op = infer_hints(method, path)
            endpoints.append(
                NormalizedEndpoint(
                    method=method,
                    path=path,
                    framework="express",
                    source_file=str(file),
                    source_line=line,
                    auth_required="auth" in line_offsets[line - 1].lower() if line - 1 < len(line_offsets) else False,
                    risk_hints=hints,
                    sensitive_data_types=sensitive,
                    sensitive_operation=sensitive_op,
                )
            )
    return endpoints

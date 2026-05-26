import re
from pathlib import Path

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint, discover_source_files, infer_hints

PATH_RE = re.compile(r"(?:path|re_path)\s*\(\s*['\"]([^'\"]+)['\"]")


def map_django(root: str | Path) -> list[NormalizedEndpoint]:
    endpoints: list[NormalizedEndpoint] = []
    for file in discover_source_files(root, (".py",)):
        if "urls" not in file.name:
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        for match in PATH_RE.finditer(text):
            path = "/" + match.group(1).strip("/")
            if path == "/":
                path = "/"
            line = text[: match.start()].count("\n") + 1
            hints, sensitive, sensitive_op = infer_hints("GET", path)
            endpoints.append(
                NormalizedEndpoint(
                    method="GET",
                    path=path,
                    framework="django",
                    source_file=str(file),
                    source_line=line,
                    risk_hints=hints,
                    sensitive_data_types=sensitive,
                    sensitive_operation=sensitive_op,
                )
            )
    return endpoints

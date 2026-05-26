import ast
from pathlib import Path

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint, discover_source_files, infer_hints

METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _decorator_to_route(dec: ast.AST) -> tuple[str, str] | None:
    if not isinstance(dec, ast.Call):
        return None
    func = dec.func
    method = None
    if isinstance(func, ast.Attribute) and func.attr.lower() in METHODS:
        method = func.attr.upper()
    if not method:
        return None
    if not dec.args:
        return None
    arg = dec.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return method, arg.value
    return None


def map_fastapi(root: str | Path) -> list[NormalizedEndpoint]:
    endpoints: list[NormalizedEndpoint] = []
    for file in discover_source_files(root, (".py",)):
        try:
            tree = ast.parse(file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                route = _decorator_to_route(dec)
                if not route:
                    continue
                method, path = route
                hints, sensitive, sensitive_op = infer_hints(method, path)
                auth_required = any("depend" in ast.unparse(d).lower() for d in node.decorator_list) if hasattr(ast, "unparse") else False
                endpoints.append(
                    NormalizedEndpoint(
                        method=method,
                        path=path,
                        framework="fastapi",
                        source_file=str(file),
                        source_line=node.lineno,
                        auth_required=auth_required,
                        risk_hints=hints,
                        sensitive_data_types=sensitive,
                        sensitive_operation=sensitive_op,
                    )
                )
    return endpoints

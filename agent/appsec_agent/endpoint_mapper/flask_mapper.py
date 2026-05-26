import ast
from pathlib import Path

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint, discover_source_files, infer_hints


def _literal_methods(call: ast.Call) -> list[str]:
    for kw in call.keywords:
        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
            methods = []
            for item in kw.value.elts:
                if isinstance(item, ast.Constant) and isinstance(item.value, str):
                    methods.append(item.value.upper())
            return methods
    return ["GET"]


def map_flask(root: str | Path) -> list[NormalizedEndpoint]:
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
                if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                    continue
                if dec.func.attr != "route" or not dec.args:
                    continue
                first = dec.args[0]
                if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
                    continue
                for method in _literal_methods(dec):
                    hints, sensitive, sensitive_op = infer_hints(method, first.value)
                    endpoints.append(
                        NormalizedEndpoint(
                            method=method,
                            path=first.value,
                            framework="flask",
                            source_file=str(file),
                            source_line=node.lineno,
                            auth_required=len(node.decorator_list) > 1,
                            risk_hints=hints,
                            sensitive_data_types=sensitive,
                            sensitive_operation=sensitive_op,
                        )
                    )
    return endpoints

from appsec_agent.endpoint_mapper.common import NormalizedEndpoint


def score_endpoint(endpoint: NormalizedEndpoint) -> float:
    score = 2.5
    if endpoint.auth_required:
        score += 0.7
    if "object_id_in_path" in endpoint.risk_hints:
        score += 1.8
    if "sensitive_operation" in endpoint.risk_hints:
        score += 1.5
    if endpoint.method in {"POST", "PUT", "PATCH", "DELETE"}:
        score += 0.8
    if endpoint.sensitive_data_types:
        score += 1.0
    return min(round(score, 1), 10.0)


def severity_from_score(score: float) -> str:
    if score >= 9:
        return "critical"
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low"

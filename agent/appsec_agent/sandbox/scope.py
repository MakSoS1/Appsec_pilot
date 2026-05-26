import ipaddress
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import yaml

SAFE_ENVIRONMENTS = {"local_lab", "staging_authorized", "ci_lab"}
DEFAULT_DENY = {"169.254.169.254", "metadata.google.internal", "metadata", "host.docker.internal"}


@dataclass
class ScopeDecision:
    allowed: bool
    reason: str


class ScopePolicy:
    def __init__(self, raw: dict[str, Any]):
        self.raw = raw
        self.environment = raw.get("environment")
        self.allowed_targets = raw.get("allowed_targets") or []
        self.denied_targets = set(raw.get("denied_targets") or []) | DEFAULT_DENY
        self.allowed_http_methods = {m.upper() for m in raw.get("allowed_http_methods") or ["GET"]}
        self.allowed_categories = set(raw.get("allowed_check_categories") or [])
        self.blocked_categories = set(raw.get("blocked_check_categories") or [])
        self.request_limits = raw.get("request_limits") or {}

    @classmethod
    def from_yaml(cls, text: str) -> "ScopePolicy":
        data = yaml.safe_load(text or "") or {}
        policy = cls(data)
        policy.validate_required()
        return policy

    def validate_required(self) -> None:
        missing = []
        for key in ["project_name", "environment", "allowed_targets", "allowed_http_methods", "request_limits", "allowed_check_categories"]:
            if not self.raw.get(key):
                missing.append(key)
        if missing:
            raise ValueError(f"scope.yaml missing required keys: {', '.join(missing)}")
        if self.environment not in SAFE_ENVIRONMENTS:
            raise ValueError("scope environment must be local_lab, staging_authorized, or ci_lab")

    def validate_url(self, url: str, method: str = "GET") -> ScopeDecision:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if method.upper() not in self.allowed_http_methods:
            return ScopeDecision(False, f"HTTP method {method} is not allowed")
        if host in self.denied_targets:
            return ScopeDecision(False, f"Host {host} is denied by policy")
        for denied in self.denied_targets:
            if "/" in denied:
                try:
                    if ipaddress.ip_address(host) in ipaddress.ip_network(denied, strict=False):
                        return ScopeDecision(False, f"Host {host} is inside denied network {denied}")
                except ValueError:
                    pass
        for target in self.allowed_targets:
            if target.get("host") != host:
                continue
            if port not in target.get("ports", []):
                continue
            if parsed.scheme not in target.get("schemes", ["http"]):
                continue
            return ScopeDecision(True, "allowed by scope")
        return ScopeDecision(False, f"Target {host}:{port} is outside allowlist")

    def validate_category(self, category: str) -> ScopeDecision:
        if category in self.blocked_categories:
            return ScopeDecision(False, f"Category {category} is blocked")
        if self.allowed_categories and category not in self.allowed_categories:
            return ScopeDecision(False, f"Category {category} is not in allowed categories")
        return ScopeDecision(True, "allowed category")

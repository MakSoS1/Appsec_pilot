import time
from pathlib import Path
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="AppSec Pilot CLI")
console = Console()

EXIT_OK = 0
EXIT_BLOCKING = 1
EXIT_SCAN_FAILED = 2
EXIT_POLICY = 3
EXIT_INVALID_CONFIG = 4
EXIT_TARGET_UNAVAILABLE = 5


def client(api_url: str) -> httpx.Client:
    return httpx.Client(base_url=api_url.rstrip("/"), timeout=30)


def auth_headers(c: httpx.Client) -> dict[str, str]:
    response = c.post("/api/auth/login", json={"email": "admin@appsec.local", "password": "AppSecPilot123!"})
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@app.command()
def init(path: Path = typer.Option(Path("appsec.scope.yaml"), "--scope")) -> None:
    """Write a safe default scope file."""
    text = Path("benchmarks/custom_vuln_apps/fastapi_vuln/scope.yaml")
    if text.exists():
        path.write_text(text.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        path.write_text("project_name: local-demo\nenvironment: local_lab\nallowed_targets: []\nallowed_http_methods: [GET]\nrequest_limits: {max_requests_total: 10}\nallowed_check_categories: [misconfiguration_detection]\n", encoding="utf-8")
    console.print(f"Wrote {path}")


@app.command()
def scan(
    api_url: str = typer.Option("http://localhost:8080", "--api-url"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    target: Optional[Path] = typer.Option(None, "--target"),
    base_url: Optional[str] = typer.Option(None, "--base-url"),
    openapi: Optional[Path] = typer.Option(None, "--openapi"),
    scope: Path = typer.Option(..., "--scope"),
    profile: str = typer.Option("safe-active", "--profile"),
    wait: bool = typer.Option(False, "--wait"),
    fail_on: str = typer.Option("critical", "--fail-on"),
) -> None:
    """Create a target if needed, start a scan, optionally wait, and return CI exit code."""
    if not scope.exists():
        console.print("Scope file not found", style="red")
        raise typer.Exit(EXIT_INVALID_CONFIG)
    scope_text = scope.read_text(encoding="utf-8")
    with client(api_url) as c:
        try:
            headers = auth_headers(c)
            if not project_id:
                projects = c.get("/api/projects", headers=headers).json()
                if not projects:
                    created = c.post("/api/projects", headers=headers, json={"name": "CLI Project", "description": "Created by CLI", "environment": "local_lab"})
                    created.raise_for_status()
                    project_id = created.json()["id"]
                else:
                    project_id = projects[0]["id"]
            target_payload = {
                "type": "local_url" if base_url else "local_repo" if target else "openapi",
                "name": base_url or str(target or openapi or "CLI target"),
                "repo_path": str(target) if target else None,
                "openapi_text": openapi.read_text(encoding="utf-8") if openapi else None,
                "base_url": base_url,
                "scope_yaml": scope_text,
            }
            target_response = c.post(f"/api/projects/{project_id}/targets", headers=headers, json=target_payload)
            target_response.raise_for_status()
            target_id = target_response.json()["id"]
            scan_response = c.post(f"/api/projects/{project_id}/scans", headers=headers, json={"target_id": target_id, "profile": profile, "start_immediately": True})
            scan_response.raise_for_status()
            scan_id = scan_response.json()["id"]
            console.print(f"Started scan {scan_id}")
            if wait:
                final = wait_for_scan(c, headers, scan_id)
                emit_findings_table(c, headers, scan_id)
                if final["status"] == "failed":
                    raise typer.Exit(EXIT_SCAN_FAILED)
                findings = c.get(f"/api/scans/{scan_id}/findings", headers=headers).json()
                blocking = [f for f in findings if f["status"] == "confirmed" and severity_blocks(f["severity"], fail_on)]
                raise typer.Exit(EXIT_BLOCKING if blocking else EXIT_OK)
        except httpx.HTTPStatusError as exc:
            console.print(str(exc), style="red")
            raise typer.Exit(EXIT_POLICY if exc.response.status_code == 400 else EXIT_SCAN_FAILED) from exc
        except httpx.ConnectError as exc:
            console.print("Backend API is unavailable", style="red")
            raise typer.Exit(EXIT_TARGET_UNAVAILABLE) from exc


def wait_for_scan(c: httpx.Client, headers: dict[str, str], scan_id: str) -> dict:
    while True:
        data = c.get(f"/api/scans/{scan_id}", headers=headers).json()
        console.print(f"{scan_id}: {data['status']}")
        if data["status"] in {"completed", "failed", "cancelled"}:
            return data
        time.sleep(1)


def severity_blocks(severity: str, fail_on: str) -> bool:
    order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return order.get(severity, 0) >= order.get(fail_on, 4)


def emit_findings_table(c: httpx.Client, headers: dict[str, str], scan_id: str) -> None:
    findings = c.get(f"/api/scans/{scan_id}/findings", headers=headers).json()
    table = Table("Severity", "Status", "Title", "Risk")
    for f in findings:
        table.add_row(f["severity"], f["status"], f["title"], str(f["risk_score"]))
    console.print(table)


@app.command()
def status(scan_id: str, api_url: str = "http://localhost:8080") -> None:
    with client(api_url) as c:
        headers = auth_headers(c)
        console.print(c.get(f"/api/scans/{scan_id}", headers=headers).json())


@app.command()
def findings(scan_id: str, confirmed: bool = False, api_url: str = "http://localhost:8080") -> None:
    with client(api_url) as c:
        headers = auth_headers(c)
        data = c.get(f"/api/scans/{scan_id}/findings", headers=headers).json()
        if confirmed:
            data = [f for f in data if f["status"] == "confirmed"]
        table = Table("ID", "Severity", "Status", "Title")
        for f in data:
            table.add_row(f["id"], f["severity"], f["status"], f["title"])
        console.print(table)


@app.command()
def report(scan_id: str, format: str = "html", api_url: str = "http://localhost:8080") -> None:
    with client(api_url) as c:
        headers = auth_headers(c)
        response = c.post(f"/api/scans/{scan_id}/reports", headers=headers, params={"fmt": format})
        response.raise_for_status()
        console.print(response.json())


@app.command()
def ci(scan_id: str, fail_on: str = "critical", api_url: str = "http://localhost:8080") -> None:
    with client(api_url) as c:
        headers = auth_headers(c)
        data = c.get(f"/api/scans/{scan_id}/findings", headers=headers).json()
        blocking = [f for f in data if f["status"] == "confirmed" and severity_blocks(f["severity"], fail_on)]
        raise typer.Exit(EXIT_BLOCKING if blocking else EXIT_OK)


if __name__ == "__main__":
    app()

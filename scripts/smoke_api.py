import time

import httpx

API = "http://localhost:8080"

with httpx.Client(base_url=API, timeout=30) as client:
    health = client.get("/health")
    health.raise_for_status()
    token = client.post("/api/auth/login", json={"email": "admin@appsec.local", "password": "AppSecPilot123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    projects = client.get("/api/projects", headers=headers).json()
    project_id = projects[0]["id"]
    targets = client.get(f"/api/projects/{project_id}/targets", headers=headers).json()
    scan = client.post(f"/api/projects/{project_id}/scans", headers=headers, json={"target_id": targets[0]["id"], "profile": "safe-active", "start_immediately": True}).json()
    for _ in range(30):
        current = client.get(f"/api/scans/{scan['id']}", headers=headers).json()
        if current["status"] in {"completed", "failed", "cancelled"}:
            break
        time.sleep(1)
    findings = client.get(f"/api/scans/{scan['id']}/findings", headers=headers).json()
    print({"scan": scan["id"], "status": current["status"], "findings": len(findings)})
    if current["status"] != "completed" or not findings:
        raise SystemExit(1)

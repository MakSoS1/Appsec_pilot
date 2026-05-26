# AppSec Pilot

AppSec Pilot is a self-hosted AI AppSec platform for authorized security validation of web applications and APIs. It builds an endpoint map, plans safe checks with a local open-weight LLM, runs checks through a policy layer, verifies findings from evidence, and exports developer-ready reports.

## What Works in This MVP

- FastAPI backend with JWT auth, projects, targets, scans, endpoints, findings, evidence, reports, settings, and audit logs.
- Vite/TanStack React interface with dashboards, projects, target wizard, scan timeline, endpoint graph, findings, reports, model settings, and audit log.
- Local model integration through OpenAI-compatible API, defaulting to Ollama at `http://localhost:11434/v1` and model tag `qwen35-hauhau-q4:latest`.
- Endpoint mapping for OpenAPI, FastAPI, Flask, Express.js, and basic Django URL maps.
- Scope validation with allowlisted hosts/ports/methods, blocked categories, request limits, and redaction settings.
- Safe adapters for HTTP probes, custom auth/role/object checks, Semgrep, Playwright, and ZAP baseline extension points.
- HTML and PDF reports with verifier decisions and evidence summaries.
- CLI for local scans and CI exit codes.
- Custom FastAPI lab app with seeded vulnerabilities for demo and tests.

## Quick Start on the Remote PC

```powershell
cd C:\Users\maksi\Documents\work\appsec-pilot
uv venv .venv
uv pip install -e agent -e backend -e cli
cd frontend
npm install
cd ..
```

Start the backend:

```powershell
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Start the frontend in another terminal:

```powershell
cd frontend
npm run dev -- --host 0.0.0.0 --port 3001
```

Open `http://10.78.211.199:3001` or `http://localhost:3001` on the remote PC.

Default login:

```text
admin@appsec.local
AppSecPilot123!
```

## Local Model

The backend expects an OpenAI-compatible chat endpoint. For the current GPU host the default is:

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen35-hauhau-q4:latest
LLM_API_KEY=local-dev-key
```

The agent treats the model as a planner and summarizer only. Every tool action is still checked by scope policy, adapter policy, audit logging, evidence redaction, and verifier logic.

## Demo Flow

1. Log in to AppSec Pilot.
2. Open Projects and choose `FastAPI Lab Demo`.
3. Use Target Wizard to review the local target and scope.
4. Start a `safe-active` scan.
5. Watch the scan timeline move through mapping, planning, checks, verification, and reporting.
6. Open Findings and inspect evidence and remediation.
7. Download HTML/PDF reports.
8. Run the CLI CI gate:

```powershell
appsec scan --api-url http://localhost:8080 --base-url http://localhost:8008 --scope benchmarks/custom_vuln_apps/fastapi_vuln/scope.yaml --wait --fail-on high
```

## Docker

When Docker Desktop is running:

```powershell
docker compose up -d --build
docker compose -f docker-compose.lab.yml up -d
```

The lab compose includes Juice Shop, WebGoat, and the custom FastAPI vulnerable app.

## Safety Position

AppSec Pilot is designed for authorized local labs, staging systems, and CI environments. It blocks public-target behavior by default, requires scope files, denies cloud metadata hosts, redacts evidence, and records every scan action in the audit log.

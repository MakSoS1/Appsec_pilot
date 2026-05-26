# Architecture

AppSec Pilot has five runtime layers:

1. Web UI and CLI for project, target, scan, finding, and report workflows.
2. Backend API for auth, persistence, RBAC, audit, reports, and scan lifecycle control.
3. Agent layer for endpoint mapping, LLM planning, policy validation, tool selection, verification, and risk scoring.
4. Sandbox/tool layer for safe HTTP probes, static checks, browser checks, and lab DAST hooks.
5. Evidence/report layer for redacted observations, verifier decisions, HTML/PDF output, and CI gate status.

The MVP uses FastAPI BackgroundTasks for local scan execution. The worker entrypoint is present for moving the same scan service behind Dramatiq/Redis without changing API contracts.

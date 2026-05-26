# API

Primary endpoints:

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `GET/POST/PATCH/DELETE /api/projects`
- `GET/POST/PATCH/DELETE /api/targets`
- `POST /api/projects/{project_id}/scans`, `GET /api/scans/{scan_id}`, `POST /api/scans/{scan_id}/cancel`, `POST /api/scans/{scan_id}/rerun`
- `GET /api/scans/{scan_id}/events`, `GET /api/scans/{scan_id}/logs`
- `GET /api/scans/{scan_id}/endpoints`, `GET /api/scans/{scan_id}/endpoint-graph`
- `GET /api/findings`, `GET /api/findings/{finding_id}`, `POST /api/findings/{finding_id}/reverify`
- `GET /api/findings/{finding_id}/evidence`, `GET /api/evidence/{evidence_id}/download`
- `POST /api/scans/{scan_id}/reports`, `GET /api/reports/{report_id}/download.html`, `GET /api/reports/{report_id}/download.pdf`
- `GET /api/settings/model`, `GET /api/settings/policies`, `GET /api/settings/tools`
- `GET /api/audit-logs`

The live OpenAPI schema is available at `/docs` when the backend is running.

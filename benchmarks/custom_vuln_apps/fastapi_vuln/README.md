# FastAPI Vulnerable Lab

Small local-only app used to demonstrate AppSec Pilot endpoint mapping, scope validation, role-differential checks, evidence capture, and remediation output.

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8008
```

Known seeded issues:
- Broken object-level authorization on `/api/users/{id}`.
- Broken object-level authorization on `/api/orders/{id}`.
- Missing admin role check on `/api/admin/reports`.

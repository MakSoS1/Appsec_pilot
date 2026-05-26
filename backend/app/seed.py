from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Project, Target, User
from app.security import hash_password

DEFAULT_SCOPE = """
project_name: "fastapi-vuln-demo"
environment: "local_lab"
allowed_targets:
  - host: "localhost"
    ports: [8008, 3000, 8081]
    schemes: ["http"]
  - host: "127.0.0.1"
    ports: [8008, 3000, 8081]
    schemes: ["http"]
denied_targets:
  - "0.0.0.0/0"
  - "169.254.169.254"
  - "metadata.google.internal"
  - "host.docker.internal"
allowed_http_methods: [GET, POST, PUT, PATCH, DELETE]
request_limits:
  max_requests_total: 120
  max_requests_per_minute: 60
  max_concurrent_requests: 4
  timeout_seconds: 10
test_accounts:
  - username: "demo_user@appsec.local"
    password: "DemoUser123!"
    role: "user"
  - username: "demo_admin@appsec.local"
    password: "DemoAdmin123!"
    role: "admin"
allowed_check_categories:
  - injection_detection
  - access_control_detection
  - auth_flow_detection
  - misconfiguration_detection
  - sensitive_data_exposure_detection
  - api_contract_detection
blocked_check_categories:
  - destructive_data_deletion
  - persistence
  - credential_theft
  - lateral_movement
  - external_reconnaissance
  - evasion
  - malware_execution
  - c2
  - public_internet_scanning
approval_required:
  - mass_assignment_checks
  - state_changing_checks
  - high_request_volume_checks
evidence:
  store_http_requests: true
  store_http_responses: true
  store_screenshots: true
  redact_secrets: true
  redact_tokens: true
""".strip()


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(func.count(User.id))) == 0:
        admin = User(
            email="admin@appsec.local",
            password_hash=hash_password("AppSecPilot123!"),
            full_name="AppSec Pilot Admin",
            role="admin",
        )
        db.add(admin)
        db.flush()
    else:
        admin = db.scalar(select(User).where(User.email == "admin@appsec.local"))

    if db.scalar(select(func.count(Project.id))) == 0:
        project = Project(
            name="FastAPI Lab Demo",
            description="Local authorized demo project with seeded vulnerabilities and evidence.",
            owner_id=admin.id if admin else None,
            environment="local_lab",
            risk_score=0,
            ci_gate="passing",
        )
        db.add(project)
        db.flush()
        db.add(
            Target(
                project_id=project.id,
                type="local_url",
                name="Custom FastAPI vulnerable API",
                base_url="http://localhost:8008",
                scope_yaml=DEFAULT_SCOPE,
            )
        )
    db.commit()

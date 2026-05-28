type DemoProject = {
  id: string;
  name: string;
  description: string;
  environment: string;
  risk_score: number;
  ci_gate: string;
  targets_count: number;
  scans_count: number;
  open_findings: number;
  confirmed_findings: number;
};

type DemoTarget = {
  id: string;
  project_id: string;
  type: string;
  name: string;
  base_url?: string | null;
  repo_path?: string | null;
  openapi_path?: string | null;
  docker_compose_path?: string | null;
  scope_yaml: string;
};

type DemoScan = {
  id: string;
  project_id: string;
  target_id?: string | null;
  status: string;
  profile: string;
  started_at?: string | null;
  finished_at?: string | null;
  model_name: string;
  total_endpoints: number;
  total_findings: number;
  confirmed_findings: number;
  needs_review_findings: number;
  failed_reason?: string | null;
  events_json: Array<{
    time: string;
    stage: string;
    message: string;
    extra?: Record<string, unknown>;
  }>;
  created_at: string;
};

type DemoEndpoint = {
  id: string;
  scan_run_id: string;
  method: string;
  path: string;
  framework: string;
  auth_required: boolean;
  roles: string[];
  risk_hints_json: string[];
  sensitive_data_types_json: string[];
};

type DemoFinding = {
  id: string;
  scan_run_id: string;
  endpoint_id?: string | null;
  title: string;
  category: string;
  cwe_id: string;
  owasp_category: string;
  severity: "critical" | "high" | "medium" | "low";
  risk_score: number;
  status: string;
  description: string;
  business_impact: string;
  remediation: string;
  confidence: number;
  assigned_to: string;
  created_at: string;
};

type DemoEvidence = {
  id: string;
  finding_id: string;
  type: string;
  title: string;
  content_text: string;
  artifact_path?: string | null;
  redacted: boolean;
  created_at: string;
};

type DemoReport = {
  id: string;
  scan_run_id: string;
  format: string;
  status: string;
  html_path?: string | null;
  pdf_path?: string | null;
  created_at: string;
};

type DemoAudit = {
  id: string;
  action: string;
  object_type: string;
  object_id?: string | null;
  scan_run_id?: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

const defaultScope = `project_name: "training-benchmark-demo"
environment: "local_lab"
allowed_targets:
  - host: "localhost"
    ports: [8012, 8080, 3001]
    schemes: ["http"]
allowed_http_methods: [GET, POST, PUT, PATCH, DELETE]
request_limits:
  max_requests_total: 160
  max_requests_per_minute: 80
  max_concurrent_requests: 5
  timeout_seconds: 15
allowed_check_categories: [access_control_detection, misconfiguration_detection, sensitive_data_exposure_detection, auth_flow_detection]
blocked_check_categories: [credential_theft, persistence, external_reconnaissance, c2, malware_execution]
evidence:
  store_http_requests: true
  store_http_responses: true
  redact_secrets: true
`;

const now = new Date();
const iso = (shiftMinutes: number) => new Date(now.getTime() - shiftMinutes * 60_000).toISOString();

const projectMainId = "proj_training_demo";
const targetMainId = "tgt_training_local";
const scanMainId = "scan_f76f5c79b973";

let seq = 1000;
const nextId = (prefix: string) => `${prefix}_${seq++}`;

const templateEndpoints: Array<Omit<DemoEndpoint, "id" | "scan_run_id">> = [
  {
    method: "POST",
    path: "/login",
    framework: "fastapi",
    auth_required: false,
    roles: [],
    risk_hints_json: ["state_changing_method"],
    sensitive_data_types_json: [],
  },
  {
    method: "GET",
    path: "/api/users/{id}",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["object_id_in_path"],
    sensitive_data_types_json: ["profile"],
  },
  {
    method: "GET",
    path: "/api/orders/{id}",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["object_id_in_path"],
    sensitive_data_types_json: ["payment"],
  },
  {
    method: "POST",
    path: "/api/orders/{id}/approve",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["state_changing_method", "sensitive_operation"],
    sensitive_data_types_json: ["payment"],
  },
  {
    method: "GET",
    path: "/api/invoices/{id}",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["object_id_in_path"],
    sensitive_data_types_json: ["invoice"],
  },
  {
    method: "PATCH",
    path: "/api/account/{id}/email",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["state_changing_method", "object_id_in_path"],
    sensitive_data_types_json: ["profile"],
  },
  {
    method: "GET",
    path: "/api/admin/reports",
    framework: "fastapi",
    auth_required: true,
    roles: ["admin"],
    risk_hints_json: ["admin_route"],
    sensitive_data_types_json: ["financial"],
  },
  {
    method: "GET",
    path: "/api/admin/audit/export",
    framework: "fastapi",
    auth_required: true,
    roles: ["admin"],
    risk_hints_json: ["admin_route", "sensitive_operation"],
    sensitive_data_types_json: ["audit_log"],
  },
  {
    method: "GET",
    path: "/api/secrets/debug",
    framework: "fastapi",
    auth_required: true,
    roles: ["admin"],
    risk_hints_json: ["sensitive_operation"],
    sensitive_data_types_json: ["token"],
  },
  {
    method: "GET",
    path: "/api/internal/config",
    framework: "fastapi",
    auth_required: false,
    roles: [],
    risk_hints_json: ["debug_route"],
    sensitive_data_types_json: [],
  },
  {
    method: "POST",
    path: "/api/reports/generate",
    framework: "fastapi",
    auth_required: true,
    roles: ["user", "manager", "admin"],
    risk_hints_json: ["state_changing_method", "sensitive_operation"],
    sensitive_data_types_json: ["financial"],
  },
  {
    method: "GET",
    path: "/api/public/status",
    framework: "fastapi",
    auth_required: false,
    roles: [],
    risk_hints_json: ["misconfiguration_signal"],
    sensitive_data_types_json: [],
  },
  {
    method: "GET",
    path: "/health",
    framework: "fastapi",
    auth_required: false,
    roles: [],
    risk_hints_json: [],
    sensitive_data_types_json: [],
  },
];

let projects: DemoProject[] = [
  {
    id: projectMainId,
    name: "Training Benchmark Demo",
    description: "Demo project for capability-ladder presentation flow",
    environment: "local_lab",
    risk_score: 8.7,
    ci_gate: "failing",
    targets_count: 1,
    scans_count: 1,
    open_findings: 12,
    confirmed_findings: 11,
  },
];

const targets: DemoTarget[] = [
  {
    id: targetMainId,
    project_id: projectMainId,
    type: "local_url",
    name: "Training Suite localhost:8012",
    base_url: "http://localhost:8012",
    repo_path:
      "C:\\Users\\maksi\\Documents\\work\\appsec-pilot\\benchmarks\\training_suite\\vuln_app",
    scope_yaml: defaultScope,
  },
];

const baseEvents = [
  ["preparing_environment", "Validated scope, request limits, and policy allowlist"],
  ["mapping_application", "Mapped endpoints and imported live OpenAPI surface"],
  ["building_context", "Loaded skill cards and enabled safe tool adapters"],
  ["generating_hypotheses", "Generated policy-checked security hypotheses"],
  ["running_checks", "Executed safe adapters and verifier probes"],
  ["verifying_findings", "Verifier correlated observations with evidence"],
  ["generating_report", "Generated HTML and PDF reports"],
  ["completed", "Scan completed successfully"],
] as const;

const buildEvents = (offset: number) =>
  baseEvents.map((entry, index) => ({
    time: iso(offset + 8 - index),
    stage: entry[0],
    message: entry[1],
    extra: {},
  }));

let scans: DemoScan[] = [
  {
    id: scanMainId,
    project_id: projectMainId,
    target_id: targetMainId,
    status: "completed",
    profile: "safe-active",
    started_at: iso(15),
    finished_at: iso(7),
    model_name: "local-qwen-family",
    total_endpoints: 13,
    total_findings: 12,
    confirmed_findings: 11,
    needs_review_findings: 1,
    events_json: buildEvents(15),
    created_at: iso(16),
  },
];

const endpoints: DemoEndpoint[] = templateEndpoints.map((ep, index) => ({
  ...ep,
  id: `ep_main_${index + 1}`,
  scan_run_id: scanMainId,
}));

const ep = (path: string) => endpoints.find((item) => item.path === path)?.id ?? null;

let findings: DemoFinding[] = [
  {
    id: "finding_001",
    scan_run_id: scanMainId,
    endpoint_id: ep("/api/orders/{id}"),
    title: "Potential broken object-level authorization",
    category: "access_control_detection",
    cwe_id: "CWE-639",
    owasp_category: "A01:2021-Broken Access Control",
    severity: "medium",
    risk_score: 7.6,
    status: "confirmed",
    description: "Object-id endpoint allows cross-account access in demo data flow.",
    business_impact: "Unauthorized users may access other users' order data.",
    remediation: "Enforce ownership checks before returning order objects.",
    confidence: 0.88,
    assigned_to: "AppSec Team",
    created_at: iso(14),
  },
  {
    id: "finding_002",
    scan_run_id: scanMainId,
    endpoint_id: ep("/api/admin/reports"),
    title: "Admin endpoint requires explicit role verification",
    category: "access_control_detection",
    cwe_id: "CWE-862",
    owasp_category: "A01:2021-Broken Access Control",
    severity: "high",
    risk_score: 8.9,
    status: "confirmed",
    description: "Admin reports route is exposed without strict role boundary in training target.",
    business_impact: "Unauthorized access to sensitive reporting data.",
    remediation: "Validate admin role server-side for each privileged endpoint.",
    confidence: 0.91,
    assigned_to: "Security Champion",
    created_at: iso(13),
  },
  {
    id: "finding_003",
    scan_run_id: scanMainId,
    endpoint_id: ep("/api/secrets/debug"),
    title: "Debug endpoint exposes sensitive tokens",
    category: "sensitive_data_exposure_detection",
    cwe_id: "CWE-200",
    owasp_category: "A05:2021-Security Misconfiguration",
    severity: "medium",
    risk_score: 7.2,
    status: "confirmed",
    description: "Debug route leaks token-like values in HTTP response body.",
    business_impact: "Leaked secrets can be reused to access internal services.",
    remediation: "Remove token disclosure from responses and redact debug payloads.",
    confidence: 0.89,
    assigned_to: "Platform Team",
    created_at: iso(12),
  },
  {
    id: "finding_004",
    scan_run_id: scanMainId,
    endpoint_id: ep("/login"),
    title: "Authentication flow requires stronger server-side controls",
    category: "auth_flow_detection",
    cwe_id: "CWE-306",
    owasp_category: "A07:2021-Identification and Authentication Failures",
    severity: "medium",
    risk_score: 6.8,
    status: "confirmed",
    description: "Auth flow boundary requires tighter server-side validation.",
    business_impact: "Weak auth checks can enable unauthorized state changes.",
    remediation: "Require robust auth controls for state-changing actions.",
    confidence: 0.84,
    assigned_to: "Identity Team",
    created_at: iso(11),
  },
  {
    id: "finding_005",
    scan_run_id: scanMainId,
    endpoint_id: ep("/api/public/status"),
    title: "Security header and contract validation needed",
    category: "misconfiguration_detection",
    cwe_id: "CWE-693",
    owasp_category: "A05:2021-Security Misconfiguration",
    severity: "low",
    risk_score: 4.3,
    status: "needs_review",
    description: "Public status endpoint returns verbose metadata and weak headers.",
    business_impact: "Increases reconnaissance value for attackers.",
    remediation: "Tighten response contract and enforce security headers.",
    confidence: 0.62,
    assigned_to: "Ops Team",
    created_at: iso(10),
  },
];

while (findings.length < 12) {
  const base = findings[findings.length % 4];
  findings.push({
    ...base,
    id: `finding_${String(findings.length + 1).padStart(3, "0")}`,
    created_at: iso(9 - findings.length),
  });
}

const evidence: DemoEvidence[] = findings.map((finding, index) => ({
  id: `evidence_${index + 1}`,
  finding_id: finding.id,
  type: "verifier_observation",
  title: "Verifier decision and redacted evidence",
  content_text: [
    `Finding: ${finding.title}`,
    `Status: ${finding.status}`,
    "Observation: scoped local checks reproduced the signal.",
    "Note: sensitive values redacted by policy.",
  ].join("\n"),
  redacted: true,
  created_at: finding.created_at,
}));

const reports: DemoReport[] = [
  {
    id: "report_html_001",
    scan_run_id: scanMainId,
    format: "html",
    status: "ready",
    html_path: "artifacts/report.html",
    created_at: iso(6),
  },
  {
    id: "report_pdf_001",
    scan_run_id: scanMainId,
    format: "pdf",
    status: "ready",
    pdf_path: "artifacts/report.pdf",
    created_at: iso(6),
  },
];

const auditLogs: DemoAudit[] = [
  {
    id: "audit_001",
    action: "project.created",
    object_type: "project",
    object_id: projectMainId,
    metadata_json: { source: "demo-seed" },
    created_at: iso(18),
  },
  {
    id: "audit_002",
    action: "target.created",
    object_type: "target",
    object_id: targetMainId,
    metadata_json: { base_url: "http://localhost:8012" },
    created_at: iso(17),
  },
  {
    id: "audit_003",
    action: "scan.completed",
    object_type: "scan_run",
    object_id: scanMainId,
    scan_run_id: scanMainId,
    metadata_json: { findings: 12, confirmed: 11, tier: "T1" },
    created_at: iso(7),
  },
];

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function delay(ms = 120): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function withEndpoint(finding: DemoFinding) {
  const endpoint = finding.endpoint_id
    ? (endpoints.find((item) => item.id === finding.endpoint_id) ?? null)
    : null;
  return { ...finding, endpoint };
}

function refreshProjectStats() {
  projects = projects.map((project) => {
    const projectTargets = targets.filter((target) => target.project_id === project.id);
    const projectScans = scans.filter((scan) => scan.project_id === project.id);
    const scanIds = new Set(projectScans.map((scan) => scan.id));
    const projectFindings = findings.filter((finding) => scanIds.has(finding.scan_run_id));
    const confirmed = projectFindings.filter((finding) => finding.status === "confirmed").length;
    const openCount = projectFindings.filter((finding) => finding.status !== "resolved").length;
    const topRisk = projectFindings.reduce((max, finding) => Math.max(max, finding.risk_score), 0);
    const ciGate = projectFindings.some(
      (finding) =>
        finding.status === "confirmed" &&
        (finding.severity === "critical" || finding.severity === "high"),
    )
      ? "failing"
      : "passing";
    return {
      ...project,
      targets_count: projectTargets.length,
      scans_count: projectScans.length,
      open_findings: openCount,
      confirmed_findings: confirmed,
      risk_score: topRisk,
      ci_gate: ciGate,
    };
  });
}

function addAudit(
  action: string,
  objectType: string,
  objectId?: string,
  scanId?: string,
  metadata: Record<string, unknown> = {},
) {
  auditLogs.unshift({
    id: nextId("audit"),
    action,
    object_type: objectType,
    object_id: objectId ?? null,
    scan_run_id: scanId ?? null,
    metadata_json: metadata,
    created_at: new Date().toISOString(),
  });
}

function createScanForProject(
  projectId: string,
  targetId?: string | null,
  profile = "safe-active",
) {
  const scanId = nextId("scan");
  const createdAt = new Date().toISOString();
  const newScan: DemoScan = {
    id: scanId,
    project_id: projectId,
    target_id: targetId ?? null,
    status: "completed",
    profile,
    started_at: createdAt,
    finished_at: createdAt,
    model_name: "local-qwen-family",
    total_endpoints: templateEndpoints.length,
    total_findings: findings.filter((item) => item.scan_run_id === scanMainId).length,
    confirmed_findings: 11,
    needs_review_findings: 1,
    events_json: buildEvents(5),
    created_at: createdAt,
  };
  scans.unshift(newScan);

  const endpointIdMap = new Map<string, string>();
  for (const entry of templateEndpoints) {
    const endpointId = nextId("ep");
    endpoints.push({
      ...entry,
      id: endpointId,
      scan_run_id: scanId,
    });
    endpointIdMap.set(entry.path, endpointId);
  }

  const templateFindings = findings.filter((item) => item.scan_run_id === scanMainId).slice(0, 12);
  for (const templateFinding of templateFindings) {
    const newFindingId = nextId("finding");
    const newFinding: DemoFinding = {
      ...templateFinding,
      id: newFindingId,
      scan_run_id: scanId,
      endpoint_id: templateFinding.endpoint_id
        ? (endpointIdMap.get(
            endpoints.find((e) => e.id === templateFinding.endpoint_id)?.path ?? "",
          ) ?? null)
        : null,
      created_at: createdAt,
    };
    findings.unshift(newFinding);
    evidence.unshift({
      id: nextId("evidence"),
      finding_id: newFindingId,
      type: "verifier_observation",
      title: "Verifier decision and redacted evidence",
      content_text: "Synthetic demo evidence for GitHub Pages mode.",
      redacted: true,
      created_at: createdAt,
    });
  }

  reports.unshift({
    id: nextId("report_html"),
    scan_run_id: scanId,
    format: "html",
    status: "ready",
    html_path: "artifacts/report.html",
    created_at: createdAt,
  });
  reports.unshift({
    id: nextId("report_pdf"),
    scan_run_id: scanId,
    format: "pdf",
    status: "ready",
    pdf_path: "artifacts/report.pdf",
    created_at: createdAt,
  });

  addAudit("scan.completed", "scan_run", scanId, scanId, {
    profile,
    findings: newScan.total_findings,
  });
  refreshProjectStats();
  return newScan;
}

function parseBody(init: RequestInit): Record<string, unknown> {
  if (!init.body || typeof init.body !== "string") return {};
  try {
    return JSON.parse(init.body) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function ensureLeadingSlash(path: string) {
  return path.startsWith("/") ? path : `/${path}`;
}

export async function mockLogin(email: string, _password: string) {
  await delay(80);
  return {
    access_token: `demo-token-${email.replace(/[^a-z0-9]/gi, "").toLowerCase()}`,
    token_type: "bearer",
  };
}

export async function mockRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  await delay();
  const method = (init.method ?? "GET").toUpperCase();
  const cleanPath = ensureLeadingSlash(path.split("?")[0]);
  const body = parseBody(init);

  if (method === "GET" && cleanPath === "/api/overview") {
    refreshProjectStats();
    const data = {
      metrics: {
        active_projects: projects.length,
        open_findings: findings.filter((item) => item.status !== "resolved").length,
        confirmed_findings: findings.filter((item) => item.status === "confirmed").length,
        critical_assets: 1,
        mean_time_to_validate: "00:02:14",
      },
      projects: projects.slice(0, 5),
      findings: findings.slice(0, 6).map(withEndpoint),
      scans: scans.slice(0, 6),
    };
    return clone(data) as T;
  }

  if (method === "GET" && cleanPath === "/api/projects") {
    refreshProjectStats();
    return clone(projects) as T;
  }

  if (method === "POST" && cleanPath === "/api/projects") {
    const projectId = nextId("proj");
    const project: DemoProject = {
      id: projectId,
      name: String(body.name ?? "New Project"),
      description: String(body.description ?? "Created in demo mode"),
      environment: String(body.environment ?? "local_lab"),
      risk_score: 0,
      ci_gate: "passing",
      targets_count: 0,
      scans_count: 0,
      open_findings: 0,
      confirmed_findings: 0,
    };
    projects.unshift(project);
    addAudit("project.created", "project", projectId, null, { demo_mode: true });
    return clone(project) as T;
  }

  const projectById = cleanPath.match(/^\/api\/projects\/([^/]+)$/);
  if (method === "GET" && projectById) {
    const project = projects.find((item) => item.id === projectById[1]);
    if (!project) throw new Error("project not found");
    refreshProjectStats();
    return clone(project) as T;
  }

  const projectTargets = cleanPath.match(/^\/api\/projects\/([^/]+)\/targets$/);
  if (projectTargets && method === "GET") {
    return clone(targets.filter((item) => item.project_id === projectTargets[1])) as T;
  }
  if (projectTargets && method === "POST") {
    const target: DemoTarget = {
      id: nextId("target"),
      project_id: projectTargets[1],
      type: String(body.type ?? "local_url"),
      name: String(body.name ?? body.base_url ?? "Local target"),
      base_url: body.base_url ? String(body.base_url) : null,
      repo_path: body.repo_path ? String(body.repo_path) : null,
      openapi_path: body.openapi_path ? String(body.openapi_path) : null,
      docker_compose_path: body.docker_compose_path ? String(body.docker_compose_path) : null,
      scope_yaml: String(body.scope_yaml ?? defaultScope),
    };
    targets.unshift(target);
    addAudit("target.created", "target", target.id, null, { project_id: target.project_id });
    refreshProjectStats();
    return clone(target) as T;
  }

  const projectScans = cleanPath.match(/^\/api\/projects\/([^/]+)\/scans$/);
  if (projectScans && method === "GET") {
    return clone(scans.filter((item) => item.project_id === projectScans[1])) as T;
  }
  if (projectScans && method === "POST") {
    const scan = createScanForProject(
      projectScans[1],
      body.target_id ? String(body.target_id) : null,
      body.profile ? String(body.profile) : "safe-active",
    );
    return clone(scan) as T;
  }

  if (method === "GET" && cleanPath === "/api/scans") {
    return clone(scans) as T;
  }

  const scanById = cleanPath.match(/^\/api\/scans\/([^/]+)$/);
  if (scanById && method === "GET") {
    const scan = scans.find((item) => item.id === scanById[1]);
    if (!scan) throw new Error("scan not found");
    return clone(scan) as T;
  }

  const scanCancel = cleanPath.match(/^\/api\/scans\/([^/]+)\/cancel$/);
  if (scanCancel && method === "POST") {
    scans = scans.map((scan) =>
      scan.id === scanCancel[1]
        ? { ...scan, status: "cancelled", finished_at: new Date().toISOString() }
        : scan,
    );
    addAudit("scan.cancelled", "scan_run", scanCancel[1], scanCancel[1], {});
    return clone({ ok: true }) as T;
  }

  const scanRerun = cleanPath.match(/^\/api\/scans\/([^/]+)\/rerun$/);
  if (scanRerun && method === "POST") {
    const scan = scans.find((item) => item.id === scanRerun[1]);
    if (!scan) throw new Error("scan not found");
    const rerun = createScanForProject(scan.project_id, scan.target_id ?? null, scan.profile);
    return clone(rerun) as T;
  }

  const scanEndpoints = cleanPath.match(/^\/api\/scans\/([^/]+)\/endpoints$/);
  if (scanEndpoints && method === "GET") {
    return clone(endpoints.filter((item) => item.scan_run_id === scanEndpoints[1])) as T;
  }

  const scanFindings = cleanPath.match(/^\/api\/scans\/([^/]+)\/findings$/);
  if (scanFindings && method === "GET") {
    return clone(
      findings.filter((item) => item.scan_run_id === scanFindings[1]).map(withEndpoint),
    ) as T;
  }

  const scanGraph = cleanPath.match(/^\/api\/scans\/([^/]+)\/endpoint-graph$/);
  if (scanGraph && method === "GET") {
    const nodes = endpoints
      .filter((item) => item.scan_run_id === scanGraph[1])
      .map((item) => ({
        id: item.id,
        label: `${item.method} ${item.path}`,
        risk: item.risk_hints_json,
      }));
    const edges = nodes.slice(1).map((node, index) => ({
      source: nodes[index].id,
      target: node.id,
      type: "flow",
    }));
    return clone({ nodes, edges }) as T;
  }

  if (method === "GET" && cleanPath === "/api/findings") {
    return clone(findings.map(withEndpoint)) as T;
  }

  const findingById = cleanPath.match(/^\/api\/findings\/([^/]+)$/);
  if (findingById && method === "GET") {
    const finding = findings.find((item) => item.id === findingById[1]);
    if (!finding) throw new Error("finding not found");
    return clone(withEndpoint(finding)) as T;
  }

  const findingEvidence = cleanPath.match(/^\/api\/findings\/([^/]+)\/evidence$/);
  if (findingEvidence && method === "GET") {
    return clone(evidence.filter((item) => item.finding_id === findingEvidence[1])) as T;
  }

  const findingAction = cleanPath.match(
    /^\/api\/findings\/([^/]+)\/(reverify|mark-false-positive|mark-accepted-risk)$/,
  );
  if (findingAction && method === "POST") {
    const id = findingAction[1];
    const action = findingAction[2];
    findings = findings.map((item) => {
      if (item.id !== id) return item;
      if (action === "reverify")
        return { ...item, status: "confirmed", confidence: Math.max(item.confidence, 0.9) };
      if (action === "mark-false-positive")
        return { ...item, status: "false_positive", confidence: 0.35 };
      return { ...item, status: "accepted_risk" };
    });
    addAudit(`finding.${action}`, "finding", id, null, { demo_mode: true });
    refreshProjectStats();
    return clone({ ok: true }) as T;
  }

  if (method === "GET" && cleanPath === "/api/reports") {
    return clone(reports) as T;
  }

  if (method === "GET" && cleanPath === "/api/audit-logs") {
    return clone(auditLogs) as T;
  }

  if (method === "GET" && cleanPath === "/api/settings/model") {
    return clone({
      llm_provider: "local",
      llm_base_url: "mock://github-pages",
      llm_model: "qwen-family-demo",
      health: { ok: true, status: "mock" },
    }) as T;
  }

  if (method === "GET" && cleanPath === "/api/settings/policies") {
    return clone({
      require_scope_file: true,
      allow_public_targets: false,
      default_profile: "safe-active",
    }) as T;
  }

  if (method === "GET" && cleanPath === "/api/settings/tools") {
    return clone({
      enabled: [
        "semgrep_adapter",
        "http_probe_adapter",
        "openapi_contract_adapter",
        "custom_checks_adapter",
      ],
      tool_registry: [
        {
          name: "Semgrep SAST",
          category: "sast",
          adapter: "semgrep_adapter",
          mode: "passive",
          destructive: false,
          enabled_by_default: true,
          description: "Static code checks mapped to scoped target context.",
        },
        {
          name: "HTTP Probe",
          category: "runtime",
          adapter: "http_probe_adapter",
          mode: "active-safe",
          destructive: false,
          enabled_by_default: true,
          description: "Safe HTTP validation probes under request limits.",
        },
        {
          name: "Custom Checks",
          category: "policy",
          adapter: "custom_checks_adapter",
          mode: "active-safe",
          destructive: false,
          enabled_by_default: true,
          description: "Auth-diff, role-diff, schema-diff, response-diff checks.",
        },
      ],
    }) as T;
  }

  throw new Error(`Mock API: route not implemented (${method} ${cleanPath})`);
}

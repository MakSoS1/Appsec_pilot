export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

export type Project = {
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

export type Target = {
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

export type ScanRun = {
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

export type Endpoint = {
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

export type Finding = {
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
  endpoint?: Endpoint | null;
};

export type Evidence = {
  id: string;
  finding_id: string;
  type: string;
  title: string;
  content_text: string;
  artifact_path?: string | null;
  redacted: boolean;
  created_at: string;
};

export type Report = {
  id: string;
  scan_run_id: string;
  format: string;
  status: string;
  html_path?: string | null;
  pdf_path?: string | null;
  created_at: string;
};

export type AuditLog = {
  id: string;
  action: string;
  object_type: string;
  object_id?: string | null;
  scan_run_id?: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export function token() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem("appsec_token") ?? "";
}

export async function login(email = "admin@appsec.local", password = "AppSecPilot123!") {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  window.localStorage.setItem("appsec_token", data.access_token);
  return data;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", headers.get("Content-Type") ?? "application/json");
  const t = token();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 401 && typeof window !== "undefined") {
    await login();
    return request<T>(path, init);
  }
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

export function reportDownloadUrl(reportId: string, format: "html" | "pdf") {
  return `${API_URL}/api/reports/${reportId}/download.${format}`;
}

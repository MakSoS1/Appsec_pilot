export type Severity = "critical" | "high" | "medium" | "low";
export type PoCStatus = "confirmed" | "likely" | "scanner-only" | "duplicate";
export type FindingStatus = "fix-now" | "needs-review" | "waiting-dev" | "accepted" | "resolved";

export interface Finding {
  id: string;
  title: string;
  severity: Severity;
  riskScore: number;
  poc: PoCStatus;
  asset: string;
  cwe: string;
  status: FindingStatus;
  assignee: string;
  detected: string;
  endpoint?: string;
  parameter?: string;
  payload?: string;
  description?: string;
  evidence?: string;
}

export const findings: Finding[] = [
  {
    id: "APP-2026-00127",
    title: "SQL Injection in /api/users/search",
    severity: "critical",
    riskScore: 9.6,
    poc: "confirmed",
    asset: "Acme SaaS — api-gateway",
    cwe: "CWE-89",
    status: "fix-now",
    assignee: "Alex Martin",
    detected: "May 12, 2026",
    endpoint: "GET /api/users/search",
    parameter: "q",
    payload: "' OR 1=1 --",
    description:
      "The /api/users/search endpoint is vulnerable to SQL Injection via the q parameter. An attacker can manipulate the query to access or modify data in the database. Confirmed by extracting data from the users table.",
    evidence: `{\n  "id": 1,\n  "username": "admin",\n  "email": "admin@acme.com",\n  "role": "admin"\n}`,
  },
  {
    id: "APP-2026-00126",
    title: "Broken authentication — JWT signature not verified",
    severity: "critical",
    riskScore: 9.2,
    poc: "confirmed",
    asset: "Acme SaaS — auth-service",
    cwe: "CWE-347",
    status: "fix-now",
    assignee: "Priya Shah",
    detected: "May 12, 2026",
  },
  {
    id: "APP-2026-00125",
    title: "Server-Side Request Forgery in webhook proxy",
    severity: "high",
    riskScore: 8.4,
    poc: "confirmed",
    asset: "Acme SaaS — webhooks",
    cwe: "CWE-918",
    status: "needs-review",
    assignee: "Unassigned",
    detected: "May 11, 2026",
  },
  {
    id: "APP-2026-00124",
    title: "Reflected XSS in /search results page",
    severity: "high",
    riskScore: 7.9,
    poc: "likely",
    asset: "Marketing Portal",
    cwe: "CWE-79",
    status: "waiting-dev",
    assignee: "Diego Romero",
    detected: "May 10, 2026",
  },
  {
    id: "APP-2026-00123",
    title: "IDOR on /api/orders/:id",
    severity: "high",
    riskScore: 7.6,
    poc: "confirmed",
    asset: "Acme SaaS — orders",
    cwe: "CWE-639",
    status: "fix-now",
    assignee: "Alex Martin",
    detected: "May 10, 2026",
  },
  {
    id: "APP-2026-00122",
    title: "Outdated dependency: lodash 4.17.10",
    severity: "medium",
    riskScore: 5.4,
    poc: "scanner-only",
    asset: "Marketing Portal",
    cwe: "CWE-1104",
    status: "needs-review",
    assignee: "Unassigned",
    detected: "May 9, 2026",
  },
  {
    id: "APP-2026-00121",
    title: "Missing rate limiting on /api/login",
    severity: "medium",
    riskScore: 5.1,
    poc: "likely",
    asset: "Acme SaaS — auth-service",
    cwe: "CWE-307",
    status: "waiting-dev",
    assignee: "Priya Shah",
    detected: "May 8, 2026",
  },
  {
    id: "APP-2026-00120",
    title: "Verbose error message leaks stack trace",
    severity: "low",
    riskScore: 3.2,
    poc: "scanner-only",
    asset: "Internal Admin",
    cwe: "CWE-209",
    status: "accepted",
    assignee: "Mei Lin",
    detected: "May 7, 2026",
  },
];

export interface Project {
  id: string;
  name: string;
  owner: string;
  env: "prod" | "staging" | "dev";
  lastScan: string;
  riskScore: number;
  open: number;
  poc: number;
  compliance: "passing" | "warning" | "failing";
  internetFacing: boolean;
}

export const projects: Project[] = [
  {
    id: "p1",
    name: "Acme SaaS — api-gateway",
    owner: "Platform Team",
    env: "prod",
    lastScan: "2h ago",
    riskScore: 9.4,
    open: 23,
    poc: 7,
    compliance: "failing",
    internetFacing: true,
  },
  {
    id: "p2",
    name: "Acme SaaS — auth-service",
    owner: "Identity Team",
    env: "prod",
    lastScan: "3h ago",
    riskScore: 8.8,
    open: 14,
    poc: 4,
    compliance: "warning",
    internetFacing: true,
  },
  {
    id: "p3",
    name: "Acme SaaS — orders",
    owner: "Commerce Team",
    env: "prod",
    lastScan: "5h ago",
    riskScore: 7.2,
    open: 11,
    poc: 3,
    compliance: "warning",
    internetFacing: true,
  },
  {
    id: "p4",
    name: "Acme SaaS — webhooks",
    owner: "Platform Team",
    env: "prod",
    lastScan: "1d ago",
    riskScore: 7.0,
    open: 8,
    poc: 2,
    compliance: "warning",
    internetFacing: true,
  },
  {
    id: "p5",
    name: "Marketing Portal",
    owner: "Growth Team",
    env: "prod",
    lastScan: "1d ago",
    riskScore: 5.6,
    open: 9,
    poc: 1,
    compliance: "passing",
    internetFacing: true,
  },
  {
    id: "p6",
    name: "Internal Admin",
    owner: "IT Ops",
    env: "staging",
    lastScan: "2d ago",
    riskScore: 3.8,
    open: 4,
    poc: 0,
    compliance: "passing",
    internetFacing: false,
  },
  {
    id: "p7",
    name: "Mobile API",
    owner: "Mobile Team",
    env: "prod",
    lastScan: "6h ago",
    riskScore: 6.2,
    open: 7,
    poc: 1,
    compliance: "warning",
    internetFacing: true,
  },
  {
    id: "p8",
    name: "Data Warehouse ETL",
    owner: "Data Team",
    env: "prod",
    lastScan: "12h ago",
    riskScore: 4.1,
    open: 3,
    poc: 0,
    compliance: "passing",
    internetFacing: false,
  },
];

export interface Run {
  id: string;
  project: string;
  startedAt: string;
  duration: string;
  status: "running" | "completed" | "failed";
  findings: number;
  pocs: number;
}

export const runs: Run[] = [
  {
    id: "Run #7842",
    project: "Acme SaaS — api-gateway",
    startedAt: "May 12, 10:31 AM",
    duration: "14m 22s",
    status: "completed",
    findings: 23,
    pocs: 7,
  },
  {
    id: "Run #7841",
    project: "Acme SaaS — auth-service",
    startedAt: "May 12, 09:02 AM",
    duration: "11m 04s",
    status: "completed",
    findings: 14,
    pocs: 4,
  },
  {
    id: "Run #7840",
    project: "Marketing Portal",
    startedAt: "May 12, 08:14 AM",
    duration: "8m 47s",
    status: "completed",
    findings: 9,
    pocs: 1,
  },
  {
    id: "Run #7839",
    project: "Mobile API",
    startedAt: "May 12, 06:00 AM",
    duration: "—",
    status: "running",
    findings: 5,
    pocs: 1,
  },
  {
    id: "Run #7838",
    project: "Internal Admin",
    startedAt: "May 11, 11:42 PM",
    duration: "6m 13s",
    status: "completed",
    findings: 4,
    pocs: 0,
  },
  {
    id: "Run #7837",
    project: "Data Warehouse ETL",
    startedAt: "May 11, 08:20 PM",
    duration: "—",
    status: "failed",
    findings: 0,
    pocs: 0,
  },
];

export const trendData = [
  { date: "Apr 13", critical: 12, high: 28, medium: 41, low: 22 },
  { date: "Apr 20", critical: 10, high: 25, medium: 38, low: 24 },
  { date: "Apr 27", critical: 14, high: 30, medium: 42, low: 21 },
  { date: "May 04", critical: 11, high: 27, medium: 39, low: 19 },
  { date: "May 11", critical: 9, high: 24, medium: 36, low: 18 },
  { date: "May 12", critical: 8, high: 22, medium: 34, low: 17 },
];

export const severityDistribution = [
  { name: "Critical", value: 8, key: "critical" },
  { name: "High", value: 22, key: "high" },
  { name: "Medium", value: 34, key: "medium" },
  { name: "Low", value: 17, key: "low" },
];

export const severityColor: Record<Severity, string> = {
  critical: "bg-critical text-critical-foreground",
  high: "bg-high text-high-foreground",
  medium: "bg-medium text-medium-foreground",
  low: "bg-low text-low-foreground",
};

export const pocLabel: Record<PoCStatus, string> = {
  confirmed: "PoC confirmed",
  likely: "Likely exploitable",
  "scanner-only": "Scanner only",
  duplicate: "Duplicate",
};

export const statusLabel: Record<FindingStatus, string> = {
  "fix-now": "Fix now",
  "needs-review": "Needs review",
  "waiting-dev": "Waiting for dev",
  accepted: "Accepted risk",
  resolved: "Resolved",
};

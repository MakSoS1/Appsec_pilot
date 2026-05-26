import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, Bug, CheckCircle2, Play, ShieldAlert, Timer } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, PageHeader, SectionTitle, SeverityBadge } from "@/components/ui-kit";
import { api, Finding, Project, ScanRun } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/")({ component: Overview });

type OverviewData = {
  metrics: Record<string, number | string>;
  projects: Project[];
  findings: Finding[];
  scans: ScanRun[];
};

function Metric({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs font-medium text-muted-foreground">{label}</div>
          <div className="mt-1.5 text-2xl font-semibold tracking-tight">{value}</div>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-accent-foreground">
          <Icon className="h-4.5 w-4.5" />
        </div>
      </div>
    </Card>
  );
}

function Overview() {
  const { data, loading, reload } = useAsyncData<OverviewData>(() => api.get("/api/overview"), []);
  async function startScan() {
    const project = data?.projects[0];
    if (!project) return;
    await api.post(`/api/projects/${project.id}/scans`, {
      profile: "safe-active",
      start_immediately: true,
    });
    await reload();
  }
  return (
    <AppLayout>
      <PageHeader
        title="Security Overview"
        description="Live posture, validated risks, and agent activity across authorized targets."
        actions={
          <Button variant="primary" onClick={() => void startScan()}>
            <Play className="h-4 w-4" />
            New scan
          </Button>
        }
      />
      {loading && <Card>Loading API data...</Card>}
      {data && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
            <Metric
              label="Active projects"
              value={data.metrics.active_projects ?? 0}
              icon={Activity}
            />
            <Metric label="Open findings" value={data.metrics.open_findings ?? 0} icon={Bug} />
            <Metric
              label="Confirmed"
              value={data.metrics.confirmed_findings ?? 0}
              icon={ShieldAlert}
            />
            <Metric
              label="Critical assets"
              value={data.metrics.critical_assets ?? 0}
              icon={CheckCircle2}
            />
            <Metric
              label="Mean validation"
              value={data.metrics.mean_time_to_validate ?? "n/a"}
              icon={Timer}
            />
          </div>
          <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <SectionTitle
                title="Latest findings"
                subtitle="Verifier-backed evidence from recent scans"
              />
              <div className="space-y-3">
                {data.findings.map((f) => (
                  <Link
                    key={f.id}
                    to="/findings/$id"
                    params={{ id: f.id }}
                    className="flex items-center justify-between rounded-md border border-border p-3 hover:bg-muted/40"
                  >
                    <div>
                      <div className="text-sm font-semibold">{f.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {f.endpoint?.method} {f.endpoint?.path} · {f.cwe_id}
                      </div>
                    </div>
                    <SeverityBadge severity={f.severity} />
                  </Link>
                ))}
              </div>
            </Card>
            <Card>
              <SectionTitle title="Recent scans" subtitle="Agent lifecycle" />
              <div className="space-y-3">
                {data.scans.map((s) => (
                  <Link
                    key={s.id}
                    to="/scans/$id"
                    params={{ id: s.id }}
                    className="block rounded-md border border-border p-3 hover:bg-muted/40"
                  >
                    <div className="text-sm font-semibold">{s.id}</div>
                    <div className="text-xs text-muted-foreground">
                      {s.status} · {s.total_findings} findings
                    </div>
                  </Link>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppLayout>
  );
}

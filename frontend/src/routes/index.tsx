import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Activity, Bug, CheckCircle2, Play, ShieldAlert, Timer } from "lucide-react";
import { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { ScanTemplateDialog } from "@/components/scan-template-dialog";
import { Button, Card, PageHeader, SectionTitle, SeverityBadge } from "@/components/ui-kit";
import { api, Finding, Project, ScanRun } from "@/lib/api";
import { ScanTemplate } from "@/lib/scan-templates";
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
  const navigate = useNavigate();
  const { data, loading, reload } = useAsyncData<OverviewData>(() => api.get("/api/overview"), []);
  const [templateOpen, setTemplateOpen] = useState(false);

  async function startScanFromTemplate(template: ScanTemplate) {
    const project = data?.projects[0];
    if (!project) return;
    const scan = await api.post<ScanRun>(`/api/projects/${project.id}/scans`, {
      profile: template.profile,
      start_immediately: true,
    });
    setTemplateOpen(false);
    await reload();
    await navigate({ to: "/scans/$id", params: { id: scan.id } });
  }
  return (
    <AppLayout>
      <PageHeader
        title="Обзор безопасности"
        description="Текущая картина рисков, верифицированные находки и активность агента."
        actions={
          <Button variant="primary" onClick={() => setTemplateOpen(true)}>
            <Play className="h-4 w-4" />
            Новый скан
          </Button>
        }
      />
      {loading && <Card>Загрузка данных...</Card>}
      {data && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
            <Metric
              label="Активные проекты"
              value={data.metrics.active_projects ?? 0}
              icon={Activity}
            />
            <Metric label="Открытые находки" value={data.metrics.open_findings ?? 0} icon={Bug} />
            <Metric
              label="Подтверждено"
              value={data.metrics.confirmed_findings ?? 0}
              icon={ShieldAlert}
            />
            <Metric
              label="Критичные активы"
              value={data.metrics.critical_assets ?? 0}
              icon={CheckCircle2}
            />
            <Metric
              label="Среднее время верификации"
              value={data.metrics.mean_time_to_validate ?? "n/a"}
              icon={Timer}
            />
          </div>
          <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <SectionTitle
                title="Последние находки"
                subtitle="Подтвержденные данные из последних запусков"
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
              <SectionTitle title="Последние сканы" subtitle="Этапы пайплайна" />
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
                      {s.status} · {s.total_findings} находок
                    </div>
                  </Link>
                ))}
              </div>
            </Card>
          </div>
          <ScanTemplateDialog
            open={templateOpen}
            title="Шаблоны сканирования"
            onClose={() => setTemplateOpen(false)}
            onSelect={(template) => void startScanFromTemplate(template)}
          />
        </>
      )}
    </AppLayout>
  );
}

import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { PlayCircle, Plus } from "lucide-react";
import { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { ScanTemplateDialog } from "@/components/scan-template-dialog";
import { Button, Card, PageHeader, SectionTitle, SeverityBadge } from "@/components/ui-kit";
import { api, Endpoint, Finding, Project, ScanRun, Target } from "@/lib/api";
import { ScanTemplate } from "@/lib/scan-templates";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/projects/$projectId")({ component: ProjectDetail });

const defaultScope = `project_name: "fastapi-vuln-demo"\nenvironment: "local_lab"\nallowed_targets:\n  - host: "localhost"\n    ports: [8008, 3000, 8081]\n    schemes: ["http"]\nallowed_http_methods: [GET, POST, PUT, PATCH, DELETE]\nrequest_limits:\n  max_requests_total: 120\n  max_requests_per_minute: 60\n  max_concurrent_requests: 4\n  timeout_seconds: 10\nallowed_check_categories: [access_control_detection, misconfiguration_detection, sensitive_data_exposure_detection, api_contract_detection]\nblocked_check_categories: [credential_theft, persistence, external_reconnaissance, c2, malware_execution]\nevidence:\n  store_http_requests: true\n  store_http_responses: true\n  redact_secrets: true\n`;

function ProjectDetail() {
  const { projectId } = Route.useParams();
  const navigate = useNavigate();
  const { data, reload } = useAsyncData(async () => {
    const [project, targets, scans] = await Promise.all([
      api.get<Project>(`/api/projects/${projectId}`),
      api.get<Target[]>(`/api/projects/${projectId}/targets`),
      api.get<ScanRun[]>(`/api/projects/${projectId}/scans`),
    ]);
    const latest = scans[0];
    const [endpoints, findings] = latest
      ? await Promise.all([
          api.get<Endpoint[]>(`/api/scans/${latest.id}/endpoints`),
          api.get<Finding[]>(`/api/scans/${latest.id}/findings`),
        ])
      : [[], []];
    return { project, targets, scans, endpoints, findings };
  }, [projectId]);
  const [baseUrl, setBaseUrl] = useState("http://localhost:8008");
  const [scanTargetId, setScanTargetId] = useState<string | null>(null);

  async function addTarget() {
    await api.post(`/api/projects/${projectId}/targets`, {
      type: "local_url",
      name: baseUrl,
      base_url: baseUrl,
      scope_yaml: defaultScope,
    });
    await reload();
  }
  async function startScanFromTemplate(template: ScanTemplate) {
    const scan = await api.post<ScanRun>(`/api/projects/${projectId}/scans`, {
      target_id:
        scanTargetId && scanTargetId !== "__no_target__" ? scanTargetId : data?.targets[0]?.id,
      profile: template.profile,
      start_immediately: true,
    });
    setScanTargetId(null);
    await reload();
    await navigate({ to: "/scans/$id", params: { id: scan.id } });
  }

  return (
    <AppLayout>
      {data && (
        <>
          <PageHeader
            title={data.project.name}
            description={data.project.description}
            actions={
              <>
                <Button variant="outline" onClick={() => void addTarget()}>
                  <Plus className="h-4 w-4" />
                  Добавить цель
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setScanTargetId(data.targets[0]?.id ?? "__no_target__")}
                >
                  <PlayCircle className="h-4 w-4" />
                  Запустить скан
                </Button>
              </>
            }
          />
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
            <Card className="lg:col-span-4">
              <SectionTitle
                title="Настройка цели"
                subtitle="Local URL, scope и профиль сканирования"
              />
              <label className="text-sm font-medium">
                Base URL
                <input
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  className="mt-1 h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                />
              </label>
              <pre className="mt-3 max-h-52 overflow-auto rounded-md border border-border bg-muted p-3 text-xs">
                {defaultScope}
              </pre>
            </Card>
            <Card className="lg:col-span-8">
              <SectionTitle title="Цели" />
              <div className="space-y-2">
                {data.targets.map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center justify-between rounded-md border border-border p-3"
                  >
                    <div>
                      <div className="text-sm font-semibold">{t.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {t.type} · {t.base_url ?? t.repo_path ?? t.openapi_path}
                      </div>
                    </div>
                    <Button variant="outline" onClick={() => setScanTargetId(t.id)}>
                      Скан
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
            <Card className="lg:col-span-6">
              <SectionTitle title="Последние endpoint'ы" />
              <div className="space-y-2">
                {data.endpoints.map((e) => (
                  <div key={e.id} className="rounded-md border border-border p-2 text-sm">
                    <span className="font-semibold">{e.method}</span> {e.path}
                    <span className="ml-2 text-xs text-muted-foreground">{e.framework}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card className="lg:col-span-6">
              <SectionTitle title="Последние находки" />
              <div className="space-y-2">
                {data.findings.map((f) => (
                  <div
                    key={f.id}
                    className="flex items-center justify-between rounded-md border border-border p-2 text-sm"
                  >
                    <span>{f.title}</span>
                    <SeverityBadge severity={f.severity} />
                  </div>
                ))}
              </div>
            </Card>
          </div>
          <ScanTemplateDialog
            open={scanTargetId !== null}
            title="Шаблоны сканирования"
            onClose={() => setScanTargetId(null)}
            onSelect={(template) => void startScanFromTemplate(template)}
          />
        </>
      )}
    </AppLayout>
  );
}

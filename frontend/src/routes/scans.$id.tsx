import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, RefreshCw, XCircle } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, PageHeader, SectionTitle, SeverityBadge } from "@/components/ui-kit";
import { api, Endpoint, Finding, ScanRun, scanLogsUrl } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/scans/$id")({ component: ScanDetail });

function ScanDetail() {
  const { id } = Route.useParams();
  const { data, reload } = useAsyncData(async () => {
    const [scan, endpoints, findings, graph] = await Promise.all([
      api.get<ScanRun>(`/api/scans/${id}`),
      api.get<Endpoint[]>(`/api/scans/${id}/endpoints`),
      api.get<Finding[]>(`/api/scans/${id}/findings`),
      api.get<{ nodes: any[]; edges: any[] }>(`/api/scans/${id}/endpoint-graph`),
    ]);
    return { scan, endpoints, findings, graph };
  }, [id]);
  async function cancel() {
    await api.post(`/api/scans/${id}/cancel`);
    await reload();
  }
  async function rerun() {
    await api.post(`/api/scans/${id}/rerun`);
    await reload();
  }
  return (
    <AppLayout>
      {data && (
        <>
          <PageHeader
            title={`Скан ${data.scan.id}`}
            description={`${data.scan.status} · ${data.scan.profile} · ${data.scan.model_name}`}
            actions={
              <>
                <Button variant="outline" onClick={() => void reload()}>
                  <RefreshCw className="h-4 w-4" />
                  Обновить
                </Button>
                <Button variant="outline" onClick={() => void cancel()}>
                  <XCircle className="h-4 w-4" />
                  Отменить
                </Button>
                <Button variant="primary" onClick={() => void rerun()}>
                  Повторить
                </Button>
              </>
            }
          />
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
            <Card className="lg:col-span-7">
              <SectionTitle
                title="Хронология этапов"
                action={
                  <a className="text-xs text-primary" href={scanLogsUrl(id)}>
                    <Download className="mr-1 inline h-3 w-3" />
                    Логи
                  </a>
                }
              />
              <ol className="relative space-y-4 border-l-2 border-border pl-6">
                {data.scan.events_json.map((e, i) => (
                  <li key={i} className="relative">
                    <span className="absolute -left-[31px] flex h-6 w-6 items-center justify-center rounded-full border-2 border-background bg-success text-success-foreground text-xs">
                      {i + 1}
                    </span>
                    <div className="text-sm font-semibold">{e.stage}</div>
                    <div className="text-xs text-muted-foreground">{e.message}</div>
                  </li>
                ))}
              </ol>
            </Card>
            <Card className="lg:col-span-5">
              <SectionTitle
                title="Граф endpoint'ов"
                subtitle={`${data.graph.nodes.length} узлов · ${data.graph.edges.length} связей`}
              />
              <div className="grid grid-cols-1 gap-2">
                {data.endpoints.map((e) => (
                  <div key={e.id} className="rounded-md border border-border p-2 text-sm">
                    <span className="font-semibold">{e.method}</span> {e.path}
                    <div className="text-xs text-muted-foreground">
                      {e.framework} · {e.risk_hints_json.join(", ") || "baseline"}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
            <Card className="lg:col-span-12">
              <SectionTitle title="Находки" />
              <div className="space-y-2">
                {data.findings.map((f) => (
                  <div
                    key={f.id}
                    className="flex items-center justify-between rounded-md border border-border p-3"
                  >
                    <div>
                      <Link
                        to="/findings/$id"
                        params={{ id: f.id }}
                        className="text-sm font-semibold text-primary hover:underline"
                      >
                        {f.title}
                      </Link>
                      <div className="text-xs text-muted-foreground">
                        {f.status} · {f.endpoint?.method} {f.endpoint?.path}
                      </div>
                    </div>
                    <SeverityBadge severity={f.severity} />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppLayout>
  );
}

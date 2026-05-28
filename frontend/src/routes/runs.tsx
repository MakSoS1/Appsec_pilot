import { createFileRoute, Link } from "@tanstack/react-router";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader } from "@/components/ui-kit";
import { api, ScanRun } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/runs")({ component: Runs });

function Runs() {
  const { data: scans } = useAsyncData<ScanRun[]>(() => api.get("/api/scans"), []);
  return (
    <AppLayout>
      <PageHeader
        title="Запуски агента"
        description="Аудируемая лента всех действий сканирования."
      />
      <Card className="p-0">
        <ul className="divide-y divide-border">
          {scans?.map((s) => (
            <li key={s.id}>
              <Link
                to="/scans/$id"
                params={{ id: s.id }}
                className="flex items-center gap-3 px-4 py-3 hover:bg-muted/40"
              >
                <RunIcon status={s.status} />
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold text-primary">{s.id}</div>
                  <div className="text-xs text-muted-foreground">
                    {s.status} · {s.profile} · {s.total_endpoints} endpoint'ов
                  </div>
                </div>
                <div className="text-right text-xs">
                  <div className="font-semibold">{s.total_findings}</div>
                  <div className="text-muted-foreground">находок</div>
                </div>
                <div className="text-right text-xs">
                  <div className="font-semibold text-critical">{s.confirmed_findings}</div>
                  <div className="text-muted-foreground">подтверждено</div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </AppLayout>
  );
}

function RunIcon({ status }: { status: string }) {
  if (
    [
      "queued",
      "preparing_environment",
      "mapping_application",
      "building_context",
      "generating_hypotheses",
      "running_checks",
      "verifying_findings",
      "generating_report",
    ].includes(status)
  )
    return (
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-info/10 text-info">
        <Loader2 className="h-4 w-4 animate-spin" />
      </span>
    );
  if (status === "failed" || status === "cancelled")
    return (
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-critical/10 text-critical">
        <XCircle className="h-4 w-4" />
      </span>
    );
  return (
    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-success/10 text-success">
      <CheckCircle2 className="h-4 w-4" />
    </span>
  );
}

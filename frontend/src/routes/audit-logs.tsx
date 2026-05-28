import { createFileRoute } from "@tanstack/react-router";
import { ScrollText } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader } from "@/components/ui-kit";
import { api, AuditLog } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/audit-logs")({ component: AuditLogs });

function AuditLogs() {
  const { data } = useAsyncData<AuditLog[]>(() => api.get("/api/audit-logs"), []);
  return (
    <AppLayout>
      <PageHeader
        title="Журнал аудита"
        description="Все действия пользователя и агента для последующей проверки."
      />
      <Card className="p-0">
        <ul className="divide-y divide-border">
          {data?.map((a) => (
            <li key={a.id} className="flex gap-3 px-4 py-3">
              <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-accent text-accent-foreground">
                <ScrollText className="h-4 w-4" />
              </div>
              <div>
                <div className="text-sm font-semibold">{a.action}</div>
                <div className="text-xs text-muted-foreground">
                  {a.object_type} · {a.object_id ?? "система"} ·{" "}
                  {new Date(a.created_at).toLocaleString()}
                </div>
                <pre className="mt-2 rounded-md bg-muted p-2 text-xs">
                  {JSON.stringify(a.metadata_json, null, 2)}
                </pre>
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </AppLayout>
  );
}

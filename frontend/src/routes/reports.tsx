import { createFileRoute } from "@tanstack/react-router";
import { Download, FileText } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, PageHeader } from "@/components/ui-kit";
import { api, reportDownloadUrl, Report } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/reports")({ component: Reports });

function Reports() {
  const { data: reports } = useAsyncData<Report[]>(() => api.get("/api/reports"), []);
  return (
    <AppLayout>
      <PageHeader
        title="Отчеты"
        description="Экспорты для разработки, безопасности и комплаенса."
      />
      <Card className="p-0">
        <ul className="divide-y divide-border">
          {reports?.map((r) => (
            <li key={r.id} className="flex items-center gap-4 px-4 py-3 hover:bg-muted/40">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-accent text-accent-foreground">
                <FileText className="h-5 w-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium">
                  {r.format.toUpperCase()} отчет · {r.scan_run_id}
                </div>
                <div className="text-xs text-muted-foreground">
                  {r.status} · {new Date(r.created_at).toLocaleString()}
                </div>
              </div>
              {r.html_path && (
                <a href={reportDownloadUrl(r.id, "html")}>
                  <Button variant="outline" size="sm">
                    <Download className="h-3.5 w-3.5" />
                    HTML
                  </Button>
                </a>
              )}
              {r.pdf_path && (
                <a href={reportDownloadUrl(r.id, "pdf")}>
                  <Button variant="outline" size="sm">
                    <Download className="h-3.5 w-3.5" />
                    PDF
                  </Button>
                </a>
              )}
            </li>
          ))}
        </ul>
      </Card>
    </AppLayout>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { Filter } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, PageHeader, SeverityBadge } from "@/components/ui-kit";
import { api, Finding } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/findings/")({ component: Findings });

function Findings() {
  const { data } = useAsyncData<Finding[]>(() => api.get("/api/findings"), []);
  return (
    <AppLayout>
      <PageHeader
        title="Findings"
        description="Confirmed and review-needed findings with evidence."
        actions={
          <Button variant="outline">
            <Filter className="h-4 w-4" />
            Filters
          </Button>
        }
      />
      <Card className="p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-3">Severity</th>
              <th>Title</th>
              <th>Endpoint</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>CWE</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data?.map((f) => (
              <tr key={f.id} className="hover:bg-muted/40">
                <td className="px-4 py-3">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td>
                  <Link
                    to="/findings/$id"
                    params={{ id: f.id }}
                    className="font-medium text-primary hover:underline"
                  >
                    {f.title}
                  </Link>
                </td>
                <td className="text-muted-foreground">
                  {f.endpoint?.method} {f.endpoint?.path}
                </td>
                <td>{f.status}</td>
                <td>{Math.round(f.confidence * 100)}%</td>
                <td>{f.cwe_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </AppLayout>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, CheckCircle2, Download, RefreshCw, ShieldCheck, XCircle } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, SeverityBadge } from "@/components/ui-kit";
import { API_URL, api, Evidence, Finding } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/findings/$id")({ component: FindingDetail });

function FindingDetail() {
  const { id } = Route.useParams();
  const { data, reload } = useAsyncData(
    async () => ({
      finding: await api.get<Finding>(`/api/findings/${id}`),
      evidence: await api.get<Evidence[]>(`/api/findings/${id}/evidence`),
    }),
    [id],
  );
  async function reverify() {
    await api.post(`/api/findings/${id}/reverify`);
    await reload();
  }
  async function falsePositive() {
    await api.post(`/api/findings/${id}/mark-false-positive`);
    await reload();
  }
  async function acceptRisk() {
    await api.post(`/api/findings/${id}/mark-accepted-risk`);
    await reload();
  }
  const f = data?.finding;
  return (
    <AppLayout>
      {f && (
        <>
          <div className="mb-4 flex items-center gap-3 text-sm text-muted-foreground">
            <Link to="/findings" className="inline-flex items-center gap-1 hover:text-foreground">
              <ArrowLeft className="h-3.5 w-3.5" />
              Findings
            </Link>
            <span>/</span>
            <span className="font-medium text-foreground">{f.id}</span>
          </div>
          <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">{f.title}</h1>
              <div className="mt-1 text-sm text-muted-foreground">
                {f.cwe_id} · {f.owasp_category} · {f.endpoint?.method} {f.endpoint?.path}
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => void reverify()}>
                <RefreshCw className="h-4 w-4" />
                Reverify
              </Button>
              <Button variant="outline" onClick={() => void falsePositive()}>
                <XCircle className="h-4 w-4" />
                False positive
              </Button>
              <Button variant="primary" onClick={() => void acceptRisk()}>
                <ShieldCheck className="h-4 w-4" />
                Accept risk
              </Button>
            </div>
          </div>
          <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-5">
            <Card className="p-4">
              <div className="text-xs text-muted-foreground">Severity</div>
              <div className="mt-2">
                <SeverityBadge severity={f.severity} />
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-xs text-muted-foreground">Risk</div>
              <div className="mt-1 text-2xl font-semibold">{f.risk_score}</div>
            </Card>
            <Card className="p-4">
              <div className="text-xs text-muted-foreground">Status</div>
              <div className="mt-1 text-sm font-semibold">{f.status}</div>
            </Card>
            <Card className="p-4">
              <div className="text-xs text-muted-foreground">Confidence</div>
              <div className="mt-1 text-sm font-semibold">{Math.round(f.confidence * 100)}%</div>
            </Card>
            <Card className="p-4">
              <div className="text-xs text-muted-foreground">Assignee</div>
              <div className="mt-1 text-sm font-semibold">{f.assigned_to}</div>
            </Card>
          </div>
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
            <div className="space-y-5 lg:col-span-4">
              <Card>
                <h2 className="mb-2 text-sm font-semibold">Summary</h2>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.description}</p>
              </Card>
              <Card>
                <h2 className="mb-2 text-sm font-semibold">Business Impact</h2>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.business_impact}</p>
              </Card>
              <Card>
                <h2 className="mb-2 text-sm font-semibold">Remediation</h2>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.remediation}</p>
              </Card>
            </div>
            <div className="space-y-5 lg:col-span-8">
              <Card>
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="text-sm font-semibold">Evidence timeline</h2>
                  <CheckCircle2 className="h-4 w-4 text-success" />
                </div>
                <div className="space-y-3">
                  {data.evidence.map((ev) => (
                    <div key={ev.id} className="rounded-md border border-border p-3">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-semibold">{ev.title}</div>
                        <a
                          href={`${API_URL}/api/evidence/${ev.id}/download`}
                          className="text-xs text-primary"
                        >
                          <Download className="mr-1 inline h-3 w-3" />
                          Download
                        </a>
                      </div>
                      <pre className="mt-2 overflow-auto rounded-md bg-muted p-3 text-xs">
                        {ev.content_text}
                      </pre>
                    </div>
                  ))}
                </div>
              </Card>
              <Card>
                <h2 className="mb-2 text-sm font-semibold">Suggested test</h2>
                <pre className="overflow-auto rounded-md border border-border bg-muted p-3 text-xs">{`// Regression check\n// 1. Authenticate as regular user\n// 2. Request ${f.endpoint?.method ?? "GET"} ${f.endpoint?.path ?? "/"}\n// 3. Assert cross-user or admin-only access is denied by server-side policy`}</pre>
              </Card>
            </div>
          </div>
        </>
      )}
    </AppLayout>
  );
}

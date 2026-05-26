import { createFileRoute } from "@tanstack/react-router";
import { GitPullRequest, Wand2, Sparkles, ExternalLink } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader, Button, SeverityBadge } from "@/components/ui-kit";
import { findings } from "@/lib/mock-data";

export const Route = createFileRoute("/fixes")({
  head: () => ({
    meta: [
      { title: "Fixes — AppSec Pilot" },
      {
        name: "description",
        content: "AI-suggested code fixes, draft pull requests and remediation guidance.",
      },
    ],
  }),
  component: Fixes,
});

const fixable = findings
  .filter((f) => f.severity === "critical" || f.severity === "high")
  .slice(0, 4);

function Fixes() {
  return (
    <AppLayout>
      <PageHeader
        title="Fixes & Remediation"
        description="Suggested patches your engineers can review, edit and ship."
      />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {fixable.map((f) => (
          <Card key={f.id}>
            <div className="mb-3 flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {f.id} · {f.cwe}
                </div>
                <h3 className="mt-1 text-base font-semibold leading-snug">{f.title}</h3>
              </div>
              <SeverityBadge severity={f.severity} />
            </div>
            <div className="mb-3 flex items-center gap-2 text-xs">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span className="text-muted-foreground">Suggested by AppSec Pilot AI v2.1</span>
              <span className="ml-auto rounded bg-success/10 px-2 py-0.5 font-medium text-success">
                High confidence
              </span>
            </div>
            <pre className="mb-3 overflow-x-auto rounded-md border border-border bg-muted/40 p-3 text-[11px] leading-relaxed">
              {`- String sql = "SELECT * FROM users WHERE name LIKE '%" + q + "%'";
+ String sql = "SELECT * FROM users WHERE name LIKE ?";
+ PreparedStatement stmt = conn.prepareStatement(sql);
+ stmt.setString(1, "%" + q + "%");`}
            </pre>
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="primary" size="sm">
                <GitPullRequest className="h-3.5 w-3.5" />
                Open draft PR
              </Button>
              <Button variant="outline" size="sm">
                <Wand2 className="h-3.5 w-3.5" />
                Refine with AI
              </Button>
              <Button variant="ghost" size="sm">
                View finding <ExternalLink className="h-3.5 w-3.5" />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, PlayCircle } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Button, Card, PageHeader } from "@/components/ui-kit";
import { api, Project } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/assets")({ component: Projects });

function Projects() {
  const {
    data: projects,
    loading,
    reload,
  } = useAsyncData<Project[]>(() => api.get("/api/projects"), []);
  async function createProject() {
    await api.post("/api/projects", {
      name: "New Local Lab",
      description: "Created from UI",
      environment: "local_lab",
    });
    await reload();
  }
  return (
    <AppLayout>
      <PageHeader
        title="Assets"
        description="Inventory of applications, APIs, and local lab targets."
        actions={
          <Button variant="primary" onClick={() => void createProject()}>
            <Plus className="h-4 w-4" />
            Create project
          </Button>
        }
      />
      {loading && <Card>Loading projects...</Card>}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {projects?.map((p) => (
          <Card key={p.id}>
            <div className="flex items-start justify-between">
              <div>
                <Link
                  to="/projects/$projectId"
                  params={{ projectId: p.id }}
                  className="text-base font-semibold hover:underline"
                >
                  {p.name}
                </Link>
                <p className="mt-1 text-sm text-muted-foreground">{p.description}</p>
              </div>
              <span className="rounded bg-muted px-2 py-0.5 text-xs uppercase">
                {p.environment}
              </span>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-xs text-muted-foreground">Targets</div>
                <div className="font-semibold">{p.targets_count}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Confirmed</div>
                <div className="font-semibold text-critical">{p.confirmed_findings}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">CI gate</div>
                <div className="font-semibold">{p.ci_gate}</div>
              </div>
            </div>
            <Button
              className="mt-4 w-full"
              variant="outline"
              onClick={() =>
                void api
                  .post(`/api/projects/${p.id}/scans`, {
                    profile: "safe-active",
                    start_immediately: true,
                  })
                  .then(reload)
              }
            >
              <PlayCircle className="h-4 w-4" />
              Start scan
            </Button>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}

import { createFileRoute, Link, Outlet, useLocation, useNavigate } from "@tanstack/react-router";
import { ExternalLink, Plus, PlayCircle } from "lucide-react";
import { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { ScanTemplateDialog } from "@/components/scan-template-dialog";
import { Button, Card, PageHeader } from "@/components/ui-kit";
import { api, Project, ScanRun } from "@/lib/api";
import { ScanTemplate } from "@/lib/scan-templates";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/projects")({ component: Projects });

function Projects() {
  const { pathname } = useLocation();
  const inProjectDetailRoute = /\/projects\/[^/]+/.test(pathname);
  const navigate = useNavigate();
  const {
    data: projects,
    loading,
    reload,
  } = useAsyncData<Project[]>(() => api.get("/api/projects"), []);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [creatingScan, setCreatingScan] = useState(false);

  async function createProject() {
    await api.post("/api/projects", {
      name: "Новый проект",
      description: "Создано из интерфейса",
      environment: "local_lab",
    });
    await reload();
  }

  async function startScanFromTemplate(template: ScanTemplate) {
    if (!selectedProjectId || creatingScan) return;
    setCreatingScan(true);
    try {
      const scan = await api.post<ScanRun>(`/api/projects/${selectedProjectId}/scans`, {
        profile: template.profile,
        start_immediately: true,
      });
      setSelectedProjectId(null);
      await reload();
      await navigate({ to: "/scans/$id", params: { id: scan.id } });
    } finally {
      setCreatingScan(false);
    }
  }

  if (inProjectDetailRoute) return <Outlet />;

  return (
    <AppLayout>
      <PageHeader
        title="Проекты"
        description="Приложения и API в рамках разрешенного AppSec-анализа."
        actions={
          <Button variant="primary" onClick={() => void createProject()}>
            <Plus className="h-4 w-4" />
            Создать проект
          </Button>
        }
      />
      {loading && <Card>Загрузка проектов...</Card>}
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
                <div className="text-xs text-muted-foreground">Цели</div>
                <div className="font-semibold">{p.targets_count}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Подтверждено</div>
                <div className="font-semibold text-critical">{p.confirmed_findings}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">CI статус</div>
                <div className="font-semibold">{p.ci_gate}</div>
              </div>
            </div>
            <Button
              className="mt-4 w-full"
              variant="primary"
              onClick={() =>
                void navigate({
                  to: "/projects/$projectId",
                  params: { projectId: p.id },
                })
              }
            >
              <ExternalLink className="h-4 w-4" />
              Открыть проект
            </Button>
            <Button
              className="mt-2 w-full"
              variant="outline"
              onClick={() => setSelectedProjectId(p.id)}
            >
              <PlayCircle className="h-4 w-4" />
              Запустить скан
            </Button>
          </Card>
        ))}
      </div>
      <ScanTemplateDialog
        open={selectedProjectId !== null}
        title="Шаблоны сканирования"
        onClose={() => setSelectedProjectId(null)}
        onSelect={(template) => void startScanFromTemplate(template)}
      />
    </AppLayout>
  );
}

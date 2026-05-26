import { createFileRoute } from "@tanstack/react-router";
import { Cpu, ShieldCheck, Wrench } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader, SectionTitle } from "@/components/ui-kit";
import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/settings")({ component: Settings });

type ToolRegistryItem = {
  name: string;
  category: string;
  adapter: string;
  mode: string;
  destructive: boolean;
  enabled_by_default: boolean;
  description: string;
};

function Settings() {
  const { data } = useAsyncData(
    async () => ({
      model: await api.get<any>("/api/settings/model"),
      policies: await api.get<any>("/api/settings/policies"),
      tools: await api.get<any>("/api/settings/tools"),
    }),
    [],
  );
  const registry = (data?.tools?.tool_registry ?? []) as ToolRegistryItem[];
  return (
    <AppLayout>
      <PageHeader
        title="Settings"
        description="Model runtime, policy defaults, skill-driven tool registry."
      />
      {data && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card>
              <SectionTitle title="Model" />
              <Cpu className="mb-3 h-5 w-5 text-primary" />
              <div className="space-y-2 text-sm">
                <Row k="Provider" v={data.model.llm_provider} />
                <Row k="Base URL" v={data.model.llm_base_url} />
                <Row k="Model" v={data.model.llm_model} />
                <Row k="Health" v={data.model.health?.ok ? "healthy" : "unavailable"} />
              </div>
            </Card>
            <Card>
              <SectionTitle title="Policies" />
              <ShieldCheck className="mb-3 h-5 w-5 text-success" />
              <div className="space-y-2 text-sm">
                <Row k="Require scope" v={String(data.policies.require_scope_file)} />
                <Row k="Public targets" v={String(data.policies.allow_public_targets)} />
                <Row k="Default profile" v={data.policies.default_profile} />
              </div>
            </Card>
            <Card>
              <SectionTitle title="Enabled tools" />
              <Wrench className="mb-3 h-5 w-5 text-info" />
              <div className="flex flex-wrap gap-2">
                {data.tools.enabled.map((t: string) => (
                  <span key={t} className="rounded bg-muted px-2 py-1 text-xs">
                    {t}
                  </span>
                ))}
              </div>
            </Card>
          </div>
          <Card>
            <SectionTitle title="Tool registry" />
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
              {registry.map((tool) => (
                <div key={tool.adapter} className="rounded-md border border-border p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-medium">{tool.name}</div>
                      <div className="text-xs text-muted-foreground">{tool.adapter}</div>
                    </div>
                    <span className="rounded bg-muted px-2 py-1 text-xs">{tool.mode}</span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">{tool.description}</p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    <span className="rounded bg-muted px-2 py-1">{tool.category}</span>
                    <span className="rounded bg-muted px-2 py-1">
                      {tool.enabled_by_default ? "default" : "optional"}
                    </span>
                    <span className="rounded bg-muted px-2 py-1">
                      {tool.destructive ? "destructive" : "safe"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </AppLayout>
  );
}
function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-muted-foreground">{k}</span>
      <span className="text-right font-medium">{v}</span>
    </div>
  );
}

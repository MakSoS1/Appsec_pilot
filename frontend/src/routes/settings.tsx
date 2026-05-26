import { createFileRoute } from "@tanstack/react-router";
import { Cpu, ShieldCheck, Wrench } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader, SectionTitle } from "@/components/ui-kit";
import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-api";

export const Route = createFileRoute("/settings")({ component: Settings });

function Settings() {
  const { data } = useAsyncData(
    async () => ({
      model: await api.get<any>("/api/settings/model"),
      policies: await api.get<any>("/api/settings/policies"),
      tools: await api.get<any>("/api/settings/tools"),
    }),
    [],
  );
  return (
    <AppLayout>
      <PageHeader
        title="Settings"
        description="Model runtime, policy defaults, and tool adapters."
      />
      {data && (
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
            <SectionTitle title="Tools" />
            <Wrench className="mb-3 h-5 w-5 text-info" />
            <div className="flex flex-wrap gap-2">
              {data.tools.tools.map((t: string) => (
                <span key={t} className="rounded bg-muted px-2 py-1 text-xs">
                  {t}
                </span>
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

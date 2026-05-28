import { createFileRoute } from "@tanstack/react-router";
import { Github, Slack, Mail, Cloud, Shield, Database, CheckCircle2 } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, PageHeader, Button } from "@/components/ui-kit";

export const Route = createFileRoute("/integrations")({
  head: () => ({
    meta: [
      { title: "Интеграции — AppSec Pilot" },
      {
        name: "description",
        content: "Подключение AppSec Pilot к source control, CI/CD и каналам уведомлений.",
      },
    ],
  }),
  component: Integrations,
});

const items = [
  {
    name: "GitHub",
    desc: "Сканирование кода, комментарии в PR, черновики исправлений.",
    icon: Github,
    connected: true,
  },
  {
    name: "Slack",
    desc: "Мгновенные алерты при подтверждении критичных уязвимостей.",
    icon: Slack,
    connected: true,
  },
  {
    name: "Jira",
    desc: "Автосоздание задач по находкам из очереди срочных исправлений.",
    icon: Database,
    connected: false,
  },
  {
    name: "AWS",
    desc: "Обнаружение активов EC2, Lambda и API Gateway.",
    icon: Cloud,
    connected: true,
  },
  {
    name: "Okta",
    desc: "SSO и сопоставление ролей для пользователей AppSec Pilot.",
    icon: Shield,
    connected: false,
  },
  {
    name: "Email-дайджесты",
    desc: "Ежедневная сводка по сканам на email.",
    icon: Mail,
    connected: false,
  },
];

function Integrations() {
  return (
    <AppLayout>
      <PageHeader
        title="Интеграции"
        description="Подключите AppSec Pilot к вашему инженерному процессу."
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map((i) => (
          <Card key={i.name}>
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <i.icon className="h-5 w-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold">{i.name}</h3>
                  {i.connected && (
                    <span className="inline-flex items-center gap-1 rounded bg-success/10 px-1.5 py-0.5 text-[10px] font-medium text-success">
                      <CheckCircle2 className="h-3 w-3" /> Подключено
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{i.desc}</p>
              </div>
            </div>
            <div className="mt-4">
              <Button
                variant={i.connected ? "outline" : "primary"}
                size="sm"
                className="w-full justify-center"
              >
                {i.connected ? "Управлять" : "Подключить"}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}

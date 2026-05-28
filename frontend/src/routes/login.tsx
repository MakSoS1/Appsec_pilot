import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Button, Card } from "@/components/ui-kit";
import { login } from "@/lib/api";

export const Route = createFileRoute("/login")({ component: Login });

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@appsec.local");
  const [password, setPassword] = useState("AppSecPilot123!");
  const [error, setError] = useState<string | null>(null);
  async function doLogin() {
    setError(null);
    try {
      await login(email, password);
      await navigate({ to: "/" });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await doLogin();
  }
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">AppSec Pilot</h1>
            <p className="text-sm text-muted-foreground">
              Локальная авторизованная AppSec-валидация
            </p>
          </div>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            />
          </label>
          <label className="block text-sm font-medium">
            Пароль
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            />
          </label>
          {error && <p className="text-sm text-critical">{error}</p>}
          <Button type="submit" variant="primary" className="w-full">
            Войти
          </Button>
          <Button type="button" variant="outline" className="w-full" onClick={() => void doLogin()}>
            Демо-режим
          </Button>
        </form>
        <div className="mt-4 text-xs text-muted-foreground">
          Версия 0.1.0 · локальный запуск модели · обязательный scope
        </div>
      </Card>
    </div>
  );
}

import { Link, useLocation } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Database,
  Bug,
  PlayCircle,
  FileText,
  Settings,
  Search,
  Bell,
  ShieldCheck,
  ChevronDown,
  FolderKanban,
  ScrollText,
  LogIn,
} from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/assets", label: "Assets", icon: Database },
  { to: "/findings", label: "Findings", icon: Bug },
  { to: "/runs", label: "Runs", icon: PlayCircle },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/audit-logs", label: "Audit", icon: ScrollText },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar md:flex">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold text-sidebar-foreground">AppSec Pilot</div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
              AI AppSec Platform
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-0.5 px-3">
          {nav.map(({ to, label, icon: Icon }) => {
            const active =
              to === "/" ? pathname === "/" : pathname === to || pathname.startsWith(to + "/");
            return (
              <Link
                key={to}
                to={to}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  active && "bg-sidebar-accent text-sidebar-accent-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-sidebar-border px-3 py-3">
          <Link
            to="/login"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground/80 hover:bg-sidebar-accent"
          >
            <LogIn className="h-4 w-4" />
            Login
          </Link>
          <div className="mt-3 px-3">
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Workspace
            </div>
            <button className="mt-1 flex w-full items-center justify-between rounded-md border border-sidebar-border bg-surface px-3 py-2 text-sm">
              <span className="flex items-center gap-2">
                <span className="flex h-5 w-5 items-center justify-center rounded bg-accent text-[10px] font-bold text-accent-foreground">
                  A
                </span>
                Local Lab
              </span>
              <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
            </button>
          </div>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-14 items-center gap-3 border-b border-border bg-surface/80 px-6 backdrop-blur">
          <div className="relative max-w-md flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              placeholder="Search findings, endpoints, runs"
              className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-14 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20"
            />
            <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
              /
            </kbd>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <button className="relative rounded-md p-2 hover:bg-muted">
              <Bell className="h-4 w-4" />
              <span className="absolute right-1.5 top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-critical px-1 text-[10px] font-semibold text-critical-foreground">
                3
              </span>
            </button>
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                AP
              </div>
              <div className="hidden text-right leading-tight md:block">
                <div className="text-sm font-medium">AppSec Admin</div>
                <div className="text-[11px] text-muted-foreground">Security Team</div>
              </div>
            </div>
          </div>
        </header>
        <main className="min-w-0 flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}

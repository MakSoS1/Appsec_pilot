import { cn } from "@/lib/utils";
import type { Severity, PoCStatus, FindingStatus } from "@/lib/mock-data";

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-5 shadow-[0_1px_2px_0_rgb(0_0_0_/_0.02)]",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function SectionTitle({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-3">
      <div>
        <h2 className="text-base font-semibold tracking-tight">{title}</h2>
        {subtitle && <p className="mt-0.5 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

const severityClasses: Record<Severity, string> = {
  critical: "bg-critical/10 text-critical border-critical/20",
  high: "bg-high/15 text-high-foreground/90 border-high/30",
  medium: "bg-medium/20 text-medium-foreground/90 border-medium/30",
  low: "bg-low/15 text-low border-low/30",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium capitalize",
        severityClasses[severity],
      )}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          severity === "critical" && "bg-critical",
          severity === "high" && "bg-high",
          severity === "medium" && "bg-medium",
          severity === "low" && "bg-low",
        )}
      />
      {severity}
    </span>
  );
}

export function PoCBadge({ poc }: { poc: PoCStatus }) {
  const map: Record<PoCStatus, { label: string; cls: string }> = {
    confirmed: { label: "PoC confirmed", cls: "bg-success/10 text-success border-success/20" },
    likely: {
      label: "Likely exploitable",
      cls: "bg-medium/15 text-medium-foreground/90 border-medium/30",
    },
    "scanner-only": { label: "Scanner only", cls: "bg-muted text-muted-foreground border-border" },
    duplicate: { label: "Duplicate", cls: "bg-muted text-muted-foreground border-border" },
  };
  const { label, cls } = map[poc];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        cls,
      )}
    >
      {label}
    </span>
  );
}

export function StatusBadge({ status }: { status: FindingStatus }) {
  const map: Record<FindingStatus, string> = {
    "fix-now": "bg-critical/10 text-critical",
    "needs-review": "bg-info/10 text-info",
    "waiting-dev": "bg-medium/15 text-medium-foreground/90",
    accepted: "bg-muted text-muted-foreground",
    resolved: "bg-success/10 text-success",
  };
  const label: Record<FindingStatus, string> = {
    "fix-now": "Fix now",
    "needs-review": "Needs review",
    "waiting-dev": "Waiting for dev",
    accepted: "Accepted",
    resolved: "Resolved",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-medium",
        map[status],
      )}
    >
      {label[status]}
    </span>
  );
}

export function Button({
  variant = "default",
  size = "md",
  className,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline" | "ghost" | "primary";
  size?: "sm" | "md";
}) {
  const variants = {
    default: "bg-surface border border-border hover:bg-muted text-foreground",
    outline: "border border-border bg-transparent hover:bg-muted text-foreground",
    ghost: "hover:bg-muted text-foreground",
    primary: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
  };
  const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-9 px-3.5 text-sm",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring/30 disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

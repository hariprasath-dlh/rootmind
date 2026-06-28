import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Panel({
  children,
  className,
  label,
  code,
  action,
}: {
  children: ReactNode;
  className?: string;
  label?: string;
  code?: string;
  action?: ReactNode;
}) {
  return (
    <section
      className={cn(
        "glass glass-shine relative overflow-hidden",
        className,
      )}
    >
      {(label || action) && (
        <header className="flex items-center justify-between border-b border-glass-border px-4 py-2.5">
          <div className="flex items-center gap-2">
            {code && (
              <span className="font-mono text-[9px] uppercase tracking-[0.28em] text-text-faint">
                {code}
              </span>
            )}
            {label && (
              <h2 className="font-mono text-[11px] uppercase tracking-[0.22em] text-text-primary">
                {label}
              </h2>
            )}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function SeverityBadge({ level }: { level: "critical" | "high" | "medium" | "low" }) {
  const map = {
    critical: {
      cls: "border-severity-critical/60 text-severity-critical bg-severity-critical/8",
      bg: "bg-severity-critical",
    },
    high: {
      cls: "border-severity-high/60 text-severity-high bg-severity-high/8",
      bg: "bg-severity-high",
    },
    medium: {
      cls: "border-severity-medium/60 text-severity-medium bg-severity-medium/8",
      bg: "bg-severity-medium",
    },
    low: {
      cls: "border-severity-low/60 text-severity-low bg-severity-low/8",
      bg: "bg-severity-low",
    },
  } as const;
  const m = map[level];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.22em]",
        m.cls,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", m.bg)} />
      {level}
    </span>
  );
}

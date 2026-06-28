import { useState, type ReactNode } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  GitBranch,
  History,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  Zap,
} from "lucide-react";
import { motion } from "framer-motion";
import { ThemeToggle } from "./ThemeToggle";

interface NavItem {
  to: string;
  label: string;
  icon: typeof Activity;
  code: string;
}

const NAV: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, code: "01" },
  { to: "/analysis", label: "Incident Analysis", icon: Zap, code: "02" },
  { to: "/history", label: "Incident History", icon: History, code: "03" },
  { to: "/workflow", label: "Agent Workflow", icon: GitBranch, code: "04" },
  { to: "/settings", label: "Settings", icon: Settings, code: "05" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  const current = NAV.find(
    (n) => (n.to === "/" ? pathname === "/" : pathname.startsWith(n.to)),
  );

  return (
    <div className="relative z-10 flex min-h-screen w-full text-text-primary">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 64 : 240 }}
        transition={{ duration: 0.25, ease: [0.2, 0.8, 0.2, 1] }}
        className="sticky top-0 z-30 flex h-screen shrink-0 flex-col border-r border-glass-border bg-glass backdrop-blur-2xl"
      >
        {/* Brand */}
        <div className="flex h-14 items-center gap-2.5 border-b border-glass-border px-4">
          <div className="relative grid h-7 w-7 place-items-center rounded-md border border-accent-primary/50 bg-accent-primary/10 shadow-[0_0_16px_var(--accent-bio-glow)]">
            <div className="h-2 w-2 rounded-full bg-accent-primary animate-pulse-dot" />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-tight">
              <span className="font-display text-[17px] tracking-tight text-text-primary">
                RootMind
              </span>
              <span className="font-mono text-[9px] uppercase tracking-[0.3em] text-text-faint">
                AIOps · v0.4.2
              </span>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex flex-1 flex-col gap-1 p-2">
          {NAV.map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`group relative flex h-10 items-center gap-3 border border-transparent px-2.5 font-mono text-[11px] uppercase tracking-[0.14em] transition-colors ${
                  active
                    ? "border-border-subtle bg-bg-surface-hover text-text-primary"
                    : "text-text-muted hover:bg-bg-surface-hover hover:text-text-primary"
                }`}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-y-0 left-0 w-[2px] bg-accent-primary"
                    transition={{ duration: 0.2 }}
                  />
                )}
                <Icon className="h-4 w-4 shrink-0" strokeWidth={1.5} />
                {!collapsed && (
                  <>
                    <span className="flex-1 truncate">{item.label}</span>
                    <span className="text-[9px] text-text-faint">{item.code}</span>
                  </>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Status footer */}
        <div className="border-t border-border-subtle p-3">
          <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-status-ok animate-pulse-dot" />
            {!collapsed && <span>Gateway online</span>}
          </div>
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="mt-3 flex h-7 w-full items-center justify-center border border-border-subtle text-text-muted transition-colors hover:bg-bg-surface-hover hover:text-text-primary"
            aria-label="Toggle sidebar"
          >
            {collapsed ? (
              <PanelLeftOpen className="h-3.5 w-3.5" />
            ) : (
              <PanelLeftClose className="h-3.5 w-3.5" />
            )}
          </button>
        </div>
      </motion.aside>

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-glass-border bg-glass px-6 backdrop-blur-2xl">
          <div className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.2em] text-text-muted">
            <span className="text-text-faint">RM</span>
            <span className="text-text-faint">/</span>
            <span className="text-text-primary">{current?.label ?? "—"}</span>
            {current && (
              <span className="ml-2 rounded-sm border border-glass-border px-1.5 py-0.5 text-[9px] text-text-faint">
                {current.code}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-md border border-glass-border bg-glass px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted md:flex">
              <Activity className="h-3 w-3 text-accent-secondary" />
              <span>p99 · 142ms</span>
            </div>
            <ThemeToggle />
            <div className="flex items-center gap-2 rounded-md border border-glass-border bg-glass px-2 py-1">
              <div className="grid h-6 w-6 place-items-center rounded-sm bg-accent-primary font-mono text-[10px] font-bold text-[color:#04110a] shadow-[0_0_12px_var(--accent-bio-glow)]">
                SR
              </div>
              <div className="hidden flex-col leading-tight md:flex">
                <span className="font-mono text-[10px] uppercase tracking-[0.18em]">
                  s.ranjan
                </span>
                <span className="font-mono text-[8px] uppercase tracking-[0.22em] text-text-faint">
                  SRE · Tier 1
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="relative flex-1">{children}</main>
      </div>
    </div>
  );
}

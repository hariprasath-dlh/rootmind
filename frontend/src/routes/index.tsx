import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUpRight, RefreshCw } from "lucide-react";
import { api, type Incident } from "@/services/api";
import { Panel, SeverityBadge } from "@/components/ui-rm/Card";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Command · RootMind" },
      { name: "description", content: "Live AIOps command center: system status, MTTR, and the real-time incident feed." },
    ],
  }),
  component: Dashboard,
});

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s.toString().padStart(2, "0")}s`;
}

function formatRelative(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60_000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function Dashboard() {
  const queryClient = useQueryClient();
  const stats = useQuery({ queryKey: ["stats"], queryFn: api.getStats });
  const incidents = useQuery({ queryKey: ["incidents"], queryFn: api.listIncidents });

  // Smart manual refresh: poll silently in background, show dot when new data
  const [pendingCount, setPendingCount] = useState(0);
  const seenIds = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!incidents.data) return;
    if (seenIds.current.size === 0) {
      incidents.data.forEach((i) => seenIds.current.add(i.id));
    }
  }, [incidents.data]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const fresh = await api.listIncidents();
      const newOnes = fresh.filter((i) => !seenIds.current.has(i.id));
      if (newOnes.length > 0) setPendingCount((c) => c + newOnes.length);
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["incidents"] });
    await queryClient.invalidateQueries({ queryKey: ["stats"] });
    const fresh = await api.listIncidents();
    fresh.forEach((i) => seenIds.current.add(i.id));
    setPendingCount(0);
  };

  const status = stats.data?.systemStatus ?? "healthy";

  return (
    <div className="relative">
      <div className="absolute inset-0 grid-bg pointer-events-none" />
      <div className="relative mx-auto max-w-[1600px] space-y-6 p-6">
        {/* Hero status */}
        <HeroStatus
          status={status}
          pendingCount={pendingCount}
          onRefresh={handleRefresh}
          refreshing={incidents.isFetching || stats.isFetching}
        />

        {/* Metrics grid */}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
          <MetricCell
            code="M01"
            label="Total Incidents"
            value={stats.data?.totalIncidents}
            unit="24h"
            trend="+12%"
          />
          <MetricCell
            code="M02"
            label="Avg MTTR"
            value={stats.data ? formatDuration(stats.data.avgMttrSeconds) : undefined}
            unit="rolling"
            trend="-08%"
            trendGood
          />
          <MetricCell
            code="M03"
            label="Critical Alerts"
            value={stats.data?.criticalAlerts}
            unit="active"
            highlight
          />
          <MetricCell
            code="M04"
            label="Active Services"
            value={stats.data?.activeServices}
            unit="monitored"
          />
        </div>

        {/* Feed + sidepanel */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
          <IncidentFeed incidents={incidents.data} loading={incidents.isLoading} />
          <AgentRail />
        </div>
      </div>
    </div>
  );
}

function HeroStatus({
  status,
  pendingCount,
  onRefresh,
  refreshing,
}: {
  status: "healthy" | "degraded" | "critical";
  pendingCount: number;
  onRefresh: () => void;
  refreshing: boolean;
}) {
  const map = {
    healthy: { label: "All systems nominal", dot: "bg-status-ok", ring: "bg-status-ok/20" },
    degraded: {
      label: "Degraded performance detected",
      dot: "bg-severity-medium",
      ring: "bg-severity-medium/20",
    },
    critical: {
      label: "Critical incident in progress",
      dot: "bg-severity-critical",
      ring: "bg-severity-critical/20",
    },
  } as const;
  const s = map[status];
  return (
    <div className="glass glass-shine relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-px overflow-hidden">
        <div className="absolute inset-y-0 w-1/3 scan-line animate-scan" />
      </div>
      <div className="flex flex-col gap-6 p-6 md:flex-row md:items-end md:justify-between">
        <div className="flex items-center gap-5">
          <div className="relative grid h-16 w-16 place-items-center">
            <div className={`absolute inset-0 rounded-full ${s.ring} animate-pulse-dot`} />
            <div className={`relative h-3 w-3 rounded-full ${s.dot}`} />
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
              System status · live
            </p>
            <h1 className="mt-1 font-display text-4xl tracking-tight text-text-primary md:text-5xl">
              {s.label}
            </h1>
            <p className="mt-1 text-sm text-text-muted">
              Last sync <LastSyncTime /> · region us-east-1
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/analysis"
            className="inline-flex items-center gap-2 rounded-md border border-accent-primary/60 bg-accent-primary px-4 py-2.5 font-mono text-[11px] uppercase tracking-[0.22em] text-[color:#04110a] shadow-[0_0_24px_var(--accent-bio-glow)] transition-all hover:shadow-[0_0_36px_var(--accent-bio-glow)]"
          >
            Trigger pipeline <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={2.5} />
          </Link>
          <button
            onClick={onRefresh}
            className="relative inline-flex h-[42px] w-[42px] items-center justify-center rounded-md border border-glass-border bg-glass text-text-primary backdrop-blur-xl transition-colors hover:bg-glass-strong"
            aria-label="Refresh"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            <AnimatePresence>
              {pendingCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="absolute -right-1 -top-1 grid h-4 min-w-4 place-items-center rounded-full bg-accent-primary px-1 font-mono text-[9px] font-bold text-[color:#04110a]"
                  title={`${pendingCount} new incidents`}
                >
                  {pendingCount}
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </div>
    </div>
  );
}

function LastSyncTime() {
  const [time, setTime] = useState<string>("");
  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
      );
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="font-mono tabular">{time || "—"}</span>;
}

function MetricCell({
  code,
  label,
  value,
  unit,
  trend,
  trendGood,
  highlight,
}: {
  code: string;
  label: string;
  value: number | string | undefined;
  unit?: string;
  trend?: string;
  trendGood?: boolean;
  highlight?: boolean;
}) {
  return (
    <div className="glass glass-shine relative overflow-hidden p-5">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[9px] uppercase tracking-[0.28em] text-text-faint">
          {code} · {label}
        </span>
        {trend && (
          <span
            className={`font-mono text-[10px] uppercase tracking-[0.18em] ${
              trendGood ? "text-status-ok" : "text-text-muted"
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      <div className="mt-6 flex items-baseline gap-2">
        <span
          className={`font-display text-5xl tracking-tight tabular ${
            highlight ? "text-accent-primary [text-shadow:0_0_24px_var(--accent-bio-glow)]" : "text-text-primary"
          }`}
        >
          {value ?? "—"}
        </span>
        {unit && (
          <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}

function IncidentFeed({ incidents, loading }: { incidents?: Incident[]; loading: boolean }) {
  return (
    <Panel
      code="F01"
      label="Recent incidents · live feed"
      action={
        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
          {incidents?.length ?? "—"} entries
        </span>
      }
    >
      <ul className="divide-y divide-border-subtle">
        {loading && (
          <li className="p-6 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
            Loading feed…
          </li>
        )}
        <AnimatePresence initial={false}>
          {incidents?.map((inc, i) => (
            <motion.li
              key={inc.id}
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: Math.min(i * 0.02, 0.2) }}
              className="group"
            >
              <Link
                to="/incidents/$id"
                params={{ id: inc.id }}
                className="grid grid-cols-[110px_1fr_auto] items-start gap-4 px-4 py-4 transition-colors hover:bg-bg-surface-hover md:grid-cols-[110px_140px_1fr_auto]"
              >
                <div className="flex flex-col">
                  <span className="font-mono text-[11px] text-text-primary">{inc.id}</span>
                  <span className="font-mono text-[10px] text-text-faint">
                    {formatRelative(inc.createdAt)}
                  </span>
                </div>
                <div className="hidden md:block">
                  <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent-secondary">
                    {inc.service}
                  </span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <p className="line-clamp-2 text-sm text-text-primary group-hover:text-text-primary">
                    {inc.rootCause}
                  </p>
                  <div className="mt-2 flex items-center gap-2 md:hidden">
                    <span className="font-mono text-[10px] uppercase text-accent-secondary">
                      {inc.service}
                    </span>
                  </div>
                </div>
                <div className="col-start-3 row-start-1 flex items-center gap-2 md:col-start-4">
                  <SeverityBadge level={inc.severity} />
                  <ArrowUpRight className="hidden h-3.5 w-3.5 text-text-faint transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-accent-primary md:block" />
                </div>
              </Link>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </Panel>
  );
}

function AgentRail() {
  const agents = useMemo(
    () => [
      { name: "Anomaly Detector", load: 64, status: "active" },
      { name: "RCA Agent", load: 38, status: "active" },
      { name: "Fix Suggester", load: 12, status: "idle" },
      { name: "Post-Mortem", load: 0, status: "idle" },
      { name: "Slack Alert", load: 22, status: "active" },
    ],
    [],
  );
  return (
    <Panel code="A01" label="Agent fleet">
      <ul className="divide-y divide-border-subtle">
        {agents.map((a) => (
          <li key={a.name} className="px-4 py-3.5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-text-primary">
                {a.name}
              </span>
              <span
                className={`font-mono text-[9px] uppercase tracking-[0.22em] ${
                  a.status === "active" ? "text-accent-primary" : "text-text-faint"
                }`}
              >
                {a.status}
              </span>
            </div>
            <div className="mt-2 flex items-center gap-3">
              <div className="relative h-1 flex-1 bg-bg-surface-hover">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${a.load}%` }}
                  transition={{ duration: 0.8, ease: [0.2, 0.8, 0.2, 1] }}
                  className={a.status === "active" ? "absolute inset-y-0 left-0 bg-accent-primary" : "absolute inset-y-0 left-0 bg-border-strong"}
                />
              </div>
              <span className="font-mono text-[10px] tabular text-text-muted">
                {a.load.toString().padStart(2, "0")}%
              </span>
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  );
}

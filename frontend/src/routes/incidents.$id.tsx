import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import ReactMarkdown from "react-markdown";
import { api } from "@/services/api";
import { Panel, SeverityBadge } from "@/components/ui-rm/Card";

export const Route = createFileRoute("/incidents/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `${params.id} · RootMind` },
      { name: "description", content: `Deep-dive analysis for incident ${params.id}.` },
    ],
  }),
  component: IncidentDetail,
  notFoundComponent: () => (
    <div className="grid min-h-[60vh] place-items-center">
      <div className="text-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
          404 · Incident
        </p>
        <h1 className="mt-3 font-mono text-3xl text-text-primary">Not found</h1>
        <Link
          to="/"
          className="mt-6 inline-flex items-center gap-2 border border-border-subtle px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] hover:bg-bg-surface-hover"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> back
        </Link>
      </div>
    </div>
  ),
  errorComponent: () => (
    <div className="p-6 font-mono text-sm text-severity-critical">Failed to load incident.</div>
  ),
});

function IncidentDetail() {
  const { id } = Route.useParams();
  const { data: inc, isLoading } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => api.getIncident(id),
  });

  if (isLoading) {
    return (
      <div className="grid min-h-[60vh] place-items-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
          Loading incident…
        </p>
      </div>
    );
  }

  if (!inc) {
    return (
      <div className="grid min-h-[60vh] place-items-center">
        <div className="text-center">
          <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
            404 · Incident
          </p>
          <h1 className="mt-3 font-mono text-3xl text-text-primary">Not found</h1>
          <Link
            to="/"
            className="mt-6 inline-flex items-center gap-2 border border-border-subtle px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] hover:bg-bg-surface-hover"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> back
          </Link>
        </div>
      </div>
    );
  }

  const chartData = inc.timeseries.map((p) => ({
    t: new Date(p.t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    cpu: p.cpu,
    memory: p.memory,
    latency: p.latency,
  }));

  return (
    <div className="mx-auto max-w-[1600px] space-y-6 p-6">
      {/* Header */}
      <div className="border border-border-subtle bg-bg-surface p-6">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.22em] text-text-muted hover:text-text-primary"
        >
          <ArrowLeft className="h-3 w-3" /> Command
        </Link>
        <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="font-mono text-4xl font-semibold tracking-tight text-text-primary">
                {inc.id}
              </h1>
              <SeverityBadge level={inc.severity} />
            </div>
            <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.18em] text-accent-secondary">
              {inc.service}
            </p>
            <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
              opened {new Date(inc.createdAt).toLocaleString()} · status {inc.status}
            </p>
          </div>
          <div className="grid grid-cols-3 gap-px bg-border-subtle">
            <DetailStat label="CPU" value={`${inc.metrics.cpu}%`} />
            <DetailStat label="MEM" value={`${inc.metrics.memory}%`} />
            <DetailStat label="p99" value={`${inc.metrics.latencyMs}ms`} />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Panel code="C01" label="CPU / Memory · 15m">
          <div className="h-[260px] p-3">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="cpuFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="memFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-secondary)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="var(--accent-secondary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
                <XAxis
                  dataKey="t"
                  stroke="var(--text-faint)"
                  tick={{ fontSize: 9, fontFamily: "var(--font-mono)" }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke="var(--text-faint)"
                  tick={{ fontSize: 9, fontFamily: "var(--font-mono)" }}
                  width={32}
                />
                <Tooltip content={<RmTooltip />} />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stroke="var(--accent-primary)"
                  strokeWidth={1.5}
                  fill="url(#cpuFill)"
                />
                <Area
                  type="monotone"
                  dataKey="memory"
                  stroke="var(--accent-secondary)"
                  strokeWidth={1.5}
                  fill="url(#memFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel code="C02" label="Latency p99 · 15m">
          <div className="h-[260px] p-3">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
                <XAxis
                  dataKey="t"
                  stroke="var(--text-faint)"
                  tick={{ fontSize: 9, fontFamily: "var(--font-mono)" }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke="var(--text-faint)"
                  tick={{ fontSize: 9, fontFamily: "var(--font-mono)" }}
                  width={32}
                />
                <Tooltip content={<RmTooltip />} />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke="var(--accent-primary)"
                  strokeWidth={1.75}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      {/* Root cause + Risk */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_280px]">
        <Panel code="R01" label="Root cause">
          <div className="p-5">
            <p className="text-base leading-relaxed text-text-primary">{inc.rootCause}</p>
          </div>
        </Panel>
        <Panel code="R02" label="Patch risk">
          <div className="flex flex-col items-start gap-3 p-5">
            <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
              Risk level
            </span>
            <span
              className={`inline-flex items-center gap-2 border px-3 py-1.5 font-mono text-[12px] uppercase tracking-[0.24em] ${
                inc.riskLevel === "high"
                  ? "border-severity-critical text-severity-critical"
                  : inc.riskLevel === "medium"
                    ? "border-severity-medium text-severity-medium"
                    : "border-status-ok text-status-ok"
              }`}
            >
              <span
                className={`h-2 w-2 ${
                  inc.riskLevel === "high"
                    ? "bg-severity-critical"
                    : inc.riskLevel === "medium"
                      ? "bg-severity-medium"
                      : "bg-status-ok"
                }`}
              />
              {inc.riskLevel}
            </span>
            <p className="text-sm text-text-muted">
              Patch is non-breaking and gated behind a feature flag. Recommended rollout: 5% canary,
              monitor for 15 minutes.
            </p>
          </div>
        </Panel>
      </div>

      {/* Technical Details + Testing Suggestions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Panel code="T01" label="Technical details">
          <div className="p-5 space-y-4">
            <div>
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint block mb-1">
                Responsible File
              </span>
              <code className="font-mono text-sm text-accent-secondary bg-bg-void px-2 py-1 border border-border-subtle block w-fit">
                {inc.responsibleFile || "unknown"}
              </code>
            </div>
            <div>
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint block mb-1">
                Suspected Commit
              </span>
              <code className="font-mono text-sm text-text-primary bg-bg-void px-2 py-1 border border-border-subtle block w-fit">
                {inc.suspectedCommit || "unknown"}
              </code>
            </div>
            {inc.technicalExplanation && (
              <div>
                <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint block mb-1">
                  Explanation
                </span>
                <p className="text-sm text-text-muted leading-relaxed">
                  {inc.technicalExplanation}
                </p>
              </div>
            )}
          </div>
        </Panel>

        <Panel code="T02" label="Testing suggestions">
          <div className="p-5">
            {inc.testingSuggestions && inc.testingSuggestions.length > 0 ? (
              <ul className="space-y-3">
                {inc.testingSuggestions.map((sug, i) => (
                  <li key={i} className="flex gap-2 text-sm text-text-primary">
                    <span className="text-accent-primary font-mono select-none">{i + 1}.</span>
                    <span>{sug}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-text-faint italic">No testing suggestions generated.</p>
            )}
          </div>
        </Panel>
      </div>

      {/* Code patch */}
      <Panel code="P01" label="Proposed patch · diff">
        <pre className="overflow-x-auto bg-bg-void p-5 font-mono text-[12px] leading-relaxed">
          <CodeDiff source={inc.patch} />
        </pre>
      </Panel>

      {/* Post-mortem */}
      <Panel code="M01" label="Post-mortem · markdown">
        <article className="prose-rm max-w-none p-6">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="mb-4 mt-2 font-mono text-3xl font-semibold tracking-tight text-text-primary">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="mb-3 mt-8 font-mono text-[11px] uppercase tracking-[0.28em] text-accent-secondary">
                  {children}
                </h2>
              ),
              p: ({ children }) => (
                <p className="mb-4 text-[15px] leading-[1.75] text-text-primary">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="mb-4 space-y-2 border-l border-border-subtle pl-4">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-4 space-y-2 border-l border-border-subtle pl-4 [counter-reset:item]">
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="text-[15px] leading-relaxed text-text-primary">{children}</li>
              ),
              strong: ({ children }) => (
                <strong className="font-mono text-[13px] text-accent-primary">{children}</strong>
              ),
            }}
          >
            {inc.postMortem}
          </ReactMarkdown>
        </article>
      </Panel>
    </div>
  );
}

function DetailStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg-surface px-4 py-2.5">
      <div className="font-mono text-[9px] uppercase tracking-[0.28em] text-text-faint">{label}</div>
      <div className="font-mono text-lg tabular text-text-primary">{value}</div>
    </div>
  );
}

function RmTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="border border-border-subtle bg-bg-void px-3 py-2 font-mono text-[10px]">
      <div className="uppercase tracking-[0.2em] text-text-faint">{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-text-primary">
          <span className="h-1.5 w-1.5" style={{ background: p.color }} />
          {p.dataKey}: <span className="tabular">{p.value}</span>
        </div>
      ))}
    </div>
  );
}

function CodeDiff({ source }: { source: string }) {
  const lines = source.split("\n");
  return (
    <code className="block">
      {lines.map((line, i) => {
        let cls = "text-text-muted";
        if (line.startsWith("+++") || line.startsWith("---")) cls = "text-text-faint";
        else if (line.startsWith("@@")) cls = "text-accent-secondary";
        else if (line.startsWith("+")) cls = "text-status-ok bg-status-ok/5";
        else if (line.startsWith("-")) cls = "text-severity-critical bg-severity-critical/5";
        else cls = "text-text-primary";
        return (
          <div key={i} className={`${cls} px-2 -mx-2`}>
            {line || "\u00A0"}
          </div>
        );
      })}
    </code>
  );
}

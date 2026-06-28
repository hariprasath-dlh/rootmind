import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUpRight, Play, CheckCircle2, Loader2 } from "lucide-react";
import { api, type Incident } from "@/services/api";
import { Panel } from "@/components/ui-rm/Card";

export const Route = createFileRoute("/analysis")({
  head: () => ({
    meta: [
      { title: "Incident Analysis · RootMind" },
      { name: "description", content: "Trigger the autonomous multi-agent pipeline and watch root-cause analysis unfold in real time." },
    ],
  }),
  component: AnalysisPage,
});

interface Form {
  service: string;
  cpu: number;
  memory: number;
  latency: number;
  errorRate: number;
  repoUrl: string;
}

const NODES = [
  { key: "anomaly", label: "Anomaly Detector", code: "01" },
  { key: "rca", label: "RCA Agent", code: "02" },
  { key: "fix", label: "Fix Suggester", code: "03" },
  { key: "postmortem", label: "Post-Mortem", code: "04" },
  { key: "alert", label: "Slack Alert", code: "05" },
] as const;

type NodeKey = (typeof NODES)[number]["key"];
type NodeState = "pending" | "running" | "done";

function AnalysisPage() {
  const [form, setForm] = useState<Form>({
    service: "payments-api",
    cpu: 87,
    memory: 73,
    latency: 612,
    errorRate: 4.8,
    repoUrl: "",
  });
  const [nodeStates, setNodeStates] = useState<Record<NodeKey, NodeState>>({
    anomaly: "pending",
    rca: "pending",
    fix: "pending",
    postmortem: "pending",
    alert: "pending",
  });
  const [activeEdges, setActiveEdges] = useState<Set<number>>(new Set());
  const [result, setResult] = useState<Incident | null>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: api.runPipeline,
    onMutate: async () => {
      setResult(null);
      setActiveEdges(new Set());
      setNodeStates({
        anomaly: "pending",
        rca: "pending",
        fix: "pending",
        postmortem: "pending",
        alert: "pending",
      });
      // Sequence nodes
      for (let i = 0; i < NODES.length; i++) {
        const key = NODES[i].key;
        await wait(450);
        setNodeStates((s) => ({ ...s, [key]: "running" }));
        if (i > 0) {
          setActiveEdges((s) => new Set(s).add(i - 1));
        }
        await wait(900);
        setNodeStates((s) => ({ ...s, [key]: "done" }));
        if (i > 0) {
          setActiveEdges((s) => {
            const next = new Set(s);
            next.delete(i - 1);
            return next;
          });
        }
      }
    },
    onSuccess: (data) => {
      setResult(data);
      // Invalidate caches so Dashboard/History pick up the new incident
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
  });

  return (
    <div className="relative">
      <div className="absolute inset-0 grid-bg pointer-events-none" />
      <div className="relative mx-auto grid max-w-[1600px] grid-cols-1 gap-6 p-6 xl:grid-cols-[420px_1fr]">
        {/* Input form */}
        <Panel code="I01" label="Telemetry input">
          <form
            className="space-y-5 p-5"
            onSubmit={(e) => {
              e.preventDefault();
              mutation.mutate(form);
            }}
          >
            <Field label="Service">
              <select
                value={form.service}
                onChange={(e) => setForm({ ...form, service: e.target.value })}
                className="w-full appearance-none border border-border-subtle bg-bg-void px-3 py-2.5 font-mono text-sm text-text-primary outline-none transition-colors focus:border-accent-primary"
              >
                {[
                  "payments-api",
                  "auth-gateway",
                  "checkout-orchestrator",
                  "ledger-writer",
                  "search-indexer",
                ].map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <NumberField
                label="CPU %"
                value={form.cpu}
                onChange={(v) => setForm({ ...form, cpu: v })}
              />
              <NumberField
                label="Memory %"
                value={form.memory}
                onChange={(v) => setForm({ ...form, memory: v })}
              />
              <NumberField
                label="Latency ms"
                value={form.latency}
                onChange={(v) => setForm({ ...form, latency: v })}
              />
              <NumberField
                label="Error rate %"
                value={form.errorRate}
                step="0.1"
                onChange={(v) => setForm({ ...form, errorRate: v })}
              />
            </div>

            <Field label="GitHub Repo URL (Optional)">
              <input
                type="text"
                value={form.repoUrl}
                placeholder="https://github.com/owner/repo"
                onChange={(e) => setForm({ ...form, repoUrl: e.target.value })}
                className="w-full border border-border-subtle bg-bg-void px-3 py-2.5 font-mono text-sm text-text-primary outline-none transition-colors focus:border-accent-primary"
              />
            </Field>

            <button
              type="submit"
              disabled={mutation.isPending}
              className="group relative flex h-12 w-full items-center justify-center gap-2 overflow-hidden border border-accent-primary bg-accent-primary font-mono text-[12px] font-semibold uppercase tracking-[0.24em] text-[color:#0a0a0c] transition-opacity hover:opacity-90 active:scale-[0.98] disabled:opacity-60"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Pipeline running
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5" fill="currentColor" />
                  Trigger autonomous pipeline
                </>
              )}
            </button>

            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-faint">
              POST {`/api/v1/agents/run`}
            </p>
          </form>
        </Panel>

        {/* Pipeline visualization */}
        <Panel
          code="P01"
          label="Live pipeline · 5 agents"
          action={
            mutation.isPending ? (
              <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.22em] text-accent-primary">
                <span className="h-1.5 w-1.5 bg-accent-primary animate-pulse-dot" />
                executing
              </span>
            ) : (
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
                {result ? "complete" : "idle"}
              </span>
            )
          }
        >
          <div className="p-6">
            <div className="relative flex flex-col gap-4 lg:flex-row lg:items-stretch lg:gap-0">
              {NODES.map((n, i) => (
                <div key={n.key} className="flex flex-1 flex-col lg:flex-row lg:items-stretch">
                  <PipelineNode
                    label={n.label}
                    code={n.code}
                    state={nodeStates[n.key]}
                  />
                  {i < NODES.length - 1 && (
                    <PipelineEdge active={activeEdges.has(i)} done={nodeStates[NODES[i + 1].key] === "done"} />
                  )}
                </div>
              ))}
            </div>

            {/* Result expansion */}
            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.4 }}
                  className="mt-8 space-y-4"
                >
                  <ResultBlock code="R01" label="Root cause · RCA agent">
                    <p className="text-sm leading-relaxed text-text-primary">
                      {result.rootCause}
                    </p>
                  </ResultBlock>
                  <ResultBlock code="R02" label="Proposed fix · Fix suggester">
                    <pre className="overflow-x-auto bg-bg-void p-4 font-mono text-[12px] leading-relaxed text-text-primary">
                      <code>{result.patch}</code>
                    </pre>
                  </ResultBlock>
                  <ResultBlock code="R03" label="Notification · Slack #incidents">
                    <div className="flex items-start gap-3 bg-bg-void p-4">
                      <div className="grid h-7 w-7 shrink-0 place-items-center bg-accent-primary font-mono text-[10px] font-bold text-[color:#0a0a0c]">
                        RM
                      </div>
                      <div className="text-sm text-text-primary">
                        <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-accent-secondary">
                          rootmind-bot
                        </span>
                        <p className="mt-1">
                          🚨 <strong>{result.id}</strong> · {result.service} ·{" "}
                          {result.severity.toUpperCase()} · patch staged for review →{" "}
                          <Link
                            to="/incidents/$id"
                            params={{ id: result.id }}
                            className="text-accent-primary underline decoration-accent-primary/40 underline-offset-2"
                          >
                            view incident
                          </Link>
                        </p>
                      </div>
                    </div>
                  </ResultBlock>
                  <div className="flex justify-end">
                    <Link
                      to="/incidents/$id"
                      params={{ id: result.id }}
                      className="inline-flex items-center gap-2 border border-accent-primary bg-accent-primary px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] text-[color:#0a0a0c]"
                    >
                      Open incident detail
                      <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={2.5} />
                    </Link>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
        {label}
      </span>
      {children}
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
  step,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: string;
}) {
  return (
    <Field label={label}>
      <input
        type="number"
        value={value}
        step={step}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="w-full border border-border-subtle bg-bg-void px-3 py-2.5 font-mono text-sm tabular text-text-primary outline-none transition-colors focus:border-accent-primary"
      />
    </Field>
  );
}

function PipelineNode({
  label,
  code,
  state,
}: {
  label: string;
  code: string;
  state: NodeState;
}) {
  const isRunning = state === "running";
  const isDone = state === "done";
  return (
    <div className="flex flex-1 flex-col">
      <motion.div
        animate={{
          borderColor: isRunning
            ? "var(--accent-primary)"
            : isDone
              ? "var(--accent-primary)"
              : "var(--border-subtle)",
          backgroundColor: isRunning || isDone ? "var(--bg-surface-hover)" : "var(--bg-surface)",
          boxShadow: isRunning
            ? "0 0 0 1px var(--accent-primary), 0 0 32px -6px var(--accent-primary)"
            : "0 0 0 0 transparent",
        }}
        transition={{ duration: 0.3 }}
        className="relative flex h-28 flex-col justify-between border p-3"
      >
        <div className="flex items-center justify-between">
          <span className="font-mono text-[9px] uppercase tracking-[0.26em] text-text-faint">
            AGT · {code}
          </span>
          <span className="flex items-center justify-center">
            {isDone && <CheckCircle2 className="h-3.5 w-3.5 text-accent-primary" />}
            {isRunning && <Loader2 className="h-3.5 w-3.5 animate-spin text-accent-primary" />}
            {state === "pending" && (
              <span className="h-1.5 w-1.5 bg-text-faint" />
            )}
          </span>
        </div>
        <div>
          <p className="font-mono text-[12px] uppercase tracking-[0.14em] text-text-primary">
            {label}
          </p>
          <p
            className={`mt-1 font-mono text-[9px] uppercase tracking-[0.24em] ${
              isRunning
                ? "text-accent-primary"
                : isDone
                  ? "text-status-ok"
                  : "text-text-faint"
            }`}
          >
            {state}
          </p>
        </div>
      </motion.div>
    </div>
  );
}

function PipelineEdge({ active, done }: { active: boolean; done: boolean }) {
  return (
    <div className="relative my-2 grid h-10 w-full place-items-center lg:my-0 lg:h-auto lg:w-10">
      <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-border-subtle lg:inset-y-0 lg:left-1/2 lg:top-0 lg:h-full lg:w-px lg:-translate-x-1/2 lg:translate-y-0 lg:bg-border-subtle" />
      {done && (
        <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-accent-primary lg:inset-y-0 lg:left-1/2 lg:top-0 lg:h-full lg:w-px lg:-translate-x-1/2 lg:translate-y-0" />
      )}
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 overflow-hidden lg:inset-y-0 lg:left-1/2 lg:top-0 lg:h-full lg:w-px lg:-translate-x-1/2 lg:translate-y-0"
          >
            <div className="absolute inset-0 bg-accent-primary/30" />
            <div className="absolute inset-y-0 w-12 scan-line animate-flow lg:inset-x-0 lg:h-12 lg:w-full" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ResultBlock({
  code,
  label,
  children,
}: {
  code: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-border-subtle bg-bg-surface">
      <div className="flex items-center gap-2 border-b border-border-subtle px-4 py-2.5">
        <span className="font-mono text-[9px] uppercase tracking-[0.28em] text-text-faint">
          {code}
        </span>
        <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-text-primary">
          {label}
        </span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

function wait(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

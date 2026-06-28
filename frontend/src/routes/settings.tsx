import { createFileRoute } from "@tanstack/react-router";
import { Panel } from "@/components/ui-rm/Card";
import { useTheme } from "@/lib/theme-store";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings · RootMind" },
      { name: "description", content: "Configure RootMind agents, integrations, and appearance." },
    ],
  }),
  component: SettingsPage,
});

function SettingsPage() {
  const { theme, setTheme } = useTheme();
  return (
    <div className="mx-auto max-w-[1200px] space-y-6 p-6">
      <h1 className="font-mono text-3xl font-semibold tracking-tight">Settings</h1>
      <Panel code="S01" label="Appearance">
        <div className="p-5">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
            Theme
          </p>
          <div className="mt-3 inline-flex border border-border-subtle">
            {(["dark", "light"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                className={`px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] transition-colors ${
                  theme === t
                    ? "bg-accent-primary text-[color:#0a0a0c]"
                    : "text-text-muted hover:bg-bg-surface-hover"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </Panel>
      <Panel code="S02" label="Integrations">
        <ul className="divide-y divide-border-subtle">
          {[
            { name: "Slack", status: "connected", channel: "#incidents" },
            { name: "PagerDuty", status: "connected", channel: "sre-primary" },
            { name: "GitHub", status: "connected", channel: "rootmind/payments" },
            { name: "Datadog", status: "pending", channel: "—" },
          ].map((i) => (
            <li key={i.name} className="flex items-center justify-between px-5 py-3.5">
              <div>
                <span className="font-mono text-[12px] uppercase tracking-[0.18em] text-text-primary">
                  {i.name}
                </span>
                <span className="ml-3 font-mono text-[10px] text-text-faint">{i.channel}</span>
              </div>
              <span
                className={`font-mono text-[10px] uppercase tracking-[0.22em] ${
                  i.status === "connected" ? "text-status-ok" : "text-severity-medium"
                }`}
              >
                {i.status}
              </span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

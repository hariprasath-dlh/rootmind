import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { Panel, SeverityBadge } from "@/components/ui-rm/Card";
import { ArrowUpRight } from "lucide-react";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Incident History · RootMind" },
      { name: "description", content: "Full incident ledger across all monitored services." },
    ],
  }),
  component: HistoryPage,
});

import { useState } from "react";

function HistoryPage() {
  const { data: incidents = [], isLoading, error, isError } = useQuery({
    queryKey: ["incidents"],
    queryFn: api.listIncidents,
  });

  const [search, setSearch] = useState("");
  const [serviceFilter, setServiceFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");

  const services = ["all", ...new Set(incidents.map((i) => i.service))];

  const filteredIncidents = incidents.filter((inc) => {
    const matchesSearch =
      inc.id.toLowerCase().includes(search.toLowerCase()) ||
      inc.service.toLowerCase().includes(search.toLowerCase()) ||
      inc.rootCause.toLowerCase().includes(search.toLowerCase());

    const matchesService = serviceFilter === "all" || inc.service === serviceFilter;
    const matchesSeverity = severityFilter === "all" || inc.severity === severityFilter;

    return matchesSearch && matchesService && matchesSeverity;
  });

  return (
    <div className="mx-auto max-w-[1600px] space-y-6 p-6">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
          Archive · ledger
        </p>
        <h1 className="mt-2 font-mono text-3xl font-semibold tracking-tight text-text-primary">
          Incident history
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-text-muted">
          Every alert detected, diagnosed, and remediated by the RootMind agent fleet.
        </p>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border border-border-subtle bg-bg-surface p-4 font-mono text-xs">
        <div>
          <span className="block text-[10px] uppercase tracking-[0.22em] text-text-faint mb-1.5">
            Search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID, service, or root cause..."
            className="w-full border border-border-subtle bg-bg-void px-3 py-2 text-text-primary outline-none focus:border-accent-primary"
          />
        </div>
        <div>
          <span className="block text-[10px] uppercase tracking-[0.22em] text-text-faint mb-1.5">
            Service
          </span>
          <select
            value={serviceFilter}
            onChange={(e) => setServiceFilter(e.target.value)}
            className="w-full appearance-none border border-border-subtle bg-bg-void px-3 py-2 text-text-primary outline-none focus:border-accent-primary"
          >
            {services.map((s) => (
              <option key={s} value={s}>
                {s.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
        <div>
          <span className="block text-[10px] uppercase tracking-[0.22em] text-text-faint mb-1.5">
            Severity
          </span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full appearance-none border border-border-subtle bg-bg-void px-3 py-2 text-text-primary outline-none focus:border-accent-primary"
          >
            {["all", "critical", "high", "medium", "low"].map((s) => (
              <option key={s} value={s}>
                {s.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <Panel code="L01" label={`All incidents · ${filteredIncidents.length}`}>
        <div className="grid grid-cols-[110px_160px_120px_1fr_100px] gap-4 border-b border-border-subtle px-4 py-2.5 font-mono text-[9px] uppercase tracking-[0.24em] text-text-faint">
          <span>ID</span>
          <span>Service</span>
          <span>Severity</span>
          <span>Root cause</span>
          <span className="text-right">MTTR</span>
        </div>
        <ul className="divide-y divide-border-subtle">
          {isLoading && (
            <li className="p-6 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
              Loading incidents…
            </li>
          )}
          {isError && (
            <li className="p-6 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-severity-critical">
              Error: {error instanceof Error ? error.message : "Failed to load incidents"}
            </li>
          )}
          {!isLoading && !isError && filteredIncidents.length === 0 && (
            <li className="p-6 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-text-faint">
              No incidents found
            </li>
          )}
          {filteredIncidents.map((inc) => (
            <li key={inc.id}>
              <Link
                to="/incidents/$id"
                params={{ id: inc.id }}
                className="grid grid-cols-[110px_160px_120px_1fr_100px] items-center gap-4 px-4 py-3.5 transition-colors hover:bg-bg-surface-hover"
              >
                <span className="font-mono text-[11px] text-text-primary">{inc.id}</span>
                <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent-secondary">
                  {inc.service}
                </span>
                <SeverityBadge level={inc.severity} />
                <span className="line-clamp-1 text-sm text-text-primary">{inc.rootCause}</span>
                <span className="flex items-center justify-end gap-2 font-mono text-[11px] tabular text-text-muted">
                  {Math.floor(inc.mttrSeconds / 60)}m{(inc.mttrSeconds % 60).toString().padStart(2, "0")}s
                  <ArrowUpRight className="h-3 w-3 text-text-faint" />
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}


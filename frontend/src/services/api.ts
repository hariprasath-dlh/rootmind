/**
 * RootMind API client.
 *
 * Pipeline calls hit the real FastAPI backend via the Vite dev proxy.
 * Stats/list endpoints still use lightweight client-side data (no backend
 * endpoint yet) but merge any real pipeline results stored in localStorage.
 */

const API_BASE = "/api/v1";
const STORAGE_KEY = "rootmind-incidents";

// ─── Types ────────────────────────────────────────────────────────────
export type Severity = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "open" | "investigating" | "mitigated" | "resolved";

export interface Incident {
  id: string;
  service: string;
  severity: Severity;
  status: IncidentStatus;
  rootCause: string;
  createdAt: string;
  mttrSeconds: number;
  metrics: {
    cpu: number;
    memory: number;
    latencyMs: number;
    errorRate: number;
  };
  timeseries: Array<{ t: string; cpu: number; memory: number; latency: number }>;
  patch: string;
  riskLevel: "low" | "medium" | "high";
  postMortem: string;
  technicalExplanation: string;
  responsibleFile: string;
  suspectedCommit: string;
  testingSuggestions: string[];
}

export interface DashboardStats {
  totalIncidents: number;
  avgMttrSeconds: number;
  criticalAlerts: number;
  activeServices: number;
  systemStatus: "healthy" | "degraded" | "critical";
}

// ─── Backend response types ────────────────────────────────────────────
interface BackendPipelineResponse {
  status: string;
  pipeline_status: string;
  anomaly_assessment: any | null;
  rca_report: any | null;
  fix_suggestion: any | null;
  postmortem_report: any | null;
  error: string | null;
}

// ─── localStorage helpers ──────────────────────────────────────────────
function loadCachedIncidents(): Incident[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveCachedIncidents(incidents: Incident[]): void {
  try {
    // Keep max 50 entries to avoid bloating localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(incidents.slice(0, 50)));
  } catch {
    // localStorage full or disabled — silent fail
  }
}

function cacheIncident(incident: Incident): void {
  const cached = loadCachedIncidents();
  cached.unshift(incident);
  saveCachedIncidents(cached);
}

// ─── Timeseries generator (no backend source for this) ─────────────────
function generateTimeseries(
  baseCpu: number,
  baseMem: number,
  baseLat: number,
  points = 30,
): Incident["timeseries"] {
  const out: Incident["timeseries"] = [];
  const now = Date.now();
  let cpu = Math.max(5, baseCpu - 20 + Math.random() * 10);
  let mem = Math.max(5, baseMem - 15 + Math.random() * 10);
  let lat = Math.max(20, baseLat - 100 + Math.random() * 40);
  for (let i = points - 1; i >= 0; i--) {
    cpu = Math.max(5, Math.min(99, cpu + (Math.random() - 0.4) * 8));
    mem = Math.max(5, Math.min(99, mem + (Math.random() - 0.4) * 6));
    lat = Math.max(20, lat + (Math.random() - 0.4) * 35);
    // Ramp up toward the anomaly in the final third
    if (i < points / 3) {
      cpu = Math.min(99, cpu + 10);
      lat += 40;
    }
    out.push({
      t: new Date(now - i * 30_000).toISOString(),
      cpu: Math.round(cpu),
      memory: Math.round(mem),
      latency: Math.round(lat),
    });
  }
  return out;
}

// ─── Backend → Frontend data transformer ───────────────────────────────
let incidentCounter = Date.now();

function mapSeverity(raw: string | undefined | null): Severity {
  if (!raw) return "medium";
  const s = raw.toLowerCase();
  if (s.includes("critical") || s.includes("p0")) return "critical";
  if (s.includes("high") || s.includes("p1")) return "high";
  if (s.includes("low") || s.includes("p3")) return "low";
  return "medium";
}

function mapRisk(raw: string | undefined | null): "low" | "medium" | "high" {
  if (!raw) return "medium";
  const s = raw.toLowerCase();
  if (s.includes("high")) return "high";
  if (s.includes("low")) return "low";
  return "medium";
}

/**
 * Derive severity from anomaly score and error rate when no explicit
 * severity field is provided by the backend.
 */
function deriveSeverity(data: BackendPipelineResponse): Severity {
  const anomalyScore = data.anomaly_assessment?.assessment?.anomaly_score ?? 0;
  const errorRate = data.anomaly_assessment?.assessment?.features?.error_rate ?? 0;

  if (errorRate > 20 || anomalyScore < -0.7) return "critical";
  if (errorRate > 10 || anomalyScore < -0.5) return "high";
  if (errorRate > 5 || anomalyScore < -0.3) return "medium";
  return "low";
}

function transformBackendResponse(
  data: BackendPipelineResponse,
  input: { service: string; cpu: number; memory: number; latency: number; errorRate: number },
  durationMs: number,
): Incident {
  const anomaly = data.anomaly_assessment ?? {} as any;
  const rca = data.rca_report ?? {} as any;
  const fix = data.fix_suggestion ?? {} as any;
  const postmortem = data.postmortem_report ?? {} as any;

  // ── 1. Root Cause Summary ─────────────────────────────────────────────
  // Backend nests under rca_report.root_cause.root_cause_summary
  const rootCauseRaw =
    rca.root_cause?.root_cause_summary ||
    rca.root_cause_analysis ||
    rca.root_cause ||
    rca.summary ||
    anomaly?.assessment?.description ||
    anomaly?.assessment?.anomaly_type ||
    "Root cause analysis unavailable — pipeline returned partial data.";

  // ── 2. Code Patch ─────────────────────────────────────────────────────
  // Backend nests under fix_suggestion.fix.patch_diff / fix_suggestion.fix.fixed_code
  const patchRaw =
    fix.fix?.patch_diff ||
    fix.fix?.fixed_code ||
    fix.code_patch ||
    fix.patch ||
    fix.suggested_fix ||
    fix.fix_code ||
    "# No code patch available\n# The fix agent did not return a code patch for this incident.";

  // ── 3. Post-Mortem Report ─────────────────────────────────────────────
  // Backend nests under postmortem_report.report
  const postMortemRaw =
    postmortem.report ||
    postmortem.markdown_report ||
    postmortem.postmortem ||
    postmortem.content ||
    "# Post-Mortem Unavailable\n\nThe post-mortem agent did not return a report for this incident.";

  // ── 4. Severity ───────────────────────────────────────────────────────
  // Try explicit severity field from RCA, otherwise derive from metrics
  const explicitSeverity = rca.severity || rca.priority || anomaly?.assessment?.severity;
  const severity = explicitSeverity ? mapSeverity(explicitSeverity) : deriveSeverity(data);

  // ── 5. Risk Level ─────────────────────────────────────────────────────
  // Backend nests under fix_suggestion.fix.risk_level
  const riskLevel = mapRisk(
    fix.fix?.risk_level ||
    fix.risk_level ||
    fix.risk,
  );

  // ── 6. Technical Explanation ──────────────────────────────────────────
  const technicalExplanation =
    rca.root_cause?.technical_explanation ||
    rca.technical_explanation ||
    "";

  // ── 7. Responsible File ───────────────────────────────────────────────
  const responsibleFile =
    rca.root_cause?.responsible_file ||
    fix.target_file ||
    "";

  // ── 8. Suspected Commit ───────────────────────────────────────────────
  const suspectedCommit =
    rca.root_cause?.suspected_commit ||
    rca.commit ||
    "";

  // ── 9. Testing Suggestions ────────────────────────────────────────────
  const testingSuggestions: string[] =
    fix.fix?.testing_suggestions ||
    fix.testing_suggestions ||
    [];

  // ── 10. Incident ID ───────────────────────────────────────────────────
  const incidentId =
    postmortem.incident_id ||
    `INC-${(++incidentCounter).toString().slice(-4)}`;

  // ── 11. Timestamp ─────────────────────────────────────────────────────
  const createdAt =
    anomaly.timestamp ||
    new Date().toISOString();

  // ── 12. Metrics from backend assessment features ──────────────────────
  const metrics = {
    cpu: anomaly.assessment?.features?.cpu_usage ?? input.cpu,
    memory: anomaly.assessment?.features?.memory_usage ?? input.memory,
    latencyMs: anomaly.assessment?.features?.request_latency_ms ?? input.latency,
    errorRate: anomaly.assessment?.features?.error_rate ?? input.errorRate,
  };

  return {
    id: incidentId,
    service: anomaly.service || input.service,
    severity,
    status: data.pipeline_status === "postmortem_complete" || data.pipeline_status === "slack_alert_sent"
      ? "resolved"
      : data.error
        ? "investigating"
        : "mitigated",
    rootCause: typeof rootCauseRaw === "string" ? rootCauseRaw : JSON.stringify(rootCauseRaw, null, 2),
    createdAt,
    mttrSeconds: Math.round(durationMs / 1000),
    metrics,
    timeseries: generateTimeseries(metrics.cpu, metrics.memory, metrics.latencyMs),
    patch: typeof patchRaw === "string" ? patchRaw : JSON.stringify(patchRaw, null, 2),
    riskLevel,
    postMortem: typeof postMortemRaw === "string" ? postMortemRaw : JSON.stringify(postMortemRaw, null, 2),
    technicalExplanation: typeof technicalExplanation === "string" ? technicalExplanation : JSON.stringify(technicalExplanation, null, 2),
    responsibleFile,
    suspectedCommit,
    testingSuggestions: Array.isArray(testingSuggestions) ? testingSuggestions : [],
  };
}

// ─── Mock data generators (for endpoints without a backend) ────────────
const SERVICES = [
  "payments-api",
  "auth-gateway",
  "checkout-orchestrator",
  "ledger-writer",
  "search-indexer",
  "media-transcoder",
  "notification-fanout",
  "rate-limiter",
];

function rand<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function makeMockIncident(id: string, severity: Severity, ageMin: number): Incident {
  const service = rand(SERVICES);
  return {
    id,
    service,
    severity,
    status: severity === "critical" ? "investigating" : "resolved",
    rootCause:
      severity === "critical"
        ? "Connection pool exhaustion in primary write path triggered cascading timeouts across dependent services."
        : severity === "high"
          ? "Memory leak in cache eviction loop pushed working set beyond container limit."
          : severity === "medium"
            ? "Upstream DNS resolver returned stale records for ~90s, causing intermittent 503s."
            : "Background job scheduler scheduled duplicate work after leader election flap.",
    createdAt: new Date(Date.now() - ageMin * 60_000).toISOString(),
    mttrSeconds: 180 + Math.floor(Math.random() * 600),
    metrics: {
      cpu: 60 + Math.floor(Math.random() * 35),
      memory: 55 + Math.floor(Math.random() * 40),
      latencyMs: 200 + Math.floor(Math.random() * 800),
      errorRate: +(Math.random() * 12).toFixed(2),
    },
    timeseries: generateTimeseries(70, 65, 400),
    patch: `--- a/services/${service}/handler.go\n+++ b/services/${service}/handler.go\n@@ -42,9 +42,14 @@\n   defer cancel()\n \n-  conn, err := h.pool.Acquire(ctx)\n+  conn, err := h.pool.AcquireWithTimeout(ctx, 250*time.Millisecond)\n   if err != nil {\n-    return nil, fmt.Errorf("acquire: %w", err)\n+    metrics.PoolStarvation.Inc()\n+    return nil, ErrPoolExhausted\n   }\n   defer conn.Release()`,
    riskLevel: severity === "critical" ? "high" : severity === "high" ? "medium" : "low",
    postMortem: `# Post-Mortem — ${id}\n\n## Summary\nAutonomous incident response triggered for **${service}**.\n\n## Timeline\n- Anomaly detected in telemetry.\n- RCA agent identified probable root cause.\n- Fix suggested and staged for review.\n\n## Action Items\n1. Review suggested patch.\n2. Deploy to canary environment.\n3. Monitor for regression.`,
    technicalExplanation: "Mock incident — no technical explanation available.",
    responsibleFile: `services/${service}/handler.go`,
    suspectedCommit: "abc1234",
    testingSuggestions: [
      "Run integration tests against the affected service.",
      "Verify connection pool metrics under load.",
    ],
  };
}

const SEED: Incident[] = [
  makeMockIncident("INC-2847", "critical", 4),
  makeMockIncident("INC-2846", "high", 22),
  makeMockIncident("INC-2845", "medium", 51),
  makeMockIncident("INC-2844", "low", 88),
  makeMockIncident("INC-2843", "high", 142),
  makeMockIncident("INC-2842", "medium", 210),
  makeMockIncident("INC-2841", "low", 388),
  makeMockIncident("INC-2840", "critical", 502),
  makeMockIncident("INC-2839", "low", 720),
  makeMockIncident("INC-2838", "medium", 944),
];

async function delay<T>(value: T, ms = 240): Promise<T> {
  return new Promise((r) => setTimeout(() => r(value), ms));
}

// ─── Public API ────────────────────────────────────────────────────────
export const api = {
  /**
   * Health check — calls the real backend.
   */
  async getHealth(): Promise<{ status: string; service: string }> {
    const res = await fetch(`${API_BASE}/../health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  },  /**
   * Dashboard stats — queries the backend, with local cache/mock fallback.
   */
  async getStats(): Promise<DashboardStats> {
    try {
      const res = await fetch(`${API_BASE}/incidents/stats`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Failed to fetch stats from backend, falling back:", e);
    }
    
    // Fallback: local calculations
    const cached = loadCachedIncidents();
    const all = [...cached, ...SEED];
    const crit = all.filter((i) => i.severity === "critical").length;
    return delay({
      totalIncidents: all.length,
      avgMttrSeconds: Math.round(
        all.reduce((s, i) => s + i.mttrSeconds, 0) / all.length,
      ),
      criticalAlerts: crit,
      activeServices: SERVICES.length,
      systemStatus: crit > 1 ? "critical" : crit > 0 ? "degraded" : "healthy",
    });
  },

  /**
   * List incidents — merges real backend incidents with mock seed data.
   */
  async listIncidents(): Promise<Incident[]> {
    let backendIncidents: Incident[] = [];
    try {
      const res = await fetch(`${API_BASE}/incidents`);
      if (!res.ok) throw new Error(`Failed to fetch incidents: ${res.status}`);
      
      const data = await res.json();
      console.log('Fetched incidents:', data);
      
      if (Array.isArray(data)) {
        backendIncidents = data;
      } else if (data && typeof data === 'object' && Array.isArray(data.incidents)) {
        backendIncidents = data.incidents;
      } else {
        console.warn("Unexpected backend incidents format:", data);
      }
    } catch (error) {
      console.error('Error fetching incidents:', error);
    }

    const cached = loadCachedIncidents();
    
    // Deduplicate: merge backendIncidents, cached (localStorage), and SEED
    const merged = [...backendIncidents, ...cached];
    const seenIds = new Set(merged.map((i) => i.id));
    const finalMerged = [...merged, ...SEED.filter((i) => !seenIds.has(i.id))];
    
    return delay(finalMerged);
  },

  /**
   * Get a single incident — checks backend, then localStorage, then mock seed.
   */
  async getIncident(id: string): Promise<Incident | undefined> {
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn(`Failed to fetch incident ${id} from backend, falling back:`, e);
    }

    const cached = loadCachedIncidents();
    const found = cached.find((i) => i.id === id) || SEED.find((i) => i.id === id);
    return delay(found);
  },

  /**
   * Trigger the autonomous pipeline — REAL backend call.
   */
  async runPipeline(input: {
    service: string;
    cpu: number;
    memory: number;
    latency: number;
    errorRate: number;
    repoUrl?: string;
  }): Promise<Incident> {
    const startTime = Date.now();

    const payload = {
      service: input.service,
      timestamp: new Date().toISOString(),
      cpu_usage: input.cpu,
      memory_usage: input.memory,
      request_latency_ms: input.latency,
      error_rate: input.errorRate,
      repo_url: input.repoUrl || null
    };

    const res = await fetch(`${API_BASE}/agents/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => "Unknown error");
      throw new Error(`Pipeline failed (${res.status}): ${errBody}`);
    }

    const data: BackendPipelineResponse = await res.json();
    const durationMs = Date.now() - startTime;

    const incident = transformBackendResponse(data, input, durationMs);
    cacheIncident(incident);

    return incident;
  },

  /**
   * Get incident history — queries backend if possible, falls back to localStorage.
   */
  async getIncidentHistory(): Promise<Incident[]> {
    try {
      const res = await fetch(`${API_BASE}/incidents`);
      if (!res.ok) throw new Error(`Failed to fetch incidents: ${res.status}`);
      
      const data = await res.json();
      console.log('Fetched incidents:', data);
      
      if (Array.isArray(data)) {
        return data;
      } else if (data && typeof data === 'object' && Array.isArray(data.incidents)) {
        return data.incidents;
      }
    } catch (error) {
      console.error('Error fetching incidents:', error);
    }
    return delay(loadCachedIncidents());
  },
};

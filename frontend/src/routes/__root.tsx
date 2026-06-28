import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";
import { AppShell } from "../components/layout/AppShell";
import { initThemeOnClient } from "../lib/theme-store";

function NotFoundComponent() {
  return (
    <div className="grid min-h-screen place-items-center bg-bg-void px-4">
      <div className="max-w-md text-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
          ERR · 404
        </p>
        <h1 className="mt-4 font-mono text-6xl font-semibold tracking-tight text-text-primary">
          NO ROUTE
        </h1>
        <p className="mt-3 text-sm text-text-muted">
          The signal you requested does not resolve to a known endpoint.
        </p>
        <a
          href="/"
          className="mt-6 inline-flex items-center border border-accent-primary bg-accent-primary px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] text-[color:#0a0a0c] transition-opacity hover:opacity-90"
        >
          Return to command
        </a>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);
  return (
    <div className="grid min-h-screen place-items-center bg-bg-void px-4">
      <div className="max-w-md text-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-severity-critical">
          SYSTEM FAULT
        </p>
        <h1 className="mt-4 font-mono text-3xl font-semibold tracking-tight text-text-primary">
          Page failed to mount
        </h1>
        <p className="mt-3 text-sm text-text-muted">
          An unhandled exception was raised during render.
        </p>
        <div className="mt-6 flex justify-center gap-2">
          <button
            onClick={() => {
              router.invalidate();
              reset();
            }}
            className="border border-accent-primary bg-accent-primary px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] text-[color:#0a0a0c]"
          >
            Retry
          </button>
          <a
            href="/"
            className="border border-border-subtle px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] text-text-primary hover:bg-bg-surface-hover"
          >
            Home
          </a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "RootMind — Autonomous AIOps Command" },
      {
        name: "description",
        content:
          "Tactical multi-agent AIOps console for elite SRE teams. Detect, diagnose, and remediate incidents autonomously.",
      },
      { name: "theme-color", content: "#050507" },
      { property: "og:title", content: "RootMind — Autonomous AIOps" },
      {
        property: "og:description",
        content: "Autonomous incident response, in real time.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=JSON.parse(localStorage.getItem('rootmind-theme')||'{}');var theme=(t&&t.state&&t.state.theme)||'dark';var r=document.documentElement;r.classList.remove('dark','light');r.classList.add(theme);r.style.colorScheme=theme;}catch(e){}})();`,
          }}
        />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  useEffect(() => {
    initThemeOnClient();
  }, []);
  return (
    <QueryClientProvider client={queryClient}>
      <div
        aria-hidden
        className="ambient-orb animate-drift"
        style={{
          width: 620,
          height: 620,
          top: -220,
          right: -180,
          background:
            "radial-gradient(circle, var(--accent-bio-glow) 0%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="ambient-orb animate-drift-slow"
        style={{
          width: 520,
          height: 520,
          bottom: -180,
          left: 80,
          background:
            "radial-gradient(circle, rgba(96,165,250,0.10) 0%, transparent 70%)",
        }}
      />
      <AppShell>
        <Outlet />
      </AppShell>
    </QueryClientProvider>
  );
}

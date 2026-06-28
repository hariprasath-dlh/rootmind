import { createFileRoute } from "@tanstack/react-router";
import { Panel } from "@/components/ui-rm/Card";

export const Route = createFileRoute("/workflow")({
  head: () => ({
    meta: [
      { title: "Agent Workflow · RootMind" },
      { name: "description", content: "Configure the autonomous agent topology and routing rules." },
    ],
  }),
  component: () => (
    <div className="mx-auto max-w-[1600px] space-y-6 p-6">
      <h1 className="font-mono text-3xl font-semibold tracking-tight">Agent workflow</h1>
      <Panel code="W01" label="Topology editor">
        <div className="grid min-h-[320px] place-items-center p-10 text-center">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-text-faint">
              Coming soon
            </p>
            <p className="mt-3 max-w-md text-sm text-text-muted">
              A drag-and-drop builder for routing rules between the 5 agents. Ships in the next
              milestone.
            </p>
          </div>
        </div>
      </Panel>
    </div>
  ),
});

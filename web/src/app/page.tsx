import Link from "next/link";
import { ConsoleShell } from "@/components/ConsoleShell";
import { Panel } from "@/components/Panel";
import { Button } from "@/components/Button";
import { StatusLamp } from "@/components/StatusLamp";

/**
 * Public landing — minimal stub for Stage 0-3.
 * Full Home composition is out of scope until after Sol Checkpoint A.
 *
 * This page exists so:
 *   - /system is not the only reachable URL
 *   - the routing tree is verified end-to-end
 *   - the chassis frame can be sanity-checked in isolation
 */
export default function HomePage() {
  return (
    <main style={{ padding: "24px 12px" }}>
      <ConsoleShell ariaLabel="OpenRadar chassis">
        <Panel
          title="OpenRadar Web V2 — Stage 0–3"
          headerRight={
            <span className="inline-flex items-center gap-2">
              <StatusLamp state="ok" label="Stage 0–3 online" />
            </span>
          }
        >
          <div className="ort-content-module">
            <p style={{ margin: "0 0 16px", color: "var(--text-secondary)" }}>
              The visual reference has been preserved and the design-token system
              is online. The full Home composition is intentionally deferred until
              after the first Sol review.
            </p>
            <p style={{ margin: "0 0 16px", color: "var(--text-secondary)" }}>
              The internal component laboratory is available at{" "}
              <Link
                href="/system"
                style={{ color: "var(--signal-primary)", textDecoration: "underline" }}
              >
                /system
              </Link>{" "}
              — it is marked <code>noindex</code> and excluded from public nav.
            </p>
            <div className="flex gap-2">
              <Link href="/system">
                <Button variant="primary">Open /system lab</Button>
              </Link>
              <Link href="/system#responsive">
                <Button variant="ghost">Responsive evidence</Button>
              </Link>
            </div>
          </div>
        </Panel>
      </ConsoleShell>
    </main>
  );
}
"use client";

import { useState } from "react";
import {
  Button,
  Panel,
  Radar,
  Segmented,
  StatusLamp,
} from "@/components";

/**
 * ResponsiveLab — narrow-width stress demo wrapped for the client tree.
 * Used by the Responsive section of /system.
 */
export function ResponsiveLab() {
  const [range, setRange] = useState<"24h" | "7d" | "30d">("7d");
  return (
    <Panel
      title="Narrow-Width Stress Case"
      headerRight={null}
    >
      <div className="ort-content-module flex flex-col gap-4">
        <p style={{ margin: 0, color: "var(--text-secondary)" }}>
          Below 480px the chassis reflows: header stacks, ThemeDial docks under
          the nav, the radar shrinks inside its instrument housing without
          losing its identity, button rows wrap. Touch targets stay ≥ 28px.
        </p>
        <div
          data-testid="responsive-mock"
          className="ort-panel-recessed p-3"
          style={{
            display: "grid",
            gap: "12px",
            gridTemplateColumns: "minmax(0, 1fr)",
          }}
        >
          <Radar size={180} />
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" size="sm">
              Primary
            </Button>
            <Button variant="default" size="sm">
              Default
            </Button>
            <Button variant="ghost" size="sm">
              Ghost
            </Button>
          </div>
          <Segmented
            ariaLabel="Time range"
            value={range}
            onChange={setRange}
            options={[
              { value: "24h", label: "24H" },
              { value: "7d", label: "7D" },
              { value: "30d", label: "30D" },
            ]}
          />
          <div className="flex flex-wrap gap-2">
            <StatusLamp state="ok" label="Nominal" />
            <StatusLamp state="warn" label="Caution" />
          </div>
        </div>
        <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "11px" }}>
          Screenshot evidence at 1440 / 768 / 393 / 320 px is captured
          separately and reported in the SOL REVIEW PACKET.
        </p>
      </div>
    </Panel>
  );
}
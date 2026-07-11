"use client";

import { useState } from "react";
import {
  AlertStrip,
  Button,
  Chip,
  Panel,
  Segmented,
  StatusLamp,
} from "@/components";
import { ACCENT_PRESETS, type AccentName } from "@/lib/accent";
import { useAccent } from "@/lib/accent-context";

/**
 * SystemExplorer — client-only section that exercises interactive states
 * the static sections cannot show (real toggles, focus demonstration,
 * row-style accent picker that mirrors the ThemeDial's mental model).
 */
export function SystemExplorer() {
  const { accent, setAccent } = useAccent();
  const [segmentValue, setSegmentValue] = useState<"a" | "b" | "c">("b");
  const [segment2Value, setSegment2Value] = useState<"dev" | "ops" | "res">(
    "ops",
  );

  return (
    <section
      id="explorer"
      aria-labelledby="explorer-title"
      className="px-1 pt-4"
    >
      <h2
        id="explorer-title"
        className="text-label"
        style={{ marginBottom: "12px" }}
      >
        § Interactive States
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Panel
          title="Hover / Focus / Active / Disabled"
          headerRight={<Chip>try keyboard</Chip>}
        >
          <div className="ort-content-module flex flex-col gap-4">
            <p style={{ margin: 0, color: "var(--text-secondary)" }}>
              Tab into this panel. The first button receives focus. Press{" "}
              <kbd>Tab</kbd> again to move to the next. Every interactive
              surface in this laboratory has a visible focus ring (cool blue,
              accent-stable). Press <kbd>Space</kbd> or <kbd>Enter</kbd> to
              activate.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button variant="primary">Action A</Button>
              <Button variant="default">Action B</Button>
              <Button variant="ghost">Action C</Button>
              <Button variant="default" disabled>
                Disabled
              </Button>
            </div>
            <AlertStrip icon="◉" variant="info">
              <strong style={{ color: "var(--text-primary)" }}>
                Visible focus is mandatory.
              </strong>{" "}
              Never rely on color alone for state.
            </AlertStrip>
          </div>
        </Panel>

        <Panel title="Segmented Control — Live" headerRight={<Chip>real state</Chip>}>
          <div className="ort-content-module flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <Segmented
                ariaLabel="View"
                value={segmentValue}
                onChange={setSegmentValue}
                options={[
                  { value: "a", label: "ALPHA" },
                  { value: "b", label: "BETA" },
                  { value: "c", label: "GAMMA" },
                ]}
              />
              <Segmented
                ariaLabel="Track"
                value={segment2Value}
                onChange={setSegment2Value}
                options={[
                  { value: "dev", label: "DEV" },
                  { value: "ops", label: "OPS" },
                  { value: "res", label: "RES" },
                ]}
              />
            </div>
            <div className="ort-panel-recessed p-3 text-data" style={{ fontSize: "12px" }}>
              <span style={{ color: "var(--text-muted)" }}>CURRENT</span>{" "}
              <span style={{ color: "var(--text-primary)" }}>{segmentValue}</span>{" / "}
              <span style={{ color: "var(--text-primary)" }}>{segment2Value}</span>
            </div>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "11px" }}>
              Arrow keys move within the group. Space/Enter activates.
            </p>
          </div>
        </Panel>

        <Panel title="Accent — Row Picker" headerRight={<Chip>mirror of ThemeDial</Chip>}>
          <div className="ort-content-module flex flex-col gap-3">
            <div className="flex flex-wrap gap-2">
              {ACCENT_PRESETS.map((p) => {
                const isActive = p.name === accent;
                return (
                  <button
                    key={p.name}
                    type="button"
                    onClick={() => setAccent(p.name as AccentName)}
                    aria-pressed={isActive}
                    style={{
                      padding: "6px 10px",
                      borderRadius: "var(--radius-control-sm)",
                      border: `1px solid ${
                        isActive ? "var(--signal-primary)" : "var(--edge-trim)"
                      }`,
                      background: isActive
                        ? "var(--signal-soft)"
                        : "transparent",
                      color: isActive
                        ? "var(--signal-primary)"
                        : "var(--text-secondary)",
                      fontFamily: "var(--font-mono)",
                      fontSize: "11px",
                      letterSpacing: "0.06em",
                      cursor: "pointer",
                    }}
                  >
                    {p.tag}
                  </button>
                );
              })}
            </div>
            <div className="ort-panel-recessed p-3 text-data" style={{ fontSize: "12px" }}>
              <span style={{ color: "var(--text-muted)" }}>ACTIVE</span>{" "}
              <span style={{ color: "var(--text-primary)" }}>{accent}</span>
            </div>
          </div>
        </Panel>

        <Panel title="Status Lamp States" headerRight={<Chip>pulse off = static</Chip>}>
          <div className="ort-content-module grid grid-cols-2 gap-3">
            <div className="ort-panel-recessed p-3 flex items-center gap-3">
              <StatusLamp state="ok" pulse />
              <span className="text-data" style={{ fontSize: "11px" }}>
                LIVE
              </span>
            </div>
            <div className="ort-panel-recessed p-3 flex items-center gap-3">
              <StatusLamp state="ok" />
              <span className="text-data" style={{ fontSize: "11px" }}>
                OK
              </span>
            </div>
            <div className="ort-panel-recessed p-3 flex items-center gap-3">
              <StatusLamp state="warn" />
              <span className="text-data" style={{ fontSize: "11px" }}>
                WARN
              </span>
            </div>
            <div className="ort-panel-recessed p-3 flex items-center gap-3">
              <StatusLamp state="err" />
              <span className="text-data" style={{ fontSize: "11px" }}>
                ERR
              </span>
            </div>
          </div>
        </Panel>
      </div>
    </section>
  );
}
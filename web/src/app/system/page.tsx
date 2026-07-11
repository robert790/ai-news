import type { Metadata } from "next";
import {
  AlertStrip,
  Button,
  Chip,
  ConsoleShell,
  ContentModule,
  DataBadge,
  ListItem,
  NavigationControl,
  Panel,
  ProgressIndicator,
  Radar,
  Readout,
  SignalRow,
  StatusLamp,
  ThemeDial,
} from "@/components";
import { SystemExplorer } from "./SystemExplorer";
import { ControlsLab } from "./ControlsLab";
import { ResponsiveLab } from "./ResponsiveLab";

export const metadata: Metadata = {
  title: "/system — OpenRadar Web V2 Component Laboratory",
  description:
    "Internal component laboratory for OpenRadar Web V2. Not for public index.",
  robots: { index: false, follow: false },
};

export default function SystemPage() {
  return (
    <main style={{ padding: "24px 12px" }}>
      <ConsoleShell ariaLabel="Component laboratory chassis">
        <div
          className="ort-panel-header flex-wrap gap-3"
          style={{
            borderRadius: "var(--radius-chassis) var(--radius-chassis) 0 0",
          }}
        >
          <div className="ort-panel-title">
            <StatusLamp state="ok" pulse />
            <span>/system — Component Laboratory</span>
            <Chip tone="signal">noindex</Chip>
          </div>
          <div className="flex items-center gap-2 text-data text-xs">
            <span style={{ color: "var(--text-muted)" }}>STAGE</span>
            <span style={{ color: "var(--text-primary)" }}>0–3</span>
          </div>
        </div>

        <NavigationControl
          currentId="system"
          items={[
            { id: "shells", label: "Shells" },
            { id: "panels", label: "Panels" },
            { id: "controls", label: "Controls" },
            { id: "readouts", label: "Readouts" },
            { id: "lists", label: "Lists & State" },
            { id: "responsive", label: "Responsive" },
            { id: "accent", label: "Accent Swap" },
          ]}
          accessory={<ThemeDial />}
          ariaLabel="Laboratory section navigation"
        />

        <SystemExplorer />

        <Shells />
        <Panels />
        <Controls />
        <Readouts />
        <Lists />
        <Responsive />
        <AccentProof />

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "11px",
            padding: "16px 8px 24px",
            margin: 0,
          }}
        >
          All components in this laboratory consume only semantic CSS variables.
          The chassis, glass, edges, typography, spacing, and motion are stable;
          only the accent signal/phosphor colors change when the ThemeDial rotates.
        </p>
      </ConsoleShell>
    </main>
  );
}

// ----- Static sections -----

function Shells() {
  return (
    <section
      id="shells"
      aria-labelledby="shells-title"
      className="px-1 py-4"
    >
      <h2 id="shells-title" className="text-label" style={{ marginBottom: "12px" }}>
        § Shells & Frame
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Panel title="ConsoleShell" headerRight={<Chip>stable</Chip>}>
          <div className="ort-content-module">
            <p style={{ margin: 0, color: "var(--text-secondary)" }}>
              The outer machine frame. Bronze perimeter hairline, gunmetal bezel,
              rounded chassis. Single presentational component. The Home page and
              every other surface lives inside one of these.
            </p>
          </div>
        </Panel>
        <Panel
          title="Structural Chassis Frame"
          headerRight={<Chip>stable</Chip>}
          fasteners
        >
          <div className="ort-content-module">
            <p style={{ margin: 0, color: "var(--text-secondary)" }}>
              A raised panel with the four-corner socket-head fastener pattern.
              The fasteners are decorative spans marked <code>aria-hidden</code>;
              AT and keyboard focus ignore them.
            </p>
          </div>
        </Panel>
      </div>
    </section>
  );
}

function Panels() {
  return (
    <section id="panels" aria-labelledby="panels-title" className="px-1 py-4">
      <h2 id="panels-title" className="text-label" style={{ marginBottom: "12px" }}>
        § Panels & Modules
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel
          title="Instrument Panel"
          headerRight={<Chip tone="signal">raised</Chip>}
          variant="raised"
        >
          <div className="p-4">
            <div className="ort-panel-recessed p-3">
              <Readout label="FREQUENCY" value="2.4" unit="GHz" />
            </div>
          </div>
        </Panel>
        <Panel
          title="Module / Card Panel"
          headerRight={<Chip>card</Chip>}
          variant="raised"
        >
          <ContentModule title="Static editorial content">
            <p style={{ margin: 0 }}>
              A typed body of prose sits inside an instrument-styled card. The
              wrapping chassis material is shared with the radar and the
              navigation — that is the system-level coherence.
            </p>
          </ContentModule>
        </Panel>
        <Panel
          title="Recessed Module"
          headerRight={<Chip tone="signal">recessed</Chip>}
          variant="recessed"
        >
          <div className="p-4">
            <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "13px" }}>
              Recessed variant for inset data displays — same chassis material,
              inverse depth treatment.
            </p>
          </div>
        </Panel>
      </div>
    </section>
  );
}

function Controls() {
  return (
    <section
      id="controls"
      aria-labelledby="controls-title"
      className="px-1 py-4"
    >
      <h2 id="controls-title" className="text-label" style={{ marginBottom: "12px" }}>
        § Controls
      </h2>
      <ControlsLab />
    </section>
  );
}

function Readouts() {
  return (
    <section
      id="readouts"
      aria-labelledby="readouts-title"
      className="px-1 py-4"
    >
      <h2 id="readouts-title" className="text-label" style={{ marginBottom: "12px" }}>
        § Readouts & Indicators
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel title="Radar Instrument" headerRight={<Chip tone="signal">SVG</Chip>}>
          <div className="p-4">
            <Radar />
          </div>
        </Panel>
        <Panel title="Readout / Status Lamp / Data Badge">
          <div className="ort-content-module flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-3">
              <Readout label="SIGNALS" value="128" />
              <Readout label="LATENCY" value="42" unit="ms" />
              <Readout label="UPTIME" value="99.98" unit="%" />
              <Readout label="CONTACTS" value="6" tone="neutral" />
            </div>
            <div className="flex flex-wrap gap-2">
              <StatusLamp state="ok" label="Nominal" pulse />
              <StatusLamp state="warn" label="Caution" />
              <StatusLamp state="err" label="Fault" />
              <StatusLamp state="idle" label="Standby" />
            </div>
            <div className="flex flex-wrap gap-2">
              <DataBadge label="SIGNALS" value="128" trend="up" />
              <DataBadge label="TOOLS" value="37" trend="flat" />
              <DataBadge label="ALERTS" value="02" trend="down" />
            </div>
          </div>
        </Panel>
        <Panel title="Progress / Chips / Alerts" headerRight={<Chip>live</Chip>}>
          <div className="ort-content-module flex flex-col gap-4">
            <ProgressIndicator total={10} value={7} ariaLabel="Console load" />
            <div className="flex flex-wrap gap-2">
              <Chip>neutral</Chip>
              <Chip tone="signal">active</Chip>
              <Chip>DEV</Chip>
              <Chip>RESEARCH</Chip>
              <Chip>BUILD</Chip>
            </div>
            <AlertStrip icon="●" variant="info">
              Sweep cycle nominal — 4s rotation, 7 active contacts.
            </AlertStrip>
            <AlertStrip icon="●" variant="warn">
              One source returned degraded metadata. Cached display only.
            </AlertStrip>
            <AlertStrip icon="●" variant="err">
              Cannot reach monitoring endpoint. Showing last-known state.
            </AlertStrip>
          </div>
        </Panel>
      </div>
    </section>
  );
}

function Lists() {
  return (
    <section id="lists" aria-labelledby="lists-title" className="px-1 py-4">
      <h2 id="lists-title" className="text-label" style={{ marginBottom: "12px" }}>
        § Lists, Modules & States
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Panel title="Signal Row" headerRight={<Chip>telemetry</Chip>}>
          <SignalRow label="SIGNALS" value="4 ACTIVE" state="ok" />
          <SignalRow label="TOOLS" value="128 AVAILABLE" state="ok" />
          <SignalRow label="JOBS" value="37 LIVE" state="warn" />
          <SignalRow label="STATUS" value="ALL SYSTEMS NOMINAL" state="ok" />
          <SignalRow label="LAST UPDATE" value="2 MIN AGO" state="idle" />
        </Panel>
        <Panel title="List Items" headerRight={<Chip>interactive</Chip>}>
          <ListItem
            title="Cursor"
            meta="Editor · 12.4 ★ · Updated 2d"
            selected
            trailing={<Chip tone="signal">SELECTED</Chip>}
          />
          <ListItem
            title="Perplexity Pro"
            meta="Search · 9.6 ★ · Updated 1d"
            trailing={<Chip>OPEN</Chip>}
          />
          <ListItem
            title="Replit Agent"
            meta="Build · 8.1 ★ · Updated 4d"
            trailing={<Chip>OPEN</Chip>}
          />
          <ListItem
            title="Data Interpreter"
            meta="Analytics · 7.8 ★ · Updated 6d"
            trailing={<Chip>WATCH</Chip>}
          />
        </Panel>
        <Panel title="States" headerRight={<Chip>full coverage</Chip>}>
          <div className="ort-content-module grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="ort-empty">Empty state — no signals yet.</div>
            <div className="ort-loading">Loading sweep…</div>
            <div className="ort-error" style={{ gridColumn: "1 / -1" }}>
              Error state — source unreachable.
            </div>
          </div>
        </Panel>
        <Panel title="Decorative vs. Actionable" headerRight={<Chip>honest</Chip>}>
          <div className="ort-content-module flex flex-col gap-3">
            <p style={{ margin: 0, color: "var(--text-secondary)" }}>
              Every element that looks interactive is either a real control or
              marked decorative. Fasteners, the radar bezel, and dial labels
              carry <code>data-interactive=&quot;false&quot;</code> and{" "}
              <code>aria-hidden</code>.
            </p>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm">
                Actionable button
              </Button>
              <span
                className="ort-chip"
                data-interactive="false"
                aria-hidden="true"
              >
                Decorative chip
              </span>
              <span
                aria-hidden="true"
                data-decorative="true"
                style={{ display: "inline-flex", gap: 6 }}
              >
                <span className="ort-fastener" />
                <span className="ort-fastener" />
              </span>
            </div>
          </div>
        </Panel>
      </div>
    </section>
  );
}

function Responsive() {
  return (
    <section
      id="responsive"
      aria-labelledby="responsive-title"
      className="px-1 py-4"
    >
      <h2
        id="responsive-title"
        className="text-label"
        style={{ marginBottom: "12px" }}
      >
        § Responsive Behavior
      </h2>
      <ResponsiveLab />
    </section>
  );
}

function AccentProof() {
  return (
    <section id="accent" aria-labelledby="accent-title" className="px-1 py-4">
      <h2
        id="accent-title"
        className="text-label"
        style={{ marginBottom: "12px" }}
      >
        § Accent Swap — Proof
      </h2>
      <Panel
        title="Rotate the ThemeDial"
        headerRight={<Chip tone="signal">signal & phosphor only</Chip>}
      >
        <div className="ort-content-module flex flex-col gap-4">
          <p style={{ margin: 0, color: "var(--text-secondary)" }}>
            When the ThemeDial rotates, only the accent variables change. The
            chassis material, glass tint, edges, typography, spacing, and
            motion are untouched. Compare this panel&apos;s surface with the
            panels above across all five presets.
          </p>
          <div className="flex flex-wrap gap-3 items-center">
            <ThemeDial />
            <DataBadge label="SIGNAL" value="SWAPPED" trend="up" />
            <StatusLamp state="ok" label="Chassis stable" />
          </div>
        </div>
      </Panel>
    </section>
  );
}
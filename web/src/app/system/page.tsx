import * as React from "react";
import {
  Machine,
  TopDeck,
  HeroDeck,
  Module,
  LowerBank,
  Footer,
  StatusRail,
} from "../components";

/**
 * OpenRadar /system — internal design laboratory.
 *
 * Reference page for the OpenRadar component + token system.
 * Demonstrates the five accent skins, typography hierarchy,
 * action states, system-state panels, and the composed chassis
 * regions. No new tokens, no new components, no redesign of the
 * Home surface.
 *
 * Static / internal-facing only.
 */

const SYSTEM_NAV = [
  { label: "Home", href: "/" },
  { label: "System", href: "/system", active: true },
  { label: "Tokens", href: "/system#tokens" },
  { label: "States", href: "/system#states" },
  { label: "Skin", href: "/system#skin" },
];

const SKINS = [
  { id: "green", label: "Green" },
  { id: "amber", label: "Amber" },
  { id: "cyan", label: "Cyan" },
  { id: "red", label: "Red" },
  { id: "violet", label: "Violet" },
] as const;

const TYP_RAMP = [
  { name: "Display", spec: "clamp(39px,3.65vw,58px) / 680 / -0.035em", use: "Hero headline" },
  { name: "Module title", spec: "11px mono / 0.09em / uppercase", use: "Module h2" },
  { name: "Rail label", spec: "9.5px mono / 0.11em / uppercase", use: "Status rail" },
  { name: "Body lede", spec: "15px / 1.52 / 0.01em", use: "Hero lede" },
  { name: "Tag chip", spec: "8px mono / uppercase", use: "Tool/kit/job tags" },
  { name: "Legal micro", spec: "8px mono / 0.07em / uppercase", use: "Footer legal bar" },
];

const SKIN_TOKEN_SAMPLE = [
  { token: "--accent", note: "primary" },
  { token: "--accent-strong", note: "primary gradient top" },
  { token: "--accent-deep-100", note: "radar origin" },
  { token: "--accent-deep-300", note: "pulse bar" },
  { token: "--accent-deep-500", note: "radar bearing text" },
  { token: "--accent-deep-800", note: "active nav glow" },
  { token: "--accent-glow-100", note: "primary CTA halo" },
];

const ACTION_STATES = [
  { key: "default", label: "Default" },
  { key: "hover", label: "Hover / Focus" },
  { key: "active", label: "Active" },
  { key: "disabled", label: "Disabled" },
];

const SYSTEM_STATES = [
  { key: "loading", label: "Loading", note: "Index rebuild in progress" },
  { key: "empty", label: "Empty", note: "Nothing in this signal yet" },
  { key: "success", label: "Success", note: "Index published — 14 tools" },
  { key: "warning", label: "Warning", note: "Two sources out of date" },
  { key: "error", label: "Error", note: "Failed to refresh feeds" },
];

function SkinPanel({ id, label }: { id: (typeof SKINS)[number]["id"]; label: string }) {
  return (
    <section className="sys-skin" data-skin={id} id={`skin-${id}`} aria-labelledby={`skin-${id}-h`}>
      <header className="sys-skin__head">
        <span className="sys-skin__code">{id}</span>
        <h3 id={`skin-${id}-h`}>{label}</h3>
      </header>
      <div className="sys-skin__grid">
        <Module title="Sample module" code="01" className="sys-skin__module">
          <div className="sys-skin__module-body">
            <span className="sys-skin__primary">Primary row</span>
            <span className="sys-skin__ghost">Ghost row</span>
            <span className="sys-skin__tag">Tag</span>
          </div>
          <div className="sys-skin__progress"><i style={{ width: "55%" }} /></div>
        </Module>
        <Module title="Status rail" code="02" className="sys-skin__rail">
          <StatusRail
            ariaLabel={`${label} accent demo`}
            items={[
              { icon: <i className="status-icon">ϟ</i>, label: "Signals", detail: "Token cascade" },
              { icon: <i className="status-icon">⌘</i>, label: "Hero", detail: "Re-skinned" },
              { icon: <i className="status-icon">▱</i>, label: "Radar", detail: "Stops recolored" },
              { icon: <i className="pulse" />, label: "Pulse", detail: "Glow tracks skin" },
              { icon: <i className="status-icon">◷</i>, label: "Hold", detail: "Stable" },
            ]}
          />
        </Module>
        <Module title="Action row" code="03" className="sys-skin__actions">
          <div className="sys-skin__action-row">
            <a className="primary-action" href="#"><b>Launch</b> →</a>
            <a href="#">Secondary</a>
            <a aria-disabled="true" className="sys-disabled">Disabled</a>
          </div>
        </Module>
      </div>
    </section>
  );
}

function StatePanel({ state }: { state: (typeof SYSTEM_STATES)[number] }) {
  return (
    <article className={`sys-state sys-state--${state.key}`}>
      <header className="sys-state__head">
        <span className={`sys-state__chip sys-state__chip--${state.key}`}>{state.label}</span>
        <h4>{state.label}</h4>
      </header>
      <p className="sys-state__body">{state.note}</p>
      <ul className="sys-state__meta">
        <li><span>Region</span><strong>Module body</strong></li>
        <li><span>Tone</span><strong>{state.label}</strong></li>
        <li><span>Recovery</span><strong>{state.key === "error" ? "Retry" : state.key === "warning" ? "Inspect" : state.key === "loading" ? "Wait" : state.key === "empty" ? "Seed" : "Ack"}</strong></li>
      </ul>
    </article>
  );
}

export default function System() {
  return (
    <main className="page-shell" data-page="system">
      <Machine ariaLabel="OpenRadar system laboratory">
        <TopDeck
          nav={SYSTEM_NAV}
        />

        <HeroDeck
          kicker="System laboratory"
          title={
            <>
              Design tokens, skins, and states.
              <br />
              One chassis. Five accents.
            </>
          }
          lede="Internal reference for the OpenRadar chassis. Browse the five accent skins, the action states, and the system-state vocabulary. Nothing here ships to users — it exists so future surfaces stay coherent with the freeze."
          actions={[
            { primary: true, href: "#skin", label: <>Jump to skins <b>→</b></> },
            { href: "#tokens", label: "Token ramp" },
            { href: "#states", label: "State panels" },
          ]}
          overview={{ href: "#legend", label: "Legend & conventions" }}
        />

        <StatusRail
          ariaLabel="System status"
          items={[
            { icon: <i className="status-icon">ϟ</i>, label: "Tokens", detail: "Stable" },
            { icon: <i className="status-icon">⌘</i>, label: "Components", detail: "12 modules" },
            { icon: <i className="status-icon">▱</i>, label: "Skins", detail: "Five accents" },
            { icon: <i className="pulse" />, label: "States", detail: "5 / 5 covered" },
            { icon: <i className="status-icon">◷</i>, label: "Static", detail: "Internal only" },
          ]}
        />

        {/* 2x2 specimen grid: row 1 = 40% / 60%, row 2 = 50% / 50%. */}
        <section className="sys-specimens" aria-label="Specimens">
          <div className="sys-specimens__row sys-specimens__row--top">
            <Module title="Component inventory" code="01" className="legend-module">
              <ul className="sys-legend">
                <li><span className="sys-legend__num">01</span><span className="sys-legend__content"><strong>Machine</strong><small>Bronze chassis, bolts, optional data-skin</small></span></li>
                <li><span className="sys-legend__num">02</span><span className="sys-legend__content"><strong>TopDeck</strong><small>Brand mark, nav, actions, online indicator</small></span></li>
                <li><span className="sys-legend__num">03</span><span className="sys-legend__content"><strong>HeroDeck</strong><small>Operational console hero panel</small></span></li>
                <li><span className="sys-legend__num">04</span><span className="sys-legend__content"><strong>Radar</strong><small>CRT scope plus four corner readouts</small></span></li>
                <li><span className="sys-legend__num">05</span><span className="sys-legend__content"><strong>StatusRail</strong><small>Five-up telemetry strip</small></span></li>
                <li><span className="sys-legend__num">06</span><span className="sys-legend__content"><strong>Module</strong><small>Header plus body card with index</small></span></li>
                <li><span className="sys-legend__num">07</span><span className="sys-legend__content"><strong>LowerBank</strong><small>Three-column secondary strip</small></span></li>
                <li><span className="sys-legend__num">08</span><span className="sys-legend__content"><strong>Footer</strong><small>Mark, dl, subscribe, legal bar</small></span></li>
              </ul>
            </Module>
            <Module title="Type hierarchy" code="02" className="typo-module">
              <ol className="sys-typo">
                {TYP_RAMP.map((t) => (
                  <li key={t.name} className={`sys-typo__item sys-typo__item--${t.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>
                    <span className="sys-typo__name">{t.name}</span>
                    <span className="sys-typo__spec">{t.spec}</span>
                    <span className="sys-typo__use">{t.use}</span>
                    <span className={`sys-typo__sample sys-typo__sample--${t.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>Find what works.</span>
                  </li>
                ))}
              </ol>
            </Module>
          </div>
          <div className="sys-specimens__row sys-specimens__row--bottom">
            <Module title="Token ramp" code="03" className="tokens-module">
              <div id="tokens" />
              <ul className="sys-tokens">
                {SKIN_TOKEN_SAMPLE.map((t) => (
                  <li key={t.token}>
                    <code>{t.token}</code>
                    <span className="sys-tokens__chip" data-token={t.token} />
                    <small>{t.note}</small>
                  </li>
                ))}
              </ul>
            </Module>
            <Module title="Action states" code="04" className="actions-module">
              <ul className="sys-actions">
                {ACTION_STATES.map((a) => (
                  <li key={a.key} className={`sys-actions__row sys-actions__row--${a.key}`}>
                    <span className="sys-actions__label">{a.label}</span>
                    <a
                      className={a.key === "default" ? "primary-action" : a.key === "active" ? "primary-action sys-active" : a.key === "hover" ? "primary-action sys-hover" : "primary-action sys-disabled"}
                      aria-disabled={a.key === "disabled" ? true : undefined}
                      href="#"
                    >
                      <b>Run</b> →
                    </a>
                    <a
                      className={a.key === "default" ? "" : a.key === "active" ? "sys-active" : a.key === "hover" ? "sys-hover" : "sys-disabled"}
                      aria-disabled={a.key === "disabled" ? true : undefined}
                      href="#"
                    >Secondary</a>
                  </li>
                ))}
              </ul>
            </Module>
          </div>
        </section>

        <LowerBank
          panels={[
            {
              className: "signal-panel",
              label: "Token cascade",
              headline: "Five skins",
              body: (
                <ul className="standards-list">
                  <li><i />Cascade via data-skin attribute</li>
                  <li><i />SVG stops use inline var()</li>
                  <li><i />No rebuild needed per skin</li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Compatibility",
              headline: "Same DOM",
              body: (
                <ul>
                  <li><b>01</b><span>Component shapes frozen</span><time>Static</time></li>
                  <li><b>02</b><span>Token names stable across skins</span><time>v1</time></li>
                  <li><b>03</b><span>Bronze / cream / steel unchanged</span><time>Lock</time></li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Coverage",
              headline: "All surfaces",
              body: (
                <ul>
                  <li>Top deck <i /></li>
                  <li>Hero deck <i /></li>
                  <li>Status rail <i /></li>
                  <li>Modules & tags <i /></li>
                </ul>
              ),
            },
          ]}
        />

        <section id="skin" className="sys-skin-section" aria-label="Five accent skins">
          <header className="sys-section__head">
            <h2>Five accent skins</h2>
            <p>Each panel scopes a <code>data-skin</code> to its section so the cascade re-targets accents without rebuilding the chassis.</p>
          </header>
          <div className="sys-skin-row">
            {SKINS.map((s) => <SkinPanel key={s.id} id={s.id} label={s.label} />)}
          </div>
        </section>

        <section id="states" className="sys-states" aria-label="System states">
          <header className="sys-section__head">
            <h2>System states</h2>
            <p>The vocabulary the chassis uses to surface runtime status without leaving its material language.</p>
          </header>
          <div className="sys-states__grid">
            {SYSTEM_STATES.map((s) => <StatePanel key={s.key} state={s} />)}
          </div>
        </section>

        <Footer
          markTitle={
            <>
              System laboratory.
              <br />
              Internal only.
            </>
          }
          markSubtitle="Not a public surface. Re-skin the chassis with data-skin."
          meta={[
            { dt: "Surface", dd: "/system" },
            { dt: "Audience", dd: "Designers" },
            { dt: "Source", dd: "Sol baseline" },
            { dt: "Static", dd: "Internal" },
          ]}
          subscribe={{
            label: "Design notes",
            sublabel: "Internal changelog — not for users.",
            placeholder: "designer@team",
            buttonLabel: "Subscribe",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Lab" },
            { kind: "link", value: "Home", href: "/" },
            { kind: "link", value: "Tokens", href: "/system#tokens" },
            { kind: "link", value: "States", href: "/system#states" },
            { kind: "small", value: "Static · internal" },
          ]}
        />
      </Machine>
    </main>
  );
}
import * as React from "react";
import {
  Machine,
  TopDeck,
  HOME_NAV,
  HeroDeck,
  Module,
  LowerBank,
  Footer,
  StatusRail,
} from "./components";

const TOOLS = [
  { mark: "PX", name: "Perplexity Pro", note: "Real-time research", tag: "Research" },
  { mark: "CU", name: "Cursor", note: "AI-first code editor", tag: "Dev" },
  { mark: "RA", name: "Replit Agent", note: "Build and deploy", tag: "Build" },
];

const KITS = [
  { no: "01", name: "Ship a feature", note: "Plan, build, test, ship", tag: "Build" },
  { no: "02", name: "Compare AI tools", note: "Side-by-side evals", tag: "Decide" },
  { no: "03", name: "Write outreach", note: "Messages that get replies", tag: "Write" },
];

const JOBS: ReadonlyArray<readonly [string, string, string]> = [
  ["AI Engineer", "Remote", "Full-time"],
  ["ML Ops Engineer", "Europe", "Full-time"],
  ["Prompt Engineer", "Remote", "Contract"],
];

export default function Home(): JSX.Element {
  return (
    <main className="page-shell" data-page="home">
      <Machine>
        <TopDeck nav={HOME_NAV} />

        <HeroDeck
          kicker="Operational console"
          title={
            <>
              Find what works.
              <br />
              Ship what matters.
            </>
          }
          lede="Practical AI tools and prompts for engineers, builders, and operators. No noise. Just signal."
          actions={[
            {
              primary: true,
              href: "/tools",
              label: (
                <>
                  Explore tools <b>→</b>
                </>
              ),
            },
            { href: "/tools#featured", label: "Browse featured" },
            { href: "/prompt-kits", label: "Browse kits" },
          ]}
          overview={{
            href: "#tools",
            label: "How to read this preview",
          }}
        />

        <StatusRail
          ariaLabel="OpenRadar preview status"
          items={[
            {
              icon: <i className="status-icon">ϟ</i>,
              label: "Signals",
              detail: "Static preview",
            },
            {
              icon: <i className="status-icon">⌘</i>,
              label: "Tools",
              detail: "Curated sample",
            },
            {
              icon: <i className="status-icon">▱</i>,
              label: "Jobs",
              detail: "Sample roles",
            },
            {
              icon: <i className="pulse" />,
              label: "Feeds",
              detail: "Preview only",
            },
            {
              icon: <i className="status-icon">◷</i>,
              label: "Cadence",
              detail: "Static preview",
            },
          ]}
        />

        <section className="module-grid" aria-label="OpenRadar destinations">
          <Module title="Featured tools" code="01" className="tools-module" id="tools" actionHref="/tools">
            {TOOLS.map((tool) => (
              <div className="tool-row" key={tool.name}>
                <span className="tool-mark">{tool.mark}</span>
                <span>
                  <strong>{tool.name}</strong>
                  <small>{tool.note}</small>
                </span>
                <em>{tool.tag}</em>
              </div>
            ))}
          </Module>
          <Module title="Prompt kits" code="02" className="kits-module" id="kits" actionHref="/prompt-kits">
            {KITS.map((kit) => (
              <div className="kit-row" key={kit.no}>
                <b>{kit.no}</b>
                <span>
                  <strong>{kit.name}</strong>
                  <small>{kit.note}</small>
                </span>
                <em>{kit.tag}</em>
              </div>
            ))}
          </Module>
          <Module title="Learn path" code="03" className="learn-module" id="learn" actionHref="/learn">
            <div className="course">
              <span className="course-icon">▤</span>
              <span>
                <strong>AI Foundations</strong>
                <small>Sample path. 10 chapters.</small>
              </span>
            </div>
            <ol>
              <li>
                <span>What is AI, really?</span>
              </li>
              <li>
                <span>Prompts that work</span>
              </li>
              <li>
                <span>Tools overview</span>
              </li>
            </ol>
          </Module>
          <Module title="Jobs / roles" code="04" className="jobs-module" id="jobs" actionHref="/jobs">
            {JOBS.map(([name, place, type]) => (
              <div className="job-row" key={name}>
                <span>
                  <strong>{name}</strong>
                  <small>{place}</small>
                </span>
                <em>{type}</em>
              </div>
            ))}
          </Module>
        </section>

        <LowerBank
          panels={[
            {
              className: "signal-panel",
              label: "Selection standard",
              headline: "Curated sample",
              body: (
                <ul className="standards-list">
                  <li>
                    <i />
                    Representative use case
                  </li>
                  <li>
                    <i />
                    Practical evidence
                  </li>
                  <li>
                    <i />
                    No paid placement
                  </li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Latest field notes",
              headline: "Editorial desk",
              body: (
                <ul>
                  <li>
                    <b>01</b>
                    <span>Choosing a research assistant</span>
                    <time>Guide</time>
                  </li>
                  <li>
                    <b>02</b>
                    <span>When an AI coding tool pays off</span>
                    <time>Test</time>
                  </li>
                  <li>
                    <b>03</b>
                    <span>A prompt kit for sharper briefs</span>
                    <time>Kit</time>
                  </li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Coverage",
              headline: "Four surfaces",
              body: (
                <ul>
                  <li>
                    AI tools <i />
                  </li>
                  <li>
                    Prompt kits <i />
                  </li>
                  <li>
                    Learning paths <i />
                  </li>
                  <li>
                    Career roles <i />
                  </li>
                </ul>
              ),
            },
          ]}
        />

        <Footer
          markTitle={
            <>
              No hype. No spam.
              <br />
              Just what works.
            </>
          }
          markSubtitle="A static preview of the index. No live feeds, no subscriptions."
          meta={[
            { dt: "Focus", dd: "Practical AI" },
            { dt: "Source", dd: "Representative data" },
            { dt: "Format", dd: "Concise" },
            { dt: "Language", dd: "English" },
          ]}
          subscribe={{
            label: "Preview only",
            sublabel: "No subscriptions implemented in this preview.",
            placeholder: "preview-only",
            buttonLabel: "Preview only",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Preview" },
            { kind: "small", value: "Privacy · Terms · Contact — preview labels only" },
            { kind: "small", value: "No live content in this preview" },
          ]}
        />
      </Machine>
    </main>
  );
}
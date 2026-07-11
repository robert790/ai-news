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
    <main className="page-shell">
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
              href: "#tools",
              label: (
                <>
                  Explore tools <b>→</b>
                </>
              ),
            },
            { href: "#picks", label: "Today's picks" },
            { href: "#kits", label: "Browse kits" },
          ]}
          overview={{
            href: "#overview",
            label: "New here? Watch 60-sec overview",
          }}
        />

        <StatusRail
          ariaLabel="Current index status"
          items={[
            {
              icon: <i className="status-icon">ϟ</i>,
              label: "Signals",
              detail: "Reviewed daily",
            },
            {
              icon: <i className="status-icon">⌘</i>,
              label: "Tools",
              detail: "Curated index",
            },
            {
              icon: <i className="status-icon">▱</i>,
              label: "Jobs",
              detail: "Verified roles",
            },
            {
              icon: <i className="pulse" />,
              label: "Feeds",
              detail: "All channels online",
            },
            {
              icon: <i className="status-icon">◷</i>,
              label: "Cadence",
              detail: "Updated weekly",
            },
          ]}
        />

        <section className="module-grid" aria-label="OpenRadar destinations">
          <Module title="Featured tools" code="01" className="tools-module">
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
          <Module title="Prompt kits" code="02" className="kits-module">
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
          <Module title="Learn path" code="03" className="learn-module">
            <div className="course">
              <span className="course-icon">▤</span>
              <span>
                <strong>AI Foundations</strong>
                <small>Start here. 10 short chapters.</small>
              </span>
              <b>4 / 10</b>
            </div>
            <div className="progress">
              <i />
            </div>
            <ol>
              <li>
                <span>What is AI, really?</span>
                <b>✓</b>
              </li>
              <li>
                <span>Prompts that work</span>
                <b>✓</b>
              </li>
              <li>
                <span>Tools overview</span>
                <b>▶</b>
              </li>
            </ol>
          </Module>
          <Module title="Jobs / roles" code="04" className="jobs-module">
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
              headline: "Human reviewed",
              body: (
                <ul className="standards-list">
                  <li>
                    <i />
                    Clear use case
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
              headline: "Five surfaces",
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
                    Career signals <i />
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
          markSubtitle="Built for builders who ship."
          meta={[
            { dt: "Focus", dd: "Practical AI" },
            { dt: "Review", dd: "Human-led" },
            { dt: "Format", dd: "Concise" },
            { dt: "Language", dd: "English" },
          ]}
          subscribe={{
            label: "Stay in the loop",
            sublabel: "Get top signals weekly.",
            placeholder: "you@domain.com",
            buttonLabel: "Subscribe",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Status" },
            { kind: "link", value: "Privacy", href: "#privacy" },
            { kind: "link", value: "Terms", href: "#terms" },
            { kind: "link", value: "Contact", href: "#contact" },
            { kind: "small", value: "Designed for engineers. Built for operators." },
          ]}
        />
      </Machine>
    </main>
  );
}
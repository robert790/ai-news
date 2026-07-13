"use client";

import * as React from "react";
import {
  Machine,
  TopDeck,
  HeroDeck,
  StatusRail,
  Module,
  LowerBank,
  Footer,
} from "../components";

/**
 * OpenRadar /prompt-kits — practical reusable prompt kits.
 *
 * Internal + external-facing. Helps users discover vetted prompt
 * kits with practical utility. Static data only; no API calls,
 * no ingestion. Reuses the accepted chassis, tokens, and the
 * component library.
 *
 * Client-side: search by title/useCase, filter by category,
 * per-row copy action with visible success feedback. Mobile
 * disclosure (Show more / Show less) on the compact index.
 */

const PROMPT_NAV = [
  { label: "Home", href: "/" },
  { label: "Tools", href: "/tools" },
  { label: "Prompt Kits", href: "/prompt-kits", active: true },
  { label: "Learn", href: "/#learn" },
  { label: "Jobs", href: "/#jobs" },
];

type Category = "Build" | "Research" | "Decide" | "Write" | "Operate";
type Difficulty = "Beginner" | "Intermediate" | "Advanced";

type Kit = {
  id: string;
  mark: string;
  title: string;
  category: Category;
  audience: string;
  difficulty: Difficulty;
  setupMin: number;
  useCase: string;
  prompt: string;
  featured?: boolean;
};

const KITS: ReadonlyArray<Kit> = [
  {
    id: "code-review",
    mark: "CR",
    title: "Code review checklist",
    category: "Build",
    audience: "Developers",
    difficulty: "Beginner",
    setupMin: 5,
    useCase: "Catch regressions before merge with a reusable review pass",
    prompt:
      "You are a senior reviewer. Review the diff for correctness, edge cases, security, readability, and test coverage. Output a verdict (approve/changes), a numbered list of findings, and concrete patch suggestions for each.",
    featured: true,
  },
  {
    id: "ship-feature",
    mark: "SF",
    title: "Ship a feature, end to end",
    category: "Build",
    audience: "Builders",
    difficulty: "Intermediate",
    setupMin: 15,
    useCase: "Plan, scaffold, implement, test, and document a small feature",
    prompt:
      "Plan a vertical slice for the following feature. Produce: (1) user story + acceptance criteria, (2) file-level plan, (3) test plan, (4) implementation diff, (5) rollback plan.",
    featured: true,
  },
  {
    id: "compare-ai-tools",
    mark: "CT",
    title: "Compare AI tools side by side",
    category: "Decide",
    audience: "Operators",
    difficulty: "Beginner",
    setupMin: 5,
    useCase: "Make a defensible tool choice between 2–5 candidates",
    prompt:
      "Build a weighted decision matrix for the listed tools across capability, fit, cost, latency, privacy, and vendor risk. Recommend a primary pick and a fallback with reasons.",
    featured: true,
  },
  {
    id: "research-brief",
    mark: "RB",
    title: "Source-grounded research brief",
    category: "Research",
    audience: "Researchers",
    difficulty: "Intermediate",
    setupMin: 20,
    useCase: "Synthesize a topic into a brief with cited sources",
    prompt:
      "Produce a 1-page brief on the topic. Cite each non-trivial claim with an inline marker [n] tied to a numbered references list. Flag any claim that cannot be supported.",
    featured: true,
  },
  {
    id: "incident-postmortem",
    mark: "PM",
    title: "Incident postmortem",
    category: "Operate",
    audience: "Operators",
    difficulty: "Intermediate",
    setupMin: 30,
    useCase: "Run a blameless review that produces corrective actions",
    prompt:
      "Draft a blameless postmortem: timeline, contributing factors (Swiss-cheese), customer impact, what went well, what didn't, action items with owners and due dates.",
  },
  {
    id: "outreach",
    mark: "OR",
    title: "Write cold outreach that earns a reply",
    category: "Write",
    audience: "Operators",
    difficulty: "Beginner",
    setupMin: 10,
    useCase: "Short, specific, value-anchored cold email that respects the reader",
    prompt:
      "Draft a 90-word cold email to the recipient for the stated purpose. Open with a specific observation about their work, state a concrete value claim, and end with a low-friction ask.",
  },
  {
    id: "meeting-summary",
    mark: "MS",
    title: "Meeting summary with action ledger",
    category: "Write",
    audience: "Operators",
    difficulty: "Beginner",
    setupMin: 5,
    useCase: "Capture decisions, owners, and due dates from a transcript",
    prompt:
      "Summarize the transcript into: TL;DR (≤3 sentences), decisions made, action ledger (owner / action / due date), open questions. Use plain prose; no headers above the TL;DR.",
  },
  {
    id: "system-design",
    mark: "SD",
    title: "System design under constraints",
    category: "Build",
    audience: "Builders",
    difficulty: "Advanced",
    setupMin: 45,
    useCase: "Pressure-test an architecture for the stated workload",
    prompt:
      "For the stated requirements, produce: top-level diagram (ASCII), data model, scaling model, failure modes + mitigations, cost envelope, and 3 concrete risks we should monitor.",
  },
  {
    id: "user-interview",
    mark: "UI",
    title: "User interview script",
    category: "Research",
    audience: "Researchers",
    difficulty: "Beginner",
    setupMin: 10,
    useCase: "Open-ended script that surfaces behavior, not opinions",
    prompt:
      "Draft a 30-minute user interview script. Open with a warm-up, then 5 behavior-first questions (past tense), each with 2–3 neutral follow-ups. Close without leading.",
  },
  {
    id: "decision-log",
    mark: "DL",
    title: "Architecture decision record",
    category: "Decide",
    audience: "Builders",
    difficulty: "Beginner",
    setupMin: 10,
    useCase: "Capture context, options, trade-offs, and the chosen path",
    prompt:
      "Write an ADR: title, status, context, decision drivers, considered options with pros/cons, decision, and consequences (positive, negative, neutral).",
  },
  {
    id: "release-notes",
    mark: "RN",
    title: "Release notes for humans",
    category: "Write",
    audience: "Operators",
    difficulty: "Beginner",
    setupMin: 5,
    useCase: "Short, user-facing changelog that respects the reader",
    prompt:
      "From the raw commit list, draft user-facing release notes. Group by impact (New / Improved / Fixed), 1 line per item, no jargon, name the user-visible behavior change.",
  },
  {
    id: "playbook",
    mark: "PB",
    title: "Operations playbook",
    category: "Operate",
    audience: "Operators",
    difficulty: "Intermediate",
    setupMin: 30,
    useCase: "Turn tribal knowledge into a runnable procedure",
    prompt:
      "Interview the operator (answers below) and produce a numbered playbook with decision points, escalation paths, and rollback steps.",
  },
  {
    id: "competitive-scan",
    mark: "CS",
    title: "Competitive landscape scan",
    category: "Research",
    audience: "Operators",
    difficulty: "Intermediate",
    setupMin: 25,
    useCase: "Map the space without copying anyone",
    prompt:
      "From the listed competitors, produce a 2x2 positioning matrix (axes of your choice, justified), a feature parity table, and a candid assessment of where we are differentiated.",
  },
  {
    id: "pricing-test",
    mark: "PT",
    title: "Pricing page test plan",
    category: "Decide",
    audience: "Operators",
    difficulty: "Beginner",
    setupMin: 10,
    useCase: "Decide between pricing variants without lying to yourself",
    prompt:
      "Design a 2-week pricing A/B test: hypothesis, primary metric (and guardrails), minimum sample size, decision rule, and stop-loss. State what would invalidate the test.",
  },
  {
    id: "bug-triage",
    mark: "BT",
    title: "Bug triage queue",
    category: "Operate",
    audience: "Developers",
    difficulty: "Beginner",
    setupMin: 5,
    useCase: "Sort the incoming bug queue by impact and reversibility",
    prompt:
      "For each report: classify (bug / regression / docs / dup / wontfix), assign severity (S0–S3) with a one-line reason, suggest an owner queue, and propose a 24h action.",
  },
  {
    id: "spec-from-conversation",
    mark: "SC",
    title: "Spec from a customer conversation",
    category: "Build",
    audience: "Builders",
    difficulty: "Intermediate",
    setupMin: 20,
    useCase: "Turn notes into a buildable spec without losing nuance",
    prompt:
      "From the transcript, produce a spec: problem statement, success metric, non-goals, user stories, open questions, and a v1 surface list. Mark every assumption that came from inference.",
  },
];

const CATEGORIES: ReadonlyArray<{ id: Category | "All"; label: string; count: number }> = [
  { id: "All", label: "All", count: KITS.length },
  { id: "Build", label: "Build", count: KITS.filter((k) => k.category === "Build").length },
  { id: "Research", label: "Research", count: KITS.filter((k) => k.category === "Research").length },
  { id: "Decide", label: "Decide", count: KITS.filter((k) => k.category === "Decide").length },
  { id: "Write", label: "Write", count: KITS.filter((k) => k.category === "Write").length },
  { id: "Operate", label: "Operate", count: KITS.filter((k) => k.category === "Operate").length },
];

function KitMark({ mark }: { mark: string }) {
  return <span className="kit-mark">{mark}</span>;
}

function FeaturedKitCard({ kit }: { kit: Kit }) {
  return (
    <Module title={kit.title} code={kit.mark} className="kits-feature">
      <div className="kits-feature__body">
        <p className="kits-feature__lede">{kit.useCase}</p>
        <ul className="kits-feature__meta">
          <li><span>Category</span><strong>{kit.category}</strong></li>
          <li><span>Audience</span><strong>{kit.audience}</strong></li>
          <li><span>Level</span><strong>{kit.difficulty}</strong></li>
          <li><span>Setup</span><strong>~{kit.setupMin} min</strong></li>
        </ul>
      </div>
    </Module>
  );
}

function KitRow({ kit, copied, onCopy }: { kit: Kit; copied: boolean; onCopy: () => void }) {
  return (
    <div className="kit-row">
      <KitMark mark={kit.mark} />
      <span>
        <strong>{kit.title}</strong>
        <small>{kit.useCase}</small>
      </span>
      <em>{kit.category}</em>
      <em>{kit.difficulty}</em>
      <em aria-label={`Setup time ${kit.setupMin} minutes`}>~{kit.setupMin}m</em>
      <button
        type="button"
        className={`kit-copy${copied ? " kit-copy--ok" : ""}`}
        onClick={onCopy}
        aria-label={`Copy prompt for ${kit.title}`}
        title="Copy the full prompt to your clipboard"
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}

function CategoryChip({
  id,
  label,
  count,
  active,
  onSelect,
}: {
  id: Category | "All";
  label: string;
  count: number;
  active: boolean;
  onSelect: (id: Category | "All") => void;
}) {
  return (
    <button
      type="button"
      className={`kits-chip ${active ? "kits-chip--active" : ""}`}
      aria-pressed={active}
      aria-label={`Filter by ${label} (${count} kits)`}
      onClick={() => onSelect(id)}
    >
      <span className="kits-chip__label">{label}</span>
      <span className="kits-chip__count" aria-hidden="true">{count}</span>
    </button>
  );
}

function EmptyState({ onClear }: { onClear: () => void }) {
  return (
    <Module title="No matches" code="00" className="kits-empty">
      <div className="kits-state">
        <p className="kits-state__title">No kits match this signal.</p>
        <p className="kits-state__body">
          Clear the active filters or try a broader term.
        </p>
        <button
          type="button"
          className="kits-state__clear"
          onClick={onClear}
        >
          Clear filters
        </button>
      </div>
    </Module>
  );
}

export default function PromptKits() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState<Category | "All">("All");
  const [copiedId, setCopiedId] = React.useState<string | null>(null);
  const [mobileExpanded, setMobileExpanded] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(max-width: 760px)");
    const sync = () => setIsMobile(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  const MOBILE_LIMIT = 6;

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return KITS.filter((k) => {
      const matchCat = category === "All" || k.category === category;
      const matchQuery =
        q === "" ||
        k.title.toLowerCase().includes(q) ||
        k.useCase.toLowerCase().includes(q);
      return matchCat && matchQuery;
    });
  }, [query, category]);

  const featured = React.useMemo(
    () => filtered.filter((k) => k.featured).slice(0, 4),
    [filtered],
  );
  const compact = filtered;

  const isMobileLimited = isMobile && compact.length > MOBILE_LIMIT;
  const isMobileCollapsed = isMobile && !mobileExpanded && isMobileLimited;
  const compactVisible = isMobileCollapsed ? compact.slice(0, MOBILE_LIMIT) : compact;
  const compactHiddenCount = isMobileLimited ? compact.length - MOBILE_LIMIT : 0;

  const countFor = React.useCallback(
    (id: Category | "All") => {
      const q = query.trim().toLowerCase();
      return KITS.filter((k) => {
        const matchCat = id === "All" || k.category === id;
        const matchQuery =
          q === "" ||
          k.title.toLowerCase().includes(q) ||
          k.useCase.toLowerCase().includes(q);
        return matchCat && matchQuery;
      }).length;
    },
    [query],
  );

  const handleCopy = React.useCallback(async (kit: Kit) => {
    const text = `${kit.title}\n\n${kit.useCase}\n\n${kit.prompt}`;
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else if (typeof document !== "undefined") {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopiedId(kit.id);
      window.setTimeout(() => {
        setCopiedId((current) => (current === kit.id ? null : current));
      }, 1600);
    } catch {
      // best-effort clipboard; leave state untouched on failure
    }
  }, []);

  // Whether the active state is the unfiltered default (no search,
  // category = All). Only in this default state do we surface the
  // Featured kits grid; otherwise we hide Featured entirely.
  const isDefaultState = query.trim() === "" && category === "All";

  // Collapse mobile disclosure whenever filters change so the user
  // is shown only the first 6 rows of the new filtered set.
  React.useEffect(() => {
    setMobileExpanded(false);
  }, [query, category]);

  const handleClearFilters = React.useCallback(() => {
    setQuery("");
    setCategory("All");
    setMobileExpanded(false);
  }, []);

  return (
    <main className="page-shell" data-page="prompt-kits">
      <Machine ariaLabel="OpenRadar prompt kits index">
        <TopDeck nav={PROMPT_NAV} />

        <HeroDeck
          kicker="Prompt kits"
          title={
            <>
              Vetted prompts.
              <br />
              Practical reuse.
            </>
          }
          lede="A focused library of prompt kits for engineers, builders, and operators. Searchable by category, with audience, difficulty, and setup time for each entry."
          actions={[
            { primary: true, href: "#search", label: <>Search the kits <b>→</b></> },
            { href: "#featured", label: "Featured kits" },
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#legend", label: "How to use these kits" }}
        />

        <StatusRail
          ariaLabel="Prompt kits status"
          items={[
            { icon: <i className="status-icon">ϟ</i>, label: "Index", detail: `${filtered.length} / ${KITS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Categories", detail: "5 groups" },
            { icon: <i className="status-icon">▱</i>, label: "Updated", detail: "Weekly" },
            { icon: <i className="pulse" />, label: "Copy", detail: "Local" },
            { icon: <i className="status-icon">◷</i>, label: "Static", detail: "Internal" },
          ]}
        />

        <section id="search" className="kits-searchbar" aria-label="Search and filter">
          <Module title="Search the kits" code="00" className="kits-search-module">
            <div className="kits-searchbar__inner">
              <label className="kits-searchbar__field">
                <span className="kits-searchbar__label">
                  Search kits
                  <span className="kits-searchbar__count" aria-live="polite">
                    {filtered.length} match{filtered.length === 1 ? "" : "es"}
                  </span>
                </span>
                <input
                  type="search"
                  name="q"
                  placeholder="Try 'code review', 'cold outreach', 'ADR'…"
                  aria-label="Search kits by title or use case"
                  autoComplete="off"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className="kits-searchbar__chips" role="group" aria-label="Filter by category">
                {CATEGORIES.map((c) => (
                  <CategoryChip
                    key={c.id}
                    id={c.id}
                    label={c.label}
                    count={countFor(c.id)}
                    active={category === c.id}
                    onSelect={(id) => setCategory(id)}
                  />
                ))}
                {(query || category !== "All") && (
                  <button
                    type="button"
                    className="kits-reset"
                    onClick={() => {
                      setQuery("");
                      setCategory("All");
                    }}
                  >
                    Clear filters
                  </button>
                )}
              </div>
            </div>
          </Module>
        </section>

        {isDefaultState && featured.length > 0 && (
          <section id="featured" className="kits-featured-section" aria-label="Featured kits">
            <header className="kits-section__head">
              <h2>Featured kits</h2>
              <p>Hand-picked kits with broad utility and clear reuse paths.</p>
            </header>
            <div className="module-grid" aria-label="Featured kits grid">
              {featured.map((k) => <FeaturedKitCard key={k.id} kit={k} />)}
            </div>
          </section>
        )}

        <section id="all" className="kits-results-section" aria-label="All kits">
          <header className="kits-section__head">
            <h2>
              All kits
              <span className="kits-section__count" aria-live="polite">
                {compact.length} {compact.length === 1 ? "entry" : "entries"}
              </span>
            </h2>
            <p>
              {category === "All"
                ? "Across build, research, decide, write, and operate."
                : `Filtered to ${category.toLowerCase()}.`}
              {query.trim() && ` Matches "${query.trim()}".`}
            </p>
          </header>
          {compact.length === 0 ? (
            <EmptyState onClear={handleClearFilters} />
          ) : (
            <>
              <p className="kits-outbound-notice" role="note">
                Each kit is a copy-and-paste prompt — the Copy button writes the full kit (title, use case, prompt body) to your clipboard. No outbound network calls.
              </p>
              <Module title="Compact index" code="··" className="kits-results-module">
                <div className="kits-results" role="list">
                  {compactVisible.map((k) => (
                    <div role="listitem" key={k.id}>
                      <KitRow
                        kit={k}
                        copied={copiedId === k.id}
                        onCopy={() => handleCopy(k)}
                      />
                    </div>
                  ))}
                </div>
                {isMobileLimited && compactHiddenCount > 0 && (
                  <div className="kits-disclosure">
                    <button
                      type="button"
                      className="kits-disclosure__btn"
                      onClick={() => setMobileExpanded((v) => !v)}
                      aria-expanded={mobileExpanded}
                    >
                      {mobileExpanded
                        ? "Show less"
                        : `Show ${compactHiddenCount} more`}
                      <span aria-hidden="true">{mobileExpanded ? " ↑" : " ↓"}</span>
                    </button>
                  </div>
                )}
              </Module>
            </>
          )}
        </section>

        <LowerBank
          panels={[
            {
              className: "signal-panel",
              label: "Selection",
              headline: "How we pick",
              body: (
                <ul className="standards-list">
                  <li><i />Real reuse, not novelty</li>
                  <li><i />Outcome-shaped, not prompt-shaped</li>
                  <li><i />Audience + difficulty labeled</li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Coverage",
              headline: "What's next",
              body: (
                <ul>
                  <li><b>01</b><span>Per-kit examples</span><time>Soon</time></li>
                  <li><b>02</b><span>Learn tracks</span><time>Soon</time></li>
                  <li><b>03</b><span>Verified jobs</span><time>Soon</time></li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Reliability",
              headline: "Stays local",
              body: (
                <ul>
                  <li>Copy is local <i /></li>
                  <li>No tracking <i /></li>
                  <li>Reviewed weekly <i /></li>
                </ul>
              ),
            },
          ]}
        />

        <Footer
          markTitle={
            <>
              Prompt kits.
              <br />
              Practical reuse.
            </>
          }
          markSubtitle="Copy-and-paste kits for real work, with audience and difficulty labels."
          meta={[
            { dt: "Surface", dd: "/prompt-kits" },
            { dt: "Audience", dd: "Engineers" },
            { dt: "Source", dd: "Sol baseline" },
            { dt: "Static", dd: "Internal" },
          ]}
          subscribe={{
            label: "Kit digest",
            sublabel: "One new kit per week — internal changelog only.",
            placeholder: "designer@team",
            buttonLabel: "Subscribe",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Library" },
            { kind: "link", value: "Home", href: "/" },
            { kind: "link", value: "Tools", href: "/tools" },
            { kind: "link", value: "System", href: "/system" },
            { kind: "small", value: "Static · internal" },
          ]}
        />
      </Machine>
    </main>
  );
}

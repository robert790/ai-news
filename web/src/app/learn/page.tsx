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
 * OpenRadar /learn — practical AI learning tracks and lessons.
 *
 * Static data only; no APIs, no progress tracking, no completion %.
 * Reuses the accepted chassis, tokens, and component library.
 * Mirrors the /prompt-kits pattern: search + topic + level filters,
 * Featured tracks (default only), compact lesson index, mobile
 * Show more/less, Preview toggles inline summary, EmptyState with
 * Clear filters action.
 */

const LEARN_NAV = [
  { label: "Home", href: "/" },
  { label: "Tools", href: "/tools" },
  { label: "Prompt Kits", href: "/prompt-kits" },
  { label: "Learn", href: "/learn", active: true },
  { label: "Jobs", href: "/jobs" },
];

type Topic = "Foundations" | "Prompting" | "Building" | "Agents" | "Career";
type Level = "Beginner" | "Intermediate" | "Advanced";
type Format = "Reading" | "Hands-on" | "Walkthrough" | "Lab";

type Track = {
  id: string;
  title: string;
  audience: string;
  level: Level;
  hours: number;
  lessonCount: number;
  outcome: string;
};

type Lesson = {
  id: string;
  trackId: string;
  title: string;
  topic: Topic;
  level: Level;
  format: Format;
  minutes: number;
  outcome: string;
  summary: string;
  featured?: boolean;
};

const TRACKS: ReadonlyArray<Track> = [
  {
    id: "foundations",
    title: "AI foundations",
    audience: "Beginners",
    level: "Beginner",
    hours: 4,
    lessonCount: 6,
    outcome: "Read a transformer diagram, explain tokens, and pick a model for the task.",
  },
  {
    id: "prompting",
    title: "Prompting that works",
    audience: "Builders, writers",
    level: "Beginner",
    hours: 3,
    lessonCount: 5,
    outcome: "Write structured prompts with constraints, examples, and verification.",
  },
  {
    id: "building",
    title: "Building with AI",
    audience: "Developers, builders",
    level: "Intermediate",
    hours: 6,
    lessonCount: 6,
    outcome: "Ship a small feature with retrieval, evaluation, and a feedback loop.",
  },
  {
    id: "agents",
    title: "Agents and tools",
    audience: "Engineers",
    level: "Advanced",
    hours: 5,
    lessonCount: 5,
    outcome: "Design a tool-using agent with reliable handoffs and failure recovery.",
  },
];

const LESSONS: ReadonlyArray<Lesson> = [
  // foundations
  {
    id: "what-is-an-llm",
    trackId: "foundations",
    title: "What an LLM actually does",
    topic: "Foundations",
    level: "Beginner",
    format: "Reading",
    minutes: 15,
    outcome: "Describe tokens, context, and sampling in plain English.",
    summary:
      "Start with the working mental model. We walk through how a prompt becomes a sequence of tokens, why context windows matter, and how sampling shapes the output. Includes a one-page diagram and a short glossary.",
    featured: true,
  },
  {
    id: "tokens-and-context",
    trackId: "foundations",
    title: "Tokens and context windows",
    topic: "Foundations",
    level: "Beginner",
    format: "Reading",
    minutes: 12,
    outcome: "Estimate token costs and pick a model that fits the budget.",
    summary:
      "How tokens are counted, what overflow looks like, and the practical difference between 8k, 32k, and 200k context. We compare three model families and when each is worth the cost.",
  },
  {
    id: "sampling-explained",
    trackId: "foundations",
    title: "Sampling, temperature, and seed",
    topic: "Foundations",
    level: "Beginner",
    format: "Reading",
    minutes: 10,
    outcome: "Choose temperature for the task and explain top-p to a teammate.",
    summary:
      "Why temperature is not creativity and what top-p actually changes. Includes a side-by-side of the same prompt at temperature 0, 0.7, and 1.2.",
  },
  {
    id: "model-selection",
    trackId: "foundations",
    title: "Picking a model for the task",
    topic: "Foundations",
    level: "Beginner",
    format: "Walkthrough",
    minutes: 18,
    outcome: "Defend a model choice with concrete criteria.",
    summary:
      "A practical scoring rubric across capability, fit, latency, cost, privacy, and vendor risk. We score three concrete projects and explain the trade-offs.",
  },
  {
    id: "evals-as-a-beginner",
    trackId: "foundations",
    title: "Evals you can run tonight",
    topic: "Foundations",
    level: "Beginner",
    format: "Hands-on",
    minutes: 22,
    outcome: "Build a 20-case eval that catches obvious regressions.",
    summary:
      "A no-framework eval that runs in a spreadsheet. We'll build a checklist, write 20 cases, score them by hand, and learn what a flaky eval feels like before we trust any metric.",
  },
  {
    id: "when-not-to-use-ai",
    trackId: "foundations",
    title: "When not to use AI",
    topic: "Foundations",
    level: "Beginner",
    format: "Reading",
    minutes: 8,
    outcome: "Spot tasks where AI adds cost without adding value.",
    summary:
      "Short list of patterns where AI is the wrong default: deterministic transforms, low-stakes text with hard rules, and anything where the audit trail matters more than the speed.",
  },
  // prompting
  {
    id: "structure-prompts",
    trackId: "prompting",
    title: "Structured prompts",
    topic: "Prompting",
    level: "Beginner",
    format: "Hands-on",
    minutes: 16,
    outcome: "Write a prompt with role, constraints, examples, and a verification step.",
    summary:
      "The four parts every reliable prompt should have, in order. We rewrite a weak prompt three ways and compare outputs side by side.",
    featured: true,
  },
  {
    id: "examples-and-cot",
    trackId: "prompting",
    title: "Few-shot examples and chain-of-thought",
    topic: "Prompting",
    level: "Intermediate",
    format: "Hands-on",
    minutes: 20,
    outcome: "Use few-shot examples and CoT without bloating tokens.",
    summary:
      "When few-shot helps, when it hurts, and how to keep the chain short. Includes a reusable CoT scaffold and three examples of bad vs good chains.",
  },
  {
    id: "system-prompts",
    trackId: "prompting",
    title: "System prompts that survive contact",
    topic: "Prompting",
    level: "Intermediate",
    format: "Walkthrough",
    minutes: 14,
    outcome: "Write a system prompt that survives adversarial inputs.",
    summary:
      "Anatomy of a system prompt: identity, scope, refusal policy, and tone. We run three adversarial inputs against a draft system prompt and patch the leaks.",
  },
  {
    id: "verification-prompts",
    trackId: "prompting",
    title: "Verification, not vibes",
    topic: "Prompting",
    level: "Intermediate",
    format: "Hands-on",
    minutes: 18,
    outcome: "Add a verification step that catches hallucinations before delivery.",
    summary:
      "Three patterns for self-verification: quote-and-check, schema check, and adversarial re-read. Each is shown with a working prompt template.",
  },
  {
    id: "prompt-catalog",
    trackId: "prompting",
    title: "Building a prompt catalog",
    topic: "Prompting",
    level: "Beginner",
    format: "Reading",
    minutes: 9,
    outcome: "Maintain a small, reusable set of vetted prompts.",
    summary:
      "Why a 30-prompt catalog beats a 300-prompt one. Naming conventions, when to version, and how to retire prompts without breaking dependents.",
  },
  // building
  {
    id: "rag-minimum",
    trackId: "building",
    title: "Retrieval: the minimum that works",
    topic: "Building",
    level: "Intermediate",
    format: "Walkthrough",
    minutes: 25,
    outcome: "Wire retrieval over a small doc set with chunking, embeddings, and a reranker.",
    summary:
      "End-to-end RAG over 50 PDFs: ingestion, chunking choices, embeddings, retrieval, reranking, and a refusal policy. Includes a minimal stack that runs locally.",
    featured: true,
  },
  {
    id: "tool-use",
    trackId: "building",
    title: "Function calling and tool use",
    topic: "Building",
    level: "Intermediate",
    format: "Hands-on",
    minutes: 22,
    outcome: "Give a model three tools with reliable schemas and error handling.",
    summary:
      "Tool schemas that survive model error. We wire three tools (search, write file, send email) and practice recovering from a wrong-arg call.",
  },
  {
    id: "structured-output",
    trackId: "building",
    title: "Structured output without surprises",
    topic: "Building",
    level: "Intermediate",
    format: "Hands-on",
    minutes: 17,
    outcome: "Constrain output to a JSON schema and validate before downstream use.",
    summary:
      "JSON mode vs tool mode, schema versioning, and how to validate without trusting. Includes a TypeScript validator that fails fast on shape drift.",
  },
  {
    id: "feedback-loop",
    trackId: "building",
    title: "Feedback loop and tracing",
    topic: "Building",
    level: "Intermediate",
    format: "Walkthrough",
    minutes: 19,
    outcome: "Capture prompts, outputs, and user feedback for weekly review.",
    summary:
      "Minimal trace schema and a weekly review ritual. We walk through a real trace, find three problems, and ship a fix that improves the eval by 8%.",
  },
  {
    id: "caching-and-cost",
    trackId: "building",
    title: "Caching and cost control",
    topic: "Building",
    level: "Intermediate",
    format: "Reading",
    minutes: 11,
    outcome: "Cut inference cost in half with prompt caching and tiered routing.",
    summary:
      "Three caching layers (exact, semantic, prefix), tiered routing by task, and budget guardrails. We show a real bill before and after.",
  },
  {
    id: "deploy-safely",
    trackId: "building",
    title: "Deploying AI features safely",
    topic: "Building",
    level: "Intermediate",
    format: "Walkthrough",
    minutes: 20,
    outcome: "Ship behind a flag with a kill switch and a clear rollback plan.",
    summary:
      "Feature flags, kill switches, traffic shaping, and rollback drills. Includes a checklist for staging, dark launches, and incident response.",
  },
  // agents
  {
    id: "agent-shapes",
    trackId: "agents",
    title: "Shapes of AI agents",
    topic: "Agents",
    level: "Advanced",
    format: "Reading",
    minutes: 14,
    outcome: "Distinguish reflex, plan-and-execute, and human-in-the-loop patterns.",
    summary:
      "The three patterns most agents fall into, with a diagram and a worked example. We pick the wrong one on purpose and see what fails.",
    featured: true,
  },
  {
    id: "reliable-handoffs",
    trackId: "agents",
    title: "Reliable handoffs and recovery",
    topic: "Agents",
    level: "Advanced",
    format: "Hands-on",
    minutes: 24,
    outcome: "Design agent handoffs with retries, timeouts, and explicit failure modes.",
    summary:
      "How to make a multi-step agent survive a flaky tool. Retries with jitter, hard timeouts, structured failure messages, and a recovery prompt.",
  },
  {
    id: "guardrails",
    trackId: "agents",
    title: "Guardrails without theater",
    topic: "Agents",
    level: "Advanced",
    format: "Walkthrough",
    minutes: 18,
    outcome: "Pick guardrails that fail loud rather than fail silent.",
    summary:
      "Input filters, output filters, and policy checkers — and why each is good at one thing and bad at others. We compare three real guardrail stacks.",
  },
  {
    id: "evals-for-agents",
    trackId: "agents",
    title: "Evals for agents",
    topic: "Agents",
    level: "Advanced",
    format: "Hands-on",
    minutes: 23,
    outcome: "Score agent traces for correctness, recovery, and waste.",
    summary:
      "Beyond pass/fail: outcome score, recovery score, and tool-call efficiency. We build a 30-case eval and watch one model improve by 12%.",
  },
  {
    id: "agent-cost",
    trackId: "agents",
    title: "Cost-aware agent design",
    topic: "Agents",
    level: "Advanced",
    format: "Reading",
    minutes: 10,
    outcome: "Cap an agent's spend before it caps your runway.",
    summary:
      "Per-step budgets, total budget guards, and tiered model routing. Includes a one-page cost model you can adapt.",
  },
  // career
  {
    id: "career-switch",
    trackId: "foundations",
    title: "Switching into AI from another role",
    topic: "Career",
    level: "Beginner",
    format: "Reading",
    minutes: 13,
    outcome: "Map your existing skills to an AI role and pick a first project.",
    summary:
      "Most switchers underestimate their existing leverage. We walk through five career paths (writer, ops, support, analyst, engineer) and pick a first project that compounds.",
  },
  {
    id: "build-a-portfolio",
    trackId: "building",
    title: "A portfolio that actually proves it",
    topic: "Career",
    level: "Beginner",
    format: "Walkthrough",
    minutes: 17,
    outcome: "Plan three portfolio pieces that demonstrate shipping, not just talking.",
    summary:
      "Three portfolio patterns: a small useful tool, a clear teardown of someone else's system, and a written post-mortem of your own. We pick titles and scope each one.",
  },
  {
    id: "first-interview-loop",
    trackId: "building",
    title: "Your first AI interview loop",
    topic: "Career",
    level: "Beginner",
    format: "Reading",
    minutes: 9,
    outcome: "Know what to expect on a take-home and a system-design round.",
    summary:
      "The two rounds most candidates underestimate: the take-home and the system-design conversation. We sketch what good looks like for each.",
  },
  {
    id: "writing-on-the-topic",
    trackId: "foundations",
    title: "Writing publicly about your work",
    topic: "Career",
    level: "Beginner",
    format: "Reading",
    minutes: 11,
    outcome: "Pick one channel and ship a first post in a weekend.",
    summary:
      "Public writing compounds. We pick a topic, an audience, and a first post that takes a weekend to write and a year to pay off.",
  },
];

const TOPICS: ReadonlyArray<Topic> = ["Foundations", "Prompting", "Building", "Agents", "Career"];
const LEVELS: ReadonlyArray<Level> = ["Beginner", "Intermediate", "Advanced"];

function formatTopicCount(t: Topic): number {
  return LESSONS.filter((l) => l.topic === t).length;
}
function formatLevelCount(l: Level): number {
  return LESSONS.filter((les) => les.level === l).length;
}

function TopicChip({
  label,
  count,
  active,
  onSelect,
}: {
  label: string;
  count: number;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`learn-chip ${active ? "learn-chip--active" : ""}`}
      aria-pressed={active}
      aria-label={`Filter by topic ${label} (${count} lessons)`}
      onClick={onSelect}
    >
      <span className="learn-chip__label">{label}</span>
      <span className="learn-chip__count" aria-hidden="true">{count}</span>
    </button>
  );
}

function LevelChip({
  label,
  count,
  active,
  onSelect,
}: {
  label: Level;
  count: number;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`learn-chip ${active ? "learn-chip--active" : ""}`}
      aria-pressed={active}
      aria-label={`Filter by level ${label} (${count} lessons)`}
      onClick={onSelect}
    >
      <span className="learn-chip__label">{label}</span>
      <span className="learn-chip__count" aria-hidden="true">{count}</span>
    </button>
  );
}

function FeaturedTrackCard({ track, lessonCount }: { track: Track; lessonCount: number }) {
  return (
    <Module title={track.title} code={track.id.slice(0, 2).toUpperCase()} className="learn-feature">
      <div className="learn-feature__body">
        <p className="learn-feature__lede">{track.outcome}</p>
        <ul className="learn-feature__meta">
          <li><span>Audience</span><strong>{track.audience}</strong></li>
          <li><span>Level</span><strong>{track.level}</strong></li>
          <li><span>Time</span><strong>~{track.hours}h</strong></li>
          <li><span>Lessons</span><strong>{lessonCount}</strong></li>
        </ul>
      </div>
    </Module>
  );
}

function LessonRow({
  lesson,
  expanded,
  onToggle,
}: {
  lesson: Lesson;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <article className={`lesson-row ${expanded ? "lesson-row--open" : ""}`}>
      <header className="lesson-row__head">
        <span className="lesson-mark">{lesson.id.slice(0, 2).toUpperCase()}</span>
        <span>
          <strong>{lesson.title}</strong>
          <small>{lesson.outcome}</small>
        </span>
        <span className="lesson-row__meta">
          <em>{lesson.topic}</em>
          <em>{lesson.level}</em>
          <em aria-label={`${lesson.minutes} minutes`}>~{lesson.minutes}m</em>
          <em>{lesson.format}</em>
        </span>
        <button
          type="button"
          className="lesson-preview"
          aria-expanded={expanded}
          aria-controls={`lesson-summary-${lesson.id}`}
          onClick={onToggle}
        >
          {expanded ? "Hide" : "Preview"}
        </button>
      </header>
      {expanded && (
        <div id={`lesson-summary-${lesson.id}`} className="lesson-row__summary" role="region">
          <p>{lesson.summary}</p>
        </div>
      )}
    </article>
  );
}

function EmptyState({ onClear }: { onClear: () => void }) {
  return (
    <Module title="No lessons match this signal" code="00" className="learn-empty">
      <div className="learn-state">
        <p className="learn-state__title">No lessons match this signal.</p>
        <p className="learn-state__body">
          Clear the active filters or try a broader term.
        </p>
        <button
          type="button"
          className="learn-state__clear"
          onClick={onClear}
        >
          Clear filters
        </button>
      </div>
    </Module>
  );
}

export default function Learn() {
  const [query, setQuery] = React.useState("");
  const [topic, setTopic] = React.useState<Topic | "All">("All");
  const [level, setLevel] = React.useState<Level | "All">("All");
  const [expandedId, setExpandedId] = React.useState<string | null>(null);
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

  const isDefaultState =
    query.trim() === "" && topic === "All" && level === "All";

  React.useEffect(() => {
    setMobileExpanded(false);
    setExpandedId(null);
  }, [query, topic, level]);

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return LESSONS.filter((l) => {
      const matchTopic = topic === "All" || l.topic === topic;
      const matchLevel = level === "All" || l.level === level;
      const matchQuery =
        q === "" ||
        l.title.toLowerCase().includes(q) ||
        l.outcome.toLowerCase().includes(q);
      return matchTopic && matchLevel && matchQuery;
    });
  }, [query, topic, level]);

  const featured = React.useMemo(
    () => filtered.filter((l) => l.featured).slice(0, 4),
    [filtered],
  );

  const featuredTracks = React.useMemo(() => {
    return TRACKS.map((t) => {
      const lessonsForTrack = filtered.filter((l) => l.trackId === t.id);
      return { track: t, lessonCount: lessonsForTrack.length };
    });
  }, [filtered]);

  const compact = filtered;
  const isMobileLimited = isMobile && compact.length > MOBILE_LIMIT;
  const isMobileCollapsed = isMobile && !mobileExpanded && isMobileLimited;
  const compactVisible = isMobileCollapsed ? compact.slice(0, MOBILE_LIMIT) : compact;
  const compactHiddenCount = isMobileLimited ? compact.length - MOBILE_LIMIT : 0;

  const topicCountFor = React.useCallback(
    (t: Topic | "All") => {
      const q = query.trim().toLowerCase();
      const lvl = level;
      return LESSONS.filter((l) => {
        const matchTopic = t === "All" || l.topic === t;
        const matchLevel = lvl === "All" || l.level === lvl;
        const matchQuery =
          q === "" ||
          l.title.toLowerCase().includes(q) ||
          l.outcome.toLowerCase().includes(q);
        return matchTopic && matchLevel && matchQuery;
      }).length;
    },
    [query, level],
  );

  const levelCountFor = React.useCallback(
    (l: Level | "All") => {
      const q = query.trim().toLowerCase();
      const tp = topic;
      return LESSONS.filter((les) => {
        const matchLevel = l === "All" || les.level === l;
        const matchTopic = tp === "All" || les.topic === tp;
        const matchQuery =
          q === "" ||
          les.title.toLowerCase().includes(q) ||
          les.outcome.toLowerCase().includes(q);
        return matchTopic && matchLevel && matchQuery;
      }).length;
    },
    [query, topic],
  );

  const handleClearFilters = React.useCallback(() => {
    setQuery("");
    setTopic("All");
    setLevel("All");
    setMobileExpanded(false);
    setExpandedId(null);
  }, []);

  return (
    <main className="page-shell" data-page="learn">
      <Machine ariaLabel="OpenRadar learning index">
        <TopDeck nav={LEARN_NAV} />

        <HeroDeck
          kicker="Learn"
          title={
            <>
              Practical AI skills,
              <br />
              in the right order.
            </>
          }
          lede="A focused learning index for engineers, builders, writers, and career switchers. Pick a track, scan the lessons, and start with the right prerequisites."
          actions={[
            { primary: true, href: "#search", label: <>Search lessons <b>→</b></> },
            { href: "#tracks", label: "Featured tracks" },
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#legend", label: "How to read these lessons" }}
        />

        <StatusRail
          ariaLabel="Learn status"
          items={[
            { icon: <i className="status-icon">▣</i>, label: "Lessons", detail: `${filtered.length} / ${LESSONS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Topics", detail: `${TOPICS.length}` },
            { icon: <i className="status-icon">⊟</i>, label: "Tracks", detail: `${TRACKS.length}` },
            { icon: <i className="pulse" />, label: "Status", detail: "Static" },
            { icon: <i className="status-icon">◷</i>, label: "Updated", detail: "Weekly" },
          ]}
        />

        <section id="search" className="learn-searchbar" aria-label="Search and filter lessons">
          <Module title="Search lessons" code="00" className="learn-search-module">
            <div className="learn-searchbar__inner">
              <label className="learn-searchbar__field">
                <span className="learn-searchbar__label">
                  Search lessons
                  <span className="learn-searchbar__count" aria-live="polite">
                    {filtered.length} match{filtered.length === 1 ? "" : "es"}
                  </span>
                </span>
                <input
                  type="search"
                  name="q"
                  placeholder="Try 'evals', 'tools', 'portfolio'…"
                  aria-label="Search lessons by title or outcome"
                  autoComplete="off"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className="learn-searchbar__chips" role="group" aria-label="Filter by topic">
                {TOPICS.map((t) => (
                  <TopicChip
                    key={t}
                    label={t}
                    count={topicCountFor(t)}
                    active={topic === t}
                    onSelect={() => setTopic(topic === t ? "All" : t)}
                  />
                ))}
              </div>
              <div className="learn-searchbar__chips" role="group" aria-label="Filter by level">
                {LEVELS.map((l) => (
                  <LevelChip
                    key={l}
                    label={l}
                    count={levelCountFor(l)}
                    active={level === l}
                    onSelect={() => setLevel(level === l ? "All" : l)}
                  />
                ))}
                {(query || topic !== "All" || level !== "All") && (
                  <button
                    type="button"
                    className="learn-reset"
                    onClick={handleClearFilters}
                  >
                    Clear filters
                  </button>
                )}
              </div>
            </div>
          </Module>
        </section>

        {isDefaultState && (
          <section id="tracks" className="learn-featured-section" aria-label="Featured tracks">
            <header className="learn-section__head">
              <h2>Featured tracks</h2>
              <p>Four tracks that cover the path from first prompts to reliable agents.</p>
            </header>
            <div className="module-grid" aria-label="Featured tracks grid">
              {featuredTracks.map(({ track, lessonCount }) => (
                <FeaturedTrackCard
                  key={track.id}
                  track={track}
                  lessonCount={lessonCount}
                />
              ))}
            </div>
          </section>
        )}

        <section id="all" className="learn-results-section" aria-label="All lessons">
          <header className="learn-section__head">
            <h2>
              All lessons
              <span className="learn-section__count" aria-live="polite">
                {compact.length} {compact.length === 1 ? "entry" : "entries"}
              </span>
            </h2>
            <p>
              {topic === "All" && level === "All"
                ? "Across foundations, prompting, building, agents, and career."
                : `Filtered to ${topic !== "All" ? topic.toLowerCase() : "any topic"}, ${level !== "All" ? level.toLowerCase() : "any level"}.`}
              {query.trim() && ` Matches "${query.trim()}".`}
            </p>
          </header>
          {compact.length === 0 ? (
            <EmptyState onClear={handleClearFilters} />
          ) : (
            <>
              <p className="learn-outbound-notice" role="note">
                Preview opens an inline summary for each lesson — no navigation, no progress tracking.
              </p>
              <Module title="Compact index" code="··" className="learn-results-module">
                <div className="learn-results" role="list">
                  {compactVisible.map((lesson) => (
                    <div role="listitem" key={lesson.id}>
                      <LessonRow
                        lesson={lesson}
                        expanded={expandedId === lesson.id}
                        onToggle={() =>
                          setExpandedId((current) =>
                            current === lesson.id ? null : lesson.id,
                          )
                        }
                      />
                    </div>
                  ))}
                </div>
                {isMobileLimited && compactHiddenCount > 0 && (
                  <div className="learn-disclosure">
                    <button
                      type="button"
                      className="learn-disclosure__btn"
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
                  <li><i />Real utility, not novelty</li>
                  <li><i />Order matters — foundations first</li>
                  <li><i />Outcome-shaped lessons</li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Coverage",
              headline: "What's next",
              body: (
                <ul>
                  <li><b>01</b><span>Per-track examples</span><time>Soon</time></li>
                  <li><b>02</b><span>Verified jobs</span><time>Soon</time></li>
                  <li><b>03</b><span>Project archive</span><time>Soon</time></li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Reliability",
              headline: "Stays current",
              body: (
                <ul>
                  <li>Reviewed weekly <i /></li>
                  <li>No tracking <i /></li>
                  <li>Static indexes <i /></li>
                </ul>
              ),
            },
          ]}
        />

        <Footer
          markTitle={
            <>
              Learn.
              <br />
              Practical skills.
            </>
          }
          markSubtitle="A focused learning index for AI work — foundations first, agents last."
          meta={[
            { dt: "Surface", dd: "/learn" },
            { dt: "Audience", dd: "All levels" },
            { dt: "Source", dd: "Sol baseline" },
            { dt: "Static", dd: "Internal" },
          ]}
          subscribe={{
            label: "Lesson digest",
            sublabel: "One new lesson per week — internal changelog only.",
            placeholder: "designer@team",
            buttonLabel: "Subscribe",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Learn" },
            { kind: "link", value: "Home", href: "/" },
            { kind: "link", value: "Tools", href: "/tools" },
            { kind: "link", value: "Prompt Kits", href: "/prompt-kits" },
            { kind: "link", value: "System", href: "/system" },
            { kind: "small", value: "Static · internal" },
          ]}
        />
      </Machine>
    </main>
  );
}
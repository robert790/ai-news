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

import { promptRecords } from "@/content/prompts";
import {
  selectPromptKitsPilotV1,
  professionalSafetyNoticeFor,
  PromptKitsPilotV1UnavailableError,
} from "@/content/prompts/selectors";
import type {
  PromptRecord,
  PromptDifficulty,
  PromptSafetyClass,
} from "@/content/prompts";

/**
 * OpenRadar /prompt-kits — practical reusable prompt kits.
 *
 * Pilot V1 wiring: the page reads its record set exclusively from the
 * canonical prompt-content pilot (`web/src/content/prompts/index.ts`)
 * via `selectPromptKitsPilotV1`. There is no duplicated prompt text or
 * static fallback dataset in this file.
 *
 * Eligibility is enforced inside the selector:
 *   reviewStatus === "approved"
 *   commercialUseStatus === "cleared"
 *   publicationEligibility === "prompt-kits"
 *
 * If the canonical catalog contains zero eligible records, the page
 * renders a clear, dev-time failure message instead of an empty grid.
 *
 * Copy semantics: the Copy button writes the canonical `prompt` body
 * verbatim. Placeholders are not transformed.
 *
 * Safety notice: records with safetyClass "professional" render a
 * restrained human-review notice inside the expanded detail region.
 * General records render no notice.
 */

const PROMPT_NAV = [
  { label: "Home", href: "/" },
  { label: "Tools", href: "/tools" },
  { label: "Prompt Kits", href: "/prompt-kits", active: true },
  { label: "Learn", href: "/learn" },
  { label: "Jobs", href: "/jobs" },
];

/**
 * The five canonical Pilot V1 categories, frozen to the canonical
 * lock order. The route surfaces a chip per category that has at
 * least one eligible record in the current selection.
 */
type CategoryId =
  | "code"
  | "write"
  | "research"
  | "decide"
  | "operate"
  | "design"
  | "agent";

type Category = "Build" | "Research" | "Decide" | "Write" | "Operate" | "Design";
type Difficulty = "Beginner" | "Intermediate" | "Advanced";

/**
 * View-model shape exposed by the route. Built from a canonical
 * `PromptRecord` plus a small UI-only presentation label. The
 * canonical record is preserved unchanged on the view-model as
 * `record` so the detail surface can render inputs, notes, and
 * anti-patterns directly from the source.
 */
type Kit = {
  id: string;
  /** Two-letter mark used for the kit-row badge. */
  mark: string;
  title: string;
  category: Category;
  categoryId: CategoryId;
  audience: string;
  difficulty: Difficulty;
  useCase: string;
  expectedOutput: string;
  /** Canonical prompt body, copied verbatim by the Copy action. */
  prompt: string;
  /** Safety classification as defined by the canonical contract. */
  safetyClass: PromptSafetyClass;
  /** Collection ids this record belongs to (display only). */
  collections: string[];
  /** Inputs as declared on the canonical record. */
  inputs: PromptRecord["inputs"];
  /** Notes as declared on the canonical record. */
  notes: PromptRecord["notes"];
  /** Anti-patterns as declared on the canonical record. */
  antiPatterns: PromptRecord["antiPatterns"];
  /** The canonical record itself, preserved for downstream surfaces. */
  record: PromptRecord;
};

const CATEGORY_LABEL: Record<CategoryId, Category> = {
  code: "Build",
  write: "Write",
  research: "Research",
  decide: "Decide",
  operate: "Operate",
  design: "Design",
  agent: "Build",
};

const DIFFICULTY_LABEL: Record<PromptDifficulty, Difficulty> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

/**
 * Two-letter mark derived from the canonical id. Stable across edits
 * because the id is immutable.
 */
function markFor(id: string): string {
  const parts = id.split("-").filter(Boolean);
  if (parts.length === 0) return "··";
  if (parts.length === 1) return (parts[0] ?? "").slice(0, 2).toUpperCase();
  const first = parts[0]?.[0] ?? "";
  const last = parts[parts.length - 1]?.[0] ?? "";
  return `${first}${last}`.toUpperCase();
}

/**
 * Build the page view-model from a canonical record. Pure.
 */
function toKit(rec: PromptRecord): Kit {
  return {
    id: rec.id,
    mark: markFor(rec.id),
    title: rec.title,
    category: CATEGORY_LABEL[rec.category],
    categoryId: rec.category,
    audience: rec.audience,
    difficulty: DIFFICULTY_LABEL[rec.difficulty],
    useCase: rec.useCase,
    expectedOutput: rec.expectedOutput,
    prompt: rec.prompt,
    safetyClass: rec.safetyClass,
    collections: [...rec.collectionIds],
    inputs: rec.inputs,
    notes: rec.notes,
    antiPatterns: rec.antiPatterns,
    record: rec,
  };
}

/**
 * Read the canonical catalog and select the Pilot V1 records. Throws
 * `PromptKitsPilotV1UnavailableError` when zero records are eligible;
 * the page renders a clear failure state in that case instead of an
 * empty grid.
 */
function loadKits(): Kit[] {
  const records = selectPromptKitsPilotV1(promptRecords);
  return records.map(toKit);
}

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
          <li><span>Collection</span><strong>{kit.collections[0] ?? "—"}</strong></li>
        </ul>
      </div>
    </Module>
  );
}

/**
 * Expanded detail surface for a single canonical Pilot V1 record.
 * Renders:
 *   - title and use case
 *   - input variables with labels and descriptions
 *   - the full canonical prompt body (verbatim)
 *   - expected output
 *   - notes
 *   - anti-patterns
 *   - copy-prompt action
 *   - restrained human-review notice when safetyClass === "professional"
 *
 * The detail surface is rendered inline below the row using the
 * existing kit-row expandable-region pattern; no new route is used.
 */
function KitDetail({
  kit,
  onCopy,
  copied,
}: {
  kit: Kit;
  onCopy: () => void;
  copied: boolean;
}) {
  const safetyNotice =
    kit.safetyClass === "professional"
      ? professionalSafetyNoticeFor(kit.record)
      : null;
  return (
    <div className="kit-detail">
      <div className="kit-detail__section">
        <h4 className="kit-detail__heading">Use case</h4>
        <p className="kit-detail__prose">{kit.useCase}</p>
      </div>

      {safetyNotice && (
        <div
          className="kit-detail__safety"
          role="note"
          aria-label="Human-review notice"
        >
          <span className="kit-detail__safety-tag">Human review</span>
          <p className="kit-detail__safety-body">{safetyNotice}</p>
        </div>
      )}

      {kit.inputs.length > 0 && (
        <div className="kit-detail__section">
          <h4 className="kit-detail__heading">Input variables</h4>
          <dl className="kit-detail__inputs">
            {kit.inputs.map((input) => (
              <div key={input.name} className="kit-detail__input">
                <dt>
                  <code className="kit-detail__input-name">{`{${input.name}}`}</code>
                  <span className="kit-detail__input-label">{input.label}</span>
                </dt>
                <dd>{input.description}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      <div className="kit-detail__section">
        <div className="kit-detail__section-head">
          <h4 className="kit-detail__heading">Prompt body</h4>
          <button
            type="button"
            className={`kit-detail__copy${copied ? " kit-detail__copy--ok" : ""}`}
            onClick={onCopy}
            aria-label={`Copy canonical prompt body for ${kit.title}`}
            title="Copy the canonical prompt body to your clipboard"
          >
            {copied ? "Copied" : "Copy prompt"}
          </button>
        </div>
        <pre className="kit-detail__prompt" tabIndex={0}>
          <code>{kit.prompt}</code>
        </pre>
      </div>

      <div className="kit-detail__section">
        <h4 className="kit-detail__heading">Expected output</h4>
        <p className="kit-detail__prose">{kit.expectedOutput}</p>
      </div>

      {kit.notes.length > 0 && (
        <div className="kit-detail__section">
          <h4 className="kit-detail__heading">Notes</h4>
          <ul className="kit-detail__list">
            {kit.notes.map((n, idx) => (
              <li key={`${kit.id}-note-${idx}`}>
                <strong>{n.title}</strong>
                <span>{n.body}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {kit.antiPatterns.length > 0 && (
        <div className="kit-detail__section">
          <h4 className="kit-detail__heading">Anti-patterns</h4>
          <ul className="kit-detail__list kit-detail__list--warn">
            {kit.antiPatterns.map((a, idx) => (
              <li key={`${kit.id}-anti-${idx}`}>
                <strong>{a.title}</strong>
                <span>{a.body}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function KitRow({
  kit,
  copied,
  expanded,
  onToggleDetails,
  onCopy,
}: {
  kit: Kit;
  copied: boolean;
  expanded: boolean;
  onToggleDetails: () => void;
  onCopy: () => void;
}) {
  const toggleId = `kit-toggle-${kit.id}`;
  const regionId = `kit-summary-${kit.id}`;
  const summary = `${kit.title} details — ${kit.category}, ${kit.difficulty}, collection ${kit.collections.join(", ") || "—"}`;
  return (
    <div
      className={`kit-row${expanded ? " kit-row--open" : ""}`}
      data-kit-id={kit.id}
      data-safety-class={kit.safetyClass}
      aria-current={expanded ? "true" : undefined}
    >
      <KitMark mark={kit.mark} />
      <span>
        <strong>{kit.title}</strong>
        <small>{kit.useCase}</small>
      </span>
      <em>{kit.category}</em>
      <em>{kit.difficulty}</em>
      <em>{kit.collections[0] ?? "—"}</em>
      <button
        type="button"
        id={toggleId}
        className="kit-details"
        aria-expanded={expanded}
        aria-controls={regionId}
        onClick={onToggleDetails}
      >
        {expanded ? "Hide" : "Open"}
      </button>
      <button
        type="button"
        className={`kit-copy${copied ? " kit-copy--ok" : ""}`}
        onClick={onCopy}
        aria-label={`Copy prompt for ${kit.title}`}
        title="Copy the full canonical prompt body to your clipboard"
      >
        {copied ? "Copied" : "Copy"}
      </button>
      <div
        id={regionId}
        role="region"
        aria-labelledby={toggleId}
        hidden={!expanded}
        className="kit-row__summary"
      >
        <KitDetail kit={kit} onCopy={onCopy} copied={copied} />
        <p className="kit-row__summary-sr sr-only" aria-hidden="true">
          {summary}
        </p>
      </div>
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

function PilotUnavailable({ message }: { message: string }) {
  return (
    <Module title="Pilot unavailable" code="··" className="kits-empty">
      <div className="kits-state">
        <p className="kits-state__title">
          Canonical Prompt Pilot V1 records are not eligible.
        </p>
        <p className="kits-state__body">
          The Web V2 /prompt-kits surface cannot render until the
          canonical Batch 1 lock is satisfied on the prompt-content
          index. Run <code>npm run content:validate</code> from{" "}
          <code>web/</code> for the exact reason.
        </p>
        <pre className="kit-detail__prompt" aria-label="Failure detail">{message}</pre>
      </div>
    </Module>
  );
}

export default function PromptKits() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState<Category | "All">("All");
  const [copiedId, setCopiedId] = React.useState<string | null>(null);
  // Exactly one kit row may be expanded at a time.
  const [expandedId, setExpandedId] = React.useState<string | null>(null);
  // Polite live region announcement (e.g. "Copied: …").
  const [liveMessage, setLiveMessage] = React.useState<string>("");
  const [mobileExpanded, setMobileExpanded] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);

  // Compute the canonical Pilot V1 view-model once per render. The
  // selector throws when zero records are eligible; we catch and
  // surface a clear failure state instead of crashing the page.
  const loaded = React.useMemo<{ ok: true; kits: Kit[] } | { ok: false; error: string }>(() => {
    try {
      return { ok: true, kits: loadKits() };
    } catch (err) {
      if (
        err instanceof PromptKitsPilotV1UnavailableError &&
        typeof err.message === "string"
      ) {
        return { ok: false, error: err.message };
      }
      throw err;
    }
  }, []);

  const KITS: ReadonlyArray<Kit> = React.useMemo(
    () => (loaded.ok ? loaded.kits : []),
    [loaded],
  );
  const pilotError = loaded.ok ? null : loaded.error;

  const CATEGORIES: ReadonlyArray<{ id: Category | "All"; label: string; count: number }> =
    React.useMemo(() => {
      const all = KITS.length;
      const counts = (cat: Category) =>
        KITS.filter((k) => k.category === cat).length;
      return [
        { id: "All", label: "All", count: all },
        { id: "Build", label: "Build", count: counts("Build") },
        { id: "Research", label: "Research", count: counts("Research") },
        { id: "Decide", label: "Decide", count: counts("Decide") },
        { id: "Write", label: "Write", count: counts("Write") },
        { id: "Operate", label: "Operate", count: counts("Operate") },
      ];
    }, [KITS]);

  const toggleDetails = React.useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  // Close expanded state and clear stale Copied feedback when
  // filters, the manual reset, or the mobile disclosure change.
  React.useEffect(() => {
    setExpandedId(null);
    setCopiedId(null);
    setLiveMessage("");
  }, [query, category, mobileExpanded]);

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
  }, [KITS, query, category]);

  const featured = React.useMemo(
    () => filtered.slice(0, 4),
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
    [KITS, query],
  );

  const handleCopy = React.useCallback(async (kit: Kit) => {
    // The canonical prompt body is copied verbatim. No title prefix,
    // no use-case wrapping, no placeholder substitution.
    const text = kit.prompt;
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
      setLiveMessage(`Copied prompt: ${kit.title}`);
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
          lede="A focused library of prompt kits for engineers, builders, and operators. Searchable by category, with audience, difficulty, and collection for each entry."
          actions={[
            { primary: true, href: "#search", label: <>Search the kits <b>→</b></> },
            { href: "#featured", label: "Featured kits" },
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#search", label: "How to read this preview" }}
        />

        <StatusRail
          ariaLabel="Prompt kits preview status"
          items={[
            { icon: <i className="status-icon">ϟ</i>, label: "Index", detail: `${filtered.length} / ${KITS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Categories", detail: "5 groups" },
            { icon: <i className="status-icon">▱</i>, label: "Updated", detail: "Canonical pilot" },
            { icon: <i className="pulse" />, label: "Source", detail: "Approved prompt pilot" },
            { icon: <i className="status-icon">◷</i>, label: "Status", detail: "Pilot V1" },
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
                  placeholder="Try 'code review', 'incident', 'page skeleton'…"
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
              <p>Hand-picked canonical prompts with broad utility and clear reuse paths.</p>
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
          <p
            className="kits-live-region"
            role="status"
            aria-live="polite"
            aria-atomic="true"
          >
            {liveMessage}
          </p>
          {pilotError ? (
            <PilotUnavailable message={pilotError} />
          ) : compact.length === 0 ? (
            <EmptyState onClear={handleClearFilters} />
          ) : (
            <>
              <p className="kits-outbound-notice" role="note">
                Each kit is sourced from the canonical OpenRadar prompt-content pilot. The Copy button writes the exact canonical prompt body to your clipboard; placeholders are preserved. These prompts do not execute tools, send messages, or change production.
              </p>
              <Module title="Compact index" code="··" className="kits-results-module">
                <div className="kits-results" role="list">
                  {compactVisible.map((k) => (
                    <div role="listitem" key={k.id}>
                      <KitRow
                        kit={k}
                        copied={copiedId === k.id}
                        expanded={expandedId === k.id}
                        onToggleDetails={() => toggleDetails(k.id)}
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
                  <li><b>03</b><span>Verified destinations</span><time>Soon</time></li>
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
                  <li>Canonical pilot <i /></li>
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
          markSubtitle="A canonical pilot of vetted prompts. Copy-and-paste wording that does not execute tools or change production."
          meta={[
            { dt: "Surface", dd: "/prompt-kits" },
            { dt: "Audience", dd: "Engineers" },
            { dt: "Source", dd: "Canonical pilot V1" },
            { dt: "Static", dd: "Preview" },
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
            { kind: "link", value: "Home", href: "/" },
            { kind: "link", value: "Tools", href: "/tools" },
            { kind: "link", value: "System", href: "/system" },
            { kind: "small", value: "Canonical · pilot V1" },
          ]}
        />
      </Machine>
    </main>
  );
}
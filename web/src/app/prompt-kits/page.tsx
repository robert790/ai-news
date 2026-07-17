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
  PromptCategory,
  PromptDifficulty,
  PromptSafetyClass,
} from "@/content/prompts";

/**
 * OpenRadar /prompt-kits — practical reusable prompt kits.
 *
 * Pilot V1 wiring: the page reads its record set exclusively from the
 * canonical prompt-content pilot (`web/src/content/prompts/index.ts`)
 * via `selectPromptKitsPilotV1`. There is no duplicated prompt text
 * or static fallback dataset in this file.
 *
 * Eligibility is enforced inside the selector (five-field predicate).
 * The selector is exact-five fail-closed: it either returns all five
 * canonical records in canonical lock order, or it throws
 * `PromptKitsPilotV1UnavailableError`.
 *
 * If the selector throws, the page renders a product-safe failure
 * panel and never exposes the underlying diagnostic message,
 * missing ids, source paths, npm commands, or stack traces.
 *
 * Copy semantics: the Copy button writes the canonical `prompt`
 * body verbatim. No title prefix, no use-case wrapping, no
 * placeholder substitution.
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
  category: string;
  categoryId: PromptCategory;
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

const CATEGORY_LABEL: Record<string, string> = {
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
    category: CATEGORY_LABEL[rec.category] ?? rec.category,
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
 * Read the canonical catalog and select the Pilot V1 records. The
 * selector throws on any exact-five fail-closed failure; the page
 * catches and surfaces a product-safe failure panel.
 */
function loadKits(): Kit[] {
  const records = selectPromptKitsPilotV1(promptRecords);
  return records.map(toKit);
}

function KitMark({ mark }: { mark: string }) {
  return <span className="kit-mark">{mark}</span>;
}

function PilotKitCard({ kit }: { kit: Kit }) {
  return (
    <Module title={kit.title} code={kit.mark} className="kits-pilot-card">
      <div className="kits-pilot-card__body">
        <p className="kits-pilot-card__lede">{kit.useCase}</p>
        <ul className="kits-pilot-card__meta">
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
        {expanded && (
          <>
            <KitDetail kit={kit} onCopy={onCopy} copied={copied} />
            <p className="kit-row__summary-sr sr-only" aria-hidden="true">
              {summary}
            </p>
          </>
        )}
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
  id: string;
  label: string;
  count: number;
  active: boolean;
  onSelect: (id: string) => void;
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

/**
 * Product-safe failure panel. Shown when the canonical selector
 * cannot satisfy the exact-five fail-closed contract. The public
 * UI never sees the underlying diagnostic string.
 */
function PilotUnavailable() {
  return (
    <Module
      title="Prompt Kits are temporarily unavailable."
      code="··"
      className="kits-empty"
    >
      <div className="kits-state">
        <p className="kits-state__title">
          Prompt Kits are temporarily unavailable.
        </p>
        <p className="kits-state__body">
          The approved Pilot V1 catalog could not be loaded. Please try
          again later.
        </p>
      </div>
    </Module>
  );
}

export default function PromptKits() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState<string>("All");
  const [copiedId, setCopiedId] = React.useState<string | null>(null);
  // Exactly one kit row may be expanded at a time.
  const [expandedId, setExpandedId] = React.useState<string | null>(null);
  // Polite live region announcement (e.g. "Copied: …").
  const [liveMessage, setLiveMessage] = React.useState<string>("");

  // Compute the canonical Pilot V1 view-model once per render. The
  // selector throws when zero records are eligible; we catch and
  // surface a product-safe failure state instead of crashing the page.
  const loaded = React.useMemo<
    { ok: true; kits: Kit[] } | { ok: false }
  >(() => {
    try {
      return { ok: true, kits: loadKits() };
    } catch (err) {
      if (err instanceof PromptKitsPilotV1UnavailableError) {
        return { ok: false };
      }
      throw err;
    }
  }, []);

  const KITS: ReadonlyArray<Kit> = React.useMemo(
    () => (loaded.ok ? loaded.kits : []),
    [loaded],
  );
  const pilotUnavailable = !loaded.ok;

  /**
   * Build the category chip set from categories ACTUALLY PRESENT in
   * the selected five records. Zero-count categories are never shown.
   * Order: All, then categories by their first appearance in the
   * canonical five (Build, Write, Operate, Design for the V1 pilot).
   */
  const CATEGORIES: ReadonlyArray<{ id: string; label: string; count: number }> =
    React.useMemo(() => {
      const counts = new Map<string, number>();
      const firstSeen = new Map<string, number>();
      KITS.forEach((k, idx) => {
        counts.set(k.categoryId, (counts.get(k.categoryId) ?? 0) + 1);
        if (!firstSeen.has(k.categoryId)) {
          firstSeen.set(k.categoryId, idx);
        }
      });
      const present = [...counts.entries()]
        .filter(([, n]) => n > 0)
        .sort((a, b) => (firstSeen.get(a[0]) ?? 0) - (firstSeen.get(b[0]) ?? 0))
        .map(([id]) => id);
      return [
        { id: "All", label: "All", count: KITS.length },
        ...present.map((id) => ({
          id,
          label: CATEGORY_LABEL[id] ?? id,
          count: counts.get(id) ?? 0,
        })),
      ];
    }, [KITS]);

  /**
   * Human-readable summary of the categories currently surfaced on
   * the page. Used in the "All kits" subhead so the copy never claims
   * an absent group is present.
   */
  const categorySummary = React.useMemo(() => {
    const present = CATEGORIES.filter((c) => c.id !== "All").map(
      (c) => c.label.toLowerCase(),
    );
    if (present.length === 0) return "No categories available.";
    if (present.length === 1) return `Across ${present[0]}.`;
    if (present.length === 2) return `Across ${present[0]} and ${present[1]}.`;
    const head = present.slice(0, -1).join(", ");
    const tail = present[present.length - 1];
    return `Across ${head}, and ${tail}.`;
  }, [CATEGORIES]);

  const toggleDetails = React.useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  // Close expanded state and clear stale Copied feedback when
  // filters change. The selector is fixed-five on this page so
  // there is no mobile disclosure to collapse.
  React.useEffect(() => {
    setExpandedId(null);
    setCopiedId(null);
    setLiveMessage("");
  }, [query, category]);

  // Drop expandedId that points at a row no longer in the visible
  // (filtered) set, so the one-open-at-a-time invariant holds when
  // the user narrows by category or search.
  React.useEffect(() => {
    if (expandedId === null) return;
    const stillVisible = KITS.some(
      (k) =>
        k.id === expandedId &&
        (category === "All" || k.categoryId === category),
    );
    if (!stillVisible) setExpandedId(null);
  }, [KITS, category, query, expandedId]);

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return KITS.filter((k) => {
      const matchCat = category === "All" || k.categoryId === category;
      const matchQuery =
        q === "" ||
        k.title.toLowerCase().includes(q) ||
        k.useCase.toLowerCase().includes(q);
      return matchCat && matchQuery;
    });
  }, [KITS, query, category]);

  const countFor = React.useCallback(
    (id: string) => {
      const q = query.trim().toLowerCase();
      return KITS.filter((k) => {
        const matchCat = id === "All" || k.categoryId === id;
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

  const isDefaultState = query.trim() === "" && category === "All";

  const handleClearFilters = React.useCallback(() => {
    setQuery("");
    setCategory("All");
  }, []);

  // The visible summary-card grid is desktop/tablet only. At <=760px
  // the page hides it and uses the compact index as the single
  // primary five-prompt presentation.
  const showPilotGrid = isDefaultState && KITS.length > 0;

  // Total surfaced category groups (excluding the synthetic "All"
  // entry), used for the StatusRail. Falls back to 0 on pilot
  // unavailable so the rail does not overstate.
  const surfacedCategoryCount = pilotUnavailable
    ? 0
    : CATEGORIES.filter((c) => c.id !== "All").length;

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
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#search", label: "How to read this preview" }}
        />

        <StatusRail
          ariaLabel="Prompt kits preview status"
          items={[
            { icon: <i className="status-icon">ϟ</i>, label: "Index", detail: `${filtered.length} / ${KITS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Categories", detail: `${surfacedCategoryCount} ${surfacedCategoryCount === 1 ? "group" : "groups"}` },
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

        {showPilotGrid && (
          <section id="pilot" className="kits-pilot-section" aria-label="Pilot kits">
            <header className="kits-section__head">
              <h2>Pilot kits</h2>
              <p>All five approved Pilot V1 prompts in canonical order.</p>
            </header>
            <div className="kits-pilot-grid" role="list" aria-label="Pilot kits grid">
              {KITS.map((k) => (
                <div role="listitem" key={`pilot-${k.id}`}>
                  <PilotKitCard kit={k} />
                </div>
              ))}
            </div>
          </section>
        )}

        <section id="all" className="kits-results-section" aria-label="All kits">
          <header className="kits-section__head">
            <h2>
              All kits
              <span className="kits-section__count" aria-live="polite">
                {filtered.length} {filtered.length === 1 ? "entry" : "entries"}
              </span>
            </h2>
            <p>
              {isDefaultState
                ? categorySummary
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
          {pilotUnavailable ? (
            <PilotUnavailable />
          ) : filtered.length === 0 ? (
            <EmptyState onClear={handleClearFilters} />
          ) : (
            <>
              <p className="kits-outbound-notice" role="note">
                Each kit is sourced from the canonical OpenRadar prompt-content pilot. The Copy button writes the exact canonical prompt body to your clipboard; placeholders are preserved. These prompts do not execute tools, send messages, or change production.
              </p>
              <Module title="Compact index" code="··" className="kits-results-module">
                <div className="kits-results" role="list">
                  {filtered.map((k) => (
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
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
 * OpenRadar /tools — practical AI tool index.
 *
 * Internal + external-facing. Helps users discover useful AI tools
 * with practical utility. Static data only at this stage; no API
 * calls, no ingestion. Reuses the accepted chassis, tokens, and
 * component library.
 *
 * Client-side filter: search by name + use case, filter by category
 * chip. No API or database calls. Outbound "Visit" actions are
 * disabled "Preview" affordances at this stage — no real links.
 */

const TOOLS_NAV = [
  { label: "Home", href: "/" },
  { label: "Tools", href: "/tools", active: true },
  { label: "Prompt Kits", href: "/prompt-kits" },
  { label: "Learn", href: "/learn" },
  { label: "Jobs", href: "/jobs" },
];

type Category = "Research" | "Build" | "Decide" | "Operate";
type Pricing = "Free" | "Freemium" | "Paid";

type Tool = {
  id: string;
  mark: string;
  name: string;
  category: Category;
  useCase: string;
  pricing: Pricing;
  featured?: boolean;
};

const TOOLS: ReadonlyArray<Tool> = [
  {
    id: "perplexity-pro",
    mark: "PX",
    name: "Perplexity Pro",
    category: "Research",
    useCase: "Real-time research with cited sources",
    pricing: "Freemium",
    featured: true,
  },
  {
    id: "cursor",
    mark: "CR",
    name: "Cursor",
    category: "Build",
    useCase: "AI-first code editor for pair-programming",
    pricing: "Freemium",
    featured: true,
  },
  {
    id: "replit-agent",
    mark: "RP",
    name: "Replit Agent",
    category: "Build",
    useCase: "Ship apps from natural-language prompts",
    pricing: "Freemium",
    featured: true,
  },
  {
    id: "notebooklm",
    mark: "NB",
    name: "NotebookLM",
    category: "Research",
    useCase: "Source-grounded notebook for long docs",
    pricing: "Freemium",
    featured: true,
  },
  {
    id: "claude",
    mark: "CL",
    name: "Claude",
    category: "Decide",
    useCase: "Long-context reasoning and writing",
    pricing: "Freemium",
  },
  {
    id: "chatgpt",
    mark: "CG",
    name: "ChatGPT",
    category: "Decide",
    useCase: "General assistant and ideation partner",
    pricing: "Freemium",
  },
  {
    id: "gemini",
    mark: "GM",
    name: "Gemini",
    category: "Decide",
    useCase: "Multimodal assistant with Workspace hooks",
    pricing: "Freemium",
  },
  {
    id: "windsurf",
    mark: "WF",
    name: "Windsurf",
    category: "Build",
    useCase: "Agentic IDE with cascade flows",
    pricing: "Freemium",
  },
  {
    id: "v0",
    mark: "V0",
    name: "v0 by Vercel",
    category: "Build",
    useCase: "Generate UI from text and screenshots",
    pricing: "Freemium",
  },
  {
    id: "elevenlabs",
    mark: "EL",
    name: "ElevenLabs",
    category: "Operate",
    useCase: "Voice synthesis and dubbing",
    pricing: "Freemium",
  },
  {
    id: "runway",
    mark: "RW",
    name: "Runway",
    category: "Operate",
    useCase: "Video generation and editing",
    pricing: "Freemium",
  },
  {
    id: "zapier",
    mark: "ZP",
    name: "Zapier",
    category: "Operate",
    useCase: "Orchestrate AI workflows across apps",
    pricing: "Freemium",
  },
  {
    id: "make",
    mark: "MK",
    name: "Make",
    category: "Operate",
    useCase: "Visual automation with branching logic",
    pricing: "Freemium",
  },
  {
    id: "ollama",
    mark: "OL",
    name: "Ollama",
    category: "Build",
    useCase: "Run local LLMs on your own hardware",
    pricing: "Free",
  },
  {
    id: "huggingface",
    mark: "HF",
    name: "Hugging Face",
    category: "Research",
    useCase: "Open models, datasets, and Spaces",
    pricing: "Freemium",
  },
  {
    id: "kaggle",
    mark: "KG",
    name: "Kaggle",
    category: "Research",
    useCase: "Datasets, notebooks, and competitions",
    pricing: "Free",
  },
];

const CATEGORIES: ReadonlyArray<{ id: Category | "All"; label: string; count: number }> = [
  { id: "All", label: "All", count: TOOLS.length },
  { id: "Research", label: "Research", count: TOOLS.filter((t) => t.category === "Research").length },
  { id: "Build", label: "Build", count: TOOLS.filter((t) => t.category === "Build").length },
  { id: "Decide", label: "Decide", count: TOOLS.filter((t) => t.category === "Decide").length },
  { id: "Operate", label: "Operate", count: TOOLS.filter((t) => t.category === "Operate").length },
];

function ToolMark({ mark }: { mark: string }) {
  return <span className="tool-mark">{mark}</span>;
}

function ToolRow({ tool }: { tool: Tool }) {
  return (
    <div className="tool-row">
      <ToolMark mark={tool.mark} />
      <span>
        <strong>{tool.name}</strong>
        <small>{tool.useCase}</small>
      </span>
      <em>{tool.category}</em>
      <em aria-label={`Pricing: ${tool.pricing}`}>{tool.pricing}</em>
    </div>
  );
}

function FeaturedCard({ tool }: { tool: Tool }) {
  return (
    <Module title={tool.name} code={tool.mark} className="tools-feature">
      <div className="tools-feature__body">
        <p className="tools-feature__lede">{tool.useCase}</p>
        <div className="tool-row tool-row--inline">
          <span><small>Category</small><strong>{tool.category}</strong></span>
          <em aria-label={`Pricing: ${tool.pricing}`}>{tool.pricing}</em>
        </div>
      </div>
    </Module>
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
      className={`tools-chip ${active ? "tools-chip--active" : ""}`}
      aria-pressed={active}
      aria-label={`Filter by ${label} (${count} tools)`}
      onClick={() => onSelect(id)}
    >
      <span className="tools-chip__label">{label}</span>
      <span className="tools-chip__count" aria-hidden="true">{count}</span>
    </button>
  );
}

function EmptyState() {
  return (
    <Module title="No matches" code="00" className="tools-empty">
      <div className="tools-state">
        <p className="tools-state__title">Nothing in this signal yet</p>
        <p className="tools-state__body">
          Try a different category, broaden the search term, or browse the featured tools above.
        </p>
      </div>
    </Module>
  );
}

function LoadingState() {
  return (
    <Module title="Loading index" code="··" className="tools-loading">
      <div className="tools-state">
        <p className="tools-state__title">Index rebuild in progress</p>
        <p className="tools-state__body">
          Pulling the latest tools from the feed pipeline. This should clear in a few seconds.
        </p>
        <div className="tools-state__bar" aria-hidden="true"><i style={{ width: "62%" }} /></div>
      </div>
    </Module>
  );
}

export default function Tools() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState<Category | "All">("All");
  // Mobile-only disclosure: on small viewports, the full 16-row
  // index is excessively long, so we render the first 6 by default
  // and reveal the rest on demand. Desktop always shows everything.
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

  // Apply category + case-insensitive name/useCase substring filter.
  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return TOOLS.filter((t) => {
      const matchCat = category === "All" || t.category === category;
      const matchQuery =
        q === "" ||
        t.name.toLowerCase().includes(q) ||
        t.useCase.toLowerCase().includes(q);
      return matchCat && matchQuery;
    });
  }, [query, category]);

  const featured = React.useMemo(
    () => filtered.filter((t) => t.featured).slice(0, 4),
    [filtered],
  );
  const compact = filtered;
  // Mobile-only disclosure: when the filtered list has more than the
  // mobile limit, show only the first MOBILE_LIMIT rows by default
  // and reveal the rest on demand. Desktop always shows everything.
  const isMobileLimited = isMobile && compact.length > MOBILE_LIMIT;
  const isMobileCollapsed = isMobile && !mobileExpanded && isMobileLimited;
  const compactVisible = isMobileCollapsed ? compact.slice(0, MOBILE_LIMIT) : compact;
  const compactHiddenCount = isMobileLimited ? compact.length - MOBILE_LIMIT : 0;

  // Per-category visible counts (post-search, for the chip badges).
  const countFor = React.useCallback(
    (id: Category | "All") => {
      const q = query.trim().toLowerCase();
      return TOOLS.filter((t) => {
        const matchCat = id === "All" || t.category === id;
        const matchQuery =
          q === "" ||
          t.name.toLowerCase().includes(q) ||
          t.useCase.toLowerCase().includes(q);
        return matchCat && matchQuery;
      }).length;
    },
    [query],
  );

  return (
    <main className="page-shell" data-page="tools">
      <Machine ariaLabel="OpenRadar tools index">
        <TopDeck nav={TOOLS_NAV} />

        <HeroDeck
          kicker="Tools index"
          title={
            <>
              Find what works.
              <br />
              Skip what doesn&apos;t.
            </>
          }
          lede="A practical, vetted index of AI tools for engineers, builders, and operators. Searchable by category, with clear pricing signals."
          actions={[
            { primary: true, href: "#search", label: <>Search the index <b>→</b></> },
            { href: "#featured", label: "Featured tools" },
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#search", label: "How to read this preview" }}
        />

        <StatusRail
          ariaLabel="Tools preview status"
          items={[
            { icon: <i className="status-icon">ϟ</i>, label: "Index", detail: `${filtered.length} / ${TOOLS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Categories", detail: "4 groups" },
            { icon: <i className="status-icon">▱</i>, label: "Updated", detail: "Static preview" },
            { icon: <i className="pulse" />, label: "Source", detail: "Curated sample" },
            { icon: <i className="status-icon">◷</i>, label: "Status", detail: "Sample data" },
          ]}
        />

        <section id="search" className="tools-searchbar" aria-label="Search and filter">
          <Module title="Search the index" code="00" className="tools-search-module">
            <div className="tools-searchbar__inner">
              <label className="tools-searchbar__field">
                <span className="tools-searchbar__label">
                  Search tools
                  <span className="tools-searchbar__count" aria-live="polite">
                    {filtered.length} match{filtered.length === 1 ? "" : "es"}
                  </span>
                </span>
                <input
                  type="search"
                  name="q"
                  placeholder="Try 'code editor', 'voice', 'free'…"
                  aria-label="Search tools by name or use case"
                  autoComplete="off"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className="tools-searchbar__chips" role="group" aria-label="Filter by category">
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
                    className="tools-reset"
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

        {featured.length > 0 && (
          <section id="featured" className="tools-featured-section" aria-label="Featured tools">
            <header className="tools-section__head">
              <h2>Featured tools</h2>
              <p>Hand-picked tools with broad coverage and strong community signal.</p>
            </header>
            <div className="module-grid" aria-label="Featured tools grid">
              {featured.map((t) => <FeaturedCard key={t.id} tool={t} />)}
            </div>
          </section>
        )}

        <section id="all" className="tools-results-section" aria-label="All tools">
          <header className="tools-section__head">
            <h2>
              All tools
              <span className="tools-section__count" aria-live="polite">
                {compact.length} {compact.length === 1 ? "entry" : "entries"}
              </span>
            </h2>
            <p>
              {category === "All"
                ? "Across research, build, decide, and operate."
                : `Filtered to ${category.toLowerCase()}.`}
              {query.trim() && ` Matches "${query.trim()}".`}
            </p>
          </header>
          {compact.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              <p className="tools-outbound-notice" role="note">
                Outbound tool links are coming soon. This index lists
                verified tools with their category and pricing; full
                visit actions activate once destinations are wired.
              </p>
              <Module title="Compact index" code="··" className="tools-results-module">
                <div className="tools-results" role="list">
                  {compactVisible.map((t) => (
                    <div role="listitem" key={t.id}><ToolRow tool={t} /></div>
                  ))}
                </div>
                {isMobileLimited && compactHiddenCount > 0 && (
                  <div className="tools-disclosure">
                    <button
                      type="button"
                      className="tools-disclosure__btn"
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
                  <li><i />Practical daily utility</li>
                  <li><i />Stable ownership and funding</li>
                  <li><i />Real production traction</li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Coverage",
              headline: "What's next",
              body: (
                <ul>
                  <li><b>01</b><span>Prompt kits</span><time>Soon</time></li>
                  <li><b>02</b><span>Learn tracks</span><time>Soon</time></li>
                  <li><b>03</b><span>Verified destinations</span><time>Soon</time></li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Reliability",
              headline: "Always reachable",
              body: (
                <ul>
                  <li>Static <i /></li>
                  <li>Curated sample <i /></li>
                  <li>Sample links <i /></li>
                </ul>
              ),
            },
          ]}
        />

        <Footer
          markTitle={
            <>
              Tools index.
              <br />
              Practical AI, vetted.
            </>
          }
          markSubtitle="A static preview of the index. Sample tools with clear use cases."
          meta={[
            { dt: "Surface", dd: "/tools" },
            { dt: "Audience", dd: "Engineers" },
            { dt: "Source", dd: "Representative data" },
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
            { kind: "link", value: "System", href: "/system" },
            { kind: "small", value: "Static · no live content" },
          ]}
        />
      </Machine>
    </main>
  );
}

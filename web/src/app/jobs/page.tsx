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
 * OpenRadar /jobs — practical AI opportunities, sourced and
 * labeled by hand. Static data only; no APIs, no scraping, no
 * applications, no fake salary. Reuses the accepted chassis, tokens,
 * and component library. Mirrors the /learn / /prompt-kits pattern:
 * search + 3 filter groups, Featured jobs (default only), compact
 * index, mobile Show more/less, Details toggles inline summary,
 * EmptyState with Clear filters action.
 */

const JOBS_NAV = [
  { label: "Home", href: "/" },
  { label: "Tools", href: "/tools" },
  { label: "Prompt Kits", href: "/prompt-kits" },
  { label: "Learn", href: "/learn" },
  { label: "Jobs", href: "/jobs", active: true },
];

type Track = "Engineering" | "Product" | "Operations" | "Research" | "Creative";
type WorkMode = "Remote" | "Hybrid" | "On-site";
type Seniority = "Junior" | "Mid" | "Senior" | "Lead";
type Employment = "Full-time" | "Part-time" | "Contract" | "Internship";

type Job = {
  id: string;
  role: string;
  company: string;
  location: string;
  workMode: WorkMode;
  track: Track;
  seniority: Seniority;
  employment: Employment;
  skills: ReadonlyArray<string>;
  source: string;
  ageDays: number;
  salary?: string;
  summary: string;
  featured?: boolean;
};

const JOBS: ReadonlyArray<Job> = [
  {
    id: "applied-llm-eng",
    role: "Applied LLM engineer",
    company: "Northwind Labs",
    location: "Remote (EU)",
    workMode: "Remote",
    track: "Engineering",
    seniority: "Mid",
    employment: "Full-time",
    skills: ["TypeScript", "OpenAI API", "function calling", "evals"],
    source: "Direct",
    ageDays: 3,
    summary:
      "Wire LLM features into a small product surface. Build internal evals, ship behind a flag, write the prompt templates, and own the quality metrics. We are a small team; you will touch UI and infra.",
    featured: true,
  },
  {
    id: "platform-ai",
    role: "Platform engineer, AI infrastructure",
    company: "Atrium Cloud",
    location: "Berlin",
    workMode: "Hybrid",
    track: "Engineering",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["Kubernetes", "GPU scheduling", "vLLM", "Python"],
    source: "Direct",
    ageDays: 7,
    salary: "€110k–€140k",
    summary:
      "Own the inference platform used by 50+ internal teams. Reduce tail latency, design multi-region failover, and ship a self-serve model catalog. Expect a quarter of incident response.",
    featured: true,
  },
  {
    id: "product-mgr-ai",
    role: "Product manager, AI features",
    company: "Strata Health",
    location: "London",
    workMode: "Hybrid",
    track: "Product",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["PM", "evals", "discovery", "stakeholder work"],
    source: "Recruiter",
    ageDays: 12,
    summary:
      "Drive the AI roadmap for the clinician-facing product. Write PRDs that include failure modes and evaluation criteria. Run weekly review with the applied research team. Pair with design on the prompt disclosure pattern.",
  },
  {
    id: "ops-prompt-ops",
    role: "Prompt operations analyst",
    company: "Bluefin Insurance",
    location: "Remote (US)",
    workMode: "Remote",
    track: "Operations",
    seniority: "Mid",
    employment: "Full-time",
    skills: ["prompt QA", "knowledge ops", "SQL"],
    source: "Direct",
    ageDays: 5,
    summary:
      "Operate the production prompt catalog. Triage failures, write regression prompts, and own the weekly quality report. We need someone who treats prompts as code: versions, tests, and rollback plans.",
  },
  {
    id: "research-engineer",
    role: "Research engineer, evaluation",
    company: "Open Synthesis",
    location: "Remote (Global)",
    workMode: "Remote",
    track: "Research",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["PyTorch", "evals", "statistics"],
    source: "Direct",
    ageDays: 9,
    salary: "$180k–$220k",
    summary:
      "Build public evals for reasoning and tool use. Publish your work. You will work with academic labs and industry teams to design benchmarks that resist contamination.",
    featured: true,
  },
  {
    id: "junior-prompt-eng",
    role: "Junior prompt engineer",
    company: "Northwind Labs",
    location: "Remote (EU)",
    workMode: "Remote",
    track: "Engineering",
    seniority: "Junior",
    employment: "Full-time",
    skills: ["prompting", "TypeScript", "evals"],
    source: "Direct",
    ageDays: 2,
    summary:
      "An entry-level role for someone who has shipped a small AI tool, runs their own evals, and writes clearly. Pair with senior engineers for the first three months.",
  },
  {
    id: "designer-ai",
    role: "Designer, AI surfaces",
    company: "Field Studio",
    location: "New York",
    workMode: "Hybrid",
    track: "Creative",
    seniority: "Mid",
    employment: "Full-time",
    skills: ["Figma", "interaction design", "research"],
    source: "Direct",
    ageDays: 18,
    summary:
      "Design the human side of AI features: disclosure, recovery, feedback. Maintain a small library of patterns and write the case studies. Work with product and engineering from day one.",
  },
  {
    id: "contract-evals",
    role: "Evaluation engineer (contract)",
    company: "Vector City",
    location: "Remote (Global)",
    workMode: "Remote",
    track: "Engineering",
    seniority: "Mid",
    employment: "Contract",
    skills: ["evals", "Python", "data viz"],
    source: "Recruiter",
    ageDays: 6,
    summary:
      "Three-month engagement to harden the evals stack and ship a public dashboard. Strong preference for engineers who write clearly about their methodology.",
    salary: "$150/hour",
  },
  {
    id: "lead-ai-product",
    role: "Lead product manager, AI platform",
    company: "Compass Labs",
    location: "San Francisco",
    workMode: "On-site",
    track: "Product",
    seniority: "Lead",
    employment: "Full-time",
    skills: ["PM", "platform strategy", "evals"],
    source: "Direct",
    ageDays: 21,
    salary: "$220k–$280k + equity",
    summary:
      "Lead the next major iteration of our AI platform. Three direct reports, a roadmap review board, and a close partnership with research. You will be the public voice of our platform direction.",
  },
  {
    id: "data-labeling-lead",
    role: "Data labeling operations lead",
    company: "Marin Sourcing",
    location: "Remote (Americas)",
    workMode: "Remote",
    track: "Operations",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["ops", "QA", "vendor management"],
    source: "Direct",
    ageDays: 4,
    summary:
      "Run the human-rater partner network. Quality bar, throughput, and a fair-pay policy that we publish. You will own the operations playbook and the public quality report.",
  },
  {
    id: "interpretability-research",
    role: "Interpretability research scientist",
    company: "Glasswork AI",
    location: "Remote (US/UK)",
    workMode: "Remote",
    track: "Research",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["interpretability", "PyTorch", "publishing"],
    source: "Direct",
    ageDays: 11,
    salary: "$190k–$240k",
    summary:
      "Conduct applied interpretability work on production models. Publish peer-reviewed papers. Two days a week dedicated to your own research direction.",
  },
  {
    id: "creative-technologist",
    role: "Creative technologist",
    company: "Loom Atelier",
    location: "London",
    workMode: "Hybrid",
    track: "Creative",
    seniority: "Mid",
    employment: "Full-time",
    skills: ["creative coding", "generative", "studio work"],
    source: "Direct",
    ageDays: 14,
    summary:
      "Build interactive experiences for cultural and brand work. You will pair with designers and producers. We expect a portfolio of shipped interactive pieces.",
  },
  {
    id: "intern-research",
    role: "Research intern (summer)",
    company: "Open Synthesis",
    location: "Remote (Global)",
    workMode: "Remote",
    track: "Research",
    seniority: "Junior",
    employment: "Internship",
    skills: ["PyTorch", "research"],
    source: "Direct",
    ageDays: 8,
    summary:
      "Twelve-week internship running alongside the evaluation team. You will own one benchmark end-to-end and present a public report at the end.",
  },
  {
    id: "security-ai",
    role: "Security engineer, AI features",
    company: "Beacon",
    location: "Remote (Global)",
    workMode: "Remote",
    track: "Engineering",
    seniority: "Senior",
    employment: "Full-time",
    skills: ["security", "threat modeling", "AI policy"],
    source: "Direct",
    ageDays: 15,
    summary:
      "Threat-model our AI features. Build the abuse test suite. Be the public voice on our AI safety posture. We publish the model card and the red-team findings.",
    featured: true,
  },
  {
    id: "product-ops",
    role: "Product operations specialist",
    company: "Strata Health",
    location: "Remote (UK)",
    workMode: "Remote",
    track: "Operations",
    seniority: "Mid",
    employment: "Full-time",
    skills: ["PMO", "data", "stakeholder work"],
    source: "Recruiter",
    ageDays: 19,
    summary:
      "Run the rhythm of the product org. Quarterly reviews, weekly metrics, cross-team alignment. Strong preference for someone who has shipped a product ops playbook.",
  },
  {
    id: "community-ai",
    role: "Community manager, AI",
    company: "Beacon",
    location: "Remote (Global)",
    workMode: "Remote",
    track: "Creative",
    seniority: "Mid",
    employment: "Part-time",
    skills: ["community", "writing", "events"],
    source: "Direct",
    ageDays: 22,
    summary:
      "Run the developer community. Weekly office hours, monthly newsletter, an in-person gathering once a year. You will write most public words for the company.",
  },
  {
    id: "junior-research-eng",
    role: "Junior research engineer",
    company: "Glasswork AI",
    location: "Remote (US)",
    workMode: "Remote",
    track: "Research",
    seniority: "Junior",
    employment: "Full-time",
    skills: ["PyTorch", "Python"],
    source: "Direct",
    ageDays: 1,
    summary:
      "Entry-level research engineer to support the interpretability team. You will run evals, write technical reports, and grow into a research direction of your own.",
  },
  {
    id: "lead-platform",
    role: "Lead platform engineer",
    company: "Atrium Cloud",
    location: "Berlin",
    workMode: "Hybrid",
    track: "Engineering",
    seniority: "Lead",
    employment: "Full-time",
    skills: ["Kubernetes", "GPU", "people management"],
    source: "Direct",
    ageDays: 27,
    salary: "€140k–€170k",
    summary:
      "Lead the AI infrastructure platform team (5 engineers). Set the technical direction, own the QBR plan, and partner with research on capacity planning.",
  },
];

const TRACKS: ReadonlyArray<Track> = ["Engineering", "Product", "Operations", "Research", "Creative"];
const WORK_MODES: ReadonlyArray<WorkMode> = ["Remote", "Hybrid", "On-site"];
const SENIORITIES: ReadonlyArray<Seniority> = ["Junior", "Mid", "Senior", "Lead"];

function ageLabel(days: number): string {
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

function FeaturedJobCard({ job }: { job: Job }) {
  return (
    <Module title={job.role} code={job.id.slice(0, 2).toUpperCase()} className="jobs-feature">
      <div className="jobs-feature__body">
        <p className="jobs-feature__lede">{job.company} — {job.location}</p>
        <ul className="jobs-feature__meta">
          <li><span>Track</span><strong>{job.track}</strong></li>
          <li><span>Mode</span><strong>{job.workMode}</strong></li>
          <li><span>Level</span><strong>{job.seniority}</strong></li>
          <li><span>Posted</span><strong>{ageLabel(job.ageDays)}</strong></li>
        </ul>
        {job.salary && (
          <p className="jobs-feature__salary">{job.salary}</p>
        )}
      </div>
    </Module>
  );
}

function JobRow({
  job,
  expanded,
  onToggleDetails,
}: {
  job: Job;
  expanded: boolean;
  onToggleDetails: () => void;
}) {
  return (
    <article className={`job-row ${expanded ? "job-row--open" : ""}`}>
      <header className="job-row__head">
        <span className="job-mark">{job.id.slice(0, 2).toUpperCase()}</span>
        <span>
          <strong>{job.role}</strong>
          <small>{job.company} — {job.location} — {job.workMode}</small>
        </span>
        <span className="job-row__meta">
          <em>{job.track}</em>
          <em>{job.workMode}</em>
          <em>{job.seniority}</em>
          <em aria-label={`Posted ${ageLabel(job.ageDays)}`}>{ageLabel(job.ageDays)}</em>
          <em>{job.employment}</em>
        </span>
        <span className="job-row__actions">
          <button
            type="button"
            className="job-details"
            aria-expanded={expanded}
            aria-controls={`job-summary-${job.id}`}
            onClick={onToggleDetails}
          >
            {expanded ? "Hide" : "Details"}
          </button>
          <a
            className="job-view"
            href="#"
            aria-disabled="true"
            tabIndex={-1}
            onClick={(e) => e.preventDefault()}
            title="External destination coming soon"
          >
            View role
          </a>
        </span>
      </header>
      {expanded && (
        <div id={`job-summary-${job.id}`} className="job-row__summary" role="region">
          <p className="job-row__summary-text">{job.summary}</p>
          <ul className="job-row__skills" aria-label="Key skills">
            {job.skills.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
          <dl className="job-row__facts">
            <div><dt>Source</dt><dd>{job.source}</dd></div>
            <div><dt>Type</dt><dd>{job.employment}</dd></div>
            {job.salary && (
              <div><dt>Salary</dt><dd>{job.salary}</dd></div>
            )}
          </dl>
        </div>
      )}
    </article>
  );
}

function EmptyState({ onClear }: { onClear: () => void }) {
  return (
    <Module title="No matches" code="00" className="jobs-empty">
      <div className="jobs-state">
        <p className="jobs-state__title">No jobs match this signal.</p>
        <p className="jobs-state__body">
          Clear the active filters or try a broader term.
        </p>
        <button
          type="button"
          className="jobs-state__clear"
          onClick={onClear}
        >
          Clear filters
        </button>
      </div>
    </Module>
  );
}

type Filter = "All" | Track;

export default function Jobs() {
  const [query, setQuery] = React.useState("");
  const [track, setTrack] = React.useState<Filter>("All");
  const [workMode, setWorkMode] = React.useState<WorkMode | "All">("All");
  const [seniority, setSeniority] = React.useState<Seniority | "All">("All");
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
    query.trim() === "" &&
    track === "All" &&
    workMode === "All" &&
    seniority === "All";

  React.useEffect(() => {
    setMobileExpanded(false);
    setExpandedId(null);
  }, [query, track, workMode, seniority]);

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return JOBS.filter((j) => {
      const matchTrack = track === "All" || j.track === track;
      const matchMode = workMode === "All" || j.workMode === workMode;
      const matchSenior = seniority === "All" || j.seniority === seniority;
      const matchQuery =
        q === "" ||
        j.role.toLowerCase().includes(q) ||
        j.company.toLowerCase().includes(q) ||
        j.skills.some((s) => s.toLowerCase().includes(q));
      return matchTrack && matchMode && matchSenior && matchQuery;
    });
  }, [query, track, workMode, seniority]);

  const featured = React.useMemo(
    () => filtered.filter((j) => j.featured).slice(0, 4),
    [filtered],
  );

  const compact = filtered;
  const isMobileLimited = isMobile && compact.length > MOBILE_LIMIT;
  const isMobileCollapsed = isMobile && !mobileExpanded && isMobileLimited;
  const compactVisible = isMobileCollapsed ? compact.slice(0, MOBILE_LIMIT) : compact;
  const compactHiddenCount = isMobileLimited ? compact.length - MOBILE_LIMIT : 0;

  const trackCountFor = React.useCallback(
    (t: Filter) => {
      const q = query.trim().toLowerCase();
      const wm = workMode;
      const sr = seniority;
      return JOBS.filter((j) => {
        const matchTrack = t === "All" || j.track === t;
        const matchMode = wm === "All" || j.workMode === wm;
        const matchSenior = sr === "All" || j.seniority === sr;
        const matchQuery =
          q === "" ||
          j.role.toLowerCase().includes(q) ||
          j.company.toLowerCase().includes(q) ||
          j.skills.some((s) => s.toLowerCase().includes(q));
        return matchTrack && matchMode && matchSenior && matchQuery;
      }).length;
    },
    [query, workMode, seniority],
  );

  const workModeCountFor = React.useCallback(
    (wm: WorkMode | "All") => {
      const q = query.trim().toLowerCase();
      const t = track;
      const sr = seniority;
      return JOBS.filter((j) => {
        const matchTrack = t === "All" || j.track === t;
        const matchMode = wm === "All" || j.workMode === wm;
        const matchSenior = sr === "All" || j.seniority === sr;
        const matchQuery =
          q === "" ||
          j.role.toLowerCase().includes(q) ||
          j.company.toLowerCase().includes(q) ||
          j.skills.some((s) => s.toLowerCase().includes(q));
        return matchTrack && matchMode && matchSenior && matchQuery;
      }).length;
    },
    [query, track, seniority],
  );

  const seniorityCountFor = React.useCallback(
    (sr: Seniority | "All") => {
      const q = query.trim().toLowerCase();
      const t = track;
      const wm = workMode;
      return JOBS.filter((j) => {
        const matchTrack = t === "All" || j.track === t;
        const matchMode = wm === "All" || j.workMode === wm;
        const matchSenior = sr === "All" || j.seniority === sr;
        const matchQuery =
          q === "" ||
          j.role.toLowerCase().includes(q) ||
          j.company.toLowerCase().includes(q) ||
          j.skills.some((s) => s.toLowerCase().includes(q));
        return matchTrack && matchMode && matchSenior && matchQuery;
      }).length;
    },
    [query, track, workMode],
  );

  const handleClearFilters = React.useCallback(() => {
    setQuery("");
    setTrack("All");
    setWorkMode("All");
    setSeniority("All");
    setMobileExpanded(false);
    setExpandedId(null);
  }, []);

  return (
    <main className="page-shell" data-page="jobs">
      <Machine ariaLabel="OpenRadar jobs index">
        <TopDeck nav={JOBS_NAV} />

        <HeroDeck
          kicker="Jobs"
          title={
            <>
              Practical AI roles,
              <br />
              sourced and labeled.
            </>
          }
          lede="A focused index of AI opportunities — engineering, product, operations, research, creative. Sourced by hand. Filtered by track, work mode, and seniority."
          actions={[
            { primary: true, href: "#search", label: <>Search jobs <b>→</b></> },
            { href: "#featured", label: "Featured opportunities" },
            { href: "#all", label: "Browse all" },
          ]}
          overview={{ href: "#legend", label: "How to read these listings" }}
        />

        <StatusRail
          ariaLabel="Jobs status"
          items={[
            { icon: <i className="status-icon">▤</i>, label: "Listings", detail: `${filtered.length} / ${JOBS.length}` },
            { icon: <i className="status-icon">⌘</i>, label: "Tracks", detail: `${TRACKS.length}` },
            { icon: <i className="status-icon">⊟</i>, label: "Sources", detail: "Direct · Recruiter" },
            { icon: <i className="pulse" />, label: "Status", detail: "Static" },
            { icon: <i className="status-icon">◷</i>, label: "Updated", detail: "Weekly" },
          ]}
        />

        <section id="search" className="jobs-searchbar" aria-label="Search and filter jobs">
          <Module title="Search jobs" code="00" className="jobs-search-module">
            <div className="jobs-searchbar__inner">
              <label className="jobs-searchbar__field">
                <span className="jobs-searchbar__label">
                  Search jobs
                  <span className="jobs-searchbar__count" aria-live="polite">
                    {filtered.length} match{filtered.length === 1 ? "" : "es"}
                  </span>
                </span>
                <input
                  type="search"
                  name="q"
                  placeholder="Try 'evals', 'remote', 'Northwind'…"
                  aria-label="Search jobs by role, company, or skill"
                  autoComplete="off"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className="jobs-searchbar__chips" role="group" aria-label="Filter by track">
                {TRACKS.map((t) => (
                  <button
                    key={t}
                    type="button"
                    className={`jobs-chip ${track === t ? "jobs-chip--active" : ""}`}
                    aria-pressed={track === t}
                    aria-label={`Filter by track ${t} (${trackCountFor(t)} jobs)`}
                    onClick={() => setTrack(track === t ? "All" : t)}
                  >
                    <span className="jobs-chip__label">{t}</span>
                    <span className="jobs-chip__count" aria-hidden="true">{trackCountFor(t)}</span>
                  </button>
                ))}
              </div>
              <div className="jobs-searchbar__chips" role="group" aria-label="Filter by work mode">
                {WORK_MODES.map((wm) => (
                  <button
                    key={wm}
                    type="button"
                    className={`jobs-chip ${workMode === wm ? "jobs-chip--active" : ""}`}
                    aria-pressed={workMode === wm}
                    aria-label={`Filter by work mode ${wm} (${workModeCountFor(wm)} jobs)`}
                    onClick={() => setWorkMode(workMode === wm ? "All" : wm)}
                  >
                    <span className="jobs-chip__label">{wm}</span>
                    <span className="jobs-chip__count" aria-hidden="true">{workModeCountFor(wm)}</span>
                  </button>
                ))}
              </div>
              <div className="jobs-searchbar__chips" role="group" aria-label="Filter by seniority">
                {SENIORITIES.map((sr) => (
                  <button
                    key={sr}
                    type="button"
                    className={`jobs-chip ${seniority === sr ? "jobs-chip--active" : ""}`}
                    aria-pressed={seniority === sr}
                    aria-label={`Filter by seniority ${sr} (${seniorityCountFor(sr)} jobs)`}
                    onClick={() => setSeniority(seniority === sr ? "All" : sr)}
                  >
                    <span className="jobs-chip__label">{sr}</span>
                    <span className="jobs-chip__count" aria-hidden="true">{seniorityCountFor(sr)}</span>
                  </button>
                ))}
                {(query || track !== "All" || workMode !== "All" || seniority !== "All") && (
                  <button
                    type="button"
                    className="jobs-reset"
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
          <section id="featured" className="jobs-featured-section" aria-label="Featured jobs">
            <header className="jobs-section__head">
              <h2>Featured opportunities</h2>
              <p>Hand-picked roles across engineering, product, research, and creative.</p>
            </header>
            <div className="module-grid" aria-label="Featured jobs grid">
              {featured.map((j) => (
                <FeaturedJobCard key={j.id} job={j} />
              ))}
            </div>
          </section>
        )}

        <section id="all" className="jobs-results-section" aria-label="All jobs">
          <header className="jobs-section__head">
            <h2>
              All listings
              <span className="jobs-section__count" aria-live="polite">
                {compact.length} {compact.length === 1 ? "entry" : "entries"}
              </span>
            </h2>
            <p>
              {track === "All" && workMode === "All" && seniority === "All"
                ? "Across all tracks, modes, and seniorities."
                : `Filtered to ${track !== "All" ? track.toLowerCase() : "any track"}, ${workMode !== "All" ? workMode.toLowerCase() : "any mode"}, ${seniority !== "All" ? seniority.toLowerCase() : "any seniority"}.`}
              {query.trim() && ` Matches "${query.trim()}".`}
            </p>
          </header>
          {compact.length === 0 ? (
            <EmptyState onClear={handleClearFilters} />
          ) : (
            <>
              <p className="jobs-outbound-notice" role="note">
                Details opens an inline summary with role context and key skills. View role links remain disabled until the outbound destinations are wired — we never send you somewhere we have not verified.
              </p>
              <Module title="Compact index" code="··" className="jobs-results-module">
                <div className="jobs-results" role="list">
                  {compactVisible.map((job) => (
                    <div role="listitem" key={job.id}>
                      <JobRow
                        job={job}
                        expanded={expandedId === job.id}
                        onToggleDetails={() =>
                          setExpandedId((current) =>
                            current === job.id ? null : job.id,
                          )
                        }
                      />
                    </div>
                  ))}
                </div>
                {isMobileLimited && compactHiddenCount > 0 && (
                  <div className="jobs-disclosure">
                    <button
                      type="button"
                      className="jobs-disclosure__btn"
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
                  <li><i />Sourced from public posts or direct contact</li>
                  <li><i />Labeled by track, mode, seniority</li>
                  <li><i />Salary only when explicitly listed</li>
                </ul>
              ),
            },
            {
              className: "updates-panel",
              label: "Coverage",
              headline: "What's next",
              body: (
                <ul>
                  <li><b>01</b><span>Verified jobs</span><time>Soon</time></li>
                  <li><b>02</b><span>External destinations</span><time>Soon</time></li>
                  <li><b>03</b><span>Saved searches</span><time>Soon</time></li>
                </ul>
              ),
            },
            {
              className: "health-panel",
              label: "Reliability",
              headline: "Stays honest",
              body: (
                <ul>
                  <li>Reviewed weekly <i /></li>
                  <li>No fake salaries <i /></li>
                  <li>Static indexes <i /></li>
                </ul>
              ),
            },
          ]}
        />

        <Footer
          markTitle={
            <>
              Jobs.
              <br />
              Practical roles.
            </>
          }
          markSubtitle="A focused index of AI opportunities — sourced, labeled, and reviewed weekly."
          meta={[
            { dt: "Surface", dd: "/jobs" },
            { dt: "Audience", dd: "All levels" },
            { dt: "Source", dd: "Sol baseline" },
            { dt: "Static", dd: "Internal" },
          ]}
          subscribe={{
            label: "Jobs digest",
            sublabel: "Weekly curated roles — internal changelog only.",
            placeholder: "designer@team",
            buttonLabel: "Subscribe",
          }}
          legal={[
            { kind: "text", value: "© 2026 OpenRadar" },
            { kind: "status", value: "Jobs" },
            { kind: "link", value: "Home", href: "/" },
            { kind: "link", value: "Tools", href: "/tools" },
            { kind: "link", value: "Learn", href: "/learn" },
            { kind: "link", value: "System", href: "/system" },
            { kind: "small", value: "Static · internal" },
          ]}
        />
      </Machine>
    </main>
  );
}
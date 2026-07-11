/**
 * Stage 0–4 chassis-rebuild spike v5 — Sol gate corrections applied.
 */

// Precomputed radar geometry (module-scope, evaluated once at module load)
const RINGS = [20, 40, 60, 80, 96].map((r, i) => ({
  r,
  op: 0.15 + i * 0.06,
}));
const CARDINALS = [0, 90, 180, 270].map((deg) => {
  const r = (deg * Math.PI) / 180;
  return {
    x1: 100 + 92 * Math.cos(r),
    y1: 100 + 92 * Math.sin(r),
    x2: 100 + 100 * Math.cos(r),
    y2: 100 + 100 * Math.sin(r),
  };
});
const MINORS = [30, 60, 120, 150, 210, 240, 300, 330].map((deg) => {
  const r = (deg * Math.PI) / 180;
  return {
    x1: 100 + 94 * Math.cos(r),
    y1: 100 + 94 * Math.sin(r),
    x2: 100 + 100 * Math.cos(r),
    y2: 100 + 100 * Math.sin(r),
  };
});
const BLIPS = [
  { a: 25, r: 65 }, { a: 70, r: 40 }, { a: 110, r: 70 },
  { a: 165, r: 50 }, { a: 220, r: 75 }, { a: 290, r: 45 },
  { a: 340, r: 60 },
].map((b) => {
  const r = (b.a * Math.PI) / 180;
  return {
    x: 100 + b.r * Math.cos(r),
    y: 100 + b.r * Math.sin(r),
  };
});

function RadarSvg({ idSuffix = "" }: { idSuffix?: string }) {
  return (
    <svg viewBox="0 0 200 200" aria-hidden="true">
      <defs>
        <radialGradient id={`bg${idSuffix}`} cx="50%" cy="50%" r="55%">
          <stop offset="0%" stopColor="rgba(140,180,195,0.04)" />
          <stop offset="80%" stopColor="rgba(0,0,0,0)" />
        </radialGradient>
        <linearGradient id={`sweep${idSuffix}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="rgba(143,224,122,0)" />
          <stop offset="85%" stopColor="rgba(143,224,122,0)" />
          <stop offset="100%" stopColor="rgba(143,224,122,0.55)" />
        </linearGradient>
        <mask id={`sweepMask${idSuffix}`}>
          <rect width="200" height="200" fill="black" />
          <g style={{ transformOrigin: "100px 100px" }}>
            <path d="M100 100 L 196 100 A 96 96 0 0 1 192 116 Z" fill="white" />
          </g>
        </mask>
      </defs>
      <circle cx="100" cy="100" r="96" fill={`url(#bg${idSuffix})`} />
      {RINGS.map(({ r, op }) => (
        <circle key={r} cx="100" cy="100" r={r} fill="none"
          stroke="rgba(143,224,122,0.45)" strokeOpacity={op} strokeWidth="0.4" />
      ))}
      <line x1="4" y1="100" x2="196" y2="100" stroke="rgba(143,224,122,0.12)" strokeWidth="0.4" />
      <line x1="100" y1="4" x2="100" y2="196" stroke="rgba(143,224,122,0.12)" strokeWidth="0.4" />
      {CARDINALS.map((c, i) => (
        <line key={i} x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2}
          stroke="rgba(143,224,122,0.5)" strokeWidth="0.7" />
      ))}
      <circle cx="100" cy="100" r="100" fill={`url(#sweep${idSuffix})`} mask={`url(#sweepMask${idSuffix})`}
        style={{ transformOrigin: "100px 100px", animation: "ort-sweep 4s linear infinite" }} />
      {BLIPS.map((b, i) => (
        <circle key={i} cx={b.x} cy={b.y} r="1.4" fill="#8fe07a" />
      ))}
      <circle cx="100" cy="100" r="3" fill="#3a444d" />
      <circle cx="100" cy="100" r="1.2" fill="#030405" />
    </svg>
  );
}

// Module data — each module has differentiated internals
const FEATURED = [
  { name: "Perplexity Pro",  meta: "Research · 9.6" },
  { name: "Cursor",          meta: "Dev · 12.4" },
  { name: "Replit Agent",    meta: "Build · 8.1" },
  { name: "Data Interpreter",meta: "Analytics · 7.8" },
];

const KITS_TAGS = ["BUILD", "DECIDE", "RESEARCH", "WRITE", "AUDIT", "PLAN"];

const LEARN_PROG = [
  { name: "AI Foundations",     done: 4, total: 10 },
  { name: "Prompt Engineering", done: 0, total: 8 },
  { name: "Tool Triage",        done: 0, total: 6 },
];

const JOBS_LAMP: { name: string; state: "ok" | "warn" | "err" | "idle"; label: string }[] = [
  { name: "AI Engineer",    state: "ok",   label: "OPERATIONAL" },
  { name: "ML Ops Engineer",state: "ok",   label: "OPERATIONAL" },
  { name: "Prompt Engineer",state: "warn", label: "WATCH" },
  { name: "Data Scientist", state: "ok",   label: "OPERATIONAL" },
];

const SIGNALS_LINE = [3, 5, 4, 6, 7, 6, 8, 9, 11, 10, 12, 14];
const UPDATES_LINE = [1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1];
const COMMUNITY_LINE = [6, 7, 7, 8, 8, 9, 9, 9, 10, 10, 11, 11];
const HEALTH_LINE = [5, 5, 5, 6, 7, 8, 9, 10, 10, 11, 11, 11];

// Dashboard compact line-instrument data
const DASH_LINES = [
  { label: "API p50",    val: "42ms",  line: [3, 5, 4, 6, 7, 6, 8, 9, 11, 10, 12, 14] },
  { label: "Errors 24h", val: "00",    line: [1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1] },
  { label: "Caches",     val: "Warm",  line: [6, 7, 7, 8, 8, 9, 9, 9, 10, 10, 11, 11] },
  { label: "Sources",    val: "11/11", line: [5, 5, 5, 6, 7, 8, 9, 10, 10, 11, 11, 11] },
  { label: "Build",      val: "v1.4.0",line: [1, 2, 2, 3, 4, 5, 6, 7, 7, 8, 8, 9] },
];

// Sparkline / line-instrument renderer — compact green line over 12 points
function MiniLine({ values, suffix = "" }: { values: number[]; suffix?: string }) {
  const max = Math.max(...values);
  const w = 80;
  const h = 22;
  const step = w / (values.length - 1);
  const points = values
    .map((v, i) => `${i * step},${h - (v / max) * (h - 2) - 1}`)
    .join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true">
      <polyline
        fill="none"
        stroke="#8fe07a"
        strokeOpacity="0.85"
        strokeWidth="1.2"
        strokeLinejoin="round"
        strokeLinecap="round"
        points={points + ` ${suffix}`}
      />
    </svg>
  );
}

export default function Page() {
  return (
    <>
      {/* ===== DESKTOP (≥981px) ===== */}
      <main className="chassis-mount">
        <div className="chassis" role="region" aria-label="Open Radar operational console">

          <span className="handle handle--l" aria-hidden="true" />
          <span className="handle handle--r" aria-hidden="true" />

          {/* 1. Header — 7% */}
          <header className="hdr">
            <div className="brand">
              <span className="brand__crest" aria-hidden="true">
                <svg viewBox="0 0 18 18">
                  <circle cx="9" cy="9" r="6.5" fill="none" stroke="#3a444d" strokeWidth="0.9" />
                  <circle cx="9" cy="9" r="3" fill="none" stroke="#3a444d" strokeWidth="0.6" />
                  <line x1="9" y1="9" x2="13.5" y2="4.5" stroke="#8fe07a" strokeWidth="0.9" />
                  <circle cx="9" cy="9" r="0.9" fill="#8fe07a" />
                </svg>
              </span>
              <span className="brand__name">OPEN · RADAR</span>
            </div>

            <nav className="nav" aria-label="Sections">
              <button className="nav__item" aria-current="true">Home</button>
              <button className="nav__item">Tools</button>
              <button className="nav__item">Kits</button>
              <button className="nav__item">Learn</button>
              <button className="nav__item">Jobs</button>
              <button className="nav__item">Signals</button>
            </nav>

            <div className="util">
              <span className="util__led" aria-hidden="true" />
              <span className="util__txt"><strong>OR-7A</strong></span>
              <span className="util__txt"><strong>Online</strong></span>
              <span className="util__txt">v1.4.0</span>
              <span className="knob" aria-hidden="true" />
            </div>
          </header>

          {/* 2. Primary instrument bay — 18% */}
          <section className="bay" aria-label="Operational console">
            <div className="hero">
              <span className="hero__eyebrow"><strong>Online</strong> · Operational console</span>
              <h1 className="hero__title">
                Practical AI tools &amp; prompts. Curated, ranked, ready to run.
              </h1>
              <p className="hero__lede">
                Engineering-oriented directory of AI tools, prompt kits,
                learning paths, and jobs — tracked daily.
              </p>
              <div className="hero__controls">
                <button className="btn btn--primary">Explore Tools</button>
                <button className="btn">Today&apos;s Picks</button>
                <button className="btn">Browse Kits</button>
              </div>
            </div>

            <div className="radar" aria-label="Radar instrument">
              {/* Left side readouts */}
              <div className="radar-readouts" aria-label="Radar telemetry left">
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Rng</span>
                  <span className="radar-readouts__value"><strong>200</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Brg</span>
                  <span className="radar-readouts__value"><strong>045°</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Swp</span>
                  <span className="radar-readouts__value"><strong>4.0s</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Chn</span>
                  <span className="radar-readouts__value"><strong>A</strong></span>
                </div>
              </div>

              <div className="radar__frame">
                <span className="f f--tl" aria-hidden="true" />
                <span className="f f--tr" aria-hidden="true" />
                <span className="f f--bl" aria-hidden="true" />
                <span className="f f--br" aria-hidden="true" />
                <div className="radar__glass">
                  <RadarSvg idSuffix="1" />
                </div>
              </div>

              {/* Right side readouts */}
              <div className="radar-readouts radar-readouts--r" aria-label="Radar telemetry right">
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Prf</span>
                  <span className="radar-readouts__value"><strong>+7</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">P50</span>
                  <span className="radar-readouts__value"><strong>42ms</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Nod</span>
                  <span className="radar-readouts__value"><strong>OR-7A</strong></span>
                </div>
                <div className="radar-readouts__cell">
                  <span className="radar-readouts__label">Upd</span>
                  <span className="radar-readouts__value"><strong>2m</strong></span>
                </div>
              </div>
            </div>
          </section>

          {/* 3. Primary telemetry — 4% */}
          <section className="tele" aria-label="Telemetry">
            <div className="tele__cell">
              <span className="tele__label">Signals</span>
              <span className="tele__value"><strong>4</strong></span>
            </div>
            <div className="tele__cell">
              <span className="tele__label">Tools</span>
              <span className="tele__value"><strong>128</strong></span>
            </div>
            <div className="tele__cell">
              <span className="tele__label">Jobs</span>
              <span className="tele__value"><strong>37</strong></span>
            </div>
            <div className="tele__cell">
              <span className="tele__label">Status</span>
              <span className="tele__value"><strong>Nominal</strong></span>
            </div>
            <div className="tele__cell">
              <span className="tele__label">Update</span>
              <span className="tele__value"><strong>2m</strong></span>
            </div>
          </section>

          {/* 4. Operational module grid — 22% (compressed), differentiated internals */}
          <section className="grid" aria-label="Operational modules">
            <Mod
              title="Featured Tools"
              template="list"
              rows={FEATURED}
              more="View all"
            />
            <Mod
              title="Prompt Kits"
              template="tags"
              tags={KITS_TAGS}
              more="View all"
            />
            <Mod
              title="Learn Paths"
              template="progress"
              progress={LEARN_PROG}
              more="View all"
            />
            <Mod
              title="Jobs"
              template="lamp"
              lamps={JOBS_LAMP}
              more="View all"
            />
            <Mod
              title="Signals"
              template="spark"
              values={SIGNALS_LINE}
              more="View all"
            />
            <Mod
              title="Updates"
              template="spark"
              values={UPDATES_LINE}
              more="View all"
            />
            <Mod
              title="Community"
              template="spark"
              values={COMMUNITY_LINE}
              more="View all"
            />
            <Mod
              title="System Health"
              template="spark"
              values={HEALTH_LINE}
              more="View all"
            />
          </section>

          {/* 5. Command dashboard — 11%, ONE shared chassis, compact line instruments */}
          <section className="dash" aria-label="Command dashboard">
            {DASH_LINES.map((d) => (
              <div key={d.label} className="dash__cell">
                <div className="dash__head">
                  <span className="dash__label">{d.label}</span>
                  <span className="dash__val">{d.val}</span>
                </div>
                <div className="dash__line">
                  <MiniLine values={d.line} />
                </div>
              </div>
            ))}
          </section>

          {/* 6. System / footer assembly — 13% */}
          <section className="foot" aria-label="System footer">
            <div className="foot__cell">
              <div className="foot__title">Engineering intent</div>
              <p className="foot__copy">
                Built for engineers who ship. No hype, no spam — only the
                tools, prompts, paths, and roles that actually work.
              </p>
            </div>
            <div className="foot__cell">
              <div className="foot__title">Node metadata</div>
              <ul className="foot__meta">
                <li><span>Node</span><strong>OR-7A</strong></li>
                <li><span>Region</span><strong>US-EAST-1</strong></li>
                <li><span>Version</span><strong>v1.4.0</strong></li>
                <li><span>Uptime</span><strong>15D 04H</strong></li>
              </ul>
            </div>
            <div className="foot__cell">
              <div className="foot__title">Newsletter</div>
              <p className="foot__copy">Weekly signal digest. No tracking.</p>
              <form className="news" aria-label="Subscribe">
                <input
                  className="news__input"
                  type="email"
                  placeholder="you@domain.com"
                  aria-label="Email address"
                  required
                />
                <button type="submit" className="btn btn--primary">Subscribe</button>
              </form>
            </div>
          </section>

          {/* Legal rail */}
          <div className="legal" aria-label="Legal">
            <span><strong>OpenRadar</strong> · OR-7A · US-EAST-1</span>
            <span>Privacy · Terms · Contact</span>
            <span>© 2025 · v1.4.0</span>
          </div>
        </div>
      </main>

      {/* ===== MOBILE (≤980px) — hero + radar integrated; one telemetry bank ===== */}
      <div className="mob-mount">
        <div className="mob-chassis" role="region" aria-label="Open Radar operational console">

          {/* Brand rail */}
          <header className="mob-brand">
            <span className="mob-brand__l">
              <span className="brand__crest" aria-hidden="true">
                <svg viewBox="0 0 18 18">
                  <circle cx="9" cy="9" r="6.5" fill="none" stroke="#3a444d" strokeWidth="0.9" />
                  <circle cx="9" cy="9" r="3" fill="none" stroke="#3a444d" strokeWidth="0.6" />
                  <line x1="9" y1="9" x2="13.5" y2="4.5" stroke="#8fe07a" strokeWidth="0.9" />
                  <circle cx="9" cy="9" r="0.9" fill="#8fe07a" />
                </svg>
              </span>
              <span className="brand__name">OPEN · RADAR</span>
            </span>
            <button className="btn" aria-label="Open menu">Menu</button>
          </header>

          {/* Status */}
          <div className="mob-status">
            <span className="mob-status__led" />
            <span><strong>Online</strong></span>
            <span>·</span>
            <span>Updated 2 min ago</span>
          </div>

          {/* Integrated instrument assembly — hero + radar in ONE framed bay */}
          <section className="mob-instr" aria-label="Operational instrument">
            <div className="mob-hero__eyebrow"><strong>Online</strong> · Operational console</div>
            <h1 className="mob-hero__title">
              Practical AI tools &amp; prompts.
            </h1>
            <p className="mob-hero__lede">
              Engineering-oriented directory — tracked daily.
            </p>
            <div className="mob-cta">
              <button className="mob-cta__primary">Explore Tools</button>
              <div className="mob-cta__row">
                <button className="btn">Today&apos;s Picks</button>
                <button className="btn">Browse Kits</button>
              </div>
            </div>
            <div className="mob-radar">
              <div className="mob-radar__frame">
                <div className="mob-radar__glass">
                  <RadarSvg idSuffix="2" />
                </div>
              </div>
            </div>
          </section>

          {/* Four featured category counters — compact, single row */}
          <section className="mob-dest" aria-label="Featured destinations">
            <div className="mob-dest__cell">
              <span className="mob-dest__title">Tools</span>
              <span className="mob-dest__num"><strong>128</strong></span>
              <span className="mob-dest__sub">Indexed</span>
            </div>
            <div className="mob-dest__cell">
              <span className="mob-dest__title">Kits</span>
              <span className="mob-dest__num"><strong>24</strong></span>
              <span className="mob-dest__sub">Prompt kits</span>
            </div>
            <div className="mob-dest__cell">
              <span className="mob-dest__title">Learn</span>
              <span className="mob-dest__num"><strong>12</strong></span>
              <span className="mob-dest__sub">Paths</span>
            </div>
            <div className="mob-dest__cell">
              <span className="mob-dest__title">Jobs</span>
              <span className="mob-dest__num"><strong>37</strong></span>
              <span className="mob-dest__sub">Live</span>
            </div>
          </section>

          {/* ONE recessed 2×3 instrument bank — single shared chassis */}
          <section className="mob-tele" aria-label="Telemetry bank">
            <div className="mob-tele__bank">
              <div className="mob-tele__cell">
                <span className="mob-tele__label">Signals</span>
                <span className="mob-tele__value"><strong>4</strong></span>
              </div>
              <div className="mob-tele__cell">
                <span className="mob-tele__label">Status</span>
                <span className="mob-tele__value"><strong>Nominal</strong></span>
              </div>
              <div className="mob-tele__cell">
                <span className="mob-tele__label">API</span>
                <span className="mob-tele__value"><strong>42ms</strong></span>
              </div>
              <div className="mob-tele__cell">
                <span className="mob-tele__label">Sweep</span>
                <span className="mob-tele__value"><strong>4.0s</strong></span>
              </div>
              <div className="mob-tele__cell">
                <span className="mob-tele__label">Sources</span>
                <span className="mob-tele__value"><strong>11/11</strong></span>
              </div>
              <div className="mob-tele__cell">
                <span className="mob-tele__label">Update</span>
                <span className="mob-tele__value"><strong>2m</strong></span>
              </div>
            </div>
          </section>

          {/* Newsletter */}
          <section className="mob-news" aria-label="Newsletter">
            <div className="mob-news__title">Weekly signal digest</div>
            <form className="news" aria-label="Subscribe">
              <input
                className="news__input"
                type="email"
                placeholder="you@domain.com"
                aria-label="Email address"
                required
              />
              <button type="submit" className="btn btn--primary">Subscribe</button>
            </form>
          </section>

          {/* Legal */}
          <div className="mob-legal">
            <div><strong>OpenRadar</strong> · OR-7A · US-EAST-1</div>
            <div style={{ marginTop: 4 }}>Privacy · Terms · Contact</div>
            <div style={{ marginTop: 4 }}>© 2025 · v1.4.0</div>
          </div>
        </div>
      </div>
    </>
  );
}

// Module component with five templates: list / tags / progress / lamp / spark
type Template = "list" | "tags" | "progress" | "lamp" | "spark";

function Mod({
  title,
  more,
  template,
  rows,
  tags,
  progress,
  lamps,
  values,
}: {
  title: string;
  more: string;
  template: Template;
  rows?: ReadonlyArray<{ name: string; meta: string }>;
  tags?: ReadonlyArray<string>;
  progress?: ReadonlyArray<{ name: string; done: number; total: number }>;
  lamps?: ReadonlyArray<{ name: string; state: "ok" | "warn" | "err" | "idle"; label: string }>;
  values?: number[];
}) {
  return (
    <div className="mod">
      <div className="mod__head">
        <span className="mod__title">{title}</span>
        <button className="mod__more">{more}</button>
      </div>
      <div className="mod__body">
        {template === "list" && rows?.map((r) => (
          <div key={r.name} className="mod__row">
            <span className="mod__name">{r.name}</span>
            <span className="mod__meta">{r.meta}</span>
          </div>
        ))}
        {template === "tags" && (
          <div className="mod__tags">
            {tags?.map((t, i) => (
              <span key={t} className={`tag${i === 0 ? " tag--id" : ""}`}>{t}</span>
            ))}
          </div>
        )}
        {template === "progress" && progress?.map((p) => (
          <div key={p.name} className="mod__progress">
            <div className="mod__progress-row">
              <span className="mod__progress-name">{p.name}</span>
              <span className="mod__progress-count">{p.done}/{p.total}</span>
            </div>
            <div className="progress-bar">
              {Array.from({ length: p.total }).map((_, i) => (
                <span
                  key={i}
                  className={`progress-bar__seg${i < p.done ? " progress-bar__seg--on" : ""}`}
                />
              ))}
            </div>
          </div>
        ))}
        {template === "lamp" && lamps?.map((l) => (
          <div key={l.name} className="mod__lamp-row">
            <span className={`lamp${l.state === "warn" ? " lamp--warn" : l.state === "err" ? " lamp--err" : l.state === "idle" ? " lamp--idle" : ""}`} />
            <span className="mod__lamp-name">{l.name}</span>
            <span className="mod__lamp-state">{l.label}</span>
          </div>
        ))}
        {template === "spark" && values && (
          <div className="mod__spark-line">
            <MiniLine values={values} />
          </div>
        )}
      </div>
    </div>
  );
}
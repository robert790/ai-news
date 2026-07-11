const BLIPS = [
  [69, 55], [132, 73], [150, 116], [117, 145], [62, 132], [47, 92],
];

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

const JOBS = [
  ["AI Engineer", "Remote", "Full-time"],
  ["ML Ops Engineer", "Europe", "Full-time"],
  ["Prompt Engineer", "Remote", "Contract"],
];

function Bolt({ className = "" }: { className?: string }) {
  return <span className={`bolt ${className}`} aria-hidden="true" />;
}

function Radar() {
  return (
    <div className="radar-rig" aria-label="OpenRadar signal display">
      <div className="radar-readout radar-readout--nw"><span>RNG</span><strong>200</strong></div>
      <div className="radar-readout radar-readout--ne"><span>BRG</span><strong>315°</strong></div>
      <div className="radar-readout radar-readout--sw"><span>SWP</span><strong>04.2s</strong></div>
      <div className="radar-readout radar-readout--se"><span>CHN</span><strong>A</strong></div>
      <div className="radar-bezel">
        <div className="radar-glass">
          <svg viewBox="0 0 200 200" role="img" aria-label="Radar showing six current signals">
            <defs>
              <radialGradient id="radarField">
                <stop offset="0" stopColor="#1b351b" stopOpacity=".72" />
                <stop offset=".68" stopColor="#071208" stopOpacity=".85" />
                <stop offset="1" stopColor="#010402" />
              </radialGradient>
              <linearGradient id="beam" x1="0" x2="1">
                <stop stopColor="#baff71" stopOpacity=".04" />
                <stop offset="1" stopColor="#baff71" stopOpacity=".78" />
              </linearGradient>
              <radialGradient id="blip">
                <stop stopColor="#e5ffae" />
                <stop offset=".45" stopColor="#9de95f" />
                <stop offset="1" stopColor="#79c84c" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="100" cy="100" r="98" fill="url(#radarField)" />
            {[24, 43, 62, 81].map((r) => <circle key={r} cx="100" cy="100" r={r} className="radar-grid" />)}
            <path d="M4 100H196M100 4V196" className="radar-grid" />
            <path d="M100 100L184 44A101 101 0 0 1 197 77Z" fill="url(#beam)" className="radar-beam" />
            <circle cx="100" cy="100" r="2.5" className="radar-origin" />
            {BLIPS.map(([cx, cy], index) => <circle key={index} cx={cx} cy={cy} r="4" fill="url(#blip)" />)}
            <g className="radar-bearing"><text x="96" y="12">000</text><text x="176" y="104">090</text><text x="94" y="193">180</text><text x="8" y="104">270</text></g>
          </svg>
        </div>
      </div>
    </div>
  );
}

function Module({ title, code, children, className = "" }: { title: string; code: string; children: React.ReactNode; className?: string }) {
  return (
    <article className={`module ${className}`}>
      <header className="module-head"><span className="module-code">{code}</span><h2>{title}</h2><button type="button">View all <b>›</b></button></header>
      <div className="module-body">{children}</div>
    </article>
  );
}

export default function Home() {
  return (
    <main className="page-shell">
      <div className="machine">
        <Bolt className="machine-bolt machine-bolt--tl" /><Bolt className="machine-bolt machine-bolt--tr" />
        <Bolt className="machine-bolt machine-bolt--bl" /><Bolt className="machine-bolt machine-bolt--br" />

        <header className="top-deck">
          <a className="brand" href="#" aria-label="OpenRadar home">
            <span className="brand-scope" aria-hidden="true"><i /></span>
            <span><strong>OPEN · RADAR</strong><small>AI tools · prompts · learn · jobs</small></span>
          </a>
          <nav aria-label="Main navigation">
            <a className="active" href="#">Home</a><a href="#tools">Tools</a><a href="#kits">Prompt Kits</a><a href="#learn">Learn</a><a href="#jobs">Jobs</a>
          </nav>
          <div className="top-actions" aria-label="Utilities"><button aria-label="Search">⌕</button><button aria-label="Saved items">▯</button><button aria-label="Notifications">♢</button><span className="dial" aria-hidden="true" /></div>
          <button className="menu" type="button" aria-label="Open navigation"><span /> Menu</button>
          <div className="online"><i /> System online</div>
        </header>

        <section className="hero-deck" aria-labelledby="hero-title">
          <span className="grip grip--left" aria-hidden="true" /><span className="grip grip--right" aria-hidden="true" />
          <Bolt className="hero-bolt hero-bolt--tl" /><Bolt className="hero-bolt hero-bolt--tr" /><Bolt className="hero-bolt hero-bolt--bl" /><Bolt className="hero-bolt hero-bolt--br" />
          <div className="hero-copy">
            <p className="kicker"><i /> Operational console</p>
            <h1 id="hero-title">Find what works.<br />Ship what matters.</h1>
            <span className="rule" aria-hidden="true" />
            <p className="lede">Practical AI tools and prompts for engineers, builders, and operators. No noise. Just signal.</p>
            <div className="hero-actions"><a className="primary-action" href="#tools">Explore tools <b>→</b></a><a href="#picks">Today&apos;s picks</a><a href="#kits">Browse kits</a></div>
            <a className="overview" href="#overview"><i>▶</i> New here? Watch 60-sec overview</a>
          </div>
          <Radar />
        </section>

        <section className="status-rail" aria-label="Current index status">
          <div><i className="status-icon">ϟ</i><span>Signals<small>Reviewed daily</small></span></div>
          <div><i className="status-icon">⌘</i><span>Tools<small>Curated index</small></span></div>
          <div><i className="status-icon">▱</i><span>Jobs<small>Verified roles</small></span></div>
          <div><i className="pulse" /><span>Feeds<small>All channels online</small></span></div>
          <div><i className="status-icon">◷</i><span>Cadence<small>Updated weekly</small></span></div>
        </section>

        <section className="module-grid" aria-label="OpenRadar destinations">
          <Module title="Featured tools" code="01" className="tools-module">
            {TOOLS.map((tool) => <div className="tool-row" key={tool.name}><span className="tool-mark">{tool.mark}</span><span><strong>{tool.name}</strong><small>{tool.note}</small></span><em>{tool.tag}</em></div>)}
          </Module>
          <Module title="Prompt kits" code="02" className="kits-module">
            {KITS.map((kit) => <div className="kit-row" key={kit.no}><b>{kit.no}</b><span><strong>{kit.name}</strong><small>{kit.note}</small></span><em>{kit.tag}</em></div>)}
          </Module>
          <Module title="Learn path" code="03" className="learn-module">
            <div className="course"><span className="course-icon">▤</span><span><strong>AI Foundations</strong><small>Start here. 10 short chapters.</small></span><b>4 / 10</b></div>
            <div className="progress"><i /></div>
            <ol><li><span>What is AI, really?</span><b>✓</b></li><li><span>Prompts that work</span><b>✓</b></li><li><span>Tools overview</span><b>▶</b></li></ol>
          </Module>
          <Module title="Jobs / roles" code="04" className="jobs-module">
            {JOBS.map(([name, place, type]) => <div className="job-row" key={name}><span><strong>{name}</strong><small>{place}</small></span><em>{type}</em></div>)}
          </Module>
        </section>

        <section className="lower-bank">
          <div className="signal-panel"><p><span>Selection standard</span><b>Human reviewed</b></p><ul className="standards-list"><li><i />Clear use case</li><li><i />Practical evidence</li><li><i />No paid placement</li></ul></div>
          <div className="updates-panel"><p><span>Latest field notes</span><b>Editorial desk</b></p><ul><li><b>01</b><span>Choosing a research assistant</span><time>Guide</time></li><li><b>02</b><span>When an AI coding tool pays off</span><time>Test</time></li><li><b>03</b><span>A prompt kit for sharper briefs</span><time>Kit</time></li></ul></div>
          <div className="health-panel"><p><span>Coverage</span><b>Five surfaces</b></p><ul><li>AI tools <i /></li><li>Prompt kits <i /></li><li>Learning paths <i /></li><li>Career signals <i /></li></ul></div>
        </section>

        <footer className="footer-deck">
          <div className="footer-mark"><span className="mini-scope" aria-hidden="true" /><p><strong>No hype. No spam.<br />Just what works.</strong><small>Built for builders who ship.</small></p></div>
          <dl><div><dt>Focus</dt><dd>Practical AI</dd></div><div><dt>Review</dt><dd>Human-led</dd></div><div><dt>Format</dt><dd>Concise</dd></div><div><dt>Language</dt><dd>English</dd></div></dl>
          <form><label htmlFor="email">Stay in the loop <small>Get top signals weekly.</small></label><span><input id="email" type="email" placeholder="you@domain.com" /><button aria-label="Subscribe">→</button></span></form>
          <div className="legal"><span>© 2026 OpenRadar</span><span>Status <i /></span><a href="#privacy">Privacy</a><a href="#terms">Terms</a><a href="#contact">Contact</a><small>Designed for engineers. Built for operators.</small></div>
        </footer>
      </div>
    </main>
  );
}
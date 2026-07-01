"""OpenRadar · Design system v3.

Cinematic warm-dark workspace. One amber accent, four section tags,
three font families. Every selector below maps to a real element;
nothing is decorative-only.

Hierarchy:
  Surface   bg → bg-side → surface → surface-2 → border
  Text      text → text-2 → muted → muted-2
  Accent    amber (primary), sage (signal), coral, lavender, sky
  Type      Newsreader (display) · Inter (UI) · JetBrains Mono (meta)

Layout primitives (use these names, they are stable):
  .or-card            — single news/repo card
  .or-bento           — 3-up landing section grid
  .or-hero            — cinematic centered hero (Azi, News, etc.)
  .or-top-bar         — left live badge · right caption (one row)
  .or-tips            — ambient dev-tip cycling strip
  .or-pill            — selection chip in filter rows
  .or-tab             — selected/unselected segmented pill (nav)
  .or-frame           — bordered frame (used by prompts cards only)
"""

# ─── Colors ──────────────────────────────────────────────────────────────
COLORS = {
    # Warm dark surfaces (no pure black — black kills premium feel)
    "bg":          "#14110d",
    "bg_sidebar":  "#0d0b08",
    "bg_glow":     "#1a1611",     # behind the radar pulse
    "surface":     "#1c1813",
    "surface_2":   "#25201a",
    "border":      "#2a2520",
    "border_strong": "#3a342c",

    # Text
    "text":        "#f4ede0",
    "text_2":      "#cdc4b1",
    "muted":       "#9a8f7c",
    "muted_2":     "#6a6058",

    # Accents — one per section. Restraint beats variety.
    "amber":       "#d4915a",    # primary warmth / CTA
    "sage":        "#8ba888",    # signal / live status
    "coral":       "#c99595",    # news
    "lavender":    "#a89cc4",    # prompts
    "sky":         "#8ba8b8",    # tools / repos

    # Semantic
    "success":     "#9bb88a",
    "warn":        "#d9b87a",
    "danger":      "#c98a82",
}


SECTION_ACCENT = {
    "azi":      "amber",
    "news":     "coral",
    "learning": "sage",
    "jobs":     "sage",
    "prompts":  "lavender",
}


# ─── Typography ──────────────────────────────────────────────────────────
FONTS = {
    "display":   "'Newsreader', 'Iowan Old Style', Georgia, serif",
    "ui":        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono":      "'JetBrains Mono', 'SF Mono', Menlo, monospace",
}


# ─── Spacing scale (px) ──────────────────────────────────────────────────
SPACING = {
    "xs": 4, "sm": 8, "md": 12, "lg": 16,
    "xl": 24, "2xl": 32, "3xl": 48, "4xl": 64, "5xl": 96,
}


# ─── Motion ──────────────────────────────────────────────────────────────
MOTION = {
    "ease":        "cubic-bezier(0.16, 1, 0.3, 1)",
    "ease_soft":   "cubic-bezier(0.4, 0, 0.2, 1)",
    "fast":        "150ms",
    "base":        "240ms",
    "slow":        "400ms",
    "reveal":      "600ms",
}


# ─── Lecture column (PR-A: Learning layout v1) ───────────────────────────
LECTURE_MAX_WIDTH_PX = 760  # comfortable reading measure for the Learning tab
LECTURE_GUTTER_PX = 24      # side gutter on narrow viewports


def lecture_css() -> str:
    """Single-column, max-width lecture page styling for the Learning tab.

    Centered reading column on desktop; full-width with side padding on
    narrow viewports. Token-driven — uses the CSS custom properties
    already emitted by ``render_css()``, so this block is a no-op if
    the global theme CSS hasn't been injected yet.
    """
    return f"""<style>
  .lrn-lecture {{
    max-width: {LECTURE_MAX_WIDTH_PX}px;
    margin: 0 auto;
    padding: 0 {LECTURE_GUTTER_PX}px;
  }}
  .lrn-rule {{
    border: 0;
    border-top: 1px solid var(--border, #2a2520);
    margin: 1.6rem 0;
  }}
  .lrn-numeral {{
    font-family: {FONTS['display']};
    font-size: 4.5rem;
    font-weight: 300;
    line-height: 1;
    letter-spacing: -0.02em;
  }}
  .lrn-breadcrumb {{
    font-family: {FONTS['mono']};
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted, #9a8f7c);
  }}
  .lrn-domain-tag {{
    font-family: {FONTS['mono']};
    font-size: 0.6rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }}
  .lrn-title {{
    font-family: {FONTS['display']};
    font-weight: 500;
    font-size: 2.4rem;
    line-height: 1.15;
    margin: 0.4rem 0 0.3rem 0;
    color: var(--text, #f4ede0);
  }}
  .lrn-subtitle {{
    font-family: {FONTS['display']};
    font-style: italic;
    font-size: 1.1rem;
    line-height: 1.5;
    color: var(--muted, #9a8f7c);
    margin: 0;
  }}
  .lrn-footer {{
    font-family: {FONTS['mono']};
    font-size: 0.7rem;
    color: var(--muted, #9a8f7c);
    letter-spacing: 0.04em;
  }}
  .lrn-navlink {{
    font-family: {FONTS['display']};
    font-size: 1rem;
    color: var(--text, #f4ede0);
    text-decoration: none;
    border-bottom: 1px dashed var(--border-strong, #3a342c);
  }}
  .lrn-navlink:hover {{ color: var(--amber, #d4915a); border-bottom-color: var(--amber, #d4915a); }}

  /* PR-A follow-up: method card + completion state.
     (Takeaway cards replaced by native st.checkbox in the render path
     — no custom CSS needed.) */

  .lrn-method {{
    border: 1px solid var(--border, #2a2520);
    border-left: 3px solid var(--sage, #8ba888);
    background: rgba(244, 237, 224, 0.018);
    border-radius: 0 10px 10px 0;
    padding: 1.1rem 1.25rem;
  }}
  .lrn-method-name {{
    font-family: {FONTS['display']};
    font-size: 1.28rem;
    font-weight: 500;
    line-height: 1.3;
    color: #f4ede0;
    margin: 0.25rem 0 0.55rem;
  }}
  .lrn-method-summary {{
    font-family: {FONTS['display']};
    font-size: 1rem;
    line-height: 1.65;
    color: #cdc4b1;
  }}
  .lrn-method-why {{
    margin-top: 0.7rem;
    padding-top: 0.7rem;
    border-top: 1px dashed rgba(244, 237, 224, 0.08);
    font-family: {FONTS['display']};
    font-style: italic;
    font-size: 0.98rem;
    line-height: 1.55;
    color: #a8c0ae;
  }}
  .lrn-completion {{
    margin-top: 1.4rem;
    padding: 1.1rem 1.2rem 1.15rem;
    border-top: 1px solid #a8c0ae;
    border-radius: 6px;
    background: rgba(168, 192, 174, 0.05);
    text-align: center;
  }}
  .lrn-completion-msg {{
    font-family: {FONTS['display']};
    font-style: italic;
    font-size: 1.2rem;
    line-height: 1.5;
    color: #f4ede0;
  }}
  .lrn-completion-sub {{
    margin-top: 0.4rem;
    font-family: {FONTS['mono']};
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a8c0ae;
  }}

  /* Narrow-viewport tightening — keep reading comfortable on phones. */
  @media (max-width: 640px) {{
    .lrn-lecture {{ padding: 0 16px; }}
    .lrn-numeral {{ font-size: 3.5rem; }}
    .lrn-title {{ font-size: 1.9rem; }}
  }}
</style>"""


# ─── CSS ─────────────────────────────────────────────────────────────────
def render_css() -> str:
    c = COLORS
    f = FONTS
    m = MOTION

    return f"""<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {{
    --bg: {c['bg']};
    --bg-side: {c['bg_sidebar']};
    --bg-glow: {c['bg_glow']};
    --surface: {c['surface']};
    --surface-2: {c['surface_2']};
    --border: {c['border']};
    --border-strong: {c['border_strong']};

    --text: {c['text']};
    --text-2: {c['text_2']};
    --muted: {c['muted']};
    --muted-2: {c['muted_2']};

    --amber: {c['amber']};
    --sage: {c['sage']};
    --coral: {c['coral']};
    --lavender: {c['lavender']};
    --sky: {c['sky']};

    --ease: {m['ease']};
    --ease-soft: {m['ease_soft']};
    --t-fast: {m['fast']};
    --t-base: {m['base']};
    --t-slow: {m['slow']};
    --t-reveal: {m['reveal']};
  }}

  html {{ scroll-behavior: smooth; }}
  *, *::before, *::after {{ box-sizing: border-box; }}

  /* ── App shell ─────────────────────────────────────────────── */
  .stApp {{
    background:
      radial-gradient(1200px 800px at 20% -10%, #1f1a12 0%, transparent 55%),
      radial-gradient(900px 600px at 90% 100%, #1a140e 0%, transparent 50%),
      var(--bg);
    color: var(--text);
    font-family: {f['ui']};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  section.main > div {{
    padding-top: 2rem;
    padding-bottom: 5rem;
    max-width: 1080px;
  }}

  /* Hide Streamlit chrome */
  #MainMenu, footer, header[data-testid="stHeader"] {{ display: none !important; }}
  .viewerBadge_link__qRIco {{ display: none !important; }}

  /* ── Typography ─────────────────────────────────────────────── */
  h1, h2, h3, h4 {{
    font-family: {f['display']};
    color: var(--text);
    margin: 0 0 0.4rem;
    line-height: 1.2;
  }}
  h1 {{ font-size: 3.4rem; font-weight: 300; letter-spacing: -0.02em; }}
  h2 {{ font-size: 1.9rem; font-weight: 500; }}
  h3 {{ font-size: 1.2rem; font-weight: 500; }}

  p, li {{ color: var(--text-2); line-height: 1.65; }}

  .stCaption, [data-testid="stCaption"] {{
    color: var(--muted) !important;
    font-family: {f['mono']};
    font-size: 0.72rem;
    letter-spacing: 0.02em;
  }}

  a {{ color: var(--coral) !important; text-decoration: none; }}
  a:hover {{ opacity: 0.7; }}

  code, pre {{
    background-color: var(--surface-2) !important;
    color: var(--sky) !important;
    font-family: {f['mono']} !important;
    font-size: 0.85em;
    padding: 0.1em 0.35em;
    border-radius: 4px;
  }}

  /* ── Top nav (sidebar is dead) ──────────────────────────────
     Three column-row: brand (left) · segmented radio (center) · status (right)
     On mobile the radio row still fits because we collapse padding; the
     brand shrinks and the status hides the version. */

  /* Hide Streamlit's sidebar + hamburger entirely */
  [data-testid="stSidebar"] {{ display: none !important; }}
  [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}

  /* Brand link — works inline */
  .or-topnav-brand {{
    display: inline-flex !important;
    align-items: center;
    gap: 0.6rem;
    text-decoration: none !important;
    color: inherit !important;
  }}
  .or-topnav-brand .or-mark {{
    width: 26px; height: 26px;
    color: var(--amber);
    flex-shrink: 0;
  }}
  /* Name + small mono kicker stacked under it — gives the brand a
     "product identity" hierarchy rather than a tiny logo-and-text. */
  .or-name-stack {{
    display: inline-flex;
    flex-direction: column;
    line-height: 1;
    gap: 0.22rem;
  }}
  .or-topnav-brand .or-name {{
    font-family: {f['display']};
    font-size: 1.45rem;
    font-weight: 500;
    letter-spacing: -0.015em;
    line-height: 1;
    color: var(--text);
  }}
  .or-topnav-brand .or-name-kicker {{
    font-family: {f['mono']};
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted-2);
    line-height: 1;
  }}
  .or-topnav-brand:hover .or-mark {{ color: var(--amber); }}

  /* ── Top nav pills (5 buttons inside `.or-nav-pills`) ──────── */

  /* Pill container wrapper (just lays them out in a row) */
  .or-nav-pills {{
    display: flex !important;
    gap: 0.35rem !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0.4rem !important;
    background: rgba(28, 24, 19, 0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    backdrop-filter: blur(8px);
    width: 100% !important;
    overflow-x: auto;
    scrollbar-width: none;
  }}
  .or-nav-pills::-webkit-scrollbar {{ display: none; }}

  /* Each nav button — pill-shaped, hover + selected. Scoped via
     Streamlit's `class="st-key-nav_*"` on the wrapping element container. */
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"],
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"] {{
    border-radius: 999px !important;
    padding: 0.5rem 0.75rem !important;
    font-family: {f['mono']} !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    min-height: 34px !important;
    height: 34px !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    transition:
      background var(--t-fast) var(--ease),
      color var(--t-fast) var(--ease),
      border-color var(--t-fast) var(--ease) !important;
  }}
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"] {{
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid transparent !important;
    font-weight: 500 !important;
  }}
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"]:hover {{
    background: rgba(244, 237, 224, 0.025) !important;
    color: var(--text-2) !important;
    border-color: var(--border) !important;
  }}
  /* Selected — calm sage underline + text-2, no loud gradient. The
     pill container still gives the bar a calm dark frame so the
     active state reads as "this one is in here", not "look at me". */
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {{
    background: rgba(168, 192, 174, 0.10) !important;
    color: var(--text) !important;
    border-color: rgba(168, 192, 174, 0.35) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }}
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"]:hover {{
    background: rgba(168, 192, 174, 0.14) !important;
    color: var(--text) !important;
  }}

  /* Status cluster — right column. Inline-rendered, no card frame. */
  .or-topnav-status {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: {f['mono']};
    font-size: 0.66rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted-2);
    white-space: nowrap;
  }}
  .or-topnav-status .or-live-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.7rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    color: var(--muted);
    background: rgba(255, 255, 255, 0.025);
    font-size: 0.62rem;
  }}
  .or-topnav-status .or-status-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--sage);
    box-shadow: 0 0 8px rgba(139, 168, 136, 0.6);
    animation: or-pulse 2.6s var(--ease-soft) infinite;
  }}
  .or-topnav-status .or-status-dot.demo {{
    background: var(--warn); box-shadow: 0 0 8px rgba(217, 184, 122, 0.5);
  }}

  /* Refresh button styling — small squarish */
  button[data-testid="stBaseButton-secondary"][aria-label=""] {{ /* default ok, but refine below */ }}

  /* The refresh button under the nav status — single, no full width */
  .stButton button[kind="secondary"][aria-label=""] {{
    /* harmless — defaults already work */
  }}

  /* Mobile — stack into 3 rows: brand / pills / status+refresh */
  @media (max-width: 720px) {{
    /* Use `:has()` to find columns by their content. This works in
       Chromium 105+, Safari 15.4+, Firefox 121+ — fine for a 2026 app. */
    [data-testid="stColumn"]:has(.or-topnav-brand),
    [data-testid="stColumn"]:has([class*="st-key-nav_"]),
    [data-testid="stColumn"]:has(.or-topnav-status) {{
      flex: 1 0 100% !important;
      max-width: 100% !important;
      min-width: 100% !important;
    }}
    /* The outer nav row: allow wrap */
    [data-testid="stHorizontalBlock"]:has([data-testid="stColumn"]:has([class*="st-key-nav_"])) {{
      flex-wrap: wrap !important;
      row-gap: 0.6rem !important;
    }}
    /* Status: align right */
    [data-testid="stColumn"]:has(.or-topnav-status) {{
      display: flex !important;
      justify-content: flex-end !important;
    }}
    /* Brand font slightly smaller on narrow; drop the kicker so the
     stack doesn't compete with the pills for horizontal space. */
    .or-topnav-brand .or-name {{ font-size: 1.2rem; }}
    .or-topnav-brand .or-name-kicker {{ display: none; }}
    .or-topnav-brand .or-mark {{ width: 22px; height: 22px; }}
    .or-topnav-status .or-tag-desktop {{ display: none; }}
    .or-topnav-status .or-live-pill {{ font-size: 0.55rem; padding: 0.22rem 0.5rem; }}
  }}

  /* On narrow screens: tighten nav row, drop tagline-ish chrome */
  @media (max-width: 880px) {{
    .or-topnav-brand .or-mark {{ width: 20px; height: 20px; }}
  }}
  @media (max-width: 520px) {{
    .or-topnav-status .or-live-pill {{ padding: 0.22rem 0.45rem; font-size: 0.58rem; }}
  }}

  /* ── Section headings (used everywhere except Azi hero) ────── */
  .or-section-head {{
    margin: 0 0 1.8rem;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
  }}
  .or-section-head .or-eyebrow {{
    font-family: {f['mono']};
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--amber);
    display: block;
    margin-bottom: 0.4rem;
  }}
  .or-section-head h1 {{
    font-size: 2.4rem;
    font-weight: 400;
    margin: 0;
    line-height: 1;
    letter-spacing: -0.015em;
  }}
  .or-section-head .or-caption {{
    font-family: {f['display']};
    font-style: italic;
    font-size: 1.05rem;
    color: var(--muted);
    margin: 0;
    max-width: 460px;
    flex-shrink: 1;
  }}

  /* ── Hero (Azi landing) ────────────────────────────────────── */
  .or-hero {{
    text-align: center;
    padding: 3.2rem 0 2.2rem;
    position: relative;
  }}
  .or-hero .or-eyebrow {{
    font-family: {f['mono']};
    font-size: 0.7rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
  }}
  .or-hero .or-eyebrow::before,
  .or-hero .or-eyebrow::after {{
    content: '';
    width: 24px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--amber), transparent);
  }}
  .or-hero h1 {{
    font-family: {f['display']};
    font-size: clamp(2.6rem, 6vw, 4.4rem);
    font-weight: 300;
    letter-spacing: -0.025em;
    line-height: 1.05;
    margin: 0 0 1.1rem;
  }}
  .or-hero h1 .or-accent {{
    color: var(--amber);
    font-style: italic;
    font-weight: 400;
  }}
  .or-hero .or-sub {{
    font-family: {f['display']};
    font-style: italic;
    font-size: 1.2rem;
    color: var(--muted);
    margin: 0 auto;
    max-width: 540px;
    line-height: 1.5;
  }}

  /* live feed badge inside hero eyebrow row */
  .or-live {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.7rem;
    border: 1px solid var(--sage);
    color: var(--sage);
    font-family: {f['mono']};
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    border-radius: 4px;
    background: rgba(139, 168, 136, 0.05);
  }}
  .or-live .dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--sage);
    animation: or-pulse 2.6s var(--ease-soft) infinite;
  }}

  /* ── Top bar — single thin row above content ──────────────── */
  .or-top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 0.8rem 0 1.6rem;
    min-height: 32px;
  }}
  .or-top-bar .or-caption {{
    font-family: {f['display']};
    font-style: italic;
    color: var(--muted);
    font-size: 0.95rem;
  }}

  /* ── Bento grid (Azi landing: News / Tools / Jobs) ────────── */
  .or-bento {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 0 0 1.6rem;
  }}
  @media (max-width: 880px) {{ .or-bento {{ grid-template-columns: 1fr; }} }}

  .or-bento-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem 1.1rem 1.2rem;
    transition:
      background var(--t-base) var(--ease),
      border-color var(--t-base) var(--ease),
      transform var(--t-base) var(--ease);
    position: relative;
  }}
  .or-bento-card:hover {{
    border-color: var(--border-strong);
    background: var(--surface-2);
  }}
  .or-bento-card .or-bento-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.9rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--border);
  }}
  .or-bento-card .or-bento-title {{
    font-family: {f['mono']};
    font-size: 0.66rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
  }}
  .or-bento-card .or-bento-count {{
    font-family: {f['display']};
    font-size: 1.1rem;
    color: var(--text);
    line-height: 1;
  }}
  .or-bento-card .or-bento-icon {{
    width: 18px; height: 18px;
    flex-shrink: 0;
  }}

  /* ── Card (single item) ────────────────────────────────────── */
  .or-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.95rem 1rem 0.85rem;
    margin: 0 0 0.6rem;
    transition:
      background var(--t-base) var(--ease),
      border-color var(--t-base) var(--ease);
  }}
  .or-card:hover {{
    background: rgba(212, 145, 90, 0.025);
    border-color: rgba(212, 145, 90, 0.35);
  }}
  .or-card-label {{
    font-family: {f['mono']};
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }}
  .or-card-label.amber    {{ color: var(--amber); }}
  .or-card-label.coral    {{ color: var(--coral); }}
  .or-card-label.sky      {{ color: var(--sky); }}
  .or-card-label.sage     {{ color: var(--sage); }}
  .or-card-label.lavender {{ color: var(--lavender); }}
  .or-card-label::before {{
    content: '';
    display: inline-block;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.85;
  }}
  .or-card-title {{
    font-family: {f['display']};
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.3;
    color: var(--text);
    display: block;
    margin-bottom: 0.35rem;
  }}
  .or-card-link {{
    text-decoration: none;
    color: inherit;
  }}
  .or-card-link:hover .or-card-title {{ color: var(--amber); }}
  .or-card-summary {{
    font-family: {f['display']};
    font-size: 0.92rem;
    color: var(--text-2);
    line-height: 1.5;
    margin: 0 0 0.5rem;
  }}
  .or-card-meta {{
    font-family: {f['mono']};
    font-size: 0.65rem;
    letter-spacing: 0.04em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 0.65rem;
    flex-wrap: wrap;
  }}
  .or-card-score {{
    font-family: {f['display']};
    font-size: 1.3rem;
    font-weight: 500;
    color: var(--amber);
    margin-right: 0.4rem;
    line-height: 1;
  }}

  /* ── Methods block (Sebastian Rey BLUE) — ◆ MAIN + ○ alts ─── */

  /* Main method callout — amber gradient border-left */
  .or-method-main {{
    margin-top: 1.5rem;
    padding: 1.1rem 1.2rem;
    background: linear-gradient(180deg,
      rgba(212, 145, 90, 0.10),
      rgba(212, 145, 90, 0.04));
    border-left: 3px solid var(--amber);
    border-radius: 6px;
    transition: transform var(--t-fast) var(--ease);
  }}
  .or-method-main:hover {{
    transform: translateX(2px);
  }}
  .or-method-main .or-method-tag {{
    font-family: {f['mono']};
    font-size: 0.62rem;
    color: var(--amber);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
    font-weight: 600;
  }}
  .or-method-main .or-method-name {{
    font-family: {f['display']};
    font-size: 1.18rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.3;
    margin-bottom: 0.55rem;
  }}
  .or-method-main .or-method-summary {{
    font-family: {f['display']};
    font-size: 0.95rem;
    color: var(--text-2);
    line-height: 1.55;
  }}
  .or-method-main .or-method-when {{
    margin-top: 0.7rem;
    padding-top: 0.55rem;
    border-top: 1px dashed rgba(212, 145, 90, 0.25);
    font-family: {f['mono']};
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 0.04em;
  }}

  /* Alt method label */
  .or-method-alts-label {{
    margin-top: 0.85rem;
    font-family: {f['mono']};
    font-size: 0.6rem;
    color: var(--muted-2);
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }}

  /* Alt expander header — open circle marker */
  .streamlit-expanderHeader:has(p:contains("○")) {{
    font-family: {f['mono']} !important;
    color: var(--muted) !important;
  }}

  /* ── Mini bento (2-up · lesson + prompt on Azi) ───────────── */
  .or-bento-mini {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1.6rem 0 0;
  }}
  @media (max-width: 880px) {{ .or-bento-mini {{ grid-template-columns: 1fr; }} }}

  .or-mini {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.3rem;
    min-height: 220px;
    display: flex;
    flex-direction: column;
  }}
  .or-mini .or-mini-tag {{
    font-family: {f['mono']};
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--sage);
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
  }}
  .or-mini.prompts .or-mini-tag {{ color: var(--lavender); }}
  .or-mini h3 {{
    font-family: {f['display']};
    font-size: 1.4rem;
    font-weight: 500;
    margin: 0 0 0.7rem;
    line-height: 1.25;
  }}
  .or-mini .or-mini-body {{
    font-family: {f['display']};
    font-size: 1rem;
    color: var(--text-2);
    line-height: 1.55;
    margin: 0;
    flex: 1;
  }}
  .or-mini .or-mini-foot {{
    margin-top: 1rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--border);
    font-family: {f['mono']};
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .or-mini .or-mini-foot a {{
    color: var(--amber) !important;
    font-weight: 500;
  }}

  /* ── Filter pills (Prompts tab) ───────────────────────────── */
  .or-pills-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.7rem 0 1rem;
  }}
  button[data-testid="stBaseButton-secondary"],
  button[data-testid="stBaseButton-primary"],
  button[data-testid="baseButton-secondary"],
  button[data-testid="baseButton-primary"] {{
    border-radius: 999px !important;
    padding: 0.3rem 0.75rem !important;
    font-family: {f['mono']} !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.04em !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    transition: all 180ms ease !important;
    min-height: 30px !important;
    height: 30px !important;
  }}
  button[data-testid="stBaseButton-secondary"],
  button[data-testid="baseButton-secondary"] {{
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
  }}
  button[data-testid="stBaseButton-secondary"]:hover,
  button[data-testid="baseButton-secondary"]:hover {{
    background: rgba(212, 145, 90, 0.06) !important;
    color: var(--text-2) !important;
    border-color: var(--border-strong) !important;
  }}
  button[data-testid="stBaseButton-primary"],
  button[data-testid="baseButton-primary"] {{
    background: rgba(212, 145, 90, 0.16) !important;
    color: var(--amber) !important;
    border: 1px solid var(--amber) !important;
    font-weight: 600 !important;
  }}
  button[data-testid="stBaseButton-primary"]:hover,
  button[data-testid="baseButton-primary"]:hover {{
    background: rgba(212, 145, 90, 0.24) !important;
  }}

  /* ── Tips cycling strip (ambient wisdom) ─────────────────── */
  .or-tips {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 0 0 1.6rem;
    padding: 0.7rem 1rem;
    background: rgba(28, 24, 19, 0.6);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-family: {f['mono']};
    color: var(--muted);
    font-size: 0.78rem;
    overflow: hidden;
    backdrop-filter: blur(6px);
  }}
  .or-tips .or-tips-tag {{
    flex-shrink: 0;
    color: var(--amber);
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }}
  .or-tips-slot {{
    position: relative;
    flex: 1;
    min-width: 0;
    height: 1.4em;
  }}
  .or-tip-line {{
    position: absolute;
    inset: 0;
    opacity: 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    animation: or-tip-cycle 24s linear infinite;
  }}
  .or-tip-line .or-tip-cat {{
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    padding: 0.05rem 0.45rem;
    border: 1px solid currentColor;
    border-radius: 2px;
  }}
  .or-tip-line .or-tip-body {{ color: var(--text-2); }}

  .tip-cat.LINUX,    .tip-cat.SHELL {{ color: #a8d9b3; }}
  .tip-cat.RSI,      .tip-cat.HEALTH {{ color: #d4b8c8; }}
  .tip-cat.INFRA,    .tip-cat.DEVOPS {{ color: #9bb8d4; }}
  .tip-cat.BEGINNER, .tip-cat.JUNIOR {{ color: #d9b87a; }}
  .tip-cat.EXPERT,   .tip-cat.PRO    {{ color: #d49898; }}
  .tip-cat.AI,       .tip-cat.PROMPT {{ color: #b8a4d9; }}
  .tip-cat.CAREER,   .tip-cat.JOBS   {{ color: #c5d97c; }}
  .tip-cat.WORKFLOW                  {{ color: #98c5b8; }}

  /* 4 tips × 6s each = 24s loop · 0.5s fade-in, hold 4.5s, 1s fade-out */
  @keyframes or-tip-cycle {{
    0%   {{ opacity: 0; }}
    4%   {{ opacity: 1; }}
    21%  {{ opacity: 1; }}
    25%  {{ opacity: 0; }}
    100% {{ opacity: 0; }}
  }}
  .or-tip-line:nth-child(1) {{ animation-delay:  0s; }}
  .or-tip-line:nth-child(2) {{ animation-delay: -18s; }}
  .or-tip-line:nth-child(3) {{ animation-delay: -12s; }}
  .or-tip-line:nth-child(4) {{ animation-delay: -6s; }}

  /* ── Ambient radar pulse (top-right glow) + scan line ────── */
  @keyframes or-pulse {{
    0%, 100% {{ opacity: 0.4; }}
    50%      {{ opacity: 1; }}
  }}

  @keyframes or-radar-ring {{
    0%   {{ transform: scale(0.1); opacity: 0.55; }}
    100% {{ transform: scale(2.2); opacity: 0; }}
  }}

  .or-radar {{
    position: fixed;
    top: -40vh;
    right: -40vw;
    width: 100vh;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
  }}
  .or-radar::before,
  .or-radar::after {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(212, 145, 90, 0.32);
    animation: or-radar-ring 9s linear infinite;
  }}
  .or-radar::after {{ animation-delay: 4.5s; }}

  @keyframes or-scan-line {{
    0%   {{ transform: translateY(-2vh); opacity: 0; }}
    10%  {{ opacity: 0.5; }}
    90%  {{ opacity: 0.5; }}
    100% {{ transform: translateY(102vh); opacity: 0; }}
  }}
  .or-scan {{
    position: fixed;
    inset: 0 0 auto 0;
    height: 1px;
    background: linear-gradient(90deg,
      transparent 0%,
      rgba(212, 145, 90, 0.45) 50%,
      transparent 100%);
    animation: or-scan-line 14s linear infinite;
    pointer-events: none;
    z-index: 0;
  }}

  @media (prefers-reduced-motion: reduce) {{
    .or-radar::before, .or-radar::after,
    .or-scan, .or-tip-line, .or-live .dot, .or-side-status .dot {{
      animation: none !important;
    }}
    .or-tip-line:first-child {{ opacity: 1 !important; }}
    .or-tip-line:not(:first-child) {{ display: none !important; }}
  }}

  /* ── Reveal animations ───────────────────────────────────── */
  @keyframes or-fade-up {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .or-reveal {{ animation: or-fade-up var(--t-reveal) var(--ease) both; }}
  .or-reveal-1 {{ animation-delay: 0ms; }}
  .or-reveal-2 {{ animation-delay: 80ms; }}
  .or-reveal-3 {{ animation-delay: 160ms; }}
  .or-reveal-4 {{ animation-delay: 240ms; }}

  /* ── Streamlit widgets we DO touch ───────────────────────── */
  /* text input (Prompts search) */
  .stTextInput input {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: {f['ui']} !important;
    padding: 0.6rem 0.9rem !important;
    caret-color: var(--amber) !important;
  }}
  .stTextInput input:focus {{
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(212, 145, 90, 0.18) !important;
  }}

  /* general buttons */
  .stButton > button {{
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 4px !important;
    font-family: {f['mono']} !important;
    font-size: 0.74rem !important;
    letter-spacing: 0.04em !important;
    transition: all var(--t-fast) var(--ease) !important;
  }}
  .stButton > button:hover {{
    background: var(--surface-2) !important;
    border-color: var(--amber) !important;
    color: var(--text) !important;
  }}

  /* radio (Prompts sort row, etc.) — neutral */
  [data-testid="stRadio"] label {{
    color: var(--muted) !important;
    font-family: {f['mono']} !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
  }}

  /* selectbox */
  .stSelectbox [data-baseweb="select"] {{
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
  }}

  /* expander */
  [data-testid="stExpander"] summary {{
    font-family: {f['mono']} !important;
    font-size: 0.74rem !important;
    color: var(--muted) !important;
    letter-spacing: 0.06em !important;
  }}

  /* tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 0.4rem;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 4px !important;
    font-family: {f['mono']} !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: rgba(212, 145, 90, 0.12) !important;
    color: var(--amber) !important;
  }}

  /* ── Responsive ───────────────────────────────────────────── */
  @media (max-width: 880px) {{
    .or-hero {{ padding: 2rem 0 1.4rem; }}
    .or-hero h1 {{ font-size: 2.4rem; }}
    h1 {{ font-size: 2rem; }}
    section.main > div {{
      max-width: 100%;
      padding-left: 1.2rem;
      padding-right: 1.2rem;
    }}
    .or-radar {{ width: 80vh; height: 80vh; top: -35vh; right: -45vw; }}
  }}
</style>"""

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
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');

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
    /* PR11: HF visual parity — widened the cap from a hard 1080px
       to a responsive 100%-with-side-margin. On VPS this still hits
       ~1080px on standard 1280-wide screens, but on HF Spaces (whose
       iframe wraps with different outer padding) the cap no longer
       imposes a noticeably narrower centered look. The `data-testid`
       selector is the modern Streamlit wide-mode container; we keep
       the legacy `section.main > div` for compatibility with 1.32. */
    max-width: min(1280px, calc(100% - 32px));
    margin: 0 auto;
  }}
  /* Modern Streamlit wide container (1.50+) — same treatment so the
     two layouts converge. */
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stAppViewMain"] {{
    max-width: min(1280px, calc(100% - 32px));
    margin: 0 auto;
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

  /* Each nav button — pill-shaped, hover + selected. Scoped via
     Streamlit's `class="st-key-nav_*"` on the wrapping element container.
     PR11: HF Spaces runs Streamlit 1.32, local venv runs ≥1.50. The
     button testid differs between the two — 1.32 emits
     `data-testid="baseButton-primary|secondary"`, 1.50+ emits
     `data-testid="stBaseButton-primary|secondary"`. We target both so
     the pill style survives on every surface. */
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"],
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"],
  [class*="st-key-nav_"] button[data-testid="baseButton-primary"],
  [class*="st-key-nav_"] button[data-testid="baseButton-secondary"] {{
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
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"],
  [class*="st-key-nav_"] button[data-testid="baseButton-secondary"] {{
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid transparent !important;
    font-weight: 500 !important;
  }}
  [class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"]:hover,
  [class*="st-key-nav_"] button[data-testid="baseButton-secondary"]:hover {{
    background: rgba(244, 237, 224, 0.025) !important;
    color: var(--text-2) !important;
    border-color: var(--border) !important;
  }}
  /* Selected — calm sage underline + text-2, no loud gradient. The
     pill container still gives the bar a calm dark frame so the
     active state reads as "this one is in here", not "look at me". */
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"],
  [class*="st-key-nav_"] button[data-testid="baseButton-primary"] {{
    background: rgba(168, 192, 174, 0.10) !important;
    color: var(--text) !important;
    border-color: rgba(168, 192, 174, 0.35) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }}
  [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"]:hover,
  [class*="st-key-nav_"] button[data-testid="baseButton-primary"]:hover {{
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

  /* PR #28: phone-overflow fixes for bento card children.
     (a) The card itself needs min-width: 0 so a CSS-Grid cell can
         shrink below its content's intrinsic width. Without this,
         the long link chip row ("BestJobs ↗ Indeed RO ↗ ...")
         forces the card wider than the viewport on phone.
     (b) The h3 title can hold long role names ("AI Solutions
         Architect"). overflow-wrap: anywhere lets the browser break
         the title at arbitrary points instead of forcing horizontal
         overflow.
     (c) The .or-bento-mini .or-mini-foot > div wraps the chip link
         row inside Jobs role cards. Making it a flex-wrap container
         with gap lets the chips wrap to multiple lines on narrow
         viewports instead of overflowing the card. */
  .or-bento-mini .or-mini {{ min-width: 0; }}
  .or-bento-mini .or-mini h3 {{ overflow-wrap: anywhere; }}
  .or-bento-mini .or-mini-foot > div {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    align-items: baseline;
  }}

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
  }}

  /* ╔══════════════════════════════════════════════════════════════════╗
     ║ RADAR TERMINAL HOME — v2.1 design integration                         ║
     ║ Approved visual target: /tmp/openradar-fallout-terminal-concept-v2-1.html.       ║
     ║ All selectors prefixed with `.ort-page` so they cannot leak onto        ║
     ║ Tools / Prompt Kits / Learn / Jobs (those sections do not emit         ║
     ║ `.ort-page` in their HTML).                                             ║
     ║ No emotion-cache selectors. No raw Streamlit column references.         ║
     ╚══════════════════════════════════════════════════════════════════╝ */

  /* ── tokens (shared with the standalone v2.1 concept) ────── */
  .ort-page{{
    --ort-bg-room:        #0B0D0E;
    --ort-bg-room-2:      #05080A;
    --ort-bg-chassis:     #0F1416;
    --ort-bg-panel:       #0A1110;
    --ort-radar:          #A6FF8A;
    --ort-radar-dim:      #5FBE7A;
    --ort-cyan-crt:       #7EE7DF;
    --ort-amber-rec:      #F0A040;
    --ort-red-rec:        #E25822;
    --ort-ink:            #DDE6DC;
    --ort-ink-mid:        rgba(221, 230, 220, 0.78);
    --ort-ink-dim:        rgba(221, 230, 220, 0.50);
    --ort-ink-deep:       rgba(221, 230, 220, 0.32);
    --ort-line:           rgba(166, 255, 138, 0.20);
    --ort-line-strong:    rgba(166, 255, 138, 0.40);
    --ort-font-display:   'Space Grotesk', system-ui, sans-serif;
    --ort-font-editorial: 'Newsreader', Georgia, serif;
    --ort-font-body:      'Inter', system-ui, -apple-system, sans-serif;
    --ort-font-mono:      'JetBrains Mono', 'SF Mono', Menlo, monospace;
  }}

  /* ── the chassis (three-layer device shell) ───────────────── */
  .ort-page .ort-chassis{{
    position:relative;
    margin-top:18px;
    background:
      linear-gradient(180deg, #232930 0%, #1A1F23 30%, #13181B 65%, #181D21 100%),
      radial-gradient(ellipse at 30% 10%, rgba(255,255,255,.045), transparent 60%);
    border-radius:20px;
    padding:22px 22px 24px;
    box-shadow:
      0 1px 0 rgba(255,255,255,.08) inset,
      0 1px 0 rgba(166,255,138,.05) inset,
      0 -1px 0 rgba(0,0,0,.7) inset,
      0 2px 6px rgba(0,0,0,.55),
      0 16px 32px rgba(0,0,0,.55),
      0 40px 80px rgba(0,0,0,.45);
  }}
  .ort-page .ort-chassis::before{{
    content:"";position:absolute;inset:0;border-radius:20px;
    pointer-events:none;z-index:0;
    background-image:repeating-linear-gradient(135deg,
      rgba(255,255,255,.022) 0 1px, transparent 1px 5px);
  }}
  .ort-page .ort-chassis::after{{
    content:"";position:absolute;inset:0;border-radius:20px;
    pointer-events:none;z-index:0;
    background:
      radial-gradient(ellipse 200px 60px at 18% 92%, rgba(0,0,0,.20), transparent 60%),
      radial-gradient(ellipse 280px 50px at 82% 8%, rgba(255,255,255,.030), transparent 60%),
      linear-gradient(180deg, rgba(255,255,255,.018) 0%, transparent 5%, transparent 95%, rgba(0,0,0,.18) 100%);
  }}

  /* corner screws */
  .ort-page .ort-screw{{position:absolute;width:14px;height:14px;border-radius:50%;
    background:radial-gradient(circle at 35% 35%, #5A6266, #2C3034 60%, #1A1E22 100%);
    box-shadow:
      0 1px 0 rgba(255,255,255,.10) inset,
      0 -1px 0 rgba(0,0,0,.5) inset,
      0 0 0 1px rgba(0,0,0,.5),
      0 1px 2px rgba(0,0,0,.6);
    z-index:3}}
  .ort-page .ort-screw::after{{
    content:"";position:absolute;left:50%;top:50%;width:1.5px;height:7px;
    background:rgba(0,0,0,.7);transform:translate(-50%,-50%) rotate(28deg);
    box-shadow:0 0 0 0.5px rgba(0,0,0,.4);
  }}
  .ort-page .ort-screw--tl{{top:10px;left:10px}}
  .ort-page .ort-screw--tr{{top:10px;right:10px}}
  .ort-page .ort-screw--bl{{bottom:10px;left:10px}}
  .ort-page .ort-screw--br{{bottom:10px;right:10px}}

  /* STAMP between the top screws */
  .ort-page .ort-stamp{{
    position:absolute;top:14px;left:50%;transform:translateX(-50%);
    font-family:var(--ort-font-mono);font-size:0.52rem;letter-spacing:0.30em;
    text-transform:uppercase;color:rgba(180, 195, 175, 0.45);
    padding:2px 10px;border:1px solid rgba(180, 195, 175, 0.12);
    border-radius:2px;background:rgba(0,0,0,.18);
    z-index:2;pointer-events:none;
  }}
  .ort-page .ort-stamp b{{color:rgba(200, 210, 195, 0.6);font-weight:600}}

  /* ── the screen frame (inner bezel between chassis and CRT) ── */
  .ort-page .ort-screen-frame{{
    position:relative;
    border-radius:12px;
    background:linear-gradient(180deg, #0C100E 0%, #080C0B 100%);
    padding:18px;
    box-shadow:
      0 1px 0 rgba(255,255,255,.05) inset,
      0 -1px 0 rgba(166,255,138,.08) inset,
      0 0 0 1px rgba(0,0,0,.6),
      0 4px 16px rgba(0,0,0,.6) inset,
      0 0 30px rgba(0,0,0,.4);
  }}
  .ort-page .ort-rivet{{position:absolute;width:6px;height:6px;border-radius:50%;
    background:radial-gradient(circle at 30% 30%, #6A7074, #2C3034 60%, #15181B 100%);
    box-shadow:0 0 0 1px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.08);
    z-index:2}}
  .ort-page .ort-rivet--tl{{top:6px;left:6px}}
  .ort-page .ort-rivet--tr{{top:6px;right:6px}}
  .ort-page .ort-rivet--bl{{bottom:6px;left:6px}}
  .ort-page .ort-rivet--br{{bottom:6px;right:6px}}

  /* ── the screen face (the CRT itself) ──────────────────────── */
  .ort-page .ort-screen{{
    position:relative;
    border-radius:6px;
    background:
      radial-gradient(ellipse 70% 50% at 6% 2%, rgba(166,255,138,.10), transparent 60%),
      radial-gradient(ellipse 70% 50% at 94% 98%, rgba(126,231,223,.06), transparent 60%),
      radial-gradient(ellipse 100% 80% at 50% 50%, rgba(166,255,138,.04), transparent 80%),
      var(--ort-bg-panel);
    padding:18px 22px 16px;
    overflow:hidden;
    box-shadow:
      0 0 0 1px rgba(166,255,138,.18),
      0 0 28px rgba(166,255,138,.06),
      inset 0 0 90px rgba(0,0,0,.5);
  }}
  .ort-page .ort-screen::before{{
    content:"";position:absolute;inset:0;pointer-events:none;
    background-image:repeating-linear-gradient(to bottom,
      rgba(166,255,138,.05) 0 1px, transparent 1px 3px);
    mix-blend-mode:screen;z-index:1;
  }}
  .ort-page .ort-screen::after{{
    content:"";position:absolute;inset:0;pointer-events:none;
    background:
      linear-gradient(180deg, rgba(166,255,138,.04) 0%, transparent 50%, rgba(0,0,0,.42) 100%),
      radial-gradient(ellipse at 50% 0%, rgba(255,255,255,.025), transparent 50%);
    z-index:2;
  }}
  .ort-page .ort-screen > *{{position:relative;z-index:3}}

  /* ── topnav ─────────────────────────────────────────────────── */
  .ort-page .ort-topnav{{
    position:relative;display:grid;
    grid-template-columns:minmax(0,auto) minmax(0,1fr) auto;
    align-items:center;gap:18px;
    padding:14px 22px 12px;
    background:linear-gradient(180deg, rgba(255,255,255,.025), rgba(0,0,0,0));
    border:1px solid rgba(255,255,255,.06);
    border-radius:8px;
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,.05),
      inset 0 -1px 0 rgba(0,0,0,.55),
      0 6px 16px rgba(0,0,0,.30);
  }}
  .ort-page .ort-topnav::after{{
    content:"";position:absolute;left:18px;right:18px;bottom:-1px;height:1px;
    background:linear-gradient(90deg, transparent 0%, var(--ort-line-strong) 50%, transparent 100%);
    pointer-events:none;
  }}
  .ort-page .ort-brand{{display:inline-flex;align-items:center;gap:14px;
    text-decoration:none !important;color:inherit !important;min-width:0}}
  .ort-page .ort-brand .ort-mark{{width:36px;height:36px;flex-shrink:0;color:var(--ort-radar);
    filter:drop-shadow(0 0 5px rgba(166,255,138,.55)) drop-shadow(0 0 16px rgba(166,255,138,.18))}}
  .ort-page .ort-brand .ort-mark svg{{width:100%;height:100%;display:block}}
  .ort-page .ort-brand-stack{{display:inline-flex;flex-direction:column;line-height:1;gap:5px;min-width:0}}
  .ort-page .ort-name{{
    font-family:var(--ort-font-display);font-weight:700;font-size:1.18rem;
    letter-spacing:0.20em;color:var(--ort-ink);text-transform:uppercase;
    white-space:nowrap;display:flex;align-items:center;gap:10px;
  }}
  .ort-page .ort-name .ort-name-dot{{color:var(--ort-radar);font-size:1.1em;line-height:1;padding:0 1px}}
  .ort-page .ort-name .ort-mark-glow{{
    display:inline-block;width:7px;height:7px;border-radius:50%;
    background:var(--ort-radar);box-shadow:0 0 8px rgba(166,255,138,.7);
    animation:ort-pulse 2.4s ease-in-out infinite;
  }}
  .ort-page .ort-kicker{{
    font-family:var(--ort-font-mono);font-size:.62rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:32ch;
  }}

  .ort-page .ort-nav{{display:flex;align-items:center;justify-content:center;gap:4px;min-width:0}}
  .ort-page .ort-tab{{
    display:inline-flex;align-items:center;gap:8px;
    padding:9px 14px;border-radius:5px;
    background:transparent !important;color:var(--ort-ink-mid) !important;
    font-family:var(--ort-font-mono);font-size:.72rem;letter-spacing:0.16em;
    text-transform:uppercase;text-decoration:none !important;
    border:1px solid transparent;white-space:nowrap;
    transition:color .18s ease, background .18s ease, border-color .18s ease;
  }}
  .ort-page .ort-tab:hover{{color:var(--ort-ink) !important;background:rgba(166,255,138,.04) !important}}
  .ort-page .ort-tab.is-active{{
    color:var(--ort-radar) !important;background:rgba(166,255,138,.10) !important;
    border-color:var(--ort-line-strong) !important;
    box-shadow:inset 0 0 0 1px rgba(166,255,138,.10);
  }}
  .ort-page .ort-tab .ort-tab-dot{{display:inline-block;width:5px;height:5px;border-radius:50%;
    background:transparent;flex-shrink:0}}
  .ort-page .ort-tab.is-active .ort-tab-dot{{background:var(--ort-radar);
    box-shadow:0 0 6px rgba(166,255,138,.6)}}

  /* nav-action slot — left as an empty column on desktop so the
     grid layout reads as brand + tabs + status. Refresh button
     lives outside this integration (deferred follow-up). */
  .ort-page .ort-nav-action{{display:inline-flex;align-items:center;justify-content:flex-end;gap:10px;min-height:1px}}
  .ort-page .ort-sys-pill{{
    display:inline-flex;align-items:center;gap:8px;
    padding:7px 12px;border-radius:999px;
    border:1px solid var(--ort-line-strong);
    background:linear-gradient(180deg, rgba(255,255,255,.025), rgba(0,0,0,0));
    font-family:var(--ort-font-mono);font-size:.6rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);white-space:nowrap;
  }}
  .ort-page .ort-sys-pill .ort-led{{
    display:inline-block;width:6px;height:6px;border-radius:50%;
    background:var(--ort-radar);box-shadow:0 0 8px rgba(166,255,138,.7);
    animation:ort-pulse 2.4s ease-in-out infinite;
  }}
  .ort-page .ort-sys-pill .live{{color:var(--ort-radar)}}

  /* ── status bezel (telemetry strip) ───────────────────────── */
  .ort-page .ort-screen-status{{
    display:flex;align-items:center;justify-content:space-between;gap:14px;
    padding:11px 16px;
    background:linear-gradient(180deg, #0A0D0F 0%, #06080A 100%);
    border:1px solid var(--ort-line);
    border-radius:5px;
    margin-top:12px;
  }}
  .ort-page .ort-screen-status .left,
  .ort-page .ort-screen-status .right{{
    display:inline-flex;align-items:center;gap:14px;flex-wrap:wrap;
  }}
  .ort-page .ort-screen-status .led{{
    display:inline-block;width:6px;height:6px;border-radius:50%;
    box-shadow:0 0 6px currentColor;
    animation:ort-pulse 2.4s ease-in-out infinite;
  }}
  .ort-page .ort-screen-status .led--rec{{color:var(--ort-red-rec);background:var(--ort-red-rec);
    animation:ort-pulse-fast 1.4s ease-in-out infinite}}
  .ort-page .ort-screen-status .led--amber{{color:var(--ort-amber-rec);background:var(--ort-amber-rec)}}
  .ort-page .ort-screen-status .led--green{{color:var(--ort-radar);background:var(--ort-radar)}}
  .ort-page .ort-screen-status .item{{display:inline-flex;align-items:center;gap:6px}}
  .ort-page .ort-screen-status .live{{color:var(--ort-radar);font-weight:600}}
  .ort-page .ort-screen-status .v{{color:var(--ort-ink);font-weight:500}}
  .ort-page .ort-screen-status .v-acc{{color:var(--ort-radar);font-weight:500}}
  .ort-page .ort-screen-status .sep{{color:var(--ort-ink-deep);opacity:.55;margin:0 4px}}

  /* ── hero (left copy + right radar) ──────────────────────── */
  .ort-page .ort-screen-body{{
    display:grid;
    grid-template-columns:minmax(0, 1.18fr) minmax(0, 1fr);
    gap:38px;align-items:stretch;
    padding:30px 4px 22px;
  }}
  .ort-page .ort-screen-copy{{display:flex;flex-direction:column;justify-content:center;min-width:0}}
  .ort-page .ort-eyebrow{{
    font-family:var(--ort-font-mono);font-size:.66rem;letter-spacing:0.24em;
    text-transform:uppercase;color:var(--ort-radar);margin:0 0 18px;
    display:flex;align-items:center;gap:10px;
  }}
  .ort-page .ort-eyebrow::before{{
    content:"";display:inline-block;width:24px;height:1px;background:var(--ort-line-strong);
  }}
  .ort-page .ort-h1{{
    font-family:var(--ort-font-display);font-weight:700;
    font-size:clamp(1.7rem, 3.4vw, 2.6rem);
    line-height:1.06;letter-spacing:0;margin:0 0 18px;
    color:var(--ort-ink);
  }}
  .ort-page .ort-h1 .lead{{color:var(--ort-ink);font-weight:600}}
  .ort-page .ort-h1 .accent{{
    color:var(--ort-radar);font-family:var(--ort-font-editorial);
    font-style:italic;font-weight:500;letter-spacing:.005em;
    text-shadow:0 0 18px rgba(166,255,138,.32);
  }}
  .ort-page .ort-sub{{
    font-family:var(--ort-font-body);font-size:0.98rem;line-height:1.6;
    color:var(--ort-ink-mid);margin:0 0 22px;max-width:46ch;
  }}
  .ort-page .ort-ctas{{display:flex;flex-wrap:wrap;gap:10px;margin-top:auto}}
  .ort-page .ort-cta{{
    display:inline-flex;align-items:center;gap:9px;
    padding:11px 18px;border-radius:5px;
    font-family:var(--ort-font-display);font-size:0.78rem;letter-spacing:0.20em;
    text-transform:uppercase;text-decoration:none !important;
    border:1px solid var(--ort-line-strong);white-space:nowrap;
    transition:all .15s ease;
  }}
  .ort-page .ort-cta svg{{width:14px;height:14px}}
  .ort-page .ort-cta--primary{{
    background:rgba(166,255,138,.14);color:var(--ort-radar) !important;
    box-shadow:inset 0 0 0 1px rgba(166,255,138,.18),0 0 14px rgba(166,255,138,.10);
  }}
  .ort-page .ort-cta--primary:hover{{
    background:rgba(166,255,138,.22);
    box-shadow:inset 0 0 0 1px rgba(166,255,138,.30),0 0 22px rgba(166,255,138,.18);
  }}
  .ort-page .ort-cta--ghost{{color:var(--ort-ink) !important;background:transparent}}
  .ort-page .ort-cta--ghost:hover{{color:var(--ort-radar) !important;border-color:var(--ort-line-strong)}}
  .ort-page .ort-cta--amber{{
    color:var(--ort-amber-rec) !important;border-color:rgba(240,160,64,.45);
  }}
  .ort-page .ort-cta--amber:hover{{
    background:rgba(240,160,64,.10);border-color:rgba(240,160,64,.7);
    color:var(--ort-amber-rec) !important;
  }}

  /* ── the radar (CRT scope, premium depth) ─────────────────── */
  .ort-page .ort-radar-wrap{{
    display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0;
  }}
  .ort-page .ort-radar-frame{{
    position:relative;aspect-ratio:1/1;width:100%;max-width:400px;
    border-radius:50%;padding:16px;
    background:linear-gradient(180deg, #1B2125 0%, #0D1216 50%, #161B1F 100%);
    border:1px solid rgba(255,255,255,.05);
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,.06),
      inset 0 -1px 0 rgba(0,0,0,.7),
      0 0 0 1px rgba(0,0,0,.7),
      0 14px 32px rgba(0,0,0,.6),
      0 0 0 8px rgba(0,0,0,.55);
  }}
  .ort-page .ort-radar-frame::before{{
    content:"";position:absolute;top:6px;left:50%;transform:translateX(-50%);
    width:62%;height:14px;border-radius:50%;
    background:radial-gradient(ellipse at 50% 0%, rgba(255,255,255,.10), transparent 70%);
    pointer-events:none;
  }}
  .ort-page .ort-radar-frame::after{{
    content:"";position:absolute;inset:0;border-radius:50%;pointer-events:none;
    background:
      radial-gradient(circle at 50% 0%, transparent 9px, rgba(255,255,255,.06) 10px, transparent 11px),
      radial-gradient(circle at 50% 100%, transparent 9px, rgba(255,255,255,.06) 10px, transparent 11px),
      radial-gradient(circle at 0% 50%, transparent 9px, rgba(255,255,255,.06) 10px, transparent 11px),
      radial-gradient(circle at 100% 50%, transparent 9px, rgba(255,255,255,.06) 10px, transparent 11px);
  }}
  .ort-page .ort-radar-shell{{
    position:relative;width:100%;height:100%;border-radius:50%;
    background:
      radial-gradient(circle at 50% 50%, rgba(166,255,138,.10) 0%, rgba(0,0,0,0) 55%),
      radial-gradient(circle at 50% 50%, #0E1812 0%, #06080A 100%);
    box-shadow:
      0 0 0 1px var(--ort-line-strong),
      0 0 0 4px rgba(0,0,0,.5),
      inset 0 0 70px rgba(0,0,0,.7),
      inset 0 0 24px rgba(166,255,138,.06);
  }}
  .ort-page .ort-radar-shell svg{{width:100%;height:100%;display:block}}
  .ort-page .ort-radar-anno{{
    position:absolute;font-family:var(--ort-font-mono);
    font-size:0.58rem;letter-spacing:0.20em;text-transform:uppercase;
    color:var(--ort-radar-dim);pointer-events:none;line-height:1;
  }}
  .ort-page .ort-radar-anno .k{{color:var(--ort-ink-deep);margin-right:4px}}
  .ort-page .ort-radar-anno .v{{color:var(--ort-radar);font-weight:600}}
  .ort-page .ort-radar-anno--tl{{top:14px;left:22px}}
  .ort-page .ort-radar-anno--tr{{top:14px;right:22px;text-align:right}}
  .ort-page .ort-radar-anno--bl{{bottom:14px;left:22px}}
  .ort-page .ort-radar-anno--br{{bottom:14px;right:22px;text-align:right}}
  .ort-page .ort-radar-caption{{
    margin-top:16px;text-align:center;
    font-family:var(--ort-font-body);font-size:0.78rem;letter-spacing:0.10em;
    text-transform:uppercase;color:var(--ort-ink-dim);max-width:360px;
  }}
  .ort-page .ort-radar-caption b{{color:var(--ort-ink);font-weight:600}}
  .ort-page .ort-sweep{{transform-origin:50% 50%;animation:ort-sweep 5s linear infinite}}

  /* ── Today section ─────────────────────────────────────────── */
  .ort-page .ort-today-head{{
    display:flex;justify-content:space-between;align-items:flex-end;
    margin:30px 0 14px;gap:14px;flex-wrap:wrap;
  }}
  .ort-page .ort-today-head .ort-eyebrow{{margin-bottom:0}}
  .ort-page .ort-today-head h2{{
    font-family:var(--ort-font-editorial);font-style:italic;font-weight:500;
    font-size:1.45rem;line-height:1.2;color:var(--ort-ink);margin:6px 0 0;
    letter-spacing:-0.005em;
  }}
  .ort-page .ort-today-head .ort-pager{{
    font-family:var(--ort-font-mono);font-size:0.62rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);
    display:inline-flex;align-items:center;gap:6px;
  }}
  .ort-page .ort-today-head .ort-nav-arrow{{
    display:inline-flex;align-items:center;justify-content:center;
    width:24px;height:22px;border:1px solid var(--ort-line);
    border-radius:3px;color:var(--ort-ink) !important;
    text-decoration:none !important;
  }}

  .ort-page .ort-today-grid{{
    display:grid;gap:14px;
    grid-template-columns:repeat(4, minmax(0,1fr));
    align-items:stretch;grid-auto-rows:1fr;
  }}
  .ort-page .ort-card{{
    display:flex;flex-direction:column;gap:10px;
    background:linear-gradient(180deg, #0B0F0D 0%, #080C0B 100%);
    border:1px solid var(--ort-line);border-radius:6px;
    padding:16px 16px 14px;position:relative;min-height:230px;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.03);
  }}
  .ort-page .ort-card::before{{
    content:"";position:absolute;top:6px;left:6px;width:10px;height:10px;
    border-top:1px solid var(--ort-radar);border-left:1px solid var(--ort-radar);
    opacity:0.65;
  }}
  .ort-page .ort-card::after{{
    content:"";position:absolute;bottom:6px;right:6px;width:10px;height:10px;
    border-bottom:1px solid var(--ort-radar);border-right:1px solid var(--ort-radar);
    opacity:0.65;
  }}
  .ort-page .ort-card-label{{
    font-family:var(--ort-font-mono);font-size:0.66rem;letter-spacing:0.20em;
    text-transform:uppercase;color:var(--ort-radar);margin:0;
    display:flex;align-items:center;gap:8px;padding-left:14px;
  }}
  .ort-page .ort-card-label .ort-led{{
    display:inline-block;width:5px;height:5px;border-radius:50%;
    background:var(--ort-radar);box-shadow:0 0 4px rgba(166,255,138,.6);
  }}
  .ort-page .ort-card-title{{
    font-family:var(--ort-font-display);font-weight:600;font-size:1.05rem;
    line-height:1.28;color:var(--ort-ink);margin:0;padding-left:14px;
    letter-spacing:0.005em;
  }}
  .ort-page .ort-card-body{{
    font-family:var(--ort-font-mono);font-size:0.76rem;line-height:1.55;
    color:var(--ort-ink-dim);margin:0;padding-left:14px;flex:1;
  }}
  .ort-page .ort-card-foot{{
    margin-top:auto;padding:10px 0 0 14px;
    border-top:1px dashed rgba(166,255,138,.10);
    display:flex;align-items:center;justify-content:flex-end;
  }}
  .ort-page .ort-card-cta{{
    display:inline-flex;align-items:center;gap:6px;
    font-family:var(--ort-font-mono);font-size:0.66rem;letter-spacing:0.16em;
    text-transform:uppercase;color:var(--ort-radar) !important;
    text-decoration:none !important;
  }}
  .ort-page .ort-card-cta svg{{width:11px;height:11px;transition:transform .15s}}
  .ort-page .ort-card-cta:hover svg{{transform:translateX(2px)}}

  .ort-page .ort-screen-foot{{
    margin-top:18px;padding-top:12px;
    border-top:1px dashed var(--ort-line);
    display:flex;justify-content:space-between;align-items:center;
    font-family:var(--ort-font-mono);font-size:0.6rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);
    flex-wrap:wrap;gap:10px;
  }}
  .ort-page .ort-nameplate{{
    margin-top:18px;display:flex;align-items:center;justify-content:space-between;
    font-family:var(--ort-font-mono);font-size:0.58rem;letter-spacing:0.22em;
    text-transform:uppercase;color:rgba(180, 195, 175, 0.4);
    flex-wrap:wrap;gap:8px;
  }}
  .ort-page .ort-nameplate .ort-stencil{{
    display:inline-flex;align-items:center;gap:8px;
    color:rgba(200, 210, 195, 0.5);
  }}
  .ort-page .ort-nameplate .ort-stencil::before{{
    content:"";display:inline-block;width:14px;height:1px;
    background:rgba(180, 195, 175, 0.4);
  }}
  .ort-page .ort-feet{{margin-top:14px;display:flex;justify-content:space-between}}
  .ort-page .ort-feet span{{
    display:inline-block;width:64px;height:6px;border-radius:3px;
    background:linear-gradient(180deg, #1E2428 0%, #0A0D10 100%);
    box-shadow:0 1px 0 rgba(255,255,255,.05) inset,0 0 6px rgba(0,0,0,.5);
  }}

  /* ── animations ───────────────────────────────────────────── */
  @keyframes ort-pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.78)}}}}
  @keyframes ort-pulse-fast{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
  @keyframes ort-sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}

  /* ── responsive ──────────────────────────────────────────── */
  @media (max-width:1180px){{
    .ort-page .ort-screen-body{{grid-template-columns:1fr;gap:24px;padding:24px 8px 18px}}
    .ort-page .ort-radar-frame{{max-width:340px;margin:0 auto}}
  }}
  @media (max-width:720px){{
    .ort-page .ort-chassis{{padding:14px;border-radius:14px}}
    .ort-page .ort-stamp{{font-size:0.46rem;letter-spacing:0.20em;padding:2px 8px}}
    .ort-page .ort-screen-frame{{padding:12px;border-radius:8px}}
    .ort-page .ort-screen{{padding:14px 14px 12px}}
    .ort-page .ort-screen-body{{padding:18px 6px 12px;gap:18px}}
    .ort-page .ort-h1{{font-size:1.45rem;line-height:1.08}}
    .ort-page .ort-eyebrow{{font-size:.55rem;letter-spacing:0.22em;margin-bottom:12px}}
    .ort-page .ort-eyebrow::before{{width:14px}}
    .ort-page .ort-radar-frame{{max-width:300px;padding:12px}}
    .ort-page .ort-radar-anno{{font-size:0.5rem;letter-spacing:0.16em}}
    .ort-page .ort-radar-anno--tl{{left:14px}}
    .ort-page .ort-radar-anno--tr{{right:14px}}
    .ort-page .ort-radar-anno--bl{{left:14px}}
    .ort-page .ort-radar-anno--br{{right:14px}}
    .ort-page .ort-radar-caption{{font-size:0.7rem}}
    .ort-page .ort-today-grid{{grid-template-columns:repeat(2, minmax(0,1fr))}}
    .ort-page .ort-screen-status{{font-size:0.55rem;gap:8px;padding:11px 14px}}
    .ort-page .ort-screen-status .left,
    .ort-page .ort-screen-status .right{{gap:8px}}
    .ort-page .ort-nameplate{{font-size:0.5rem;letter-spacing:0.18em}}
    .ort-page .ort-feet span{{width:48px}}
  }}

  /* very narrow (414 / 393): collapse topnav to 2-row, all 5 tabs
     on a single line at the bottom, brand + status pill on row 1 */
  @media (max-width:480px){{
    .ort-page .ort-topnav{{
      grid-template-columns:1fr auto;
      grid-template-areas:
        "brand action"
        "tabs   tabs";
      column-gap:10px;row-gap:10px;
      padding:10px 14px;
    }}
    .ort-page .ort-brand{{grid-area:brand;min-width:0}}
    .ort-page .ort-nav{{grid-area:tabs;min-width:0;justify-content:space-between;gap:2px;flex-wrap:nowrap}}
    .ort-page .ort-nav-action{{grid-area:action}}
    .ort-page .ort-kicker{{display:none}}
    .ort-page .ort-name{{font-size:0.98rem;letter-spacing:0.18em}}
    .ort-page .ort-brand .ort-mark{{width:30px;height:30px}}
    .ort-page .ort-sys-pill{{padding:5px 9px;font-size:0.55rem;letter-spacing:0.14em}}
    .ort-page .ort-sys-pill .label-wide{{display:none}}
    .ort-page .ort-tab{{padding:6px 6px;gap:5px;font-size:0.6rem;letter-spacing:0.10em;min-width:0}}
    .ort-page .ort-tab .ort-tab-dot{{display:none}}
    .ort-page .ort-h1{{font-size:1.25rem}}
    .ort-page .ort-radar-frame{{max-width:240px}}
    .ort-page .ort-cta{{padding:9px 14px;font-size:0.7rem;letter-spacing:0.16em;gap:8px}}
    .ort-page .ort-radar-anno{{font-size:0.42rem;letter-spacing:0.10em}}
    .ort-page .ort-radar-anno--tl{{left:6px;top:6px}}
    .ort-page .ort-radar-anno--tr{{right:6px;top:6px}}
    .ort-page .ort-radar-anno--bl{{left:6px;bottom:6px}}
    .ort-page .ort-radar-anno--br{{right:6px;bottom:6px}}
    .ort-page .ort-radar-caption{{font-size:0.66rem;margin-top:12px}}
  }}
  @media (max-width:560px){{
    .ort-page .ort-today-grid{{grid-template-columns:1fr}}
  }}
  @media (max-width:380px){{
    .ort-page .ort-radar-frame{{max-width:210px}}
  }}

  /* ── reduced motion (scoped to .ort-* selectors only) ───── */
  @media (prefers-reduced-motion: reduce){{
    .ort-page .ort-sweep,
    .ort-page .ort-name .ort-mark-glow,
    .ort-page .ort-sys-pill .ort-led,
    .ort-page .ort-screen-status .led,
    .ort-page .ort-card-label .ort-led{{
      animation:none !important;opacity:0.85 !important;
    }}
  }}

  /* ── v2.1 NARROW REPAIR · topnav-only selectors (no .ort-page prefix)
     Reason: .ort-topnav / .ort-nav / .ort-tab etc are NOT inside
     `.ort-page` (the chassis lives in render_groq, but the topnav lives
     in render_top_nav() which does NOT emit `.ort-page`). So all
     `.ort-page .ort-topnav*` selectors in the v2.1 CSS block above
     never match. We add unprefixed selectors for the topnav row
     only (topnav is the only place these classes are emitted, so
     it doesn't bleed onto other sections). The rest of the chassis
     CSS keeps the `.ort-page` prefix and is unaffected. */
  .ort-topnav{{
    position:relative;display:grid;
    grid-template-columns:minmax(0,auto) minmax(0,1fr) auto;
    align-items:center;gap:18px;
    padding:14px 22px 12px;
    background:linear-gradient(180deg, rgba(255,255,255,.025), rgba(0,0,0,0));
    border:1px solid rgba(255, 255, 255, 0.06);
    border-radius:8px;
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,.05),
      inset 0 -1px 0 rgba(0,0,0,.55),
      0 6px 16px rgba(0, 0, 0, 0.30);
  }}
  .ort-topnav::after{{
    content:"";position:absolute;left:18px;right:18px;bottom:-1px;height:1px;
    background:linear-gradient(90deg, transparent 0%, var(--ort-line-strong) 50%, transparent 100%);
    pointer-events:none;
  }}
  .ort-brand{{
    display:inline-flex;align-items:center;gap:14px;
    text-decoration:none !important;color:inherit !important;min-width:0;
  }}
  .ort-brand .ort-mark{{
    width:36px;height:36px;flex-shrink:0;color:var(--ort-radar);
    filter:drop-shadow(0 0 5px rgba(166,255,138,.55)) drop-shadow(0 0 16px rgba(166,255,138,.18));
  }}
  .ort-brand .ort-mark svg{{width:100%;height:100%;display:block}}
  .ort-brand-stack{{display:inline-flex;flex-direction:column;line-height:1;gap:5px;min-width:0}}
  .ort-name{{
    font-family:var(--ort-font-display);font-weight:700;font-size:1.18rem;
    letter-spacing:0.20em;color:var(--ort-ink);text-transform:uppercase;
    white-space:nowrap;display:flex;align-items:center;gap:10px;
  }}
  .ort-name .ort-name-dot{{color:var(--ort-radar);font-size:1.1em;line-height:1;padding:0 1px}}
  .ort-name .ort-mark-glow{{
    display:inline-block;width:7px;height:7px;border-radius:50%;
    background:var(--ort-radar);box-shadow:0 0 8px rgba(166,255,138,.7);
    animation:ort-pulse 2.4s ease-in-out infinite;
  }}
  .ort-kicker{{
    font-family:var(--ort-font-mono);font-size:.62rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:32ch;
  }}
  .ort-nav{{
    display:flex;align-items:center;justify-content:center;gap:4px;
    min-width:0;min-height:0;align-self:center;
  }}
  .ort-tab{{
    display:inline-flex;align-items:center;gap:8px;
    padding:9px 14px;border-radius:5px;
    background:transparent !important;color:var(--ort-ink-mid) !important;
    font-family:var(--font-mono);font-size:.72rem;letter-spacing:0.16em;
    text-transform:uppercase;text-decoration:none !important;
    border:1px solid transparent;white-space:nowrap;
    transition:color .18s ease, background .18s ease, border-color .18s ease;
  }}
  .ort-tab:hover{{color:var(--ort-ink) !important;background:rgba(166,255,138,.04) !important}}
  .ort-tab.is-active{{
    color:var(--ort-radar) !important;background:rgba(166,255,138,.10) !important;
    border-color:var(--ort-line-strong) !important;
    box-shadow:inset 0 0 0 1px rgba(166,255,138,.10);
  }}
  .ort-tab .ort-tab-dot{{
    display:inline-block;width:5px;height:5px;border-radius:50%;
    background:transparent;flex-shrink:0;
  }}
  .ort-tab.is-active .ort-tab-dot{{background:var(--ort-radar);box-shadow:0 0 6px rgba(166,255,138,.6)}}
  .ort-nav-action{{
    display:inline-flex;align-items:center;justify-content:flex-end;gap:10px;
    min-height:0;min-width:0;width:auto;height:auto;
  }}
  .ort-sys-pill{{
    display:inline-flex;align-items:center;gap:8px;
    padding:7px 12px;border-radius:999px;
    border:1px solid var(--ort-line-strong);
    background:linear-gradient(180deg, rgba(255,255,255,.025), rgba(0,0,0,0));
    font-family:var(--ort-font-mono);font-size:.6rem;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ort-ink-dim);white-space:nowrap;
  }}
  .ort-sys-pill .ort-led{{
    display:inline-block;width:6px;height:6px;border-radius:50%;
    background:var(--ort-radar);box-shadow:0 0 8px rgba(166,255,138,.7);
    animation:ort-pulse 2.4s ease-in-out infinite;
  }}
  .ort-sys-pill .live{{color:var(--ort-radar)}}

  /* mobile 2-row collapse for the topnav (topnav is the only place
     these classes are emitted, so unprefixed is safe) */
  @media (max-width:480px){{
    .ort-topnav{{
      grid-template-columns:1fr auto;
      grid-template-areas:"brand action" "tabs tabs";
      column-gap:10px;row-gap:10px;padding:10px 14px;
    }}
    .ort-brand{{grid-area:brand;min-width:0}}
    .ort-nav{{grid-area:tabs;min-width:0;justify-content:space-between;gap:2px;flex-wrap:nowrap}}
    .ort-nav-action{{grid-area:action}}
    .ort-kicker{{display:none}}
    .ort-name{{font-size:0.98rem;letter-spacing:0.18em}}
    .ort-brand .ort-mark{{width:30px;height:30px}}
    .ort-sys-pill{{padding:5px 9px;font-size:0.55rem;letter-spacing:0.14em}}
    .ort-tab{{padding:6px 6px;gap:5px;font-size:0.6rem;letter-spacing:0.10em;min-width:0}}
    .ort-tab .ort-tab-dot{{display:none}}
  }}
</style>"""

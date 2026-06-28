"""Theme · central design tokens for OpenRadar.

Headspace-inspired "infusion" palette: soft warm dark base, four gentle
accent colors (sage / coral / lavender / sky), one per major section.
Editorial typography (Newsreader serif for reading, Inter for UI,
JetBrains Mono for tags and meta).

Sidebar-first layout: persistent left navigation lets the user flip
between Azi / News / Learning / Jobs / Prompts without losing context.

Design principle: every pixel must earn its place. No generic gradients,
no AI-flop aesthetics. Calm + premium + a pleasure to read.
"""

# ===== Colors =====
COLORS = {
    # Warm dark base (charcoal, not pure black)
    "bg":         "#1f1d1a",
    "bg_sidebar": "#161310",   # slightly darker — sidebar contrast
    "surface":    "#2a2723",
    "surface_2":  "#34302a",
    "border":     "#3a3530",
    "border_strong": "#4a443d",

    # Text
    "text":       "#f4ede0",
    "text_2":     "#d4cebf",
    "muted":      "#8a8478",
    "muted_2":    "#6a6458",

    # Accent "infusion"
    "sage":       "#a8c0ae",   # learning + jobs + azi
    "coral":      "#e8a598",   # news
    "lavender":   "#b5a8c9",   # prompts / apply
    "sky":        "#a5c5d4",   # tools / repos

    # Semantic
    "success":    "#9bb88a",
    "warn":       "#d9b87a",
    "danger":     "#c98a82",
}


SECTION_ACCENT = {
    "azi":      "sage",
    "news":     "coral",
    "learning": "sage",
    "jobs":     "sage",
    "prompts":  "lavender",
}


# ===== Typography =====
FONTS = {
    "serif":  "'Newsreader', 'Spectral', Georgia, serif",
    "sans":   "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono":   "'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace",
}


# ===== Spacing scale (px) =====
SPACING = {
    "xs":  4,
    "sm":  8,
    "md":  12,
    "lg":  16,
    "xl":  24,
    "2xl": 32,
    "3xl": 48,
    "4xl": 64,
    "5xl": 96,
}


# ===== Motion =====
MOTION = {
    "ease":         "cubic-bezier(0.16, 1, 0.3, 1)",
    "ease_soft":    "cubic-bezier(0.4, 0, 0.2, 1)",
    "dur_fast":     "150ms",
    "dur_base":     "240ms",
    "dur_slow":     "400ms",
    "dur_reveal":   "600ms",
}


# ===== CSS =====
def render_css() -> str:
    c = COLORS
    f = FONTS
    m = MOTION

    return f"""<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {{
    --bg: {c['bg']};
    --bg-sidebar: {c['bg_sidebar']};
    --surface: {c['surface']};
    --surface-2: {c['surface_2']};
    --border: {c['border']};
    --border-strong: {c['border_strong']};

    --text: {c['text']};
    --text-2: {c['text_2']};
    --muted: {c['muted']};
    --muted-2: {c['muted_2']};

    --sage: {c['sage']};
    --coral: {c['coral']};
    --lavender: {c['lavender']};
    --sky: {c['sky']};

    --ease: {m['ease']};
    --ease-soft: {m['ease_soft']};
    --dur-fast: {m['dur_fast']};
    --dur-base: {m['dur_base']};
    --dur-slow: {m['dur_slow']};
    --dur-reveal: {m['dur_reveal']};
  }}

  html {{ scroll-behavior: smooth; }}
  * {{ box-sizing: border-box; }}

  /* App background */
  .stApp {{
    background-color: var(--bg);
    color: var(--text);
    font-family: {f['sans']};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  section.main > div {{
    padding-top: 0;
    padding-bottom: 4rem;
    max-width: 920px;
  }}

  /* Typography */
  h1, h2, h3, h4, h5, h6 {{
    font-family: {f['serif']};
    font-weight: 400;
    letter-spacing: -0.01em;
    color: var(--text);
    margin-top: 0;
  }}
  h1 {{ font-weight: 300; letter-spacing: -0.02em; }}
  h2 {{ color: var(--text); font-size: 1.85rem; line-height: 1.25; }}
  h3 {{ font-size: 1.2rem; }}
  h4 {{ font-size: 1rem; }}

  p, li {{ color: var(--text-2); line-height: 1.65; }}

  /* Caption */
  .stCaption, [data-testid="stCaption"] {{
    color: var(--muted) !important;
    font-family: {f['mono']};
    font-size: 0.72rem;
    letter-spacing: 0.02em;
  }}

  /* Sidebar styling */
  section[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
  }}
  section[data-testid="stSidebar"] > div {{
    padding-top: 1.5rem;
    padding-left: 0;
    padding-right: 0;
  }}

  /* Sidebar nav items — styled as full-width buttons */
  section[data-testid="stSidebar"] .stRadio {{
    margin-top: 0;
  }}
  section[data-testid="stSidebar"] .stRadio > label {{
    display: none;
  }}
  section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
    display: none;
  }}
  section[data-testid="stSidebar"] [role="radiogroup"] {{
    gap: 2px;
  }}
  section[data-testid="stSidebar"] [role="radio"] {{
    background-color: transparent;
    border: none;
    color: var(--muted);
    padding: 0.65rem 1.1rem;
    font-family: {f['sans']};
    font-size: 0.92rem;
    font-weight: 400;
    border-radius: 8px;
    margin: 0 0.6rem;
    cursor: pointer;
    transition: background-color var(--dur-fast) var(--ease),
                color var(--dur-fast) var(--ease);
    width: calc(100% - 1.2rem);
  }}
  section[data-testid="stSidebar"] [role="radio"]:hover {{
    background-color: rgba(255, 255, 255, 0.04);
    color: var(--text);
  }}
  section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {{
    background-color: rgba(168, 192, 174, 0.12);
    color: var(--sage);
  }}

  /* Sidebar branding block */
  .sidebar-brand {{
    padding: 0.5rem 1.1rem 1.5rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }}
  .brand-row {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 0.3rem;
  }}
  .radar-icon {{
    flex-shrink: 0;
  }}
  .sidebar-brand h2 {{
    font-family: {f['serif']};
    font-size: 1.3rem;
    font-weight: 400;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.01em;
  }}
  .sidebar-brand p {{
    font-family: {f['mono']};
    font-size: 0.66rem;
    color: var(--muted);
    margin: 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}

  /* Sidebar meta (date, status) */
  .sidebar-meta {{
    padding: 1rem 1.1rem 1.5rem;
    margin-top: 1rem;
    border-top: 1px solid var(--border);
    font-family: {f['mono']};
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.04em;
  }}

  /* Cards */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.4rem !important;
    transition: transform var(--dur-base) var(--ease),
                border-color var(--dur-base) var(--ease),
                box-shadow var(--dur-base) var(--ease);
  }}
  [data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-2px);
    border-color: var(--border-strong) !important;
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.4);
  }}

  /* Buttons */
  .stButton > button {{
    background-color: transparent;
    color: var(--text-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    font-family: {f['mono']};
    font-size: 0.74rem;
    letter-spacing: 0.04em;
    padding: 0.45rem 0.9rem;
    transition: all var(--dur-fast) var(--ease);
  }}
  .stButton > button:hover {{
    background-color: var(--surface-2);
    border-color: var(--border-strong);
    color: var(--text);
  }}

  /* Links */
  a {{ color: var(--coral) !important; text-decoration: none; transition: opacity var(--dur-fast); }}
  a:hover {{ opacity: 0.75; }}

  /* Code blocks */
  code, pre {{
    background-color: var(--surface-2) !important;
    color: var(--sky) !important;
    font-family: {f['mono']} !important;
    font-size: 0.85em;
    padding: 0.1em 0.35em;
    border-radius: 4px;
  }}

  /* Reveal animation */
  @keyframes fade-up {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .reveal {{ animation: fade-up var(--dur-reveal) var(--ease) both; }}
  .reveal-1 {{ animation-delay: 0ms; }}
  .reveal-2 {{ animation-delay: 80ms; }}
  .reveal-3 {{ animation-delay: 160ms; }}
  .reveal-4 {{ animation-delay: 240ms; }}

  /* Pulse for "new" indicators */
  @keyframes pulse-soft {{
    0%, 100% {{ opacity: 0.5; }}
    50%      {{ opacity: 1; }}
  }}
  .pulse-dot {{
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--sage);
    animation: pulse-soft 2.4s var(--ease-soft) infinite;
    margin-right: 6px;
    vertical-align: middle;
  }}

  /* Section header */
  .section-header {{
    margin-bottom: 2rem;
  }}
  .section-header h1 {{
    font-size: 2.2rem;
    margin: 0 0 0.4rem;
    line-height: 1.15;
  }}
  .section-header .caption {{
    font-family: {f['serif']};
    font-style: italic;
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
    max-width: 540px;
  }}

  /* Subsection labels */
  .subsection-label {{
    font-family: {f['mono']};
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 1rem;
    color: var(--muted);
  }}

  /* Hide Streamlit chrome */
  #MainMenu, footer {{ visibility: hidden; }}
  .viewerBadge_link__qRIco {{ display: none !important; }}
  header[data-testid="stHeader"] {{ display: none; }}

  /* Force sidebar visible — workaround for Streamlit auto-collapse on smaller
     screens combined with hidden header (no hamburger to re-open it). The
     initial_sidebar_state="expanded" isn't enough on narrow viewports. */
  section[data-testid="stSidebar"] {{
    display: block !important;
    visibility: visible !important;
    transform: translateX(0) !important;
    min-width: 240px !important;
  }}
  section[data-testid="stSidebar"] > div:first-child {{
    transform: translateX(0) !important;
  }}
</style>"""
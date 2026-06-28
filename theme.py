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

  /* App background — subtle tactical grid (graph-paper feel) */
  .stApp {{
    background-color: var(--bg);
    background-image:
      linear-gradient(to right, rgba(168, 192, 174, 0.025) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(168, 192, 174, 0.025) 1px, transparent 1px);
    background-size: 24px 24px;
    background-attachment: fixed;
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

  /* Sidebar nav items — tactical flat style with left-border accent */
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
    gap: 0;
  }}
  section[data-testid="stSidebar"] [role="radio"] {{
    background-color: transparent;
    border: none;
    border-left: 2px solid transparent;
    color: var(--muted);
    padding: 0.7rem 1rem 0.7rem 1.1rem;
    font-family: {f['mono']};
    font-size: 0.78rem;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: 0;
    margin: 0;
    cursor: pointer;
    transition: background-color var(--dur-fast) var(--ease),
                color var(--dur-fast) var(--ease),
                border-left-color var(--dur-fast) var(--ease);
  }}
  section[data-testid="stSidebar"] [role="radio"]:hover {{
    background-color: rgba(168, 192, 174, 0.05);
    color: var(--text);
    border-left-color: var(--border-strong);
  }}
  section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {{
    background-color: rgba(168, 192, 174, 0.1);
    color: var(--sage);
    border-left-color: var(--sage);
  }}

  /* Sidebar status bar (top tray) */
  .sb-statusbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.1rem 0.8rem;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
    font-family: {f['mono']};
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .sb-statusbar .sb-status-name {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--text-2);
  }}
  .sb-statusbar .sb-version {{
    color: var(--muted-2);
  }}

  /* Sidebar frame — generic boxed container with label */
  .sb-frame {{
    background-color: var(--surface);
    border: 1px solid var(--border-strong);
    border-radius: 2px;
    padding: 0.7rem 0.9rem;
    margin: 0 0.8rem 0.9rem;
    font-family: {f['mono']};
    font-size: 0.7rem;
    color: var(--text-2);
    letter-spacing: 0.03em;
    line-height: 1.55;
  }}
  .sb-frame-label {{
    font-family: {f['mono']};
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 0.4rem 0.9rem;
    padding-left: 0;
  }}

  /* Brand block — crosshair + name + tagline */
  .sb-brand {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.2rem 0;
  }}
  .sb-brand .crosshair {{
    flex-shrink: 0;
  }}
  .sb-brand h2 {{
    font-family: {f['mono']};
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text);
    margin: 0;
  }}
  .sb-brand .tagline {{
    font-family: {f['mono']};
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.45rem;
    padding-top: 0.45rem;
    border-top: 1px solid var(--border);
  }}

  /* Telemetry frame — coordinate readouts */
  .sb-telemetry-row {{
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
  }}
  .sb-telemetry-row .k {{
    color: var(--muted);
  }}
  .sb-telemetry-row .v {{
    color: var(--text-2);
  }}
  .sb-telemetry-divider {{
    height: 1px;
    background: var(--border);
    margin: 0.45rem 0;
  }}
  .status-dot {{
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--sage);
    margin-right: 5px;
    vertical-align: middle;
    animation: pulse-soft 2.4s var(--ease-soft) infinite;
    box-shadow: 0 0 6px rgba(168, 192, 174, 0.5);
  }}

  /* Sidebar footer */
  .sb-footer {{
    padding: 0.9rem 1.1rem;
    border-top: 1px solid var(--border);
    font-family: {f['mono']};
    font-size: 0.62rem;
    color: var(--muted-2);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: center;
  }}

  /* Cards — sharp tactical corners */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--surface);
    border: 1px solid var(--border-strong) !important;
    border-radius: 2px !important;
    padding: 1.2rem 1.4rem !important;
    transition: border-color var(--dur-base) var(--ease),
                background-color var(--dur-base) var(--ease);
  }}
  [data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: var(--sage) !important;
    background-color: var(--surface-2);
  }}

  /* Buttons — sharp tactical corners */
  .stButton > button {{
    background-color: transparent;
    color: var(--text-2);
    border: 1px solid var(--border-strong);
    border-radius: 2px;
    font-family: {f['mono']};
    font-size: 0.74rem;
    letter-spacing: 0.04em;
    padding: 0.45rem 0.9rem;
    transition: all var(--dur-fast) var(--ease);
  }}
  .stButton > button:hover {{
    background-color: var(--surface-2);
    border-color: var(--sage);
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

  /* Section header — bracket markers via CSS pseudo */
  .section-header {{
    margin-bottom: 2rem;
  }}
  .section-header h1 {{
    font-size: 2.2rem;
    margin: 0 0 0.4rem;
    line-height: 1.15;
  }}
  .section-header h1::before {{
    content: "[ ";
    font-family: {f['mono']};
    color: var(--muted);
    font-weight: 300;
    font-size: 0.7em;
    vertical-align: 0.25em;
    margin-right: 0.2em;
    letter-spacing: 0;
  }}
  .section-header h1::after {{
    content: " ]";
    font-family: {f['mono']};
    color: var(--muted);
    font-weight: 300;
    font-size: 0.7em;
    vertical-align: 0.25em;
    margin-left: 0.2em;
    letter-spacing: 0;
  }}
  .section-header .caption {{
    font-family: {f['serif']};
    font-style: italic;
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
    max-width: 540px;
  }}

  /* Live badge — pulsing signal indicator */
  .live-badge {{
    display: inline-flex;
    align-items: center;
    font-family: {f['mono']};
    font-size: 0.65rem;
    color: var(--sage);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.18rem 0.55rem;
    border: 1px solid var(--sage);
    border-radius: 2px;
    background: rgba(168, 192, 174, 0.06);
    margin-left: 0.8rem;
    vertical-align: middle;
  }}
  .live-badge .status-dot {{
    width: 6px;
    height: 6px;
    margin-right: 6px;
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
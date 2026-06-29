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
    "serif":      "'Newsreader', 'Spectral', Georgia, serif",
    "sans":       "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "mono":       "'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace",  # data, code
    "mono_tactical": "'Space Mono', 'JetBrains Mono', 'SF Mono', monospace",  # tactical UI
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
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Mono:wght@400;700&display=swap');

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

    --mono-tac: {f['mono_tactical']};

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

  /* Sidebar nav items — REAL button boxes with full borders + fill on active */
  section[data-testid="stSidebar"] .stRadio {{
    margin-top: 0;
  }}
  section[data-testid="stSidebar"] .stRadio > label {{
    display: none;
  }}
  section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
    display: none;
  }}

  /* Aggressively hide ALL Streamlit radio visual remnants (input, dot, svg) */
  section[data-testid="stSidebar"] [role="radio"] input[type="radio"],
  section[data-testid="stSidebar"] [role="radio"] > div:not(label),
  section[data-testid="stSidebar"] [role="radio"] label > div,
  section[data-testid="stSidebar"] [role="radio"] label > svg,
  section[data-testid="stSidebar"] [role="radio"] svg,
  section[data-testid="stSidebar"] [role="radio"] *::before,
  section[data-testid="stSidebar"] [role="radio"] *::after {{
    display: none !important;
    content: none !important;
  }}

  section[data-testid="stSidebar"] [role="radiogroup"] {{
    gap: 6px;
    padding: 0.25rem 0;
  }}

  section[data-testid="stSidebar"] [role="radio"] {{
    position: relative;
    display: flex !important;
    align-items: center;
    gap: 0.7rem;
    width: calc(100% - 1rem);
    min-height: 44px;
    padding: 0.85rem 1rem 0.85rem 1rem;
    background-color: var(--surface);
    border: 1px solid var(--border-strong);
    border-left: 3px solid transparent;
    border-radius: 2px;
    color: var(--muted);
    font-family: var(--mono-tac);
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0.5rem;
    cursor: pointer;
    transition: background-color var(--dur-fast) var(--ease),
                color var(--dur-fast) var(--ease),
                border-color var(--dur-fast) var(--ease),
                border-left-color var(--dur-fast) var(--ease),
                transform var(--dur-fast) var(--ease),
                box-shadow var(--dur-fast) var(--ease);
  }}
  section[data-testid="stSidebar"] [role="radio"]:hover {{
    background-color: var(--surface-2);
    color: var(--text);
    border-color: var(--sage);
    border-left-color: var(--sage);
    transform: translateX(3px);
    box-shadow: 0 2px 8px -2px rgba(168, 192, 174, 0.3);
  }}
  section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {{
    background-color: var(--sage);
    color: var(--bg);
    border-color: var(--sage);
    border-left-color: var(--sage);
    font-weight: 700;
    box-shadow: 0 0 16px -2px rgba(168, 192, 174, 0.4);
  }}
  section[data-testid="stSidebar"] [role="radio"][aria-checked="true"]:hover {{
    transform: none;
    box-shadow: 0 0 20px -2px rgba(168, 192, 174, 0.5);
  }}

  /* Action buttons inside [ ACTIONS ] frame — full-width tactical */
  .sb-action {{
    width: 100%;
    margin-bottom: 0.4rem;
  }}
  .sb-action:last-child {{ margin-bottom: 0; }}
  .sb-action .stButton > button {{
    width: 100%;
    text-align: left;
    padding: 0.55rem 0.8rem;
    font-family: var(--mono-tac);
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background-color: var(--surface-2);
    color: var(--text-2);
    border: 1px solid var(--border);
    border-radius: 2px;
    transition: all var(--dur-fast) var(--ease);
  }}
  .sb-action .stButton > button:hover {{
    background-color: var(--sage);
    border-color: var(--sage);
    color: var(--bg);
  }}
  .sb-action .stButton > button:active {{
    transform: scale(0.98);
  }}

  /* Sidebar status bar (top tray) */
  .sb-statusbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1rem 0.75rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
    font-family: var(--mono-tac);
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
    padding: 0.75rem 0.875rem;
    margin: 0 0.75rem 0.75rem;
    font-family: var(--mono-tac);
    font-size: 0.7rem;
    color: var(--text-2);
    letter-spacing: 0.03em;
    line-height: 1.55;
    transition: border-color var(--dur-fast) var(--ease),
                background-color var(--dur-fast) var(--ease);
  }}
  .sb-frame:hover {{
    border-color: var(--sage);
    background-color: rgba(168, 192, 174, 0.04);
  }}
  .sb-frame-label {{
    font-family: var(--mono-tac);
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 0.4rem 0.875rem;
    padding-left: 0;
    transition: color var(--dur-fast) var(--ease);
  }}
  .sb-frame-label:hover {{ color: var(--sage); }}
  .sb-frame-label .bracket {{ color: var(--muted-2); }}

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
    font-family: var(--mono-tac);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text);
    margin: 0;
  }}
  .sb-brand .tagline {{
    font-family: var(--mono-tac);
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
    padding: 0.875rem 1rem;
    border-top: 1px solid var(--border);
    font-family: var(--mono-tac);
    font-size: 0.62rem;
    color: var(--muted-2);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: center;
    transition: color var(--dur-base) var(--ease),
                letter-spacing var(--dur-base) var(--ease);
    cursor: default;
  }}
  .sb-footer:hover {{
    color: var(--sage);
    letter-spacing: 0.2em;
  }}

  /* Cards — sharp tactical corners with top accent line + hover lift */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--surface);
    border: 1px solid var(--border-strong) !important;
    border-top: 2px solid var(--sage) !important;
    border-radius: 2px !important;
    padding: 1.1rem 1.4rem !important;
    transition: border-color var(--dur-base) var(--ease),
                border-top-color var(--dur-base) var(--ease),
                background-color var(--dur-base) var(--ease),
                transform var(--dur-base) var(--ease);
  }}
  [data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: var(--sage) !important;
    border-top-color: var(--sage) !important;
    background-color: rgba(168, 192, 174, 0.05);
    transform: scale(1.008);
  }}

  /* Card accent color variants — top border tint */
  .card-accent-coral [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stVerticalBlockBorderWrapper"].accent-coral {{
    border-top-color: var(--coral) !important;
  }}
  .card-accent-sky [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stVerticalBlockBorderWrapper"].accent-sky {{
    border-top-color: var(--sky) !important;
  }}
  .card-accent-sage [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stVerticalBlockBorderWrapper"].accent-sage {{
    border-top-color: var(--sage) !important;
  }}

  /* Card mono label — tactical header inside card */
  .card-label {{
    font-family: var(--mono-tac);
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: -0.4rem 0 0.65rem;
    color: var(--sage);
  }}
  .card-label.coral {{ color: var(--coral); }}
  .card-label.sky {{ color: var(--sky); }}
  .card-label.lavender {{ color: var(--lavender); }}

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

  /* ============================================
     Background animations — radar pulse + scan line
     ============================================ */
  @keyframes radar-pulse {{
    0%   {{ transform: scale(0.15); opacity: 0.55; }}
    100% {{ transform: scale(2.2);  opacity: 0; }}
  }}
  @keyframes scan-down {{
    0%   {{ transform: translateY(-3vh); opacity: 0; }}
    10%  {{ opacity: 0.55; }}
    90%  {{ opacity: 0.55; }}
    100% {{ transform: translateY(103vh); opacity: 0; }}
  }}

  /* Radar pulse rings — fixed overlay from bottom-right corner */
  .bg-radar {{
    position: fixed;
    bottom: -30vh;
    right: -30vw;
    width: 80vh;
    height: 80vh;
    pointer-events: none;
    z-index: 0;
  }}
  .bg-radar::before,
  .bg-radar::after {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(168, 192, 174, 0.35);
    animation: radar-pulse 6s linear infinite;
  }}
  .bg-radar::after {{ animation-delay: 3s; }}

  /* Vertical scan line — sweeps top to bottom */
  .bg-scan {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(to right,
      transparent 0%,
      rgba(168, 192, 174, 0.45) 50%,
      transparent 100%);
    animation: scan-down 12s linear infinite;
    pointer-events: none;
    z-index: 0;
  }}

  /* Respect reduced-motion preference */
  @media (prefers-reduced-motion: reduce) {{
    .bg-radar::before,
    .bg-radar::after,
    .bg-scan {{
      animation: none !important;
    }}
  }}

  /* ============================================
     Sidebar hacker upgrades
     ============================================ */

  /* Crosshair cluster (3x3 targeting feel) */
  .sb-cluster {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2px;
    justify-items: center;
    align-items: center;
    margin: 0 auto 0.55rem;
    width: 70%;
    font-family: var(--mono-tac);
    color: var(--sage);
    font-size: 0.7rem;
    line-height: 1;
  }}
  .sb-cluster .c {{
    opacity: 0.45;
    transition: opacity var(--dur-fast) var(--ease),
                transform var(--dur-slow) var(--ease);
  }}
  .sb-cluster:hover .c {{ opacity: 0.85; }}
  .sb-cluster .c.center {{
    opacity: 1;
    font-size: 0.95rem;
    grid-column: 2;
    grid-row: 2;
    transition: opacity var(--dur-fast) var(--ease),
                transform var(--dur-slow) var(--ease);
  }}
  .sb-cluster:hover .c.center {{ transform: rotate(45deg); }}

  /* ASCII cache bar in TELEMETRY */
  .sb-cache-bar {{
    font-family: var(--mono-tac);
    font-size: 0.7rem;
    letter-spacing: 0;
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }}
  .sb-cache-bar .bar {{
    flex: 1;
    color: var(--sage);
    letter-spacing: 0.1em;
  }}
  .sb-cache-bar .bar .empty {{ color: var(--muted-2); }}
  .sb-cache-bar .pct {{ color: var(--muted); min-width: 2.5rem; text-align: right; }}

  /* Activity log rows in [ ACTIVITY ] frame */
  .sb-activity-row {{
    display: grid;
    grid-template-columns: auto 1fr auto auto;
    gap: 0.5rem;
    align-items: baseline;
    font-family: var(--mono-tac);
    font-size: 0.6rem;
    line-height: 1.7;
    color: var(--text-2);
    padding: 0.1rem 0.3rem;
    margin: 0 -0.3rem;
    border-radius: 2px;
    transition: background-color var(--dur-fast) var(--ease);
  }}
  .sb-activity-row:hover {{
    background-color: rgba(168, 192, 174, 0.08);
  }}
  .sb-activity-row .time {{ color: var(--muted); flex-shrink: 0; }}
  .sb-activity-row .op {{
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .sb-activity-row .dur {{
    color: var(--sage);
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
  }}
  .sb-activity-row .status {{
    flex-shrink: 0;
    font-size: 0.7rem;
    width: 0.7rem;
    text-align: center;
  }}
  .sb-activity-row .status-ok {{ color: var(--sage); }}
  .sb-activity-row .status-running {{
    color: var(--warn);
    animation: pulse-soft 1.5s var(--ease-soft) infinite;
  }}
  .sb-activity-row .status-error {{ color: var(--danger); }}

  /* Frame counter (e.g., '12 OPS' in label) */
  .sb-counter {{
    color: var(--sage);
    margin-left: 0.4rem;
  }}

  /* Section header — bracket markers as inline spans (adjacent to title) */
  .section-header {{
    margin-bottom: 2rem;
  }}
  .section-header h1 {{
    font-size: 2.2rem;
    margin: 0 0 0.4rem;
    line-height: 1.15;
  }}
  .section-header h1 .bracket {{
    font-family: var(--mono-tac);
    color: var(--muted);
    font-weight: 300;
    font-size: 0.7em;
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
    font-family: var(--mono-tac);
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

  /* ============================================
     Loading-screen tip terminal (Fallout vibe)
     ============================================ */
  .tips-terminal {{
    position: relative;
    margin: 0 0 1.5rem;
    padding: 0.9rem 1.1rem 0.95rem;
    background: rgba(124, 255, 155, 0.025);
    border: 1px solid rgba(124, 255, 155, 0.18);
    border-left: 2px solid var(--sage);
    font-family: {f['mono']};
    color: #7CFF9B;
    min-height: 100px;
    overflow: hidden;
  }}
  /* Corner brackets around the [ TIPS ] label */
  .tips-terminal::before {{
    content: "┌──[ TIPS · LOADING SCREEN ]──┐";
    position: absolute;
    top: -0.05rem;
    left: 0.9rem;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    color: rgba(124, 255, 155, 0.55);
    background: var(--bg);
    padding: 0 0.4rem;
  }}
  .tips-terminal::after {{
    content: "└────────────┘";
    position: absolute;
    bottom: 0.05rem;
    left: 0.9rem;
    right: 0.9rem;
    font-size: 0.58rem;
    letter-spacing: 0.05em;
    color: rgba(124, 255, 155, 0.25);
  }}

  /* Header row inside the tips box */
  .tips-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.7rem;
    font-size: 0.62rem;
    color: rgba(124, 255, 155, 0.55);
    letter-spacing: 0.1em;
  }}
  .tips-header .prefix {{ color: var(--sage); }}
  .tips-header .blinker {{
    display: inline-block;
    width: 7px;
    height: 11px;
    background: var(--sage);
    margin-left: 4px;
    vertical-align: -2px;
    animation: tips-blink 1.1s steps(1) infinite;
  }}

  /* Category badge */
  .tips-cat {{
    display: inline-block;
    padding: 1px 6px;
    margin-right: 6px;
    background: rgba(124, 255, 155, 0.12);
    border: 1px solid rgba(124, 255, 155, 0.35);
    border-radius: 1px;
    color: var(--sage);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
  }}
  .tips-cat.LINUX,    .tips-cat.SHELL {{ color: #a8d9b3; border-color: rgba(168, 217, 179, 0.5); background: rgba(168, 217, 179, 0.08); }}
  .tips-cat.RSI,      .tips-cat.HEALTH {{ color: #d4b8c8; border-color: rgba(212, 184, 200, 0.5); background: rgba(212, 184, 200, 0.08); }}
  .tips-cat.INFRA,    .tips-cat.DEVOPS {{ color: #9bb8d4; border-color: rgba(155, 184, 212, 0.5); background: rgba(155, 184, 212, 0.08); }}
  .tips-cat.BEGINNER, .tips-cat.JUNIOR {{ color: #e8c994; border-color: rgba(232, 201, 148, 0.5); background: rgba(232, 201, 148, 0.08); }}
  .tips-cat.EXPERT,   .tips-cat.PRO    {{ color: #d49898; border-color: rgba(212, 152, 152, 0.5); background: rgba(212, 152, 152, 0.08); }}
  .tips-cat.AI,       .tips-cat.PROMPT {{ color: #b8a4d9; border-color: rgba(184, 164, 217, 0.5); background: rgba(184, 164, 217, 0.08); }}
  .tips-cat.CAREER,   .tips-cat.JOBS   {{ color: #c5d97c; border-color: rgba(197, 217, 124, 0.5); background: rgba(197, 217, 124, 0.08); }}
  .tips-cat.WORKFLOW              {{ color: #98c5b8; border-color: rgba(152, 197, 184, 0.5); background: rgba(152, 197, 184, 0.08); }}

  /* Cycling tip body lines */
  .tip-slot {{
    position: relative;
    min-height: 56px;
  }}
  .tip-line {{
    position: absolute;
    inset: 0;
    opacity: 0;
    transform: translateY(6px);
    font-size: 0.78rem;
    line-height: 1.5;
    color: #9be3ad;
    letter-spacing: 0.02em;
    animation: tip-cycle 20s linear infinite;
  }}
  .tip-line .body {{
    overflow: hidden;
    white-space: nowrap;
    border-right: 0;
    animation: tip-type 5s steps(60, end) infinite;
  }}
  .tip-line .body.wrapped {{
    white-space: normal;
    animation: tip-fade 5s ease infinite;
    clip-path: none;
  }}
  .tip-line .attrib {{
    display: block;
    margin-top: 0.4rem;
    font-size: 0.6rem;
    color: rgba(124, 255, 155, 0.4);
    letter-spacing: 0.08em;
  }}

  /* Cycle per tip = 25% of 20s = 5s. Visible window ~4.4s with 0.3s fade in/out. */
  @keyframes tip-cycle {{
    0%     {{ opacity: 0; transform: translateY(6px); }}
    1.5%   {{ opacity: 1; transform: translateY(0); }}
    23.5%  {{ opacity: 1; transform: translateY(0); }}
    25%    {{ opacity: 0; transform: translateY(-6px); }}
    100%   {{ opacity: 0; }}
  }}
  /* Typewriter reveal (clip-path on first line) — runs each 5s slot */
  @keyframes tip-type {{
    0%   {{ clip-path: inset(0 100% 0 0); }}
    8%   {{ clip-path: inset(0 0% 0 0); }}
    90%  {{ clip-path: inset(0 0% 0 0); }}
    100% {{ clip-path: inset(0 100% 0 0); }}
  }}
  /* Fade for wrapped/2-line tips */
  @keyframes tip-fade {{
    0%   {{ opacity: 0; }}
    8%   {{ opacity: 1; }}
    90%  {{ opacity: 1; }}
    100% {{ opacity: 0; }}
  }}
  /* Cursor blink */
  @keyframes tips-blink {{
    0%, 49%  {{ opacity: 1; }}
    50%, 100%{{ opacity: 0; }}
  }}

  /* Stagger delays — 4 tips, each owns a 5s slot of the 20s loop.
     Negative delay = animation already partway through at t=0.
     Math: tip N is at delay -20 + (N * 5) so its visible window is t=(N-1)*5..N*5. */
  .tip-line:nth-child(1)  {{ animation-delay: 0s; }}
  .tip-line:nth-child(2)  {{ animation-delay: -15s; }}
  .tip-line:nth-child(3)  {{ animation-delay: -10s; }}
  .tip-line:nth-child(4)  {{ animation-delay: -5s; }}

  /* Responsive — collapse tip box on mobile */
  @media (max-width: 640px) {{
    .tips-terminal {{
      font-size: 0.7rem;
      min-height: 80px;
      padding: 0.7rem 0.8rem 0.75rem;
    }}
    .tip-line {{
      font-size: 0.7rem;
    }}
  }}

  /* Respect reduced motion */
  @media (prefers-reduced-motion: reduce) {{
    .tip-line, .tip-line .body, .tip-line .body.wrapped, .tips-header .blinker {{
      animation: none !important;
      opacity: 1 !important;
      transform: none !important;
      clip-path: none !important;
    }}
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

  /* ============================================
     Responsive breakpoints
     ============================================ */

  /* Tablet: ≤1024px — tighter spacing, smaller sidebar */
  @media (max-width: 1024px) {{
    section[data-testid="stSidebar"] {{
      min-width: 220px !important;
    }}
    section.main > div {{
      max-width: 720px;
      padding-left: 1.5rem;
      padding-right: 1.5rem;
    }}
    .bg-radar {{
      width: 60vh;
      height: 60vh;
      bottom: -28vh;
      right: -28vw;
    }}
    .section-header h1 {{
      font-size: 1.9rem;
    }}
  }}

  /* Mobile: ≤640px — compact nav, hide secondary frames */
  @media (max-width: 640px) {{
    section[data-testid="stSidebar"] {{
      min-width: 180px !important;
    }}
    section.main > div {{
      max-width: 100%;
      padding-left: 1rem;
      padding-right: 1rem;
    }}
    .section-header h1 {{
      font-size: 1.5rem;
    }}
    .section-header h1 .bracket {{
      font-size: 0.6em;
    }}
    .stApp {{
      background-size: 16px 16px;
    }}
    .bg-radar {{
      width: 50vh;
      height: 50vh;
      bottom: -25vh;
      right: -25vw;
    }}
    .bg-scan {{
      animation-duration: 18s;
    }}
    /* Hide secondary sidebar frames on mobile (essential nav stays) */
    .sb-frame-label[data-frame="telemetry"],
    .sb-frame-label[data-frame="telemetry"] + .sb-frame,
    .sb-frame-label[data-frame="activity"],
    .sb-frame-label[data-frame="activity"] + .sb-frame {{
      display: none;
    }}
    /* Tighter spacing */
    .sb-frame {{
      padding: 0.6rem 0.7rem;
      margin: 0 0.5rem 0.6rem;
    }}
    .sb-frame-label {{
      margin: 0 0 0.3rem 0.7rem;
    }}
    .sb-footer {{
      font-size: 0.55rem;
      padding: 0.6rem 0.8rem;
      letter-spacing: 0.05em;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
      padding: 0.9rem 1.1rem !important;
    }}
    .card-label {{
      font-size: 0.58rem;
    }}
    .column-header {{
      font-size: 1.2rem !important;
    }}
  }}
</style>"""
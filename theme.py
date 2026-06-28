"""Theme · central design tokens for Ziarul Digital.

Headspace-inspired "infusion" palette: soft warm dark base, four gentle
accent colors, one per major section. Editorial serif for reading,
clean sans for UI, mono for tags/meta.

The render_css() function returns a self-contained <style> block that
Streamlit injects via st.markdown. It encodes:
  - color tokens (--bg, --surface, --text, --muted, --sage, --coral,
    --lavender, --sky)
  - typography stacks
  - spacing scale
  - motion tokens (durations + easings)
  - per-tab accent colors via :nth-child selectors
  - card hover lift, fade-up reveal keyframes, smooth scroll, shimmer

Design principle: every pixel must earn its place. No generic gradients,
no AI-flop aesthetics. Calm + premium + a pleasure to read.
"""

# ===== Colors =====
COLORS = {
    # Warm dark base (charcoal, not pure black)
    "bg":         "#1f1d1a",
    "surface":    "#2a2723",
    "surface_2":  "#34302a",
    "border":     "#3a3530",
    "border_strong": "#4a443d",

    # Text
    "text":       "#f4ede0",   # paper
    "text_2":     "#d4cebf",
    "muted":      "#8a8478",
    "muted_2":    "#6a6458",

    # Accent "infusion" — soft, one per section
    "sage":       "#a8c0ae",   # learning + jobs
    "coral":      "#e8a598",   # news
    "lavender":   "#b5a8c9",   # prompts / apply
    "sky":        "#a5c5d4",   # tools / repos

    # Semantic
    "success":    "#9bb88a",
    "warn":       "#d9b87a",
    "danger":     "#c98a82",
}


# Per-source accent color (used as small badge next to items)
SOURCE_ACCENT = {
    "hackernews":      "coral",
    "huggingface":     "sky",
    "findarepo":       "lavender",
    "lobsters":        "sage",
    "github_trending": "sky",
    "importai":        "coral",
}


# Per-tab accent (for tab indicator + section accents)
TAB_ACCENT = {
    "astazi":  "sage",     # morning glance — calm, neutral
    "stiri":   "coral",    # news — energetic but soft
    "invata":  "sage",     # learning
    "aplica":  "lavender", # prompts
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
    "ease":         "cubic-bezier(0.16, 1, 0.3, 1)",     # smooth ease-out
    "ease_soft":    "cubic-bezier(0.4, 0, 0.2, 1)",     # material-style
    "dur_fast":     "150ms",
    "dur_base":     "240ms",
    "dur_slow":     "400ms",
    "dur_reveal":   "600ms",
}


# ===== CSS =====
def render_css() -> str:
    """Return the full CSS string for the app."""
    c = COLORS
    f = FONTS
    m = MOTION

    # Per-tab accent colors (used in nth-child rules)
    tab_colors = {
        1: c["sage"],       # ASTĂZI
        2: c["coral"],      # ȘTIRI
        3: c["sage"],       # ÎNVAȚĂ
        4: c["lavender"],   # APLICĂ
    }

    # Build per-tab CSS rules
    tab_css = "\n".join(
        f"""  .stTabs [data-baseweb="tab"]:nth-child({i})[aria-selected="true"] {{
    color: {col} !important;
    border-bottom: 2px solid {col} !important;
  }}"""
        for i, col in tab_colors.items()
    )

    return f"""<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {{
    --bg: {c['bg']};
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

  /* App background */
  .stApp {{
    background-color: var(--bg);
    color: var(--text);
    font-family: {f['sans']};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  section.main > div {{ padding-top: 1.5rem; max-width: 1200px; }}

  /* Typography */
  h1, h2, h3, h4, h5, h6 {{
    font-family: {f['serif']};
    font-weight: 400;
    letter-spacing: -0.01em;
    color: var(--text);
  }}
  h1 {{ font-weight: 300; letter-spacing: -0.02em; }}
  h2 {{ color: var(--text); font-size: 1.75rem; margin: 0 0 0.5rem; }}
  h3 {{ font-size: 1.25rem; }}
  h4 {{ font-size: 1.05rem; }}

  p, li {{ color: var(--text-2); line-height: 1.65; }}

  /* Caption + small text */
  .stCaption, [data-testid="stCaption"] {{
    color: var(--muted) !important;
    font-family: {f['mono']};
    font-size: 0.75rem;
    letter-spacing: 0.02em;
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    background-color: transparent;
    border-bottom: 1px solid var(--border);
    padding: 0;
  }}
  .stTabs [data-baseweb="tab"] {{
    background-color: transparent;
    color: var(--muted);
    padding: 0.85rem 1.25rem;
    font-family: {f['mono']};
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-bottom: 2px solid transparent;
    transition: color var(--dur-base) var(--ease),
                border-color var(--dur-base) var(--ease);
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    color: var(--text);
    background-color: rgba(255, 255, 255, 0.02);
  }}
{tab_css}

  /* Cards */
  [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.3rem !important;
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
    font-size: 0.75rem;
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

  /* Code */
  code {{
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
  .reveal {{
    animation: fade-up var(--dur-reveal) var(--ease) both;
  }}
  .reveal-1 {{ animation-delay: 0ms; }}
  .reveal-2 {{ animation-delay: 80ms; }}
  .reveal-3 {{ animation-delay: 160ms; }}
  .reveal-4 {{ animation-delay: 240ms; }}

  /* Shimmer for skeleton loaders */
  @keyframes shimmer {{
    0%   {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
  }}
  .shimmer {{
    background: linear-gradient(
      90deg,
      var(--surface) 0%,
      var(--surface-2) 50%,
      var(--surface) 100%
    );
    background-size: 200% 100%;
    animation: shimmer 1.6s infinite linear;
    border-radius: 6px;
  }}

  /* Pulse for "new" badge */
  @keyframes pulse-soft {{
    0%, 100% {{ opacity: 0.5; }}
    50%      {{ opacity: 1; }}
  }}
  .pulse-dot {{
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--coral);
    animation: pulse-soft 2.4s var(--ease-soft) infinite;
    margin-right: 6px;
    vertical-align: middle;
  }}

  /* Hide Streamlit chrome */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  .viewerBadge_link__qRIco {{ display: none !important; }}
</style>"""
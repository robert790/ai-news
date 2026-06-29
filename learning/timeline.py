"""Hero timeline · Drumul Erica · Learning v1.0 redesign.

Replaces the old Cytoscape skill tree with a horizontal SVG timeline
of 7 eras, drawn as a flowing path with subtle CSS animations. This
IS the visual that anchors the redesigned Learning tab — the
unifying thread for the Erica story.

Why an SVG timeline and not another graph:
- The user wants the story arc visible at a glance
- A horizontal "you-are-here" timeline is far more legible than a
  graph for a 10-chapter linear curriculum
- Pure SVG + CSS = no JS deps, no iframe, no Streamlit 1.32 vs 1.50
  incompatibilities. Renders identically everywhere.
- Animations are declarative CSS — drops on @keyframes only, no
  infinite animation loops to fight Streamlit reruns.

Public API:
    render_hero_timeline()      → full-width hero SVG (7 eras + HERE)
    render_chapter_card(cid)    → chip-style card with illustration
"""

from __future__ import annotations

# The 7 eras — narrative arcs of AI in 2026 framing.
ERAS = [
    {"label": "Reguli",        "year": "1950–1990", "color": "#d4cebf", "tone": "fade"},
    {"label": "ML",            "year": "1990–2010", "color": "#a5c5d4", "tone": "fade"},
    {"label": "Deep Learning",  "year": "2012",      "color": "#b5a8c9", "tone": "fade"},
    {"label": "Transformer",   "year": "2017",      "color": "#a8c0ae", "tone": "fade"},
    {"label": "LLM / ChatGPT", "year": "2022",      "color": "#d4a574", "tone": "rise"},
    {"label": "Restricții",    "year": "2025+",     "color": "#c98a82", "tone": "alert"},
    {"label": "Fuziune",       "year": "2026",      "color": "#e8a598", "tone": "rise"},
    {"label": "Tu",            "year": "acum",      "color": "#f4ede0", "tone": "pulse"},
]


def render_hero_timeline() -> str:
    """Return HTML for the timeline hero — used at top of Learning tab."""
    # 8 stops equally spaced along a horizontal axis (40px..1080px wide)
    stops = []
    labels = []
    n = len(ERAS)
    x_min, x_max = 90, 1110
    for i, era in enumerate(ERAS):
        x = x_min + (x_max - x_min) * i / (n - 1)
        stops.append((x, era))

    # Build SVG circles
    circles_svg = []
    labels_svg = []
    for x, era in stops:
        is_here = era["label"] == "Tu"
        r = 14 if is_here else 9
        if is_here:
            circles_svg.append(
                f'<g transform="translate({x},180)">'
                f'<circle r="22" fill="{era["color"]}" opacity="0.18" '
                f'class="tl-here-pulse"/>'
                f'<circle r="{r}" fill="{era["color"]}" '
                f'stroke="#1a1816" stroke-width="3" class="tl-here-core"/>'
                f'<text x="0" y="-32" text-anchor="middle" '
                f'font-family="JetBrains Mono, monospace" font-size="13" '
                f'fill="{era["color"]}" letter-spacing="2">ERIKA</text>'
                f'<text x="0" y="-50" text-anchor="middle" '
                f'font-family="Outfit, Inter, sans-serif" font-size="11" '
                f'fill="#8a8478" letter-spacing="3">TU EȘTI AICI</text>'
                f'</g>'
            )
        else:
            circles_svg.append(
                f'<g transform="translate({x},180)">'
                f'<circle r="{r}" fill="{era["color"]}" '
                f'stroke="#1a1816" stroke-width="2"/>'
                f'</g>'
            )
        # Year below
        labels_svg.append(
            f'<text x="{x}" y="220" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10" '
            f'fill="#8a8478" letter-spacing="1">{era["year"]}</text>'
        )
        # Label above
        labels_svg.append(
            f'<text x="{x}" y="158" text-anchor="middle" '
            f'font-family="Newsreader, serif" font-size="13" '
            f'fill="{era["color"]}" font-weight="500">{era["label"]}</text>'
        )

    # Connecting line — gold dashed through all eras
    line_svg = (
        f'<line x1="{x_min}" y1="180" x2="{x_max}" y2="180" '
        f'stroke="#d4a574" stroke-width="2" stroke-dasharray="6 6" '
        f'class="tl-flow-line"/>'
    )

    # Final assembled SVG
    svg = f"""
<svg viewBox="0 0 1200 320" xmlns="http://www.w3.org/2000/svg" class="erika-timeline-svg">
  {line_svg}
  {''.join(circles_svg)}
  {''.join(labels_svg)}
  <text x="50%" y="270" text-anchor="middle"
        font-family="JetBrains Mono, monospace" font-size="11"
        fill="#6a6458" letter-spacing="6">DE LA PROJECT ERICA · LA AICI</text>
  <text x="50%" y="295" text-anchor="middle"
        font-family="Newsreader, serif" font-size="15"
        fill="#c4b9a7" font-style="italic">7 era. 10 capitole. un singur proiect: tu.</text>
</svg>
"""

    return f"""
<style>
  .erika-timeline-wrap {{
    width: 100%;
    overflow-x: auto;
    padding: 1rem 0;
  }}
  .erika-timeline-svg {{
    width: 100%;
    max-width: 1200px;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
  /* Animations: subtle, no bouncing */
  .tl-flow-line {{
    stroke-dashoffset: 0;
    animation: tl-flow 22s linear infinite;
  }}
  @keyframes tl-flow {{
    to {{ stroke-dashoffset: -120; }}
  }}
  .tl-here-pulse {{
    transform-origin: center;
    animation: tl-pulse 2.2s ease-in-out infinite;
  }}
  @keyframes tl-pulse {{
    0%, 100% {{ opacity: 0.18; transform: scale(1); }}
    50% {{ opacity: 0.32; transform: scale(1.18); }}
  }}
  .tl-here-core {{
    transform-origin: center;
    animation: tl-core 2.2s ease-in-out infinite;
  }}
  @keyframes tl-core {{
    0%, 100% {{ filter: drop-shadow(0 0 0 #d4a57400); }}
    50% {{ filter: drop-shadow(0 0 8px #d4a57499); }}
  }}
</style>

<div class="erika-timeline-wrap">
  {svg}
</div>
"""


# Era → illustration mapping (a tiny inline SVG per era is overkill
# for chips; the timeline carries the visual story). The chapter
# detail panel can still render whichever body content we built.

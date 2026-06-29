"""Skill tree visualization · Learning v0.6 (BLUE-inspired).

Builds a Cytoscape.js graph from the chapter data. Nodes are chapters,
edges are prerequisites. Cytoscape's breadthfirst layout puts the root
at top and branches downward — exactly the user's whiteboard sketch.

v0.6 additions (Sebastian Rey B.L.U.E. inspired):
  - Pillar nodes (chapters flagged `recommended_pillar=True`) get a
    gold ring and the recommended path between them is a dashed
    animated line — this IS the BLUE "Better Methods can move up"
    visual: a curated reading sequence through the curriculum.
  - Tooltip is now richer: chapter title, complexity dots, prereq
    list, recommended method name when present.
  - Click handler is best-effort (uses `Streamlit.setComponentValue`
    when available). On Streamlit 1.32 the iframe doesn't expose the
    Streamlit global, so the click is visually responsive but does
    NOT update the detail panel. Use the chapter chip grid below
    the tree to navigate — those buttons work on every version.
"""
import json
import streamlit.components.v1 as components

from learning.chapters import CHAPTERS, get_root_id, DOMAIN_META

# BLUE pillar sequence — the curated reading order.
# Visualised as a dashed connecting line on the skill tree.
PILLAR_PATH: list[str] = [
    ch.id for ch in CHAPTERS.values() if ch.recommended_pillar
]


def build_tree_elements() -> dict:
    """Build the nodes + edges payload for Cytoscape."""
    nodes = []
    for ch in CHAPTERS.values():
        meta = DOMAIN_META[ch.domain]
        recommended_name = ""
        for m in ch.methods:
            if m.recommended:
                recommended_name = m.name
                break
        nodes.append({
            "data": {
                "id": ch.id,
                "label": f"{ch.number}",
                "title": ch.title,
                "subtitle": ch.subtitle,
                "domain": ch.domain,
                "domain_label": meta["label"],
                "domain_color": meta["color"],
                "complexity": ch.complexity,
                "methods_count": len(ch.methods),
                "recommended_method": recommended_name,
                "prereq_count": len(ch.prerequisites),
                "is_pillar": ch.recommended_pillar,
            },
            "classes": f"domain-{ch.domain} complexity-{ch.complexity}" + (
                " has-methods" if ch.methods else ""
            ) + (
                " is-pillar" if ch.recommended_pillar else ""
            ),
        })

    edges = []
    for ch in CHAPTERS.values():
        for prereq in ch.prerequisites:
            edges.append({
                "data": {
                    "source": prereq,
                    "target": ch.id,
                },
                "classes": "prereq-edge",
            })

    # Recommended path edges — consecutive pillars get a dashed
    # gold edge drawn ABOVE the regular prerequisite edges. Cytoscape
    # draws edges in declaration order, so we append these last so
    # they paint on top.
    for i in range(len(PILLAR_PATH) - 1):
        edges.append({
            "data": {
                "source": PILLAR_PATH[i],
                "target": PILLAR_PATH[i + 1],
            },
            "classes": "pillar-edge",
        })

    return {"nodes": nodes, "edges": edges}


SKILL_TREE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    #cy {{
      width: 100%;
      height: 580px;
      background: #242019;
      border: 1px solid #3a3530;
      border-radius: 14px;
      background-image:
        radial-gradient(circle, #3a3530 1px, transparent 1px);
      background-size: 24px 24px;
      position: relative;
    }}

    /* ---------- Tooltip (BLUE-inspired · richer on hover) ---------- */
    #tooltip {{
      position: absolute;
      display: none;
      background: #1a1815;
      border: 1px solid #3a3530;
      border-radius: 10px;
      padding: 0.7rem 0.85rem;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      color: #f4ede0;
      pointer-events: none;
      z-index: 10;
      max-width: 280px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }}
    #tooltip .tt-title {{
      font-family: 'Newsreader', Georgia, serif;
      font-size: 1rem;
      margin-bottom: 0.15rem;
      line-height: 1.2;
      font-weight: 500;
    }}
    #tooltip .tt-sub {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.6rem;
      color: #8a8478;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 0.45rem;
    }}
    #tooltip .tt-row {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.65rem;
      color: #c4b9a7;
      letter-spacing: 0.02em;
      margin-bottom: 0.2rem;
    }}
    #tooltip .tt-row .label {{
      color: #6a6458;
      width: 64px;
      flex-shrink: 0;
    }}
    #tooltip .tt-dots {{
      font-family: 'JetBrains Mono', monospace;
      color: #d4a574;
      letter-spacing: 0.15em;
    }}
    #tooltip .tt-pillar {{
      display: inline-block;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.55rem;
      color: #d4a574;
      background: rgba(212, 165, 116, 0.12);
      border: 1px solid rgba(212, 165, 116, 0.3);
      padding: 0.1rem 0.4rem;
      border-radius: 4px;
      letter-spacing: 0.06em;
      margin-bottom: 0.4rem;
    }}
    #tooltip .tt-method {{
      margin-top: 0.4rem;
      padding-top: 0.4rem;
      border-top: 1px solid #3a3530;
      font-family: 'Newsreader', serif;
      font-style: italic;
      font-size: 0.8rem;
      color: #d4a574;
    }}
    #tooltip .tt-method::before {{
      content: "◆ ";
      color: #d4a574;
      font-style: normal;
    }}

    /* ---------- Legend ---------- */
    .legend {{
      display: flex;
      gap: 1.2rem;
      margin-top: 1rem;
      flex-wrap: wrap;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: #8a8478;
      letter-spacing: 0.04em;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }}
    .legend-line {{
      width: 18px;
      height: 0;
      border-top: 1.5px dashed #d4a574;
      display: inline-block;
    }}
    .hint {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: #6a6458;
      margin-top: 0.6rem;
      letter-spacing: 0.04em;
    }}
  </style>
</head>
<body>
  <div id="cy">
    <div id="tooltip"></div>
  </div>
  <div class="legend">
    <div class="legend-item"><span class="legend-dot" style="background:#a8c0ae;"></span>Foundations</div>
    <div class="legend-item"><span class="legend-dot" style="background:#e8a598;"></span>Applied</div>
    <div class="legend-item"><span class="legend-dot" style="background:#a5c5d4;"></span>Research</div>
    <div class="legend-item"><span class="legend-dot" style="background:#d9b87a;"></span>Romania</div>
    <div class="legend-item"><span class="legend-dot" style="background:#b5a8c9;"></span>Career</div>
    <div class="legend-item"><span class="legend-dot" style="background:#8a8478;"></span>Tools</div>
    <div class="legend-item"><span class="legend-dot" style="background:#d4a574; box-shadow: 0 0 0 2px #d4a57455;"></span>Pillar</div>
    <div class="legend-item"><span class="legend-line"></span>Recommended path</div>
  </div>
  <div class="hint">Gold nodes = the curated sequence. Click the chip grid below to navigate.</div>

  <script>
    const elements = {ELEMENTS_JSON};

    const COMPLEXITY_DOTS = {{1: "·", 2: "··", 3: "···", 4: "····"}};

    const cy = cytoscape({{
      container: document.getElementById('cy'),
      elements: elements,
      wheelSensitivity: 0.2,
      style: [
        {{
          selector: 'node',
          style: {{
            'background-color': 'data(domain_color)',
            'label': 'data(label)',
            'color': '#f4ede0',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-family': 'Newsreader, Georgia, serif',
            'font-size': '14px',
            'font-weight': '400',
            'width': 48,
            'height': 48,
            'border-width': 2,
            'border-color': '#1f1d1a',
            'text-outline-width': 0,
            'transition-property': 'background-color, width, height, border-color, border-width',
            'transition-duration': '200ms',
          }},
        }},
        {{
          selector: 'node:hover',
          style: {{
            'width': 60,
            'height': 60,
            'border-color': '#f4ede0',
            'border-width': 3,
            'cursor': 'pointer',
          }},
        }},
        {{
          selector: 'node.complexity-1',
          style: {{ 'width': 54, 'height': 54, 'font-size': '15px' }},
        }},
        {{
          selector: 'node.complexity-4',
          style: {{ 'border-style': 'solid', 'border-width': 3 }},
        }},
        /* ----- BLUE pillar nodes: gold outer ring + glow ----- */
        {{
          selector: 'node.is-pillar',
          style: {{
            'border-color': '#d4a574',
            'border-width': 3,
            'border-style': 'solid',
            'background-blacken': -10,
          }},
        }},
        {{
          selector: 'node.is-pillar:hover',
          style: {{
            'border-color': '#e8c895',
            'border-width': 4,
          }},
        }},
        /* ----- Regular edges: faint prerequisite arrows ----- */
        {{
          selector: 'edge.prereq-edge',
          style: {{
            'width': 1.2,
            'line-color': '#4a443d',
            'target-arrow-color': '#4a443d',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'control-point-step-size': 40,
            'transition-property': 'line-color, width',
            'transition-duration': '200ms',
            'opacity': 0.7,
          }},
        }},
        {{
          selector: 'edge.prereq-edge:hover',
          style: {{
            'line-color': '#d4a574',
            'width': 2.5,
            'opacity': 1,
          }},
        }},
        /* ----- BLUE recommended path: dashed gold line, animated ----- */
        {{
          selector: 'edge.pillar-edge',
          style: {{
            'width': 2.5,
            'line-color': '#d4a574',
            'line-style': 'dashed',
            'line-dash-pattern': [6, 4],
            'target-arrow-color': '#d4a574',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'control-point-step-size': 60,
            'opacity': 0.85,
            'z-index': 99,
          }},
        }},
        {{
          selector: 'edge.pillar-edge:hover',
          style: {{
            'width': 3.5,
            'opacity': 1,
          }},
        }},
      ],
      layout: {{
        name: 'breadthfirst',
        directed: true,
        padding: 30,
        spacingFactor: 1.6,
        nodeRepulsion: 8000,
        animate: true,
        animationDuration: 600,
      }},
    }});

    /* ---------- Tooltip (richer on hover) ---------- */
    const tooltipEl = document.getElementById('tooltip');
    const cyContainer = document.getElementById('cy');

    function escapeHtml(s) {{
      return String(s).replace(/[&<>"']/g, c => ({{
        '&': '&amp;', '<': '&lt;', '>': '&gt;',
        '"': '&quot;', "'": '&#39;'
      }})[c]);
    }}

    cy.on('mouseover', 'node', function(evt) {{
      const node = evt.target;
      const data = node.data();
      const complexity = data.complexity || 1;
      const dots = COMPLEXITY_DOTS[complexity] || '·';
      const html = [];
      html.push('<div class="tt-title">' + escapeHtml(data.title) + '</div>');
      html.push('<div class="tt-sub">Ch ' + data.label + ' · ' + escapeHtml(data.domain_label) + '</div>');
      if (data.is_pillar) {{
        html.push('<div><span class="tt-pillar">◆ BLUE PILLAR</span></div>');
      }}
      html.push('<div class="tt-row"><span class="label">Complexitate</span><span class="tt-dots">' + dots + '</span></div>');
      html.push('<div class="tt-row"><span class="label">Necesită</span><span>' + (data.prereq_count || 0) + ' capitol' + (data.prereq_count === 1 ? '' : 'e') + '</span></div>');
      if ((data.methods_count || 0) > 0) {{
        html.push('<div class="tt-row"><span class="label">Methods</span><span>' + data.methods_count + '</span></div>');
      }}
      if (data.recommended_method) {{
        html.push('<div class="tt-method">' + escapeHtml(data.recommended_method) + '</div>');
      }}
      tooltipEl.innerHTML = html.join('');
      tooltipEl.style.display = 'block';
    }});

    cy.on('mouseout', 'node', function() {{
      tooltipEl.style.display = 'none';
    }});

    cyContainer.addEventListener('mousemove', function(evt) {{
      const rect = cyContainer.getBoundingClientRect();
      const x = evt.clientX - rect.left + 14;
      const y = evt.clientY - rect.top + 14;
      // Keep tooltip inside the canvas
      const ttW = tooltipEl.offsetWidth;
      const ttH = tooltipEl.offsetHeight;
      const maxX = rect.width - ttW - 8;
      const maxY = rect.height - ttH - 8;
      tooltipEl.style.left = Math.min(x, maxX) + 'px';
      tooltipEl.style.top = Math.min(y, maxY) + 'px';
    }});

    /* ---------- Click → best-effort send to Streamlit ----------
       On Streamlit 1.32 the iframe doesn't expose window.Streamlit,
       so the click is visually responsive (hover ring, focus) but
       does NOT update the chapter detail panel. The chip grid below
       the tree is the reliable way to navigate chapters. */
    cy.on('tap', 'node', function(evt) {{
      const node = evt.target;
      if (window.Streamlit !== undefined) {{
        Streamlit.setComponentValue(node.id());
      }}
    }});

    cy.on('tap', function(evt) {{
      if (evt.target === cy && window.Streamlit !== undefined) {{
        Streamlit.setComponentValue(null);
      }}
    }});

    /* ---------- Animate the recommended path (BLUE signature) ----------
       Subtle dash-offset shift = the gold line appears to flow
       toward the next pillar. Lives on top of the static layout. */
    let dashOffset = 0;
    function flowRecommended() {{
      dashOffset = (dashOffset - 1) % 10;
      cy.style().selector('edge.pillar-edge').style('line-dash-offset', dashOffset).update();
      requestAnimationFrame(flowRecommended);
    }}
    requestAnimationFrame(flowRecommended);

    /* Initial fit + size to window width */
    setTimeout(function() {{ cy.resize(); cy.fit(null, 40); }}, 200);
  </script>
</body>
</html>
"""


def render_skill_tree() -> "streamlit.components.v1.HTML":
    """Render the skill tree. The returned value is the selected
    chapter id when Streamlit's bidirectional channel is available
    (Streamlit >= 1.40). On 1.32, use the chapter chip grid below."""
    elements = build_tree_elements()
    html = SKILL_TREE_HTML.format(ELEMENTS_JSON=json.dumps(elements))
    return components.html(html, height=680, scrolling=False)


def render_mini_skill_tree() -> "streamlit.components.v1.HTML":
    """Smaller version for the Azi landing (Today's lesson preview)."""
    elements = build_tree_elements()
    html = SKILL_TREE_HTML.format(ELEMENTS_JSON=json.dumps(elements))
    return components.html(html.replace("height: 580px", "height: 320px"),
                           height=380, scrolling=False)
"""Skill tree visualization · Learning v0.4.

Builds a Cytoscape.js graph from the chapter data. Nodes are chapters,
edges are prerequisites. Cytoscape's breadthfirst layout puts the root
at top and branches downward — exactly the user's whiteboard sketch.

Click a node → its ID is sent back to Streamlit via
Streamlit.setComponentValue, which triggers a chapter-detail panel below.
"""
import json
import streamlit.components.v1 as components

from learning.chapters import CHAPTERS, get_root_id, DOMAIN_META


def build_tree_elements() -> dict:
    """Build the nodes + edges payload for Cytoscape."""
    nodes = []
    for ch in CHAPTERS.values():
        meta = DOMAIN_META[ch.domain]
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
            },
            "classes": f"domain-{ch.domain} complexity-{ch.complexity}",
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
    }}
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
  <div id="cy"></div>
  <div class="legend">
    <div class="legend-item"><span class="legend-dot" style="background:#a8c0ae;"></span>Foundations</div>
    <div class="legend-item"><span class="legend-dot" style="background:#e8a598;"></span>Applied</div>
    <div class="legend-item"><span class="legend-dot" style="background:#a5c5d4;"></span>Research</div>
    <div class="legend-item"><span class="legend-dot" style="background:#d9b87a;"></span>Romania</div>
    <div class="legend-item"><span class="legend-dot" style="background:#b5a8c9;"></span>Career</div>
    <div class="legend-item"><span class="legend-dot" style="background:#8a8478;"></span>Tools</div>
  </div>
  <div class="hint">Click a chapter to open its detail panel below.</div>

  <script>
    const elements = {ELEMENTS_JSON};

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
            'transition-property': 'background-color, width, height, border-color',
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
          style: {{
            'border-style': 'solid',
            'border-width': 3,
          }},
        }},
        {{
          selector: 'edge',
          style: {{
            'width': 1.5,
            'line-color': '#4a443d',
            'target-arrow-color': '#4a443d',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'control-point-step-size': 40,
            'transition-property': 'line-color, width',
            'transition-duration': '200ms',
          }},
        }},
        {{
          selector: 'edge:hover',
          style: {{
            'line-color': '#d4a574',
            'width': 2.5,
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

    // Send selected node id back to Streamlit.
    cy.on('tap', 'node', function(evt) {{
      const node = evt.target;
      const value = node.id();
      if (window.Streamlit !== undefined) {{
        Streamlit.setComponentValue(value);
      }}
    }});

    // Deselect on background tap.
    cy.on('tap', function(evt) {{
      if (evt.target === cy) {{
        if (window.Streamlit !== undefined) {{
          Streamlit.setComponentValue(null);
        }}
      }}
    }});

    // Initial fit + size to window width
    setTimeout(function() {{ cy.resize(); cy.fit(null, 40); }}, 200);
  </script>
</body>
</html>
"""


def render_skill_tree() -> "streamlit.components.v1.HTML":
    """Render the skill tree and return the click handler value (chapter id)."""
    elements = build_tree_elements()
    html = SKILL_TREE_HTML.format(ELEMENTS_JSON=json.dumps(elements))
    return components.html(html, height=680, scrolling=False)


def render_mini_skill_tree() -> "streamlit.components.v1.HTML":
    """Smaller version for the Azi landing (Today's lesson preview)."""
    elements = build_tree_elements()
    html = SKILL_TREE_HTML.format(ELEMENTS_JSON=json.dumps(elements))
    # Compact height
    return components.html(html.replace("height: 580px", "height: 320px"),
                           height=380, scrolling=False)
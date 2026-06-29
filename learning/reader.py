"""In-app lesson reader · Learning v1.0 (Phase A).

Loads pre-parsed chapter HTML chunks (from parser.py) and renders
them inside Streamlit's chapter detail panel as a real reading
experience — no link out to the standalone HTML course.

The chapter detail panel becomes a 3-tab reader:
  - READ     · the chapter content (callouts, analogies, SVGs)
  - METHODS  · the BLUE-inspired methods (existing v0.6)
  - PRACTICE · verifiers + "build this"

Why so much for one file: this is the single biggest unlock for
the user's request — "vrem sa fie totul afisat acolo". When this
ship, the user reads the chapter, ticks verifiers, and marks
complete — all inside OpenRadar.
"""
from __future__ import annotations

import json
from pathlib import Path
from functools import lru_cache

CONTENT_DIR = Path(__file__).resolve().parent / "content"


@lru_cache(maxsize=32)
def load_chapter_html(chapter_id: str) -> str:
    """Return the rendered HTML for a chapter, with reader CSS baked in.

    Cached so we don't re-read on every Streamlit rerun.
    """
    p = CONTENT_DIR / f"{chapter_id}.html"
    if not p.exists():
        return (
            "<div class='lrn-reader'><p style='color:#8a8478;'>"
            "Conținutul capitolului se pregătește. "
            "Rulează <code>python -m learning.parser</code> pentru a-l genera."
            "</p></div>"
        )
    return p.read_text(encoding="utf-8")


@lru_cache(maxsize=32)
def load_chapter_meta(chapter_id: str) -> dict:
    p = CONTENT_DIR / f"{chapter_id}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def render_reader(chapter_id: str) -> str:
    """Same as load_chapter_html; named for use in app.py."""
    return load_chapter_html(chapter_id)


def render_tagline_callout(chapter_id: str) -> str:
    """A subtle header above the body — course's tagline.

    The source course uses `<p class='tagline'>` as the chapter's
    one-line thesis. Render it as a serif quote to differentiate
    from the body.
    """
    meta = load_chapter_meta(chapter_id)
    tagline = meta.get("tagline") or ""
    if not tagline:
        return ""
    return (
        '<div style="margin-bottom: 1.2rem; padding: 0.8rem 1rem; '
        'border-left: 2px solid #b5a8c9; background: rgba(181, 168, 201, 0.05); '
        'font-family: Newsreader, serif; font-style: italic; '
        f'color: #e9e2d3; font-size: 1.05rem; line-height: 1.5; '
        f'border-radius: 0 6px 6px 0;">{tagline}</div>'
    )


def render_lead(chapter_id: str) -> str:
    """Lead paragraph — pulled from the source course's first <p>.

    Rendered slightly larger to signal 'orientation paragraph'.
    """
    meta = load_chapter_meta(chapter_id)
    lead = meta.get("lead") or ""
    if not lead:
        return ""
    return (
        '<p style="font-family: Newsreader, serif; font-size: 1.12rem; '
        'line-height: 1.65; color: #f4ede0; margin: 0 0 1.4rem 0;">'
        f"{lead}</p>"
    )

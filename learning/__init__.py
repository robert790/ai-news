"""Learning module — Hartă AI pe categorii (v1.1 redesign).

Public API (chapters) flows through :mod:`learning.loader` so the
preferred editable source is ``content/chapters.jsonl``. The legacy
Python module :mod:`learning.chapters` remains the fallback for
dev environments without the JSONL file.
"""
from .chapters import (
    CHAPTERS,
    DOMAIN_META,
    COMPLEXITY_META,
    Chapter,
    domain_color,
)
from .loader import (
    get_all_chapters,
    get_chapter,
    get_root_id,
)
from .skill_tree import render_skill_tree, render_mini_skill_tree
from .timeline import render_hero_timeline
from .learning_render import render_detail_panel

__all__ = [
    "CHAPTERS",            # legacy fallback list (loader wins at runtime)
    "DOMAIN_META",
    "COMPLEXITY_META",
    "Chapter",
    "get_all_chapters",   # loader-backed; reads content/chapters.jsonl
    "get_chapter",         # loader-backed
    "get_root_id",         # loader-backed
    "domain_color",
    "render_skill_tree",
    "render_mini_skill_tree",
    "render_hero_timeline",
    "render_detail_panel",
]

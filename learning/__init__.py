"""Learning module — Hartă AI pe categorii (v1.1 redesign)."""
from .chapters import (
    CHAPTERS,
    DOMAIN_META,
    COMPLEXITY_META,
    Chapter,
    get_all_chapters,
    get_chapter,
    get_root_id,
    domain_color,
)
from .skill_tree import render_skill_tree, render_mini_skill_tree
from .timeline import render_hero_timeline
from .learning_render import render_detail_panel

__all__ = [
    "CHAPTERS",
    "DOMAIN_META",
    "COMPLEXITY_META",
    "Chapter",
    "get_all_chapters",
    "get_chapter",
    "get_root_id",
    "domain_color",
    "render_skill_tree",
    "render_mini_skill_tree",
    "render_hero_timeline",
    "render_detail_panel",
]

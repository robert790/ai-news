"""Skill tree stub — kept only for backward compat.

The redesigned Learning tab uses `timeline.render_hero_timeline()`
for the unifying visual. This module returns nothing useful so
`from learning.skill_tree import render_skill_tree` still works
in legacy code paths.
"""
from __future__ import annotations


def render_skill_tree() -> str:
    """Return an empty string — replaced by the timeline hero."""
    return ""


def render_mini_skill_tree() -> str:
    return ""


PILLAR_PATH: list[str] = []  # all chapters are part of the linear path

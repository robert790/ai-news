"""Prompt Bible data loader + filter helpers.

Loads `prompts_data/prompts.json` (committed to the repo, generated
from the upstream Prompt Bible `data.js` by `_convert_data.py`) once
per session, then exposes thin query helpers the Prompts tab uses.

The JSON shape:
  {
    "meta":       {version, updated, note},
    "vendors":    {vendor_id: {label, color, modelIds, note}},
    "models":     {model_id: {vendor, label, color, strengths}},
    "categories": [{id, label, icon, blurb}, ...],
    "prompts":    [{id, category, title, difficulty, models, tags,
                    when, prompt, variants?, notes?, antiPatterns?}, ...]
  }

The data is intentionally kept in the repo (not fetched from Hugging
Face at runtime) so the Space boots with no network dependency and the
Prompts tab renders even when the upstream site is down.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

DATA_PATH = Path(__file__).parent / "prompts_data" / "prompts.json"


@dataclass(frozen=True)
class PromptBible:
    meta: dict
    vendors: dict
    models: dict
    categories: list
    prompts: list


@lru_cache(maxsize=1)
def load_prompt_bible() -> PromptBible:
    """Load and cache the prompt bible JSON. Called at most once."""
    with DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return PromptBible(
        meta=raw["meta"],
        vendors=raw["vendors"],
        models=raw["models"],
        categories=raw["categories"],
        prompts=raw["prompts"],
    )


def load_prompts_index() -> list[dict]:
    """Lightweight: just the fields a chapter cross-ref needs.

    Avoids passing the full Bible around and serializing huge prompt
    bodies when we only care about title/category/difficulty/tags.
    """
    bible = load_prompt_bible()
    out = []
    for p in bible.prompts:
        out.append({
            "id": p.get("id"),
            "title": p.get("title", ""),
            "category": p.get("category", ""),
            "difficulty": p.get("difficulty", ""),
            "tags": p.get("tags", []) or [],
        })
    return out


def category_label(bible: PromptBible, cat_id: str) -> str:
    """Resolve a category id to its display label (falls back to id)."""
    for c in bible.categories:
        if c["id"] == cat_id:
            return c.get("label", cat_id)
    return cat_id


def category_icon(bible: PromptBible, cat_id: str) -> str:
    for c in bible.categories:
        if c["id"] == cat_id:
            return c.get("icon", "·")
    return "·"


def category_color(bible: PromptBible, cat_id: str) -> str:
    """Pick a soft accent color per category. Mirrors the landing-page
    palette so the Prompts tab feels like part of OpenRadar."""
    palette = {
        "code":                 "#a8c0ae",   # sage
        "write":                "#e8a598",   # coral
        "research":             "#b5a8c9",   # lavender
        "decide":               "#a5c5d4",   # sky
        "operate":              "#d9b87a",   # warn / amber
        "security":             "#c98a82",   # danger / red
        "design":               "#b8a4d9",   # purple
        "agent":                "#9bb88a",   # success
        "multimodal":           "#98c5b8",   # mint
        "image":                "#f4a3a8",   # pink
        "video":                "#d4b8c8",   # rose
        "professional-research":"#e8c994",   # gold
    }
    return palette.get(cat_id, "#a8a094")


def difficulty_label(d: str) -> str:
    return {"beginner": "Beginner", "intermediate": "Intermediate",
            "advanced": "Advanced", "expert": "Expert"}.get(d, d.title())


def difficulty_color(d: str) -> str:
    return {"beginner": "#9bb88a", "intermediate": "#a5c5d4",
            "advanced": "#e8a598", "expert": "#c98a82"}.get(d, "#a8a094")


def filter_prompts(
    bible: PromptBible,
    *,
    text: str = "",
    category: str = "",
    difficulty: str = "",
    model: str = "",
) -> list:
    """Return prompts matching all supplied filters. Empty filter = match all.

    Text search is case-insensitive across title, tags, when, prompt, and
    notes (antiPatterns intentionally excluded — those are pitfalls,
    not content).
    """
    out = []
    needle = text.strip().lower()
    for p in bible.prompts:
        if category and p.get("category") != category:
            continue
        if difficulty and p.get("difficulty") != difficulty:
            continue
        if model and model not in p.get("models", []):
            continue
        if needle:
            haystack_parts = [
                p.get("title", ""),
                " ".join(p.get("tags", [])),
                p.get("when", ""),
                p.get("prompt", ""),
                " ".join(p.get("notes", []) or []),
            ]
            haystack = " ".join(haystack_parts).lower()
            if needle not in haystack:
                continue
        out.append(p)
    return out


def all_model_ids(bible: PromptBible) -> list:
    """Stable, ordered list of model ids from the loaded bible."""
    return list(bible.models.keys())


def all_difficulties() -> list:
    return ["beginner", "intermediate", "advanced", "expert"]


def all_categories(bible: PromptBible) -> list:
    return [c["id"] for c in bible.categories]


def iter_examples(bible: PromptBible, limit: int = 3) -> Iterable[dict]:
    """First `limit` prompts, useful for the Azi landing-page slot."""
    return bible.prompts[:limit]
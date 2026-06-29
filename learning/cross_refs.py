"""Cross-refs · match a chapter to live items from News / GitHub /
Prompts / Jobs.

The chapters live as static content. The moat of OpenRadar is
TYING those chapters to what actually moved today in the AI space.
This module is that bridge.

Strategy:
1. Hand-curated `chapter_tags` (already in chapter_tags.py).
2. Score every item against every tag — sum of weight hits.
3. Top-N items per chapter per source.

Items come from the scrapers' public entry points. We DON'T call
scrapers fresh per render — we accept the news from whatever was
loaded on the side (Azi section already fetches them). For
chapter-only contexts (no news loaded), we do a quick `fetch_*`
call but cap results.

Important: this module is pure — no Streamlit imports, no caching.
`app.py` is responsible for caching results in st.session_state.
"""
from __future__ import annotations

from dataclasses import dataclass

from learning.chapter_tags import tags_for


@dataclass
class CrossRef:
    """One cross-reference for a chapter."""
    source: str            # "hackernews" | "github_trending" | "lobsters" | ...
    title: str
    url: str
    summary: str = ""
    score: float = 0.0     # community score (when applicable)


def _score_text(text: str, chapter_id: str) -> float:
    """Sum-of-tag-hits score for a text against a chapter's tags."""
    if not text:
        return 0.0
    haystack = text.lower()
    total = 0.0
    for tag, weight in tags_for(chapter_id):
        if tag in haystack:
            total += weight
    return total


def score_item(item, chapter_id: str) -> float:
    """Score a NewsItem OR a TrendingRepo OR a dict-like object."""
    title = getattr(item, "title", "") or ""
    summary = getattr(item, "summary", "") or ""
    source = getattr(item, "source", "") or ""
    text = f"{title} {summary} {source}"
    return _score_text(text, chapter_id)


def top_for_chapter(
    items: list,
    chapter_id: str,
    *,
    limit: int = 3,
    min_score: float = 0.5,
) -> list[CrossRef]:
    """Score items and return top-N that beat `min_score`."""
    scored: list[CrossRef] = []
    for it in items:
        s = score_item(it, chapter_id)
        if s < min_score:
            continue
        scored.append(
            CrossRef(
                source=getattr(it, "source", "") or "",
                title=getattr(it, "title", "") or "(fără titlu)",
                url=getattr(it, "url", "") or "#",
                summary=getattr(it, "summary", "") or "",
                score=float(getattr(it, "score", 0) or 0),
            )
        )
    scored.sort(key=lambda x: (x.score), reverse=True)
    return scored[:limit]


def fetch_quick_news_for_chapter(chapter_id: str, limit: int = 3) -> list[CrossRef]:
    """Best-effort fetch if no other news loaded. Tries multiple
    sources, fails silently if any single source is down."""
    items = []
    # Lazy import to keep startup fast
    try:
        from scrapers import fetch_hackernews_ai
        items.extend(fetch_hackernews_ai(limit=40) or [])
    except Exception:
        pass
    try:
        from scrapers import fetch_lobsters
        items.extend(fetch_lobsters(limit=20) or [])
    except Exception:
        pass
    try:
        from scrapers import fetch_hf_papers
        items.extend(fetch_hf_papers(limit=15) or [])
    except Exception:
        pass
    try:
        from scrapers import fetch_importai
        items.extend(fetch_importai(limit=10) or [])
    except Exception:
        pass
    return top_for_chapter(items, chapter_id, limit=limit, min_score=0.5)


def fetch_quick_repos_for_chapter(chapter_id: str, limit: int = 2) -> list[CrossRef]:
    """Use findarepo (TrendingRepo objects), which carry real repo metadata."""
    try:
        from scrapers import fetch_findarepo_daily
        repos = fetch_findarepo_daily(limit=15) or []
    except Exception:
        # Fallback: derive repos from github_trending (returns NewsItem w/ title)
        try:
            from scrapers import fetch_github_trending
            repos = fetch_github_trending(limit=20) or []
        except Exception:
            return []
    out = []
    for r in repos:
        name = getattr(r, "name", "") or getattr(r, "title", "")
        desc = getattr(r, "description", "") or ""
        tags = " ".join(getattr(r, "tags", []) or []) if hasattr(r, "tags") else ""
        text = f"{name} {desc} {tags}"
        s = _score_text(text, chapter_id)
        if s < 0.5:
            continue
        out.append(
            CrossRef(
                source="findarepo" if hasattr(r, "tags") else "github_trending",
                title=name,
                url=getattr(r, "url", "#") or "#",
                summary=desc,
            )
        )
    return out[:limit]


def find_prompts_for_chapter(chapter_id: str, prompts_index: list, limit: int = 1) -> list[dict]:
    """Match the prompt-bible index against chapter tags.

    `prompts_index` shape (one entry per prompt):
        {"title": str, "category": str, "difficulty": str, ...}

    Returns up to `limit` matching entries.
    """
    if not prompts_index:
        return []
    tag_set = {t for t, _ in tags_for(chapter_id)}
    matches = []
    for p in prompts_index:
        blob = " ".join([
            str(p.get("title", "")),
            str(p.get("category", "")),
            str(p.get("difficulty", "")),
            " ".join(p.get("tags", []) if isinstance(p.get("tags"), list) else []),
        ]).lower()
        score = sum(1 for t in tag_set if t in blob)
        if score > 0:
            matches.append((score, p))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in matches[:limit]]

"""Lobsters scraper · tech community news, filtered for AI.

Lobsters is a tech-focused community (invite-only, high-signal) with a public
JSON API. Reddit's r/MachineLearning is often blocked by anti-scrape rules, so
Lobsters is our reliable fallback for community AI discussions.

Lobsters tags posts (e.g., "ai", "ml", "llm"). We fetch the hottest feed and
prefer items that carry an AI-related tag, falling back to the full feed if
no AI-tagged stories are present.
"""
import httpx
from datetime import datetime, timezone
from typing import List

from scrapers import NewsItem


LOBSTERS_URL = "https://lobste.rs/hottest.json"
USER_AGENT = "ZiarulDigital/0.3 (AI news aggregator; https://huggingface.co/vrobert94)"

# Tag prefixes we treat as AI-relevant. Lower-case, exact match on full tag.
AI_TAGS = {"ai", "ml", "llm", "nlp", "machine-learning", "deep-learning", "generative-ai"}


def _is_ai_relevant(tags: list[str]) -> bool:
    """Return True if any tag matches the AI tag set."""
    if not tags:
        return False
    return any(t.lower() in AI_TAGS for t in tags)


def fetch_lobsters(limit: int = 12, ai_only: bool = True) -> List[NewsItem]:
    """Fetch hot Lobsters stories, optionally filtered to AI-tagged ones."""
    try:
        resp = httpx.get(
            LOBSTERS_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"[lobsters] fetch failed: {e}")
        return []

    if not isinstance(data, list):
        return []

    items: List[NewsItem] = []
    pool = []

    for story in data:
        tags = story.get("tags") or []
        title = (story.get("title") or "").strip()
        if not title:
            continue

        # Prefer external URL, fallback to Lobsters comments page
        url = story.get("url") or story.get("comments_url") or ""
        if not url:
            continue

        # Parse the ISO 8601 created_at
        created_raw = story.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            published_iso = dt.isoformat()
        except (ValueError, AttributeError):
            published_iso = datetime.now(timezone.utc).isoformat()

        submitter = story.get("submitter_user") or ""
        score = story.get("score", 0)
        comments = story.get("comment_count", 0)
        desc = story.get("description_plain") or story.get("description") or ""

        item_tags = ["lobsters", "community", "discussion"]
        for t in tags:
            item_tags.append(t.lower())

        news_item = NewsItem(
            source="lobsters",
            external_id=story.get("short_id", ""),
            title=title,
            url=url,
            summary=desc[:500] if desc else "",
            published_at=published_iso,
            score=score,
            author=submitter,
            tags=item_tags,
        )

        if ai_only and not _is_ai_relevant(tags):
            pool.append(news_item)  # keep as fallback
        else:
            items.append(news_item)
            if len(items) >= limit:
                break

    # Fallback: if we filtered too aggressively, top up from the non-AI pool
    if len(items) < limit and pool:
        for fallback_item in pool:
            if fallback_item in items:
                continue
            items.append(fallback_item)
            if len(items) >= limit:
                break

    return items


if __name__ == "__main__":
    items = fetch_lobsters(limit=5)
    print(f"Lobsters · {len(items)} stories")
    for it in items:
        print(f"  \u2b06{it.score:>3}  {it.title[:70]}")
        print(f"    {it.url}")
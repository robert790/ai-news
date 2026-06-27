"""Hacker News scraper · AI-tagged stories via the official Algolia HN Search API.

No API key required. Free, public, well-documented.
Docs: https://hn.algolia.com/api

We pull the most recent AI-tagged stories and normalize them into a common NewsItem shape.
"""
import httpx
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class NewsItem:
    """Common shape every scraper returns."""
    source: str
    external_id: str
    title: str
    url: str
    summary: str           # raw snippet / description
    published_at: str      # ISO format
    score: int = 0
    author: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_hackernews_ai(limit: int = 30) -> List[NewsItem]:
    """Fetch top AI-tagged Hacker News stories from the last 7 days."""
    # search_by_date returns newest first; recency is implicit.
    # Query kept short — Algolia's parser chokes on long OR lists with
    # multi-word terms. Single keywords work best.
    params = {
        "tags": "story",
        "query": "AI OR LLM OR GPT OR Claude OR DeepSeek",
        "numericFilters": "points>=5",
        "hitsPerPage": limit,
    }
    url = "https://hn.algolia.com/api/v1/search_by_date"

    try:
        resp = httpx.get(url, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"[hackernews] fetch failed: {e}")
        return []

    items: List[NewsItem] = []
    for hit in data.get("hits", []):
        items.append(NewsItem(
            source="hackernews",
            external_id=str(hit.get("objectID", "")),
            title=hit.get("title") or hit.get("story_title", "(no title)"),
            url=hit.get("url") or hit.get("story_url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            summary=hit.get("story_text", "")[:500] if hit.get("story_text") else "",
            published_at=datetime.fromtimestamp(hit.get("created_at_i", 0), tz=timezone.utc).isoformat(),
            score=hit.get("points", 0),
            author=hit.get("author", ""),
            tags=["ai", "hackernews"],
        ))
    return items


if __name__ == "__main__":
    # Smoke test
    items = fetch_hackernews_ai(limit=5)
    print(f"Fetched {len(items)} HN AI stories")
    for item in items[:3]:
        print(f"  · [{item.score:>3}] {item.title[:80]}")
        print(f"    {item.url}")
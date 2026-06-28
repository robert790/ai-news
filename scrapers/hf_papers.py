"""HuggingFace Daily Papers scraper · top research papers trending today.

Uses HuggingFace's public JSON API at huggingface.co/api/daily_papers.
Free, no auth required. Returns papers ranked by community upvotes.

Each item in the response has:
  - id (e.g. "arxiv:2406.01234")
  - title
  - summary (abstract)
  - upvotes
  - authors (list of {name})
  - publishedAt
  - githubRepo (optional, if authors open-sourced code)
  - ai_summary / ai_keywords (HF-generated, sometimes)

We normalize into the common NewsItem shape so it flows through the same
DeepSeek summarization pipeline as the other sources.
"""
import httpx
from datetime import datetime, timezone
from typing import List

from scrapers import NewsItem


API_URL = "https://huggingface.co/api/daily_papers"


def fetch_hf_papers(limit: int = 12) -> List[NewsItem]:
    """Fetch today's top HuggingFace papers (ranked by upvotes)."""
    try:
        resp = httpx.get(API_URL, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"[hf_papers] fetch failed: {e}")
        return []

    if not isinstance(data, list):
        return []

    items: List[NewsItem] = []
    for entry in data[:limit]:
        # Each entry has the same fields as `paper` plus metadata.
        # Prefer the nested `paper` block when present.
        paper = entry.get("paper") or entry
        title = paper.get("title") or entry.get("title") or "(no title)"
        pid = paper.get("id") or entry.get("id") or ""
        summary = paper.get("summary") or entry.get("summary") or ""

        # URL: link to the HF paper page if id is arxiv-style, else /papers/<id>
        if pid.startswith("arxiv:"):
            arxiv_id = pid.replace("arxiv:", "")
            url = f"https://huggingface.co/papers/{arxiv_id}"
        else:
            url = f"https://huggingface.co/papers/{pid}"

        # Authors: join the names if present
        authors = paper.get("authors") or entry.get("authors") or []
        if isinstance(authors, list) and authors and isinstance(authors[0], dict):
            author_str = ", ".join(a.get("name", "") for a in authors[:3])
            if len(authors) > 3:
                author_str += f" +{len(authors) - 3}"
        else:
            author_str = ""

        # Published date — `publishedAt` is sometimes present
        published_raw = paper.get("publishedAt") or entry.get("publishedAt")
        if published_raw:
            try:
                # Format is usually ISO 8601
                dt = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
                published_iso = dt.isoformat()
            except ValueError:
                published_iso = datetime.now(timezone.utc).isoformat()
        else:
            published_iso = datetime.now(timezone.utc).isoformat()

        items.append(NewsItem(
            source="huggingface",
            external_id=pid,
            title=title,
            url=url,
            summary=summary[:1000],
            published_at=published_iso,
            score=paper.get("upvotes", 0) or entry.get("upvotes", 0),
            author=author_str,
            tags=["research", "paper", "arxiv"],
        ))

    return items


if __name__ == "__main__":
    items = fetch_hf_papers(limit=5)
    print(f"HF Daily Papers · {len(items)} papers")
    for it in items:
        print(f"  · \u2b06{it.score:>3}  {it.title[:70]}")
        print(f"    {it.url}")
"""Import AI newsletter scraper · Jack Clark's weekly AI policy + research digest.

Import AI is one of the most respected AI newsletters. We pull the public RSS
feed at importai.substack.com/feed and parse it with a lightweight regex walker.

Substack wraps content in CDATA blocks, so we strip those before tag-stripping.
Each item has:
  - title
  - link
  - pubDate (RFC 822)
  - description (HTML snippet)
  - guid
"""
import httpx
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List

from scrapers import NewsItem


FEED_URL = "https://importai.substack.com/feed"

# Match a CDATA block (e.g. "<![CDATA[ ... ]]>")
_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
# Match a regular HTML/XML tag
_TAG_RE = re.compile(r"<[^>]+>")
# Collapse whitespace
_WS_RE = re.compile(r"\s+")


def _strip_all(s: str) -> str:
    """Strip CDATA wrappers, HTML tags, and collapse whitespace."""
    if not s:
        return ""
    s = _CDATA_RE.sub(r"\1", s)  # unwrap CDATA
    s = _TAG_RE.sub(" ", s)       # drop tags
    s = _WS_RE.sub(" ", s).strip()
    return s


def _extract_items(xml: str) -> list[dict]:
    """Crack open the RSS XML with a regex walker."""
    items = []
    for m in re.finditer(r"<item>(.*?)</item>", xml, re.DOTALL):
        block = m.group(1)

        def _find(pattern: str) -> str:
            mm = re.search(pattern, block, re.DOTALL)
            return mm.group(1).strip() if mm else ""

        items.append({
            "title": _strip_all(_find(r"<title>(.*?)</title>")),
            "link": _find(r"<link>(.*?)</link>"),
            "pubDate": _find(r"<pubDate>(.*?)</pubDate>"),
            "description": _strip_all(_find(r"<description>(.*?)</description>")),
            "guid": _find(r"<guid[^>]*>(.*?)</guid>"),
        })
    return items


def fetch_importai(limit: int = 8) -> List[NewsItem]:
    """Fetch the latest Import AI newsletter issues."""
    try:
        resp = httpx.get(FEED_URL, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[importai] fetch failed: {e}")
        return []

    raw_items = _extract_items(resp.text)
    items: List[NewsItem] = []

    for raw in raw_items[:limit]:
        # Parse the RFC 822 date format from RSS
        published_iso = datetime.now(timezone.utc).isoformat()
        if raw["pubDate"]:
            try:
                dt = parsedate_to_datetime(raw["pubDate"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                published_iso = dt.isoformat()
            except (TypeError, ValueError):
                pass

        title = raw["title"]
        if not title:
            continue

        items.append(NewsItem(
            source="importai",
            external_id=raw["guid"] or raw["link"] or title,
            title=title,
            url=raw["link"],
            summary=raw["description"][:1000],
            published_at=published_iso,
            score=0,
            author="Jack Clark",
            tags=["newsletter", "analysis", "policy"],
        ))

    return items


if __name__ == "__main__":
    items = fetch_importai(limit=3)
    print(f"Import AI · {len(items)} issues")
    for it in items:
        print(f"  \u00b7 {it.title[:80]}")
        print(f"    {it.url}")
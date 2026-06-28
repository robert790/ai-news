"""GitHub Trending scraper · top repositories trending today on GitHub.

GitHub serves a public trending page at github.com/trending that ranks repos by
their recent star-velocity. We scrape the HTML with BeautifulSoup and extract
each repo card.

Each card has:
  - owner/name (the h2 anchor)
  - description (the <p> tag)
  - primary language (itemprop="programmingLanguage")
  - total stars (the text inside the stargazers link)
  - stars today (a text node like "1,183 stars today")

We normalize into the same NewsItem shape used by other scrapers so the
DeepSeek summarizer and the Streamlit renderer can treat them uniformly.
"""
import re
import httpx
from datetime import datetime, timezone
from typing import List

from bs4 import BeautifulSoup

from scrapers import NewsItem


TRENDING_URL = "https://github.com/trending"


def fetch_github_trending(since: str = "daily", limit: int = 12) -> List[NewsItem]:
    """Fetch trending GitHub repos. `since` can be: daily | weekly | monthly."""
    url = f"{TRENDING_URL}?since={since}"

    try:
        resp = httpx.get(url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[github_trending] fetch failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items: List[NewsItem] = []

    for article in soup.find_all("article", class_="Box-row"):
        # --- Repo name (h2 > a /owner/name) ---
        h2 = article.find("h2")
        if not h2:
            continue
        anchor = h2.find("a")
        if not anchor or not anchor.get("href"):
            continue
        href = anchor["href"].strip("/")
        full_name = href  # "owner/repo"

        # --- Description (optional) ---
        desc_p = article.find("p", class_="col-9")
        description = desc_p.get_text(strip=True) if desc_p else ""

        # --- Language (itemprop="programmingLanguage" span) ---
        lang_span = article.find("span", attrs={"itemprop": "programmingLanguage"})
        language = lang_span.get_text(strip=True) if lang_span else ""

        # --- Total stars (the stargazers link's text content) ---
        total_stars_anchor = article.find(
            "a", href=re.compile(r"/[^/]+/[^/]+/stargazers$")
        )
        total_stars = total_stars_anchor.get_text(strip=True) if total_stars_anchor else ""

        # --- Stars today (a text node like "1,183 stars today") ---
        today_text = ""
        stars_node = article.find(
            string=lambda t: t and "stars today" in t
        )
        if stars_node:
            today_text = stars_node.strip()

        # Parse the star delta for the score
        score = 0
        m = re.search(r"([\d,]+)\s*stars?\s*today", today_text.replace(",", ""))
        if not m:
            m = re.search(r"([\d,]+)", today_text.replace(",", ""))
        if m:
            try:
                score = int(m.group(1))
            except ValueError:
                score = 0

        # Build the summary text
        summary_bits = []
        if description:
            summary_bits.append(description)
        meta_line = []
        if language:
            meta_line.append(language)
        if total_stars:
            meta_line.append(f"{total_stars} total")
        if today_text:
            meta_line.append(today_text)
        if meta_line:
            summary_bits.append(" · ".join(meta_line))
        summary = "\n".join(summary_bits)

        tags = ["github", "repo", "trending"]
        if language:
            tags.append(language.lower())

        items.append(NewsItem(
            source="github_trending",
            external_id=full_name,
            title=full_name,
            url=f"https://github.com/{full_name}",
            summary=summary,
            published_at=datetime.now(timezone.utc).isoformat(),
            score=score,
            author="",
            tags=tags,
        ))

        if len(items) >= limit:
            break

    return items


if __name__ == "__main__":
    items = fetch_github_trending(since="daily", limit=5)
    print(f"GitHub Trending · {len(items)} repos today")
    for it in items:
        print(f"  \u2b06{it.score:>5}  {it.title[:40]}")
        print(f"      {it.summary[:80]}")
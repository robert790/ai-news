"""findarepo.com scraper · daily top 10 fastest-growing GitHub repos.

findarepo measures its own 7-day star-growth deltas. We fetch the latest
digest page (discovered via RSS feed) and parse it with BeautifulSoup.

The page has two sections:
- Main table: top 10 repos with rank, repo link, description, stars, growth, language
- "Skills & MCP movers" section: a smaller list (LLM-tooling side)

We only want the main top-10.
"""
import re
import httpx
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup

from scrapers import NewsItem


@dataclass
class TrendingRepo:
    """A single repo from findarepo's daily digest."""
    rank: int
    full_name: str        # e.g. "DietrichGebert/ponytail"
    url: str              # direct link to GitHub repo
    description: str
    stars: str            # raw string like "61k"
    growth: str           # raw string like "+20k"
    language: str

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "full_name": self.full_name,
            "url": self.url,
            "description": self.description,
            "stars": self.stars,
            "growth": self.growth,
            "language": self.language,
        }


def _discover_latest_digest_url() -> str:
    """Read the RSS feed and return the link of the most recent digest."""
    feed_url = "https://findarepo.com/feed.xml"
    try:
        resp = httpx.get(feed_url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[findarepo] feed fetch failed: {e}")
        return ""

    xml = resp.text
    m = re.search(r"<item>.*?<link>(https?://[^<]+)</link>", xml, re.DOTALL)
    return m.group(1).strip() if m else ""


def _parse_digest(html: str) -> List[TrendingRepo]:
    """Parse the top-10 table from a digest page using BeautifulSoup.

    Each repo sits in a <tr> with five <td> cells: rank, repo+desc, stars, growth, language.
    """
    soup = BeautifulSoup(html, "html.parser")
    repos: List[TrendingRepo] = []

    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    for row in rows[1:]:  # skip header row
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        # Cell 1: rank
        try:
            rank = int(cells[0].get_text(strip=True))
        except ValueError:
            continue

        # Cell 2: repo link + description
        # findarepo links to either /repo/owner/name/ (internal) or full github.com URLs.
        anchor = cells[1].find("a", href=re.compile(r"(/repo/|github\.com/)"))
        if not anchor:
            continue
        href = anchor["href"]
        if "/repo/" in href:
            full_name = href.replace("/repo/", "").strip("/")
        else:
            # github.com/owner/name → owner/name
            full_name = href.split("github.com/")[-1].strip("/")

        desc_span = cells[1].find("span", class_="row-desc")
        description = desc_span.get_text(strip=True) if desc_span else ""

        # Cell 3: stars, e.g. "★ 61k"
        stars_text = cells[2].get_text(strip=True)
        star_match = re.search(r'([\d.]+k?)', stars_text)
        stars = star_match.group(1) if star_match else "?"

        # Cell 4: growth, e.g. "+20k /7d"
        delta_span = cells[3].find("span", class_="delta")
        growth = delta_span.get_text(strip=True).lstrip("+") if delta_span else "?"

        # Cell 5: language
        language = cells[4].get_text(strip=True) or "—"

        repos.append(TrendingRepo(
            rank=rank,
            full_name=full_name,
            url=f"https://github.com/{full_name}",
            description=description,
            stars=stars,
            growth=growth,
            language=language,
        ))

        if len(repos) >= 10:
            break

    return repos


def fetch_findarepo_daily(limit: int = 10) -> List[TrendingRepo]:
    """Fetch today's top trending GitHub repos from findarepo.com."""
    digest_url = _discover_latest_digest_url()
    if not digest_url:
        return []

    try:
        resp = httpx.get(digest_url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[findarepo] digest fetch failed: {e}")
        return []

    repos = _parse_digest(resp.text)
    return repos[:limit]


# ----------------------------------------------------------------------
# NewsItem compatibility — wrap repos as news items so they can flow
# through the existing summarization + feed pipeline.

def repos_to_news_items(repos: List[TrendingRepo]) -> List[NewsItem]:
    """Convert trending repos to NewsItem shape so they fit in the same feed."""
    items = []
    for r in repos:
        items.append(NewsItem(
            source="findarepo",
            external_id=f"findarepo:{r.full_name}",
            title=f"{r.full_name}",
            url=r.url,
            summary=r.description,
            published_at=datetime.now(timezone.utc).isoformat(),
            score=0,
            author="",
            tags=["repo", "github", r.language.lower()] if r.language and r.language != "—" else ["repo", "github"],
        ))
    return items


if __name__ == "__main__":
    repos = fetch_findarepo_daily(limit=10)
    print(f"findarepo · {len(repos)} trending repos today")
    for r in repos:
        print(f"  {r.rank:>2}. {r.full_name:<35} ★{r.stars:<6} +{r.growth:<6}/7d  {r.language}")
"""__init__ for scrapers package.

Each scraper module returns its own data type, plus a list of NewsItem for
sources that fit the common news-feed shape. findarepo returns a specialized
TrendingRepo list because the repo metadata (rank, growth) is too specific
to fold into a generic news item.

Reddit was originally on the list but is now blocked at the network layer
for many IPs. Lobsters (a tech-focused community) is a reliable alternative
with AI-tagged stories.
"""
from .hackernews import fetch_hackernews_ai, NewsItem
from .findarepo import fetch_findarepo_daily, repos_to_news_items, TrendingRepo
from .hf_papers import fetch_hf_papers
from .lobsters import fetch_lobsters
from .github_trending import fetch_github_trending
from .importai import fetch_importai

__all__ = [
    # Core data shape
    "NewsItem",
    "TrendingRepo",
    # Fetchers
    "fetch_hackernews_ai",
    "fetch_findarepo_daily",
    "fetch_hf_papers",
    "fetch_lobsters",
    "fetch_github_trending",
    "fetch_importai",
    # Converters
    "repos_to_news_items",
]
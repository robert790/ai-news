"""__init__ for scrapers package."""
from .hackernews import fetch_hackernews_ai, NewsItem

__all__ = ["fetch_hackernews_ai", "NewsItem"]
"""
RSS and Atom feed ingestion provider.
Parses open syndicated feeds from permitted publishers with validation and error handling.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
import logging
import httpx
import feedparser

from backend.app.ingestion.base import NewsProvider
from backend.app.ml.preprocessor import clean_text

logger = logging.getLogger(__name__)

DEFAULT_FEEDS = [
    {
        "name": "BBC World News",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml"
    },
    {
        "name": "NPR News",
        "url": "https://feeds.npr.org/1001/rss.xml"
    },
    {
        "name": "Phys.org Science",
        "url": "https://phys.org/rss-feed/science-news/"
    }
]


class RSSNewsProvider(NewsProvider):
    """
    Ingests live articles from standard RSS 2.0 and Atom feeds.
    """
    @property
    def provider_name(self) -> str:
        return "rss"

    def fetch_articles(
        self,
        query: Optional[str] = None,
        limit: int = 25,
        feed_url: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from configured RSS feed or default feeds.
        """
        target_feeds = [{"name": "Custom RSS", "url": feed_url}] if feed_url else DEFAULT_FEEDS
        articles: List[Dict[str, Any]] = []

        headers = {
            "User-Agent": "NewsEventDetectionResearchBot/1.0 (+http://localhost:8000/research)"
        }

        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            for feed_info in target_feeds:
                try:
                    response = client.get(feed_info["url"])
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch feed {feed_info['url']}: HTTP {response.status_code}")
                        continue

                    parsed = feedparser.parse(response.content)
                    feed_title = parsed.feed.get("title", feed_info["name"])

                    for entry in parsed.entries:
                        headline = clean_text(entry.get("title", ""))
                        if not headline or len(headline) < 5:
                            continue

                        # Extract description / body
                        summary = entry.get("summary", "") or entry.get("description", "")
                        body = clean_text(summary)
                        if not body:
                            body = headline # Fallback if summary empty

                        # Apply topic query filter if requested
                        if query:
                            q_lower = query.lower()
                            if q_lower not in headline.lower() and q_lower not in body.lower():
                                continue

                        # Parse publication date
                        pub_date = None
                        if hasattr(entry, "published"):
                            try:
                                pub_date = parsedate_to_datetime(entry.published)
                            except Exception:
                                pass
                        elif hasattr(entry, "updated"):
                            try:
                                pub_date = parsedate_to_datetime(entry.updated)
                            except Exception:
                                pass

                        if pub_date is None:
                            pub_date = datetime.now(timezone.utc)
                        else:
                            # Normalize to UTC
                            if pub_date.tzinfo is None:
                                pub_date = pub_date.replace(tzinfo=timezone.utc)
                            else:
                                pub_date = pub_date.astimezone(timezone.utc)

                        link = entry.get("link", "")
                        ext_id = entry.get("id", link)

                        articles.append({
                            "headline": headline,
                            "body": body,
                            "source_name": feed_title,
                            "source_url": link,
                            "published_at": pub_date,
                            "external_id": ext_id,
                            "language": "en"
                        })

                        if len(articles) >= limit:
                            return articles

                except Exception as e:
                    logger.error(f"Error reading RSS feed '{feed_info['url']}': {e}")

        return articles

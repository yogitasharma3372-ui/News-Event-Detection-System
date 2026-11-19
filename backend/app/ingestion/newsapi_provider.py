"""
NewsAPI provider implementation.
Connects to NewsAPI when credentials are provided in settings or environment.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
import httpx

from backend.app.ingestion.base import NewsProvider
from backend.app.ml.preprocessor import clean_text
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class NewsAPIProvider(NewsProvider):
    """
    Ingests live articles from NewsAPI.org v2 endpoints.
    """
    @property
    def provider_name(self) -> str:
        return "newsapi"

    def fetch_articles(
        self,
        query: Optional[str] = None,
        limit: int = 25,
        api_key: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        active_key = api_key or settings.NEWSAPI_KEY
        if not active_key:
            raise ValueError(
                "NewsAPI requires an API key. Please configure NEWSAPI_KEY in Settings or your .env file. "
                "You can also use the open RSS provider or upload local datasets without any API key."
            )

        url = f"{settings.NEWS_API_BASE_URL}/top-headlines" if not query else f"{settings.NEWS_API_BASE_URL}/everything"
        params: Dict[str, Any] = {
            "apiKey": active_key,
            "pageSize": min(limit, 100),
            "language": "en"
        }
        if query:
            params["q"] = query
        else:
            params["country"] = "us"

        articles: List[Dict[str, Any]] = []

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params)
                data = resp.json()

                if resp.status_code != 200 or data.get("status") != "ok":
                    msg = data.get("message", f"NewsAPI returned status {resp.status_code}")
                    raise RuntimeError(f"NewsAPI error: {msg}")

                raw_articles = data.get("articles", [])
                for item in raw_articles:
                    headline = clean_text(item.get("title", ""))
                    if not headline or headline == "[Removed]":
                        continue

                    body = clean_text(item.get("content", "") or item.get("description", ""))
                    if not body:
                        body = headline

                    source_name = item.get("source", {}).get("name", "NewsAPI Source")
                    source_url = item.get("url")

                    # Parse publishedAt ISO-8601
                    raw_time = item.get("publishedAt")
                    pub_date = datetime.now(timezone.utc)
                    if raw_time:
                        try:
                            pub_date = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                        except Exception:
                            pass

                    articles.append({
                        "headline": headline,
                        "body": body,
                        "source_name": source_name,
                        "source_url": source_url,
                        "published_at": pub_date,
                        "external_id": source_url,
                        "language": "en"
                    })

                    if len(articles) >= limit:
                        break

        except httpx.RequestError as e:
            logger.error(f"Network error querying NewsAPI: {e}")
            raise RuntimeError(f"Network error connecting to NewsAPI: {e}")

        return articles

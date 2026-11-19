"""
Abstract Base Class for News Ingestion Providers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class NewsProvider(ABC):
    """
    Standard interface contract for news ingestion providers (RSS, NewsAPI, Files).
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier (e.g. 'rss', 'newsapi', 'file')."""
        pass

    @abstractmethod
    def fetch_articles(
        self,
        query: Optional[str] = None,
        limit: int = 25,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch normalized articles from provider.
        Each returned article dict must include:
        - headline (str)
        - body (str)
        - source_name (str)
        - source_url (str)
        - published_at (datetime)
        - external_id (Optional[str])
        """
        pass

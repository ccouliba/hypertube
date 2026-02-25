"""
Abstract base class for content providers
"""
from abc import (ABC, abstractmethod)


class Provider(ABC):
    """Abstract base class for content providers"""
    
    @abstractmethod
    def search(self, query: str) -> list[dict]:
        """Search for content by query"""
        pass
    
    @abstractmethod
    def get_popular(self) -> list[dict]:
        """Get popular content without query"""
        pass
    
    def _handle_request_error(
            self,
            error: Exception,
            provider_name: str
        ) -> list[dict]:
        """Centralized Provider error handling"""
        print(f"{provider_name} Provider error: {error}")
        return []
    
    def _format_result(
        self,
        data: dict,
        provider: str,
        content_type: str,
        torrents: list[dict]
    ) -> dict:
        """Generic result formatter for all providers"""
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "year": data.get("year"),
            "rating": data.get("rating"),
            "download_count": data.get("download_count"),
            "genres": data.get("genres", ["TV Show"] if content_type == "tv_show" else []),
            "synopsis": data.get("synopsis"),
            "thumbnail": data.get("thumbnail"),
            "large_cover": data.get("large_cover"),
            "language": data.get("language", "en"),
            "content_type": content_type,
            "torrents": torrents,
            "provider": provider
        }

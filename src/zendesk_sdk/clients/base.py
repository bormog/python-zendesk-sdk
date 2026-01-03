"""Base client class for all Zendesk API clients."""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar

from async_lru import alru_cache

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient

T = TypeVar("T")


class BaseClient:
    """Base class for all API resource clients.

    Provides common HTTP methods and shared functionality.
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize the client.

        Args:
            http_client: Shared HTTP client instance
            cache_config: Optional cache configuration
        """
        self._http = http_client
        self._cache_config = cache_config

    def __hash__(self) -> int:
        """Hash based on subdomain for cache key differentiation."""
        return hash(self._http.config.subdomain)

    def __eq__(self, other: object) -> bool:
        """Equality based on subdomain."""
        if not isinstance(other, BaseClient):
            return NotImplemented
        return self._http.config.subdomain == other._http.config.subdomain

    def _create_cached_method(
        self,
        method: Callable[..., T],
        maxsize: int,
        ttl: int,
    ) -> Callable[..., T]:
        """Create a cached version of an async method.

        If caching is disabled, returns the original method unchanged.

        Args:
            method: The async method to cache
            maxsize: Maximum cache size
            ttl: Time-to-live in seconds

        Returns:
            Cached method or original if caching disabled
        """
        if self._cache_config is None or not self._cache_config.enabled:
            return method
        return alru_cache(maxsize=maxsize, ttl=ttl)(method)

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        return await self._http.get(path, params=params, max_retries=max_retries)

    async def _post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        return await self._http.post(path, json=json, max_retries=max_retries)

    async def _put(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._http.put(path, json=json, max_retries=max_retries)

    async def _delete(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request."""
        return await self._http.delete(path, json=json, max_retries=max_retries)


class HelpCenterBaseClient(BaseClient):
    """Base class for Help Center API clients.

    Automatically prepends 'help_center/' to all paths.
    """

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make GET request to Help Center API."""
        return await self._http.get(f"help_center/{path}", params=params, max_retries=max_retries)

    async def _post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make POST request to Help Center API."""
        return await self._http.post(f"help_center/{path}", json=json, max_retries=max_retries)

    async def _put(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make PUT request to Help Center API."""
        return await self._http.put(f"help_center/{path}", json=json, max_retries=max_retries)

    async def _delete(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request to Help Center API."""
        return await self._http.delete(f"help_center/{path}", json=json, max_retries=max_retries)

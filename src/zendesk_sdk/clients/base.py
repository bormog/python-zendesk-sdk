"""Base client class for all Zendesk API clients."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..http_client import HTTPClient


class BaseClient:
    """Base class for all API resource clients.

    Provides common HTTP methods and shared functionality.
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize the client.

        Args:
            http_client: Shared HTTP client instance
        """
        self._http = http_client

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

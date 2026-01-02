"""HTTP client for Zendesk API with retry, rate limiting, and error handling."""

import asyncio
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from .config import ZendeskConfig
from .exceptions import (
    ZendeskHTTPException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
    create_exception_from_response,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """Async HTTP client for Zendesk API with advanced error handling and retry logic."""

    def __init__(self, config: ZendeskConfig) -> None:
        """Initialize HTTP client with configuration.

        Args:
            config: Zendesk configuration containing auth and connection settings
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._closed = False

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create httpx async client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> httpx.AsyncClient:
        """Create configured httpx async client."""
        auth = httpx.BasicAuth(username=self.config.auth_tuple[0], password=self.config.auth_tuple[1])

        headers = {
            "User-Agent": "python-zendesk-sdk/0.1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        return httpx.AsyncClient(
            auth=auth,
            headers=headers,
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic and rate limiting handling."""
        if max_retries is None:
            max_retries = self.config.max_retries

        last_exception: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                # Make the actual request
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                )

                # Handle different response types
                retry_info = await self._handle_response(response, attempt, max_retries)
                if retry_info:
                    last_exception = retry_info
                    continue
                return response

            except httpx.TimeoutException:
                last_exception = await self._handle_timeout_exception(attempt, max_retries)
                if last_exception:
                    continue

            except (httpx.NetworkError, httpx.ConnectError) as e:
                last_exception = await self._handle_network_exception(e, attempt, max_retries)
                if last_exception:
                    continue

        # This shouldn't happen, but just in case
        if last_exception:
            raise last_exception
        raise ZendeskHTTPException("Unexpected error: no response after retries", 0)

    async def _handle_response(self, response: httpx.Response, attempt: int, max_retries: int) -> Optional[Exception]:
        """Handle HTTP response based on status code. Return exception if should retry, None if success."""
        # Handle rate limiting (429)
        if response.status_code == 429:
            return await self._handle_rate_limit(response, attempt, max_retries)

        # Handle server errors (5xx) - retry these
        if 500 <= response.status_code < 600:
            return await self._handle_server_error(response, attempt, max_retries)

        # Handle other HTTP errors (4xx, etc.) - don't retry these
        if not response.is_success:
            raise create_exception_from_response(response)

        # Success!
        return None

    async def _handle_rate_limit(self, response: httpx.Response, attempt: int, max_retries: int) -> Optional[Exception]:
        """Handle rate limiting response. Return exception if should retry, otherwise raise."""
        rate_limit_exc = ZendeskRateLimitException.from_response(response)

        if attempt < max_retries:
            # Wait based on retry-after header or default backoff
            wait_time = rate_limit_exc.retry_after or self._calculate_backoff(attempt)
            logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
            await asyncio.sleep(wait_time)
            return rate_limit_exc
        else:
            raise rate_limit_exc

    async def _handle_server_error(
        self, response: httpx.Response, attempt: int, max_retries: int
    ) -> Optional[Exception]:
        """Handle server error response. Return exception if should retry, otherwise raise."""
        server_error = create_exception_from_response(response)

        if attempt < max_retries:
            wait_time = self._calculate_backoff(attempt)
            logger.warning(
                f"Server error {response.status_code}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(wait_time)
            return server_error
        else:
            raise server_error

    async def _handle_timeout_exception(self, attempt: int, max_retries: int) -> Optional[ZendeskTimeoutException]:
        """Handle timeout exception. Return exception if should retry, otherwise raise."""
        timeout_exc = ZendeskTimeoutException(f"Request timed out after {self.config.timeout}s", self.config.timeout)

        if attempt < max_retries:
            wait_time = self._calculate_backoff(attempt)
            logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(wait_time)
            return timeout_exc
        else:
            raise timeout_exc

    async def _handle_network_exception(
        self, exc: Exception, attempt: int, max_retries: int
    ) -> Optional[ZendeskHTTPException]:
        """Handle network exception. Return exception if should retry, otherwise raise."""
        network_exc = ZendeskHTTPException(f"Network error: {str(exc)}", 0)

        if attempt < max_retries:
            wait_time = self._calculate_backoff(attempt)
            logger.warning(f"Network error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {exc}")
            await asyncio.sleep(wait_time)
            return network_exc
        else:
            raise network_exc

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        return min(2**attempt, 60.0)  # Max 60 seconds

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        if path.startswith("http"):
            return path
        return urljoin(f"{self.config.endpoint}/", path.lstrip("/"))

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make GET request and return JSON response."""
        url = self._build_url(path)
        response = await self._make_request_with_retry("GET", url, params=params, max_retries=max_retries)
        return response.json()

    async def post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make POST request and return JSON response."""
        url = self._build_url(path)
        response = await self._make_request_with_retry("POST", url, json=json, max_retries=max_retries)
        return response.json()

    async def put(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make PUT request and return JSON response."""
        url = self._build_url(path)
        response = await self._make_request_with_retry("PUT", url, json=json, max_retries=max_retries)
        return response.json()

    async def delete(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request and return JSON response if any.

        Args:
            path: API endpoint path
            json: Optional request body (some Zendesk endpoints like tags require this)
            max_retries: Override default retry count

        Returns:
            JSON response from API if any, None for empty responses
        """
        url = self._build_url(path)
        response = await self._make_request_with_retry("DELETE", url, json=json, max_retries=max_retries)

        # Some DELETE requests return empty responses
        if response.content:
            return response.json()
        return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._closed:
            await self._client.aclose()
            self._closed = True

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit."""
        await self.close()

    def __del__(self) -> None:
        """Destructor to ensure client is closed."""
        if self._client and not self._closed:
            # Can't call async method in __del__, so we log a warning
            logger.warning("HTTPClient was not properly closed. Use 'async with' or call close() explicitly.")

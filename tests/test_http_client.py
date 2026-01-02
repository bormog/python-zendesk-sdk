"""Tests for HTTP client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from zendesk_sdk.config import ZendeskConfig
from zendesk_sdk.exceptions import (
    ZendeskHTTPException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
)
from zendesk_sdk.http_client import HTTPClient


class TestHTTPClient:
    """Test cases for HTTPClient."""

    def test_init(self):
        """Test HTTPClient initialization."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        client = HTTPClient(config)

        assert client.config == config
        assert client._client is None
        assert not client._closed

    def test_build_url(self):
        """Test URL building from paths."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        client = HTTPClient(config)

        # Test relative path
        assert client._build_url("users.json") == "https://test.zendesk.com/api/v2/users.json"

        # Test path with leading slash
        assert client._build_url("/users.json") == "https://test.zendesk.com/api/v2/users.json"

        # Test full URL (should not change)
        full_url = "https://example.com/api/test"
        assert client._build_url(full_url) == full_url

    def test_calculate_backoff(self):
        """Test exponential backoff calculation."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        client = HTTPClient(config)

        assert client._calculate_backoff(0) == 1.0
        assert client._calculate_backoff(1) == 2.0
        assert client._calculate_backoff(2) == 4.0
        assert client._calculate_backoff(3) == 8.0
        # Should cap at 60 seconds
        assert client._calculate_backoff(10) == 60.0

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limit exception when max retries exceeded."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123", max_retries=1)
        http_client = HTTPClient(config)

        # Mock rate limited response
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"retry-after": "60"}
        rate_limit_response.json.return_value = {"description": "Rate limit exceeded"}

        # Mock the _client attribute directly and return it from client property
        mock_httpx_client = AsyncMock()
        http_client._client = mock_httpx_client
        with patch.object(http_client, "_client", mock_httpx_client) as mock_client:
            mock_client.request = AsyncMock(return_value=rate_limit_response)
            with patch("asyncio.sleep", new_callable=AsyncMock):

                with pytest.raises(ZendeskRateLimitException) as exc_info:
                    await http_client.get("users.json")

                assert exc_info.value.status_code == 429
                assert exc_info.value.retry_after == 60
                assert mock_client.request.call_count == 2  # Initial + 1 retry

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Test timeout exception when max retries exceeded."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123", max_retries=1)
        http_client = HTTPClient(config)

        # Mock the _client attribute directly and return it from client property
        mock_httpx_client = AsyncMock()
        http_client._client = mock_httpx_client
        with patch.object(http_client, "_client", mock_httpx_client) as mock_client:
            mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
            with patch("asyncio.sleep", new_callable=AsyncMock):

                with pytest.raises(ZendeskTimeoutException) as exc_info:
                    await http_client.get("users.json")

                assert "Request timed out after 30.0s" in str(exc_info.value)
                assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_client_error_no_retry(self):
        """Test that 4xx errors don't trigger retries."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        http_client = HTTPClient(config)

        # Mock 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.is_success = False
        error_response.json.return_value = {"error": "Not found"}

        # Mock the _client attribute directly and return it from client property
        mock_httpx_client = AsyncMock()
        http_client._client = mock_httpx_client
        with patch.object(http_client, "_client", mock_httpx_client) as mock_client:
            mock_client.request = AsyncMock(return_value=error_response)

            with pytest.raises(ZendeskHTTPException) as exc_info:
                await http_client.get("users/999.json")

            assert exc_info.value.status_code == 404
            # Should only be called once (no retries for 4xx)
            assert mock_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close functionality."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        http_client = HTTPClient(config)

        # Create a mock client
        mock_httpx_client = AsyncMock()
        http_client._client = mock_httpx_client

        await http_client.close()

        assert http_client._closed
        mock_httpx_client.aclose.assert_called_once()

    def test_destructor_warning(self, caplog):
        """Test destructor logs warning when client not properly closed."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        http_client = HTTPClient(config)

        # Create a mock client to simulate unclosed state
        http_client._client = Mock()
        http_client._closed = False

        # Trigger destructor
        del http_client

        # Check that warning was logged
        assert "HTTPClient was not properly closed" in caplog.text

    @pytest.mark.asyncio
    async def test_custom_max_retries(self):
        """Test custom max_retries parameter overrides config."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123", max_retries=3)
        http_client = HTTPClient(config)

        # Mock server error
        server_error_response = Mock()
        server_error_response.status_code = 500
        server_error_response.is_success = False
        server_error_response.json.return_value = {"error": "Server error"}

        # Mock the _client attribute directly and return it from client property
        mock_httpx_client = AsyncMock()
        http_client._client = mock_httpx_client
        with patch.object(http_client, "_client", mock_httpx_client) as mock_client:
            mock_client.request = AsyncMock(return_value=server_error_response)
            with patch("asyncio.sleep", new_callable=AsyncMock):

                with pytest.raises(ZendeskHTTPException):
                    # Override max_retries to 1 (instead of config's 3)
                    await http_client.get("users.json", max_retries=1)

                # Should be called initial + 1 retry (not 3)
                assert mock_client.request.call_count == 2

"""Tests for exception classes."""

import httpx

from zendesk_sdk.exceptions import (
    ZendeskAuthException,
    ZendeskBaseException,
    ZendeskHTTPException,
    ZendeskPaginationException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
    ZendeskValidationException,
    create_exception_from_response,
)


class TestZendeskBaseException:
    """Test cases for ZendeskBaseException."""

    def test_base_exception(self):
        """Test basic exception creation."""
        exc = ZendeskBaseException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"


class TestZendeskHTTPException:
    """Test cases for ZendeskHTTPException."""

    def test_http_exception(self):
        """Test HTTP exception creation."""
        exc = ZendeskHTTPException("Not found", 404)
        assert str(exc) == "HTTP 404: Not found"
        assert exc.status_code == 404
        assert exc.message == "Not found"

    def test_from_response_with_json_error(self):
        """Test creating exception from response with JSON error."""
        # Mock response with JSON error
        response = httpx.Response(
            status_code=400,
            json={"error": "Bad request", "description": "Invalid parameter"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = ZendeskHTTPException.from_response(response)
        assert exc.status_code == 400
        assert exc.message == "Bad request"
        assert exc.response == response

    def test_from_response_with_message(self):
        """Test creating exception from response with message field."""
        response = httpx.Response(
            status_code=500,
            json={"message": "Internal server error"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = ZendeskHTTPException.from_response(response)
        assert exc.status_code == 500
        assert exc.message == "Internal server error"

    def test_from_response_without_json(self):
        """Test creating exception from response without JSON."""
        response = httpx.Response(
            status_code=404,
            text="Not Found",
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )
        response._content = b"Not Found"

        exc = ZendeskHTTPException.from_response(response)
        assert exc.status_code == 404
        assert exc.message  # Should have some error message


class TestZendeskAuthException:
    """Test cases for ZendeskAuthException."""

    def test_auth_exception_default(self):
        """Test auth exception with defaults."""
        exc = ZendeskAuthException()
        assert exc.status_code == 401
        assert exc.message == "Authentication failed"

    def test_auth_exception_custom(self):
        """Test auth exception with custom values."""
        exc = ZendeskAuthException("Invalid token", 403)
        assert exc.status_code == 403
        assert exc.message == "Invalid token"


class TestZendeskRateLimitException:
    """Test cases for ZendeskRateLimitException."""

    def test_rate_limit_exception_default(self):
        """Test rate limit exception with defaults."""
        exc = ZendeskRateLimitException()
        assert exc.status_code == 429
        assert exc.message == "Rate limit exceeded"
        assert exc.retry_after is None

    def test_rate_limit_exception_with_retry_after(self):
        """Test rate limit exception with retry after."""
        exc = ZendeskRateLimitException(retry_after=60)
        assert exc.retry_after == 60
        assert "retry after 60s" in str(exc)

    def test_from_response_with_retry_after_header(self):
        """Test creating rate limit exception with retry-after header."""
        response = httpx.Response(
            status_code=429,
            headers={"retry-after": "120"},
            json={"description": "Rate limit exceeded"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = ZendeskRateLimitException.from_response(response)
        assert exc.status_code == 429
        assert exc.retry_after == 120
        assert exc.message == "Rate limit exceeded"


class TestZendeskPaginationException:
    """Test cases for ZendeskPaginationException."""

    def test_pagination_exception(self):
        """Test pagination exception."""
        page_info = {"page": 1, "per_page": 100}
        exc = ZendeskPaginationException("Invalid page", page_info)
        assert exc.message == "Invalid page"
        assert exc.page_info == page_info

    def test_pagination_exception_no_page_info(self):
        """Test pagination exception without page info."""
        exc = ZendeskPaginationException("Invalid page")
        assert exc.page_info == {}


class TestZendeskValidationException:
    """Test cases for ZendeskValidationException."""

    def test_validation_exception_with_field(self):
        """Test validation exception with field info."""
        exc = ZendeskValidationException("Required field", "email", None)
        assert exc.field == "email"
        assert exc.value is None
        assert "field 'email'" in str(exc)

    def test_validation_exception_without_field(self):
        """Test validation exception without field info."""
        exc = ZendeskValidationException("General validation error")
        assert exc.field is None
        assert "Validation error: General validation error" == str(exc)


class TestZendeskTimeoutException:
    """Test cases for ZendeskTimeoutException."""

    def test_timeout_exception_default(self):
        """Test timeout exception with default message."""
        exc = ZendeskTimeoutException()
        assert exc.message == "Request timed out"
        assert exc.timeout is None

    def test_timeout_exception_with_timeout(self):
        """Test timeout exception with specific timeout."""
        exc = ZendeskTimeoutException(timeout=30.0)
        assert exc.timeout == 30.0
        assert "30.0s" in str(exc)


class TestCreateExceptionFromResponse:
    """Test cases for create_exception_from_response function."""

    def test_create_auth_exception_401(self):
        """Test creating auth exception for 401 response."""
        response = httpx.Response(
            status_code=401,
            json={"error": "Unauthorized"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = create_exception_from_response(response)
        assert isinstance(exc, ZendeskAuthException)
        assert exc.status_code == 401

    def test_create_auth_exception_403(self):
        """Test creating auth exception for 403 response."""
        response = httpx.Response(
            status_code=403,
            json={"error": "Forbidden"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = create_exception_from_response(response)
        assert isinstance(exc, ZendeskAuthException)
        assert exc.status_code == 403

    def test_create_rate_limit_exception(self):
        """Test creating rate limit exception for 429 response."""
        response = httpx.Response(
            status_code=429,
            json={"description": "Rate limit exceeded"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = create_exception_from_response(response)
        assert isinstance(exc, ZendeskRateLimitException)
        assert exc.status_code == 429

    def test_create_generic_http_exception(self):
        """Test creating generic HTTP exception for other status codes."""
        response = httpx.Response(
            status_code=500,
            json={"error": "Internal server error"},
            request=httpx.Request("GET", "https://test.zendesk.com/api/v2/test"),
        )

        exc = create_exception_from_response(response)
        assert isinstance(exc, ZendeskHTTPException)
        assert not isinstance(exc, (ZendeskAuthException, ZendeskRateLimitException))
        assert exc.status_code == 500

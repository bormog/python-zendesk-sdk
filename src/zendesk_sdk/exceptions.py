"""Exception classes for Zendesk SDK."""

from typing import Any, Optional

import httpx


class ZendeskBaseException(Exception):
    """Base exception for all Zendesk SDK errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ZendeskHTTPException(ZendeskBaseException):
    """Exception raised for HTTP-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[httpx.Response] = None,
        request: Optional[httpx.Request] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.request = request

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.message}"

    @classmethod
    def from_response(cls, response: httpx.Response) -> "ZendeskHTTPException":
        """Create exception from HTTP response."""
        try:
            # Try to extract error message from JSON response
            json_data = response.json()
            if isinstance(json_data, dict):
                if "error" in json_data:
                    message = json_data["error"]
                elif "description" in json_data:
                    message = json_data["description"]
                elif "message" in json_data:
                    message = json_data["message"]
                else:
                    message = f"HTTP {response.status_code} error"
            else:
                message = f"HTTP {response.status_code} error"
        except Exception:
            # If JSON parsing fails, use status text or generic message
            message = response.reason_phrase or f"HTTP {response.status_code} error"

        return cls(
            message=message,
            status_code=response.status_code,
            response=response,
            request=response.request,
        )


class ZendeskAuthException(ZendeskHTTPException):
    """Exception raised for authentication-related errors (401, 403)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        response: Optional[httpx.Response] = None,
        request: Optional[httpx.Request] = None,
    ) -> None:
        super().__init__(message, status_code, response, request)


class ZendeskRateLimitException(ZendeskHTTPException):
    """Exception raised when rate limits are exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response: Optional[httpx.Response] = None,
        request: Optional[httpx.Request] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code, response, request)
        self.retry_after = retry_after

    @classmethod
    def from_response(cls, response: httpx.Response) -> "ZendeskRateLimitException":
        """Create rate limit exception from HTTP response."""
        # Extract retry-after header if present
        retry_after = None
        retry_after_header = response.headers.get("retry-after")
        if retry_after_header:
            try:
                retry_after = int(retry_after_header)
            except ValueError:
                pass

        try:
            json_data = response.json()
            message = json_data.get("description") or json_data.get("error") or "Rate limit exceeded"
        except Exception:
            message = "Rate limit exceeded"

        return cls(
            message=message,
            status_code=response.status_code,
            response=response,
            request=response.request,
            retry_after=retry_after,
        )

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.retry_after:
            return f"{base_str} (retry after {self.retry_after}s)"
        return base_str


class ZendeskPaginationException(ZendeskBaseException):
    """Exception raised for pagination-related errors."""

    def __init__(
        self,
        message: str,
        page_info: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.page_info = page_info or {}


class ZendeskValidationException(ZendeskBaseException):
    """Exception raised for data validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class ZendeskTimeoutException(ZendeskBaseException):
    """Exception raised when requests timeout."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.timeout = timeout

    def __str__(self) -> str:
        if self.timeout:
            return f"Request timed out after {self.timeout}s"
        return self.message


def create_exception_from_response(response: httpx.Response) -> ZendeskHTTPException:
    """Create appropriate exception based on response status code."""
    if response.status_code in (401, 403):
        return ZendeskAuthException.from_response(response)
    elif response.status_code == 429:
        return ZendeskRateLimitException.from_response(response)
    else:
        return ZendeskHTTPException.from_response(response)

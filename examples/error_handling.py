"""Error handling example for Zendesk SDK.

This example demonstrates:
- Handling authentication errors
- Handling rate limiting
- Handling HTTP errors
- Handling validation errors
"""

import asyncio

from zendesk_sdk import ZendeskClient, ZendeskConfig
from zendesk_sdk.exceptions import (
    ZendeskAuthException,
    ZendeskBaseException,
    ZendeskHTTPException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
    ZendeskValidationException,
)


async def main() -> None:
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
        timeout=30.0,  # Request timeout in seconds
        max_retries=3,  # Number of retry attempts
    )

    async with ZendeskClient(config) as client:
        try:
            # Try to get a user that might not exist
            user = await client.users.get(999999999)
            print(f"User: {user.name}")

        except ZendeskAuthException as e:
            # 401 or 403 errors
            print(f"Authentication failed: {e.message}")
            print(f"Status code: {e.status_code}")

        except ZendeskRateLimitException as e:
            # 429 Too Many Requests
            print(f"Rate limit exceeded: {e.message}")
            if e.retry_after:
                print(f"Retry after: {e.retry_after} seconds")

        except ZendeskTimeoutException as e:
            # Request timeout
            print(f"Request timed out: {e.message}")
            if e.timeout:
                print(f"Timeout was set to: {e.timeout} seconds")

        except ZendeskHTTPException as e:
            # Other HTTP errors (404, 500, etc.)
            print(f"HTTP error: {e.message}")
            print(f"Status code: {e.status_code}")

        except ZendeskValidationException as e:
            # Data validation errors
            print(f"Validation error: {e.message}")
            if e.field:
                print(f"Field: {e.field}")

        except ZendeskBaseException as e:
            # Catch-all for any Zendesk SDK errors
            print(f"Zendesk error: {e.message}")

        # Example: Handling specific HTTP status codes
        try:
            _ = await client.tickets.get(123)
        except ZendeskHTTPException as e:
            if e.status_code == 404:
                print("Ticket not found")
            elif e.status_code == 403:
                print("Access denied to this ticket")
            else:
                raise  # Re-raise unexpected errors


async def retry_with_backoff() -> None:
    """Example of custom retry logic."""
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
        max_retries=0,  # Disable built-in retries
    )

    async with ZendeskClient(config) as client:
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Search returns paginator - iterate to get results
                tickets = await client.search.tickets("status:open", limit=10).collect()
                print(f"Found {len(tickets)} tickets")
                break
            except ZendeskRateLimitException as e:
                if attempt < max_attempts - 1:
                    wait_time = e.retry_after or (2**attempt)
                    print(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise


if __name__ == "__main__":
    asyncio.run(main())

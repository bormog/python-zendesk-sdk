# Python Zendesk SDK

Modern Python SDK for Zendesk API with async support, full type safety, and comprehensive error handling.

## Features

- **Async HTTP Client**: Built on httpx with retry logic, rate limiting, and exponential backoff
- **Type Safety**: Full Pydantic v2 models for Users, Organizations, Tickets, and Comments
- **Pagination**: Both offset-based and cursor-based pagination support
- **Search**: Zendesk search API support
- **Configuration**: Flexible configuration with environment variable support

## Installation

```bash
pip install python-zendesk-sdk
```

## Quick Start

```python
import asyncio
from zendesk_sdk import ZendeskClient, ZendeskConfig

async def main():
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Get users with pagination
        users_paginator = await client.get_users(per_page=10)
        users = await users_paginator.get_page()

        for user in users:
            print(f"User: {user.name} ({user.email})")

        # Get specific ticket
        ticket = await client.get_ticket(ticket_id=12345)
        print(f"Ticket: {ticket.subject}")

        # Search tickets
        results = await client.search_tickets("status:open priority:high")
        for ticket in results:
            print(f"High priority: {ticket.subject}")

asyncio.run(main())
```

## Configuration

### Direct instantiation
```python
config = ZendeskConfig(
    subdomain="mycompany",
    email="user@example.com",
    token="api_token_here"
)
```

### Environment variables
```bash
export ZENDESK_SUBDOMAIN=mycompany
export ZENDESK_EMAIL=user@example.com
export ZENDESK_TOKEN=api_token_here
```

```python
config = ZendeskConfig()  # Will load from environment
```

## API Methods

### Users
- `get_users()` - List users with pagination
- `get_user(user_id)` - Get user by ID
- `get_user_by_email(email)` - Get user by email

### Organizations
- `get_organizations()` - List organizations with pagination
- `get_organization(organization_id)` - Get organization by ID

### Tickets
- `get_tickets()` - List tickets with pagination
- `get_ticket(ticket_id)` - Get ticket by ID
- `get_user_tickets(user_id)` - Get tickets for a user
- `get_organization_tickets(organization_id)` - Get tickets for an organization

### Enriched Tickets

Load tickets with all related data (comments + users) in minimum API requests:

- `get_enriched_ticket(ticket_id)` - Get ticket with comments and all users
- `search_enriched_tickets(query)` - Search tickets with all related data
- `get_organization_enriched_tickets(org_id)` - Get organization tickets with all data
- `get_user_enriched_tickets(user_id)` - Get user tickets with all data

```python
# Get ticket with all related data
enriched = await client.get_enriched_ticket(12345)

print(f"Ticket: {enriched.ticket.subject}")
print(f"Requester: {enriched.requester.name}")
print(f"Assignee: {enriched.assignee.name if enriched.assignee else 'Unassigned'}")

for comment in enriched.comments:
    author = enriched.get_comment_author(comment)
    print(f"Comment by {author.name}: {comment.body[:50]}...")

# Search with all data loaded
results = await client.search_enriched_tickets("status:open")
for item in results:
    print(f"{item.ticket.subject} - {len(item.comments)} comments")
```

### Comments
- `get_ticket_comments(ticket_id)` - Get comments for a ticket

### Search
- `search(query)` - General search
- `search_users(query)` - Search users
- `search_tickets(query)` - Search tickets
- `search_organizations(query)` - Search organizations

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from zendesk_sdk.exceptions import (
    ZendeskAuthException,
    ZendeskHTTPException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
    ZendeskValidationException,
)

async with ZendeskClient(config) as client:
    try:
        user = await client.get_user(user_id=12345)
    except ZendeskAuthException as e:
        # 401/403 - Authentication failed
        print(f"Auth error: {e.message}")
    except ZendeskRateLimitException as e:
        # 429 - Rate limit exceeded
        print(f"Rate limited, retry after: {e.retry_after}s")
    except ZendeskHTTPException as e:
        # Other HTTP errors (404, 500, etc.)
        print(f"HTTP {e.status_code}: {e.message}")
    except ZendeskTimeoutException as e:
        # Request timeout
        print(f"Timeout: {e.message}")
```

### Automatic Retry

The SDK automatically retries on:
- Rate limiting (429) - with respect to `Retry-After` header
- Server errors (5xx) - with exponential backoff
- Network errors and timeouts

Configure retry behavior:
```python
config = ZendeskConfig(
    subdomain="mycompany",
    email="user@example.com",
    token="api_token",
    timeout=30.0,      # Request timeout in seconds
    max_retries=3,     # Number of retry attempts
)
```

## Examples

See the `examples/` directory for complete usage examples:
- `basic_usage.py` - Basic configuration and API operations
- `pagination_example.py` - Working with paginated results
- `error_handling.py` - Error handling patterns
- `enriched_tickets.py` - Loading tickets with related data

## Requirements

- Python 3.8+
- httpx
- pydantic >=2.0

## License

MIT License

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

### Comments
- `get_ticket_comments(ticket_id)` - Get comments for a ticket

### Search
- `search(query)` - General search
- `search_users(query)` - Search users
- `search_tickets(query)` - Search tickets
- `search_organizations(query)` - Search organizations

## Requirements

- Python 3.8+
- httpx
- pydantic >=2.0

## License

MIT License

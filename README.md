# Python Zendesk SDK

Modern Python SDK for Zendesk API with async support, full type safety, and comprehensive error handling.

## Features

- **Async HTTP Client**: Built on httpx with retry logic, rate limiting, and exponential backoff
- **Type Safety**: Full Pydantic v2 models for Users, Organizations, Tickets, Comments, and Help Center
- **Namespace Pattern**: Clean API organization (`client.users`, `client.tickets`, `client.help_center`)
- **Help Center**: Full CRUD for Categories, Sections, and Articles
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
        paginator = await client.users.list(per_page=10)
        users = await paginator.get_page()

        for user in users:
            print(f"User: {user['name']} ({user['email']})")

        # Get specific ticket
        ticket = await client.tickets.get(12345)
        print(f"Ticket: {ticket.subject}")

        # Search tickets
        results = await client.search.tickets("status:open priority:high")
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
```python
user = await client.users.get(user_id)           # Get user by ID
paginator = await client.users.list()            # List users with pagination
user = await client.users.by_email(email)        # Get user by email
users = await client.users.search(query)         # Search users
users = await client.users.get_many([id1, id2])  # Get multiple users
```

### Organizations
```python
org = await client.organizations.get(org_id)     # Get organization by ID
paginator = await client.organizations.list()    # List organizations
orgs = await client.organizations.search(query)  # Search organizations
```

### Tickets
```python
ticket = await client.tickets.get(ticket_id)           # Get ticket by ID
paginator = await client.tickets.list()                # List tickets
tickets = await client.tickets.for_user(user_id)       # Get user's tickets
tickets = await client.tickets.for_organization(org_id) # Get org's tickets
tickets = await client.tickets.search(query)           # Search tickets
```

### Comments (nested under tickets)
```python
comments = await client.tickets.comments.list(ticket_id)
ticket = await client.tickets.comments.add(ticket_id, body, public=False)
await client.tickets.comments.make_private(ticket_id, comment_id)
comment = await client.tickets.comments.redact(ticket_id, comment_id, text)
```

### Tags (nested under tickets)
```python
tags = await client.tickets.tags.get(ticket_id)           # Get tags
tags = await client.tickets.tags.add(ticket_id, ["vip"])  # Add tags
tags = await client.tickets.tags.set(ticket_id, ["new"])  # Replace all tags
tags = await client.tickets.tags.remove(ticket_id, ["old"]) # Remove tags
```

### Enriched Tickets

Load tickets with all related data (comments + users) in minimum API requests:

```python
# Get ticket with all related data
enriched = await client.tickets.get_enriched(12345)

print(f"Ticket: {enriched.ticket.subject}")
print(f"Requester: {enriched.requester.name}")
print(f"Assignee: {enriched.assignee.name if enriched.assignee else 'Unassigned'}")

for comment in enriched.comments:
    author = enriched.get_comment_author(comment)
    print(f"Comment by {author.name}: {comment.body[:50]}...")

# Search with all data loaded
results = await client.tickets.search_enriched("status:open")
for item in results:
    print(f"{item.ticket.subject} - {len(item.comments)} comments")
```

### Attachments
```python
content = await client.attachments.download(content_url)  # Download file
token = await client.attachments.upload(data, filename, content_type)  # Upload file

# Attach to comment
await client.tickets.comments.add(ticket_id, "See attached", uploads=[token])
```

### Search
```python
paginator = await client.search.all(query)        # General search
tickets = await client.search.tickets(query)      # Search tickets
users = await client.search.users(query)          # Search users
orgs = await client.search.organizations(query)   # Search organizations
```

### Help Center

Access Help Center (Guide) via `client.help_center` namespace:

#### Categories
```python
cat = await client.help_center.categories.get(category_id)
paginator = await client.help_center.categories.list()
cat = await client.help_center.categories.create(name, description)
cat = await client.help_center.categories.update(category_id, name=new_name)
await client.help_center.categories.delete(category_id, force=True)
```

#### Sections
```python
sec = await client.help_center.sections.get(section_id)
paginator = await client.help_center.sections.list()
paginator = await client.help_center.sections.for_category(category_id)
sec = await client.help_center.sections.create(category_id, name, description)
sec = await client.help_center.sections.update(section_id, name=new_name)
await client.help_center.sections.delete(section_id, force=True)
```

#### Articles
```python
art = await client.help_center.articles.get(article_id)
paginator = await client.help_center.articles.list()
paginator = await client.help_center.articles.for_section(section_id)
paginator = await client.help_center.articles.for_category(category_id)
results = await client.help_center.articles.search(query)
art = await client.help_center.articles.create(section_id, title, body=html)
art = await client.help_center.articles.update(article_id, title=new_title)
await client.help_center.articles.delete(article_id)
```

#### Example
```python
async with ZendeskClient(config) as client:
    hc = client.help_center

    # Get permission_group_id from existing article (required for article creation)
    existing = await (await hc.articles.list(per_page=1)).get_page()
    article_details = await hc.articles.get(existing[0]["id"])
    permission_group_id = article_details.permission_group_id

    # Create category -> section -> article hierarchy
    category = await hc.categories.create(
        name="Product Documentation",
        description="Help articles for our product"
    )

    section = await hc.sections.create(
        category.id,
        "Getting Started"
    )

    article = await hc.articles.create(
        section.id,
        title="Installation Guide",
        body="<h1>Installation</h1><p>Follow these steps...</p>",
        permission_group_id=permission_group_id,
        draft=True,
        label_names=["installation", "guide"],
    )

    # Search articles (useful for AI assistants)
    results = await hc.articles.search("password reset")
    for article in results:
        print(f"{article.title}")
        print(f"Snippet: {article.snippet}")  # Matching text with <em> tags

    # Cascade delete (removes category + all sections + all articles)
    await hc.categories.delete(category.id, force=True)
```

> **Note**: `delete()` for categories and sections requires `force=True` as a safety measure since they cascade delete all child content.

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
        user = await client.users.get(12345)
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
- `help_center.py` - Help Center categories, sections, and articles

## Requirements

- Python 3.8+
- httpx
- pydantic >=2.0

## License

MIT License

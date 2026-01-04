# Python Zendesk SDK

[![PyPI](https://img.shields.io/pypi/v/python-zendesk-sdk)](https://pypi.org/project/python-zendesk-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/python-zendesk-sdk)](https://pypi.org/project/python-zendesk-sdk/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/python-zendesk-sdk?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/python-zendesk-sdk)
[![License](https://img.shields.io/github/license/bormog/python-zendesk-sdk)](https://github.com/bormog/python-zendesk-sdk/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-blue)](https://docs.pydantic.dev/)
[![Async](https://img.shields.io/badge/async-first-blueviolet)](https://docs.python.org/3/library/asyncio.html)

Modern Python SDK for Zendesk API, designed for automation and AI agents.

## Why This SDK?

Zendesk has a powerful REST API, but using it directly is painful:
- Multiple API calls needed to get complete ticket context (ticket + comments + users)
- No type safety — just raw JSON dictionaries
- Manual pagination handling
- Boilerplate retry/rate-limit logic in every project

**This SDK solves these problems** with a clean, typed interface optimized for:

- **Support automation** — workflows, triggers, integrations
- **LLM agents** — Claude Code, Codex, custom AI assistants that need structured Zendesk access
- **Internal tools** — dashboards, reports, bulk operations

### Built for AI Agents

When an LLM agent needs to work with Zendesk, it needs:
- **Predictable structure** — typed models instead of arbitrary dicts
- **Complete context in one call** — `get_enriched()` returns ticket + all comments + all users
- **Minimal API calls** — built-in caching reduces redundant requests
- **Clear namespaces** — `client.tickets.comments.add()` is self-documenting

## Features

- **Async HTTP Client**: Built on httpx with retry logic, rate limiting, and exponential backoff
- **Type Safety**: Full Pydantic v2 models for Users, Organizations, Tickets, Comments, and Help Center
- **Namespace Pattern**: Clean API organization (`client.users`, `client.tickets`, `client.help_center`)
- **Caching**: Built-in TTL-based caching for users, organizations, and Help Center content
- **Help Center**: Full CRUD for Categories, Sections, and Articles
- **Pagination**: Both offset-based and cursor-based (export) pagination support
- **Search**: Type-safe SearchQueryConfig + raw query strings, with export methods for stable pagination
- **Human-readable output**: All models have `__str__` methods for easy printing
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

        # Search tickets (async iterator with auto-pagination)
        async for ticket in client.search.tickets("status:open priority:high", limit=10):
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
users = await client.users.get_many([id1, id2])  # Get multiple users
# For search use client.search.users() - see Search section below
```

### Organizations
```python
org = await client.organizations.get(org_id)     # Get organization by ID
paginator = await client.organizations.list()    # List organizations
# For search use client.search.organizations() - see Search section below
```

### Tickets
```python
ticket = await client.tickets.get(ticket_id)           # Get ticket by ID
paginator = await client.tickets.list()                # List tickets
tickets = await client.tickets.for_user(user_id)       # Get user's tickets
tickets = await client.tickets.for_organization(org_id) # Get org's tickets
# For search use client.search.tickets() - see Search section below
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
from zendesk_sdk import SearchQueryConfig

# Get ticket with all related data
enriched = await client.tickets.get_enriched(12345)

print(f"Ticket: {enriched.ticket.subject}")
print(f"Requester: {enriched.requester.name}")
print(f"Assignee: {enriched.assignee.name if enriched.assignee else 'Unassigned'}")

for comment in enriched.comments:
    author = enriched.get_comment_author(comment)
    print(f"Comment by {author.name}: {comment.body[:50]}...")

# Search with all data loaded (using SearchQueryConfig)
config = SearchQueryConfig.tickets(
    status=["open"],
    priority=["high", "urgent"],
    organization_id=12345,
)

# search_enriched returns async iterator
async for item in client.tickets.search_enriched(config, limit=10):
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

All search methods return **async iterators** with automatic pagination.

#### Raw Queries (Zendesk syntax)

Use the same query syntax as in Zendesk UI — it just works:

```python
# Tickets
async for ticket in client.search.tickets("status:open priority:high"):
    print(ticket.subject)

# Users
async for user in client.search.users("role:admin"):
    print(user.name)

# Organizations
async for org in client.search.organizations("tags:enterprise"):
    print(org.name)

# Collect to list
all_tickets = [t async for t in client.search.tickets("status:pending", limit=100)]

# Search with enrichment (loads comments + users)
async for item in client.tickets.search_enriched("status:open", limit=10):
    print(f"{item.ticket.subject} - {len(item.comments)} comments")
```

#### SearchQueryConfig (typed alternative)

Don't want to memorize Zendesk query syntax? Use `SearchQueryConfig` — your IDE will autocomplete available fields:

```python
from zendesk_sdk import SearchQueryConfig

config = SearchQueryConfig.tickets(
    status=["open", "pending"],
    priority=["high", "urgent"],
    organization_id=12345,
    created_after=date(2024, 1, 1),
    tags=["vip"],
    exclude_tags=["spam"],
)
async for ticket in client.search.tickets(config):
    print(ticket.subject)

config = SearchQueryConfig.users(
    role=["admin", "agent"],
    is_verified=True,
)
async for user in client.search.users(config):
    print(user.name)

config = SearchQueryConfig.organizations(tags=["enterprise"])
async for org in client.search.organizations(config):
    print(org.name)
```

<details>
<summary>Available SearchQueryConfig fields</summary>

| Field | Type | Description |
|-------|------|-------------|
| `type` | SearchType | TICKET (default), USER, ORGANIZATION |
| `status` | List[str] | new, open, pending, hold, solved, closed |
| `priority` | List[str] | low, normal, high, urgent |
| `ticket_type` | List[str] | question, incident, problem, task |
| `organization_id` | int | Filter by organization |
| `requester_id` | int\|"me"\|"none" | Filter by requester |
| `assignee_id` | int\|"me"\|"none" | Filter by assignee |
| `group_id` | int | Filter by group |
| `tags` | List[str] | Include items with tags (OR) |
| `exclude_tags` | List[str] | Exclude items with tags |
| `created_after` | date | Created after date |
| `created_before` | date | Created before date |
| `updated_after` | date | Updated after date |
| `updated_before` | date | Updated before date |
| `via` | List[str] | Channel: email, web, chat, api, phone |
| `custom_fields` | Dict[int, Any] | Custom field values |
| `order_by` | str | Sort field |
| `sort` | str | asc or desc |

</details>

#### Export Search (No Zendesk Limit)

Regular search is capped at 1000 results by Zendesk. Export endpoint has **no such limit**:

```python
# Export fetches ALL matching entities (no 1000 limit)
async for ticket in client.search.export_tickets("status:open"):
    print(ticket.subject)  # Will iterate through ALL open tickets

async for user in client.search.export_users():
    print(user.name)  # ALL users

async for org in client.search.export_organizations():
    print(org.name)  # ALL organizations

# Works with SearchQueryConfig too
config = SearchQueryConfig.tickets(status=["open"], priority=["high"])
async for ticket in client.search.export_tickets(config):
    print(ticket.subject)

# With limit if you don't need everything
async for ticket in client.search.export_tickets("priority:high", limit=500):
    print(ticket.subject)
```

| Method | Zendesk Limit | Pagination | Duplicates |
|--------|---------------|------------|------------|
| `search.tickets()` | 1000 max | Offset | Possible |
| `search.export_tickets()` | None | Cursor | None |

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

## Caching

The SDK includes built-in caching for frequently accessed resources. Caching is enabled by default and can be configured or disabled.

### Default Cache Settings

| Resource | TTL | Max Size |
|----------|-----|----------|
| Users | 5 min | 1000 |
| Organizations | 10 min | 500 |
| Articles | 15 min | 500 |
| Categories | 30 min | 200 |
| Sections | 30 min | 200 |

### Custom Cache Configuration

```python
from zendesk_sdk import CacheConfig, ZendeskClient, ZendeskConfig

config = ZendeskConfig(
    subdomain="mycompany",
    email="user@example.com",
    token="api_token",
    cache=CacheConfig(
        enabled=True,
        user_ttl=60,           # 1 minute
        user_maxsize=100,
        org_ttl=300,           # 5 minutes
        article_ttl=600,       # 10 minutes
    )
)
```

### Disable Caching

```python
config = ZendeskConfig(
    subdomain="mycompany",
    email="user@example.com",
    token="api_token",
    cache=CacheConfig(enabled=False)
)
```

### Cache Control

```python
# Check cache statistics
info = client.users.get.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}")

# Clear all cached users
client.users.get.cache_clear()

# Invalidate specific entry
client.users.get.cache_invalidate(user_id)
```

## Examples

See the `examples/` directory for complete usage examples:
- `basic_usage.py` - Basic configuration and API operations
- `search.py` - Type-safe search with SearchQueryConfig
- `pagination_example.py` - Working with paginated results
- `error_handling.py` - Error handling patterns
- `enriched_tickets.py` - Loading tickets with related data
- `help_center.py` - Help Center categories, sections, and articles
- `caching.py` - Cache configuration and usage

## Requirements

- Python 3.8+
- httpx
- pydantic >=2.0
- async-lru

## License

MIT License

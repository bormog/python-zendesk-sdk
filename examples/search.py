"""Search example for Zendesk SDK.

This example demonstrates:
- Using SearchQueryConfig for type-safe search
- Searching tickets, users, and organizations
- Combining search with enrichment
- Using date filters and tags
"""

import asyncio
from datetime import date, timedelta

from zendesk_sdk import (
    SearchQueryConfig,
    ZendeskClient,
    ZendeskConfig,
)


async def search_tickets_basic() -> None:
    """Basic ticket search with typed parameters."""
    print("=== Basic Ticket Search ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Search for open and pending tickets
        query = SearchQueryConfig.tickets(
            status=["open", "pending"],
            priority=["high", "urgent"],
        )

        # Collect first 5 tickets
        tickets = [t async for t in client.search.tickets(query, limit=5)]
        print(f"Found {len(tickets)} high-priority open/pending tickets")

        for ticket in tickets:
            print(f"  #{ticket.id}: {ticket.subject} (priority={ticket.priority})")


async def search_tickets_with_filters() -> None:
    """Search tickets with organization and date filters."""
    print("\n=== Ticket Search with Filters ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Search for tickets from specific organization in last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)

        query = SearchQueryConfig.tickets(
            status=["open", "pending", "hold"],
            organization_id=12345,
            created_after=thirty_days_ago,
            tags=["vip"],
            exclude_tags=["spam", "test"],
        )

        print(f"Query: {query.to_query()}")
        tickets = [t async for t in client.search.tickets(query, limit=10)]
        print(f"Found {len(tickets)} tickets")


async def search_enriched_tickets() -> None:
    """Search tickets and load all related data."""
    print("\n=== Enriched Ticket Search ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        query = SearchQueryConfig.tickets(
            status=["open"],
            priority=["high", "urgent"],
        )

        # search_enriched returns async iterator with tickets + comments + users pre-loaded
        count = 0
        async for item in client.tickets.search_enriched(query, limit=10):
            count += 1
            requester = item.requester.name if item.requester else "Unknown"
            assignee = item.assignee.name if item.assignee else "Unassigned"

            print(f"\n  #{item.ticket.id}: {item.ticket.subject}")
            print(f"    Requester: {requester}")
            print(f"    Assignee: {assignee}")
            print(f"    Comments: {len(item.comments)}")

            # Access comment authors without additional API calls
            for comment in item.comments[:2]:
                author = item.get_comment_author(comment)
                author_name = author.name if author else "Unknown"
                body = comment.plain_body[:50] if comment.plain_body else ""
                print(f"    - {author_name}: {body}...")

        print(f"\nTotal: {count} enriched tickets")


async def search_users() -> None:
    """Search for users with typed parameters."""
    print("\n=== User Search ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Search for verified agent users
        query = SearchQueryConfig.users(
            role=["agent", "admin"],
            is_verified=True,
        )

        users = [u async for u in client.search.users(query, limit=5)]
        print(f"Found {len(users)} verified agents/admins")

        for user in users:
            print(f"  {user.name} ({user.email}) - role: {user.role}")


async def search_organizations() -> None:
    """Search for organizations with typed parameters."""
    print("\n=== Organization Search ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Search for enterprise organizations
        query = SearchQueryConfig.organizations(
            tags=["enterprise", "premium"],
        )

        orgs = [o async for o in client.search.organizations(query, limit=5)]
        print(f"Found {len(orgs)} enterprise/premium organizations")

        for org in orgs:
            print(f"  {org.name} (id={org.id})")


async def search_with_custom_fields() -> None:
    """Search using custom ticket fields."""
    print("\n=== Search with Custom Fields ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Search using custom field IDs
        # Replace 12345678 with your actual custom field ID
        query = SearchQueryConfig.tickets(
            status=["open"],
            custom_fields={
                12345678: "premium",  # custom_field_12345678:premium
                87654321: True,  # custom_field_87654321:true
            },
        )

        print(f"Query: {query.to_query()}")
        tickets = [t async for t in client.search.tickets(query, limit=10)]
        print(f"Found {len(tickets)} tickets")


async def backward_compatible_search() -> None:
    """Search using raw query strings (backward compatible)."""
    print("\n=== Backward Compatible Search ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Raw query strings still work - returns async iterator
        tickets = [t async for t in client.search.tickets("status:open priority:high", limit=10)]
        print(f"Found {len(tickets)} tickets with raw query")

        # Enriched search also returns async iterator
        enriched = [e async for e in client.tickets.search_enriched("status:open", limit=10)]
        print(f"Found {len(enriched)} enriched tickets with raw query")


async def main() -> None:
    """Run all search examples."""
    await search_tickets_basic()
    await search_tickets_with_filters()
    await search_enriched_tickets()
    await search_users()
    await search_organizations()
    await search_with_custom_fields()
    await backward_compatible_search()


if __name__ == "__main__":
    asyncio.run(main())

"""Enriched tickets example for Zendesk SDK.

This example demonstrates:
- Loading tickets with all related data (comments + users)
- Using EnrichedTicket for efficient data access
- Minimizing API requests with batch loading
"""

import asyncio

from zendesk_sdk import ZendeskClient, ZendeskConfig


async def main() -> None:
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # ==================== Single enriched ticket ====================

        # Get a single ticket with all related data
        # This makes 2 API calls: ticket + comments (with sideloaded users)
        enriched = await client.tickets.get_enriched(12345)

        print(f"Ticket: {enriched.ticket.subject}")
        print(f"Status: {enriched.ticket.status}")

        # Access requester directly
        requester = enriched.requester
        if requester:
            print(f"Requester: {requester.name} ({requester.email})")

        # Access assignee directly
        assignee = enriched.assignee
        if assignee:
            print(f"Assignee: {assignee.name}")
        else:
            print("Ticket is unassigned")

        # Process comments with author information
        print(f"\nComments ({len(enriched.comments)}):")
        for comment in enriched.comments:
            author = enriched.get_comment_author(comment)
            body_preview = (comment.body[:50] + "...") if comment.body else "(no body)"
            if author:
                print(f"  - {author.name}: {body_preview}")
            else:
                print(f"  - Unknown: {body_preview}")

        # ==================== Search with enrichment ====================

        # Search for tickets and load all related data
        # This efficiently batch-loads users using show_many endpoint
        print("\n--- Searching tickets with enriched data ---")
        async for item in client.tickets.search_enriched("status:open priority:high", limit=10):
            print(f"\nTicket #{item.ticket.id}: {item.ticket.subject}")
            print(f"  Requester: {item.requester.name if item.requester else 'N/A'}")
            print(f"  Assignee: {item.assignee.name if item.assignee else 'Unassigned'}")
            print(f"  Comments: {len(item.comments)}")

        # ==================== Collect enriched tickets ====================

        # You can also collect enriched tickets to a list
        print("\n--- Collecting enriched tickets ---")
        enriched_tickets = [item async for item in client.tickets.search_enriched("status:pending", limit=5)]
        print(f"Collected {len(enriched_tickets)} enriched tickets")

        for item in enriched_tickets:
            print(f"  #{item.ticket.id}: {item.ticket.subject}")


if __name__ == "__main__":
    asyncio.run(main())

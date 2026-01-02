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
        # Get a single ticket with all related data
        # This makes 2 API calls: ticket + comments (with sideloaded users)
        enriched = await client.get_enriched_ticket(ticket_id=12345)

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
            if author:
                print(f"  - {author.name}: {comment.body[:50]}...")
            else:
                print(f"  - Unknown: {comment.body[:50]}...")

        # Search for tickets and load all related data
        # This efficiently batch-loads users using show_many endpoint
        print("\n--- Searching tickets with enriched data ---")
        results = await client.search_enriched_tickets(
            query="status:open priority:high",
            per_page=10,
        )

        for item in results:
            print(f"\nTicket #{item.ticket.id}: {item.ticket.subject}")
            print(f"  Requester: {item.requester.name if item.requester else 'N/A'}")
            print(f"  Assignee: {item.assignee.name if item.assignee else 'Unassigned'}")
            print(f"  Comments: {len(item.comments)}")

        # Get organization tickets with all related data
        print("\n--- Organization tickets ---")
        org_tickets = await client.get_organization_enriched_tickets(
            org_id=123,
            per_page=10,
        )

        for item in org_tickets:
            print(f"Ticket #{item.ticket.id}: {item.ticket.subject}")

        # Get user's tickets with all related data
        print("\n--- User tickets ---")
        user_tickets = await client.get_user_enriched_tickets(
            user_id=456,
            per_page=10,
        )

        for item in user_tickets:
            print(f"Ticket #{item.ticket.id}: {item.ticket.subject}")


if __name__ == "__main__":
    asyncio.run(main())

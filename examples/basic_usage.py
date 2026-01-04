"""Basic usage example for Zendesk SDK.

This example demonstrates:
- Configuration setup
- Basic API operations (get users, tickets, organizations)
- Search functionality
"""

import asyncio

from zendesk_sdk import ZendeskClient, ZendeskConfig


async def main() -> None:
    # Option 1: Direct configuration
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    # Option 2: Configuration from environment variables
    # Set these environment variables:
    #   ZENDESK_SUBDOMAIN=your-subdomain
    #   ZENDESK_EMAIL=your-email@example.com
    #   ZENDESK_TOKEN=your-api-token
    # config = ZendeskConfig()

    # Use async context manager for proper resource cleanup
    async with ZendeskClient(config) as client:
        # Get a single user
        user = await client.users.get(12345)
        print(f"User: {user.name} ({user.email})")

        # Find user by email
        user_by_email = await client.users.by_email("user@example.com")
        if user_by_email:
            print(f"Found user: {user_by_email.name}")

        # Get a single ticket
        ticket = await client.tickets.get(12345)
        print(f"Ticket: {ticket.subject} (status: {ticket.status})")

        # Get ticket comments
        comments = await client.tickets.comments.list(12345)
        print(f"Ticket has {len(comments)} comments")

        # Get organization
        org = await client.organizations.get(123)
        print(f"Organization: {org.name}")

        # Search for tickets (returns async iterator)
        count = 0
        async for ticket in client.search.tickets("status:open", limit=10):
            count += 1
            print(f"  Open ticket: {ticket.subject}")
        print(f"Found {count} open tickets (limited to 10)")

        # Search for users (returns async iterator)
        admins = [u async for u in client.search.users("role:admin", limit=5)]
        print(f"Found {len(admins)} admin users (limited to 5)")


if __name__ == "__main__":
    asyncio.run(main())

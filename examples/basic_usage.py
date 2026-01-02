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
        user = await client.get_user(user_id=12345)
        print(f"User: {user.name} ({user.email})")

        # Find user by email
        user_by_email = await client.get_user_by_email("user@example.com")
        if user_by_email:
            print(f"Found user: {user_by_email.name}")

        # Get a single ticket
        ticket = await client.get_ticket(ticket_id=12345)
        print(f"Ticket: {ticket.subject} (status: {ticket.status})")

        # Get ticket comments
        comments = await client.get_ticket_comments(ticket_id=12345)
        print(f"Ticket has {len(comments)} comments")

        # Get organization
        org = await client.get_organization(org_id=123)
        print(f"Organization: {org.name}")

        # Search for tickets
        open_tickets = await client.search_tickets("status:open")
        print(f"Found {len(open_tickets)} open tickets")

        # Search for users
        users = await client.search_users("role:admin")
        print(f"Found {len(users)} admin users")


if __name__ == "__main__":
    asyncio.run(main())

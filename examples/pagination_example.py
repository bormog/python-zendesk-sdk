"""Pagination example for Zendesk SDK.

This example demonstrates:
- Getting paginated results
- Iterating through all pages
- Working with large datasets
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
        # Get paginated list of users
        paginator = await client.get_users(per_page=50)

        # Get first page
        first_page = await paginator.get_page()
        print(f"First page: {len(first_page)} users")

        # Get specific page
        second_page = await paginator.get_page(page=2)
        print(f"Second page: {len(second_page)} users")

        # Check pagination info
        if paginator.pagination_info:
            print(f"Total count: {paginator.pagination_info.count}")
            print(f"Has more: {paginator.pagination_info.has_more}")

        # Iterate through all users (all pages)
        all_users_count = 0
        paginator = await client.get_users(per_page=100)
        async for user_data in paginator:
            all_users_count += 1
            # Process each user
            # user_data is a dictionary from API response

        print(f"Total users across all pages: {all_users_count}")

        # Similarly for tickets
        ticket_paginator = await client.get_tickets(per_page=100)
        async for ticket_data in ticket_paginator:
            # Process each ticket
            pass

        # Search with pagination
        search_paginator = await client.search(
            query="type:ticket status:open",
            per_page=100,
        )

        async for result in search_paginator:
            # Process search results
            print(f"Found: {result.get('subject', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())

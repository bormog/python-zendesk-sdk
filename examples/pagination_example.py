"""Pagination example for Zendesk SDK.

This example demonstrates four ways to work with paginators:
1. Get specific page
2. Iterate through all items
3. Collect to list
4. Ask for total count without collecting

All list() and search() methods return Paginator objects.
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
        # ==================== Method 1: Get specific page ====================

        print("=== Method 1: Get specific page ===")

        # Create paginator (no await needed)
        paginator = client.users.list(per_page=20)

        # Get first page
        first_page = await paginator.get_page()
        print(f"First page: {len(first_page)} users")

        # Get specific page by number
        second_page = await paginator.get_page(page=2)
        print(f"Second page: {len(second_page)} users")

        # Check pagination info after fetching
        if paginator.pagination_info:
            print(f"Total count: {paginator.pagination_info.count}")
            print(f"Has more: {paginator.pagination_info.has_more}")

        # ==================== Method 2: Iterate through all ====================

        print("\n=== Method 2: Iterate through all items ===")

        # Iterate through all users (handles pagination automatically)
        count = 0
        async for user in client.users.list(per_page=100):
            count += 1
            if count <= 3:
                print(f"  User: {user.name}")
            if count >= 100:
                print(f"  ... stopping at {count} users")
                break

        print(f"Iterated through {count} users")

        # ==================== Method 3: Collect to list ====================

        print("\n=== Method 3: Collect to list ===")

        # Collect with limit
        users = await client.users.list(limit=50).collect()
        print(f"Collected {len(users)} users (limit=50)")

        # Collect all (be careful with large datasets!)
        # all_users = await client.users.list().collect()

        # ==================== Method 4: Total count only ====================

        print("\n=== Method 4: Total count without collecting ===")

        # count() issues a lightweight probe (per_page=1) when no page has been
        # fetched yet; returns the cached count otherwise. Does not mutate state.
        total_open = await client.search.tickets("status:open").count()
        print(f"Open tickets in total: {total_open}")

        # After iteration / get_page(), total_count is a free sync property.
        paginator = client.users.list(per_page=100)
        await paginator.get_page()
        print(f"Users total_count (cached): {paginator.total_count}")

        # Cursor-based paginators (incremental, search export) return None:
        # the Zendesk API does not expose a total for them.

        # ==================== Pagination with search ====================

        print("\n=== Pagination with search ===")

        # Search also returns paginator
        paginator = client.search.tickets("status:open", per_page=50)

        # Get first page
        open_tickets = await paginator.get_page()
        print(f"Found {len(open_tickets)} open tickets on first page")

        # Or iterate
        async for ticket in client.search.tickets("priority:high", limit=10):
            print(f"  High priority: {ticket.subject}")

        # Or collect
        urgent = await client.search.tickets("priority:urgent", limit=20).collect()
        print(f"Collected {len(urgent)} urgent tickets")

        # ==================== Pagination info ====================

        print("\n=== Pagination info ===")

        paginator = client.tickets.list(per_page=10)
        await paginator.get_page()

        info = paginator.pagination_info
        if info:
            print(f"Page: {info.page}")
            print(f"Per page: {info.per_page}")
            print(f"Total count: {info.count}")
            print(f"Has more: {info.has_more}")


if __name__ == "__main__":
    asyncio.run(main())

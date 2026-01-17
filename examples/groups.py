"""Groups API example for Zendesk SDK.

This example demonstrates:
- Reading groups (get, list, count)
- Creating groups
- Updating groups
- Deleting groups
- Listing assignable groups
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
        # ==================== Read Operations ====================

        print("=== Read Operations ===")

        # Get group by ID (cached)
        group = await client.groups.get(12345)
        print(f"Group by ID: {group.name}")

        # Get total number of groups
        count = await client.groups.count()
        print(f"Total groups: {count}")

        # List all groups with pagination
        print("\nAll groups:")
        async for group in client.groups.list(limit=10):
            print(f"  {group.id}: {group.name}")
            if group.description:
                print(f"       Description: {group.description}")

        # Collect groups to list
        groups = await client.groups.list(limit=50).collect()
        print(f"\nCollected {len(groups)} groups")

        # List assignable groups (groups current user can assign tickets to)
        print("\nAssignable groups:")
        async for group in client.groups.list_assignable(limit=5):
            print(f"  Can assign to: {group.name}")

        # ==================== Create Operations ====================

        print("\n=== Create Operations ===")

        # Create minimal group
        new_group = await client.groups.create(name="New Support Team")
        print(f"Created group: {new_group.id} - {new_group.name}")

        # Create group with all options
        detailed_group = await client.groups.create(
            name="Engineering Support",
            description="Technical support escalation team",
            is_public=False,  # Private group
        )
        print(f"Created private group: {detailed_group.id} - {detailed_group.name}")

        # ==================== Update Operations ====================

        print("\n=== Update Operations ===")

        # Update description only
        updated = await client.groups.update(
            new_group.id,
            description="Updated team description",
        )
        print(f"Updated description: {updated.description}")

        # Update multiple fields
        updated = await client.groups.update(
            new_group.id,
            name="Renamed Support Team",
            description="Renamed and updated",
            is_public=True,  # Make public
        )
        print(f"Updated group: {updated.name} (public={updated.is_public})")

        # ==================== Delete Operations ====================

        print("\n=== Delete Operations ===")

        # Delete a group (soft delete - marks as deleted)
        await client.groups.delete(new_group.id)
        print(f"Deleted group: {new_group.id}")

        # Also delete the detailed group
        await client.groups.delete(detailed_group.id)
        print(f"Deleted group: {detailed_group.id}")

        # ==================== Caching Example ====================

        print("\n=== Caching Example ===")

        # First call - fetches from API
        group1 = await client.groups.get(12345)
        print(f"First fetch: {group1.name}")

        # Second call - returns from cache (faster, no API call)
        group2 = await client.groups.get(12345)
        print(f"Cached fetch: {group2.name}")


if __name__ == "__main__":
    asyncio.run(main())

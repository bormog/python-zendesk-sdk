"""Views API example for Zendesk SDK.

This example demonstrates read-only operations on Views:
- Listing views (all + active only)
- Getting a single view (cached)
- Iterating tickets in a view
- Counting tickets in views (single + bulk)
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
        # ==================== List views ====================

        print("=== All views ===")
        async for view in client.views.list(limit=10):
            status = "active" if view.active else "inactive"
            default = " (default)" if view.default else ""
            print(f"  {view.id}: {view.title} [{status}]{default}")

        print("\n=== Active views only ===")
        active_views = await client.views.list(active_only=True, limit=10).collect()
        for view in active_views:
            print(f"  {view.id}: {view.title}")

        if not active_views:
            print("  (no active views found)")
            return

        sample_view = active_views[0]

        # ==================== Get a single view ====================

        print(f"\n=== Get view {sample_view.id} ===")
        view = await client.views.get(sample_view.id)  # type: ignore[arg-type]
        print(f"  Title: {view.title}")
        print(f"  Description: {view.description or '(none)'}")
        print(f"  Conditions: {view.conditions}")

        # Second call hits the cache
        view_cached = await client.views.get(sample_view.id)  # type: ignore[arg-type]
        print(f"  (cached) Title: {view_cached.title}")

        # ==================== get_many ====================

        print("\n=== get_many ===")
        ids = [v.id for v in active_views[:3] if v.id is not None]
        many = await client.views.get_many(ids)
        for vid, v in many.items():
            print(f"  {vid}: {v.title}")

        # ==================== Tickets in a view ====================

        print(f"\n=== First 5 tickets in view {sample_view.id} ===")
        async for ticket in client.views.tickets(sample_view.id, limit=5):  # type: ignore[arg-type]
            print(f"  #{ticket.id}: {ticket.subject} [{ticket.status}]")

        # ==================== Count tickets in a view ====================

        print(f"\n=== Count for view {sample_view.id} ===")
        count = await client.views.count(sample_view.id)  # type: ignore[arg-type]
        staleness = "fresh" if count.fresh else "stale (cached server-side)"
        print(f"  {count.value} tickets ({staleness})")

        # ==================== count_many for a dashboard ====================

        print("\n=== count_many for several views ===")
        counts = await client.views.count_many(ids)
        for c in counts:
            print(f"  view {c.view_id}: {c.value} tickets")


if __name__ == "__main__":
    asyncio.run(main())

"""Ticket Metrics example for Zendesk SDK.

Three ways to use ticket_metrics:
1. Get metrics for a specific ticket (primary use case)
2. Iterate over all metrics
3. Find tickets that took long to resolve
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
        # ==================== Method 1: Metrics for a ticket ====================

        print("=== Method 1: Metrics for a specific ticket ===")

        ticket_id = 12345
        metrics = await client.ticket_metrics.for_ticket(ticket_id)

        # Time fields are dicts with "calendar" (wall-clock) and "business"
        # (business hours) sub-values, either of which may be None.
        reply = metrics.reply_time_in_minutes or {}
        resolution = metrics.full_resolution_time_in_minutes or {}

        print(f"Ticket #{metrics.ticket_id}")
        print(f"  Replies:                    {metrics.replies}")
        print(f"  Reply time (calendar):      {reply.get('calendar')} min")
        print(f"  Reply time (business):      {reply.get('business')} min")
        print(f"  Full resolution (calendar): {resolution.get('calendar')} min")
        print(f"  Reopens:                    {metrics.reopens}")

        # ==================== Method 2: Iterate all ====================

        print("\n=== Method 2: Iterate over all metrics ===")

        total = await client.ticket_metrics.list().count()
        print(f"Total ticket_metrics: {total}")

        count = 0
        async for m in client.ticket_metrics.list(per_page=100, limit=10):
            count += 1
            print(f"  #{m.ticket_id}: replies={m.replies}, reopens={m.reopens}")

        print(f"Looked at {count} metric records")

        # ==================== Method 3: Long-to-resolve tickets =================

        print("\n=== Method 3: Tickets that took > 1 day of business hours ===")

        threshold_minutes = 24 * 60
        slow = []
        async for m in client.ticket_metrics.list(limit=500):
            resolution = m.full_resolution_time_in_minutes or {}
            business = resolution.get("business")
            if business is not None and business > threshold_minutes:
                slow.append((m.ticket_id, business))

        slow.sort(key=lambda pair: pair[1], reverse=True)
        for ticket_id, business_minutes in slow[:10]:
            hours = business_minutes / 60
            print(f"  #{ticket_id}: {hours:.1f} business hours to resolve")


if __name__ == "__main__":
    asyncio.run(main())

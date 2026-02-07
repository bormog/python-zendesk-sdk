"""Organizations API example for Zendesk SDK.

This example demonstrates:
- Reading organizations (get, list)
- Creating organizations
- Updating organizations
- Upserting organizations (create_or_update)
- Deleting organizations
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

        # Get organization by ID (cached)
        org = await client.organizations.get(12345)
        print(f"Organization: {org.name}")
        print(f"  Domains: {org.domain_names}")
        print(f"  Tags: {org.tags}")

        # List all organizations with pagination
        print("\nAll organizations:")
        async for org in client.organizations.list(limit=10):
            print(f"  {org.id}: {org.name}")

        # Collect organizations to list
        orgs = await client.organizations.list(limit=50).collect()
        print(f"\nCollected {len(orgs)} organizations")

        # ==================== Create Operations ====================

        print("\n=== Create Operations ===")

        # Create minimal organization
        new_org = await client.organizations.create(name="Acme Corp")
        print(f"Created organization: {new_org.id} - {new_org.name}")

        # Create organization with all options
        detailed_org = await client.organizations.create(
            name="Enterprise Client",
            domain_names=["enterprise.com", "enterprise.io"],
            details="123 Business Ave, Suite 100",
            notes="VIP customer, priority support",
            tags=["enterprise", "vip"],
            group_id=12345,
            shared_tickets=True,
            shared_comments=True,
            organization_fields={"plan": "premium", "industry": "tech"},
        )
        print(f"Created detailed org: {detailed_org.id} - {detailed_org.name}")

        # ==================== Update Operations ====================

        print("\n=== Update Operations ===")

        # Update tags only
        updated = await client.organizations.update(
            new_org.id,
            tags=["enterprise", "partner"],
        )
        print(f"Updated tags: {updated.tags}")

        # Update multiple fields
        updated = await client.organizations.update(
            new_org.id,
            name="Acme Corporation",
            domain_names=["acme.com", "acme.io"],
            organization_fields={"plan": "enterprise"},
        )
        print(f"Updated org: {updated.name} (domains={updated.domain_names})")

        # ==================== Upsert Operations ====================

        print("\n=== Upsert Operations ===")

        # Create or update by external_id
        upserted = await client.organizations.create_or_update(
            name="Synced Organization",
            external_id="CRM-12345",
            tags=["synced"],
            organization_fields={"source": "crm"},
        )
        print(f"Upserted org: {upserted.id} - {upserted.name}")

        # ==================== Delete Operations ====================

        print("\n=== Delete Operations ===")

        await client.organizations.delete(new_org.id)
        print(f"Deleted organization: {new_org.id}")

        await client.organizations.delete(detailed_org.id)
        print(f"Deleted organization: {detailed_org.id}")


if __name__ == "__main__":
    asyncio.run(main())

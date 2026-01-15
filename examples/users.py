"""Users API example for Zendesk SDK.

This example demonstrates:
- Reading users (get, list, search)
- Creating users
- Updating users
- Suspending/unsuspending users
- Deleting users
- Password management
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

        # Get current authenticated user
        me = await client.users.me()
        print(f"Current user: {me.name} <{me.email}>")

        # Get user by ID (cached)
        user = await client.users.get(12345)
        print(f"User by ID: {user.name}")

        # Find user by email (cached)
        user = await client.users.by_email("user@example.com")
        if user:
            print(f"Found by email: {user.name}")

        # Get multiple users at once (batch)
        users = await client.users.get_many([123, 456, 789])
        print(f"Batch loaded {len(users)} users")

        # List all users with pagination
        async for user in client.users.list(limit=10):
            print(f"  User: {user.name}")

        # ==================== Create Operations ====================

        print("\n=== Create Operations ===")

        # Create end-user (receives verification email)
        new_user = await client.users.create(
            name="John Doe",
            email="john.doe@example.com",
        )
        print(f"Created user: {new_user.id}")

        # Create verified user (no email sent)
        verified_user = await client.users.create(
            name="Jane Doe",
            email="jane.doe@example.com",
            verified=True,
            role="end-user",
            organization_id=12345,
            tags=["vip", "enterprise"],
            user_fields={"department": "Sales"},
        )
        print(f"Created verified user: {verified_user.id}")

        # Upsert - create or update by email/external_id
        upserted = await client.users.create_or_update(
            name="John Doe Updated",
            email="john.doe@example.com",
            external_id="CRM-12345",
        )
        print(f"Upserted user: {upserted.name}")

        # ==================== Update Operations ====================

        print("\n=== Update Operations ===")

        updated = await client.users.update(
            new_user.id,
            phone="+1234567890",
            tags=["premium"],
            user_fields={"account_type": "premium"},
        )
        print(f"Updated user phone: {updated.phone}")

        # ==================== Suspension ====================

        print("\n=== Suspension ===")

        # Suspend user (blocks access)
        suspended = await client.users.suspend(new_user.id)
        print(f"User suspended: {suspended.suspended}")

        # Unsuspend user (restores access)
        unsuspended = await client.users.unsuspend(new_user.id)
        print(f"User unsuspended: {unsuspended.suspended}")

        # ==================== Password Management ====================

        print("\n=== Password Management ===")

        # Get password requirements
        reqs = await client.users.get_password_requirements(new_user.id)
        print("Password requirements:")
        for rule in reqs.rules:
            print(f"  - {rule}")

        # Set password (requires admin setting enabled in Zendesk)
        try:
            await client.users.set_password(new_user.id, "SecurePass123!")
            print("Password set successfully")
        except Exception as e:
            print(f"Set password failed (admin setting may be disabled): {e}")

        # ==================== Delete Operations ====================

        print("\n=== Delete Operations ===")

        # Soft delete (recoverable for 30 days)
        await client.users.delete(new_user.id)
        print(f"User {new_user.id} deleted (soft)")

        # Permanent delete for GDPR (irreversible!)
        # await client.users.permanently_delete(new_user.id)

        # ==================== Merge Duplicates ====================

        print("\n=== Merge Duplicates ===")

        # Merge source user into target (source is deleted)
        # merged = await client.users.merge(
        #     user_id=duplicate_id,       # Source: will be deleted
        #     target_user_id=primary_id,  # Target: receives all data
        # )
        # print(f"Merged into user: {merged.id}")


if __name__ == "__main__":
    asyncio.run(main())

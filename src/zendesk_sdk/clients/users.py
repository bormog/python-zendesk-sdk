"""Users API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..models import PasswordRequirements, User
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class UsersClient(BaseClient):
    """Client for Zendesk Users API.

    Provides full CRUD operations for users, including password management
    and suspension handling.

    Example:
        async with ZendeskClient(config) as client:
            # Get a user by ID
            user = await client.users.get(12345)

            # List all users with pagination
            async for user in client.users.list():
                print(user.name)

            # Create a new user
            user = await client.users.create(
                name="John Doe",
                email="john@example.com"
            )

            # Update a user
            user = await client.users.update(12345, phone="+1234567890")

            # Delete a user
            await client.users.delete(12345)

            # Set password (requires admin setting enabled)
            await client.users.set_password(12345, "NewSecurePass123!")

            # Suspend/unsuspend
            await client.users.suspend(12345)
            await client.users.unsuspend(12345)
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize UsersClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], User] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.user_maxsize if cache_config else 1000,
            ttl=cache_config.user_ttl if cache_config else 300,
        )
        self.by_email: Callable[[str], Optional[User]] = self._create_cached_method(
            self._by_email_impl,
            maxsize=cache_config.user_maxsize if cache_config else 1000,
            ttl=cache_config.user_ttl if cache_config else 300,
        )

    # ==================== Read Operations ====================

    async def _get_impl(self, user_id: int) -> User:
        """Get a specific user by ID.

        Results are cached based on cache configuration.

        Args:
            user_id: The user's ID

        Returns:
            User object
        """
        response = await self._get(f"users/{user_id}.json")
        return User(**response["user"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[User]":
        """Get paginated list of users.

        Args:
            per_page: Number of users per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all users
        """
        return ZendeskPaginator.create_users_paginator(self._http, per_page=per_page, limit=limit)

    async def _by_email_impl(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Results are cached based on cache configuration.

        Args:
            email: The user's email address

        Returns:
            User object if found, None otherwise
        """
        response = await self._get("users/search.json", params={"query": email})
        users = response.get("users", [])
        if users:
            return User(**users[0])
        return None

    async def get_many(self, user_ids: List[int]) -> Dict[int, User]:
        """Fetch multiple users by IDs.

        Uses show_many endpoint for efficiency (max 100 IDs per request).

        Args:
            user_ids: List of user IDs to fetch

        Returns:
            Dictionary mapping user_id to User object
        """
        if not user_ids:
            return {}

        unique_ids = list(set(user_ids))[:100]
        ids_param = ",".join(str(uid) for uid in unique_ids)

        response = await self._get(f"users/show_many.json?ids={ids_param}")

        users: Dict[int, User] = {}
        for user_data in response.get("users", []):
            user = User(**user_data)
            if user.id is not None:
                users[user.id] = user
        return users

    async def me(self) -> User:
        """Get the currently authenticated user.

        Returns:
            User object for the authenticated user
        """
        response = await self._get("users/me.json")
        return User(**response["user"])

    # ==================== Create Operations ====================

    async def create(
        self,
        name: str,
        *,
        email: Optional[str] = None,
        role: Optional[str] = None,
        verified: bool = False,
        external_id: Optional[str] = None,
        organization_id: Optional[int] = None,
        phone: Optional[str] = None,
        time_zone: Optional[str] = None,
        locale: Optional[str] = None,
        locale_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        alias: Optional[str] = None,
        signature: Optional[str] = None,
        custom_role_id: Optional[int] = None,
        default_group_id: Optional[int] = None,
        ticket_restriction: Optional[str] = None,
        only_private_comments: Optional[bool] = None,
        restricted_agent: Optional[bool] = None,
        user_fields: Optional[Dict[str, Any]] = None,
        identities: Optional[List[Dict[str, Any]]] = None,
    ) -> User:
        """Create a new user.

        If email is provided and verified=False (default), Zendesk sends
        a verification email where the user can set their password.

        If verified=True, the user's email is marked as verified and you
        should set a password using set_password().

        Args:
            name: The user's name (required)
            email: The user's primary email address
            role: User role - one of: "end-user", "agent", "admin"
            verified: If True, email is marked as verified (default: False).
                     If False, user receives verification email to set password.
            external_id: External ID for linking to your system
            organization_id: Organization to assign the user to
            phone: User's phone number
            time_zone: User's time zone (e.g., "Pacific Time (US & Canada)")
            locale: User's locale (BCP-47 format, e.g., "en-US")
            locale_id: Zendesk locale ID
            tags: List of tags to apply to user
            details: Additional details about the user
            notes: Internal notes about the user
            alias: Display name for agents shown to end users
            signature: Agent's signature for email responses
            custom_role_id: Custom role ID for Enterprise accounts
            default_group_id: Default group for agent users
            ticket_restriction: Ticket access restriction
            only_private_comments: If True, user can only create private comments
            restricted_agent: If True, agent has access restrictions
            user_fields: Custom user field values as {field_key: value}
            identities: Additional user identities (emails, X handles, etc.)

        Returns:
            Created User object

        Example:
            # Create end-user (receives verification email)
            user = await client.users.create(
                name="John Doe",
                email="john@example.com"
            )

            # Create verified user (admin sets password)
            user = await client.users.create(
                name="Jane Doe",
                email="jane@example.com",
                verified=True
            )
            await client.users.set_password(user.id, "SecurePass123!")

            # Create agent
            user = await client.users.create(
                name="Support Agent",
                email="agent@company.com",
                role="agent",
                verified=True
            )
        """
        user_data: Dict[str, Any] = {"name": name}

        if email is not None:
            user_data["email"] = email
        if role is not None:
            user_data["role"] = role
        if verified:
            user_data["verified"] = verified
        if external_id is not None:
            user_data["external_id"] = external_id
        if organization_id is not None:
            user_data["organization_id"] = organization_id
        if phone is not None:
            user_data["phone"] = phone
        if time_zone is not None:
            user_data["time_zone"] = time_zone
        if locale is not None:
            user_data["locale"] = locale
        if locale_id is not None:
            user_data["locale_id"] = locale_id
        if tags is not None:
            user_data["tags"] = tags
        if details is not None:
            user_data["details"] = details
        if notes is not None:
            user_data["notes"] = notes
        if alias is not None:
            user_data["alias"] = alias
        if signature is not None:
            user_data["signature"] = signature
        if custom_role_id is not None:
            user_data["custom_role_id"] = custom_role_id
        if default_group_id is not None:
            user_data["default_group_id"] = default_group_id
        if ticket_restriction is not None:
            user_data["ticket_restriction"] = ticket_restriction
        if only_private_comments is not None:
            user_data["only_private_comments"] = only_private_comments
        if restricted_agent is not None:
            user_data["restricted_agent"] = restricted_agent
        if user_fields is not None:
            user_data["user_fields"] = user_fields
        if identities is not None:
            user_data["identities"] = identities

        response = await self._post("users.json", json={"user": user_data})
        return User(**response["user"])

    async def create_or_update(
        self,
        name: str,
        *,
        email: Optional[str] = None,
        external_id: Optional[str] = None,
        role: Optional[str] = None,
        verified: bool = False,
        organization_id: Optional[int] = None,
        phone: Optional[str] = None,
        time_zone: Optional[str] = None,
        tags: Optional[List[str]] = None,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        user_fields: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Create a user or update if matching email/external_id exists.

        Uses Zendesk's create_or_update endpoint which matches users by
        email or external_id. If a match is found, the user is updated.
        If not, a new user is created.

        Args:
            name: The user's name (required)
            email: Email address (used for matching existing user)
            external_id: External ID (used for matching if no email match)
            role: User role
            verified: Mark email as verified
            organization_id: Organization ID
            phone: Phone number
            time_zone: Time zone
            tags: User tags
            details: User details
            notes: Internal notes
            user_fields: Custom field values

        Returns:
            Created or updated User object

        Example:
            # Upsert user from external system
            user = await client.users.create_or_update(
                name="John Doe",
                email="john@example.com",
                external_id="CRM-12345",
                user_fields={"department": "Sales"}
            )
        """
        user_data: Dict[str, Any] = {"name": name}

        if email is not None:
            user_data["email"] = email
        if external_id is not None:
            user_data["external_id"] = external_id
        if role is not None:
            user_data["role"] = role
        if verified:
            user_data["verified"] = verified
        if organization_id is not None:
            user_data["organization_id"] = organization_id
        if phone is not None:
            user_data["phone"] = phone
        if time_zone is not None:
            user_data["time_zone"] = time_zone
        if tags is not None:
            user_data["tags"] = tags
        if details is not None:
            user_data["details"] = details
        if notes is not None:
            user_data["notes"] = notes
        if user_fields is not None:
            user_data["user_fields"] = user_fields

        response = await self._post("users/create_or_update.json", json={"user": user_data})
        return User(**response["user"])

    async def create_many(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple users in a single request.

        This is a batch operation that creates a job. For small numbers
        of users, consider using create() in a loop instead.

        Args:
            users: List of user data dictionaries, each containing at least "name"

        Returns:
            Job status response with job_status containing id, url, status

        Example:
            result = await client.users.create_many([
                {"name": "User 1", "email": "user1@example.com"},
                {"name": "User 2", "email": "user2@example.com"},
            ])
            job_id = result["job_status"]["id"]
        """
        response = await self._post("users/create_many.json", json={"users": users})
        return response

    # ==================== Update Operations ====================

    async def update(
        self,
        user_id: int,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        verified: Optional[bool] = None,
        external_id: Optional[str] = None,
        organization_id: Optional[int] = None,
        phone: Optional[str] = None,
        time_zone: Optional[str] = None,
        locale: Optional[str] = None,
        locale_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        alias: Optional[str] = None,
        signature: Optional[str] = None,
        custom_role_id: Optional[int] = None,
        default_group_id: Optional[int] = None,
        ticket_restriction: Optional[str] = None,
        only_private_comments: Optional[bool] = None,
        restricted_agent: Optional[bool] = None,
        user_fields: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Update an existing user.

        All fields are optional - only provided fields will be updated.

        Args:
            user_id: The user's ID
            name: New name
            email: New primary email
            role: New role - one of: "end-user", "agent", "admin"
            verified: Mark primary identity as verified
            external_id: New external ID
            organization_id: New organization ID
            phone: New phone number
            time_zone: New time zone
            locale: New locale (BCP-47 format)
            locale_id: New Zendesk locale ID
            tags: Replace all user tags
            details: New details
            notes: New internal notes
            alias: New agent alias
            signature: New agent signature
            custom_role_id: New custom role ID
            default_group_id: New default group ID
            ticket_restriction: New ticket restriction
            only_private_comments: Update private comments setting
            restricted_agent: Update restricted agent setting
            user_fields: Custom field values to update

        Returns:
            Updated User object

        Example:
            # Update phone number
            user = await client.users.update(12345, phone="+1234567890")

            # Update multiple fields
            user = await client.users.update(
                12345,
                organization_id=999,
                tags=["vip", "premium"],
                user_fields={"account_type": "enterprise"}
            )
        """
        user_data: Dict[str, Any] = {}

        if name is not None:
            user_data["name"] = name
        if email is not None:
            user_data["email"] = email
        if role is not None:
            user_data["role"] = role
        if verified is not None:
            user_data["verified"] = verified
        if external_id is not None:
            user_data["external_id"] = external_id
        if organization_id is not None:
            user_data["organization_id"] = organization_id
        if phone is not None:
            user_data["phone"] = phone
        if time_zone is not None:
            user_data["time_zone"] = time_zone
        if locale is not None:
            user_data["locale"] = locale
        if locale_id is not None:
            user_data["locale_id"] = locale_id
        if tags is not None:
            user_data["tags"] = tags
        if details is not None:
            user_data["details"] = details
        if notes is not None:
            user_data["notes"] = notes
        if alias is not None:
            user_data["alias"] = alias
        if signature is not None:
            user_data["signature"] = signature
        if custom_role_id is not None:
            user_data["custom_role_id"] = custom_role_id
        if default_group_id is not None:
            user_data["default_group_id"] = default_group_id
        if ticket_restriction is not None:
            user_data["ticket_restriction"] = ticket_restriction
        if only_private_comments is not None:
            user_data["only_private_comments"] = only_private_comments
        if restricted_agent is not None:
            user_data["restricted_agent"] = restricted_agent
        if user_fields is not None:
            user_data["user_fields"] = user_fields

        response = await self._put(f"users/{user_id}.json", json={"user": user_data})
        return User(**response["user"])

    async def update_many(
        self,
        user_ids: List[int],
        *,
        organization_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        user_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update multiple users with the same values.

        This is a batch operation that creates a job. Only fields that
        can be set to the same value for multiple users are supported.

        Args:
            user_ids: List of user IDs to update (max 100)
            organization_id: Set organization for all users
            tags: Set tags for all users
            user_fields: Set custom fields for all users

        Returns:
            Job status response

        Example:
            result = await client.users.update_many(
                [123, 456, 789],
                organization_id=999,
                tags=["bulk-updated"]
            )
        """
        user_data: Dict[str, Any] = {}

        if organization_id is not None:
            user_data["organization_id"] = organization_id
        if tags is not None:
            user_data["tags"] = tags
        if user_fields is not None:
            user_data["user_fields"] = user_fields

        ids_param = ",".join(str(uid) for uid in user_ids[:100])
        response = await self._put(f"users/update_many.json?ids={ids_param}", json={"user": user_data})
        return response

    # ==================== Delete Operations ====================

    async def delete(self, user_id: int) -> bool:
        """Delete a user.

        The user is soft-deleted and can be recovered within 30 days.
        Deleted users cannot authenticate and their tickets are unassigned.

        Args:
            user_id: The user's ID

        Returns:
            True if successful

        Example:
            await client.users.delete(12345)
        """
        await self._delete(f"users/{user_id}.json")
        return True

    async def delete_many(self, user_ids: List[int]) -> Dict[str, Any]:
        """Delete multiple users.

        This is a batch operation that creates a job.

        Args:
            user_ids: List of user IDs to delete (max 100)

        Returns:
            Job status response

        Example:
            result = await client.users.delete_many([123, 456, 789])
        """
        ids_param = ",".join(str(uid) for uid in user_ids[:100])
        response = await self._delete(f"users/destroy_many.json?ids={ids_param}")
        return response or {}

    async def permanently_delete(self, user_id: int) -> Dict[str, Any]:
        """Permanently delete a user (GDPR compliance).

        WARNING: This action is irreversible. The user and all their
        data will be permanently removed.

        Args:
            user_id: The user's ID

        Returns:
            Deletion response with user data

        Example:
            # Permanent deletion for GDPR request
            result = await client.users.permanently_delete(12345)
        """
        response = await self._delete(f"deleted_users/{user_id}.json")
        return response or {}

    # ==================== Password Management ====================

    async def set_password(self, user_id: int, password: str) -> bool:
        """Set a user's password.

        This method requires the "Allow admins to set passwords" setting
        to be enabled in Zendesk (Settings > Security > Global).
        Only account owners can enable this setting.

        Args:
            user_id: The user's ID
            password: The new password

        Returns:
            True if successful

        Example:
            # Set password for newly created verified user
            user = await client.users.create(
                name="John Doe",
                email="john@example.com",
                verified=True
            )
            await client.users.set_password(user.id, "SecurePass123!")
        """
        await self._post(f"users/{user_id}/password.json", json={"password": password})
        return True

    async def get_password_requirements(self, user_id: int) -> PasswordRequirements:
        """Get password requirements for a user.

        Returns the password policy that applies to the user based on
        their role and the account's security settings.

        Args:
            user_id: The user's ID

        Returns:
            PasswordRequirements object with list of requirement rules

        Example:
            reqs = await client.users.get_password_requirements(12345)
            for rule in reqs.rules:
                print(f"- {rule}")
        """
        response = await self._get(f"users/{user_id}/password/requirements.json")
        return PasswordRequirements(requirements=response["requirements"])

    # ==================== Suspension Management ====================

    async def suspend(self, user_id: int) -> User:
        """Suspend a user.

        Suspended users cannot sign in and their tickets are removed
        from views. The user can be unsuspended later.

        Args:
            user_id: The user's ID

        Returns:
            Updated User object with suspended=True

        Example:
            user = await client.users.suspend(12345)
            assert user.suspended is True
        """
        response = await self._put(f"users/{user_id}.json", json={"user": {"suspended": True}})
        return User(**response["user"])

    async def unsuspend(self, user_id: int) -> User:
        """Unsuspend a previously suspended user.

        Restores the user's ability to sign in and access their tickets.

        Args:
            user_id: The user's ID

        Returns:
            Updated User object with suspended=False

        Example:
            user = await client.users.unsuspend(12345)
            assert user.suspended is False
        """
        response = await self._put(f"users/{user_id}.json", json={"user": {"suspended": False}})
        return User(**response["user"])

    # ==================== Merge Operations ====================

    async def merge(self, user_id: int, target_user_id: int) -> User:
        """Merge one user into another.

        The source user (user_id) is merged into the target user.
        The source user's tickets, identities, and other data are
        transferred to the target user. The source user is then deleted.

        Args:
            user_id: The source user's ID (will be deleted)
            target_user_id: The target user's ID (will receive data)

        Returns:
            The target User object after merge

        Example:
            # Merge duplicate user into primary
            merged = await client.users.merge(
                user_id=duplicate_id,
                target_user_id=primary_id
            )
        """
        response = await self._put(f"users/{user_id}/merge.json", json={"user": {"id": target_user_id}})
        return User(**response["user"])

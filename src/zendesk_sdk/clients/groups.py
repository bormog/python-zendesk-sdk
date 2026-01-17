"""Groups API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from ..models import Group
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class GroupsClient(BaseClient):
    """Client for Zendesk Groups API.

    Provides full CRUD operations for groups, which organize agents
    into teams for ticket assignment and routing.

    Example:
        async with ZendeskClient(config) as client:
            # Get a group by ID
            group = await client.groups.get(12345)

            # List all groups with pagination
            async for group in client.groups.list():
                print(group.name)

            # Create a new group
            group = await client.groups.create(
                name="Support Team",
                description="First-line support agents",
                is_public=True
            )

            # Update a group
            group = await client.groups.update(
                12345,
                description="Updated description"
            )

            # Delete a group
            await client.groups.delete(12345)

            # Count groups
            count = await client.groups.count()

            # List assignable groups
            async for group in client.groups.list_assignable():
                print(group.name)
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize GroupsClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], Group] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.group_maxsize if cache_config else 500,
            ttl=cache_config.group_ttl if cache_config else 600,
        )

    # ==================== Read Operations ====================

    async def _get_impl(self, group_id: int) -> Group:
        """Get a specific group by ID.

        Retrieves detailed information about a single group.
        Results are cached based on cache configuration to reduce API calls.

        Args:
            group_id: The unique identifier of the group to retrieve

        Returns:
            Group object containing all group details including
            name, description, and settings

        Example:
            group = await client.groups.get(12345)
            print(f"Group: {group.name}")
            print(f"Description: {group.description}")
        """
        response = await self._get(f"groups/{group_id}.json")
        return Group(**response["group"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Group]":
        """Get paginated list of all groups.

        Returns a paginator that can be used to iterate through all groups
        in the Zendesk account. The paginator handles offset-based pagination
        automatically and supports various iteration patterns.

        Args:
            per_page: Number of groups to fetch per API request (max 100).
                Higher values reduce API calls but increase response size.
            limit: Maximum total number of groups to return when iterating.
                Use None (default) for no limit. Useful for testing or when you
                only need a subset of groups.

        Returns:
            Paginator[Group] that supports:
            - Async iteration: `async for group in client.groups.list()`
            - Page access: `await client.groups.list().get_page(2)`
            - Collection: `await client.groups.list().collect()`

        Example:
            # Iterate through all groups
            async for group in client.groups.list():
                print(f"{group.id}: {group.name}")

            # Get first 50 groups as a list
            groups = await client.groups.list(limit=50).collect()

            # Get a specific page
            page_groups = await client.groups.list().get_page(1)

            # Process with custom page size
            async for group in client.groups.list(per_page=25):
                process_group(group)
        """
        return ZendeskPaginator.create_groups_paginator(self._http, per_page=per_page, limit=limit)

    async def count(self) -> int:
        """Get count of all groups.

        Returns:
            Total number of groups in the account

        Example:
            count = await client.groups.count()
            print(f"Total groups: {count}")
        """
        response = await self._get("groups/count.json")
        return int(response["count"]["value"])

    def list_assignable(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Group]":
        """Get paginated list of assignable groups.

        Returns only groups that the current user can assign tickets to.
        Useful for agent interfaces where ticket assignment is limited.

        Args:
            per_page: Number of groups to fetch per API request (max 100).
            limit: Maximum total number of groups to return when iterating.
                Use None (default) for no limit.

        Returns:
            Paginator[Group] for iterating through assignable groups

        Example:
            async for group in client.groups.list_assignable():
                print(f"Can assign to: {group.name}")

            # Collect assignable groups to list
            assignable = await client.groups.list_assignable().collect()
        """
        return ZendeskPaginator.create_assignable_groups_paginator(self._http, per_page=per_page, limit=limit)

    # ==================== Create Operations ====================

    async def create(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Group:
        """Create a new group.

        Requires admin permissions or custom role with group creation rights.

        Args:
            name: The group's name (required)
            description: Description of the group's purpose
            is_public: If True, group is public. If False, group is private.
                Public groups are visible to all agents.
                Private groups are only visible to members.

        Returns:
            Created Group object with assigned ID and timestamps

        Example:
            # Create a public support group
            group = await client.groups.create(
                name="Level 1 Support",
                description="First-line customer support team",
                is_public=True
            )

            # Create a private escalation group
            group = await client.groups.create(
                name="Escalations",
                description="Senior engineers for escalated issues",
                is_public=False
            )

            # Create minimal group
            group = await client.groups.create("New Team")
        """
        group_data: Dict[str, Any] = {"name": name}

        if description is not None:
            group_data["description"] = description
        if is_public is not None:
            group_data["is_public"] = is_public

        response = await self._post("groups.json", json={"group": group_data})
        return Group(**response["group"])

    # ==================== Update Operations ====================

    async def update(
        self,
        group_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Group:
        """Update an existing group.

        Requires admin permissions. All fields are optional - only
        provided fields will be updated.

        Args:
            group_id: The group's ID
            name: New name for the group
            description: New description
            is_public: Change group visibility (True=public, False=private)

        Returns:
            Updated Group object

        Example:
            # Update description only
            group = await client.groups.update(
                12345,
                description="Updated team description"
            )

            # Make group private
            group = await client.groups.update(
                12345,
                is_public=False
            )

            # Update multiple fields
            group = await client.groups.update(
                12345,
                name="Support Team (EMEA)",
                description="European support team",
                is_public=True
            )
        """
        group_data: Dict[str, Any] = {}

        if name is not None:
            group_data["name"] = name
        if description is not None:
            group_data["description"] = description
        if is_public is not None:
            group_data["is_public"] = is_public

        response = await self._put(f"groups/{group_id}.json", json={"group": group_data})
        return Group(**response["group"])

    # ==================== Delete Operations ====================

    async def delete(self, group_id: int) -> bool:
        """Delete a group.

        The group is soft-deleted and marked with deleted=True.
        Agents in the group are unassigned from it.
        Cannot delete the default group.

        Requires admin permissions or custom role with group deletion rights.

        Args:
            group_id: The group's ID

        Returns:
            True if successful

        Raises:
            ZendeskHTTPException: If group is default group or doesn't exist

        Example:
            # Delete a group
            await client.groups.delete(12345)

            # Check if successful
            success = await client.groups.delete(12345)
            if success:
                print("Group deleted successfully")
        """
        await self._delete(f"groups/{group_id}.json")
        return True

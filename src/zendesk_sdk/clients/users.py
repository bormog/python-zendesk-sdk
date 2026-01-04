"""Users API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..models import User
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class UsersClient(BaseClient):
    """Client for Zendesk Users API.

    Example:
        async with ZendeskClient(config) as client:
            # Get a user by ID
            user = await client.users.get(12345)

            # List all users with pagination
            paginator = await client.users.list()
            async for user_data in paginator:
                print(user_data["name"])

            # Find user by email
            user = await client.users.by_email("user@example.com")

            # For search use client.search.users()
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

    async def list(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of users.

        Args:
            per_page: Number of users per page (max 100)

        Returns:
            Paginator for iterating through all users
        """
        return ZendeskPaginator.create_users_paginator(self._http, per_page=per_page)

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

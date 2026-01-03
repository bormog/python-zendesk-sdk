"""Users API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models import User
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
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

            # Search users
            users = await client.users.search("role:admin")
    """

    async def get(self, user_id: int) -> User:
        """Get a specific user by ID.

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

    async def by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

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

    async def search(self, query: str, per_page: int = 100) -> List[User]:
        """Search for users.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of User objects
        """
        full_query = f"type:user {query}"
        response = await self._get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [User(**result) for result in results if result.get("result_type") == "user"]

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

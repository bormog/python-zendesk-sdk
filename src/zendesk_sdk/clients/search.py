"""Search API client."""

from typing import TYPE_CHECKING, Any, Dict, List

from ..models import Organization, Ticket, User
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..pagination import Paginator


class SearchClient(BaseClient):
    """Client for Zendesk Search API.

    Example:
        async with ZendeskClient(config) as client:
            # General search
            paginator = await client.search.all("status:open")

            # Search specific resources
            tickets = await client.search.tickets("priority:high")
            users = await client.search.users("role:admin")
            orgs = await client.search.organizations("acme")
    """

    async def all(self, query: str, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Search across all Zendesk resources.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            Paginator for iterating through search results
        """
        return ZendeskPaginator.create_search_paginator(self._http, query=query, per_page=per_page)

    async def tickets(self, query: str, per_page: int = 100) -> List[Ticket]:
        """Search for tickets.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Ticket objects
        """
        full_query = f"type:ticket {query}"
        response = await self._get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [Ticket(**result) for result in results if result.get("result_type") == "ticket"]

    async def users(self, query: str, per_page: int = 100) -> List[User]:
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

    async def organizations(self, query: str, per_page: int = 100) -> List[Organization]:
        """Search for organizations.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Organization objects
        """
        full_query = f"type:organization {query}"
        response = await self._get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [Organization(**result) for result in results if result.get("result_type") == "organization"]

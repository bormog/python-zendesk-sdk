"""Search API client."""

from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Union

from ..models import Organization, Ticket, User
from ..models.search import SearchQueryConfig, SearchType
from ..pagination import SearchExportPaginator, ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..pagination import Paginator


class SearchClient(BaseClient):
    """Client for Zendesk Search API.

    Supports both raw query strings and typed SearchQueryConfig.

    Example:
        async with ZendeskClient(config) as client:
            # Using SearchQueryConfig (recommended)
            from zendesk_sdk import SearchQueryConfig

            config = SearchQueryConfig(
                status=["open", "pending"],
                priority=["high"],
                organization_id=12345,
            )
            tickets = await client.search.tickets(config)

            # Raw query string (backward compatible)
            tickets = await client.search.tickets("status:open priority:high")

            # Unified search method
            results = await client.search(config)
    """

    def _resolve_query(
        self,
        query: Union[str, SearchQueryConfig],
        force_type: Optional[SearchType] = None,
    ) -> str:
        """Convert query input to Zendesk query string.

        Args:
            query: Raw query string or SearchQueryConfig
            force_type: Override the type in SearchQueryConfig

        Returns:
            Zendesk query string
        """
        if isinstance(query, SearchQueryConfig):
            if force_type and query.type != force_type:
                # Create a copy with the correct type
                query = query.model_copy(update={"type": force_type})
            return query.to_query()
        else:
            # Raw query string - prepend type if needed
            if force_type:
                return f"type:{force_type.value} {query}"
            return query

    async def __call__(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
    ) -> Union[List[Ticket], List[User], List[Organization]]:
        """Unified search method that returns typed results based on query type.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Ticket, User, or Organization objects based on query type
        """
        if isinstance(query, SearchQueryConfig):
            search_type = query.type
            query_str = query.to_query()
        else:
            # Try to detect type from raw query
            query_str = query
            if "type:user" in query.lower():
                search_type = SearchType.USER
            elif "type:organization" in query.lower():
                search_type = SearchType.ORGANIZATION
            else:
                search_type = SearchType.TICKET
                if "type:ticket" not in query.lower():
                    query_str = f"type:ticket {query}"

        response = await self._get("search.json", params={"query": query_str, "per_page": per_page})
        results = response.get("results", [])

        if search_type == SearchType.USER:
            return [User(**r) for r in results if r.get("result_type") == "user"]
        elif search_type == SearchType.ORGANIZATION:
            return [Organization(**r) for r in results if r.get("result_type") == "organization"]
        else:
            return [Ticket(**r) for r in results if r.get("result_type") == "ticket"]

    async def all(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
    ) -> "Paginator[Dict[str, Any]]":
        """Search across all Zendesk resources with pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)

        Returns:
            Paginator for iterating through search results
        """
        query_str = self._resolve_query(query)
        return ZendeskPaginator.create_search_paginator(self._http, query=query_str, per_page=per_page)

    async def tickets(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Ticket]:
        """Search for tickets with automatic pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            Ticket objects

        Example:
            # Get first 10 tickets
            async for ticket in client.search.tickets(config, limit=10):
                print(ticket.subject)

            # Get all tickets (up to Zendesk's 1000 limit)
            async for ticket in client.search.tickets(config):
                print(ticket.subject)
        """
        query_str = self._resolve_query(query, force_type=SearchType.TICKET)
        paginator = await self.all(query_str, per_page=per_page)
        count = 0
        async for item in paginator:
            if item.get("result_type") == "ticket":
                yield Ticket(**item)
                count += 1
                if limit and count >= limit:
                    return

    async def users(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[User]:
        """Search for users with automatic pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            User objects

        Example:
            # Get first 10 users
            async for user in client.search.users(config, limit=10):
                print(user.name)
        """
        query_str = self._resolve_query(query, force_type=SearchType.USER)
        paginator = await self.all(query_str, per_page=per_page)
        count = 0
        async for item in paginator:
            if item.get("result_type") == "user":
                yield User(**item)
                count += 1
                if limit and count >= limit:
                    return

    async def organizations(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Organization]:
        """Search for organizations with automatic pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            Organization objects

        Example:
            # Get first 10 organizations
            async for org in client.search.organizations(config, limit=10):
                print(org.name)
        """
        query_str = self._resolve_query(query, force_type=SearchType.ORGANIZATION)
        paginator = await self.all(query_str, per_page=per_page)
        count = 0
        async for item in paginator:
            if item.get("result_type") == "organization":
                yield Organization(**item)
                count += 1
                if limit and count >= limit:
                    return

    # Export methods (cursor-based pagination, no duplicates)

    async def export_tickets(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Ticket]:
        """Export tickets using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string (empty = all tickets)
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            Ticket objects

        Example:
            async for ticket in client.search.export_tickets("status:open"):
                print(ticket)
        """
        query_str = self._resolve_query(query) or "*"
        paginator = SearchExportPaginator(self._http, query_str, "ticket", page_size)
        count = 0
        async for item in paginator:
            yield Ticket(**item)
            count += 1
            if limit and count >= limit:
                return

    async def export_users(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[User]:
        """Export users using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            User objects
        """
        query_str = self._resolve_query(query) or "*"
        paginator = SearchExportPaginator(self._http, query_str, "user", page_size)
        count = 0
        async for item in paginator:
            yield User(**item)
            count += 1
            if limit and count >= limit:
                return

    async def export_organizations(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Organization]:
        """Export organizations using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            Organization objects
        """
        query_str = self._resolve_query(query) or "*"
        paginator = SearchExportPaginator(self._http, query_str, "organization", page_size)
        count = 0
        async for item in paginator:
            yield Organization(**item)
            count += 1
            if limit and count >= limit:
                return

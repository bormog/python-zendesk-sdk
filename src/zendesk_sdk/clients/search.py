"""Search API client."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..models import Organization, Ticket, User
from ..models.search import SearchQueryConfig, SearchType
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..pagination import CursorPaginator, OffsetPaginator, Paginator


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

    def all(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> "Paginator[Dict[str, Any]]":
        """Search across all Zendesk resources with pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through search results
        """
        query_str = self._resolve_query(query)
        return ZendeskPaginator.create_search_paginator(self._http, query=query_str, per_page=per_page, limit=limit)

    def tickets(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> "OffsetPaginator[Ticket]":
        """Search for tickets with pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through ticket results

        Example:
            # Iterate through tickets
            async for ticket in client.search.tickets(config, limit=10):
                print(ticket.subject)

            # Get specific page
            paginator = client.search.tickets(config)
            page = await paginator.get_page(2)
        """
        query_str = self._resolve_query(query, force_type=SearchType.TICKET)
        return ZendeskPaginator.create_search_tickets_paginator(
            self._http, query=query_str, per_page=per_page, limit=limit
        )

    def users(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> "OffsetPaginator[User]":
        """Search for users with pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through user results

        Example:
            # Iterate through users
            async for user in client.search.users(config, limit=10):
                print(user.name)

            # Get specific page
            paginator = client.search.users(config)
            page = await paginator.get_page(2)
        """
        query_str = self._resolve_query(query, force_type=SearchType.USER)
        return ZendeskPaginator.create_search_users_paginator(
            self._http, query=query_str, per_page=per_page, limit=limit
        )

    def organizations(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> "OffsetPaginator[Organization]":
        """Search for organizations with pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through organization results

        Example:
            # Iterate through organizations
            async for org in client.search.organizations(config, limit=10):
                print(org.name)

            # Get specific page
            paginator = client.search.organizations(config)
            page = await paginator.get_page(2)
        """
        query_str = self._resolve_query(query, force_type=SearchType.ORGANIZATION)
        return ZendeskPaginator.create_search_organizations_paginator(
            self._http, query=query_str, per_page=per_page, limit=limit
        )

    # Export methods (cursor-based pagination, no duplicates)

    def export_tickets(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> "CursorPaginator[Ticket]":
        """Export tickets using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string (empty = all tickets)
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            CursorPaginator for iterating through ticket results

        Example:
            async for ticket in client.search.export_tickets("status:open"):
                print(ticket)
        """
        query_str = self._resolve_query(query) or "*"
        return ZendeskPaginator.create_export_tickets_paginator(
            self._http, query=query_str, page_size=page_size, limit=limit
        )

    def export_users(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> "CursorPaginator[User]":
        """Export users using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            CursorPaginator for iterating through user results
        """
        query_str = self._resolve_query(query) or "*"
        return ZendeskPaginator.create_export_users_paginator(
            self._http, query=query_str, page_size=page_size, limit=limit
        )

    def export_organizations(
        self,
        query: Union[str, SearchQueryConfig] = "",
        page_size: int = 100,
        limit: Optional[int] = None,
    ) -> "CursorPaginator[Organization]":
        """Export organizations using cursor-based pagination.

        Uses /search/export endpoint which:
        - Returns results without duplicates
        - Uses cursor pagination (more stable for changing data)
        - Cursor expires after 1 hour

        Args:
            query: SearchQueryConfig or raw query string
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            CursorPaginator for iterating through organization results
        """
        query_str = self._resolve_query(query) or "*"
        return ZendeskPaginator.create_export_organizations_paginator(
            self._http, query=query_str, page_size=page_size, limit=limit
        )

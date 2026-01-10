"""Pagination utilities for Zendesk API."""

import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Generic, List, Optional, TypeVar

from .exceptions import ZendeskPaginationException
from .models import Article, Category, Comment, Organization, Section, Ticket, TicketField, User

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PaginationInfo:
    """Information about pagination state.

    Stores metadata from paginated API responses including current page,
    total count, and navigation cursors/URLs.

    Attributes:
        page: Current page number (1-based, for offset pagination).
        per_page: Number of items per page.
        count: Total number of items across all pages.
        next_page: URL to the next page (if available).
        previous_page: URL to the previous page (if available).
        has_more: Whether more pages are available.

    Example:
        paginator = client.tickets.list()
        await paginator.get_page(1)
        info = paginator.pagination_info
        print(f"Page {info.page}, total: {info.count}")
    """

    def __init__(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        count: Optional[int] = None,
        next_page: Optional[str] = None,
        previous_page: Optional[str] = None,
        has_more: Optional[bool] = None,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.count = count
        self.next_page = next_page
        self.previous_page = previous_page
        self.has_more = has_more

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "PaginationInfo":
        """Create pagination info from API response."""
        next_page = response.get("next_page")
        # Zendesk doesn't return has_more directly, but we can infer it from next_page
        has_more = response.get("has_more")
        if has_more is None and next_page is not None:
            has_more = True
        return cls(
            page=response.get("page"),
            per_page=response.get("per_page"),
            count=response.get("count"),
            next_page=next_page,
            previous_page=response.get("previous_page"),
            has_more=has_more,
        )

    def __repr__(self) -> str:
        return (
            f"PaginationInfo(page={self.page}, per_page={self.per_page}, count={self.count}, has_more={self.has_more})"
        )


class Paginator(ABC, Generic[T]):
    """Abstract base class for paginators.

    Provides common interface for paginating through Zendesk API results.
    Supports async iteration, page-by-page fetching, and collecting all results.

    Subclasses implement offset-based (OffsetPaginator) or cursor-based
    (CursorPaginator) pagination strategies.

    Args:
        http_client: HTTP client for making API requests.
        path: API endpoint path.
        params: Additional query parameters.
        per_page: Number of results per page.
        limit: Maximum total items to return (None = unlimited).

    Example:
        # Async iteration (most common)
        async for ticket in client.tickets.list():
            print(ticket.subject)

        # Limit results
        async for ticket in client.tickets.list(limit=50):
            print(ticket.subject)

        # Get specific page
        paginator = client.tickets.list()
        page_items = await paginator.get_page(2)

        # Collect all to list
        all_items = await paginator.collect()
    """

    def __init__(
        self,
        http_client: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> None:
        self.http_client = http_client
        self.path = path
        self.params = params or {}
        self.per_page = per_page
        self.limit = limit if limit else None  # 0 or None means no limit
        self._current_page = 1
        self._pagination_info: Optional[PaginationInfo] = None

    @abstractmethod
    async def _fetch_page(self, page_params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch a single page of data."""
        pass

    @abstractmethod
    def _extract_items(self, response: Dict[str, Any]) -> List[T]:
        """Extract items from API response."""
        pass

    @abstractmethod
    def _update_pagination_state(self, response: Dict[str, Any]) -> bool:
        """Update pagination state and return True if more pages available."""
        pass

    async def get_page(self, page: Optional[int] = None) -> List[T]:
        """Get a specific page of items."""
        if page is not None:
            self._current_page = page

        page_params = self._build_page_params()
        response = await self._fetch_page(page_params)
        self._update_pagination_state(response)

        return self._extract_items(response)

    def _build_page_params(self) -> Dict[str, Any]:
        """Build parameters for current page request."""
        params = self.params.copy()
        params.update(self._get_page_params())
        return params

    @abstractmethod
    def _get_page_params(self) -> Dict[str, Any]:
        """Get page-specific parameters."""
        pass

    @property
    def pagination_info(self) -> Optional[PaginationInfo]:
        """Get current pagination information."""
        return self._pagination_info

    async def __aiter__(self) -> AsyncIterator[T]:
        """Async iterator over all items across all pages."""
        from .exceptions import ZendeskHTTPException

        self._current_page = 1
        count = 0

        while True:
            try:
                items = await self.get_page()
                for item in items:
                    yield item
                    count += 1
                    if self.limit and count >= self.limit:
                        return

                # Check if there are more pages
                if not self._has_more_pages():
                    break

                self._advance_to_next_page()

            except ZendeskHTTPException as e:
                # Zendesk Search API returns 422 after ~1000 results (page 11+)
                # This is a known limitation, not an error
                if e.status_code == 422:
                    break
                raise ZendeskPaginationException(
                    f"Error during pagination: {str(e)}", {"page": self._current_page, "per_page": self.per_page}
                )
            except Exception as e:
                raise ZendeskPaginationException(
                    f"Error during pagination: {str(e)}", {"page": self._current_page, "per_page": self.per_page}
                )

    async def collect(self) -> List[T]:
        """Collect all items into a list.

        Returns:
            List of all items across all pages (respects limit if set)

        Example:
            comments = await client.tickets.comments.list(ticket_id).collect()
            tickets = await client.search.tickets(query, limit=50).collect()
        """
        return [item async for item in self]

    @abstractmethod
    def _has_more_pages(self) -> bool:
        """Check if there are more pages available."""
        pass

    @abstractmethod
    def _advance_to_next_page(self) -> None:
        """Advance to next page."""
        pass


class OffsetPaginator(Paginator[T]):
    """Offset-based paginator using page and per_page parameters.

    Standard pagination for most Zendesk endpoints. Uses page numbers
    to navigate through results.

    Note:
        Zendesk Search API limits offset pagination to approximately
        1000 results. Use cursor-based export endpoints for larger datasets.

    Example:
        paginator = client.users.list(per_page=50)
        async for user in paginator:
            print(user.name)
    """

    async def _fetch_page(self, page_params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch page using HTTP client."""
        return await self.http_client.get(self.path, params=page_params)

    def _extract_items(self, response: Dict[str, Any]) -> List[T]:
        """Extract items from response. Override in subclasses."""
        # This is a generic implementation - subclasses should override
        # to extract specific item types (users, tickets, etc.)
        return response.get("items", [])

    def _update_pagination_state(self, response: Dict[str, Any]) -> bool:
        """Update pagination state from response."""
        self._pagination_info = PaginationInfo.from_response(response)
        # Zendesk doesn't return page/per_page - fill from our internal state
        if self._pagination_info.page is None:
            self._pagination_info.page = self._current_page
        if self._pagination_info.per_page is None:
            self._pagination_info.per_page = self.per_page
        return self._has_more_pages()

    def _get_page_params(self) -> Dict[str, Any]:
        """Get offset-based page parameters."""
        return {"page": self._current_page, "per_page": self.per_page}

    def _has_more_pages(self) -> bool:
        """Check if more pages available using count and current page."""
        if not self._pagination_info:
            return False

        if self._pagination_info.has_more is not None:
            return self._pagination_info.has_more

        # Calculate based on count if available
        if self._pagination_info.count is not None:
            total_pages = (self._pagination_info.count + self.per_page - 1) // self.per_page
            return self._current_page < total_pages

        # Fallback: assume more pages if we got a full page
        return True

    def _advance_to_next_page(self) -> None:
        """Move to next page."""
        self._current_page += 1


class CursorPaginator(Paginator[T]):
    """Cursor-based paginator for large datasets.

    Uses opaque cursor tokens instead of page numbers. Provides stable
    iteration over changing data and supports datasets larger than
    offset pagination limits.

    Note:
        Cursors typically expire after 1 hour. For long-running exports,
        handle cursor expiration gracefully.

    Example:
        async for ticket in client.search.export_tickets("status:open"):
            print(ticket.subject)
    """

    def __init__(
        self,
        http_client: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> None:
        super().__init__(http_client, path, params, per_page, limit)
        self._next_cursor: Optional[str] = None
        self._has_started = False

    async def _fetch_page(self, page_params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch page using HTTP client."""
        return await self.http_client.get(self.path, params=page_params)

    def _extract_items(self, response: Dict[str, Any]) -> List[T]:
        """Extract items from response. Override in subclasses."""
        return response.get("items", [])

    def _update_pagination_state(self, response: Dict[str, Any]) -> bool:
        """Update cursor-based pagination state."""
        self._pagination_info = PaginationInfo.from_response(response)

        # Update cursor for next page
        self._next_cursor = response.get("next_cursor") or response.get("after_cursor")

        # Some APIs use different field names
        if not self._next_cursor:
            links = response.get("links", {})
            if "next" in links:
                # Extract cursor from next URL if needed
                self._next_cursor = str(links["next"])

        self._has_started = True
        return self._has_more_pages()

    def _get_page_params(self) -> Dict[str, Any]:
        """Get cursor-based page parameters."""
        params = {"per_page": self.per_page}

        if self._next_cursor and self._has_started:
            params["cursor"] = self._next_cursor  # type: ignore[assignment]

        return params

    def _has_more_pages(self) -> bool:
        """Check if more pages available using cursor."""
        if not self._has_started:
            return True

        if self._pagination_info and self._pagination_info.has_more is not None:
            return self._pagination_info.has_more

        # If we have a next cursor, there are more pages
        return self._next_cursor is not None

    def _advance_to_next_page(self) -> None:
        """Cursor advancement is handled in _update_pagination_state."""
        pass


class SearchExportPaginator(CursorPaginator[Dict[str, Any]]):
    """Cursor-based paginator for /search/export endpoint.

    This endpoint:
    - Uses cursor pagination (no duplicates)
    - Requires filter[type] parameter
    - Uses page[size] instead of per_page
    - Returns links.next and meta.after_cursor
    - Cursor expires after 1 hour

    Args:
        http_client: HTTP client for making API requests.
        query: Zendesk search query string.
        filter_type: Object type to filter (ticket, user, organization, group).
        page_size: Results per page (max 1000, recommended 100).
        limit: Maximum total items to return (None = unlimited).

    Example:
        paginator = SearchExportPaginator(http_client, "*", "ticket", 100)
        async for result in paginator:
            print(result)
    """

    def __init__(
        self, http_client: Any, query: str, filter_type: str, page_size: int = 100, limit: Optional[int] = None
    ) -> None:
        super().__init__(http_client, "search/export.json", per_page=page_size, limit=limit)
        self.query = query
        self.filter_type = filter_type
        self._next_url: Optional[str] = None

    def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        return response.get("results", [])

    def _update_pagination_state(self, response: Dict[str, Any]) -> bool:
        """Update cursor-based pagination state from export response."""
        # Export uses different structure: links.next and meta.has_more
        links = response.get("links", {})
        meta = response.get("meta", {})

        self._next_url = links.get("next")
        self._next_cursor = meta.get("after_cursor")

        # Update pagination info
        self._pagination_info = PaginationInfo(
            has_more=meta.get("has_more", False),
            next_page=self._next_url,
        )

        self._has_started = True
        return self._has_more_pages()

    def _get_page_params(self) -> Dict[str, Any]:
        """Get export-specific page parameters."""
        params: Dict[str, Any] = {
            "query": self.query,
            "filter[type]": self.filter_type,
            "page[size]": self.per_page,
        }

        if self._next_cursor and self._has_started:
            params["page[after]"] = self._next_cursor

        return params

    def _has_more_pages(self) -> bool:
        """Check if more pages available."""
        if not self._has_started:
            return True

        if self._pagination_info and self._pagination_info.has_more is not None:
            return self._pagination_info.has_more

        return self._next_cursor is not None


class ZendeskPaginator:
    """Factory for creating Zendesk-specific paginators.

    Provides static methods to create pre-configured paginators for
    various Zendesk API endpoints. Each method returns a paginator
    that handles response parsing and model instantiation.

    This is an internal factory class. Users should access paginators
    through the client API methods instead.

    Example:
        # Internal usage (not recommended for external use)
        paginator = ZendeskPaginator.create_tickets_paginator(http_client)

        # Preferred: use client methods
        async for ticket in client.tickets.list():
            print(ticket.subject)
    """

    @staticmethod
    def create_users_paginator(
        http_client: Any, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[User]:
        """Create paginator for users endpoint."""

        class UsersPaginator(OffsetPaginator[User]):
            def _extract_items(self, response: Dict[str, Any]) -> List[User]:
                return [User(**u) for u in response.get("users", [])]

        return UsersPaginator(http_client, "users.json", per_page=per_page, limit=limit)

    @staticmethod
    def create_tickets_paginator(
        http_client: Any, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Ticket]:
        """Create paginator for tickets endpoint."""

        class TicketsPaginator(OffsetPaginator[Ticket]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Ticket]:
                return [Ticket(**t) for t in response.get("tickets", [])]

        return TicketsPaginator(http_client, "tickets.json", per_page=per_page, limit=limit)

    @staticmethod
    def create_user_tickets_paginator(
        http_client: Any, user_id: int, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Ticket]:
        """Create paginator for user's requested tickets endpoint."""

        class UserTicketsPaginator(OffsetPaginator[Ticket]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Ticket]:
                return [Ticket(**t) for t in response.get("tickets", [])]

        return UserTicketsPaginator(
            http_client, f"users/{user_id}/tickets/requested.json", per_page=per_page, limit=limit
        )

    @staticmethod
    def create_organization_tickets_paginator(
        http_client: Any, organization_id: int, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Ticket]:
        """Create paginator for organization's tickets endpoint."""

        class OrganizationTicketsPaginator(OffsetPaginator[Ticket]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Ticket]:
                return [Ticket(**t) for t in response.get("tickets", [])]

        return OrganizationTicketsPaginator(
            http_client, f"organizations/{organization_id}/tickets.json", per_page=per_page, limit=limit
        )

    @staticmethod
    def create_ticket_comments_paginator(
        http_client: Any, ticket_id: int, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Comment]:
        """Create paginator for ticket comments endpoint."""

        class TicketCommentsPaginator(OffsetPaginator[Comment]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Comment]:
                return [Comment(**c) for c in response.get("comments", [])]

        return TicketCommentsPaginator(
            http_client, f"tickets/{ticket_id}/comments.json", per_page=per_page, limit=limit
        )

    @staticmethod
    def create_organizations_paginator(
        http_client: Any, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Organization]:
        """Create paginator for organizations endpoint."""

        class OrganizationsPaginator(OffsetPaginator[Organization]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Organization]:
                return [Organization(**o) for o in response.get("organizations", [])]

        return OrganizationsPaginator(http_client, "organizations.json", per_page=per_page, limit=limit)

    @staticmethod
    def create_ticket_fields_paginator(
        http_client: Any, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[TicketField]:
        """Create paginator for ticket fields endpoint."""

        class TicketFieldsPaginator(OffsetPaginator[TicketField]):
            def _extract_items(self, response: Dict[str, Any]) -> List[TicketField]:
                return [TicketField(**f) for f in response.get("ticket_fields", [])]

        return TicketFieldsPaginator(http_client, "ticket_fields.json", per_page=per_page, limit=limit)

    @staticmethod
    def create_search_paginator(
        http_client: Any, query: str, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for search endpoint (raw results)."""

        class SearchPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("results", [])

        return SearchPaginator(http_client, "search.json", params={"query": query}, per_page=per_page, limit=limit)

    @staticmethod
    def create_search_tickets_paginator(
        http_client: Any, query: str, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Ticket]:
        """Create paginator for ticket search. Query should include type:ticket."""

        class SearchTicketsPaginator(OffsetPaginator[Ticket]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Ticket]:
                return [Ticket(**r) for r in response.get("results", []) if r.get("result_type") == "ticket"]

        return SearchTicketsPaginator(
            http_client, "search.json", params={"query": query}, per_page=per_page, limit=limit
        )

    @staticmethod
    def create_search_users_paginator(
        http_client: Any, query: str, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[User]:
        """Create paginator for user search. Query should include type:user."""

        class SearchUsersPaginator(OffsetPaginator[User]):
            def _extract_items(self, response: Dict[str, Any]) -> List[User]:
                return [User(**r) for r in response.get("results", []) if r.get("result_type") == "user"]

        return SearchUsersPaginator(http_client, "search.json", params={"query": query}, per_page=per_page, limit=limit)

    @staticmethod
    def create_search_organizations_paginator(
        http_client: Any, query: str, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Organization]:
        """Create paginator for organization search. Query should include type:organization."""

        class SearchOrganizationsPaginator(OffsetPaginator[Organization]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Organization]:
                return [
                    Organization(**r) for r in response.get("results", []) if r.get("result_type") == "organization"
                ]

        return SearchOrganizationsPaginator(
            http_client, "search.json", params={"query": query}, per_page=per_page, limit=limit
        )

    @staticmethod
    def create_search_export_paginator(
        http_client: Any, query: str, filter_type: str, page_size: int = 100, limit: Optional[int] = None
    ) -> "SearchExportPaginator":
        """Create cursor-based paginator for search export endpoint (raw results).

        Args:
            http_client: HTTP client instance
            query: Search query string
            filter_type: Object type to filter (ticket, user, organization, group)
            page_size: Results per page (max 1000, recommended 100)
            limit: Maximum number of items to return (None = no limit)

        Returns:
            SearchExportPaginator for cursor-based iteration
        """
        return SearchExportPaginator(http_client, query, filter_type, page_size, limit=limit)

    @staticmethod
    def create_export_tickets_paginator(
        http_client: Any, query: str, page_size: int = 100, limit: Optional[int] = None
    ) -> CursorPaginator[Ticket]:
        """Create cursor-based paginator for ticket export."""

        class ExportTicketsPaginator(SearchExportPaginator):
            def _extract_items(self, response: Dict[str, Any]) -> List[Ticket]:
                return [Ticket(**r) for r in response.get("results", [])]

        return ExportTicketsPaginator(http_client, query, "ticket", page_size, limit=limit)

    @staticmethod
    def create_export_users_paginator(
        http_client: Any, query: str, page_size: int = 100, limit: Optional[int] = None
    ) -> CursorPaginator[User]:
        """Create cursor-based paginator for user export."""

        class ExportUsersPaginator(SearchExportPaginator):
            def _extract_items(self, response: Dict[str, Any]) -> List[User]:
                return [User(**r) for r in response.get("results", [])]

        return ExportUsersPaginator(http_client, query, "user", page_size, limit=limit)

    @staticmethod
    def create_export_organizations_paginator(
        http_client: Any, query: str, page_size: int = 100, limit: Optional[int] = None
    ) -> CursorPaginator[Organization]:
        """Create cursor-based paginator for organization export."""

        class ExportOrganizationsPaginator(SearchExportPaginator):
            def _extract_items(self, response: Dict[str, Any]) -> List[Organization]:
                return [Organization(**r) for r in response.get("results", [])]

        return ExportOrganizationsPaginator(http_client, query, "organization", page_size, limit=limit)

    @staticmethod
    def create_incremental_paginator(
        http_client: Any, resource_type: str, start_time: int, limit: Optional[int] = None
    ) -> CursorPaginator[Dict[str, Any]]:
        """Create cursor-based paginator for incremental exports."""

        class IncrementalPaginator(CursorPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get(resource_type, [])

        path = f"incremental/{resource_type}.json"
        params = {"start_time": start_time}
        return IncrementalPaginator(http_client, path, params=params, limit=limit)

    # Help Center paginators

    @staticmethod
    def create_categories_paginator(
        http_client: Any, per_page: int = 100, limit: Optional[int] = None
    ) -> OffsetPaginator[Category]:
        """Create paginator for Help Center categories endpoint."""

        class CategoriesPaginator(OffsetPaginator[Category]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Category]:
                return [Category(**c) for c in response.get("categories", [])]

        return CategoriesPaginator(http_client, "help_center/categories.json", per_page=per_page, limit=limit)

    @staticmethod
    def create_sections_paginator(
        http_client: Any, per_page: int = 100, category_id: Optional[int] = None, limit: Optional[int] = None
    ) -> OffsetPaginator[Section]:
        """Create paginator for Help Center sections endpoint.

        Args:
            http_client: HTTP client instance
            per_page: Number of items per page
            category_id: If provided, list sections only in this category
            limit: Maximum number of items to return (None = no limit)
        """

        class SectionsPaginator(OffsetPaginator[Section]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Section]:
                return [Section(**s) for s in response.get("sections", [])]

        if category_id:
            path = f"help_center/categories/{category_id}/sections.json"
        else:
            path = "help_center/sections.json"
        return SectionsPaginator(http_client, path, per_page=per_page, limit=limit)

    @staticmethod
    def create_articles_paginator(
        http_client: Any,
        per_page: int = 100,
        section_id: Optional[int] = None,
        category_id: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> OffsetPaginator[Article]:
        """Create paginator for Help Center articles endpoint.

        Args:
            http_client: HTTP client instance
            per_page: Number of items per page
            section_id: If provided, list articles only in this section
            category_id: If provided, list articles only in this category
            limit: Maximum number of items to return (None = no limit)
        """

        class ArticlesPaginator(OffsetPaginator[Article]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Article]:
                return [Article(**a) for a in response.get("articles", [])]

        if section_id:
            path = f"help_center/sections/{section_id}/articles.json"
        elif category_id:
            path = f"help_center/categories/{category_id}/articles.json"
        else:
            path = "help_center/articles.json"
        return ArticlesPaginator(http_client, path, per_page=per_page, limit=limit)

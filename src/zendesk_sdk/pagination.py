"""Pagination utilities for Zendesk API."""

import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Generic, List, Optional, TypeVar

from .exceptions import ZendeskPaginationException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PaginationInfo:
    """Information about pagination state."""

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
        return cls(
            page=response.get("page"),
            per_page=response.get("per_page"),
            count=response.get("count"),
            next_page=response.get("next_page"),
            previous_page=response.get("previous_page"),
            has_more=response.get("has_more"),
        )

    def __repr__(self) -> str:
        return (
            f"PaginationInfo(page={self.page}, per_page={self.per_page}, count={self.count}, has_more={self.has_more})"
        )


class Paginator(ABC, Generic[T]):
    """Abstract base class for paginators."""

    def __init__(
        self, http_client: Any, path: str, params: Optional[Dict[str, Any]] = None, per_page: int = 100
    ) -> None:
        self.http_client = http_client
        self.path = path
        self.params = params or {}
        self.per_page = per_page
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

        while True:
            try:
                items = await self.get_page()
                for item in items:
                    yield item

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

    @abstractmethod
    def _has_more_pages(self) -> bool:
        """Check if there are more pages available."""
        pass

    @abstractmethod
    def _advance_to_next_page(self) -> None:
        """Advance to next page."""
        pass


class OffsetPaginator(Paginator[T]):
    """Offset-based paginator using page and per_page parameters."""

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
    """Cursor-based paginator for large datasets."""

    def __init__(
        self, http_client: Any, path: str, params: Optional[Dict[str, Any]] = None, per_page: int = 100
    ) -> None:
        super().__init__(http_client, path, params, per_page)
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
    """

    def __init__(self, http_client: Any, query: str, filter_type: str, page_size: int = 100) -> None:
        super().__init__(http_client, "search/export.json", per_page=page_size)
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
    """Factory for creating Zendesk-specific paginators."""

    @staticmethod
    def create_users_paginator(http_client: Any, per_page: int = 100) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for users endpoint."""

        class UsersPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("users", [])

        return UsersPaginator(http_client, "users.json", per_page=per_page)

    @staticmethod
    def create_tickets_paginator(http_client: Any, per_page: int = 100) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for tickets endpoint."""

        class TicketsPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("tickets", [])

        return TicketsPaginator(http_client, "tickets.json", per_page=per_page)

    @staticmethod
    def create_organizations_paginator(http_client: Any, per_page: int = 100) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for organizations endpoint."""

        class OrganizationsPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("organizations", [])

        return OrganizationsPaginator(http_client, "organizations.json", per_page=per_page)

    @staticmethod
    def create_search_paginator(http_client: Any, query: str, per_page: int = 100) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for search endpoint."""

        class SearchPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("results", [])

        return SearchPaginator(http_client, "search.json", params={"query": query}, per_page=per_page)

    @staticmethod
    def create_search_export_paginator(
        http_client: Any, query: str, filter_type: str, page_size: int = 100
    ) -> "SearchExportPaginator":
        """Create cursor-based paginator for search export endpoint.

        Args:
            http_client: HTTP client instance
            query: Search query string
            filter_type: Object type to filter (ticket, user, organization, group)
            page_size: Results per page (max 1000, recommended 100)

        Returns:
            SearchExportPaginator for cursor-based iteration
        """
        return SearchExportPaginator(http_client, query, filter_type, page_size)

    @staticmethod
    def create_incremental_paginator(
        http_client: Any, resource_type: str, start_time: int
    ) -> CursorPaginator[Dict[str, Any]]:
        """Create cursor-based paginator for incremental exports."""

        class IncrementalPaginator(CursorPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get(resource_type, [])

        path = f"incremental/{resource_type}.json"
        params = {"start_time": start_time}
        return IncrementalPaginator(http_client, path, params=params)

    # Help Center paginators

    @staticmethod
    def create_categories_paginator(http_client: Any, per_page: int = 100) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for Help Center categories endpoint."""

        class CategoriesPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("categories", [])

        return CategoriesPaginator(http_client, "help_center/categories.json", per_page=per_page)

    @staticmethod
    def create_sections_paginator(
        http_client: Any, per_page: int = 100, category_id: Optional[int] = None
    ) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for Help Center sections endpoint.

        Args:
            http_client: HTTP client instance
            per_page: Number of items per page
            category_id: If provided, list sections only in this category
        """

        class SectionsPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("sections", [])

        if category_id:
            path = f"help_center/categories/{category_id}/sections.json"
        else:
            path = "help_center/sections.json"
        return SectionsPaginator(http_client, path, per_page=per_page)

    @staticmethod
    def create_articles_paginator(
        http_client: Any, per_page: int = 100, section_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> OffsetPaginator[Dict[str, Any]]:
        """Create paginator for Help Center articles endpoint.

        Args:
            http_client: HTTP client instance
            per_page: Number of items per page
            section_id: If provided, list articles only in this section
            category_id: If provided, list articles only in this category
        """

        class ArticlesPaginator(OffsetPaginator[Dict[str, Any]]):
            def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
                return response.get("articles", [])

        if section_id:
            path = f"help_center/sections/{section_id}/articles.json"
        elif category_id:
            path = f"help_center/categories/{category_id}/articles.json"
        else:
            path = "help_center/articles.json"
        return ArticlesPaginator(http_client, path, per_page=per_page)

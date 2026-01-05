"""Tests for pagination functionality."""

from unittest.mock import AsyncMock, Mock

import pytest

from zendesk_sdk.exceptions import ZendeskPaginationException
from zendesk_sdk.pagination import (
    CursorPaginator,
    OffsetPaginator,
    PaginationInfo,
    ZendeskPaginator,
)


class TestPaginationInfo:
    """Test cases for PaginationInfo."""

    def test_init_with_defaults(self):
        """Test PaginationInfo initialization with defaults."""
        info = PaginationInfo()
        assert info.page is None
        assert info.per_page is None
        assert info.count is None
        assert info.next_page is None
        assert info.previous_page is None
        assert info.has_more is None

    def test_init_with_values(self):
        """Test PaginationInfo initialization with values."""
        info = PaginationInfo(
            page=2,
            per_page=50,
            count=150,
            next_page="https://test.zendesk.com/api/v2/users.json?page=3",
            previous_page="https://test.zendesk.com/api/v2/users.json?page=1",
            has_more=True,
        )
        assert info.page == 2
        assert info.per_page == 50
        assert info.count == 150
        assert info.next_page == "https://test.zendesk.com/api/v2/users.json?page=3"
        assert info.previous_page == "https://test.zendesk.com/api/v2/users.json?page=1"
        assert info.has_more is True

    def test_from_response(self):
        """Test creating PaginationInfo from API response."""
        response = {
            "page": 1,
            "per_page": 100,
            "count": 250,
            "next_page": "https://test.zendesk.com/api/v2/users.json?page=2",
            "has_more": True,
        }
        info = PaginationInfo.from_response(response)
        assert info.page == 1
        assert info.per_page == 100
        assert info.count == 250
        assert info.next_page == "https://test.zendesk.com/api/v2/users.json?page=2"
        assert info.has_more is True

    def test_from_response_missing_fields(self):
        """Test creating PaginationInfo with missing fields."""
        response = {"page": 1}
        info = PaginationInfo.from_response(response)
        assert info.page == 1
        assert info.per_page is None
        assert info.count is None

    def test_repr(self):
        """Test string representation."""
        info = PaginationInfo(page=1, per_page=100, count=250, has_more=True)
        repr_str = repr(info)
        assert "PaginationInfo" in repr_str
        assert "page=1" in repr_str
        assert "per_page=100" in repr_str
        assert "count=250" in repr_str
        assert "has_more=True" in repr_str


class TestOffsetPaginator:
    """Test cases for OffsetPaginator."""

    def test_init(self):
        """Test OffsetPaginator initialization."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json", params={"sort": "name"}, per_page=50)

        assert paginator.http_client == http_client
        assert paginator.path == "users.json"
        assert paginator.params == {"sort": "name"}
        assert paginator.per_page == 50
        assert paginator._current_page == 1
        assert paginator._pagination_info is None

    def test_get_page_params(self):
        """Test offset-based page parameters generation."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json", per_page=25)
        paginator._current_page = 3

        params = paginator._get_page_params()
        assert params == {"page": 3, "per_page": 25}

    def test_build_page_params(self):
        """Test building complete page parameters."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json", params={"sort": "name"}, per_page=50)
        paginator._current_page = 2

        params = paginator._build_page_params()
        expected = {"sort": "name", "page": 2, "per_page": 50}
        assert params == expected

    def test_extract_items_default(self):
        """Test default item extraction."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "test.json")

        response = {"items": [{"id": 1}, {"id": 2}]}
        items = paginator._extract_items(response)
        assert items == [{"id": 1}, {"id": 2}]

    def test_extract_items_empty(self):
        """Test item extraction with empty response."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "test.json")

        response = {}
        items = paginator._extract_items(response)
        assert items == []

    def test_update_pagination_state(self):
        """Test pagination state update."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json")

        response = {"page": 1, "per_page": 100, "count": 250, "has_more": True}
        has_more = paginator._update_pagination_state(response)

        assert paginator._pagination_info.page == 1
        assert paginator._pagination_info.count == 250
        assert has_more is True

    def test_has_more_pages_with_has_more_field(self):
        """Test has_more_pages with explicit has_more field."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json")
        paginator._pagination_info = PaginationInfo(has_more=True)

        assert paginator._has_more_pages() is True

        paginator._pagination_info = PaginationInfo(has_more=False)
        assert paginator._has_more_pages() is False

    def test_has_more_pages_with_count(self):
        """Test has_more_pages calculation using count."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json", per_page=100)
        paginator._current_page = 2
        paginator._pagination_info = PaginationInfo(count=250)

        # Page 2 of 3 pages (250 items / 100 per page = 3 pages)
        assert paginator._has_more_pages() is True

        paginator._current_page = 3
        assert paginator._has_more_pages() is False

    def test_has_more_pages_fallback(self):
        """Test has_more_pages fallback behavior."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json")
        paginator._pagination_info = PaginationInfo()

        # Should return True as fallback
        assert paginator._has_more_pages() is True

    def test_has_more_pages_no_pagination_info(self):
        """Test has_more_pages with no pagination info."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json")

        assert paginator._has_more_pages() is False

    def test_advance_to_next_page(self):
        """Test advancing to next page."""
        http_client = Mock()
        paginator = OffsetPaginator(http_client, "users.json")

        assert paginator._current_page == 1
        paginator._advance_to_next_page()
        assert paginator._current_page == 2

    @pytest.mark.asyncio
    async def test_get_page(self):
        """Test getting a specific page."""
        http_client = AsyncMock()
        paginator = OffsetPaginator(http_client, "users.json")

        # Mock HTTP response
        mock_response = {"page": 1, "per_page": 100, "count": 150, "items": [{"id": 1}, {"id": 2}]}
        http_client.get.return_value = mock_response

        items = await paginator.get_page()

        assert items == [{"id": 1}, {"id": 2}]
        http_client.get.assert_called_once_with("users.json", params={"page": 1, "per_page": 100})

    @pytest.mark.asyncio
    async def test_get_page_specific_page_number(self):
        """Test getting a specific page number."""
        http_client = AsyncMock()
        paginator = OffsetPaginator(http_client, "users.json")

        mock_response = {"page": 3, "per_page": 100, "items": [{"id": 5}, {"id": 6}]}
        http_client.get.return_value = mock_response

        items = await paginator.get_page(page=3)

        assert items == [{"id": 5}, {"id": 6}]
        assert paginator._current_page == 3
        http_client.get.assert_called_once_with("users.json", params={"page": 3, "per_page": 100})

    @pytest.mark.asyncio
    async def test_async_iterator(self):
        """Test async iterator functionality."""
        http_client = AsyncMock()
        paginator = OffsetPaginator(http_client, "users.json", per_page=2)

        # Mock responses for 3 pages
        responses = [
            {"page": 1, "per_page": 2, "count": 5, "items": [{"id": 1}, {"id": 2}]},
            {"page": 2, "per_page": 2, "count": 5, "items": [{"id": 3}, {"id": 4}]},
            {"page": 3, "per_page": 2, "count": 5, "items": [{"id": 5}]},
        ]
        http_client.get.side_effect = responses

        items = []
        async for item in paginator:
            items.append(item)

        assert len(items) == 5
        assert items == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
        assert http_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_async_iterator_error_handling(self):
        """Test async iterator error handling."""
        http_client = AsyncMock()
        paginator = OffsetPaginator(http_client, "users.json")

        http_client.get.side_effect = Exception("Network error")

        with pytest.raises(ZendeskPaginationException) as exc_info:
            async for item in paginator:
                pass

        assert "Error during pagination" in str(exc_info.value)
        assert exc_info.value.page_info["page"] == 1


class TestCursorPaginator:
    """Test cases for CursorPaginator."""

    def test_init(self):
        """Test CursorPaginator initialization."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json", params={"start_time": 1234567890})

        assert paginator.http_client == http_client
        assert paginator.path == "incremental/tickets.json"
        assert paginator.params == {"start_time": 1234567890}
        assert paginator._next_cursor is None
        assert not paginator._has_started

    def test_get_page_params_initial(self):
        """Test cursor-based page parameters for initial request."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json", per_page=50)

        params = paginator._get_page_params()
        assert params == {"per_page": 50}

    def test_get_page_params_with_cursor(self):
        """Test cursor-based page parameters with cursor."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json", per_page=50)
        paginator._next_cursor = "abc123"
        paginator._has_started = True

        params = paginator._get_page_params()
        assert params == {"per_page": 50, "cursor": "abc123"}

    def test_extract_items_default(self):
        """Test default item extraction for cursor paginator."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "test.json")

        response = {"items": [{"id": 1}, {"id": 2}]}
        items = paginator._extract_items(response)
        assert items == [{"id": 1}, {"id": 2}]

    def test_update_pagination_state_with_next_cursor(self):
        """Test pagination state update with next cursor."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")

        response = {
            "next_cursor": "xyz789",
            "has_more": True,
            "items": [{"id": 1}],
        }
        has_more = paginator._update_pagination_state(response)

        assert paginator._next_cursor == "xyz789"
        assert paginator._has_started
        assert has_more is True

    def test_update_pagination_state_with_after_cursor(self):
        """Test pagination state update with after_cursor field."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")

        response = {
            "after_cursor": "abc123",
            "items": [{"id": 1}],
        }
        paginator._update_pagination_state(response)

        assert paginator._next_cursor == "abc123"
        assert paginator._has_started

    def test_update_pagination_state_with_links(self):
        """Test pagination state update with links field."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")

        response = {
            "links": {"next": "https://test.zendesk.com/api/v2/tickets.json?cursor=def456"},
            "items": [{"id": 1}],
        }
        paginator._update_pagination_state(response)

        assert paginator._next_cursor == "https://test.zendesk.com/api/v2/tickets.json?cursor=def456"
        assert paginator._has_started

    def test_has_more_pages_not_started(self):
        """Test has_more_pages when not started."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")

        assert paginator._has_more_pages() is True

    def test_has_more_pages_with_has_more_field(self):
        """Test has_more_pages with explicit has_more field."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")
        paginator._has_started = True
        paginator._pagination_info = PaginationInfo(has_more=False)

        assert paginator._has_more_pages() is False

    def test_has_more_pages_with_cursor(self):
        """Test has_more_pages based on cursor presence."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")
        paginator._has_started = True
        paginator._next_cursor = "abc123"

        assert paginator._has_more_pages() is True

        paginator._next_cursor = None
        assert paginator._has_more_pages() is False

    def test_advance_to_next_page(self):
        """Test advance to next page (no-op for cursor paginator)."""
        http_client = Mock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json")

        # Should be a no-op since cursor advancement is handled in _update_pagination_state
        paginator._advance_to_next_page()
        # No assertion needed, just ensuring it doesn't crash

    @pytest.mark.asyncio
    async def test_async_iterator_cursor_based(self):
        """Test async iterator for cursor-based pagination."""
        http_client = AsyncMock()
        paginator = CursorPaginator(http_client, "incremental/tickets.json", per_page=2)

        # Mock responses with cursors
        responses = [
            {"next_cursor": "cursor2", "items": [{"id": 1}, {"id": 2}]},
            {"next_cursor": "cursor3", "items": [{"id": 3}, {"id": 4}]},
            {"items": [{"id": 5}]},  # No next_cursor means end
        ]
        http_client.get.side_effect = responses

        items = []
        async for item in paginator:
            items.append(item)

        assert len(items) == 5
        assert items == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
        assert http_client.get.call_count == 3


class TestZendeskPaginator:
    """Test cases for ZendeskPaginator factory."""

    def test_create_users_paginator(self):
        """Test creating users paginator."""
        from zendesk_sdk.models import User

        http_client = Mock()
        paginator = ZendeskPaginator.create_users_paginator(http_client, per_page=50)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "users.json"
        assert paginator.per_page == 50

        # Test users-specific item extraction - now returns User models
        response = {"users": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]}
        items = paginator._extract_items(response)
        assert len(items) == 2
        assert all(isinstance(item, User) for item in items)
        assert items[0].id == 1
        assert items[0].name == "User 1"
        assert items[1].id == 2
        assert items[1].name == "User 2"

    def test_create_tickets_paginator(self):
        """Test creating tickets paginator."""
        from zendesk_sdk.models import Ticket

        http_client = Mock()
        paginator = ZendeskPaginator.create_tickets_paginator(http_client, per_page=25)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "tickets.json"
        assert paginator.per_page == 25

        # Test tickets-specific item extraction - now returns Ticket models
        response = {"tickets": [{"id": 1, "subject": "Test Ticket"}]}
        items = paginator._extract_items(response)
        assert len(items) == 1
        assert isinstance(items[0], Ticket)
        assert items[0].id == 1
        assert items[0].subject == "Test Ticket"

    def test_create_organizations_paginator(self):
        """Test creating organizations paginator."""
        from zendesk_sdk.models import Organization

        http_client = Mock()
        paginator = ZendeskPaginator.create_organizations_paginator(http_client, per_page=75)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "organizations.json"
        assert paginator.per_page == 75

        # Test organizations-specific item extraction - now returns Organization models
        response = {"organizations": [{"id": 1, "name": "Test Org"}]}
        items = paginator._extract_items(response)
        assert len(items) == 1
        assert isinstance(items[0], Organization)
        assert items[0].id == 1
        assert items[0].name == "Test Org"

    def test_create_search_paginator(self):
        """Test creating search paginator."""
        http_client = Mock()
        query = "type:user status:active"
        paginator = ZendeskPaginator.create_search_paginator(http_client, query, per_page=30)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "search.json"
        assert paginator.params == {"query": query}
        assert paginator.per_page == 30

        # Test search-specific item extraction
        response = {"results": [{"id": 1, "result_type": "user"}, {"id": 2, "result_type": "ticket"}]}
        items = paginator._extract_items(response)
        assert items == [{"id": 1, "result_type": "user"}, {"id": 2, "result_type": "ticket"}]

    def test_create_incremental_paginator(self):
        """Test creating incremental export paginator."""
        http_client = Mock()
        start_time = 1234567890
        paginator = ZendeskPaginator.create_incremental_paginator(http_client, "tickets", start_time)

        assert isinstance(paginator, CursorPaginator)
        assert paginator.path == "incremental/tickets.json"
        assert paginator.params == {"start_time": start_time}

        # Test incremental-specific item extraction
        response = {"tickets": [{"id": 1, "updated_at": "2023-01-01T00:00:00Z"}]}
        items = paginator._extract_items(response)
        assert items == [{"id": 1, "updated_at": "2023-01-01T00:00:00Z"}]

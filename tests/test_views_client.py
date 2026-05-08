"""Tests for ViewsClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zendesk_sdk.clients import ViewsClient
from zendesk_sdk.models import Ticket, View, ViewCount
from zendesk_sdk.pagination import OffsetPaginator, ZendeskPaginator


class TestViewsClient:
    """Test cases for ViewsClient."""

    def get_client(self) -> ViewsClient:
        """Create a ViewsClient with a mock HTTP client (no cache)."""
        return ViewsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        """Get a view by id."""
        client = self.get_client()
        payload = {
            "view": {
                "id": 12345,
                "title": "My Open Tickets",
                "active": True,
                "default": False,
                "position": 1,
                "conditions": {"all": [{"field": "status", "operator": "less_than", "value": "solved"}]},
                "execution": {"sort_by": "created_at", "sort_order": "desc", "columns": []},
                "restriction": None,
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.get(12345)

            assert isinstance(result, View)
            assert result.id == 12345
            assert result.title == "My Open Tickets"
            assert result.active is True
            assert result.conditions == {"all": [{"field": "status", "operator": "less_than", "value": "solved"}]}
            mock_get.assert_called_once_with("views/12345.json")

    def test_list_returns_paginator(self) -> None:
        """list() returns an OffsetPaginator over Views."""
        client = self.get_client()

        paginator = client.list(per_page=50, limit=200)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "views.json"
        assert paginator.per_page == 50
        assert paginator.limit == 200

    def test_list_active_only_uses_different_endpoint(self) -> None:
        """list(active_only=True) hits /views/active.json."""
        client = self.get_client()
        paginator = client.list(active_only=True)
        assert paginator.path == "views/active.json"

    @pytest.mark.asyncio
    async def test_list_iterates_and_deserializes(self) -> None:
        """Paginator yields View objects from a real API response shape."""
        http_client = AsyncMock()
        http_client.get.return_value = {
            "views": [
                {"id": 1, "title": "View 1", "active": True},
                {"id": 2, "title": "View 2", "active": False},
            ],
            "page": 1,
            "per_page": 100,
            "count": 2,
        }

        paginator = ZendeskPaginator.create_views_paginator(http_client)
        items = await paginator.collect()

        assert len(items) == 2
        assert all(isinstance(v, View) for v in items)
        assert items[0].title == "View 1"
        assert items[1].active is False

    @pytest.mark.asyncio
    async def test_get_many(self) -> None:
        """get_many returns a {id: View} dict and dedupes ids."""
        client = self.get_client()
        payload = {
            "views": [
                {"id": 1, "title": "First"},
                {"id": 2, "title": "Second"},
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.get_many([1, 2, 1])

            assert set(result.keys()) == {1, 2}
            assert result[1].title == "First"
            # The query string contains both ids in some order
            called_path = mock_get.call_args.args[0]
            assert called_path.startswith("views/show_many.json?ids=")
            ids_in_path = sorted(called_path.split("ids=")[1].split(","))
            assert ids_in_path == ["1", "2"]

    @pytest.mark.asyncio
    async def test_get_many_empty_returns_empty(self) -> None:
        """get_many([]) short-circuits — no HTTP call."""
        client = self.get_client()
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            result = await client.get_many([])
            assert result == {}
            mock_get.assert_not_called()

    def test_tickets_returns_paginator(self) -> None:
        """tickets(view_id) returns paginator pointed at the right path."""
        client = self.get_client()

        paginator = client.tickets(42, per_page=50)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "views/42/tickets.json"
        assert paginator.per_page == 50

    @pytest.mark.asyncio
    async def test_tickets_iterates_and_deserializes(self) -> None:
        """View tickets paginator yields Ticket objects."""
        http_client = AsyncMock()
        http_client.get.return_value = {
            "tickets": [
                {"id": 100, "subject": "Hello"},
                {"id": 101, "subject": "World"},
            ],
            "page": 1,
            "per_page": 100,
            "count": 2,
        }

        paginator = ZendeskPaginator.create_view_tickets_paginator(http_client, 42)
        items = await paginator.collect()

        assert len(items) == 2
        assert all(isinstance(t, Ticket) for t in items)
        assert items[0].id == 100

    @pytest.mark.asyncio
    async def test_count(self) -> None:
        """count() returns ViewCount with value/fresh."""
        client = self.get_client()
        payload = {
            "view_count": {
                "view_id": 12345,
                "url": "https://example.zendesk.com/api/v2/views/12345/count.json",
                "value": 42,
                "pretty": "42",
                "fresh": True,
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.count(12345)

            assert isinstance(result, ViewCount)
            assert result.view_id == 12345
            assert result.value == 42
            assert result.fresh is True
            mock_get.assert_called_once_with("views/12345/count.json")

    @pytest.mark.asyncio
    async def test_count_many(self) -> None:
        """count_many returns a list of ViewCount objects."""
        client = self.get_client()
        payload = {
            "view_counts": [
                {"view_id": 1, "value": 10, "fresh": True, "pretty": "10"},
                {"view_id": 2, "value": 0, "fresh": True, "pretty": "0"},
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.count_many([1, 2])

            assert len(result) == 2
            assert all(isinstance(c, ViewCount) for c in result)
            assert {c.view_id for c in result} == {1, 2}
            called_path = mock_get.call_args.args[0]
            assert called_path.startswith("views/count_many.json?ids=")

    @pytest.mark.asyncio
    async def test_count_many_empty(self) -> None:
        """count_many([]) short-circuits."""
        client = self.get_client()
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            result = await client.count_many([])
            assert result == []
            mock_get.assert_not_called()

    def test_no_write_methods(self) -> None:
        """Read-only client must not expose create/update/delete."""
        client = self.get_client()
        for method in ("create", "update", "delete"):
            assert not hasattr(client, method), f"ViewsClient should not expose {method}"


class TestViewModel:
    """Smoke tests for the View pydantic model."""

    def test_minimal_payload(self) -> None:
        v = View(id=1, title="X", active=True)
        assert v.id == 1
        assert v.title == "X"
        assert "id=1" in str(v)

    def test_extra_fields_ignored(self) -> None:
        """Unknown API fields don't break parsing (extra='ignore')."""
        v = View(
            id=1,
            title="X",
            active=True,
            some_unknown_field="value",  # type: ignore[call-arg]
        )
        assert v.id == 1


class TestViewsClientCaching:
    """Cache wiring smoke test — get() should be cached when CacheConfig enables it."""

    def test_get_is_cached_method(self) -> None:
        from zendesk_sdk.config import CacheConfig

        client = ViewsClient(MagicMock(), cache_config=CacheConfig(enabled=True))
        # When caching is enabled, get is wrapped by alru_cache and exposes cache_info.
        assert hasattr(client.get, "cache_info")

    def test_get_not_cached_when_disabled(self) -> None:
        from zendesk_sdk.config import CacheConfig

        client = ViewsClient(MagicMock(), cache_config=CacheConfig(enabled=False))
        assert not hasattr(client.get, "cache_info")

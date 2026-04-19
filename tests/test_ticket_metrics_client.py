"""Tests for TicketMetricsClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zendesk_sdk.clients import TicketMetricsClient
from zendesk_sdk.models import TicketMetrics
from zendesk_sdk.pagination import OffsetPaginator, ZendeskPaginator


class TestTicketMetricsClient:
    """Test cases for TicketMetricsClient."""

    def get_client(self) -> TicketMetricsClient:
        """Create a TicketMetricsClient with a mock HTTP client."""
        return TicketMetricsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        """Get ticket metric by its own id."""
        client = self.get_client()
        payload = {
            "ticket_metric": {
                "id": 999,
                "ticket_id": 42,
                "reply_time_in_minutes": {"calendar": 42, "business": 15},
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.get(999)

            assert isinstance(result, TicketMetrics)
            assert result.id == 999
            assert result.ticket_id == 42
            assert result.reply_time_in_minutes == {"calendar": 42, "business": 15}
            mock_get.assert_called_once_with("ticket_metrics/999.json")

    @pytest.mark.asyncio
    async def test_for_ticket(self) -> None:
        """Get metrics for a specific ticket — primary use case."""
        client = self.get_client()
        payload = {
            "ticket_metric": {
                "id": 1,
                "ticket_id": 42,
                "full_resolution_time_in_minutes": {"calendar": 1440, "business": 480},
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = payload

            result = await client.for_ticket(42)

            assert isinstance(result, TicketMetrics)
            assert result.ticket_id == 42
            assert result.full_resolution_time_in_minutes == {"calendar": 1440, "business": 480}
            mock_get.assert_called_once_with("tickets/42/metrics.json")

    def test_list_returns_paginator(self) -> None:
        """list() returns an OffsetPaginator over TicketMetrics."""
        client = self.get_client()

        paginator = client.list(per_page=50, limit=200)

        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "ticket_metrics.json"
        assert paginator.per_page == 50
        assert paginator.limit == 200

    @pytest.mark.asyncio
    async def test_list_iterates_and_deserializes(self) -> None:
        """Paginator yields TicketMetrics objects from a real API response shape."""
        http_client = AsyncMock()
        http_client.get.return_value = {
            "ticket_metrics": [
                {"id": 1, "ticket_id": 100, "replies": 2},
                {"id": 2, "ticket_id": 101, "replies": 5},
            ],
            "page": 1,
            "per_page": 100,
            "count": 2,
        }

        paginator = ZendeskPaginator.create_ticket_metrics_paginator(http_client)
        items = await paginator.collect()

        assert len(items) == 2
        assert all(isinstance(m, TicketMetrics) for m in items)
        assert items[0].ticket_id == 100
        assert items[1].replies == 5

    @pytest.mark.asyncio
    async def test_list_total_count_from_first_response(self) -> None:
        """count() returns the total from the Zendesk response."""
        http_client = AsyncMock()
        http_client.get.return_value = {"ticket_metrics": [], "page": 1, "per_page": 1, "count": 1337}

        paginator = ZendeskPaginator.create_ticket_metrics_paginator(http_client)
        total = await paginator.count()

        assert total == 1337

    def test_no_cache_configured(self) -> None:
        """Metrics are live — client must not wrap methods with @alru_cache."""
        client = self.get_client()

        # Methods are coroutines, not cached wrappers from async_lru.
        assert not hasattr(client.get, "cache_info")
        assert not hasattr(client.for_ticket, "cache_info")

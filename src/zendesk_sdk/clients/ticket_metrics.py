"""Ticket Metrics API client."""

from typing import TYPE_CHECKING, Optional

from ..models.ticket import TicketMetrics
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class TicketMetricsClient(BaseClient):
    """Client for Zendesk Ticket Metrics API.

    Provides read-only access to per-ticket metrics: first reply time,
    full resolution time, requester/agent wait time, on-hold time, etc.
    All time-based fields expose both calendar and business hours.

    Metrics are live data — they change with every ticket update, so
    responses are not cached.

    Example:
        async with ZendeskClient(config) as client:
            # Metrics for a specific ticket (most common)
            metrics = await client.ticket_metrics.for_ticket(12345)
            print(metrics.reply_time_in_minutes)
            # {"calendar": 42, "business": 15}

            # Metric by its own id
            metrics = await client.ticket_metrics.get(999)

            # Iterate over all metrics
            async for m in client.ticket_metrics.list(per_page=100):
                if m.full_resolution_time_in_minutes:
                    ...
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize TicketMetricsClient.

        No cache: metrics are live data and change with each ticket update.
        """
        super().__init__(http_client)

    async def get(self, metric_id: int) -> TicketMetrics:
        """Get a ticket metric by its own id.

        Args:
            metric_id: The ticket metric id (not the ticket id)

        Returns:
            TicketMetrics object
        """
        response = await self._get(f"ticket_metrics/{metric_id}.json")
        return TicketMetrics(**response["ticket_metric"])

    async def for_ticket(self, ticket_id: int) -> TicketMetrics:
        """Get metrics for a given ticket.

        This is the primary use case — look up metrics for a ticket
        you already have an id for.

        Args:
            ticket_id: The ticket id

        Returns:
            TicketMetrics object
        """
        response = await self._get(f"tickets/{ticket_id}/metrics.json")
        return TicketMetrics(**response["ticket_metric"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[TicketMetrics]":
        """Get paginated list of all ticket metrics.

        Args:
            per_page: Number of metrics per page (max 100)
            limit: Maximum total items when iterating (None = no limit)

        Returns:
            Paginator yielding TicketMetrics objects
        """
        return ZendeskPaginator.create_ticket_metrics_paginator(self._http, per_page=per_page, limit=limit)

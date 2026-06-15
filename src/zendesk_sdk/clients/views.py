"""Views API client (read-only)."""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..models import Ticket, View, ViewCount
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class ViewsClient(BaseClient):
    """Client for Zendesk Views API (read-only).

    Views are saved searches over tickets — the day-to-day workspace
    of an agent. This client lets you list views, fetch a view's tickets,
    and read counts without loading the tickets themselves.

    No write operations are exposed: views are owned by admins and rarely
    edited via API.

    Example:
        async with ZendeskClient(config) as client:
            # List all views
            async for view in client.views.list():
                print(f"{view.title} (active={view.active})")

            # Get a specific view (cached)
            view = await client.views.get(12345)

            # Tickets matching the view's conditions
            async for ticket in client.views.tickets(12345):
                print(ticket.subject)

            # Count tickets without loading them
            count = await client.views.count(12345)
            print(f"{count.value} tickets in view (fresh={count.fresh})")

            # Counts for several views in one request
            counts = await client.views.count_many([1, 2, 3])
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize ViewsClient with optional caching.

        Counts are never cached: they're inherently live data, and
        Zendesk already caches large views server-side.
        """
        super().__init__(http_client, cache_config)
        self.get = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.view_maxsize if cache_config else 200,
            ttl=cache_config.view_ttl if cache_config else 900,
        )

    # ==================== Read Operations ====================

    async def _get_impl(self, view_id: int) -> View:
        """Get a specific view by ID.

        Results are cached based on cache configuration.

        Args:
            view_id: The view's ID

        Returns:
            View object
        """
        response = await self._get(f"views/{view_id}.json")
        return View(**response["view"])

    def list(
        self,
        per_page: int = 100,
        limit: Optional[int] = None,
        active_only: bool = False,
    ) -> "Paginator[View]":
        """Get paginated list of views.

        Args:
            per_page: Number of views per page (max 100)
            limit: Maximum total items to return (None = no limit)
            active_only: If True, returns only active views (uses /views/active)

        Returns:
            Paginator yielding View objects

        Example:
            # All views
            async for view in client.views.list():
                ...

            # Only active views
            async for view in client.views.list(active_only=True):
                ...
        """
        return ZendeskPaginator.create_views_paginator(
            self._http, per_page=per_page, limit=limit, active_only=active_only
        )

    async def get_many(self, view_ids: List[int]) -> Dict[int, View]:
        """Fetch multiple views by IDs in a single request.

        Uses /views/show_many. Max 100 IDs per request.

        Args:
            view_ids: List of view IDs to fetch

        Returns:
            Dictionary mapping view_id -> View

        Example:
            views = await client.views.get_many([1, 2, 3])
            for vid, view in views.items():
                print(view.title)
        """
        if not view_ids:
            return {}

        unique_ids = list(set(view_ids))[:100]
        ids_param = ",".join(str(v) for v in unique_ids)

        response = await self._get(f"views/show_many.json?ids={ids_param}")

        views: Dict[int, View] = {}
        for view_data in response.get("views", []):
            view = View(**view_data)
            if view.id is not None:
                views[view.id] = view
        return views

    def tickets(self, view_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Ticket]":
        """Get paginated list of tickets matching a view's conditions.

        Args:
            view_id: The view's ID
            per_page: Number of tickets per page (max 100)
            limit: Maximum total tickets to return (None = no limit)

        Returns:
            Paginator yielding Ticket objects

        Example:
            async for ticket in client.views.tickets(12345):
                print(f"#{ticket.id}: {ticket.subject}")

            # First 10 tickets
            tickets = await client.views.tickets(12345, limit=10).collect()
        """
        return ZendeskPaginator.create_view_tickets_paginator(self._http, view_id, per_page=per_page, limit=limit)

    async def count(self, view_id: int) -> ViewCount:
        """Get the ticket count for a single view.

        The count may be served from a server-side cache for very large
        views — check `ViewCount.fresh` to see if it's authoritative.

        Args:
            view_id: The view's ID

        Returns:
            ViewCount with value, pretty representation, and freshness flag
        """
        response = await self._get(f"views/{view_id}/count.json")
        return ViewCount(**response["view_count"])

    async def count_many(self, view_ids: List[int]) -> List[ViewCount]:
        """Get ticket counts for multiple views in a single request.

        Useful for dashboards. Max 20 view IDs per request per Zendesk
        documentation.

        Args:
            view_ids: List of view IDs

        Returns:
            List of ViewCount objects (preserves API response order)

        Example:
            counts = await client.views.count_many([1, 2, 3])
            for c in counts:
                print(f"View {c.view_id}: {c.value}")
        """
        if not view_ids:
            return []

        unique_ids = list(set(view_ids))[:20]
        ids_param = ",".join(str(v) for v in unique_ids)

        response = await self._get(f"views/count_many.json?ids={ids_param}")
        return [ViewCount(**c) for c in response.get("view_counts", [])]

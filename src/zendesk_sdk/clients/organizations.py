"""Organizations API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from ..models import Organization
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class OrganizationsClient(BaseClient):
    """Client for Zendesk Organizations API.

    Example:
        async with ZendeskClient(config) as client:
            # Get an organization by ID
            org = await client.organizations.get(12345)

            # List all organizations with pagination
            paginator = await client.organizations.list()
            async for org_data in paginator:
                print(org_data["name"])

            # For search use client.search.organizations()
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize OrganizationsClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], Organization] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.org_maxsize if cache_config else 500,
            ttl=cache_config.org_ttl if cache_config else 600,
        )

    async def _get_impl(self, org_id: int) -> Organization:
        """Get a specific organization by ID.

        Results are cached based on cache configuration.

        Args:
            org_id: The organization's ID

        Returns:
            Organization object
        """
        response = await self._get(f"organizations/{org_id}.json")
        return Organization(**response["organization"])

    async def list(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of organizations.

        Args:
            per_page: Number of organizations per page (max 100)

        Returns:
            Paginator for iterating through all organizations
        """
        return ZendeskPaginator.create_organizations_paginator(self._http, per_page=per_page)

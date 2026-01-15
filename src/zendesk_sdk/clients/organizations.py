"""Organizations API client."""

from typing import TYPE_CHECKING, Callable, Optional

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
            async for org in client.organizations.list():
                print(org.name)

            # Get specific page
            orgs = await client.organizations.list().get_page(2)

            # Collect all organizations to list
            orgs = await client.organizations.list(limit=50).collect()

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

        Retrieves detailed information about a single organization.
        Results are cached based on cache configuration to reduce API calls.

        Args:
            org_id: The unique identifier of the organization to retrieve

        Returns:
            Organization object containing all organization details including
            name, domain names, tags, and custom fields

        Example:
            org = await client.organizations.get(12345)
            print(f"Organization: {org.name}")
            print(f"Domains: {org.domain_names}")
        """
        response = await self._get(f"organizations/{org_id}.json")
        return Organization(**response["organization"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Organization]":
        """Get paginated list of all organizations.

        Returns a paginator that can be used to iterate through all organizations
        in the Zendesk account. The paginator handles cursor-based pagination
        automatically and supports various iteration patterns.

        Args:
            per_page: Number of organizations to fetch per API request (max 100).
                Higher values reduce API calls but increase response size.
            limit: Maximum total number of organizations to return when iterating.
                Use None (default) for no limit. Useful for testing or when you
                only need a subset of organizations.

        Returns:
            Paginator[Organization] that supports:
            - Async iteration: `async for org in client.organizations.list()`
            - Page access: `await client.organizations.list().get_page(2)`
            - Collection: `await client.organizations.list().collect()`

        Example:
            # Iterate through all organizations
            async for org in client.organizations.list():
                print(f"{org.id}: {org.name}")

            # Get first 50 organizations as a list
            orgs = await client.organizations.list(limit=50).collect()

            # Get a specific page
            page_orgs = await client.organizations.list().get_page(1)

            # Process with custom page size
            async for org in client.organizations.list(per_page=25):
                process_organization(org)
        """
        return ZendeskPaginator.create_organizations_paginator(self._http, per_page=per_page, limit=limit)

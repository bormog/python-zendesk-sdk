"""Organizations API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..models import Organization
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class OrganizationsClient(BaseClient):
    """Client for Zendesk Organizations API.

    Provides full CRUD operations for organizations, which group
    end users for shared ticket access and routing.

    Example:
        async with ZendeskClient(config) as client:
            # Get an organization by ID
            org = await client.organizations.get(12345)

            # List all organizations with pagination
            async for org in client.organizations.list():
                print(org.name)

            # Create an organization
            org = await client.organizations.create(
                name="Acme Corp",
                domain_names=["acme.com"],
                tags=["enterprise"]
            )

            # Update an organization
            org = await client.organizations.update(
                12345,
                tags=["enterprise", "vip"]
            )

            # Delete an organization
            await client.organizations.delete(12345)

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
        in the Zendesk account. The paginator handles offset-based pagination
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

    # ==================== Create Operations ====================

    async def create(
        self,
        name: str,
        *,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        external_id: Optional[str] = None,
        domain_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        group_id: Optional[int] = None,
        shared_tickets: Optional[bool] = None,
        shared_comments: Optional[bool] = None,
        organization_fields: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Create a new organization.

        Args:
            name: A unique name for the organization (required)
            details: Any details about the organization, such as the address
            notes: Any notes you have about the organization
            external_id: A unique external id to associate organizations to an external record
            domain_names: Array of domain names associated with this organization
            tags: Tags for the organization
            group_id: New tickets from users in this organization are automatically
                put in this group
            shared_tickets: End users in this organization can see each other's tickets
            shared_comments: End users in this organization can comment on each other's tickets
            organization_fields: Custom organization field values as {field_key: value}

        Returns:
            Created Organization object

        Example:
            # Create minimal organization
            org = await client.organizations.create("Acme Corp")

            # Create with all options
            org = await client.organizations.create(
                name="Acme Corp",
                domain_names=["acme.com", "acme.io"],
                tags=["enterprise"],
                organization_fields={"plan": "premium"},
            )
        """
        org_data: Dict[str, Any] = {"name": name}

        if details is not None:
            org_data["details"] = details
        if notes is not None:
            org_data["notes"] = notes
        if external_id is not None:
            org_data["external_id"] = external_id
        if domain_names is not None:
            org_data["domain_names"] = domain_names
        if tags is not None:
            org_data["tags"] = tags
        if group_id is not None:
            org_data["group_id"] = group_id
        if shared_tickets is not None:
            org_data["shared_tickets"] = shared_tickets
        if shared_comments is not None:
            org_data["shared_comments"] = shared_comments
        if organization_fields is not None:
            org_data["organization_fields"] = organization_fields

        response = await self._post("organizations.json", json={"organization": org_data})
        return Organization(**response["organization"])

    async def create_or_update(
        self,
        name: str,
        *,
        external_id: Optional[str] = None,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        domain_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        group_id: Optional[int] = None,
        shared_tickets: Optional[bool] = None,
        shared_comments: Optional[bool] = None,
        organization_fields: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Create an organization or update if matching external_id exists.

        Uses Zendesk's create_or_update endpoint which matches organizations
        by external_id. If a match is found, the organization is updated.
        If not, a new organization is created.

        Args:
            name: A unique name for the organization (required)
            external_id: External ID used for matching existing organization
            details: Any details about the organization
            notes: Any notes about the organization
            domain_names: Array of domain names
            tags: Tags for the organization
            group_id: Default group for new tickets
            shared_tickets: End users can see each other's tickets
            shared_comments: End users can comment on each other's tickets
            organization_fields: Custom field values as {field_key: value}

        Returns:
            Created or updated Organization object

        Example:
            org = await client.organizations.create_or_update(
                name="Acme Corp",
                external_id="acme-123",
                organization_fields={"plan": "premium"},
            )
        """
        org_data: Dict[str, Any] = {"name": name}

        if external_id is not None:
            org_data["external_id"] = external_id
        if details is not None:
            org_data["details"] = details
        if notes is not None:
            org_data["notes"] = notes
        if domain_names is not None:
            org_data["domain_names"] = domain_names
        if tags is not None:
            org_data["tags"] = tags
        if group_id is not None:
            org_data["group_id"] = group_id
        if shared_tickets is not None:
            org_data["shared_tickets"] = shared_tickets
        if shared_comments is not None:
            org_data["shared_comments"] = shared_comments
        if organization_fields is not None:
            org_data["organization_fields"] = organization_fields

        response = await self._post("organizations/create_or_update.json", json={"organization": org_data})
        return Organization(**response["organization"])

    # ==================== Update Operations ====================

    async def update(
        self,
        org_id: int,
        *,
        name: Optional[str] = None,
        details: Optional[str] = None,
        notes: Optional[str] = None,
        external_id: Optional[str] = None,
        domain_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        group_id: Optional[int] = None,
        shared_tickets: Optional[bool] = None,
        shared_comments: Optional[bool] = None,
        organization_fields: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Update an existing organization.

        All fields are optional - only provided fields will be updated.

        Args:
            org_id: The organization's ID
            name: New name for the organization
            details: New details
            notes: New notes
            external_id: New external ID
            domain_names: New array of domain names (replaces existing)
            tags: New tags (replaces existing)
            group_id: New default group for tickets
            shared_tickets: Change shared tickets setting
            shared_comments: Change shared comments setting
            organization_fields: Update custom field values

        Returns:
            Updated Organization object

        Example:
            # Update tags only
            org = await client.organizations.update(
                12345,
                tags=["enterprise", "vip"]
            )

            # Update multiple fields
            org = await client.organizations.update(
                12345,
                name="Acme Corporation",
                domain_names=["acme.com", "acme.io"],
                organization_fields={"plan": "enterprise"},
            )
        """
        org_data: Dict[str, Any] = {}

        if name is not None:
            org_data["name"] = name
        if details is not None:
            org_data["details"] = details
        if notes is not None:
            org_data["notes"] = notes
        if external_id is not None:
            org_data["external_id"] = external_id
        if domain_names is not None:
            org_data["domain_names"] = domain_names
        if tags is not None:
            org_data["tags"] = tags
        if group_id is not None:
            org_data["group_id"] = group_id
        if shared_tickets is not None:
            org_data["shared_tickets"] = shared_tickets
        if shared_comments is not None:
            org_data["shared_comments"] = shared_comments
        if organization_fields is not None:
            org_data["organization_fields"] = organization_fields

        response = await self._put(f"organizations/{org_id}.json", json={"organization": org_data})
        return Organization(**response["organization"])

    # ==================== Delete Operations ====================

    async def delete(self, org_id: int) -> bool:
        """Delete an organization.

        This permanently deletes the organization. Users associated
        with the organization will be disassociated but not deleted.

        Args:
            org_id: The organization's ID

        Returns:
            True if successful

        Example:
            await client.organizations.delete(12345)
        """
        await self._delete(f"organizations/{org_id}.json")
        return True

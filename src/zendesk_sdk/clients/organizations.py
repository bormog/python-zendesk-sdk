"""Organizations API client."""

from typing import TYPE_CHECKING, Any, Dict, List

from ..models import Organization
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
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

            # Search organizations
            orgs = await client.organizations.search("acme")
    """

    async def get(self, org_id: int) -> Organization:
        """Get a specific organization by ID.

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

    async def search(self, query: str, per_page: int = 100) -> List[Organization]:
        """Search for organizations.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Organization objects
        """
        full_query = f"type:organization {query}"
        response = await self._get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [Organization(**result) for result in results if result.get("result_type") == "organization"]

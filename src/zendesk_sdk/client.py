"""Main Zendesk API client."""

from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, Optional

from .config import ZendeskConfig
from .http_client import HTTPClient

if TYPE_CHECKING:
    from .clients import (
        AttachmentsClient,
        GroupsClient,
        HelpCenterClient,
        OrganizationsClient,
        SearchClient,
        TicketFieldsClient,
        TicketsClient,
        UsersClient,
    )


class ZendeskClient:
    """Main client for interacting with the Zendesk API.

    This client provides a unified interface to all Zendesk API resources
    through namespaced sub-clients.

    Example:
        async with ZendeskClient(config) as client:
            # Users
            user = await client.users.get(12345)

            # Tickets
            ticket = await client.tickets.get(67890)
            await client.tickets.comments.add(67890, "Note", public=False)
            await client.tickets.tags.add(67890, ["vip"])

            # Organizations
            org = await client.organizations.get(111)

            # Search (with pagination and limit)
            async for ticket in client.search.tickets("status:open", limit=10):
                print(ticket.subject)

            # Attachments
            content = await client.attachments.download(url)
            token = await client.attachments.upload(data, "file.pdf")

            # Help Center
            article = await client.help_center.articles.get(222)
            results = await client.help_center.articles.search("password")
    """

    def __init__(self, config: ZendeskConfig) -> None:
        """Initialize the Zendesk client.

        Args:
            config: Zendesk configuration object containing authentication
                   and connection settings.
        """
        self.config = config
        self._http_client: Optional[HTTPClient] = None

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ZendeskClient(subdomain='{self.config.subdomain}')"

    @property
    def http_client(self) -> HTTPClient:
        """Get or create HTTP client instance."""
        if self._http_client is None:
            self._http_client = HTTPClient(self.config)
        return self._http_client

    # ==================== Namespace Properties ====================

    @cached_property
    def users(self) -> "UsersClient":
        """Access Users API.

        Example:
            user = await client.users.get(12345)
            paginator = await client.users.list()
            user = await client.users.by_email("user@example.com")
            # For search use client.search.users()
        """
        from .clients import UsersClient

        return UsersClient(self.http_client, self.config.cache)

    @cached_property
    def organizations(self) -> "OrganizationsClient":
        """Access Organizations API.

        Example:
            org = await client.organizations.get(12345)
            paginator = await client.organizations.list()
            # For search use client.search.organizations()
        """
        from .clients import OrganizationsClient

        return OrganizationsClient(self.http_client, self.config.cache)

    @cached_property
    def groups(self) -> "GroupsClient":
        """Access Groups API.

        Example:
            group = await client.groups.get(12345)
            async for group in client.groups.list():
                print(group.name)

            # Create a new group
            group = await client.groups.create("Support Team", description="Main support")

            # Update a group
            group = await client.groups.update(12345, description="Updated")

            # Delete a group
            await client.groups.delete(12345)

            # Count groups
            count = await client.groups.count()

            # List assignable groups
            async for group in client.groups.list_assignable():
                print(group.name)
        """
        from .clients import GroupsClient

        return GroupsClient(self.http_client, self.config.cache)

    @cached_property
    def tickets(self) -> "TicketsClient":
        """Access Tickets API with nested comments and tags.

        Example:
            # Tickets
            ticket = await client.tickets.get(12345)
            paginator = await client.tickets.list()
            tickets = await client.tickets.for_user(67890)
            tickets = await client.tickets.for_organization(111)

            # Comments (nested)
            comments = await client.tickets.comments.list(12345)
            await client.tickets.comments.add(12345, "Note")
            await client.tickets.comments.make_private(12345, 999)

            # Tags (nested)
            tags = await client.tickets.tags.get(12345)
            await client.tickets.tags.add(12345, ["vip"])
            await client.tickets.tags.set(12345, ["new"])
            await client.tickets.tags.remove(12345, ["old"])

            # Enriched tickets (with comments + users)
            enriched = await client.tickets.get_enriched(12345)
            enriched = await client.tickets.search_enriched("status:open")

            # For search use client.search.tickets()
        """
        from .clients import TicketsClient

        return TicketsClient(self.http_client)

    @cached_property
    def ticket_fields(self) -> "TicketFieldsClient":
        """Access Ticket Fields API.

        Provides access to ticket field definitions, including system
        and custom fields. Essential for understanding ticket schema.

        Example:
            # List all ticket fields
            async for field in client.ticket_fields.list():
                print(f"{field.title}: {field.type}")

            # Get specific field
            field = await client.ticket_fields.get(12345)

            # Get only custom fields
            custom = await client.ticket_fields.list_custom()

            # Get only active fields
            active = await client.ticket_fields.list_active()
        """
        from .clients import TicketFieldsClient

        return TicketFieldsClient(self.http_client, self.config.cache)

    @cached_property
    def attachments(self) -> "AttachmentsClient":
        """Access Attachments API.

        Example:
            # Download
            content = await client.attachments.download(attachment.content_url)

            # Upload
            token = await client.attachments.upload(data, "file.pdf", "application/pdf")
            await client.tickets.comments.add(12345, "See attached", uploads=[token])
        """
        from .clients import AttachmentsClient

        return AttachmentsClient(self.http_client, self.config)

    @cached_property
    def search(self) -> "SearchClient":
        """Access Search API.

        Example:
            paginator = await client.search.all("status:open")
            tickets = await client.search.tickets("priority:high")
            users = await client.search.users("role:admin")
            orgs = await client.search.organizations("acme")
        """
        from .clients import SearchClient

        return SearchClient(self.http_client)

    @cached_property
    def help_center(self) -> "HelpCenterClient":
        """Access Help Center API with nested categories, sections, articles.

        Example:
            # Categories
            cat = await client.help_center.categories.get(123)
            paginator = await client.help_center.categories.list()
            cat = await client.help_center.categories.create(name="Docs")
            await client.help_center.categories.delete(123, force=True)

            # Sections
            sec = await client.help_center.sections.get(456)
            paginator = await client.help_center.sections.for_category(123)
            sec = await client.help_center.sections.create(123, name="Start")

            # Articles
            art = await client.help_center.articles.get(789)
            paginator = await client.help_center.articles.for_section(456)
            results = await client.help_center.articles.search("password")
            art = await client.help_center.articles.create(456, title="Guide")
        """
        from .clients import HelpCenterClient

        return HelpCenterClient(self.http_client, self.config.cache)

    # ==================== Low-level HTTP Methods ====================

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make GET request to Zendesk API.

        Args:
            path: API endpoint path (e.g., 'users.json')
            params: Query parameters
            max_retries: Override default retry count

        Returns:
            JSON response from API
        """
        return await self.http_client.get(path, params=params, max_retries=max_retries)

    async def post(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make POST request to Zendesk API.

        Args:
            path: API endpoint path (e.g., 'users.json')
            json: Request body data
            max_retries: Override default retry count

        Returns:
            JSON response from API
        """
        return await self.http_client.post(path, json=json, max_retries=max_retries)

    async def put(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make PUT request to Zendesk API.

        Args:
            path: API endpoint path (e.g., 'users/123.json')
            json: Request body data
            max_retries: Override default retry count

        Returns:
            JSON response from API
        """
        return await self.http_client.put(path, json=json, max_retries=max_retries)

    async def delete(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request to Zendesk API.

        Args:
            path: API endpoint path (e.g., 'users/123.json')
            json: Optional request body (some endpoints like tags require this)
            max_retries: Override default retry count

        Returns:
            JSON response from API if any, None for empty responses
        """
        return await self.http_client.delete(path, json=json, max_retries=max_retries)

    # ==================== Context Manager ====================

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._http_client:
            await self._http_client.close()

    async def __aenter__(self) -> "ZendeskClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit."""
        await self.close()

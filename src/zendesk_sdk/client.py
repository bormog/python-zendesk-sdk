"""Main Zendesk API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .config import ZendeskConfig
from .http_client import HTTPClient
from .models import Comment, Organization, Ticket, User
from .pagination import ZendeskPaginator

if TYPE_CHECKING:
    from .pagination import Paginator


class ZendeskClient:
    """Main client for interacting with the Zendesk API.

    This client provides a unified interface to all Zendesk API resources
    including users, tickets, organizations, and search functionality.
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
        max_retries: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request to Zendesk API.

        Args:
            path: API endpoint path (e.g., 'users/123.json')
            max_retries: Override default retry count

        Returns:
            JSON response from API if any, None for empty responses
        """
        return await self.http_client.delete(path, max_retries=max_retries)

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

    # Users API methods

    async def get_users(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of users.

        Args:
            per_page: Number of users per page (max 100)

        Returns:
            Paginator for iterating through all users
        """
        paginator = ZendeskPaginator.create_users_paginator(self.http_client, per_page=per_page)
        return paginator

    async def get_user(self, user_id: int) -> User:
        """Get a specific user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User object
        """
        response = await self.get(f"users/{user_id}.json")
        return User(**response["user"])

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Args:
            email: The user's email address

        Returns:
            User object if found, None otherwise
        """
        response = await self.get("users/search.json", params={"query": email})
        users = response.get("users", [])
        if users:
            return User(**users[0])
        return None

    # Organizations API methods

    async def get_organizations(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of organizations.

        Args:
            per_page: Number of organizations per page (max 100)

        Returns:
            Paginator for iterating through all organizations
        """
        paginator = ZendeskPaginator.create_organizations_paginator(self.http_client, per_page=per_page)
        return paginator

    async def get_organization(self, org_id: int) -> Organization:
        """Get a specific organization by ID.

        Args:
            org_id: The organization's ID

        Returns:
            Organization object
        """
        response = await self.get(f"organizations/{org_id}.json")
        return Organization(**response["organization"])

    # Tickets API methods

    async def get_tickets(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of tickets.

        Args:
            per_page: Number of tickets per page (max 100)

        Returns:
            Paginator for iterating through all tickets
        """
        paginator = ZendeskPaginator.create_tickets_paginator(self.http_client, per_page=per_page)
        return paginator

    async def get_ticket(self, ticket_id: int) -> Ticket:
        """Get a specific ticket by ID.

        Args:
            ticket_id: The ticket's ID

        Returns:
            Ticket object
        """
        response = await self.get(f"tickets/{ticket_id}.json")
        return Ticket(**response["ticket"])

    async def get_user_tickets(self, user_id: int, per_page: int = 100) -> List[Ticket]:
        """Get tickets requested by a specific user.

        Args:
            user_id: The user's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of Ticket objects
        """
        response = await self.get(f"users/{user_id}/tickets/requested.json", params={"per_page": per_page})
        return [Ticket(**ticket_data) for ticket_data in response.get("tickets", [])]

    async def get_organization_tickets(self, org_id: int, per_page: int = 100) -> List[Ticket]:
        """Get tickets for a specific organization.

        Args:
            org_id: The organization's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of Ticket objects
        """
        response = await self.get(f"organizations/{org_id}/tickets.json", params={"per_page": per_page})
        return [Ticket(**ticket_data) for ticket_data in response.get("tickets", [])]

    # Comments API methods

    async def get_ticket_comments(self, ticket_id: int, per_page: int = 100) -> List[Comment]:
        """Get comments for a specific ticket.

        Args:
            ticket_id: The ticket's ID
            per_page: Number of comments per page (max 100)

        Returns:
            List of Comment objects
        """
        response = await self.get(f"tickets/{ticket_id}/comments.json", params={"per_page": per_page})
        return [Comment(**comment_data) for comment_data in response.get("comments", [])]

    # Search API methods

    async def search(self, query: str, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Search across all Zendesk resources.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            Paginator for iterating through search results
        """
        paginator = ZendeskPaginator.create_search_paginator(self.http_client, query=query, per_page=per_page)
        return paginator

    async def search_users(self, query: str, per_page: int = 100) -> List[User]:
        """Search for users.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of User objects
        """
        full_query = f"type:user {query}"
        response = await self.get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [User(**result) for result in results if result.get("result_type") == "user"]

    async def search_tickets(self, query: str, per_page: int = 100) -> List[Ticket]:
        """Search for tickets.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Ticket objects
        """
        full_query = f"type:ticket {query}"
        response = await self.get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [Ticket(**result) for result in results if result.get("result_type") == "ticket"]

    async def search_organizations(self, query: str, per_page: int = 100) -> List[Organization]:
        """Search for organizations.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of Organization objects
        """
        full_query = f"type:organization {query}"
        response = await self.get("search.json", params={"query": full_query, "per_page": per_page})
        results = response.get("results", [])
        return [Organization(**result) for result in results if result.get("result_type") == "organization"]

"""Main Zendesk API client."""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import httpx

from .config import ZendeskConfig
from .http_client import HTTPClient
from .models import Comment, EnrichedTicket, Organization, Ticket, User
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

    async def add_ticket_comment(
        self,
        ticket_id: int,
        body: str,
        *,
        public: bool = False,
        author_id: Optional[int] = None,
        uploads: Optional[List[str]] = None,
    ) -> Ticket:
        """Add a comment to a ticket.

        This is the primary way to add comments in Zendesk. Comments are added
        by updating the ticket with a comment object.

        Note: Zendesk does not support editing or deleting comments after creation.
        Use make_comment_private() or redact_comment_string() instead.

        Args:
            ticket_id: The ticket's ID
            body: The comment text (plain text or HTML)
            public: If True, comment is visible to end users.
                   If False, it's an internal note (default: False)
            author_id: The user ID to show as the comment author.
                      Defaults to the authenticated user.
            uploads: List of upload tokens from upload_attachment() to attach files

        Returns:
            Updated Ticket object

        Example:
            # Add an internal note (default)
            ticket = await client.add_ticket_comment(12345, "Internal: Customer is VIP")

            # Add a public comment visible to customer
            ticket = await client.add_ticket_comment(
                12345,
                "Thanks for contacting us!",
                public=True
            )

            # Add a comment with attachment
            token = await client.upload_attachment(data, "file.pdf", "application/pdf")
            ticket = await client.add_ticket_comment(
                12345,
                "Please see the attached document.",
                uploads=[token]
            )
        """
        comment_data: Dict[str, Any] = {
            "body": body,
            "public": public,
        }
        if author_id is not None:
            comment_data["author_id"] = author_id
        if uploads:
            comment_data["uploads"] = uploads

        payload = {"ticket": {"comment": comment_data}}
        response = await self.put(f"tickets/{ticket_id}.json", json=payload)
        return Ticket(**response["ticket"])

    async def make_comment_private(self, ticket_id: int, comment_id: int) -> bool:
        """Make a public comment private (convert to internal note).

        This action is irreversible - once a comment is made private,
        it cannot be made public again.

        Args:
            ticket_id: The ticket's ID
            comment_id: The comment's ID

        Returns:
            True if successful

        Raises:
            ZendeskHTTPException: If the operation fails (e.g., comment already private)

        Example:
            await client.make_comment_private(12345, 67890)
        """
        await self.put(f"tickets/{ticket_id}/comments/{comment_id}/make_private.json")
        return True

    async def redact_comment_string(
        self,
        ticket_id: int,
        comment_id: int,
        text: str,
    ) -> Comment:
        """Permanently redact (remove) a string from a comment.

        This permanently removes the specified text from the comment body.
        The text is replaced with a placeholder like "▇▇▇▇".

        This is useful for removing sensitive information like:
        - Credit card numbers
        - Social security numbers
        - Passwords or API keys
        - Personal information

        Warning: This action is PERMANENT and cannot be undone.

        Args:
            ticket_id: The ticket's ID
            comment_id: The comment's ID
            text: The exact text string to redact from the comment

        Returns:
            Updated Comment object

        Raises:
            ZendeskHTTPException: If the text is not found or operation fails

        Example:
            # Redact a credit card number from a comment
            await client.redact_comment_string(
                ticket_id=12345,
                comment_id=67890,
                text="4111-1111-1111-1111"
            )
        """
        payload = {"text": text}
        response = await self.put(
            f"tickets/{ticket_id}/comments/{comment_id}/redact.json",
            json=payload,
        )
        return Comment(**response["comment"])

    # Tags API methods

    async def get_ticket_tags(self, ticket_id: int) -> List[str]:
        """Get all tags for a ticket.

        Args:
            ticket_id: The ticket's ID

        Returns:
            List of tag strings

        Example:
            tags = await client.get_ticket_tags(12345)
            # ["vip", "urgent", "billing"]
        """
        response = await self.get(f"tickets/{ticket_id}/tags.json")
        return response.get("tags", [])

    async def add_ticket_tags(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Add tags to a ticket without removing existing tags.

        This appends the specified tags to the ticket's existing tags.
        Duplicate tags are automatically ignored.

        Note: Cannot be used on closed tickets. Use set_ticket_tags() via
        ticket update for closed tickets.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to add

        Returns:
            Updated list of all tags on the ticket

        Example:
            # Existing tags: ["billing"]
            tags = await client.add_ticket_tags(12345, ["vip", "urgent"])
            # Result: ["billing", "vip", "urgent"]
        """
        response = await self.put(f"tickets/{ticket_id}/tags.json", json={"tags": tags})
        return response.get("tags", [])

    async def set_ticket_tags(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Replace all tags on a ticket with a new set.

        This completely replaces the ticket's tags with the specified list.
        All existing tags are removed.

        Note: Cannot be used on closed tickets.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to set (replaces all existing)

        Returns:
            Updated list of tags on the ticket

        Example:
            # Existing tags: ["old1", "old2"]
            tags = await client.set_ticket_tags(12345, ["new1", "new2"])
            # Result: ["new1", "new2"]
        """
        response = await self.post(f"tickets/{ticket_id}/tags.json", json={"tags": tags})
        return response.get("tags", [])

    async def remove_ticket_tags(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Remove specific tags from a ticket.

        Only the specified tags are removed. Other tags remain unchanged.

        Note: Cannot be used on closed tickets.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to remove

        Returns:
            Updated list of remaining tags on the ticket

        Example:
            # Existing tags: ["vip", "urgent", "billing"]
            tags = await client.remove_ticket_tags(12345, ["urgent"])
            # Result: ["vip", "billing"]
        """
        # Zendesk DELETE with body requires special handling
        response = await self.http_client.delete(
            f"tickets/{ticket_id}/tags.json",
            json={"tags": tags},
        )
        return response.get("tags", []) if response else []

    # Attachments API methods

    async def download_attachment(self, content_url: str) -> bytes:
        """Download attachment content from Zendesk.

        Zendesk attachment URLs require following redirects to access
        the actual file content.

        Args:
            content_url: The content_url from a CommentAttachment object

        Returns:
            Raw bytes of the attachment content

        Example:
            comments = await client.get_ticket_comments(12345)
            for comment in comments:
                for attachment in comment.attachments or []:
                    content = await client.download_attachment(attachment.content_url)
                    with open(attachment.file_name, "wb") as f:
                        f.write(content)
        """
        # Attachment URLs redirect to the actual file, so we need to follow redirects
        async with httpx.AsyncClient(follow_redirects=True) as http:
            response = await http.get(content_url)
            response.raise_for_status()
            return response.content

    async def upload_attachment(
        self,
        data: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file attachment to Zendesk.

        This uploads a file and returns a token that can be used when
        creating a ticket comment with attachments.

        Note: The token is valid for 60 minutes.

        Args:
            data: Raw bytes of the file content
            filename: Name for the uploaded file (include extension)
            content_type: MIME type of the file (default: application/octet-stream)

        Returns:
            Upload token to use with add_ticket_comment's uploads parameter

        Example:
            # Upload a file
            with open("screenshot.png", "rb") as f:
                token = await client.upload_attachment(
                    f.read(),
                    "screenshot.png",
                    "image/png"
                )

            # Attach to a comment
            await client.add_ticket_comment(
                ticket_id=12345,
                body="See attached screenshot",
                uploads=[token]
            )
        """
        # Zendesk upload requires raw binary data with Content-Type header
        url = f"{self.config.endpoint}/uploads.json"
        params = {"filename": filename}
        headers = {
            "Content-Type": content_type,
        }

        # Use authenticated request
        auth = httpx.BasicAuth(
            username=self.config.auth_tuple[0],
            password=self.config.auth_tuple[1],
        )

        async with httpx.AsyncClient(auth=auth) as http:
            response = await http.post(url, params=params, headers=headers, content=data)
            response.raise_for_status()
            result = response.json()
            return result["upload"]["token"]

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

    # EnrichedTicket API methods - tickets with all related data

    def _extract_users_from_response(self, response: Dict[str, Any]) -> Dict[int, User]:
        """Extract sideloaded users from API response.

        Args:
            response: API response containing 'users' array

        Returns:
            Dictionary mapping user_id to User object
        """
        users: Dict[int, User] = {}
        for user_data in response.get("users", []):
            user = User(**user_data)
            if user.id is not None:
                users[user.id] = user
        return users

    def _collect_user_ids_from_tickets(self, tickets: List[Ticket]) -> List[int]:
        """Collect all user IDs from a list of tickets.

        Args:
            tickets: List of Ticket objects

        Returns:
            List of unique user IDs
        """
        user_ids: set[int] = set()
        for ticket in tickets:
            if ticket.requester_id:
                user_ids.add(ticket.requester_id)
            if ticket.assignee_id:
                user_ids.add(ticket.assignee_id)
            if ticket.submitter_id:
                user_ids.add(ticket.submitter_id)
            if ticket.collaborator_ids:
                user_ids.update(ticket.collaborator_ids)
            if ticket.follower_ids:
                user_ids.update(ticket.follower_ids)
        return list(user_ids)

    async def _fetch_users_batch(self, user_ids: List[int]) -> Dict[int, User]:
        """Fetch multiple users by IDs using show_many endpoint.

        Args:
            user_ids: List of user IDs to fetch

        Returns:
            Dictionary mapping user_id to User object
        """
        if not user_ids:
            return {}

        # Zendesk show_many supports up to 100 IDs
        unique_ids = list(set(user_ids))[:100]
        ids_param = ",".join(str(uid) for uid in unique_ids)

        response = await self.get(f"users/show_many.json?ids={ids_param}")
        return self._extract_users_from_response(response)

    async def _fetch_comments_with_users(self, ticket_id: int) -> tuple[List[Comment], Dict[int, User]]:
        """Fetch comments for a ticket with sideloaded users.

        Args:
            ticket_id: Ticket ID

        Returns:
            Tuple of (comments list, users dict)
        """
        response = await self.get(f"tickets/{ticket_id}/comments.json", params={"include": "users"})
        comments = [Comment(**c) for c in response.get("comments", [])]
        users = self._extract_users_from_response(response)
        return comments, users

    async def _build_enriched_ticket(self, ticket: Ticket, ticket_users: Dict[int, User]) -> EnrichedTicket:
        """Build EnrichedTicket by fetching comments and merging users.

        Args:
            ticket: Ticket object
            ticket_users: Users already loaded with ticket (from sideloading)

        Returns:
            EnrichedTicket object with all data
        """
        if ticket.id is None:
            raise ValueError("Ticket must have an ID to fetch full data")
        comments, comment_users = await self._fetch_comments_with_users(ticket.id)

        # Merge all users
        all_users = {**ticket_users, **comment_users}

        return EnrichedTicket(ticket=ticket, comments=comments, users=all_users)

    async def _build_enriched_tickets(
        self, tickets: List[Ticket], ticket_users: Dict[int, User]
    ) -> List[EnrichedTicket]:
        """Build list of EnrichedTicket by fetching comments in parallel.

        Args:
            tickets: List of Ticket objects
            ticket_users: Users already loaded with tickets (from sideloading)

        Returns:
            List of EnrichedTicket objects
        """
        if not tickets:
            return []

        # Filter tickets with valid IDs
        valid_tickets = [t for t in tickets if t.id is not None]
        if not valid_tickets:
            return []

        # Fetch comments for all tickets in parallel
        comment_tasks = [self._fetch_comments_with_users(t.id) for t in valid_tickets]  # type: ignore[arg-type]
        results = await asyncio.gather(*comment_tasks)

        # Build EnrichedTicket for each ticket with only its users
        enriched_tickets: List[EnrichedTicket] = []
        for ticket, (comments, comment_users) in zip(valid_tickets, results):
            # Collect user IDs for this specific ticket
            ticket_user_ids: set[int] = set()
            if ticket.requester_id:
                ticket_user_ids.add(ticket.requester_id)
            if ticket.assignee_id:
                ticket_user_ids.add(ticket.assignee_id)
            if ticket.submitter_id:
                ticket_user_ids.add(ticket.submitter_id)
            if ticket.collaborator_ids:
                ticket_user_ids.update(ticket.collaborator_ids)
            if ticket.follower_ids:
                ticket_user_ids.update(ticket.follower_ids)

            # Filter ticket_users to only include users for this ticket
            this_ticket_users = {uid: user for uid, user in ticket_users.items() if uid in ticket_user_ids}

            # Merge with comment users
            all_users = {**this_ticket_users, **comment_users}
            enriched_tickets.append(EnrichedTicket(ticket=ticket, comments=comments, users=all_users))

        return enriched_tickets

    async def get_enriched_ticket(self, ticket_id: int) -> EnrichedTicket:
        """Get a ticket with all related data: comments and users.

        This method fetches the ticket with sideloaded users,
        then fetches comments with their authors in a single additional request.

        Args:
            ticket_id: The ticket's ID

        Returns:
            EnrichedTicket object containing ticket, comments, and all related users
        """
        # Fetch ticket with sideloaded users
        response = await self.get(f"tickets/{ticket_id}.json", params={"include": "users"})
        ticket = Ticket(**response["ticket"])
        ticket_users = self._extract_users_from_response(response)

        return await self._build_enriched_ticket(ticket, ticket_users)

    async def search_enriched_tickets(self, query: str, per_page: int = 100) -> List[EnrichedTicket]:
        """Search for tickets and load all related data.

        This method searches for tickets, then fetches users and comments in parallel.
        Note: Zendesk Search API does not support sideloading, so users are fetched separately.

        Args:
            query: Search query string
            per_page: Number of results per page (max 100)

        Returns:
            List of EnrichedTicket objects
        """
        full_query = f"type:ticket {query}"
        response = await self.get("search.json", params={"query": full_query, "per_page": per_page})

        results = response.get("results", [])
        tickets = [Ticket(**r) for r in results if r.get("result_type") == "ticket"]

        if not tickets:
            return []

        # Fetch users from tickets via show_many (search API doesn't support sideloading)
        user_ids = self._collect_user_ids_from_tickets(tickets)
        ticket_users = await self._fetch_users_batch(user_ids)

        return await self._build_enriched_tickets(tickets, ticket_users)

    async def get_organization_enriched_tickets(self, org_id: int, per_page: int = 100) -> List[EnrichedTicket]:
        """Get tickets for an organization with all related data.

        This method fetches organization tickets with sideloaded users,
        then fetches comments for all tickets in parallel.

        Args:
            org_id: The organization's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of EnrichedTicket objects
        """
        response = await self.get(
            f"organizations/{org_id}/tickets.json", params={"per_page": per_page, "include": "users"}
        )

        tickets = [Ticket(**t) for t in response.get("tickets", [])]
        ticket_users = self._extract_users_from_response(response)

        return await self._build_enriched_tickets(tickets, ticket_users)

    async def get_user_enriched_tickets(self, user_id: int, per_page: int = 100) -> List[EnrichedTicket]:
        """Get tickets requested by a user with all related data.

        This method fetches user's tickets with sideloaded users,
        then fetches comments for all tickets in parallel.

        Args:
            user_id: The user's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of EnrichedTicket objects
        """
        response = await self.get(
            f"users/{user_id}/tickets/requested.json", params={"per_page": per_page, "include": "users"}
        )

        tickets = [Ticket(**t) for t in response.get("tickets", [])]
        ticket_users = self._extract_users_from_response(response)

        return await self._build_enriched_tickets(tickets, ticket_users)

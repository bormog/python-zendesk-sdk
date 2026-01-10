"""Tickets API client with nested Comments and Tags."""

import asyncio
from functools import cached_property
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Union

from ..models import Comment, EnrichedTicket, Ticket, TicketField, User
from ..models.search import (
    SearchQueryConfig,
    SearchType,
    TicketPriorityInput,
    TicketStatusInput,
    TicketTypeInput,
)
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import OffsetPaginator, Paginator


class CommentsClient(BaseClient):
    """Client for Ticket Comments API.

    Example:
        async with ZendeskClient(config) as client:
            # Iterate through comments
            async for comment in client.tickets.comments.list(12345):
                print(comment.body)

            # Add a private note
            await client.tickets.comments.add(12345, "Internal note")

            # Add a public reply
            await client.tickets.comments.add(12345, "Hello!", public=True)
    """

    def list(self, ticket_id: int, per_page: int = 100, limit: Optional[int] = None) -> "OffsetPaginator[Comment]":
        """Get comments for a specific ticket with pagination.

        Args:
            ticket_id: The ticket's ID
            per_page: Number of comments per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through comments
        """
        return ZendeskPaginator.create_ticket_comments_paginator(self._http, ticket_id, per_page=per_page, limit=limit)

    async def add(
        self,
        ticket_id: int,
        body: str,
        *,
        public: bool = False,
        author_id: Optional[int] = None,
        uploads: Optional[List[str]] = None,
    ) -> Ticket:
        """Add a comment to a ticket.

        Args:
            ticket_id: The ticket's ID
            body: The comment text (plain text or HTML)
            public: If True, comment is visible to end users.
                   If False, it's an internal note (default: False)
            author_id: The user ID to show as the comment author.
                      Defaults to the authenticated user.
            uploads: List of upload tokens from attachments.upload() to attach files

        Returns:
            Updated Ticket object

        Example:
            # Add an internal note (default)
            ticket = await client.tickets.comments.add(12345, "Internal: VIP customer")

            # Add a public comment visible to customer
            ticket = await client.tickets.comments.add(
                12345,
                "Thanks for contacting us!",
                public=True
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
        response = await self._put(f"tickets/{ticket_id}.json", json=payload)
        return Ticket(**response["ticket"])

    async def make_private(self, ticket_id: int, comment_id: int) -> bool:
        """Make a public comment private (convert to internal note).

        This action is irreversible.

        Args:
            ticket_id: The ticket's ID
            comment_id: The comment's ID

        Returns:
            True if successful
        """
        await self._put(f"tickets/{ticket_id}/comments/{comment_id}/make_private.json")
        return True

    async def redact(self, ticket_id: int, comment_id: int, text: str) -> Comment:
        """Permanently redact (remove) a string from a comment.

        Warning: This action is PERMANENT and cannot be undone.

        Args:
            ticket_id: The ticket's ID
            comment_id: The comment's ID
            text: The exact text string to redact from the comment

        Returns:
            Updated Comment object
        """
        response = await self._put(
            f"tickets/{ticket_id}/comments/{comment_id}/redact.json",
            json={"text": text},
        )
        return Comment(**response["comment"])


class TagsClient(BaseClient):
    """Client for Ticket Tags API.

    Example:
        async with ZendeskClient(config) as client:
            # Get tags
            tags = await client.tickets.tags.get(12345)

            # Add tags
            await client.tickets.tags.add(12345, ["vip", "urgent"])

            # Replace all tags
            await client.tickets.tags.set(12345, ["new-tag"])

            # Remove specific tags
            await client.tickets.tags.remove(12345, ["old-tag"])
    """

    async def get(self, ticket_id: int) -> List[str]:
        """Get all tags for a ticket.

        Args:
            ticket_id: The ticket's ID

        Returns:
            List of tag strings
        """
        response = await self._get(f"tickets/{ticket_id}/tags.json")
        return response.get("tags", [])

    async def add(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Add tags to a ticket without removing existing tags.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to add

        Returns:
            Updated list of all tags on the ticket
        """
        response = await self._put(f"tickets/{ticket_id}/tags.json", json={"tags": tags})
        return response.get("tags", [])

    async def set(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Replace all tags on a ticket with a new set.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to set (replaces all existing)

        Returns:
            Updated list of tags on the ticket
        """
        response = await self._post(f"tickets/{ticket_id}/tags.json", json={"tags": tags})
        return response.get("tags", [])

    async def remove(self, ticket_id: int, tags: List[str]) -> List[str]:
        """Remove specific tags from a ticket.

        Args:
            ticket_id: The ticket's ID
            tags: List of tags to remove

        Returns:
            Updated list of remaining tags on the ticket
        """
        response = await self._delete(f"tickets/{ticket_id}/tags.json", json={"tags": tags})
        return response.get("tags", []) if response else []


class TicketsClient(BaseClient):
    """Client for Zendesk Tickets API.

    Provides full CRUD operations for tickets, plus access to comments and tags
    through a namespace pattern.

    Example:
        async with ZendeskClient(config) as client:
            # Create a ticket
            ticket = await client.tickets.create(
                comment_body="Customer needs help with login",
                subject="Login Issue",
                priority="high",
                tags=["login", "urgent"]
            )

            # Get a ticket
            ticket = await client.tickets.get(12345)

            # Update a ticket
            ticket = await client.tickets.update(
                12345,
                status="solved",
                comment={"body": "Issue resolved!", "public": True}
            )

            # Delete a ticket
            await client.tickets.delete(12345)

            # List all tickets (returns paginator)
            async for ticket in client.tickets.list():
                print(ticket.subject)

            # Get tickets for a user
            async for ticket in client.tickets.for_user(67890):
                print(ticket.subject)

            # Access nested resources
            async for comment in client.tickets.comments.list(12345):
                print(comment.body)
            tags = await client.tickets.tags.get(12345)

            # Get enriched ticket with all data
            enriched = await client.tickets.get_enriched(12345)
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize tickets client."""
        super().__init__(http_client)

    @cached_property
    def comments(self) -> CommentsClient:
        """Access ticket comments API."""
        return CommentsClient(self._http)

    @cached_property
    def tags(self) -> TagsClient:
        """Access ticket tags API."""
        return TagsClient(self._http)

    async def get(self, ticket_id: int) -> Ticket:
        """Get a specific ticket by ID.

        Args:
            ticket_id: The ticket's ID

        Returns:
            Ticket object
        """
        response = await self._get(f"tickets/{ticket_id}.json")
        return Ticket(**response["ticket"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Ticket]":
        """Get paginated list of tickets.

        Args:
            per_page: Number of tickets per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all tickets
        """
        return ZendeskPaginator.create_tickets_paginator(self._http, per_page=per_page, limit=limit)

    def for_user(self, user_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Ticket]":
        """Get paginated tickets requested by a specific user.

        Args:
            user_id: The user's ID
            per_page: Number of tickets per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through user's tickets
        """
        return ZendeskPaginator.create_user_tickets_paginator(self._http, user_id, per_page=per_page, limit=limit)

    def for_organization(self, org_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Ticket]":
        """Get paginated tickets for a specific organization.

        Args:
            org_id: The organization's ID
            per_page: Number of tickets per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through organization's tickets
        """
        return ZendeskPaginator.create_organization_tickets_paginator(
            self._http, org_id, per_page=per_page, limit=limit
        )

    # ==================== CRUD Operations ====================

    async def create(
        self,
        comment_body: str,
        *,
        subject: Optional[str] = None,
        priority: Optional[TicketPriorityInput] = None,
        status: Optional[TicketStatusInput] = None,
        ticket_type: Optional[TicketTypeInput] = None,
        assignee_id: Optional[int] = None,
        group_id: Optional[int] = None,
        requester_id: Optional[int] = None,
        submitter_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        collaborator_ids: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[List[Dict[str, Any]]] = None,
        external_id: Optional[str] = None,
        public: bool = True,
        uploads: Optional[List[str]] = None,
    ) -> Ticket:
        """Create a new ticket.

        The only required field is comment_body which becomes the initial
        comment/description of the ticket.

        Args:
            comment_body: The initial comment text (required)
            subject: Ticket subject/title
            priority: Priority level - one of: "low", "normal", "high", "urgent"
            status: Initial status - one of: "new", "open", "pending", "hold", "solved", "closed"
            ticket_type: Ticket type - one of: "question", "incident", "problem", "task"
            assignee_id: Agent ID to assign the ticket to
            group_id: Group ID to assign the ticket to
            requester_id: User ID of the requester (defaults to authenticated user)
            submitter_id: User ID of the submitter (defaults to authenticated user)
            organization_id: Organization ID for the ticket
            collaborator_ids: List of user IDs to CC on the ticket
            tags: List of tags to apply
            custom_fields: List of custom field dicts with 'id' and 'value' keys
            external_id: External ID for linking to local records
            public: If True (default), comment is visible to end users.
                   If False, it's an internal note.
            uploads: List of upload tokens from attachments.upload() to attach files

        Returns:
            Created Ticket object

        Example:
            # Minimal creation
            ticket = await client.tickets.create(
                comment_body="My printer is not working"
            )

            # Full creation
            ticket = await client.tickets.create(
                comment_body="Customer cannot log in to their account",
                subject="Login Issue",
                priority="high",
                assignee_id=12345,
                tags=["login", "urgent"],
                custom_fields=[{"id": 360001234, "value": "bug"}]
            )
        """
        ticket_data: Dict[str, Any] = {
            "comment": {
                "body": comment_body,
                "public": public,
            }
        }

        if uploads:
            ticket_data["comment"]["uploads"] = uploads

        if subject is not None:
            ticket_data["subject"] = subject
        if priority is not None:
            ticket_data["priority"] = priority
        if status is not None:
            ticket_data["status"] = status
        if ticket_type is not None:
            ticket_data["type"] = ticket_type
        if assignee_id is not None:
            ticket_data["assignee_id"] = assignee_id
        if group_id is not None:
            ticket_data["group_id"] = group_id
        if requester_id is not None:
            ticket_data["requester_id"] = requester_id
        if submitter_id is not None:
            ticket_data["submitter_id"] = submitter_id
        if organization_id is not None:
            ticket_data["organization_id"] = organization_id
        if collaborator_ids is not None:
            ticket_data["collaborator_ids"] = collaborator_ids
        if tags is not None:
            ticket_data["tags"] = tags
        if custom_fields is not None:
            ticket_data["custom_fields"] = custom_fields
        if external_id is not None:
            ticket_data["external_id"] = external_id

        response = await self._post("tickets.json", json={"ticket": ticket_data})
        return Ticket(**response["ticket"])

    async def update(
        self,
        ticket_id: int,
        *,
        subject: Optional[str] = None,
        priority: Optional[TicketPriorityInput] = None,
        status: Optional[TicketStatusInput] = None,
        ticket_type: Optional[TicketTypeInput] = None,
        assignee_id: Optional[int] = None,
        group_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        collaborator_ids: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[List[Dict[str, Any]]] = None,
        external_id: Optional[str] = None,
        comment: Optional[Dict[str, Any]] = None,
    ) -> Ticket:
        """Update an existing ticket.

        All fields are optional - only provided fields will be updated.
        To add a comment during update, use the comment parameter with
        a dict containing 'body' and optionally 'public' keys.

        Args:
            ticket_id: The ticket's ID
            subject: New ticket subject/title
            priority: New priority level - one of: "low", "normal", "high", "urgent"
            status: New status - one of: "new", "open", "pending", "hold", "solved", "closed"
            ticket_type: New ticket type - one of: "question", "incident", "problem", "task"
            assignee_id: Reassign to different agent
            group_id: Reassign to different group
            organization_id: Change organization
            collaborator_ids: Update list of CC'd users
            tags: Replace all tags (for add/remove use tickets.tags client)
            custom_fields: Update custom field values
            external_id: Update external ID
            comment: Add a comment with dict containing:
                - body (str): Comment text (required)
                - public (bool): Visible to end users (default: False)
                - author_id (int): Override comment author
                - uploads (List[str]): Attachment upload tokens

        Returns:
            Updated Ticket object

        Example:
            # Update status
            ticket = await client.tickets.update(12345, status="solved")

            # Update with internal note
            ticket = await client.tickets.update(
                12345,
                status="pending",
                comment={"body": "Waiting for customer response", "public": False}
            )

            # Update with public reply
            ticket = await client.tickets.update(
                12345,
                status="solved",
                comment={"body": "Issue has been resolved!", "public": True}
            )
        """
        ticket_data: Dict[str, Any] = {}

        if subject is not None:
            ticket_data["subject"] = subject
        if priority is not None:
            ticket_data["priority"] = priority
        if status is not None:
            ticket_data["status"] = status
        if ticket_type is not None:
            ticket_data["type"] = ticket_type
        if assignee_id is not None:
            ticket_data["assignee_id"] = assignee_id
        if group_id is not None:
            ticket_data["group_id"] = group_id
        if organization_id is not None:
            ticket_data["organization_id"] = organization_id
        if collaborator_ids is not None:
            ticket_data["collaborator_ids"] = collaborator_ids
        if tags is not None:
            ticket_data["tags"] = tags
        if custom_fields is not None:
            ticket_data["custom_fields"] = custom_fields
        if external_id is not None:
            ticket_data["external_id"] = external_id
        if comment is not None:
            ticket_data["comment"] = comment

        response = await self._put(f"tickets/{ticket_id}.json", json={"ticket": ticket_data})
        return Ticket(**response["ticket"])

    async def delete(self, ticket_id: int) -> bool:
        """Delete a ticket.

        Note: Deleted tickets are moved to the trash and can be recovered
        within 30 days via the Zendesk admin UI.

        Args:
            ticket_id: The ticket's ID

        Returns:
            True if successful

        Example:
            success = await client.tickets.delete(12345)
        """
        await self._delete(f"tickets/{ticket_id}.json")
        return True

    def _resolve_query(self, query: Union[str, SearchQueryConfig]) -> str:
        """Convert query input to Zendesk query string."""
        if isinstance(query, SearchQueryConfig):
            if query.type != SearchType.TICKET:
                query = query.model_copy(update={"type": SearchType.TICKET})
            return query.to_query()
        return f"type:ticket {query}"

    # ==================== Enriched Ticket Methods ====================

    def _extract_users_from_response(self, response: Dict[str, Any]) -> Dict[int, User]:
        """Extract sideloaded users from API response."""
        users: Dict[int, User] = {}
        for user_data in response.get("users", []):
            user = User(**user_data)
            if user.id is not None:
                users[user.id] = user
        return users

    def _collect_user_ids_from_tickets(self, tickets: List[Ticket]) -> List[int]:
        """Collect all user IDs from a list of tickets."""
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
        """Fetch multiple users by IDs using show_many endpoint."""
        if not user_ids:
            return {}

        unique_ids = list(set(user_ids))[:100]
        ids_param = ",".join(str(uid) for uid in unique_ids)

        response = await self._get(f"users/show_many.json?ids={ids_param}")
        return self._extract_users_from_response(response)

    async def _fetch_comments_with_users(self, ticket_id: int) -> tuple[List[Comment], Dict[int, User]]:
        """Fetch comments for a ticket with sideloaded users."""
        response = await self._get(f"tickets/{ticket_id}/comments.json", params={"include": "users"})
        comments = [Comment(**c) for c in response.get("comments", [])]
        users = self._extract_users_from_response(response)
        return comments, users

    async def _fetch_fields(self) -> Dict[int, TicketField]:
        """Fetch all ticket field definitions using paginator."""
        paginator = ZendeskPaginator.create_ticket_fields_paginator(self._http)
        fields: Dict[int, TicketField] = {}
        async for field in paginator:
            if field.id is not None:
                fields[field.id] = field
        return fields

    async def _build_enriched_ticket(
        self,
        ticket: Ticket,
        ticket_users: Dict[int, User],
        fields: Optional[Dict[int, TicketField]] = None,
    ) -> EnrichedTicket:
        """Build EnrichedTicket by fetching comments and merging users."""
        if ticket.id is None:
            raise ValueError("Ticket must have an ID to fetch full data")
        comments, comment_users = await self._fetch_comments_with_users(ticket.id)
        all_users = {**ticket_users, **comment_users}
        return EnrichedTicket(
            ticket=ticket,
            comments=comments,
            users=all_users,
            fields=fields or {},
        )

    async def _build_enriched_tickets(
        self,
        tickets: List[Ticket],
        ticket_users: Dict[int, User],
        fields: Optional[Dict[int, TicketField]] = None,
    ) -> List[EnrichedTicket]:
        """Build list of EnrichedTicket by fetching comments in parallel."""
        if not tickets:
            return []

        valid_tickets = [t for t in tickets if t.id is not None]
        if not valid_tickets:
            return []

        comment_tasks = [self._fetch_comments_with_users(t.id) for t in valid_tickets]  # type: ignore[arg-type]
        results = await asyncio.gather(*comment_tasks)

        enriched_tickets: List[EnrichedTicket] = []
        for ticket, (comments, comment_users) in zip(valid_tickets, results):
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

            this_ticket_users = {uid: user for uid, user in ticket_users.items() if uid in ticket_user_ids}
            all_users = {**this_ticket_users, **comment_users}
            enriched_tickets.append(EnrichedTicket(
                ticket=ticket,
                comments=comments,
                users=all_users,
                fields=fields or {},
            ))

        return enriched_tickets

    async def get_enriched(self, ticket_id: int) -> EnrichedTicket:
        """Get a ticket with all related data: comments, users, and field definitions.

        Args:
            ticket_id: The ticket's ID

        Returns:
            EnrichedTicket object containing ticket, comments, users, and field definitions
        """
        # Fetch ticket with users and fields in parallel
        ticket_task = self._get(f"tickets/{ticket_id}.json", params={"include": "users"})
        fields_task = self._fetch_fields()
        response, fields = await asyncio.gather(ticket_task, fields_task)

        ticket = Ticket(**response["ticket"])
        ticket_users = self._extract_users_from_response(response)
        return await self._build_enriched_ticket(ticket, ticket_users, fields)

    async def search_enriched(
        self,
        query: Union[str, SearchQueryConfig],
        limit: Optional[int] = None,
    ) -> AsyncIterator[EnrichedTicket]:
        """Search for tickets and load all related data with automatic pagination.

        Note: This method makes N+1 API calls per ticket (fetching comments).
        Users are batched for efficiency.

        Args:
            query: SearchQueryConfig or raw query string
            limit: Maximum number of results to return (None = no limit)

        Yields:
            EnrichedTicket objects

        Example:
            # Iterate through enriched tickets
            async for item in client.tickets.search_enriched("status:open", limit=10):
                print(f"Ticket: {item.ticket.subject}")
                print(f"Requester: {item.requester.name}")
                print(f"Comments: {len(item.comments)}")

            # Collect to list
            enriched = [e async for e in client.tickets.search_enriched(query)]
        """
        full_query = self._resolve_query(query)
        paginator = ZendeskPaginator.create_search_tickets_paginator(
            self._http, query=full_query, per_page=100, limit=limit
        )

        # Fetch fields once at the start
        fields = await self._fetch_fields()

        # Process in batches for efficient user fetching
        batch: List[Ticket] = []
        async for ticket in paginator:
            batch.append(ticket)

            if len(batch) >= 100:
                async for enriched in self._enrich_ticket_batch(batch, fields):
                    yield enriched
                batch = []

        # Process remaining
        if batch:
            async for enriched in self._enrich_ticket_batch(batch, fields):
                yield enriched

    async def _enrich_ticket_batch(
        self,
        tickets: List[Ticket],
        fields: Optional[Dict[int, TicketField]] = None,
    ) -> AsyncIterator[EnrichedTicket]:
        """Enrich a batch of tickets with users, comments, and fields."""
        if not tickets:
            return

        # Batch fetch users for all tickets
        user_ids = self._collect_user_ids_from_tickets(tickets)
        ticket_users = await self._fetch_users_batch(user_ids)

        # Fetch comments and build enriched tickets
        enriched_list = await self._build_enriched_tickets(tickets, ticket_users, fields)
        for enriched in enriched_list:
            yield enriched

"""Tickets API client with nested Comments and Tags."""

import asyncio
from functools import cached_property
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Union

from ..models import Comment, EnrichedTicket, Ticket, User
from ..models.search import SearchQueryConfig, SearchType
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class CommentsClient(BaseClient):
    """Client for Ticket Comments API.

    Example:
        async with ZendeskClient(config) as client:
            # List comments on a ticket
            comments = await client.tickets.comments.list(12345)

            # Add a private note
            await client.tickets.comments.add(12345, "Internal note")

            # Add a public reply
            await client.tickets.comments.add(12345, "Hello!", public=True)
    """

    async def list(self, ticket_id: int, per_page: int = 100) -> List[Comment]:
        """Get comments for a specific ticket.

        Args:
            ticket_id: The ticket's ID
            per_page: Number of comments per page (max 100)

        Returns:
            List of Comment objects
        """
        response = await self._get(f"tickets/{ticket_id}/comments.json", params={"per_page": per_page})
        return [Comment(**comment_data) for comment_data in response.get("comments", [])]

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

    Provides access to tickets, comments, and tags through a namespace pattern.

    Example:
        async with ZendeskClient(config) as client:
            # Get a ticket
            ticket = await client.tickets.get(12345)

            # List all tickets
            paginator = await client.tickets.list()

            # Get tickets for a user
            tickets = await client.tickets.for_user(67890)

            # Access nested resources
            comments = await client.tickets.comments.list(12345)
            tags = await client.tickets.tags.get(12345)

            # Get enriched ticket with all data
            enriched = await client.tickets.get_enriched(12345)
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize tickets client with nested clients."""
        super().__init__(http_client)
        self._comments: Optional[CommentsClient] = None
        self._tags: Optional[TagsClient] = None

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

    async def list(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of tickets.

        Args:
            per_page: Number of tickets per page (max 100)

        Returns:
            Paginator for iterating through all tickets
        """
        return ZendeskPaginator.create_tickets_paginator(self._http, per_page=per_page)

    async def for_user(self, user_id: int, per_page: int = 100) -> List[Ticket]:
        """Get tickets requested by a specific user.

        Args:
            user_id: The user's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of Ticket objects
        """
        response = await self._get(f"users/{user_id}/tickets/requested.json", params={"per_page": per_page})
        return [Ticket(**ticket_data) for ticket_data in response.get("tickets", [])]

    async def for_organization(self, org_id: int, per_page: int = 100) -> List[Ticket]:
        """Get tickets for a specific organization.

        Args:
            org_id: The organization's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of Ticket objects
        """
        response = await self._get(f"organizations/{org_id}/tickets.json", params={"per_page": per_page})
        return [Ticket(**ticket_data) for ticket_data in response.get("tickets", [])]

    def _resolve_query(self, query: Union[str, SearchQueryConfig]) -> str:
        """Convert query input to Zendesk query string."""
        if isinstance(query, SearchQueryConfig):
            # Force ticket type and get query string
            if query.type != SearchType.TICKET:
                query = query.model_copy(update={"type": SearchType.TICKET})
            return query.to_query()
        else:
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

    async def _build_enriched_ticket(self, ticket: Ticket, ticket_users: Dict[int, User]) -> EnrichedTicket:
        """Build EnrichedTicket by fetching comments and merging users."""
        if ticket.id is None:
            raise ValueError("Ticket must have an ID to fetch full data")
        comments, comment_users = await self._fetch_comments_with_users(ticket.id)
        all_users = {**ticket_users, **comment_users}
        return EnrichedTicket(ticket=ticket, comments=comments, users=all_users)

    async def _build_enriched_tickets(
        self, tickets: List[Ticket], ticket_users: Dict[int, User]
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
            enriched_tickets.append(EnrichedTicket(ticket=ticket, comments=comments, users=all_users))

        return enriched_tickets

    async def get_enriched(self, ticket_id: int) -> EnrichedTicket:
        """Get a ticket with all related data: comments and users.

        Args:
            ticket_id: The ticket's ID

        Returns:
            EnrichedTicket object containing ticket, comments, and all related users
        """
        response = await self._get(f"tickets/{ticket_id}.json", params={"include": "users"})
        ticket = Ticket(**response["ticket"])
        ticket_users = self._extract_users_from_response(response)
        return await self._build_enriched_ticket(ticket, ticket_users)

    async def search_enriched(
        self,
        query: Union[str, SearchQueryConfig],
        per_page: int = 100,
        limit: Optional[int] = None,
    ) -> AsyncIterator[EnrichedTicket]:
        """Search for tickets and load all related data with automatic pagination.

        Args:
            query: SearchQueryConfig or raw query string
            per_page: Number of results per page (max 100)
            limit: Maximum number of results to return (None = no limit)

        Yields:
            EnrichedTicket objects

        Example:
            # Iterate through enriched tickets
            async for item in client.tickets.search_enriched(config, limit=10):
                print(f"Ticket: {item.ticket.subject}")
                print(f"Requester: {item.requester.name}")
                print(f"Comments: {len(item.comments)}")

            # Collect to list
            enriched = [e async for e in client.tickets.search_enriched(config)]
        """
        full_query = self._resolve_query(query)
        paginator = ZendeskPaginator.create_search_paginator(
            self._http, query=full_query, per_page=per_page
        )

        count = 0
        async for page_data in self._paginate_enriched(paginator):
            # page_data is a batch of raw ticket dicts
            tickets = [Ticket(**r) for r in page_data if r.get("result_type") == "ticket"]

            if not tickets:
                continue

            # Enrich the batch
            user_ids = self._collect_user_ids_from_tickets(tickets)
            ticket_users = await self._fetch_users_batch(user_ids)
            enriched_batch = await self._build_enriched_tickets(tickets, ticket_users)

            for enriched in enriched_batch:
                yield enriched
                count += 1
                if limit and count >= limit:
                    return

    async def _paginate_enriched(
        self, paginator: "Paginator[Dict[str, Any]]"
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """Yield pages of raw ticket data for batch enrichment."""
        while True:
            try:
                items = await paginator.get_page()
                if items:
                    yield items
                if not paginator._has_more_pages():
                    break
                paginator._advance_to_next_page()
            except Exception:
                break

    async def for_organization_enriched(self, org_id: int, per_page: int = 100) -> List[EnrichedTicket]:
        """Get tickets for an organization with all related data.

        Args:
            org_id: The organization's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of EnrichedTicket objects
        """
        response = await self._get(
            f"organizations/{org_id}/tickets.json", params={"per_page": per_page, "include": "users"}
        )

        tickets = [Ticket(**t) for t in response.get("tickets", [])]
        ticket_users = self._extract_users_from_response(response)

        return await self._build_enriched_tickets(tickets, ticket_users)

    async def for_user_enriched(self, user_id: int, per_page: int = 100) -> List[EnrichedTicket]:
        """Get tickets requested by a user with all related data.

        Args:
            user_id: The user's ID
            per_page: Number of tickets per page (max 100)

        Returns:
            List of EnrichedTicket objects
        """
        response = await self._get(
            f"users/{user_id}/tickets/requested.json", params={"per_page": per_page, "include": "users"}
        )

        tickets = [Ticket(**t) for t in response.get("tickets", [])]
        ticket_users = self._extract_users_from_response(response)

        return await self._build_enriched_tickets(tickets, ticket_users)

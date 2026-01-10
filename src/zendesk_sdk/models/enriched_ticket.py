"""EnrichedTicket model - ticket with all related data."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel
from .comment import Comment
from .ticket import Ticket, TicketField
from .user import User


class EnrichedTicket(ZendeskModel):
    """Ticket with all related data: comments, users, and field definitions.

    EnrichedTicket provides convenient access to all ticket-related data
    in a single object, including resolved user references and custom field
    definitions.

    Attributes:
        ticket: The core ticket object
        comments: All comments for this ticket
        users: Dictionary of all related users by their ID
        fields: Dictionary of all ticket field definitions by their ID

    Example:
        async with ZendeskClient(config) as client:
            enriched = await client.tickets.get_enriched(12345)

            # Access ticket properties
            print(f"Subject: {enriched.ticket.subject}")
            print(f"Status: {enriched.ticket.status}")

            # Access resolved user references
            print(f"Requester: {enriched.requester.name}")
            print(f"Assignee: {enriched.assignee.name if enriched.assignee else 'Unassigned'}")

            # Iterate over comments with authors
            for comment in enriched.comments:
                author = enriched.get_comment_author(comment)
                print(f"{author.name}: {comment.plain_body}")

            # Access custom field values by title
            custom_values = enriched.get_field_values()
            print(f"Subscription: {custom_values.get('Subscription')}")
    """

    ticket: Ticket = Field(..., description="The ticket")
    comments: List[Comment] = Field(default_factory=list, description="All comments for this ticket")
    users: Dict[int, User] = Field(default_factory=dict, description="All related users by ID")
    fields: Dict[int, TicketField] = Field(default_factory=dict, description="All ticket field definitions by ID")

    def get_user(self, user_id: Optional[int]) -> Optional[User]:
        """Get user by ID from loaded users.

        Args:
            user_id: User ID to look up

        Returns:
            User object if found, None otherwise
        """
        if user_id is None:
            return None
        return self.users.get(user_id)

    @property
    def requester(self) -> Optional[User]:
        """Get the ticket requester."""
        return self.get_user(self.ticket.requester_id)

    @property
    def assignee(self) -> Optional[User]:
        """Get the ticket assignee."""
        return self.get_user(self.ticket.assignee_id)

    @property
    def submitter(self) -> Optional[User]:
        """Get the ticket submitter."""
        return self.get_user(self.ticket.submitter_id)

    def get_comment_author(self, comment: Comment) -> Optional[User]:
        """Get the author of a comment.

        Args:
            comment: Comment object

        Returns:
            User object if found, None otherwise
        """
        return self.get_user(comment.author_id)

    def get_field(self, field_id: int) -> Optional[TicketField]:
        """Get field definition by ID.

        Args:
            field_id: Field ID to look up

        Returns:
            TicketField object if found, None otherwise
        """
        return self.fields.get(field_id)

    def get_field_value(self, field_id: int) -> Any:
        """Get custom field value from ticket by field ID.

        Args:
            field_id: Field ID to look up

        Returns:
            Field value if found, None otherwise
        """
        if not self.ticket.custom_fields:
            return None
        for cf in self.ticket.custom_fields:
            if cf.id == field_id:
                return cf.value
        return None

    def get_field_values(self) -> Dict[str, Any]:
        """Get all custom field values as dict with field titles as keys.

        Returns:
            Dictionary mapping field title to value, e.g.:
            {"Subscription": "enterprise", "Username": "john@example.com", ...}
        """
        result: Dict[str, Any] = {}
        if not self.ticket.custom_fields:
            return result
        for cf in self.ticket.custom_fields:
            field_def = self.fields.get(cf.id)
            if field_def:
                result[field_def.title] = cf.value
            else:
                # Fallback to ID if field definition not found
                result[str(cf.id)] = cf.value
        return result

    def __str__(self) -> str:
        """Human-readable string representation."""
        requester = self.requester.name if self.requester else "Unknown"
        assignee = self.assignee.name if self.assignee else "Unassigned"
        return f"{self.ticket} | by {requester} → {assignee} | {len(self.comments)} comments"

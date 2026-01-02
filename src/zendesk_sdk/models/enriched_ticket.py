"""EnrichedTicket model - ticket with all related data."""

from typing import Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel
from .comment import Comment
from .ticket import Ticket
from .user import User


class EnrichedTicket(ZendeskModel):
    """Ticket with all related data: comments and users."""

    ticket: Ticket = Field(..., description="The ticket")
    comments: List[Comment] = Field(default_factory=list, description="All comments for this ticket")
    users: Dict[int, User] = Field(default_factory=dict, description="All related users by ID")

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

"""Group Membership model for Zendesk API."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import ZendeskModel


class GroupMembership(ZendeskModel):
    """Zendesk Group Membership model.

    Represents the association between a user (agent) and a group.
    Agents can be members of multiple groups, and one group is marked
    as their default group for ticket assignment.
    """

    # Read-only fields
    id: Optional[int] = Field(None, description="Automatically assigned when creating memberships")
    url: Optional[str] = Field(None, description="The API url of the membership")
    user_id: int = Field(..., description="The ID of the agent")
    group_id: int = Field(..., description="The ID of the group")
    default: Optional[bool] = Field(None, description="If true, tickets assigned directly to the agent use this group")
    created_at: Optional[datetime] = Field(None, description="The time the membership was created")
    updated_at: Optional[datetime] = Field(None, description="The time of the last update")

    def __str__(self) -> str:
        """Human-readable string representation."""
        default_str = " (default)" if self.default else ""
        return f"User {self.user_id} -> Group {self.group_id}{default_str} (id={self.id})"

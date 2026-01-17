"""Group model for Zendesk API."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import ZendeskModel


class Group(ZendeskModel):
    """Zendesk Group model with all API fields.

    Groups organize agents into teams for ticket assignment and routing.
    Tickets can be assigned to groups, and agents can be members of multiple groups.
    """

    # Read-only fields
    id: Optional[int] = Field(None, description="Automatically assigned when creating groups")
    url: Optional[str] = Field(None, description="The API url of the group")
    default: Optional[bool] = Field(None, description="If the group is the default one for the account")
    deleted: Optional[bool] = Field(None, description="Deleted groups get marked as such")
    created_at: Optional[datetime] = Field(None, description="The time the group was created")
    updated_at: Optional[datetime] = Field(None, description="The time of the last update of the group")

    # Writable fields
    name: str = Field(..., description="The name of the group")
    description: Optional[str] = Field(None, description="The description of the group")
    is_public: Optional[bool] = Field(None, description="If true, the group is public. If false, the group is private")

    def __str__(self) -> str:
        """Human-readable string representation."""
        status = " (default)" if self.default else ""
        status += " (deleted)" if self.deleted else ""
        return f"{self.name}{status} (id={self.id})"

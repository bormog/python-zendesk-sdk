"""View models for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from .base import ZendeskModel


class View(ZendeskModel):
    """Zendesk View — a saved search of tickets visible to agents.

    Views ("My Open Tickets", "Unassigned High Priority") are the way
    agents work with tickets day-to-day. They're built from conditions
    (`all`/`any` clauses) and can be personal or shared.
    """

    # Read-only fields
    id: Optional[int] = Field(default=None, description="Automatically assigned when the view is created")
    url: Optional[str] = Field(default=None, description="The API URL of the view")
    default: Optional[bool] = Field(default=None, description="If true, the view is one of the default views")
    created_at: Optional[datetime] = Field(default=None, description="The time the view was created")
    updated_at: Optional[datetime] = Field(default=None, description="The time the view was last updated")

    # Writable fields
    title: Optional[str] = Field(default=None, description="The title of the view")
    description: Optional[str] = Field(default=None, description="The description of the view")
    active: Optional[bool] = Field(default=None, description="Useful for determining if the view should be displayed")
    position: Optional[int] = Field(default=None, description="The position of the view")

    # Structured fields
    conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="An object describing how the view is constructed"
    )
    execution: Optional[Dict[str, Any]] = Field(
        default=None, description="An object describing how the view is executed (columns, sort, group_by)"
    )
    restriction: Optional[Dict[str, Any]] = Field(
        default=None, description="Who has access — null (everyone), or {type: 'Group'/'User', id, ids}"
    )
    raw_title: Optional[str] = Field(default=None, description="The raw title (untranslated) of the view")

    def __str__(self) -> str:
        """Human-readable string representation."""
        flags = []
        if self.active is False:
            flags.append("inactive")
        if self.default:
            flags.append("default")
        suffix = f" [{', '.join(flags)}]" if flags else ""
        return f"{self.title}{suffix} (id={self.id})"


class ViewCount(ZendeskModel):
    """Count of tickets in a view.

    Returned by `/views/{id}/count` and `/views/count_many` endpoints.
    Counts are cached server-side and may be stale (`fresh=False`).
    """

    view_id: Optional[int] = Field(default=None, description="The view's ID")
    url: Optional[str] = Field(default=None, description="The API URL that was queried")
    value: Optional[int] = Field(default=None, description="The actual count of tickets in the view")
    pretty: Optional[str] = Field(default=None, description="Human-readable representation of value (e.g., '1k+')")
    fresh: Optional[bool] = Field(default=None, description="True if the count is up-to-date, False if cached/stale")

    def __str__(self) -> str:
        """Human-readable string representation."""
        staleness = "" if self.fresh else " (stale)"
        return f"ViewCount(view_id={self.view_id}, value={self.value}{staleness})"

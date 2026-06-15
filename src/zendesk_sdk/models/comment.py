"""Comment model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class CommentAttachment(ZendeskModel):
    """Comment attachment model."""

    id: Optional[int] = Field(default=None, description="Attachment ID")
    file_name: Optional[str] = Field(default=None, description="Filename of the attachment")
    content_url: Optional[str] = Field(default=None, description="URL to download the attachment")
    content_type: Optional[str] = Field(default=None, description="MIME type of the attachment")
    size: Optional[int] = Field(default=None, description="Size of the attachment in bytes")
    width: Optional[int] = Field(default=None, description="Width in pixels (images only)")
    height: Optional[int] = Field(default=None, description="Height in pixels (images only)")
    inline: Optional[bool] = Field(default=None, description="If attachment is inline")
    deleted: Optional[bool] = Field(default=None, description="If attachment has been deleted")
    url: Optional[str] = Field(default=None, description="API URL for this attachment")
    thumbnails: Optional[List[Dict[str, Any]]] = Field(default=None, description="Thumbnail attachments")


class CommentVia(ZendeskModel):
    """Comment via object."""

    channel: Optional[str] = Field(default=None, description="The channel the comment was created through")
    source: Optional[Dict[str, Any]] = Field(default=None, description="Additional source information")


class CommentMetadata(ZendeskModel):
    """Comment metadata model."""

    system: Optional[Dict[str, Any]] = Field(default=None, description="System information like web client, IP address")
    custom: Optional[Dict[str, Any]] = Field(default=None, description="Custom metadata")
    flags: Optional[List[Any]] = Field(default=None, description="Comment flags (can be strings or integers)")
    flags_options: Optional[Dict[str, Any]] = Field(default=None, description="Comment flag options")


class Comment(ZendeskModel):
    """Zendesk Comment model with all API fields."""

    id: Optional[int] = Field(default=None, description="Automatically assigned when the comment is created")
    type: Optional[str] = Field(default=None, description="Comment or VoiceComment")
    author_id: Optional[int] = Field(default=None, description="The id of the comment author")
    body: Optional[str] = Field(default=None, description="The comment string")
    html_body: Optional[str] = Field(default=None, description="The comment formatted as HTML")
    plain_body: Optional[str] = Field(default=None, description="The comment presented as plain text")
    public: Optional[bool] = Field(default=None, description="True if a public comment; false if an internal note")
    audit_id: Optional[int] = Field(default=None, description="The id of the ticket audit record")
    via: Optional[CommentVia] = Field(default=None, description="Describes how the object was created")
    created_at: Optional[datetime] = Field(default=None, description="The time the comment was created")
    attachments: Optional[List[CommentAttachment]] = Field(default=None, description="Attachments, if any")
    metadata: Optional[CommentMetadata] = Field(default=None, description="System information and comment flags")
    uploads: Optional[List[str]] = Field(
        default=None, description="List of tokens from uploading files for attachments"
    )

    # Additional fields that may appear in some contexts
    ticket_id: Optional[int] = Field(default=None, description="The ID of the ticket this comment belongs to")
    event_type: Optional[str] = Field(
        default=None, description="Event type when comment appears in audit/export context"
    )

    def __str__(self) -> str:
        """Human-readable string representation."""
        visibility = "public" if self.public else "private"
        body = (self.plain_body or self.body or "")[:100]
        return f"[{visibility}] {body}"

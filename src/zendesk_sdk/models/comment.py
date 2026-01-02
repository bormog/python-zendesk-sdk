"""Comment model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class CommentAttachment(ZendeskModel):
    """Comment attachment model."""

    id: Optional[int] = Field(None, description="Attachment ID")
    file_name: Optional[str] = Field(None, description="Filename of the attachment")
    content_url: Optional[str] = Field(None, description="URL to download the attachment")
    content_type: Optional[str] = Field(None, description="MIME type of the attachment")
    size: Optional[int] = Field(None, description="Size of the attachment in bytes")
    width: Optional[int] = Field(None, description="Width in pixels (images only)")
    height: Optional[int] = Field(None, description="Height in pixels (images only)")
    inline: Optional[bool] = Field(None, description="If attachment is inline")
    deleted: Optional[bool] = Field(None, description="If attachment has been deleted")
    url: Optional[str] = Field(None, description="API URL for this attachment")
    thumbnails: Optional[List[Dict[str, Any]]] = Field(None, description="Thumbnail attachments")


class CommentVia(ZendeskModel):
    """Comment via object."""

    channel: Optional[str] = Field(None, description="The channel the comment was created through")
    source: Optional[Dict[str, Any]] = Field(None, description="Additional source information")


class CommentMetadata(ZendeskModel):
    """Comment metadata model."""

    system: Optional[Dict[str, Any]] = Field(None, description="System information like web client, IP address")
    custom: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    flags: Optional[List[Any]] = Field(None, description="Comment flags (can be strings or integers)")
    flags_options: Optional[Dict[str, Any]] = Field(None, description="Comment flag options")


class Comment(ZendeskModel):
    """Zendesk Comment model with all API fields."""

    id: Optional[int] = Field(None, description="Automatically assigned when the comment is created")
    type: Optional[str] = Field(None, description="Comment or VoiceComment")
    author_id: Optional[int] = Field(None, description="The id of the comment author")
    body: Optional[str] = Field(None, description="The comment string")
    html_body: Optional[str] = Field(None, description="The comment formatted as HTML")
    plain_body: Optional[str] = Field(None, description="The comment presented as plain text")
    public: Optional[bool] = Field(None, description="True if a public comment; false if an internal note")
    audit_id: Optional[int] = Field(None, description="The id of the ticket audit record")
    via: Optional[CommentVia] = Field(None, description="Describes how the object was created")
    created_at: Optional[datetime] = Field(None, description="The time the comment was created")
    attachments: Optional[List[CommentAttachment]] = Field(None, description="Attachments, if any")
    metadata: Optional[CommentMetadata] = Field(None, description="System information and comment flags")
    uploads: Optional[List[str]] = Field(None, description="List of tokens from uploading files for attachments")

    # Additional fields that may appear in some contexts
    ticket_id: Optional[int] = Field(None, description="The ID of the ticket this comment belongs to")
    event_type: Optional[str] = Field(None, description="Event type when comment appears in audit/export context")

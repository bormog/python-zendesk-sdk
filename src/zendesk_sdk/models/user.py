"""User model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class UserIdentity(ZendeskModel):
    """User identity model."""

    id: Optional[int] = Field(None, description="Automatically assigned on creation")
    url: Optional[str] = Field(None, description="The API url of this identity")
    user_id: int = Field(..., description="The id of the user")
    type: str = Field(..., description="The type of identity")
    value: str = Field(..., description="The identifier for this identity, such as an email address")
    verified: Optional[bool] = Field(None, description="If the identity has been verified")
    primary: Optional[bool] = Field(None, description="If the identity is the primary identity")
    created_at: Optional[datetime] = Field(None, description="The time the identity was created")
    updated_at: Optional[datetime] = Field(None, description="The time the identity was updated")
    undeliverable_count: Optional[int] = Field(None, description="Number of soft-bounce responses received")
    deliverable_state: Optional[str] = Field(None, description="Email delivery state")
    verification_method: Optional[str] = Field(None, description="State of user identity verification")
    verified_at: Optional[datetime] = Field(None, description="Last time full verification was completed")


class UserPhoto(ZendeskModel):
    """User photo attachment model."""

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


class User(ZendeskModel):
    """Zendesk User model with all API fields."""

    id: Optional[int] = Field(None, description="Automatically assigned when the user is created")
    url: Optional[str] = Field(None, description="The API URL of this user")
    name: str = Field(..., description="The user's name")
    email: Optional[str] = Field(None, description="The user's primary email address")
    created_at: Optional[datetime] = Field(None, description="The time the user was created")
    updated_at: Optional[datetime] = Field(None, description="The time the user was last updated")
    time_zone: Optional[str] = Field(None, description="The user's time zone")
    iana_time_zone: Optional[str] = Field(None, description="The time zone for the user")
    phone: Optional[str] = Field(None, description="The user's primary phone number")
    shared_phone_number: Optional[bool] = Field(None, description="Whether the phone number is shared")
    photo: Optional[UserPhoto] = Field(None, description="The user's profile picture")
    locale_id: Optional[int] = Field(None, description="The user's language identifier")
    locale: Optional[str] = Field(None, description="The user's locale (BCP-47 compliant)")
    organization_id: Optional[int] = Field(None, description="The id of the user's organization")
    role: Optional[str] = Field(None, description="The user's role")
    verified: Optional[bool] = Field(None, description="If the user's primary identity has been verified")
    external_id: Optional[str] = Field(None, description="A unique identifier from another system")
    tags: Optional[List[str]] = Field(None, description="The user's tags")
    alias: Optional[str] = Field(None, description="An alias displayed to end users")
    active: Optional[bool] = Field(None, description="False if the user has been deleted")
    shared: Optional[bool] = Field(None, description="If the user is shared from different instance")
    shared_agent: Optional[bool] = Field(None, description="If the user is a shared agent")
    last_login_at: Optional[datetime] = Field(None, description="Last time user signed in or made API request")
    two_factor_auth_enabled: Optional[bool] = Field(None, description="If user has two-factor authentication enabled")
    signature: Optional[str] = Field(None, description="The user's signature")
    details: Optional[str] = Field(None, description="Any details about the user")
    notes: Optional[str] = Field(None, description="Any notes about the user")
    role_type: Optional[int] = Field(None, description="The user's role id")
    custom_role_id: Optional[int] = Field(None, description="A custom role if user is agent on Enterprise+")
    moderator: Optional[bool] = Field(None, description="If user has forum moderation capabilities")
    ticket_restriction: Optional[str] = Field(None, description="Which tickets the user has access to")
    only_private_comments: Optional[bool] = Field(None, description="If user can only create private comments")
    restricted_agent: Optional[bool] = Field(None, description="If agent has any restrictions")
    suspended: Optional[bool] = Field(None, description="If the agent is suspended")
    default_group_id: Optional[int] = Field(None, description="The id of the user's default group")
    report_csv: Optional[bool] = Field(None, description="Inert parameter for CSV report access")
    user_fields: Optional[Dict[str, Any]] = Field(None, description="Custom user field values")

    def __str__(self) -> str:
        """Human-readable string representation."""
        email = f" <{self.email}>" if self.email else ""
        role = f" ({self.role})" if self.role else ""
        return f"{self.name}{email}{role}"


class PasswordRequirements(ZendeskModel):
    """Password requirements for a user.

    Zendesk returns requirements as human-readable strings.
    Use the `rules` property to get the list of requirement descriptions.
    """

    requirements: List[str] = Field(..., description="List of password requirement descriptions")

    @property
    def rules(self) -> List[str]:
        """Get password requirements as list of strings."""
        return self.requirements

    def __str__(self) -> str:
        """Human-readable representation."""
        return "; ".join(self.requirements)


class UserField(ZendeskModel):
    """Zendesk User Field model."""

    id: Optional[int] = Field(None, description="Automatically assigned upon creation")
    url: Optional[str] = Field(None, description="The URL for this resource")
    key: str = Field(..., description="A unique key that identifies this custom field")
    type: str = Field(..., description="The custom field type")
    title: str = Field(..., description="The title of the custom field")
    raw_title: Optional[str] = Field(None, description="Dynamic content placeholder or title")
    description: Optional[str] = Field(None, description="User-defined description of field's purpose")
    raw_description: Optional[str] = Field(None, description="Dynamic content placeholder or description")
    position: Optional[int] = Field(None, description="Ordering of field relative to other fields")
    active: Optional[bool] = Field(None, description="If true, this field is available for use")
    system: Optional[bool] = Field(None, description="If true, only active and position can be changed")
    regexp_for_validation: Optional[str] = Field(None, description="Validation pattern for field value")
    tag: Optional[str] = Field(None, description="Optional for checkbox type fields")
    custom_field_options: Optional[List[Dict[str, Any]]] = Field(None, description="Options for dropdown fields")
    created_at: Optional[datetime] = Field(None, description="Time of field creation")
    updated_at: Optional[datetime] = Field(None, description="Time of last field update")
    relationship_target_type: Optional[str] = Field(None, description="Type of object the field references")
    relationship_filter: Optional[Dict[str, Any]] = Field(None, description="Filter definition for autocomplete")

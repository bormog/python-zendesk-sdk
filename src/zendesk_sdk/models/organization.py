"""Organization model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class Organization(ZendeskModel):
    """Zendesk Organization model with all API fields."""

    id: Optional[int] = Field(None, description="Automatically assigned when the organization is created")
    url: Optional[str] = Field(None, description="The API url of this organization")
    name: str = Field(..., description="A unique name for the organization")
    created_at: Optional[datetime] = Field(None, description="The time the organization was created")
    updated_at: Optional[datetime] = Field(None, description="The time of the last update of the organization")
    details: Optional[str] = Field(None, description="Any details about the organization, such as the address")
    notes: Optional[str] = Field(None, description="Any notes you have about the organization")
    external_id: Optional[str] = Field(None, description="A unique external id to associate organizations")
    domain_names: Optional[List[str]] = Field(None, description="Array of domain names associated with organization")
    tags: Optional[List[str]] = Field(None, description="The tags of the organization")
    group_id: Optional[int] = Field(None, description="New tickets from users automatically put in this group")
    shared_tickets: Optional[bool] = Field(None, description="End users can see each other's tickets")
    shared_comments: Optional[bool] = Field(None, description="End users can comment on each other's tickets")
    organization_fields: Optional[Dict[str, Any]] = Field(None, description="Custom organization field values")


class OrganizationField(ZendeskModel):
    """Zendesk Organization Field model."""

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


class OrganizationSubscription(ZendeskModel):
    """Organization subscription model."""

    id: Optional[int] = Field(None, description="The ID of the organization subscription")
    organization_id: Optional[int] = Field(None, description="The ID of the organization")
    user_id: Optional[int] = Field(None, description="The ID of the user")
    created_at: Optional[datetime] = Field(None, description="The date the organization subscription was created")

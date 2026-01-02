"""Ticket model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class TicketVia(ZendeskModel):
    """Ticket via object."""

    channel: Optional[str] = Field(None, description="The channel the ticket was created through")
    source: Optional[Dict[str, Any]] = Field(None, description="Additional source information")


class TicketCustomField(ZendeskModel):
    """Custom field value for tickets."""

    id: int = Field(..., description="The ID of the custom field")
    value: Optional[Any] = Field(None, description="The value of the custom field")


class SatisfactionRating(ZendeskModel):
    """Satisfaction rating for ticket."""

    id: Optional[int] = Field(None, description="The ID of the satisfaction rating")
    score: Optional[str] = Field(None, description="The satisfaction score")
    comment: Optional[str] = Field(None, description="The satisfaction rating comment")


class TicketMetrics(ZendeskModel):
    """Zendesk Ticket Metrics model."""

    id: Optional[int] = Field(None, description="Automatically assigned when the client is created")
    url: Optional[str] = Field(None, description="The API url of the ticket metric")
    ticket_id: Optional[int] = Field(None, description="Id of the associated ticket")
    created_at: Optional[datetime] = Field(None, description="When the record was created")
    updated_at: Optional[datetime] = Field(None, description="When the record was last updated")
    group_stations: Optional[int] = Field(None, description="Number of groups the ticket passed through")
    assignee_stations: Optional[int] = Field(None, description="Number of assignees the ticket had")
    reopens: Optional[int] = Field(None, description="Total number of times the ticket was reopened")
    replies: Optional[int] = Field(None, description="The number of public replies added to a ticket by an agent")
    assignee_updated_at: Optional[datetime] = Field(None, description="When the assignee last updated the ticket")
    requester_updated_at: Optional[datetime] = Field(None, description="When the requester last updated the ticket")
    status_updated_at: Optional[datetime] = Field(None, description="When the status of the ticket was last updated")
    initially_assigned_at: Optional[datetime] = Field(None, description="When the ticket was initially assigned")
    assigned_at: Optional[datetime] = Field(None, description="When the ticket was assigned")
    solved_at: Optional[datetime] = Field(None, description="When the ticket was solved")
    latest_comment_added_at: Optional[datetime] = Field(None, description="When the latest comment was added")
    custom_status_updated_at: Optional[datetime] = Field(
        None, description="When ticket's custom status was last updated"
    )
    reply_time_in_minutes: Optional[Dict[str, Any]] = Field(
        None, description="Minutes to first reply during business hours"
    )
    reply_time_in_seconds: Optional[Dict[str, Any]] = Field(
        None, description="Seconds to first reply during calendar hours"
    )
    first_resolution_time_in_minutes: Optional[Dict[str, Any]] = Field(None, description="Minutes to first resolution")
    full_resolution_time_in_minutes: Optional[Dict[str, Any]] = Field(None, description="Minutes to full resolution")
    agent_wait_time_in_minutes: Optional[Dict[str, Any]] = Field(None, description="Minutes agent spent waiting")
    requester_wait_time_in_minutes: Optional[Dict[str, Any]] = Field(
        None, description="Minutes requester spent waiting"
    )
    on_hold_time_in_minutes: Optional[Dict[str, Any]] = Field(None, description="Number of minutes on hold")


class Ticket(ZendeskModel):
    """Zendesk Ticket model with all API fields."""

    id: Optional[int] = Field(None, description="Automatically assigned when the ticket is created")
    url: Optional[str] = Field(None, description="The API URL of this ticket")
    external_id: Optional[str] = Field(None, description="An id you can use to link Zendesk tickets to local records")
    created_at: Optional[datetime] = Field(None, description="When this record was created")
    updated_at: Optional[datetime] = Field(None, description="When this record was last updated")
    type: Optional[str] = Field(None, description="The type of this ticket")
    subject: Optional[str] = Field(None, description="The value of the subject field for this ticket")
    raw_subject: Optional[str] = Field(None, description="The dynamic content placeholder if present")
    description: Optional[str] = Field(None, description="Read-only first comment on the ticket")
    priority: Optional[str] = Field(None, description="The urgency with which the ticket should be addressed")
    status: Optional[str] = Field(None, description="The state of the ticket")
    recipient: Optional[str] = Field(None, description="The original recipient e-mail address of the ticket")
    requester_id: Optional[int] = Field(None, description="The user who requested this ticket")
    submitter_id: Optional[int] = Field(None, description="The user who submitted the ticket")
    assignee_id: Optional[int] = Field(None, description="The agent currently assigned to the ticket")
    organization_id: Optional[int] = Field(None, description="The organization of the requester")
    group_id: Optional[int] = Field(None, description="The group this ticket is assigned to")
    collaborator_ids: Optional[List[int]] = Field(None, description="The ids of users currently CC'ed on the ticket")
    follower_ids: Optional[List[int]] = Field(None, description="The ids of agents currently following the ticket")
    email_cc_ids: Optional[List[int]] = Field(
        None, description="The ids of agents or end users currently CC'ed on the ticket"
    )
    forum_topic_id: Optional[int] = Field(
        None, description="The topic in the Zendesk Web portal this ticket originated from"
    )
    problem_id: Optional[int] = Field(
        None, description="For tickets of type 'incident', the ID of the problem the incident is linked to"
    )
    has_incidents: Optional[bool] = Field(
        None, description="Is true if ticket is a problem type and has incidents linked"
    )
    is_public: Optional[bool] = Field(None, description="Is true if any comments are public, false otherwise")
    due_at: Optional[datetime] = Field(None, description="If this is a ticket of type 'task' it has a due date")
    tags: Optional[List[str]] = Field(None, description="The array of tags applied to this ticket")
    custom_fields: Optional[List[TicketCustomField]] = Field(None, description="Custom fields for the ticket")
    custom_status_id: Optional[int] = Field(None, description="The custom ticket status id of the ticket")
    satisfaction_rating: Optional[SatisfactionRating] = Field(None, description="The satisfaction rating of the ticket")
    sharing_agreement_ids: Optional[List[int]] = Field(
        None, description="The ids of the sharing agreements used for this ticket"
    )
    followup_ids: Optional[List[int]] = Field(None, description="The ids of the followups created from this ticket")
    brand_id: Optional[int] = Field(
        None, description="Enterprise only. The id of the brand this ticket is associated with"
    )
    allow_channelback: Optional[bool] = Field(None, description="Is false if channelback is disabled, true otherwise")
    allow_attachments: Optional[bool] = Field(None, description="Permission for agents to add attachments to a comment")
    from_messaging_channel: Optional[bool] = Field(
        None, description="If true, the ticket's via type is a messaging channel"
    )
    via: Optional[TicketVia] = Field(None, description="A record of the channel the ticket was created through")
    generated_timestamp: Optional[int] = Field(None, description="Unix timestamp of when this record was last updated")


class TicketField(ZendeskModel):
    """Zendesk Ticket Field model."""

    id: Optional[int] = Field(None, description="Automatically assigned when created")
    url: Optional[str] = Field(None, description="The URL for this resource")
    type: str = Field(..., description="System or custom field type")
    title: str = Field(..., description="The title of the ticket field")
    raw_title: Optional[str] = Field(None, description="Dynamic content placeholder or title")
    title_in_portal: Optional[str] = Field(
        None, description="The title of the ticket field for end users in Help Center"
    )
    raw_title_in_portal: Optional[str] = Field(None, description="Dynamic content placeholder or title_in_portal")
    description: Optional[str] = Field(None, description="Describes the purpose of the ticket field to users")
    raw_description: Optional[str] = Field(None, description="Dynamic content placeholder or description")
    position: Optional[int] = Field(None, description="The relative position of the ticket field on a ticket")
    active: Optional[bool] = Field(None, description="Whether this field is available")
    required: Optional[bool] = Field(None, description="If true, agents must enter a value to change status to solved")
    collapsed_for_agents: Optional[bool] = Field(None, description="If true, field shown to agents by default")
    regexp_for_validation: Optional[str] = Field(None, description="For 'regexp' fields only. The validation pattern")
    visible_in_portal: Optional[bool] = Field(None, description="Whether field is visible to end users in Help Center")
    editable_in_portal: Optional[bool] = Field(
        None, description="Whether field is editable by end users in Help Center"
    )
    required_in_portal: Optional[bool] = Field(
        None, description="If true, end users must enter a value to create request"
    )
    tag: Optional[str] = Field(None, description="For 'checkbox' fields only. A tag added when checkbox is selected")
    created_at: Optional[datetime] = Field(None, description="The time the custom ticket field was created")
    updated_at: Optional[datetime] = Field(None, description="The time the custom ticket field was last updated")
    removable: Optional[bool] = Field(
        None, description="If false, this field is a system field that must be present on all tickets"
    )
    agent_can_edit: Optional[bool] = Field(None, description="Whether this field is editable by agents")
    agent_description: Optional[str] = Field(None, description="A description that only agents can see")
    system_field_options: Optional[List[Dict[str, Any]]] = Field(None, description="Presented for system ticket fields")
    custom_field_options: Optional[List[Dict[str, Any]]] = Field(
        None, description="Required for custom fields of certain types"
    )
    custom_statuses: Optional[List[Dict[str, Any]]] = Field(None, description="List of customized ticket statuses")
    sub_type_id: Optional[int] = Field(None, description="For system ticket fields of type 'priority' and 'status'")
    relationship_target_type: Optional[str] = Field(None, description="Type of object the field references")
    relationship_filter: Optional[Dict[str, Any]] = Field(None, description="Filter definition for autocomplete")
    creator_user_id: Optional[int] = Field(None, description="The id of the user that created the ticket field")
    creator_app_name: Optional[str] = Field(None, description="Name of the app that created the ticket field")

"""Zendesk API data models."""

from .base import ZendeskModel
from .comment import Comment, CommentAttachment, CommentMetadata, CommentVia
from .enriched_ticket import EnrichedTicket
from .help_center import Article, Category, Section
from .organization import Organization, OrganizationField, OrganizationSubscription
from .ticket import (
    SatisfactionRating,
    Ticket,
    TicketCustomField,
    TicketField,
    TicketMetrics,
    TicketVia,
)
from .user import User, UserField, UserIdentity, UserPhoto

__all__ = [
    # Base
    "ZendeskModel",
    # User models
    "User",
    "UserField",
    "UserIdentity",
    "UserPhoto",
    # Organization models
    "Organization",
    "OrganizationField",
    "OrganizationSubscription",
    # Ticket models
    "Ticket",
    "TicketField",
    "TicketMetrics",
    "TicketCustomField",
    "TicketVia",
    "SatisfactionRating",
    # Comment models
    "Comment",
    "CommentAttachment",
    "CommentMetadata",
    "CommentVia",
    # Enriched ticket model
    "EnrichedTicket",
    # Help Center models
    "Category",
    "Section",
    "Article",
]

"""Zendesk API data models."""

from .base import ZendeskModel
from .comment import Comment, CommentAttachment, CommentMetadata, CommentVia
from .enriched_ticket import EnrichedTicket
from .group import Group
from .help_center import Article, Category, Section
from .organization import Organization, OrganizationField, OrganizationSubscription
from .search import (
    SearchQueryConfig,
    SearchType,
    SortOrder,
    TicketChannel,
    TicketPriority,
    TicketPriorityInput,
    TicketPriorityLiteral,
    TicketStatus,
    TicketStatusInput,
    TicketStatusLiteral,
    TicketType,
    TicketTypeInput,
    TicketTypeLiteral,
    UserRole,
)
from .ticket import (
    SatisfactionRating,
    Ticket,
    TicketCustomField,
    TicketField,
    TicketMetrics,
    TicketVia,
)
from .user import PasswordRequirements, User, UserField, UserIdentity, UserPhoto

__all__ = [
    # Base
    "ZendeskModel",
    # User models
    "User",
    "UserField",
    "UserIdentity",
    "UserPhoto",
    "PasswordRequirements",
    # Group models
    "Group",
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
    # Search models
    "SearchQueryConfig",
    "SearchType",
    "TicketStatus",
    "TicketStatusLiteral",
    "TicketStatusInput",
    "TicketPriority",
    "TicketPriorityLiteral",
    "TicketPriorityInput",
    "TicketType",
    "TicketTypeLiteral",
    "TicketTypeInput",
    "TicketChannel",
    "UserRole",
    "SortOrder",
]

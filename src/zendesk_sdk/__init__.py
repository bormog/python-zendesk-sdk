"""
Modern Python SDK for Zendesk API.

This package provides a clean, async-first interface to the Zendesk API
with full type safety and comprehensive error handling.
"""

__version__ = "0.9.0"

from .client import ZendeskClient
from .clients import (
    ArticlesClient,
    AttachmentsClient,
    CategoriesClient,
    CommentsClient,
    GroupsClient,
    HelpCenterClient,
    OrganizationsClient,
    SearchClient,
    SectionsClient,
    TagsClient,
    TicketFieldsClient,
    TicketsClient,
    UsersClient,
)
from .config import CacheConfig, ZendeskConfig
from .exceptions import (
    ZendeskAuthException,
    ZendeskBaseException,
    ZendeskHTTPException,
    ZendeskPaginationException,
    ZendeskRateLimitException,
    ZendeskTimeoutException,
    ZendeskValidationException,
)
from .models import (
    Article,
    Category,
    EnrichedTicket,
    Group,
    PasswordRequirements,
    SearchQueryConfig,
    SearchType,
    Section,
    SortOrder,
    TicketChannel,
    TicketField,
    TicketPriority,
    TicketPriorityInput,
    TicketStatus,
    TicketStatusInput,
    TicketType,
    TicketTypeInput,
    UserRole,
)

__all__ = [
    # Main client
    "ZendeskClient",
    "ZendeskConfig",
    "CacheConfig",
    # Resource clients
    "UsersClient",
    "GroupsClient",
    "OrganizationsClient",
    "TicketsClient",
    "TicketFieldsClient",
    "CommentsClient",
    "TagsClient",
    "AttachmentsClient",
    "SearchClient",
    # Help Center
    "HelpCenterClient",
    "CategoriesClient",
    "SectionsClient",
    "ArticlesClient",
    # Models
    "Group",
    "EnrichedTicket",
    "TicketField",
    "Category",
    "Section",
    "Article",
    # Search
    "SearchQueryConfig",
    "SearchType",
    "TicketStatus",
    "TicketStatusInput",
    "TicketPriority",
    "TicketPriorityInput",
    "TicketType",
    "TicketTypeInput",
    "TicketChannel",
    "UserRole",
    "SortOrder",
    # Exceptions
    "ZendeskBaseException",
    "ZendeskHTTPException",
    "ZendeskAuthException",
    "ZendeskRateLimitException",
    "ZendeskPaginationException",
    "ZendeskTimeoutException",
    "ZendeskValidationException",
    # User models
    "PasswordRequirements",
]

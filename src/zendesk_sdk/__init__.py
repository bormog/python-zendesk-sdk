"""
Modern Python SDK for Zendesk API.

This package provides a clean, async-first interface to the Zendesk API
with full type safety and comprehensive error handling.
"""

__version__ = "0.3.1"

from .client import ZendeskClient
from .clients import (
    ArticlesClient,
    AttachmentsClient,
    CategoriesClient,
    CommentsClient,
    HelpCenterClient,
    OrganizationsClient,
    SearchClient,
    SectionsClient,
    TagsClient,
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
)
from .models import (
    Article,
    Category,
    EnrichedTicket,
    SearchQueryConfig,
    SearchType,
    Section,
    SortOrder,
    TicketChannel,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserRole,
)

__all__ = [
    # Main client
    "ZendeskClient",
    "ZendeskConfig",
    "CacheConfig",
    # Resource clients
    "UsersClient",
    "OrganizationsClient",
    "TicketsClient",
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
    "EnrichedTicket",
    "Category",
    "Section",
    "Article",
    # Search
    "SearchQueryConfig",
    "SearchType",
    "TicketStatus",
    "TicketPriority",
    "TicketType",
    "TicketChannel",
    "UserRole",
    "SortOrder",
    # Exceptions
    "ZendeskBaseException",
    "ZendeskHTTPException",
    "ZendeskAuthException",
    "ZendeskRateLimitException",
    "ZendeskPaginationException",
]

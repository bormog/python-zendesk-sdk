"""
Modern Python SDK for Zendesk API.

This package provides a clean, async-first interface to the Zendesk API
with full type safety and comprehensive error handling.
"""

__version__ = "0.2.0"

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
from .config import ZendeskConfig
from .exceptions import (
    ZendeskAuthException,
    ZendeskBaseException,
    ZendeskHTTPException,
    ZendeskPaginationException,
    ZendeskRateLimitException,
)
from .models import Article, Category, EnrichedTicket, Section

__all__ = [
    # Main client
    "ZendeskClient",
    "ZendeskConfig",
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
    # Exceptions
    "ZendeskBaseException",
    "ZendeskHTTPException",
    "ZendeskAuthException",
    "ZendeskRateLimitException",
    "ZendeskPaginationException",
]

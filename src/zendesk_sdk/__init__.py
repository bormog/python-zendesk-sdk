"""
Modern Python SDK for Zendesk API.

This package provides a clean, async-first interface to the Zendesk API
with full type safety and comprehensive error handling.
"""

__version__ = "0.1.3"

from .client import ZendeskClient
from .config import ZendeskConfig
from .exceptions import (
    ZendeskAuthException,
    ZendeskBaseException,
    ZendeskHTTPException,
    ZendeskPaginationException,
    ZendeskRateLimitException,
)
from .help_center_client import HelpCenterClient
from .models import Article, Category, EnrichedTicket, Section

__all__ = [
    "ZendeskClient",
    "ZendeskConfig",
    "HelpCenterClient",
    "EnrichedTicket",
    # Help Center models
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

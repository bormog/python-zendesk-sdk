"""Zendesk API clients."""

from .attachments import AttachmentsClient
from .groups import GroupsClient
from .help_center import ArticlesClient, CategoriesClient, HelpCenterClient, SectionsClient
from .organizations import OrganizationsClient
from .search import SearchClient
from .ticket_fields import TicketFieldsClient
from .tickets import CommentsClient, TagsClient, TicketsClient
from .users import UsersClient

__all__ = [
    # Main clients
    "UsersClient",
    "GroupsClient",
    "OrganizationsClient",
    "TicketsClient",
    "TicketFieldsClient",
    "AttachmentsClient",
    "SearchClient",
    # Ticket sub-clients
    "CommentsClient",
    "TagsClient",
    # Help Center
    "HelpCenterClient",
    "CategoriesClient",
    "SectionsClient",
    "ArticlesClient",
]

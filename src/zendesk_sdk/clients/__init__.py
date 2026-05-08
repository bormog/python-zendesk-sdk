"""Zendesk API clients."""

from .attachments import AttachmentsClient
from .groups import GroupsClient
from .help_center import ArticlesClient, CategoriesClient, HelpCenterClient, SectionsClient
from .organizations import OrganizationsClient
from .search import SearchClient
from .ticket_fields import TicketFieldsClient
from .ticket_metrics import TicketMetricsClient
from .tickets import CommentsClient, TagsClient, TicketsClient
from .users import UsersClient
from .views import ViewsClient

__all__ = [
    # Main clients
    "UsersClient",
    "GroupsClient",
    "OrganizationsClient",
    "TicketsClient",
    "TicketFieldsClient",
    "TicketMetricsClient",
    "AttachmentsClient",
    "SearchClient",
    "ViewsClient",
    # Ticket sub-clients
    "CommentsClient",
    "TagsClient",
    # Help Center
    "HelpCenterClient",
    "CategoriesClient",
    "SectionsClient",
    "ArticlesClient",
]

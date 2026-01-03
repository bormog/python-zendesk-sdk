"""Help Center API client namespace."""

from functools import cached_property
from typing import TYPE_CHECKING

from .articles import ArticlesClient
from .categories import CategoriesClient
from .sections import SectionsClient

if TYPE_CHECKING:
    from ...http_client import HTTPClient


class HelpCenterClient:
    """Client for Zendesk Help Center API.

    Provides access to Help Center resources through namespaced clients:
    - categories: Manage Help Center categories
    - sections: Manage Help Center sections
    - articles: Manage Help Center articles

    Help Center has a hierarchical structure:
    - Categories contain Sections
    - Sections contain Articles

    Example:
        async with ZendeskClient(config) as client:
            hc = client.help_center

            # Categories
            category = await hc.categories.get(123)
            paginator = await hc.categories.list()
            new_cat = await hc.categories.create(name="Docs")

            # Sections
            section = await hc.sections.get(456)
            sections = await hc.sections.for_category(123)
            new_sec = await hc.sections.create(123, name="Getting Started")

            # Articles
            article = await hc.articles.get(789)
            articles = await hc.articles.for_section(456)
            results = await hc.articles.search("password reset")
            new_art = await hc.articles.create(
                456,
                title="How to Reset Password",
                body="<p>Follow these steps...</p>"
            )

            # Cascade delete
            await hc.categories.delete(123, force=True)
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize Help Center client.

        Args:
            http_client: Shared HTTP client instance from main ZendeskClient
        """
        self._http = http_client

    @cached_property
    def categories(self) -> CategoriesClient:
        """Access Help Center Categories API."""
        return CategoriesClient(self._http)

    @cached_property
    def sections(self) -> SectionsClient:
        """Access Help Center Sections API."""
        return SectionsClient(self._http)

    @cached_property
    def articles(self) -> ArticlesClient:
        """Access Help Center Articles API."""
        return ArticlesClient(self._http)


__all__ = [
    "HelpCenterClient",
    "CategoriesClient",
    "SectionsClient",
    "ArticlesClient",
]

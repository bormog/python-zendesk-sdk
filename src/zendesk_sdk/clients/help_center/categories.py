"""Help Center Categories API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from ...models.help_center import Category
from ...pagination import ZendeskPaginator
from ..base import HelpCenterBaseClient

if TYPE_CHECKING:
    from ...config import CacheConfig
    from ...http_client import HTTPClient
    from ...pagination import Paginator


class CategoriesClient(HelpCenterBaseClient):
    """Client for Help Center Categories API.

    Example:
        async with ZendeskClient(config) as client:
            # Get a category
            category = await client.help_center.categories.get(12345)

            # List all categories
            paginator = await client.help_center.categories.list()

            # Create a category
            category = await client.help_center.categories.create(
                name="Documentation",
                description="Product documentation"
            )

            # Delete with cascade
            await client.help_center.categories.delete(12345, force=True)
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize CategoriesClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], Category] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.category_maxsize if cache_config else 200,
            ttl=cache_config.category_ttl if cache_config else 1800,
        )

    async def _get_impl(self, category_id: int) -> Category:
        """Get a specific Help Center category by ID.

        Results are cached based on cache configuration.

        Args:
            category_id: The category's ID

        Returns:
            Category object
        """
        response = await self._get(f"categories/{category_id}.json")
        return Category(**response["category"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Category]":
        """Get paginated list of Help Center categories.

        Args:
            per_page: Number of categories per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all categories
        """
        return ZendeskPaginator.create_categories_paginator(self._http, per_page=per_page, limit=limit)

    async def create(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Category:
        """Create a new Help Center category.

        Args:
            name: Category name (required)
            description: Category description
            position: Display position relative to other categories

        Returns:
            Created Category object
        """
        category_data: Dict[str, Any] = {"name": name}
        if description is not None:
            category_data["description"] = description
        if position is not None:
            category_data["position"] = position

        response = await self._post("categories.json", json={"category": category_data})
        return Category(**response["category"])

    async def update(
        self,
        category_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
        locale: Optional[str] = None,
    ) -> Category:
        """Update a Help Center category.

        Note: name and description are translation properties in Zendesk.
        They are updated via the translations API automatically.

        Args:
            category_id: The category's ID
            name: New category name (updates translation)
            description: New category description (updates translation)
            position: New display position
            locale: Locale for translation update (defaults to source locale)

        Returns:
            Updated Category object
        """
        # Update position via category endpoint if specified
        if position is not None:
            await self._put(f"categories/{category_id}.json", json={"category": {"position": position}})

        # Update name/description via translations endpoint
        if name is not None or description is not None:
            # Get current category to find source locale
            if locale is None:
                current = await self.get(category_id)
                locale = current.source_locale or "en-us"

            translation_data: Dict[str, Any] = {}
            if name is not None:
                translation_data["title"] = name
            if description is not None:
                translation_data["body"] = description

            await self._put(
                f"categories/{category_id}/translations/{locale}.json",
                json={"translation": translation_data},
            )

        # Fetch and return updated category
        return await self.get(category_id)

    async def delete(self, category_id: int, *, force: bool = False) -> bool:
        """Delete a Help Center category.

        WARNING: Deleting a category will also delete ALL sections and articles
        within that category. This action cannot be undone.

        Args:
            category_id: The category's ID
            force: Must be True to confirm cascade deletion of all
                   sections and articles. If False, raises ValueError.

        Returns:
            True if successful

        Raises:
            ValueError: If force is False (safety check)
        """
        if not force:
            raise ValueError(
                "Deleting a category will delete ALL sections and articles within it. "
                "Set force=True to confirm this destructive action."
            )
        await self._delete(f"categories/{category_id}.json")
        return True

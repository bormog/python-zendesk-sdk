"""Help Center Sections API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from ...models.help_center import Section
from ...pagination import ZendeskPaginator
from ..base import HelpCenterBaseClient

if TYPE_CHECKING:
    from ...config import CacheConfig
    from ...http_client import HTTPClient
    from ...pagination import Paginator


class SectionsClient(HelpCenterBaseClient):
    """Client for Help Center Sections API.

    Example:
        async with ZendeskClient(config) as client:
            # Get a section
            section = await client.help_center.sections.get(12345)

            # List all sections (returns paginator)
            async for section in client.help_center.sections.list():
                print(section.name)

            # Collect all sections with limit
            sections = await client.help_center.sections.list(limit=30).collect()

            # Get first page
            first_page = await client.help_center.sections.list().get_page()

            # List sections in a category (returns paginator)
            async for section in client.help_center.sections.for_category(67890):
                print(section.name)

            # Create a section
            section = await client.help_center.sections.create(
                category_id=67890,
                name="Getting Started"
            )

            # Delete with cascade
            await client.help_center.sections.delete(12345, force=True)
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize SectionsClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], Section] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.section_maxsize if cache_config else 200,
            ttl=cache_config.section_ttl if cache_config else 1800,
        )

    async def _get_impl(self, section_id: int) -> Section:
        """Get a specific Help Center section by ID.

        Results are cached based on cache configuration.

        Args:
            section_id: The section's ID

        Returns:
            Section object
        """
        response = await self._get(f"sections/{section_id}.json")
        return Section(**response["section"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Section]":
        """Get paginated list of all Help Center sections.

        Args:
            per_page: Number of sections per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all sections
        """
        return ZendeskPaginator.create_sections_paginator(self._http, per_page=per_page, limit=limit)

    def for_category(self, category_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Section]":
        """Get paginated list of sections in a specific category.

        Args:
            category_id: The category's ID
            per_page: Number of sections per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through category's sections
        """
        return ZendeskPaginator.create_sections_paginator(
            self._http, per_page=per_page, category_id=category_id, limit=limit
        )

    async def create(
        self,
        category_id: int,
        name: str,
        *,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Section:
        """Create a new Help Center section.

        Args:
            category_id: Parent category ID (required)
            name: Section name (required)
            description: Section description
            position: Display position relative to other sections

        Returns:
            Created Section object
        """
        section_data: Dict[str, Any] = {"name": name}
        if description is not None:
            section_data["description"] = description
        if position is not None:
            section_data["position"] = position

        response = await self._post(f"categories/{category_id}/sections.json", json={"section": section_data})
        return Section(**response["section"])

    async def update(
        self,
        section_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
        category_id: Optional[int] = None,
        locale: Optional[str] = None,
    ) -> Section:
        """Update a Help Center section.

        Note: name and description are translation properties in Zendesk.
        They are updated via the translations API automatically.

        Args:
            section_id: The section's ID
            name: New section name (updates translation)
            description: New section description (updates translation)
            position: New display position
            category_id: Move section to a different category
            locale: Locale for translation update (defaults to source locale)

        Returns:
            Updated Section object
        """
        # Update position/category_id via section endpoint if specified
        section_data: Dict[str, Any] = {}
        if position is not None:
            section_data["position"] = position
        if category_id is not None:
            section_data["category_id"] = category_id

        if section_data:
            await self._put(f"sections/{section_id}.json", json={"section": section_data})

        # Update name/description via translations endpoint
        if name is not None or description is not None:
            # Get current section to find source locale
            if locale is None:
                current = await self.get(section_id)
                locale = current.source_locale or "en-us"

            translation_data: Dict[str, Any] = {}
            if name is not None:
                translation_data["title"] = name
            if description is not None:
                translation_data["body"] = description

            await self._put(
                f"sections/{section_id}/translations/{locale}.json",
                json={"translation": translation_data},
            )

        # Fetch and return updated section
        return await self.get(section_id)

    async def delete(self, section_id: int, *, force: bool = False) -> bool:
        """Delete a Help Center section.

        WARNING: Deleting a section will also delete ALL articles within
        that section. This action cannot be undone.

        Args:
            section_id: The section's ID
            force: Must be True to confirm cascade deletion of all
                   articles. If False, raises ValueError.

        Returns:
            True if successful

        Raises:
            ValueError: If force is False (safety check)
        """
        if not force:
            raise ValueError(
                "Deleting a section will delete ALL articles within it. "
                "Set force=True to confirm this destructive action."
            )
        await self._delete(f"sections/{section_id}.json")
        return True

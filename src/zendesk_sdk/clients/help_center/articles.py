"""Help Center Articles API client."""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ...models.help_center import Article
from ...pagination import ZendeskPaginator
from ..base import HelpCenterBaseClient

if TYPE_CHECKING:
    from ...config import CacheConfig
    from ...http_client import HTTPClient
    from ...pagination import Paginator


class ArticlesClient(HelpCenterBaseClient):
    """Client for Help Center Articles API.

    Example:
        async with ZendeskClient(config) as client:
            # Get an article
            article = await client.help_center.articles.get(12345)

            # List all articles
            paginator = await client.help_center.articles.list()

            # Search articles
            results = await client.help_center.articles.search("password reset")

            # Create an article
            article = await client.help_center.articles.create(
                section_id=67890,
                title="How to Reset Password",
                body="<p>Follow these steps...</p>"
            )
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize ArticlesClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Set up cached methods
        self.get: Callable[[int], Article] = self._create_cached_method(
            self._get_impl,
            maxsize=cache_config.article_maxsize if cache_config else 500,
            ttl=cache_config.article_ttl if cache_config else 900,
        )

    async def _get_impl(self, article_id: int) -> Article:
        """Get a specific Help Center article by ID.

        Results are cached based on cache configuration.

        Args:
            article_id: The article's ID

        Returns:
            Article object
        """
        response = await self._get(f"articles/{article_id}.json")
        return Article(**response["article"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Article]":
        """Get paginated list of all Help Center articles.

        Args:
            per_page: Number of articles per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all articles
        """
        return ZendeskPaginator.create_articles_paginator(self._http, per_page=per_page, limit=limit)

    def for_section(self, section_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Article]":
        """Get paginated list of articles in a specific section.

        Args:
            section_id: The section's ID
            per_page: Number of articles per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through section's articles
        """
        return ZendeskPaginator.create_articles_paginator(
            self._http, per_page=per_page, section_id=section_id, limit=limit
        )

    def for_category(self, category_id: int, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Article]":
        """Get paginated list of articles in a specific category.

        This returns all articles across all sections in the category.

        Args:
            category_id: The category's ID
            per_page: Number of articles per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through category's articles
        """
        return ZendeskPaginator.create_articles_paginator(
            self._http, per_page=per_page, category_id=category_id, limit=limit
        )

    async def search(
        self,
        query: str,
        *,
        category_id: Optional[int] = None,
        section_id: Optional[int] = None,
        label_names: Optional[List[str]] = None,
        per_page: int = 25,
    ) -> List[Article]:
        """Search Help Center articles.

        Full-text search across article titles and content.
        Returns articles with matching snippets.

        Args:
            query: Search query string
            category_id: Limit search to a specific category
            section_id: Limit search to a specific section
            label_names: Filter by article labels
            per_page: Number of results per page (max 100, default 25)

        Returns:
            List of Article objects matching the query.
            Each article includes a 'snippet' field with matching
            text highlighted with <em> tags.
        """
        params: Dict[str, Any] = {"query": query, "per_page": per_page}
        if category_id is not None:
            params["category"] = category_id
        if section_id is not None:
            params["section"] = section_id
        if label_names is not None:
            params["label_names"] = ",".join(label_names)

        response = await self._get("articles/search.json", params=params)
        return [Article(**article_data) for article_data in response.get("results", [])]

    async def create(
        self,
        section_id: int,
        title: str,
        *,
        body: Optional[str] = None,
        draft: bool = True,
        promoted: bool = False,
        position: Optional[int] = None,
        permission_group_id: Optional[int] = None,
        user_segment_id: Optional[int] = None,
        label_names: Optional[List[str]] = None,
    ) -> Article:
        """Create a new Help Center article.

        Args:
            section_id: Parent section ID (required)
            title: Article title (required)
            body: Article content in HTML
            draft: If True (default), article is saved as draft.
                   If False, article is published immediately.
            promoted: If True, article is promoted/featured
            position: Display position relative to other articles
            permission_group_id: Permission group for access control
            user_segment_id: User segment for visibility control
            label_names: List of labels for the article

        Returns:
            Created Article object
        """
        article_data: Dict[str, Any] = {
            "title": title,
            "draft": draft,
            "promoted": promoted,
            "user_segment_id": user_segment_id,
        }
        if body is not None:
            article_data["body"] = body
        if position is not None:
            article_data["position"] = position
        if permission_group_id is not None:
            article_data["permission_group_id"] = permission_group_id
        if label_names is not None:
            article_data["label_names"] = label_names

        response = await self._post(f"sections/{section_id}/articles.json", json={"article": article_data})
        return Article(**response["article"])

    async def update(
        self,
        article_id: int,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        draft: Optional[bool] = None,
        promoted: Optional[bool] = None,
        position: Optional[int] = None,
        section_id: Optional[int] = None,
        permission_group_id: Optional[int] = None,
        user_segment_id: Optional[int] = None,
        label_names: Optional[List[str]] = None,
        locale: Optional[str] = None,
    ) -> Article:
        """Update a Help Center article.

        Note: title and body are translation properties in Zendesk.
        They are updated via the translations API automatically.

        Args:
            article_id: The article's ID
            title: New article title (updates translation)
            body: New article content in HTML (updates translation)
            draft: Change draft/published status
            promoted: Change promoted status
            position: New display position
            section_id: Move article to a different section
            permission_group_id: Update permission group
            user_segment_id: Update user segment
            label_names: Update article labels
            locale: Locale for translation update (defaults to source locale)

        Returns:
            Updated Article object
        """
        # Update article properties via article endpoint
        article_data: Dict[str, Any] = {}
        if draft is not None:
            article_data["draft"] = draft
        if promoted is not None:
            article_data["promoted"] = promoted
        if position is not None:
            article_data["position"] = position
        if section_id is not None:
            article_data["section_id"] = section_id
        if permission_group_id is not None:
            article_data["permission_group_id"] = permission_group_id
        if user_segment_id is not None:
            article_data["user_segment_id"] = user_segment_id
        if label_names is not None:
            article_data["label_names"] = label_names

        if article_data:
            await self._put(f"articles/{article_id}.json", json={"article": article_data})

        # Update title/body via translations endpoint
        if title is not None or body is not None:
            # Get current article to find source locale
            if locale is None:
                current = await self.get(article_id)
                locale = current.source_locale or "en-us"

            translation_data: Dict[str, Any] = {}
            if title is not None:
                translation_data["title"] = title
            if body is not None:
                translation_data["body"] = body

            await self._put(
                f"articles/{article_id}/translations/{locale}.json",
                json={"translation": translation_data},
            )

        # Fetch and return updated article
        return await self.get(article_id)

    async def delete(self, article_id: int) -> bool:
        """Delete a Help Center article.

        Note: Articles are "archived" in Zendesk and can be restored
        via the Help Center admin UI.

        Args:
            article_id: The article's ID

        Returns:
            True if successful
        """
        await self._delete(f"articles/{article_id}.json")
        return True

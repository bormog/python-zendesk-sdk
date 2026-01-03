"""Help Center API client for Zendesk."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .models.help_center import Article, Category, Section
from .pagination import ZendeskPaginator

if TYPE_CHECKING:
    from .http_client import HTTPClient
    from .pagination import Paginator


class HelpCenterClient:
    """Client for Zendesk Help Center API.

    This client provides access to Help Center resources including
    categories, sections, and articles.

    Help Center has a hierarchical structure:
    - Categories contain Sections
    - Sections contain Articles

    Example:
        async with ZendeskClient(config) as client:
            # Get all categories
            paginator = await client.help_center.get_categories()
            async for category_data in paginator:
                print(category_data["name"])

            # Search articles
            articles = await client.help_center.search_articles("troubleshooting")
            for article in articles:
                print(article.title)
    """

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize Help Center client.

        Args:
            http_client: Shared HTTP client instance from main ZendeskClient
        """
        self._http_client = http_client

    async def _get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request to Help Center API.

        Automatically prepends 'help_center/' to the path.
        """
        return await self._http_client.get(f"help_center/{path}", **kwargs)

    async def _post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make POST request to Help Center API."""
        return await self._http_client.post(f"help_center/{path}", **kwargs)

    async def _put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make PUT request to Help Center API."""
        return await self._http_client.put(f"help_center/{path}", **kwargs)

    async def _delete(self, path: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Make DELETE request to Help Center API."""
        return await self._http_client.delete(f"help_center/{path}", **kwargs)

    # ==================== Categories ====================

    async def get_categories(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of Help Center categories.

        Args:
            per_page: Number of categories per page (max 100)

        Returns:
            Paginator for iterating through all categories

        Example:
            paginator = await client.help_center.get_categories()
            async for category_data in paginator:
                category = Category(**category_data)
                print(category.name)
        """
        return ZendeskPaginator.create_categories_paginator(self._http_client, per_page=per_page)

    async def get_category(self, category_id: int) -> Category:
        """Get a specific Help Center category by ID.

        Args:
            category_id: The category's ID

        Returns:
            Category object
        """
        response = await self._get(f"categories/{category_id}.json")
        return Category(**response["category"])

    async def create_category(
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

    async def update_category(
        self,
        category_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Category:
        """Update a Help Center category.

        Args:
            category_id: The category's ID
            name: New category name
            description: New category description
            position: New display position

        Returns:
            Updated Category object
        """
        category_data: Dict[str, Any] = {}
        if name is not None:
            category_data["name"] = name
        if description is not None:
            category_data["description"] = description
        if position is not None:
            category_data["position"] = position

        response = await self._put(f"categories/{category_id}.json", json={"category": category_data})
        return Category(**response["category"])

    async def delete_category(self, category_id: int, *, force: bool = False) -> bool:
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

        Example:
            # Delete category and all its contents
            await client.help_center.delete_category(123, force=True)
        """
        if not force:
            raise ValueError(
                "Deleting a category will delete ALL sections and articles within it. "
                "Set force=True to confirm this destructive action."
            )
        await self._delete(f"categories/{category_id}.json")
        return True

    # ==================== Sections ====================

    async def get_sections(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of all Help Center sections.

        Args:
            per_page: Number of sections per page (max 100)

        Returns:
            Paginator for iterating through all sections
        """
        return ZendeskPaginator.create_sections_paginator(self._http_client, per_page=per_page)

    async def get_category_sections(self, category_id: int, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of sections in a specific category.

        Args:
            category_id: The category's ID
            per_page: Number of sections per page (max 100)

        Returns:
            Paginator for iterating through category's sections
        """
        return ZendeskPaginator.create_sections_paginator(self._http_client, per_page=per_page, category_id=category_id)

    async def get_section(self, section_id: int) -> Section:
        """Get a specific Help Center section by ID.

        Args:
            section_id: The section's ID

        Returns:
            Section object
        """
        response = await self._get(f"sections/{section_id}.json")
        return Section(**response["section"])

    async def create_section(
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

    async def update_section(
        self,
        section_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> Section:
        """Update a Help Center section.

        Args:
            section_id: The section's ID
            name: New section name
            description: New section description
            position: New display position
            category_id: Move section to a different category

        Returns:
            Updated Section object
        """
        section_data: Dict[str, Any] = {}
        if name is not None:
            section_data["name"] = name
        if description is not None:
            section_data["description"] = description
        if position is not None:
            section_data["position"] = position
        if category_id is not None:
            section_data["category_id"] = category_id

        response = await self._put(f"sections/{section_id}.json", json={"section": section_data})
        return Section(**response["section"])

    async def delete_section(self, section_id: int, *, force: bool = False) -> bool:
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

        Example:
            # Delete section and all its articles
            await client.help_center.delete_section(456, force=True)
        """
        if not force:
            raise ValueError(
                "Deleting a section will delete ALL articles within it. "
                "Set force=True to confirm this destructive action."
            )
        await self._delete(f"sections/{section_id}.json")
        return True

    # ==================== Articles ====================

    async def get_articles(self, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of all Help Center articles.

        Args:
            per_page: Number of articles per page (max 100)

        Returns:
            Paginator for iterating through all articles
        """
        return ZendeskPaginator.create_articles_paginator(self._http_client, per_page=per_page)

    async def get_section_articles(self, section_id: int, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of articles in a specific section.

        Args:
            section_id: The section's ID
            per_page: Number of articles per page (max 100)

        Returns:
            Paginator for iterating through section's articles
        """
        return ZendeskPaginator.create_articles_paginator(self._http_client, per_page=per_page, section_id=section_id)

    async def get_category_articles(self, category_id: int, per_page: int = 100) -> "Paginator[Dict[str, Any]]":
        """Get paginated list of articles in a specific category.

        This returns all articles across all sections in the category.

        Args:
            category_id: The category's ID
            per_page: Number of articles per page (max 100)

        Returns:
            Paginator for iterating through category's articles
        """
        return ZendeskPaginator.create_articles_paginator(self._http_client, per_page=per_page, category_id=category_id)

    async def get_article(self, article_id: int) -> Article:
        """Get a specific Help Center article by ID.

        Args:
            article_id: The article's ID

        Returns:
            Article object
        """
        response = await self._get(f"articles/{article_id}.json")
        return Article(**response["article"])

    async def create_article(
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

        Example:
            article = await client.help_center.create_article(
                section_id=123,
                title="How to Get Started",
                body="<h1>Welcome</h1><p>This guide will help you...</p>",
                draft=False  # Publish immediately
            )
        """
        article_data: Dict[str, Any] = {
            "title": title,
            "draft": draft,
            "promoted": promoted,
            # user_segment_id must be explicitly set (None = visible to everyone)
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

    async def update_article(
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
    ) -> Article:
        """Update a Help Center article.

        Args:
            article_id: The article's ID
            title: New article title
            body: New article content in HTML
            draft: Change draft/published status
            promoted: Change promoted status
            position: New display position
            section_id: Move article to a different section
            permission_group_id: Update permission group
            user_segment_id: Update user segment
            label_names: Update article labels

        Returns:
            Updated Article object
        """
        article_data: Dict[str, Any] = {}
        if title is not None:
            article_data["title"] = title
        if body is not None:
            article_data["body"] = body
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

        response = await self._put(f"articles/{article_id}.json", json={"article": article_data})
        return Article(**response["article"])

    async def delete_article(self, article_id: int) -> bool:
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

    async def search_articles(
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

        Example:
            results = await client.help_center.search_articles(
                "password reset",
                category_id=123
            )
            for article in results:
                print(f"{article.title}")
                print(f"Snippet: {article.snippet}")
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

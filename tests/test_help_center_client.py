"""Tests for Help Center client functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zendesk_sdk import Article, Category, HelpCenterClient, Section, ZendeskClient, ZendeskConfig


class TestHelpCenterModels:
    """Test Help Center model classes."""

    def test_category_model(self):
        """Test Category model creation."""
        data = {
            "id": 123,
            "name": "Test Category",
            "description": "Test description",
            "position": 1,
            "url": "https://example.zendesk.com/api/v2/help_center/categories/123.json",
            "html_url": "https://example.zendesk.com/hc/en-us/categories/123",
        }
        category = Category(**data)
        assert category.id == 123
        assert category.name == "Test Category"
        assert category.description == "Test description"
        assert category.position == 1

    def test_section_model(self):
        """Test Section model creation."""
        data = {
            "id": 456,
            "name": "Test Section",
            "description": "Test section description",
            "category_id": 123,
            "position": 2,
        }
        section = Section(**data)
        assert section.id == 456
        assert section.name == "Test Section"
        assert section.category_id == 123
        assert section.position == 2

    def test_article_model(self):
        """Test Article model creation."""
        data = {
            "id": 789,
            "title": "Test Article",
            "body": "<h1>Test</h1><p>Content</p>",
            "section_id": 456,
            "author_id": 1,
            "draft": False,
            "promoted": True,
            "vote_sum": 10,
            "vote_count": 15,
            "label_names": ["help", "guide"],
        }
        article = Article(**data)
        assert article.id == 789
        assert article.title == "Test Article"
        assert article.body == "<h1>Test</h1><p>Content</p>"
        assert article.section_id == 456
        assert article.draft is False
        assert article.promoted is True
        assert article.label_names == ["help", "guide"]

    def test_article_search_fields(self):
        """Test Article model with search-specific fields."""
        data = {
            "id": 789,
            "title": "Password Reset Guide",
            "result_type": "article",
            "snippet": "How to <em>reset</em> your <em>password</em>...",
        }
        article = Article(**data)
        assert article.result_type == "article"
        assert article.snippet == "How to <em>reset</em> your <em>password</em>..."


class TestHelpCenterClientAccess:
    """Test accessing Help Center client from main client."""

    def test_help_center_property_exists(self):
        """Test that help_center property exists on ZendeskClient."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="token")
        client = ZendeskClient(config)
        assert hasattr(client, "help_center")

    def test_help_center_returns_client(self):
        """Test that help_center property returns HelpCenterClient."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="token")
        client = ZendeskClient(config)
        assert isinstance(client.help_center, HelpCenterClient)

    def test_help_center_is_cached(self):
        """Test that help_center returns the same instance."""
        config = ZendeskConfig(subdomain="test", email="test@example.com", token="token")
        client = ZendeskClient(config)
        hc1 = client.help_center
        hc2 = client.help_center
        assert hc1 is hc2


class TestHelpCenterCategories:
    """Test Help Center category operations."""

    def get_mock_http_client(self):
        """Create a mock HTTP client."""
        mock = MagicMock()
        mock.get = AsyncMock()
        mock.post = AsyncMock()
        mock.put = AsyncMock()
        mock.delete = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_category(self):
        """Test get_category method."""
        mock_http = self.get_mock_http_client()
        mock_http.get.return_value = {"category": {"id": 123, "name": "Test Category"}}

        client = HelpCenterClient(mock_http)
        category = await client.get_category(123)

        assert category.id == 123
        assert category.name == "Test Category"
        mock_http.get.assert_called_once_with("help_center/categories/123.json")

    @pytest.mark.asyncio
    async def test_create_category(self):
        """Test create_category method."""
        mock_http = self.get_mock_http_client()
        mock_http.post.return_value = {"category": {"id": 123, "name": "New Category", "description": "Desc"}}

        client = HelpCenterClient(mock_http)
        category = await client.create_category(name="New Category", description="Desc", position=1)

        assert category.id == 123
        assert category.name == "New Category"
        mock_http.post.assert_called_once_with(
            "help_center/categories.json",
            json={"category": {"name": "New Category", "description": "Desc", "position": 1}},
        )

    @pytest.mark.asyncio
    async def test_update_category(self):
        """Test update_category method."""
        mock_http = self.get_mock_http_client()
        mock_http.put.return_value = {"category": {"id": 123, "name": "Updated Category"}}

        client = HelpCenterClient(mock_http)
        category = await client.update_category(123, name="Updated Category")

        assert category.name == "Updated Category"
        mock_http.put.assert_called_once_with(
            "help_center/categories/123.json",
            json={"category": {"name": "Updated Category"}},
        )

    @pytest.mark.asyncio
    async def test_delete_category_requires_force(self):
        """Test delete_category raises without force=True."""
        mock_http = self.get_mock_http_client()
        client = HelpCenterClient(mock_http)

        with pytest.raises(ValueError, match="force=True"):
            await client.delete_category(123)

    @pytest.mark.asyncio
    async def test_delete_category_with_force(self):
        """Test delete_category with force=True."""
        mock_http = self.get_mock_http_client()
        mock_http.delete.return_value = None

        client = HelpCenterClient(mock_http)
        result = await client.delete_category(123, force=True)

        assert result is True
        mock_http.delete.assert_called_once_with("help_center/categories/123.json")


class TestHelpCenterSections:
    """Test Help Center section operations."""

    def get_mock_http_client(self):
        """Create a mock HTTP client."""
        mock = MagicMock()
        mock.get = AsyncMock()
        mock.post = AsyncMock()
        mock.put = AsyncMock()
        mock.delete = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_section(self):
        """Test get_section method."""
        mock_http = self.get_mock_http_client()
        mock_http.get.return_value = {"section": {"id": 456, "name": "Test Section", "category_id": 123}}

        client = HelpCenterClient(mock_http)
        section = await client.get_section(456)

        assert section.id == 456
        assert section.name == "Test Section"
        assert section.category_id == 123
        mock_http.get.assert_called_once_with("help_center/sections/456.json")

    @pytest.mark.asyncio
    async def test_create_section(self):
        """Test create_section method."""
        mock_http = self.get_mock_http_client()
        mock_http.post.return_value = {"section": {"id": 456, "name": "New Section", "category_id": 123}}

        client = HelpCenterClient(mock_http)
        section = await client.create_section(category_id=123, name="New Section", description="Section desc")

        assert section.id == 456
        assert section.name == "New Section"
        mock_http.post.assert_called_once_with(
            "help_center/categories/123/sections.json",
            json={"section": {"name": "New Section", "description": "Section desc"}},
        )

    @pytest.mark.asyncio
    async def test_update_section(self):
        """Test update_section method."""
        mock_http = self.get_mock_http_client()
        mock_http.put.return_value = {"section": {"id": 456, "name": "Updated Section"}}

        client = HelpCenterClient(mock_http)
        section = await client.update_section(456, name="Updated Section")

        assert section.name == "Updated Section"
        mock_http.put.assert_called_once_with(
            "help_center/sections/456.json",
            json={"section": {"name": "Updated Section"}},
        )

    @pytest.mark.asyncio
    async def test_update_section_move_category(self):
        """Test update_section can move to another category."""
        mock_http = self.get_mock_http_client()
        mock_http.put.return_value = {"section": {"id": 456, "category_id": 999}}

        client = HelpCenterClient(mock_http)
        section = await client.update_section(456, category_id=999)

        assert section.category_id == 999
        mock_http.put.assert_called_once_with(
            "help_center/sections/456.json",
            json={"section": {"category_id": 999}},
        )

    @pytest.mark.asyncio
    async def test_delete_section_requires_force(self):
        """Test delete_section raises without force=True."""
        mock_http = self.get_mock_http_client()
        client = HelpCenterClient(mock_http)

        with pytest.raises(ValueError, match="force=True"):
            await client.delete_section(456)

    @pytest.mark.asyncio
    async def test_delete_section_with_force(self):
        """Test delete_section with force=True."""
        mock_http = self.get_mock_http_client()
        mock_http.delete.return_value = None

        client = HelpCenterClient(mock_http)
        result = await client.delete_section(456, force=True)

        assert result is True
        mock_http.delete.assert_called_once_with("help_center/sections/456.json")


class TestHelpCenterArticles:
    """Test Help Center article operations."""

    def get_mock_http_client(self):
        """Create a mock HTTP client."""
        mock = MagicMock()
        mock.get = AsyncMock()
        mock.post = AsyncMock()
        mock.put = AsyncMock()
        mock.delete = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_article(self):
        """Test get_article method."""
        mock_http = self.get_mock_http_client()
        mock_http.get.return_value = {
            "article": {
                "id": 789,
                "title": "Test Article",
                "body": "<p>Content</p>",
                "section_id": 456,
                "draft": False,
            }
        }

        client = HelpCenterClient(mock_http)
        article = await client.get_article(789)

        assert article.id == 789
        assert article.title == "Test Article"
        assert article.body == "<p>Content</p>"
        assert article.draft is False
        mock_http.get.assert_called_once_with("help_center/articles/789.json")

    @pytest.mark.asyncio
    async def test_create_article(self):
        """Test create_article method."""
        mock_http = self.get_mock_http_client()
        mock_http.post.return_value = {
            "article": {
                "id": 789,
                "title": "New Article",
                "body": "<p>Body</p>",
                "section_id": 456,
                "draft": True,
            }
        }

        client = HelpCenterClient(mock_http)
        article = await client.create_article(
            section_id=456,
            title="New Article",
            body="<p>Body</p>",
            draft=True,
        )

        assert article.id == 789
        assert article.title == "New Article"
        assert article.draft is True
        mock_http.post.assert_called_once_with(
            "help_center/sections/456/articles.json",
            json={
                "article": {
                    "title": "New Article",
                    "body": "<p>Body</p>",
                    "draft": True,
                    "promoted": False,
                    "user_segment_id": None,
                }
            },
        )

    @pytest.mark.asyncio
    async def test_create_article_published(self):
        """Test create_article with draft=False (published)."""
        mock_http = self.get_mock_http_client()
        mock_http.post.return_value = {"article": {"id": 789, "title": "Published Article", "draft": False}}

        client = HelpCenterClient(mock_http)
        article = await client.create_article(
            section_id=456,
            title="Published Article",
            body="<p>Content</p>",
            draft=False,
            promoted=True,
        )

        assert article.draft is False
        call_json = mock_http.post.call_args[1]["json"]
        assert call_json["article"]["draft"] is False
        assert call_json["article"]["promoted"] is True

    @pytest.mark.asyncio
    async def test_create_article_with_labels(self):
        """Test create_article with label_names."""
        mock_http = self.get_mock_http_client()
        mock_http.post.return_value = {
            "article": {"id": 789, "title": "Labeled Article", "label_names": ["faq", "help"]}
        }

        client = HelpCenterClient(mock_http)
        article = await client.create_article(
            section_id=456,
            title="Labeled Article",
            label_names=["faq", "help"],
        )

        assert article.label_names == ["faq", "help"]
        call_json = mock_http.post.call_args[1]["json"]
        assert call_json["article"]["label_names"] == ["faq", "help"]

    @pytest.mark.asyncio
    async def test_update_article(self):
        """Test update_article method."""
        mock_http = self.get_mock_http_client()
        mock_http.put.return_value = {"article": {"id": 789, "title": "Updated Title", "body": "<p>New body</p>"}}

        client = HelpCenterClient(mock_http)
        article = await client.update_article(789, title="Updated Title", body="<p>New body</p>")

        assert article.title == "Updated Title"
        assert article.body == "<p>New body</p>"
        mock_http.put.assert_called_once_with(
            "help_center/articles/789.json",
            json={"article": {"title": "Updated Title", "body": "<p>New body</p>"}},
        )

    @pytest.mark.asyncio
    async def test_update_article_move_section(self):
        """Test update_article can move to another section."""
        mock_http = self.get_mock_http_client()
        mock_http.put.return_value = {"article": {"id": 789, "section_id": 999}}

        client = HelpCenterClient(mock_http)
        article = await client.update_article(789, section_id=999)

        assert article.section_id == 999

    @pytest.mark.asyncio
    async def test_delete_article(self):
        """Test delete_article method (no force needed)."""
        mock_http = self.get_mock_http_client()
        mock_http.delete.return_value = None

        client = HelpCenterClient(mock_http)
        result = await client.delete_article(789)

        assert result is True
        mock_http.delete.assert_called_once_with("help_center/articles/789.json")

    @pytest.mark.asyncio
    async def test_search_articles(self):
        """Test search_articles method."""
        mock_http = self.get_mock_http_client()
        mock_http.get.return_value = {
            "results": [
                {
                    "id": 789,
                    "title": "Password Reset",
                    "result_type": "article",
                    "snippet": "How to <em>reset</em> your password",
                },
                {
                    "id": 790,
                    "title": "Account Recovery",
                    "result_type": "article",
                    "snippet": "Recover your account",
                },
            ]
        }

        client = HelpCenterClient(mock_http)
        articles = await client.search_articles("password reset")

        assert len(articles) == 2
        assert articles[0].title == "Password Reset"
        assert articles[0].snippet == "How to <em>reset</em> your password"
        assert articles[1].title == "Account Recovery"
        mock_http.get.assert_called_once_with(
            "help_center/articles/search.json",
            params={"query": "password reset", "per_page": 25},
        )

    @pytest.mark.asyncio
    async def test_search_articles_with_filters(self):
        """Test search_articles with category and section filters."""
        mock_http = self.get_mock_http_client()
        mock_http.get.return_value = {"results": []}

        client = HelpCenterClient(mock_http)
        await client.search_articles(
            "test",
            category_id=123,
            section_id=456,
            label_names=["faq", "help"],
            per_page=50,
        )

        mock_http.get.assert_called_once_with(
            "help_center/articles/search.json",
            params={
                "query": "test",
                "per_page": 50,
                "category": 123,
                "section": 456,
                "label_names": "faq,help",
            },
        )


class TestHelpCenterPaginators:
    """Test Help Center pagination factory methods."""

    def test_categories_paginator_path(self):
        """Test categories paginator uses correct path."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_categories_paginator(mock_http, per_page=50)

        assert paginator.path == "help_center/categories.json"
        assert paginator.per_page == 50

    def test_sections_paginator_path(self):
        """Test sections paginator uses correct path."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_sections_paginator(mock_http)

        assert paginator.path == "help_center/sections.json"

    def test_sections_paginator_with_category(self):
        """Test sections paginator with category filter."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_sections_paginator(mock_http, category_id=123)

        assert paginator.path == "help_center/categories/123/sections.json"

    def test_articles_paginator_path(self):
        """Test articles paginator uses correct path."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_articles_paginator(mock_http)

        assert paginator.path == "help_center/articles.json"

    def test_articles_paginator_with_section(self):
        """Test articles paginator with section filter."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_articles_paginator(mock_http, section_id=456)

        assert paginator.path == "help_center/sections/456/articles.json"

    def test_articles_paginator_with_category(self):
        """Test articles paginator with category filter."""
        from zendesk_sdk.pagination import ZendeskPaginator

        mock_http = MagicMock()
        paginator = ZendeskPaginator.create_articles_paginator(mock_http, category_id=123)

        assert paginator.path == "help_center/categories/123/articles.json"


class TestPackageExports:
    """Test that Help Center classes are exported from package."""

    def test_category_export(self):
        """Test Category is exported from zendesk_sdk."""
        from zendesk_sdk import Category

        assert Category is not None

    def test_section_export(self):
        """Test Section is exported from zendesk_sdk."""
        from zendesk_sdk import Section

        assert Section is not None

    def test_article_export(self):
        """Test Article is exported from zendesk_sdk."""
        from zendesk_sdk import Article

        assert Article is not None

    def test_help_center_client_export(self):
        """Test HelpCenterClient is exported from zendesk_sdk."""
        from zendesk_sdk import HelpCenterClient

        assert HelpCenterClient is not None

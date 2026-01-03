"""Tests for Help Center clients."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zendesk_sdk.clients.help_center import (
    ArticlesClient,
    CategoriesClient,
    HelpCenterClient,
    SectionsClient,
)
from zendesk_sdk.models.help_center import Article, Category, Section


class TestHelpCenterClient:
    """Test cases for HelpCenterClient namespace."""

    def get_client(self):
        """Create a mock HelpCenterClient."""
        mock_http = MagicMock()
        return HelpCenterClient(mock_http)

    def test_categories_accessor(self):
        """Test categories accessor returns CategoriesClient."""
        client = self.get_client()
        assert isinstance(client.categories, CategoriesClient)

    def test_sections_accessor(self):
        """Test sections accessor returns SectionsClient."""
        client = self.get_client()
        assert isinstance(client.sections, SectionsClient)

    def test_articles_accessor(self):
        """Test articles accessor returns ArticlesClient."""
        client = self.get_client()
        assert isinstance(client.articles, ArticlesClient)


class TestCategoriesClient:
    """Test cases for CategoriesClient."""

    def get_client(self):
        """Create a mock CategoriesClient."""
        mock_http = MagicMock()
        return CategoriesClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get category by ID."""
        client = self.get_client()
        category_data = {
            "category": {
                "id": 123,
                "name": "Test Category",
                "description": "Test description",
                "position": 1,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = category_data

            result = await client.get(123)

            assert isinstance(result, Category)
            assert result.id == 123
            assert result.name == "Test Category"
            mock_get.assert_called_once_with("categories/123.json")

    @pytest.mark.asyncio
    async def test_create(self):
        """Test create category."""
        client = self.get_client()
        category_data = {
            "category": {
                "id": 123,
                "name": "New Category",
                "description": "New description",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = category_data

            result = await client.create("New Category", description="New description")

            assert isinstance(result, Category)
            assert result.name == "New Category"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update(self):
        """Test update category."""
        client = self.get_client()
        category_data = {
            "category": {
                "id": 123,
                "name": "Updated Category",
                "source_locale": "en-us",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with (
            patch.object(client, "_put", new_callable=AsyncMock) as mock_put,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_get.return_value = category_data
            mock_put.return_value = {}

            result = await client.update(123, name="Updated Category")

            assert isinstance(result, Category)
            assert result.name == "Updated Category"
            # Verify translation update was called
            assert mock_put.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_without_force(self):
        """Test delete category without force raises error."""
        client = self.get_client()

        with pytest.raises(ValueError, match="force=True"):
            await client.delete(123)

    @pytest.mark.asyncio
    async def test_delete_with_force(self):
        """Test delete category with force."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete(123, force=True)

            assert result is True
            mock_delete.assert_called_once_with("categories/123.json")


class TestSectionsClient:
    """Test cases for SectionsClient."""

    def get_client(self):
        """Create a mock SectionsClient."""
        mock_http = MagicMock()
        return SectionsClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get section by ID."""
        client = self.get_client()
        section_data = {
            "section": {
                "id": 456,
                "name": "Test Section",
                "category_id": 123,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = section_data

            result = await client.get(456)

            assert isinstance(result, Section)
            assert result.id == 456
            assert result.category_id == 123
            mock_get.assert_called_once_with("sections/456.json")

    @pytest.mark.asyncio
    async def test_create(self):
        """Test create section."""
        client = self.get_client()
        section_data = {
            "section": {
                "id": 456,
                "name": "New Section",
                "category_id": 123,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = section_data

            result = await client.create(123, "New Section")

            assert isinstance(result, Section)
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update(self):
        """Test update section."""
        client = self.get_client()
        section_data = {
            "section": {
                "id": 456,
                "name": "Updated Section",
                "category_id": 123,
                "source_locale": "en-us",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with (
            patch.object(client, "_put", new_callable=AsyncMock) as mock_put,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_get.return_value = section_data
            mock_put.return_value = {}

            result = await client.update(456, name="Updated Section")

            assert isinstance(result, Section)
            assert result.name == "Updated Section"

    @pytest.mark.asyncio
    async def test_delete_without_force(self):
        """Test delete section without force raises error."""
        client = self.get_client()

        with pytest.raises(ValueError, match="force=True"):
            await client.delete(456)

    @pytest.mark.asyncio
    async def test_delete_with_force(self):
        """Test delete section with force."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete(456, force=True)

            assert result is True


class TestArticlesClient:
    """Test cases for ArticlesClient."""

    def get_client(self):
        """Create a mock ArticlesClient."""
        mock_http = MagicMock()
        return ArticlesClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get article by ID."""
        client = self.get_client()
        article_data = {
            "article": {
                "id": 789,
                "title": "Test Article",
                "body": "<p>Content</p>",
                "section_id": 456,
                "draft": False,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = article_data

            result = await client.get(789)

            assert isinstance(result, Article)
            assert result.id == 789
            assert result.title == "Test Article"
            mock_get.assert_called_once_with("articles/789.json")

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search articles."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 789,
                    "title": "Password Reset",
                    "snippet": "How to reset your <em>password</em>",
                    "section_id": 456,
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.search("password")

            assert len(result) == 1
            assert isinstance(result[0], Article)
            assert result[0].title == "Password Reset"
            mock_get.assert_called_once_with("articles/search.json", params={"query": "password", "per_page": 25})

    @pytest.mark.asyncio
    async def test_create(self):
        """Test create article."""
        client = self.get_client()
        article_data = {
            "article": {
                "id": 789,
                "title": "New Article",
                "body": "<p>Content</p>",
                "section_id": 456,
                "draft": True,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = article_data

            result = await client.create(456, "New Article", body="<p>Content</p>")

            assert isinstance(result, Article)
            assert result.draft is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_published(self):
        """Test create published article."""
        client = self.get_client()
        article_data = {
            "article": {
                "id": 789,
                "title": "Published Article",
                "draft": False,
                "section_id": 456,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = article_data

            result = await client.create(456, "Published Article", draft=False)

            assert result.draft is False

    @pytest.mark.asyncio
    async def test_update(self):
        """Test update article."""
        client = self.get_client()
        article_data = {
            "article": {
                "id": 789,
                "title": "Updated Article",
                "section_id": 456,
                "source_locale": "en-us",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with (
            patch.object(client, "_put", new_callable=AsyncMock) as mock_put,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_get.return_value = article_data
            mock_put.return_value = {}

            result = await client.update(789, title="Updated Article")

            assert isinstance(result, Article)
            assert result.title == "Updated Article"

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete article."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete(789)

            assert result is True
            mock_delete.assert_called_once_with("articles/789.json")

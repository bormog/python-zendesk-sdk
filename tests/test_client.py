"""Tests for ZendeskClient."""

from unittest.mock import AsyncMock, patch

import pytest

from zendesk_sdk.client import ZendeskClient
from zendesk_sdk.config import ZendeskConfig


class TestZendeskClient:
    """Test cases for ZendeskClient class."""

    def get_client(self):
        """Helper method to create a test client."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )
        return ZendeskClient(config)

    def test_http_client_property(self):
        """Test HTTP client property creates client lazily."""
        client = self.get_client()
        assert client._http_client is None

        # Access should create the client
        http_client = client.http_client
        assert http_client is not None
        assert client._http_client is http_client

        # Second access should return same instance
        http_client2 = client.http_client
        assert http_client2 is http_client

    @pytest.mark.asyncio
    async def test_close_method_no_http_client(self):
        """Test close method when no HTTP client exists."""
        client = self.get_client()
        # Don't access http_client property so it remains None
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager_with_close(self):
        """Test context manager calls close on exit."""
        client = self.get_client()

        with patch.object(client, "close", new_callable=AsyncMock) as mock_close:
            async with client as ctx_client:
                assert ctx_client is client

            mock_close.assert_called_once()

    def test_repr(self):
        """Test __repr__ method."""
        client = self.get_client()
        assert repr(client) == "ZendeskClient(subdomain='test')"

    # Namespace access tests

    def test_users_namespace(self):
        """Test users namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import UsersClient

        assert isinstance(client.users, UsersClient)
        # Should return same instance
        assert client.users is client.users

    def test_organizations_namespace(self):
        """Test organizations namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import OrganizationsClient

        assert isinstance(client.organizations, OrganizationsClient)

    def test_tickets_namespace(self):
        """Test tickets namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import TicketsClient

        assert isinstance(client.tickets, TicketsClient)

    def test_tickets_comments_namespace(self):
        """Test tickets.comments namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import CommentsClient

        assert isinstance(client.tickets.comments, CommentsClient)

    def test_tickets_tags_namespace(self):
        """Test tickets.tags namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import TagsClient

        assert isinstance(client.tickets.tags, TagsClient)

    def test_attachments_namespace(self):
        """Test attachments namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import AttachmentsClient

        assert isinstance(client.attachments, AttachmentsClient)

    def test_search_namespace(self):
        """Test search namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import SearchClient

        assert isinstance(client.search, SearchClient)

    def test_help_center_namespace(self):
        """Test help_center namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import HelpCenterClient

        assert isinstance(client.help_center, HelpCenterClient)

    def test_help_center_categories_namespace(self):
        """Test help_center.categories namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import CategoriesClient

        assert isinstance(client.help_center.categories, CategoriesClient)

    def test_help_center_sections_namespace(self):
        """Test help_center.sections namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import SectionsClient

        assert isinstance(client.help_center.sections, SectionsClient)

    def test_help_center_articles_namespace(self):
        """Test help_center.articles namespace is accessible."""
        client = self.get_client()
        from zendesk_sdk.clients import ArticlesClient

        assert isinstance(client.help_center.articles, ArticlesClient)


class TestZendeskClientHTTPMethods:
    """Test cases for ZendeskClient low-level HTTP methods."""

    def get_client(self):
        """Helper method to create a test client."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )
        return ZendeskClient(config)

    @pytest.mark.asyncio
    async def test_get_method(self):
        """Test get method."""
        client = self.get_client()
        mock_response = {"users": []}

        with patch.object(client.http_client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get("users.json")

            assert result == mock_response
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_method(self):
        """Test post method."""
        client = self.get_client()
        mock_response = {"user": {"id": 123, "name": "New User"}}

        with patch.object(client.http_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.post("users.json", json={"user": {"name": "New User"}})

            assert result == mock_response
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_method(self):
        """Test put method."""
        client = self.get_client()
        mock_response = {"user": {"id": 123, "name": "Updated User"}}

        with patch.object(client.http_client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response

            result = await client.put("users/123.json", json={"user": {"name": "Updated User"}})

            assert result == mock_response
            mock_put.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_method(self):
        """Test delete method."""
        client = self.get_client()

        with patch.object(client.http_client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete("users/123.json")

            assert result is None
            mock_delete.assert_called_once()

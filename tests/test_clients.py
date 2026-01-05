"""Tests for resource clients (users, tickets, organizations, etc.)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zendesk_sdk.clients import (
    AttachmentsClient,
    CommentsClient,
    OrganizationsClient,
    SearchClient,
    TagsClient,
    TicketsClient,
    UsersClient,
)
from zendesk_sdk.models import Comment, Organization, Ticket, User


class TestUsersClient:
    """Test cases for UsersClient."""

    def get_client(self):
        """Create a mock UsersClient."""
        mock_http = MagicMock()
        return UsersClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get user by ID."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Test User",
                "email": "test@example.com",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_data

            result = await client.get(123)

            assert isinstance(result, User)
            assert result.id == 123
            assert result.name == "Test User"
            mock_get.assert_called_once_with("users/123.json")

    @pytest.mark.asyncio
    async def test_by_email(self):
        """Test get user by email."""
        client = self.get_client()
        search_data = {
            "users": [
                {
                    "id": 123,
                    "name": "Test User",
                    "email": "test@example.com",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.by_email("test@example.com")

            assert isinstance(result, User)
            assert result.email == "test@example.com"
            mock_get.assert_called_once_with("users/search.json", params={"query": "test@example.com"})

    @pytest.mark.asyncio
    async def test_by_email_not_found(self):
        """Test get user by email when not found."""
        client = self.get_client()

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"users": []}

            result = await client.by_email("notfound@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_many(self):
        """Test get multiple users."""
        client = self.get_client()
        users_data = {
            "users": [
                {"id": 1, "name": "User1", "email": "u1@example.com", "created_at": "2023-01-01T00:00:00Z"},
                {"id": 2, "name": "User2", "email": "u2@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = users_data

            result = await client.get_many([1, 2])

            assert len(result) == 2
            assert 1 in result
            assert 2 in result

    @pytest.mark.asyncio
    async def test_get_many_empty(self):
        """Test get_many with empty list."""
        client = self.get_client()

        result = await client.get_many([])

        assert result == {}


class TestOrganizationsClient:
    """Test cases for OrganizationsClient."""

    def get_client(self):
        """Create a mock OrganizationsClient."""
        mock_http = MagicMock()
        return OrganizationsClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get organization by ID."""
        client = self.get_client()
        org_data = {
            "organization": {
                "id": 456,
                "name": "Test Org",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = org_data

            result = await client.get(456)

            assert isinstance(result, Organization)
            assert result.id == 456
            assert result.name == "Test Org"
            mock_get.assert_called_once_with("organizations/456.json")


class TestTicketsClient:
    """Test cases for TicketsClient."""

    def get_client(self):
        """Create a mock TicketsClient."""
        mock_http = MagicMock()
        return TicketsClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get ticket by ID."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = ticket_data

            result = await client.get(789)

            assert isinstance(result, Ticket)
            assert result.id == 789
            assert result.subject == "Test Ticket"
            mock_get.assert_called_once_with("tickets/789.json")

    @pytest.mark.asyncio
    async def test_for_user(self):
        """Test get tickets for user returns paginator."""
        from zendesk_sdk.pagination import OffsetPaginator

        client = self.get_client()
        tickets_data = {
            "tickets": [
                {"id": 789, "subject": "User Ticket", "status": "open", "created_at": "2023-01-01T00:00:00Z"},
            ],
            "count": 1,
        }

        # for_user now returns a paginator (sync method)
        paginator = client.for_user(123)
        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "users/123/tickets/requested.json"

        # Test that paginator extracts tickets correctly
        client._http.get = AsyncMock(return_value=tickets_data)
        result = await paginator.get_page()

        assert len(result) == 1
        assert isinstance(result[0], Ticket)
        assert result[0].id == 789

    @pytest.mark.asyncio
    async def test_for_organization(self):
        """Test get tickets for organization returns paginator."""
        from zendesk_sdk.pagination import OffsetPaginator

        client = self.get_client()
        tickets_data = {
            "tickets": [
                {"id": 789, "subject": "Org Ticket", "status": "open", "created_at": "2023-01-01T00:00:00Z"},
            ],
            "count": 1,
        }

        # for_organization now returns a paginator (sync method)
        paginator = client.for_organization(456)
        assert isinstance(paginator, OffsetPaginator)
        assert paginator.path == "organizations/456/tickets.json"

        # Test that paginator extracts tickets correctly
        client._http.get = AsyncMock(return_value=tickets_data)
        result = await paginator.get_page()

        assert len(result) == 1
        assert isinstance(result[0], Ticket)
        assert result[0].id == 789

    def test_comments_accessor(self):
        """Test comments accessor returns CommentsClient."""
        client = self.get_client()
        assert isinstance(client.comments, CommentsClient)

    def test_tags_accessor(self):
        """Test tags accessor returns TagsClient."""
        client = self.get_client()
        assert isinstance(client.tags, TagsClient)


class TestCommentsClient:
    """Test cases for CommentsClient."""

    def get_client(self):
        """Create a mock CommentsClient."""
        mock_http = MagicMock()
        return CommentsClient(mock_http)

    @pytest.mark.asyncio
    async def test_list(self):
        """Test list comments returns paginator."""
        client = self.get_client()

        paginator = client.list(789)

        # Should return a paginator, not awaitable
        assert hasattr(paginator, "get_page")
        assert hasattr(paginator, "__aiter__")

    @pytest.mark.asyncio
    async def test_add_private(self):
        """Test add private comment (default)."""
        client = self.get_client()
        ticket_data = {"ticket": {"id": 789, "subject": "Test", "status": "open", "created_at": "2023-01-01T00:00:00Z"}}

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add(789, "Internal note")

            assert isinstance(result, Ticket)
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={"ticket": {"comment": {"body": "Internal note", "public": False}}},
            )

    @pytest.mark.asyncio
    async def test_add_public(self):
        """Test add public comment."""
        client = self.get_client()
        ticket_data = {"ticket": {"id": 789, "subject": "Test", "status": "open", "created_at": "2023-01-01T00:00:00Z"}}

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add(789, "Public reply", public=True)

            assert isinstance(result, Ticket)
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={"ticket": {"comment": {"body": "Public reply", "public": True}}},
            )

    @pytest.mark.asyncio
    async def test_make_private(self):
        """Test make comment private."""
        client = self.get_client()

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await client.make_private(789, 111)

            assert result is True
            mock_put.assert_called_once_with("tickets/789/comments/111/make_private.json")

    @pytest.mark.asyncio
    async def test_redact(self):
        """Test redact comment."""
        client = self.get_client()
        comment_data = {
            "comment": {
                "id": 111,
                "body": "Redacted",
                "author_id": 123,
                "public": True,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = comment_data

            result = await client.redact(789, 111, "secret")

            assert isinstance(result, Comment)
            mock_put.assert_called_once_with(
                "tickets/789/comments/111/redact.json",
                json={"text": "secret"},
            )


class TestTagsClient:
    """Test cases for TagsClient."""

    def get_client(self):
        """Create a mock TagsClient."""
        mock_http = MagicMock()
        return TagsClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get tags."""
        client = self.get_client()

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"tags": ["vip", "urgent"]}

            result = await client.get(789)

            assert result == ["vip", "urgent"]
            mock_get.assert_called_once_with("tickets/789/tags.json")

    @pytest.mark.asyncio
    async def test_add(self):
        """Test add tags."""
        client = self.get_client()

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"tags": ["existing", "new"]}

            result = await client.add(789, ["new"])

            assert result == ["existing", "new"]
            mock_put.assert_called_once_with("tickets/789/tags.json", json={"tags": ["new"]})

    @pytest.mark.asyncio
    async def test_set(self):
        """Test set tags (replace all)."""
        client = self.get_client()

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"tags": ["new1", "new2"]}

            result = await client.set(789, ["new1", "new2"])

            assert result == ["new1", "new2"]
            mock_post.assert_called_once_with("tickets/789/tags.json", json={"tags": ["new1", "new2"]})

    @pytest.mark.asyncio
    async def test_remove(self):
        """Test remove tags."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {"tags": ["remaining"]}

            result = await client.remove(789, ["to_remove"])

            assert result == ["remaining"]
            mock_delete.assert_called_once_with("tickets/789/tags.json", json={"tags": ["to_remove"]})

    @pytest.mark.asyncio
    async def test_remove_empty_response(self):
        """Test remove tags with empty response."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.remove(789, ["to_remove"])

            assert result == []


class TestSearchClient:
    """Test cases for SearchClient."""

    def get_client(self):
        """Create a mock SearchClient."""
        mock_http = MagicMock()
        return SearchClient(mock_http)

    @pytest.mark.asyncio
    async def test_tickets(self):
        """Test search tickets returns async iterator."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 789,
                    "subject": "Found",
                    "status": "open",
                    "result_type": "ticket",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
            "count": 1,
        }

        # Mock the HTTP client's get method (used by paginator)
        client._http.get = AsyncMock(return_value=search_data)

        result = [ticket async for ticket in client.tickets("status:open")]

        assert len(result) == 1
        assert isinstance(result[0], Ticket)

    @pytest.mark.asyncio
    async def test_users(self):
        """Test search users returns async iterator."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 123,
                    "name": "Found",
                    "email": "f@e.com",
                    "result_type": "user",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
            "count": 1,
        }

        client._http.get = AsyncMock(return_value=search_data)

        result = [user async for user in client.users("role:admin")]

        assert len(result) == 1
        assert isinstance(result[0], User)

    @pytest.mark.asyncio
    async def test_organizations(self):
        """Test search organizations returns async iterator."""
        client = self.get_client()
        search_data = {
            "results": [
                {"id": 456, "name": "ACME", "result_type": "organization", "created_at": "2023-01-01T00:00:00Z"}
            ],
            "count": 1,
        }

        client._http.get = AsyncMock(return_value=search_data)

        result = [org async for org in client.organizations("ACME")]

        assert len(result) == 1
        assert isinstance(result[0], Organization)


class TestAttachmentsClient:
    """Test cases for AttachmentsClient."""

    @pytest.mark.asyncio
    async def test_download(self):
        """Test download attachment."""
        from zendesk_sdk.config import ZendeskConfig

        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        mock_http = MagicMock()
        client = AttachmentsClient(mock_http, config)

        test_content = b"file content"

        with patch("zendesk_sdk.clients.attachments.httpx.AsyncClient") as mock_client_class:
            mock_http_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = test_content
            mock_response.raise_for_status = AsyncMock()
            mock_http_client.get.return_value = mock_response
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_http_client

            result = await client.download("https://example.com/file.pdf")

            assert result == test_content

    @pytest.mark.asyncio
    async def test_upload(self):
        """Test upload attachment."""
        from zendesk_sdk.config import ZendeskConfig

        config = ZendeskConfig(subdomain="test", email="test@example.com", token="abc123")
        mock_http = MagicMock()
        client = AttachmentsClient(mock_http, config)

        with patch("zendesk_sdk.clients.attachments.httpx.AsyncClient") as mock_client_class:
            mock_http_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.json = lambda: {"upload": {"token": "token123"}}
            mock_response.raise_for_status = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_http_client

            result = await client.upload(b"data", "file.txt", "text/plain")

            assert result == "token123"

"""Tests for ZendeskClient."""

from unittest.mock import AsyncMock, patch

import pytest

from zendesk_sdk.client import ZendeskClient
from zendesk_sdk.config import ZendeskConfig
from zendesk_sdk.models import Comment, Organization, Ticket, User


class TestZendeskClient:
    """Test cases for ZendeskClient class."""


    def test_http_client_property(self):
        """Test HTTP client property creates client lazily."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )

        client = ZendeskClient(config)
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
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )

        client = ZendeskClient(config)
        # Don't access http_client property so it remains None

        # Should not raise any exceptions
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager_with_close(self):
        """Test context manager calls close on exit."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )

        client = ZendeskClient(config)

        with patch.object(client, "close", new_callable=AsyncMock) as mock_close:
            async with client as ctx_client:
                assert ctx_client is client

            mock_close.assert_called_once()


class TestZendeskClientAPIReadMethods:
    """Test cases for ZendeskClient API read methods."""

    def get_client(self):
        """Helper method to create a test client."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )
        return ZendeskClient(config)

    # Users API tests

    @pytest.mark.asyncio
    async def test_get_users(self):
        """Test get_users method returns paginator."""
        client = self.get_client()

        with patch("zendesk_sdk.client.ZendeskPaginator.create_users_paginator") as mock_create:
            mock_paginator = AsyncMock()
            mock_create.return_value = mock_paginator

            result = await client.get_users(per_page=50)

            assert result == mock_paginator
            mock_create.assert_called_once_with(client.http_client, per_page=50)

    @pytest.mark.asyncio
    async def test_get_user(self):
        """Test get_user method."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Test User",
                "email": "[email protected]",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_data

            result = await client.get_user(123)

            assert isinstance(result, User)
            assert result.id == 123
            assert result.name == "Test User"
            assert result.email == "[email protected]"
            mock_get.assert_called_once_with("users/123.json")

    @pytest.mark.asyncio
    async def test_get_user_by_email(self):
        """Test get_user_by_email method."""
        client = self.get_client()
        search_data = {
            "users": [
                {
                    "id": 123,
                    "name": "Test User",
                    "email": "[email protected]",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.get_user_by_email("[email protected]")

            assert isinstance(result, User)
            assert result.id == 123
            assert result.email == "[email protected]"
            mock_get.assert_called_once_with("users/search.json", params={"query": "[email protected]"})

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """Test get_user_by_email method when user not found."""
        client = self.get_client()
        search_data = {"users": []}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.get_user_by_email("[email protected]")

            assert result is None
            mock_get.assert_called_once_with("users/search.json", params={"query": "[email protected]"})

    # Organizations API tests

    @pytest.mark.asyncio
    async def test_get_organizations(self):
        """Test get_organizations method returns paginator."""
        client = self.get_client()

        with patch("zendesk_sdk.client.ZendeskPaginator.create_organizations_paginator") as mock_create:
            mock_paginator = AsyncMock()
            mock_create.return_value = mock_paginator

            result = await client.get_organizations(per_page=25)

            assert result == mock_paginator
            mock_create.assert_called_once_with(client.http_client, per_page=25)

    @pytest.mark.asyncio
    async def test_get_organization(self):
        """Test get_organization method."""
        client = self.get_client()
        org_data = {
            "organization": {
                "id": 456,
                "name": "Test Org",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = org_data

            result = await client.get_organization(456)

            assert isinstance(result, Organization)
            assert result.id == 456
            assert result.name == "Test Org"
            mock_get.assert_called_once_with("organizations/456.json")

    # Tickets API tests

    @pytest.mark.asyncio
    async def test_get_tickets(self):
        """Test get_tickets method returns paginator."""
        client = self.get_client()

        with patch("zendesk_sdk.client.ZendeskPaginator.create_tickets_paginator") as mock_create:
            mock_paginator = AsyncMock()
            mock_create.return_value = mock_paginator

            result = await client.get_tickets(per_page=75)

            assert result == mock_paginator
            mock_create.assert_called_once_with(client.http_client, per_page=75)

    @pytest.mark.asyncio
    async def test_get_ticket(self):
        """Test get_ticket method."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = ticket_data

            result = await client.get_ticket(789)

            assert isinstance(result, Ticket)
            assert result.id == 789
            assert result.subject == "Test Ticket"
            assert result.status == "open"
            mock_get.assert_called_once_with("tickets/789.json")

    @pytest.mark.asyncio
    async def test_get_user_tickets(self):
        """Test get_user_tickets method."""
        client = self.get_client()
        tickets_data = {
            "tickets": [
                {
                    "id": 789,
                    "subject": "User Ticket 1",
                    "status": "open",
                    "created_at": "2023-01-01T00:00:00Z",
                },
                {
                    "id": 790,
                    "subject": "User Ticket 2",
                    "status": "pending",
                    "created_at": "2023-01-02T00:00:00Z",
                },
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tickets_data

            result = await client.get_user_tickets(123, per_page=50)

            assert len(result) == 2
            assert all(isinstance(ticket, Ticket) for ticket in result)
            assert result[0].id == 789
            assert result[1].id == 790
            mock_get.assert_called_once_with("users/123/tickets/requested.json", params={"per_page": 50})

    @pytest.mark.asyncio
    async def test_get_organization_tickets(self):
        """Test get_organization_tickets method."""
        client = self.get_client()
        tickets_data = {
            "tickets": [
                {
                    "id": 791,
                    "subject": "Org Ticket",
                    "status": "solved",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tickets_data

            result = await client.get_organization_tickets(456, per_page=25)

            assert len(result) == 1
            assert isinstance(result[0], Ticket)
            assert result[0].id == 791
            assert result[0].subject == "Org Ticket"
            mock_get.assert_called_once_with("organizations/456/tickets.json", params={"per_page": 25})

    # Comments API tests

    @pytest.mark.asyncio
    async def test_get_ticket_comments(self):
        """Test get_ticket_comments method."""
        client = self.get_client()
        comments_data = {
            "comments": [
                {
                    "id": 111,
                    "body": "First comment",
                    "author_id": 123,
                    "public": True,
                    "created_at": "2023-01-01T12:00:00Z",
                },
                {
                    "id": 112,
                    "body": "Second comment",
                    "author_id": 124,
                    "public": False,
                    "created_at": "2023-01-01T13:00:00Z",
                },
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = comments_data

            result = await client.get_ticket_comments(789, per_page=20)

            assert len(result) == 2
            assert all(isinstance(comment, Comment) for comment in result)
            assert result[0].id == 111
            assert result[0].body == "First comment"
            assert result[1].id == 112
            assert result[1].body == "Second comment"
            mock_get.assert_called_once_with("tickets/789/comments.json", params={"per_page": 20})

    # Search API tests

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search method returns paginator."""
        client = self.get_client()

        with patch("zendesk_sdk.client.ZendeskPaginator.create_search_paginator") as mock_create:
            mock_paginator = AsyncMock()
            mock_create.return_value = mock_paginator

            result = await client.search("test query", per_page=30)

            assert result == mock_paginator
            mock_create.assert_called_once_with(client.http_client, query="test query", per_page=30)

    @pytest.mark.asyncio
    async def test_search_users(self):
        """Test search_users method."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 123,
                    "name": "Found User",
                    "email": "[email protected]",
                    "result_type": "user",
                    "created_at": "2023-01-01T00:00:00Z",
                },
                {
                    "id": 789,
                    "subject": "Some ticket",
                    "result_type": "ticket",  # Should be filtered out
                },
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.search_users("john", per_page=40)

            assert len(result) == 1  # Only user result should be returned
            assert isinstance(result[0], User)
            assert result[0].id == 123
            assert result[0].name == "Found User"
            mock_get.assert_called_once_with("search.json", params={"query": "type:user john", "per_page": 40})

    @pytest.mark.asyncio
    async def test_search_tickets(self):
        """Test search_tickets method."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 789,
                    "subject": "Found Ticket",
                    "status": "open",
                    "result_type": "ticket",
                    "created_at": "2023-01-01T00:00:00Z",
                },
                {
                    "id": 123,
                    "name": "Some user",
                    "result_type": "user",  # Should be filtered out
                },
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.search_tickets("urgent", per_page=60)

            assert len(result) == 1  # Only ticket result should be returned
            assert isinstance(result[0], Ticket)
            assert result[0].id == 789
            assert result[0].subject == "Found Ticket"
            mock_get.assert_called_once_with("search.json", params={"query": "type:ticket urgent", "per_page": 60})

    @pytest.mark.asyncio
    async def test_search_organizations(self):
        """Test search_organizations method."""
        client = self.get_client()
        search_data = {
            "results": [
                {
                    "id": 456,
                    "name": "Found Org",
                    "result_type": "organization",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_data

            result = await client.search_organizations("ACME", per_page=10)

            assert len(result) == 1
            assert isinstance(result[0], Organization)
            assert result[0].id == 456
            assert result[0].name == "Found Org"
            mock_get.assert_called_once_with("search.json", params={"query": "type:organization ACME", "per_page": 10})

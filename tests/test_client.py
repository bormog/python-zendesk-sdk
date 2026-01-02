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

    @pytest.mark.asyncio
    async def test_add_ticket_comment_default_private(self):
        """Test add_ticket_comment method creates private comment by default."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add_ticket_comment(789, "Internal note")

            assert isinstance(result, Ticket)
            assert result.id == 789
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={"ticket": {"comment": {"body": "Internal note", "public": False}}},
            )

    @pytest.mark.asyncio
    async def test_add_ticket_comment_public(self):
        """Test add_ticket_comment method with explicit public=True."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add_ticket_comment(789, "Thanks for contacting us!", public=True)

            assert isinstance(result, Ticket)
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={"ticket": {"comment": {"body": "Thanks for contacting us!", "public": True}}},
            )

    @pytest.mark.asyncio
    async def test_add_ticket_comment_with_author(self):
        """Test add_ticket_comment method with custom author."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add_ticket_comment(789, "Comment", author_id=456)

            assert isinstance(result, Ticket)
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={"ticket": {"comment": {"body": "Comment", "public": False, "author_id": 456}}},
            )

    @pytest.mark.asyncio
    async def test_make_comment_private(self):
        """Test make_comment_private method."""
        client = self.get_client()

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {}

            result = await client.make_comment_private(789, 111)

            assert result is True
            mock_put.assert_called_once_with("tickets/789/comments/111/make_private.json")

    @pytest.mark.asyncio
    async def test_redact_comment_string(self):
        """Test redact_comment_string method."""
        client = self.get_client()
        comment_data = {
            "comment": {
                "id": 111,
                "body": "My card is ▇▇▇▇",
                "author_id": 123,
                "public": True,
                "created_at": "2023-01-01T12:00:00Z",
            }
        }

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = comment_data

            result = await client.redact_comment_string(789, 111, "4111-1111-1111-1111")

            assert isinstance(result, Comment)
            assert result.id == 111
            assert "▇▇▇▇" in result.body
            mock_put.assert_called_once_with(
                "tickets/789/comments/111/redact.json",
                json={"text": "4111-1111-1111-1111"},
            )

    # Tags API tests

    @pytest.mark.asyncio
    async def test_get_ticket_tags(self):
        """Test get_ticket_tags method."""
        client = self.get_client()
        tags_data = {"tags": ["urgent", "vip", "billing"]}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tags_data

            result = await client.get_ticket_tags(789)

            assert result == ["urgent", "vip", "billing"]
            mock_get.assert_called_once_with("tickets/789/tags.json")

    @pytest.mark.asyncio
    async def test_get_ticket_tags_empty(self):
        """Test get_ticket_tags method with no tags."""
        client = self.get_client()
        tags_data = {"tags": []}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = tags_data

            result = await client.get_ticket_tags(789)

            assert result == []

    @pytest.mark.asyncio
    async def test_add_ticket_tags(self):
        """Test add_ticket_tags method adds tags without removing existing."""
        client = self.get_client()
        tags_data = {"tags": ["existing", "urgent", "vip"]}

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = tags_data

            result = await client.add_ticket_tags(789, ["urgent", "vip"])

            assert result == ["existing", "urgent", "vip"]
            mock_put.assert_called_once_with(
                "tickets/789/tags.json",
                json={"tags": ["urgent", "vip"]},
            )

    @pytest.mark.asyncio
    async def test_set_ticket_tags(self):
        """Test set_ticket_tags method replaces all tags."""
        client = self.get_client()
        tags_data = {"tags": ["new1", "new2"]}

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = tags_data

            result = await client.set_ticket_tags(789, ["new1", "new2"])

            assert result == ["new1", "new2"]
            mock_post.assert_called_once_with(
                "tickets/789/tags.json",
                json={"tags": ["new1", "new2"]},
            )

    @pytest.mark.asyncio
    async def test_remove_ticket_tags(self):
        """Test remove_ticket_tags method removes specific tags."""
        client = self.get_client()
        tags_data = {"tags": ["remaining"]}

        with patch.object(client.http_client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = tags_data

            result = await client.remove_ticket_tags(789, ["to_remove"])

            assert result == ["remaining"]
            mock_delete.assert_called_once_with(
                "tickets/789/tags.json",
                json={"tags": ["to_remove"]},
            )

    @pytest.mark.asyncio
    async def test_remove_ticket_tags_empty_response(self):
        """Test remove_ticket_tags method with empty response."""
        client = self.get_client()

        with patch.object(client.http_client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.remove_ticket_tags(789, ["to_remove"])

            assert result == []

    # Attachments API tests

    @pytest.mark.asyncio
    async def test_download_attachment(self):
        """Test download_attachment method downloads file content."""
        client = self.get_client()
        test_content = b"test file content"

        with patch("zendesk_sdk.client.httpx.AsyncClient") as mock_client_class:
            mock_http = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = test_content
            mock_response.raise_for_status = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__.return_value = mock_http
            mock_http.__aexit__.return_value = None
            mock_client_class.return_value = mock_http

            result = await client.download_attachment("https://example.com/attachment/123")

            assert result == test_content
            mock_http.get.assert_called_once_with("https://example.com/attachment/123")

    @pytest.mark.asyncio
    async def test_upload_attachment(self):
        """Test upload_attachment method uploads file and returns token."""
        client = self.get_client()
        test_data = b"file content"
        expected_token = "abc123token"

        with patch("zendesk_sdk.client.httpx.AsyncClient") as mock_client_class:
            mock_http = AsyncMock()
            mock_response = AsyncMock()
            # json() is a regular method, not async
            mock_response.json = lambda: {"upload": {"token": expected_token}}
            mock_response.raise_for_status = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_http.__aenter__.return_value = mock_http
            mock_http.__aexit__.return_value = None
            mock_client_class.return_value = mock_http

            result = await client.upload_attachment(test_data, "test.txt", "text/plain")

            assert result == expected_token
            mock_http.post.assert_called_once()
            call_args = mock_http.post.call_args
            assert "filename" in str(call_args)
            assert call_args.kwargs["content"] == test_data

    @pytest.mark.asyncio
    async def test_add_ticket_comment_with_uploads(self):
        """Test add_ticket_comment method with file uploads."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.add_ticket_comment(
                789,
                "See attached file",
                uploads=["token123", "token456"],
            )

            assert isinstance(result, Ticket)
            mock_put.assert_called_once_with(
                "tickets/789.json",
                json={
                    "ticket": {
                        "comment": {
                            "body": "See attached file",
                            "public": False,
                            "uploads": ["token123", "token456"],
                        }
                    }
                },
            )

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


class TestZendeskClientEnrichedTickets:
    """Test cases for EnrichedTicket methods."""

    def get_client(self):
        """Helper method to create a test client."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )
        return ZendeskClient(config)

    @pytest.mark.asyncio
    async def test_get_enriched_ticket(self):
        """Test get_enriched_ticket method."""
        from zendesk_sdk.models import EnrichedTicket

        client = self.get_client()

        ticket_response = {
            "ticket": {
                "id": 789,
                "subject": "Test Ticket",
                "status": "open",
                "requester_id": 123,
                "assignee_id": 456,
                "created_at": "2023-01-01T00:00:00Z",
            },
            "users": [
                {"id": 123, "name": "Requester", "email": "req@example.com", "created_at": "2023-01-01T00:00:00Z"},
                {"id": 456, "name": "Assignee", "email": "assign@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ],
        }

        comments_response = {
            "comments": [
                {
                    "id": 111,
                    "body": "First comment",
                    "author_id": 123,
                    "public": True,
                    "created_at": "2023-01-01T12:00:00Z",
                },
            ],
            "users": [
                {"id": 123, "name": "Requester", "email": "req@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [ticket_response, comments_response]

            result = await client.get_enriched_ticket(789)

            assert isinstance(result, EnrichedTicket)
            assert result.ticket.id == 789
            assert result.ticket.subject == "Test Ticket"
            assert len(result.comments) == 1
            assert 123 in result.users
            assert result.requester is not None
            assert result.requester.name == "Requester"

    @pytest.mark.asyncio
    async def test_search_enriched_tickets(self):
        """Test search_enriched_tickets method."""
        from zendesk_sdk.models import EnrichedTicket

        client = self.get_client()

        search_response = {
            "results": [
                {
                    "id": 789,
                    "subject": "Found Ticket",
                    "status": "open",
                    "result_type": "ticket",
                    "requester_id": 123,
                    "created_at": "2023-01-01T00:00:00Z",
                },
            ]
        }

        users_response = {
            "users": [
                {"id": 123, "name": "Requester", "email": "req@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ]
        }

        comments_response = {
            "comments": [
                {"id": 111, "body": "Comment", "author_id": 123, "public": True, "created_at": "2023-01-01T12:00:00Z"},
            ],
            "users": [],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [search_response, users_response, comments_response]

            result = await client.search_enriched_tickets("status:open", per_page=10)

            assert len(result) == 1
            assert isinstance(result[0], EnrichedTicket)
            assert result[0].ticket.id == 789

    @pytest.mark.asyncio
    async def test_search_enriched_tickets_empty(self):
        """Test search_enriched_tickets method with no results."""
        client = self.get_client()

        search_response = {"results": []}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = search_response

            result = await client.search_enriched_tickets("nonexistent", per_page=10)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_organization_enriched_tickets(self):
        """Test get_organization_enriched_tickets method."""
        from zendesk_sdk.models import EnrichedTicket

        client = self.get_client()

        tickets_response = {
            "tickets": [
                {
                    "id": 789,
                    "subject": "Org Ticket",
                    "status": "open",
                    "requester_id": 123,
                    "created_at": "2023-01-01T00:00:00Z",
                },
            ],
            "users": [
                {"id": 123, "name": "Requester", "email": "req@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ],
        }

        comments_response = {
            "comments": [],
            "users": [],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [tickets_response, comments_response]

            result = await client.get_organization_enriched_tickets(456, per_page=10)

            assert len(result) == 1
            assert isinstance(result[0], EnrichedTicket)
            assert result[0].ticket.id == 789

    @pytest.mark.asyncio
    async def test_get_user_enriched_tickets(self):
        """Test get_user_enriched_tickets method."""
        from zendesk_sdk.models import EnrichedTicket

        client = self.get_client()

        tickets_response = {
            "tickets": [
                {
                    "id": 789,
                    "subject": "User Ticket",
                    "status": "open",
                    "requester_id": 123,
                    "created_at": "2023-01-01T00:00:00Z",
                },
            ],
            "users": [
                {"id": 123, "name": "Requester", "email": "req@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ],
        }

        comments_response = {
            "comments": [],
            "users": [],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [tickets_response, comments_response]

            result = await client.get_user_enriched_tickets(123, per_page=10)

            assert len(result) == 1
            assert isinstance(result[0], EnrichedTicket)
            assert result[0].ticket.id == 789

    @pytest.mark.asyncio
    async def test_fetch_users_batch_empty(self):
        """Test _fetch_users_batch method with empty list."""
        client = self.get_client()

        result = await client._fetch_users_batch([])
        assert result == {}

    def test_collect_user_ids_from_tickets(self):
        """Test _collect_user_ids_from_tickets method."""
        client = self.get_client()
        tickets = [
            Ticket(id=1, requester_id=101, assignee_id=102, submitter_id=103, created_at="2023-01-01T00:00:00Z"),
            Ticket(id=2, requester_id=104, collaborator_ids=[105, 106], created_at="2023-01-01T00:00:00Z"),
        ]

        result = client._collect_user_ids_from_tickets(tickets)

        assert set(result) == {101, 102, 103, 104, 105, 106}

    def test_extract_users_from_response(self):
        """Test _extract_users_from_response method."""
        client = self.get_client()
        response = {
            "users": [
                {"id": 123, "name": "User1", "email": "user1@example.com", "created_at": "2023-01-01T00:00:00Z"},
                {"id": 456, "name": "User2", "email": "user2@example.com", "created_at": "2023-01-01T00:00:00Z"},
            ]
        }

        result = client._extract_users_from_response(response)

        assert len(result) == 2
        assert 123 in result
        assert 456 in result
        assert result[123].name == "User1"
        assert result[456].name == "User2"


class TestZendeskClientHTTPMethods:
    """Test cases for ZendeskClient HTTP methods."""

    def get_client(self):
        """Helper method to create a test client."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
        )
        return ZendeskClient(config)

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

    def test_repr(self):
        """Test __repr__ method."""
        client = self.get_client()
        assert repr(client) == "ZendeskClient(subdomain='test')"

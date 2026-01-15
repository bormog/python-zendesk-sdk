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

    @pytest.mark.asyncio
    async def test_me(self):
        """Test get current user."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Current User",
                "email": "me@example.com",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_data

            result = await client.me()

            assert isinstance(result, User)
            assert result.name == "Current User"
            mock_get.assert_called_once_with("users/me.json")

    @pytest.mark.asyncio
    async def test_create_minimal(self):
        """Test create user with minimal parameters."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "New User",
                "email": None,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = user_data

            result = await client.create(name="New User")

            assert isinstance(result, User)
            assert result.id == 123
            mock_post.assert_called_once_with(
                "users.json",
                json={"user": {"name": "New User"}},
            )

    @pytest.mark.asyncio
    async def test_create_full(self):
        """Test create user with all parameters."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "email": "john@example.com",
                "role": "agent",
                "verified": True,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = user_data

            result = await client.create(
                name="John Doe",
                email="john@example.com",
                role="agent",
                verified=True,
                external_id="EXT-123",
                organization_id=999,
                phone="+1234567890",
                tags=["vip"],
                user_fields={"department": "Sales"},
            )

            assert isinstance(result, User)
            payload = mock_post.call_args[1]["json"]["user"]
            assert payload["name"] == "John Doe"
            assert payload["email"] == "john@example.com"
            assert payload["role"] == "agent"
            assert payload["verified"] is True
            assert payload["external_id"] == "EXT-123"
            assert payload["organization_id"] == 999
            assert payload["phone"] == "+1234567890"
            assert payload["tags"] == ["vip"]
            assert payload["user_fields"] == {"department": "Sales"}

    @pytest.mark.asyncio
    async def test_create_or_update(self):
        """Test create or update user."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Upserted User",
                "email": "upsert@example.com",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = user_data

            result = await client.create_or_update(
                name="Upserted User",
                email="upsert@example.com",
                external_id="CRM-123",
            )

            assert isinstance(result, User)
            mock_post.assert_called_once()
            assert "users/create_or_update.json" in mock_post.call_args[0]

    @pytest.mark.asyncio
    async def test_create_many(self):
        """Test create multiple users."""
        client = self.get_client()
        job_data = {
            "job_status": {
                "id": "job-123",
                "status": "queued",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = job_data

            result = await client.create_many(
                [
                    {"name": "User 1", "email": "u1@example.com"},
                    {"name": "User 2", "email": "u2@example.com"},
                ]
            )

            assert "job_status" in result
            mock_post.assert_called_once_with(
                "users/create_many.json",
                json={
                    "users": [
                        {"name": "User 1", "email": "u1@example.com"},
                        {"name": "User 2", "email": "u2@example.com"},
                    ]
                },
            )

    @pytest.mark.asyncio
    async def test_update(self):
        """Test update user."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Updated User",
                "phone": "+9999999999",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = user_data

            result = await client.update(123, phone="+9999999999")

            assert isinstance(result, User)
            mock_put.assert_called_once_with(
                "users/123.json",
                json={"user": {"phone": "+9999999999"}},
            )

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self):
        """Test update user with multiple fields."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "New Name",
                "tags": ["updated"],
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = user_data

            result = await client.update(
                123,
                name="New Name",
                tags=["updated"],
                user_fields={"status": "active"},
            )

            assert isinstance(result, User)
            payload = mock_put.call_args[1]["json"]["user"]
            assert payload["name"] == "New Name"
            assert payload["tags"] == ["updated"]
            assert payload["user_fields"] == {"status": "active"}

    @pytest.mark.asyncio
    async def test_update_many(self):
        """Test update multiple users."""
        client = self.get_client()
        job_data = {"job_status": {"id": "job-456"}}

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = job_data

            result = await client.update_many(
                [123, 456],
                organization_id=999,
                tags=["bulk"],
            )

            assert "job_status" in result
            assert "users/update_many.json?ids=123,456" in mock_put.call_args[0][0]

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete user."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete(123)

            assert result is True
            mock_delete.assert_called_once_with("users/123.json")

    @pytest.mark.asyncio
    async def test_delete_many(self):
        """Test delete multiple users."""
        client = self.get_client()
        job_data = {"job_status": {"id": "job-789"}}

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = job_data

            result = await client.delete_many([123, 456])

            assert "job_status" in result
            assert "users/destroy_many.json?ids=123,456" in mock_delete.call_args[0][0]

    @pytest.mark.asyncio
    async def test_permanently_delete(self):
        """Test permanently delete user."""
        client = self.get_client()
        delete_data = {"deleted_user": {"id": 123}}

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = delete_data

            await client.permanently_delete(123)

            mock_delete.assert_called_once_with("deleted_users/123.json")

    @pytest.mark.asyncio
    async def test_set_password(self):
        """Test set user password."""
        client = self.get_client()

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {}

            result = await client.set_password(123, "NewPass123!")

            assert result is True
            mock_post.assert_called_once_with(
                "users/123/password.json",
                json={"password": "NewPass123!"},
            )

    @pytest.mark.asyncio
    async def test_get_password_requirements(self):
        """Test get password requirements."""
        from zendesk_sdk.models import PasswordRequirements

        client = self.get_client()
        req_data = {
            "requirements": [
                "must be at least 8 characters",
                "must include letters in mixed case",
                "must include numbers",
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = req_data

            result = await client.get_password_requirements(123)

            assert isinstance(result, PasswordRequirements)
            assert len(result.rules) == 3
            assert "must be at least 8 characters" in result.rules
            mock_get.assert_called_once_with("users/123/password/requirements.json")

    @pytest.mark.asyncio
    async def test_suspend(self):
        """Test suspend user."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Suspended User",
                "suspended": True,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = user_data

            result = await client.suspend(123)

            assert isinstance(result, User)
            assert result.suspended is True
            mock_put.assert_called_once_with(
                "users/123.json",
                json={"user": {"suspended": True}},
            )

    @pytest.mark.asyncio
    async def test_unsuspend(self):
        """Test unsuspend user."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 123,
                "name": "Active User",
                "suspended": False,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = user_data

            result = await client.unsuspend(123)

            assert isinstance(result, User)
            assert result.suspended is False
            mock_put.assert_called_once_with(
                "users/123.json",
                json={"user": {"suspended": False}},
            )

    @pytest.mark.asyncio
    async def test_merge(self):
        """Test merge users."""
        client = self.get_client()
        user_data = {
            "user": {
                "id": 456,
                "name": "Merged User",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = user_data

            result = await client.merge(123, 456)

            assert isinstance(result, User)
            assert result.id == 456
            mock_put.assert_called_once_with(
                "users/123/merge.json",
                json={"user": {"id": 456}},
            )


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

    @pytest.mark.asyncio
    async def test_create_minimal(self):
        """Test create ticket with minimal parameters (only comment_body)."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": None,
                "status": "new",
                "description": "Help me!",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = ticket_data

            result = await client.create(comment_body="Help me!")

            assert isinstance(result, Ticket)
            assert result.id == 12345
            mock_post.assert_called_once_with(
                "tickets.json",
                json={"ticket": {"comment": {"body": "Help me!", "public": True}}},
            )

    @pytest.mark.asyncio
    async def test_create_full(self):
        """Test create ticket with all parameters."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": "Login Issue",
                "status": "open",
                "priority": "high",
                "tags": ["login", "urgent"],
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = ticket_data

            result = await client.create(
                comment_body="Customer cannot login",
                subject="Login Issue",
                priority="high",
                status="open",
                ticket_type="problem",
                assignee_id=111,
                group_id=222,
                requester_id=333,
                tags=["login", "urgent"],
                custom_fields=[{"id": 360001, "value": "bug"}],
                external_id="EXT-123",
                public=False,
            )

            assert isinstance(result, Ticket)
            assert result.id == 12345

            # Verify all fields were sent
            call_args = mock_post.call_args
            payload = call_args[1]["json"]["ticket"]
            assert payload["comment"]["body"] == "Customer cannot login"
            assert payload["comment"]["public"] is False
            assert payload["subject"] == "Login Issue"
            assert payload["priority"] == "high"
            assert payload["status"] == "open"
            assert payload["type"] == "problem"
            assert payload["assignee_id"] == 111
            assert payload["group_id"] == 222
            assert payload["requester_id"] == 333
            assert payload["tags"] == ["login", "urgent"]
            assert payload["custom_fields"] == [{"id": 360001, "value": "bug"}]
            assert payload["external_id"] == "EXT-123"

    @pytest.mark.asyncio
    async def test_create_with_uploads(self):
        """Test create ticket with file attachments."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": "Issue with attachment",
                "status": "new",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = ticket_data

            result = await client.create(
                comment_body="See attached screenshot", subject="Issue with attachment", uploads=["token1", "token2"]
            )

            assert isinstance(result, Ticket)
            payload = mock_post.call_args[1]["json"]["ticket"]
            assert payload["comment"]["uploads"] == ["token1", "token2"]

    @pytest.mark.asyncio
    async def test_update_single_field(self):
        """Test update ticket with single field."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": "Test",
                "status": "solved",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.update(12345, status="solved")

            assert isinstance(result, Ticket)
            assert result.status == "solved"
            mock_put.assert_called_once_with(
                "tickets/12345.json",
                json={"ticket": {"status": "solved"}},
            )

    @pytest.mark.asyncio
    async def test_update_with_comment(self):
        """Test update ticket with comment."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": "Test",
                "status": "pending",
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.update(
                12345, status="pending", comment={"body": "Waiting for customer", "public": False}
            )

            assert isinstance(result, Ticket)
            payload = mock_put.call_args[1]["json"]["ticket"]
            assert payload["status"] == "pending"
            assert payload["comment"]["body"] == "Waiting for customer"
            assert payload["comment"]["public"] is False

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self):
        """Test update ticket with multiple fields."""
        client = self.get_client()
        ticket_data = {
            "ticket": {
                "id": 12345,
                "subject": "Updated Subject",
                "status": "open",
                "priority": "urgent",
                "assignee_id": 999,
                "created_at": "2023-01-01T00:00:00Z",
            }
        }

        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = ticket_data

            result = await client.update(
                12345, subject="Updated Subject", priority="urgent", assignee_id=999, tags=["escalated"]
            )

            assert isinstance(result, Ticket)
            payload = mock_put.call_args[1]["json"]["ticket"]
            assert payload["subject"] == "Updated Subject"
            assert payload["priority"] == "urgent"
            assert payload["assignee_id"] == 999
            assert payload["tags"] == ["escalated"]

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete ticket."""
        client = self.get_client()

        with patch.object(client, "_delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None

            result = await client.delete(12345)

            assert result is True
            mock_delete.assert_called_once_with("tickets/12345.json")


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


class TestTicketFieldsClient:
    """Test cases for TicketFieldsClient."""

    def get_client(self):
        """Create a mock TicketFieldsClient."""
        from zendesk_sdk.clients import TicketFieldsClient

        mock_http = MagicMock()
        return TicketFieldsClient(mock_http)

    @pytest.mark.asyncio
    async def test_get(self):
        """Test get ticket field by ID."""
        client = self.get_client()
        field_data = {
            "ticket_field": {
                "id": 123,
                "type": "text",
                "title": "Custom Field",
                "active": True,
                "required": False,
                "removable": True,
            }
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = field_data

            from zendesk_sdk.models import TicketField

            result = await client.get(123)

            assert isinstance(result, TicketField)
            assert result.id == 123
            assert result.title == "Custom Field"
            assert result.type == "text"
            mock_get.assert_called_once_with("ticket_fields/123.json")

    @pytest.mark.asyncio
    async def test_get_by_title_found(self):
        """Test find ticket field by title."""
        client = self.get_client()

        from zendesk_sdk.models import TicketField

        async def mock_iter(self):
            yield TicketField(id=1, type="text", title="Status")
            yield TicketField(id=2, type="text", title="Custom Field")
            yield TicketField(id=3, type="text", title="Priority")

        with patch.object(client, "list") as mock_list:
            mock_paginator = MagicMock()
            mock_paginator.__aiter__ = mock_iter
            mock_list.return_value = mock_paginator

            result = await client.get_by_title("Custom Field")

            assert result is not None
            assert result.id == 2
            assert result.title == "Custom Field"

    @pytest.mark.asyncio
    async def test_get_by_title_case_insensitive(self):
        """Test find ticket field by title is case insensitive."""
        client = self.get_client()

        from zendesk_sdk.models import TicketField

        async def mock_iter(self):
            yield TicketField(id=1, type="text", title="Custom Field")

        with patch.object(client, "list") as mock_list:
            mock_paginator = MagicMock()
            mock_paginator.__aiter__ = mock_iter
            mock_list.return_value = mock_paginator

            result = await client.get_by_title("CUSTOM FIELD")

            assert result is not None
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_by_title_not_found(self):
        """Test find ticket field by title when not found."""
        client = self.get_client()

        from zendesk_sdk.models import TicketField

        async def mock_iter(self):
            yield TicketField(id=1, type="text", title="Status")
            yield TicketField(id=2, type="text", title="Priority")

        with patch.object(client, "list") as mock_list:
            mock_paginator = MagicMock()
            mock_paginator.__aiter__ = mock_iter
            mock_list.return_value = mock_paginator

            result = await client.get_by_title("NonExistent")

            assert result is None

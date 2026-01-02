"""Tests for Zendesk API data models."""

from datetime import datetime
from typing import Optional

import pytest
from pydantic import Field, ValidationError

from zendesk_sdk.models import (
    Comment,
    CommentAttachment,
    CommentMetadata,
    CommentVia,
    Organization,
    OrganizationField,
    OrganizationSubscription,
    SatisfactionRating,
    Ticket,
    TicketCustomField,
    TicketField,
    TicketMetrics,
    TicketVia,
    User,
    UserField,
    UserIdentity,
    UserPhoto,
    ZendeskModel,
)


class TestModel(ZendeskModel):
    """Test model for testing base functionality."""

    uid: int = Field(alias="id")
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    extra_field: Optional[str] = None


class TestZendeskModel:
    """Test base ZendeskModel functionality."""

    def test_basic_model_creation(self):
        """Test creating a basic model."""
        model = TestModel(id=123, name="Test")
        assert model.uid == 123
        assert model.name == "Test"

    def test_alias_support(self):
        """Test field aliases work correctly."""
        # Using alias
        model1 = TestModel(id=123, name="Test")
        assert model1.uid == 123

        # Using actual field name
        model2 = TestModel(uid=456, name="Test")
        assert model2.uid == 456

    def test_model_config(self):
        """Test that model config is properly set."""
        model = TestModel(id=123)
        config = model.model_config
        assert config["populate_by_name"] is True
        assert config["use_enum_values"] is True
        assert config["validate_assignment"] is True
        assert config["extra"] == "ignore"

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        data = {
            "id": 123,
            "name": "Test",
            "unknown_field": "ignored",
            "another_unknown": 456,
        }
        model = TestModel(**data)
        assert model.uid == 123
        assert model.name == "Test"


class TestUserModels:
    """Test User-related models."""

    def test_user_creation_minimal(self):
        """Test User creation with minimal required fields."""
        user = User(name="John Doe")
        assert user.name == "John Doe"
        assert user.id is None
        assert user.email is None

    def test_user_creation_full(self):
        """Test User creation with all fields."""
        user_data = {
            "id": 123,
            "name": "John Doe",
            "email": "[email protected]",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "phone": "+1234567890",
            "organization_id": 456,
            "role": "end-user",
            "tags": ["vip", "enterprise"],
            "active": True,
            "verified": True,
            "user_fields": {"custom_field": "value"},
        }
        user = User(**user_data)
        assert user.id == 123
        assert user.name == "John Doe"
        assert user.email == "[email protected]"
        assert user.tags == ["vip", "enterprise"]
        assert user.active is True
        assert user.user_fields == {"custom_field": "value"}

    def test_user_datetime_parsing(self):
        """Test that datetime fields are properly parsed."""
        user = User(name="John Doe", created_at="2023-01-01T12:30:45Z", updated_at="2023-01-02T15:45:30Z")
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_identity_creation(self):
        """Test UserIdentity creation."""
        identity = UserIdentity(user_id=123, type="email", value="[email protected]", verified=True, primary=True)
        assert identity.user_id == 123
        assert identity.type == "email"
        assert identity.value == "[email protected]"
        assert identity.verified is True
        assert identity.primary is True

    def test_user_field_creation(self):
        """Test UserField creation."""
        field = UserField(key="custom_field_1", type="text", title="Custom Field 1", active=True)
        assert field.key == "custom_field_1"
        assert field.type == "text"
        assert field.title == "Custom Field 1"
        assert field.active is True

    def test_user_photo_creation(self):
        """Test UserPhoto creation."""
        photo = UserPhoto(id=456, file_name="avatar.jpg", content_type="image/jpeg", size=12345, width=100, height=100)
        assert photo.id == 456
        assert photo.file_name == "avatar.jpg"
        assert photo.content_type == "image/jpeg"
        assert photo.size == 12345


class TestOrganizationModels:
    """Test Organization-related models."""

    def test_organization_creation_minimal(self):
        """Test Organization creation with minimal required fields."""
        org = Organization(name="ACME Corp")
        assert org.name == "ACME Corp"
        assert org.id is None

    def test_organization_creation_full(self):
        """Test Organization creation with all fields."""
        org_data = {
            "id": 789,
            "name": "ACME Corp",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "details": "A great company",
            "notes": "Important client",
            "external_id": "EXT123",
            "domain_names": ["acme.com", "acme.org"],
            "tags": ["enterprise", "priority"],
            "group_id": 111,
            "shared_tickets": True,
            "shared_comments": False,
            "organization_fields": {"industry": "technology"},
        }
        org = Organization(**org_data)
        assert org.id == 789
        assert org.name == "ACME Corp"
        assert org.domain_names == ["acme.com", "acme.org"]
        assert org.tags == ["enterprise", "priority"]
        assert org.shared_tickets is True
        assert org.organization_fields == {"industry": "technology"}

    def test_organization_field_creation(self):
        """Test OrganizationField creation."""
        field = OrganizationField(
            key="company_size",
            type="dropdown",
            title="Company Size",
            custom_field_options=[{"name": "Small", "value": "small"}, {"name": "Large", "value": "large"}],
        )
        assert field.key == "company_size"
        assert field.type == "dropdown"
        assert field.title == "Company Size"
        assert len(field.custom_field_options) == 2

    def test_organization_subscription_creation(self):
        """Test OrganizationSubscription creation."""
        sub = OrganizationSubscription(id=999, organization_id=789, user_id=123, created_at="2023-01-01T00:00:00Z")
        assert sub.id == 999
        assert sub.organization_id == 789
        assert sub.user_id == 123


class TestTicketModels:
    """Test Ticket-related models."""

    def test_ticket_creation_minimal(self):
        """Test Ticket creation with minimal fields."""
        ticket = Ticket()
        assert ticket.id is None
        assert ticket.subject is None

    def test_ticket_creation_full(self):
        """Test Ticket creation with comprehensive fields."""
        ticket_data = {
            "id": 12345,
            "subject": "Help needed",
            "description": "I need help with my account",
            "status": "open",
            "priority": "normal",
            "type": "question",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "requester_id": 123,
            "assignee_id": 456,
            "organization_id": 789,
            "group_id": 111,
            "tags": ["account", "billing"],
            "external_id": "EXT-456",
            "custom_fields": [{"id": 27642, "value": "745"}, {"id": 27648, "value": "yes"}],
            "has_incidents": False,
            "is_public": True,
            "collaborator_ids": [222, 333],
            "follower_ids": [444, 555],
        }
        ticket = Ticket(**ticket_data)
        assert ticket.id == 12345
        assert ticket.subject == "Help needed"
        assert ticket.status == "open"
        assert ticket.priority == "normal"
        assert ticket.tags == ["account", "billing"]
        assert len(ticket.custom_fields) == 2
        assert ticket.custom_fields[0].id == 27642
        assert ticket.custom_fields[0].value == "745"

    def test_ticket_via_creation(self):
        """Test TicketVia creation."""
        via = TicketVia(channel="web", source={"from": {"address": "[email protected]"}})
        assert via.channel == "web"
        assert via.source["from"]["address"] == "[email protected]"

    def test_satisfaction_rating_creation(self):
        """Test SatisfactionRating creation."""
        rating = SatisfactionRating(id=678, score="good", comment="Great support!")
        assert rating.id == 678
        assert rating.score == "good"
        assert rating.comment == "Great support!"

    def test_ticket_custom_field_creation(self):
        """Test TicketCustomField creation."""
        field = TicketCustomField(id=123, value="test_value")
        assert field.id == 123
        assert field.value == "test_value"

    def test_ticket_field_creation(self):
        """Test TicketField creation."""
        field = TicketField(type="text", title="Custom Field", active=True, required=False, position=1)
        assert field.type == "text"
        assert field.title == "Custom Field"
        assert field.active is True
        assert field.required is False

    def test_ticket_metrics_creation(self):
        """Test TicketMetrics creation."""
        metrics = TicketMetrics(
            ticket_id=12345,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            reopens=2,
            replies=5,
            group_stations=1,
            assignee_stations=2,
        )
        assert metrics.ticket_id == 12345
        assert metrics.reopens == 2
        assert metrics.replies == 5
        assert metrics.group_stations == 1


class TestCommentModels:
    """Test Comment-related models."""

    def test_comment_creation_minimal(self):
        """Test Comment creation with minimal fields."""
        comment = Comment()
        assert comment.id is None
        assert comment.body is None

    def test_comment_creation_full(self):
        """Test Comment creation with all fields."""
        comment_data = {
            "id": 98765,
            "type": "Comment",
            "author_id": 123,
            "body": "This is a test comment",
            "html_body": "<p>This is a test comment</p>",
            "plain_body": "This is a test comment",
            "public": True,
            "audit_id": 54321,
            "created_at": "2023-01-01T12:00:00Z",
            "ticket_id": 12345,
        }
        comment = Comment(**comment_data)
        assert comment.id == 98765
        assert comment.type == "Comment"
        assert comment.author_id == 123
        assert comment.body == "This is a test comment"
        assert comment.public is True
        assert comment.ticket_id == 12345

    def test_comment_via_creation(self):
        """Test CommentVia creation."""
        via = CommentVia(channel="email", source={"from": {"address": "[email protected]"}})
        assert via.channel == "email"
        assert via.source["from"]["address"] == "[email protected]"

    def test_comment_attachment_creation(self):
        """Test CommentAttachment creation."""
        attachment = CommentAttachment(
            id=999,
            file_name="screenshot.png",
            content_type="image/png",
            size=123456,
            width=800,
            height=600,
            inline=False,
        )
        assert attachment.id == 999
        assert attachment.file_name == "screenshot.png"
        assert attachment.content_type == "image/png"
        assert attachment.size == 123456
        assert attachment.inline is False

    def test_comment_metadata_creation(self):
        """Test CommentMetadata creation."""
        metadata = CommentMetadata(
            system={"client": "web", "ip_address": "192.168.1.1"},
            flags=["important", "escalated"],
            custom={"priority": "high"},
        )
        assert metadata.system["client"] == "web"
        assert "important" in metadata.flags
        assert metadata.custom["priority"] == "high"


class TestModelValidation:
    """Test model validation and error handling."""

    def test_user_name_required(self):
        """Test that User name is required."""
        with pytest.raises(ValidationError) as exc_info:
            User()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "name" in str(errors[0])

    def test_organization_name_required(self):
        """Test that Organization name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Organization()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "name" in str(errors[0])

    def test_user_identity_required_fields(self):
        """Test that UserIdentity required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            UserIdentity()

        errors = exc_info.value.errors()
        # Should have errors for user_id, type, and value
        assert len(errors) == 3
        error_fields = {error["loc"][0] for error in errors}
        assert "user_id" in error_fields
        assert "type" in error_fields
        assert "value" in error_fields

    def test_ticket_field_required_fields(self):
        """Test that TicketField required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            TicketField()

        errors = exc_info.value.errors()
        # Should have errors for type and title
        assert len(errors) == 2
        error_fields = {error["loc"][0] for error in errors}
        assert "type" in error_fields
        assert "title" in error_fields

    def test_ticket_custom_field_required_id(self):
        """Test that TicketCustomField id is required."""
        with pytest.raises(ValidationError) as exc_info:
            TicketCustomField(value="test")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "id" in str(errors[0])

    def test_datetime_string_conversion(self):
        """Test that datetime strings are properly converted."""
        user = User(name="Test User", created_at="2023-12-25T10:30:00Z", last_login_at="2023-12-25T11:45:30.123456Z")
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.last_login_at, datetime)
        assert user.created_at.year == 2023
        assert user.created_at.month == 12
        assert user.created_at.day == 25

    def test_model_dict_conversion(self):
        """Test that models can be converted to dictionaries."""
        user = User(name="Test User", email="[email protected]", active=True, tags=["test", "sample"])
        user_dict = user.model_dump()

        # Should contain the fields we set
        assert user_dict["name"] == "Test User"
        assert user_dict["email"] == "[email protected]"
        assert user_dict["active"] is True
        assert user_dict["tags"] == ["test", "sample"]

        # Should contain None values for unset optional fields
        assert "id" in user_dict
        assert user_dict["id"] is None

    def test_model_json_serialization(self):
        """Test that models can be serialized to JSON."""
        ticket = Ticket(id=123, subject="Test Ticket", status="open", created_at=datetime(2023, 12, 25, 10, 30, 0))

        json_str = ticket.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test Ticket" in json_str
        assert "2023-12-25T10:30:00" in json_str

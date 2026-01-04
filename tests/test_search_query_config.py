"""Tests for SearchQueryConfig query string generation.

These tests verify that SearchQueryConfig generates valid Zendesk query strings
based on official Zendesk documentation examples:
https://support.zendesk.com/hc/en-us/articles/203663226
"""

from datetime import date, datetime

import pytest

from zendesk_sdk.models.search import (
    SearchQueryConfig,
    SearchType,
    SortOrder,
    TicketChannel,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserRole,
)


class TestTicketSearchQueries:
    """Test ticket search query generation based on Zendesk docs."""

    def test_basic_status_filter(self) -> None:
        """Test: status:open"""
        config = SearchQueryConfig(status=["open"])
        assert "type:ticket" in config.to_query()
        assert "status:open" in config.to_query()

    def test_multiple_status_or_logic(self) -> None:
        """Test: status:open status:pending (OR logic within same field)"""
        config = SearchQueryConfig(status=["open", "pending"])
        query = config.to_query()
        assert "status:open" in query
        assert "status:pending" in query

    def test_priority_filter(self) -> None:
        """Test: priority:high priority:urgent"""
        config = SearchQueryConfig(priority=["high", "urgent"])
        query = config.to_query()
        assert "priority:high" in query
        assert "priority:urgent" in query

    def test_ticket_type_filter(self) -> None:
        """Test: ticket_type:incident ticket_type:problem"""
        config = SearchQueryConfig(ticket_type=["incident", "problem"])
        query = config.to_query()
        assert "ticket_type:incident" in query
        assert "ticket_type:problem" in query

    def test_organization_filter(self) -> None:
        """Test: organization:12345"""
        config = SearchQueryConfig(organization_id=12345)
        assert "organization:12345" in config.to_query()

    def test_requester_filter_by_id(self) -> None:
        """Test: requester:67890"""
        config = SearchQueryConfig(requester_id=67890)
        assert "requester:67890" in config.to_query()

    def test_requester_filter_none(self) -> None:
        """Test: requester:none (tickets without requester)"""
        config = SearchQueryConfig(requester_id="none")
        assert "requester:none" in config.to_query()

    def test_requester_filter_me(self) -> None:
        """Test: requester:me (my tickets)"""
        config = SearchQueryConfig(requester_id="me")
        assert "requester:me" in config.to_query()

    def test_assignee_filter_by_id(self) -> None:
        """Test: assignee:12345"""
        config = SearchQueryConfig(assignee_id=12345)
        assert "assignee:12345" in config.to_query()

    def test_assignee_filter_none(self) -> None:
        """Test: assignee:none (unassigned tickets)"""
        config = SearchQueryConfig(assignee_id="none")
        assert "assignee:none" in config.to_query()

    def test_group_filter(self) -> None:
        """Test: group:111"""
        config = SearchQueryConfig(group_id=111)
        assert "group:111" in config.to_query()

    def test_brand_filter(self) -> None:
        """Test: brand:222"""
        config = SearchQueryConfig(brand_id=222)
        assert "brand:222" in config.to_query()

    def test_via_channel_filter(self) -> None:
        """Test: via:email via:web"""
        config = SearchQueryConfig(via=["email", "web"])
        query = config.to_query()
        assert "via:email" in query
        assert "via:web" in query

    def test_tags_include(self) -> None:
        """Test: tags:vip tags:enterprise (OR logic)"""
        config = SearchQueryConfig(tags=["vip", "enterprise"])
        query = config.to_query()
        assert "tags:vip" in query
        assert "tags:enterprise" in query

    def test_tags_exclude(self) -> None:
        """Test: -tags:spam -tags:test (NOT logic)"""
        config = SearchQueryConfig(exclude_tags=["spam", "test"])
        query = config.to_query()
        assert "-tags:spam" in query
        assert "-tags:test" in query

    def test_has_attachment(self) -> None:
        """Test: has_attachment:true"""
        config = SearchQueryConfig(has_attachment=True)
        assert "has_attachment:true" in config.to_query()

    def test_no_attachment(self) -> None:
        """Test: has_attachment:false"""
        config = SearchQueryConfig(has_attachment=False)
        assert "has_attachment:false" in config.to_query()

    def test_subject_search(self) -> None:
        """Test: subject:"password reset" """
        config = SearchQueryConfig(subject="password reset")
        assert 'subject:"password reset"' in config.to_query()

    def test_description_search(self) -> None:
        """Test: description:"error message" """
        config = SearchQueryConfig(description="error message")
        assert 'description:"error message"' in config.to_query()


class TestDateFilters:
    """Test date filter query generation based on Zendesk docs."""

    def test_created_after_date(self) -> None:
        """Test: created>2024-01-01"""
        config = SearchQueryConfig(created_after=date(2024, 1, 1))
        assert "created>2024-01-01" in config.to_query()

    def test_created_before_date(self) -> None:
        """Test: created<2024-12-31"""
        config = SearchQueryConfig(created_before=date(2024, 12, 31))
        assert "created<2024-12-31" in config.to_query()

    def test_created_range(self) -> None:
        """Test: created>2024-01-01 created<2024-12-31"""
        config = SearchQueryConfig(
            created_after=date(2024, 1, 1),
            created_before=date(2024, 12, 31),
        )
        query = config.to_query()
        assert "created>2024-01-01" in query
        assert "created<2024-12-31" in query

    def test_updated_range(self) -> None:
        """Test: updated>2024-06-01 updated<2024-06-30"""
        config = SearchQueryConfig(
            updated_after=date(2024, 6, 1),
            updated_before=date(2024, 6, 30),
        )
        query = config.to_query()
        assert "updated>2024-06-01" in query
        assert "updated<2024-06-30" in query

    def test_solved_range(self) -> None:
        """Test: solved>2024-01-01"""
        config = SearchQueryConfig(solved_after=date(2024, 1, 1))
        assert "solved>2024-01-01" in config.to_query()

    def test_due_date_range(self) -> None:
        """Test: due_date>2024-01-01 due_date<2024-01-31"""
        config = SearchQueryConfig(
            due_date_after=date(2024, 1, 1),
            due_date_before=date(2024, 1, 31),
        )
        query = config.to_query()
        assert "due_date>2024-01-01" in query
        assert "due_date<2024-01-31" in query

    def test_datetime_with_timezone(self) -> None:
        """Test: created>2024-01-01T12:00:00Z (ISO 8601 format)"""
        config = SearchQueryConfig(
            created_after=datetime(2024, 1, 1, 12, 0, 0),
        )
        assert "created>2024-01-01T12:00:00Z" in config.to_query()

    def test_date_as_string(self) -> None:
        """Test passing date as string directly."""
        config = SearchQueryConfig(created_after="2024-01-01")
        assert "created>2024-01-01" in config.to_query()


class TestCustomFields:
    """Test custom field query generation based on Zendesk docs."""

    def test_custom_field_string_value(self) -> None:
        """Test: custom_field_12345:premium"""
        config = SearchQueryConfig(custom_fields={12345: "premium"})
        assert "custom_field_12345:premium" in config.to_query()

    def test_custom_field_boolean_value(self) -> None:
        """Test: custom_field_67890:True (checkbox)"""
        config = SearchQueryConfig(custom_fields={67890: True})
        assert "custom_field_67890:True" in config.to_query()

    def test_multiple_custom_fields(self) -> None:
        """Test multiple custom fields."""
        config = SearchQueryConfig(
            custom_fields={
                11111: "value1",
                22222: "value2",
            }
        )
        query = config.to_query()
        assert "custom_field_11111:value1" in query
        assert "custom_field_22222:value2" in query


class TestUserSearchQueries:
    """Test user search query generation based on Zendesk docs."""

    def test_user_type(self) -> None:
        """Test: type:user"""
        config = SearchQueryConfig(type=SearchType.USER)
        assert "type:user" in config.to_query()

    def test_user_role_filter(self) -> None:
        """Test: role:admin role:agent"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            role=["admin", "agent"],
        )
        query = config.to_query()
        assert "type:user" in query
        assert "role:admin" in query
        assert "role:agent" in query

    def test_user_email_filter(self) -> None:
        """Test: email:user@example.com"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            email="user@example.com",
        )
        assert "email:user@example.com" in config.to_query()

    def test_user_name_filter(self) -> None:
        """Test: name:John"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            name="John",
        )
        assert "name:John" in config.to_query()

    def test_user_verified_filter(self) -> None:
        """Test: is_verified:true"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            is_verified=True,
        )
        assert "is_verified:true" in config.to_query()

    def test_user_suspended_filter(self) -> None:
        """Test: is_suspended:true"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            is_suspended=True,
        )
        assert "is_suspended:true" in config.to_query()

    def test_user_organization_filter(self) -> None:
        """Test: organization:12345 for users"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            organization_id=12345,
        )
        assert "organization:12345" in config.to_query()

    def test_user_external_id_filter(self) -> None:
        """Test: external_id:abc123"""
        config = SearchQueryConfig(
            type=SearchType.USER,
            external_id="abc123",
        )
        assert "external_id:abc123" in config.to_query()

    def test_user_notes_filter(self) -> None:
        """Test: notes:"VIP customer" """
        config = SearchQueryConfig(
            type=SearchType.USER,
            notes="VIP customer",
        )
        assert 'notes:"VIP customer"' in config.to_query()


class TestOrganizationSearchQueries:
    """Test organization search query generation based on Zendesk docs."""

    def test_organization_type(self) -> None:
        """Test: type:organization"""
        config = SearchQueryConfig(type=SearchType.ORGANIZATION)
        assert "type:organization" in config.to_query()

    def test_organization_name_filter(self) -> None:
        """Test: name:Acme"""
        config = SearchQueryConfig(
            type=SearchType.ORGANIZATION,
            name="Acme",
        )
        assert "name:Acme" in config.to_query()

    def test_organization_tags_filter(self) -> None:
        """Test: tags:enterprise"""
        config = SearchQueryConfig(
            type=SearchType.ORGANIZATION,
            tags=["enterprise"],
        )
        assert "tags:enterprise" in config.to_query()

    def test_organization_external_id(self) -> None:
        """Test: external_id:org123"""
        config = SearchQueryConfig(
            type=SearchType.ORGANIZATION,
            external_id="org123",
        )
        assert "external_id:org123" in config.to_query()


class TestSorting:
    """Test sorting query generation based on Zendesk docs."""

    def test_order_by_created(self) -> None:
        """Test: order_by:created_at"""
        config = SearchQueryConfig(order_by="created_at")
        assert "order_by:created_at" in config.to_query()

    def test_sort_descending(self) -> None:
        """Test: sort:desc"""
        config = SearchQueryConfig(sort=SortOrder.DESC)
        assert "sort:desc" in config.to_query()

    def test_order_by_with_sort(self) -> None:
        """Test: order_by:updated_at sort:asc"""
        config = SearchQueryConfig(
            order_by="updated_at",
            sort=SortOrder.ASC,
        )
        query = config.to_query()
        assert "order_by:updated_at" in query
        assert "sort:asc" in query


class TestRawQueryAppend:
    """Test raw query string appending for advanced use cases."""

    def test_raw_query_append(self) -> None:
        """Test appending raw query for unsupported fields."""
        config = SearchQueryConfig(
            status=["open"],
            raw_query="fieldvalue:special",
        )
        query = config.to_query()
        assert "status:open" in query
        assert "fieldvalue:special" in query


class TestComplexQueries:
    """Test complex real-world query scenarios."""

    def test_high_priority_open_tickets_for_org(self) -> None:
        """Common use case: Find urgent open tickets for an organization."""
        config = SearchQueryConfig(
            status=["open", "pending"],
            priority=["high", "urgent"],
            organization_id=12345,
        )
        query = config.to_query()
        assert "type:ticket" in query
        assert "status:open" in query
        assert "status:pending" in query
        assert "priority:high" in query
        assert "priority:urgent" in query
        assert "organization:12345" in query

    def test_unassigned_tickets_last_week(self) -> None:
        """Common use case: Find unassigned tickets from last 7 days."""
        config = SearchQueryConfig(
            status=["open", "new"],
            assignee_id="none",
            created_after=date(2024, 1, 1),
        )
        query = config.to_query()
        assert "assignee:none" in query
        assert "created>2024-01-01" in query

    def test_vip_tickets_excluding_spam(self) -> None:
        """Common use case: VIP tickets excluding spam."""
        config = SearchQueryConfig(
            status=["open"],
            tags=["vip", "enterprise"],
            exclude_tags=["spam", "test"],
        )
        query = config.to_query()
        assert "tags:vip" in query
        assert "tags:enterprise" in query
        assert "-tags:spam" in query
        assert "-tags:test" in query

    def test_agent_search_verified_only(self) -> None:
        """Common use case: Find verified agent users."""
        config = SearchQueryConfig(
            type=SearchType.USER,
            role=["agent"],
            is_verified=True,
            is_suspended=False,
        )
        query = config.to_query()
        assert "type:user" in query
        assert "role:agent" in query
        assert "is_verified:true" in query
        assert "is_suspended:false" in query


class TestEnumValues:
    """Test that enum values are correctly converted."""

    def test_ticket_status_enum(self) -> None:
        """Test TicketStatus enum values."""
        config = SearchQueryConfig(status=[TicketStatus.OPEN, TicketStatus.PENDING])
        query = config.to_query()
        assert "status:open" in query
        assert "status:pending" in query

    def test_ticket_priority_enum(self) -> None:
        """Test TicketPriority enum values."""
        config = SearchQueryConfig(priority=[TicketPriority.HIGH, TicketPriority.URGENT])
        query = config.to_query()
        assert "priority:high" in query
        assert "priority:urgent" in query

    def test_ticket_type_enum(self) -> None:
        """Test TicketType enum values."""
        config = SearchQueryConfig(ticket_type=[TicketType.INCIDENT, TicketType.PROBLEM])
        query = config.to_query()
        assert "ticket_type:incident" in query
        assert "ticket_type:problem" in query

    def test_ticket_channel_enum(self) -> None:
        """Test TicketChannel enum values."""
        config = SearchQueryConfig(via=[TicketChannel.EMAIL, TicketChannel.WEB])
        query = config.to_query()
        assert "via:email" in query
        assert "via:web" in query

    def test_user_role_enum(self) -> None:
        """Test UserRole enum values."""
        config = SearchQueryConfig(
            type=SearchType.USER,
            role=[UserRole.ADMIN, UserRole.AGENT],
        )
        query = config.to_query()
        assert "role:admin" in query
        assert "role:agent" in query


class TestQueryStringMethods:
    """Test __str__ and __repr__ methods."""

    def test_str_returns_query(self) -> None:
        """Test that str() returns the query string."""
        config = SearchQueryConfig(status=["open"])
        assert str(config) == config.to_query()

    def test_repr_contains_query(self) -> None:
        """Test that repr contains the query string."""
        config = SearchQueryConfig(status=["open"])
        assert "type:ticket" in repr(config)
        assert "status:open" in repr(config)


class TestFactoryMethods:
    """Test factory classmethods for type-specific configurations."""

    def test_tickets_factory_sets_type(self) -> None:
        """Test that tickets() factory sets type to TICKET."""
        config = SearchQueryConfig.tickets(status=["open"])
        assert config.type == SearchType.TICKET
        assert "type:ticket" in config.to_query()

    def test_tickets_factory_with_all_fields(self) -> None:
        """Test tickets() factory with ticket-specific fields."""
        config = SearchQueryConfig.tickets(
            status=["open", "pending"],
            priority=["high"],
            organization_id=12345,
            tags=["vip"],
        )
        query = config.to_query()
        assert "status:open" in query
        assert "status:pending" in query
        assert "priority:high" in query
        assert "organization:12345" in query
        assert "tags:vip" in query

    def test_users_factory_sets_type(self) -> None:
        """Test that users() factory sets type to USER."""
        config = SearchQueryConfig.users(role=["admin"])
        assert config.type == SearchType.USER
        assert "type:user" in config.to_query()

    def test_users_factory_with_all_fields(self) -> None:
        """Test users() factory with user-specific fields."""
        config = SearchQueryConfig.users(
            role=["admin", "agent"],
            is_verified=True,
            organization_id=12345,
        )
        query = config.to_query()
        assert "role:admin" in query
        assert "role:agent" in query
        assert "is_verified:true" in query
        assert "organization:12345" in query

    def test_organizations_factory_sets_type(self) -> None:
        """Test that organizations() factory sets type to ORGANIZATION."""
        config = SearchQueryConfig.organizations(name="Acme")
        assert config.type == SearchType.ORGANIZATION
        assert "type:organization" in config.to_query()

    def test_organizations_factory_with_all_fields(self) -> None:
        """Test organizations() factory with org-specific fields."""
        config = SearchQueryConfig.organizations(
            name="Acme",
            tags=["enterprise"],
            external_id="ext-123",
        )
        query = config.to_query()
        assert "name:Acme" in query
        assert "tags:enterprise" in query
        assert "external_id:ext-123" in query

    def test_factory_with_common_fields(self) -> None:
        """Test that factory methods accept common fields."""
        config = SearchQueryConfig.tickets(
            status=["open"],
            created_after=date(2024, 1, 1),
            order_by="created_at",
            sort=SortOrder.DESC,
        )
        query = config.to_query()
        assert "created>2024-01-01" in query
        assert "order_by:created_at" in query
        assert "sort:desc" in query

    def test_empty_factory_creates_valid_config(self) -> None:
        """Test that empty factory calls create valid configs."""
        tickets = SearchQueryConfig.tickets()
        users = SearchQueryConfig.users()
        orgs = SearchQueryConfig.organizations()

        assert tickets.type == SearchType.TICKET
        assert users.type == SearchType.USER
        assert orgs.type == SearchType.ORGANIZATION

        assert "type:ticket" in tickets.to_query()
        assert "type:user" in users.to_query()
        assert "type:organization" in orgs.to_query()

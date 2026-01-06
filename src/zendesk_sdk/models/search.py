"""Search query configuration for Zendesk API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchType(str, Enum):
    """Type of resource to search."""

    TICKET = "ticket"
    USER = "user"
    ORGANIZATION = "organization"


class TicketStatus(str, Enum):
    """Ticket status values."""

    NEW = "new"
    OPEN = "open"
    PENDING = "pending"
    HOLD = "hold"
    SOLVED = "solved"
    CLOSED = "closed"


# Literal type for string autocomplete in IDE
TicketStatusLiteral = Literal["new", "open", "pending", "hold", "solved", "closed"]
# Union type: accepts both Enum and string literals
TicketStatusInput = Union[TicketStatus, TicketStatusLiteral]


class TicketPriority(str, Enum):
    """Ticket priority values."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Literal type for string autocomplete in IDE
TicketPriorityLiteral = Literal["low", "normal", "high", "urgent"]
# Union type: accepts both Enum and string literals
TicketPriorityInput = Union[TicketPriority, TicketPriorityLiteral]


class TicketType(str, Enum):
    """Ticket type values."""

    QUESTION = "question"
    INCIDENT = "incident"
    PROBLEM = "problem"
    TASK = "task"


# Literal type for string autocomplete in IDE
TicketTypeLiteral = Literal["question", "incident", "problem", "task"]
# Union type: accepts both Enum and string literals
TicketTypeInput = Union[TicketType, TicketTypeLiteral]


class TicketChannel(str, Enum):
    """Ticket channel (via) values."""

    EMAIL = "email"
    WEB = "web"
    CHAT = "chat"
    API = "api"
    PHONE = "phone"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class UserRole(str, Enum):
    """User role values."""

    ADMIN = "admin"
    AGENT = "agent"
    END_USER = "end-user"


class SortOrder(str, Enum):
    """Sort order for search results."""

    ASC = "asc"
    DESC = "desc"


class SearchQueryConfig(BaseModel):
    """Unified search configuration for all Zendesk resources.

    This model provides a type-safe way to build Zendesk search queries
    instead of manually constructing query strings.

    Example:
        # Search for open/pending high-priority tickets
        config = SearchQueryConfig(
            status=["open", "pending"],
            priority=["high", "urgent"],
            organization_id=12345,
        )
        tickets = await client.search(config)

        # Search for admin users
        config = SearchQueryConfig(
            type=SearchType.USER,
            role=["admin"],
        )
        users = await client.search(config)

        # Search for organizations
        config = SearchQueryConfig(
            type=SearchType.ORGANIZATION,
            name="Acme",
        )
        orgs = await client.search(config)
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
    )

    # === Resource type ===
    type: SearchType = Field(
        default=SearchType.TICKET,
        description="Type of resource to search (ticket, user, organization)",
    )

    # === Common fields (all types) ===
    created_after: Optional[Union[date, datetime, str]] = Field(
        None, description="Search items created after this date"
    )
    created_before: Optional[Union[date, datetime, str]] = Field(
        None, description="Search items created before this date"
    )
    updated_after: Optional[Union[date, datetime, str]] = Field(
        None, description="Search items updated after this date"
    )
    updated_before: Optional[Union[date, datetime, str]] = Field(
        None, description="Search items updated before this date"
    )
    tags: Optional[List[str]] = Field(None, description="Include items with these tags (OR logic)")
    exclude_tags: Optional[List[str]] = Field(None, description="Exclude items with these tags")

    # === Ticket-specific fields ===
    status: Optional[List[Union[TicketStatus, str]]] = Field(None, description="Ticket statuses to search (OR logic)")
    priority: Optional[List[Union[TicketPriority, str]]] = Field(
        None, description="Ticket priorities to search (OR logic)"
    )
    ticket_type: Optional[List[Union[TicketType, str]]] = Field(None, description="Ticket types to search (OR logic)")
    organization_id: Optional[int] = Field(None, description="Filter by organization ID")
    requester_id: Optional[Union[int, Literal["me", "none"]]] = Field(
        None, description="Filter by requester ID, 'me', or 'none'"
    )
    assignee_id: Optional[Union[int, Literal["me", "none"]]] = Field(
        None, description="Filter by assignee ID, 'me', or 'none'"
    )
    submitter_id: Optional[Union[int, Literal["me", "none"]]] = Field(
        None, description="Filter by submitter ID, 'me', or 'none'"
    )
    group_id: Optional[int] = Field(None, description="Filter by group ID")
    brand_id: Optional[int] = Field(None, description="Filter by brand ID (Enterprise)")
    via: Optional[List[Union[TicketChannel, str]]] = Field(None, description="Filter by channel (OR logic)")
    subject: Optional[str] = Field(None, description="Search in ticket subject")
    description: Optional[str] = Field(None, description="Search in ticket description/comments")
    solved_after: Optional[Union[date, datetime, str]] = Field(None, description="Tickets solved after this date")
    solved_before: Optional[Union[date, datetime, str]] = Field(None, description="Tickets solved before this date")
    due_date_after: Optional[Union[date, datetime, str]] = Field(None, description="Task tickets due after this date")
    due_date_before: Optional[Union[date, datetime, str]] = Field(None, description="Task tickets due before this date")
    has_attachment: Optional[bool] = Field(None, description="Filter tickets with/without attachments")
    custom_fields: Optional[Dict[int, Any]] = Field(
        None, description="Search by custom field values: {field_id: value}"
    )

    # === User-specific fields ===
    role: Optional[List[Union[UserRole, str]]] = Field(None, description="User roles to search (OR logic)")
    email: Optional[str] = Field(None, description="Search by user email")
    name: Optional[str] = Field(None, description="Search by user/organization name")
    phone: Optional[str] = Field(None, description="Search by user phone number")
    is_verified: Optional[bool] = Field(None, description="Filter verified users")
    is_suspended: Optional[bool] = Field(None, description="Filter suspended users")
    external_id: Optional[str] = Field(None, description="Search by external ID")
    notes: Optional[str] = Field(None, description="Search in user/org notes field")
    details: Optional[str] = Field(None, description="Search in user/org details field")

    # === Sorting ===
    order_by: Optional[str] = Field(
        None, description="Sort field (created_at, updated_at, priority, status, ticket_type)"
    )
    sort: Optional[SortOrder] = Field(None, description="Sort order (asc, desc)")

    # === Query limit ===
    raw_query: Optional[str] = Field(None, description="Append raw query string for advanced use cases")

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> "SearchQueryConfig":
        """Warn if using fields not applicable to the search type."""
        # This is a soft validation - we don't raise errors,
        # but fields for wrong types will be ignored in to_query()
        return self

    def _format_date(self, value: Union[date, datetime, str]) -> str:
        """Format date for Zendesk query."""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def _add_date_range(
        self,
        parts: List[str],
        field: str,
        after: Optional[Union[date, datetime, str]],
        before: Optional[Union[date, datetime, str]],
    ) -> None:
        """Add date range conditions to query parts."""
        if after:
            parts.append(f"{field}>{self._format_date(after)}")
        if before:
            parts.append(f"{field}<{self._format_date(before)}")

    def to_query(self) -> str:
        """Build Zendesk query string from config.

        Returns:
            Zendesk search query string ready for API call.
        """
        parts: List[str] = []

        # Add type (use .value for enum)
        type_value = self.type.value if isinstance(self.type, SearchType) else self.type
        parts.append(f"type:{type_value}")

        # === Common fields ===
        self._add_date_range(parts, "created", self.created_after, self.created_before)
        self._add_date_range(parts, "updated", self.updated_after, self.updated_before)

        if self.tags:
            for tag in self.tags:
                parts.append(f"tags:{tag}")
        if self.exclude_tags:
            for tag in self.exclude_tags:
                parts.append(f"-tags:{tag}")

        # === Ticket-specific fields ===
        if self.type == SearchType.TICKET:
            if self.status:
                for s in self.status:
                    parts.append(f"status:{s}")
            if self.priority:
                for p in self.priority:
                    parts.append(f"priority:{p}")
            if self.ticket_type:
                for t in self.ticket_type:
                    parts.append(f"ticket_type:{t}")
            if self.organization_id is not None:
                parts.append(f"organization:{self.organization_id}")
            if self.requester_id is not None:
                parts.append(f"requester:{self.requester_id}")
            if self.assignee_id is not None:
                parts.append(f"assignee:{self.assignee_id}")
            if self.submitter_id is not None:
                parts.append(f"submitter:{self.submitter_id}")
            if self.group_id is not None:
                parts.append(f"group:{self.group_id}")
            if self.brand_id is not None:
                parts.append(f"brand:{self.brand_id}")
            if self.via:
                for v in self.via:
                    parts.append(f"via:{v}")
            if self.subject:
                parts.append(f'subject:"{self.subject}"')
            if self.description:
                parts.append(f'description:"{self.description}"')
            self._add_date_range(parts, "solved", self.solved_after, self.solved_before)
            self._add_date_range(parts, "due_date", self.due_date_after, self.due_date_before)
            if self.has_attachment is not None:
                parts.append(f"has_attachment:{str(self.has_attachment).lower()}")
            if self.custom_fields:
                for field_id, value in self.custom_fields.items():
                    parts.append(f"custom_field_{field_id}:{value}")

        # === User-specific fields ===
        elif self.type == SearchType.USER:
            if self.role:
                for r in self.role:
                    parts.append(f"role:{r}")
            if self.email:
                parts.append(f"email:{self.email}")
            if self.name:
                parts.append(f"name:{self.name}")
            if self.phone:
                parts.append(f"phone:{self.phone}")
            if self.is_verified is not None:
                parts.append(f"is_verified:{str(self.is_verified).lower()}")
            if self.is_suspended is not None:
                parts.append(f"is_suspended:{str(self.is_suspended).lower()}")
            if self.external_id:
                parts.append(f"external_id:{self.external_id}")
            if self.notes:
                parts.append(f'notes:"{self.notes}"')
            if self.details:
                parts.append(f'details:"{self.details}"')
            if self.organization_id is not None:
                parts.append(f"organization:{self.organization_id}")

        # === Organization-specific fields ===
        elif self.type == SearchType.ORGANIZATION:
            if self.name:
                parts.append(f"name:{self.name}")
            if self.external_id:
                parts.append(f"external_id:{self.external_id}")
            if self.notes:
                parts.append(f'notes:"{self.notes}"')
            if self.details:
                parts.append(f'details:"{self.details}"')

        # === Sorting ===
        if self.order_by:
            parts.append(f"order_by:{self.order_by}")
        if self.sort:
            parts.append(f"sort:{self.sort}")

        # === Raw query append ===
        if self.raw_query:
            parts.append(self.raw_query)

        return " ".join(parts)

    def __str__(self) -> str:
        """Return the query string representation."""
        return self.to_query()

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"SearchQueryConfig({self.to_query()!r})"

    # === Factory methods ===

    @classmethod
    def tickets(
        cls,
        *,
        # Ticket-specific
        status: Optional[List[Union[TicketStatus, str]]] = None,
        priority: Optional[List[Union[TicketPriority, str]]] = None,
        ticket_type: Optional[List[Union[TicketType, str]]] = None,
        organization_id: Optional[int] = None,
        requester_id: Optional[Union[int, Literal["me", "none"]]] = None,
        assignee_id: Optional[Union[int, Literal["me", "none"]]] = None,
        submitter_id: Optional[Union[int, Literal["me", "none"]]] = None,
        group_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        via: Optional[List[Union[TicketChannel, str]]] = None,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        solved_after: Optional[Union[date, datetime, str]] = None,
        solved_before: Optional[Union[date, datetime, str]] = None,
        due_date_after: Optional[Union[date, datetime, str]] = None,
        due_date_before: Optional[Union[date, datetime, str]] = None,
        has_attachment: Optional[bool] = None,
        custom_fields: Optional[Dict[int, Any]] = None,
        # Common
        created_after: Optional[Union[date, datetime, str]] = None,
        created_before: Optional[Union[date, datetime, str]] = None,
        updated_after: Optional[Union[date, datetime, str]] = None,
        updated_before: Optional[Union[date, datetime, str]] = None,
        tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        sort: Optional[SortOrder] = None,
        raw_query: Optional[str] = None,
    ) -> "SearchQueryConfig":
        """Create a ticket search configuration.

        Example:
            config = SearchQueryConfig.tickets(
                status=["open", "pending"],
                priority=["high", "urgent"],
                organization_id=12345,
            )
            async for ticket in client.search.tickets(config):
                print(ticket.subject)
        """
        return cls(
            type=SearchType.TICKET,
            status=status,
            priority=priority,
            ticket_type=ticket_type,
            organization_id=organization_id,
            requester_id=requester_id,
            assignee_id=assignee_id,
            submitter_id=submitter_id,
            group_id=group_id,
            brand_id=brand_id,
            via=via,
            subject=subject,
            description=description,
            solved_after=solved_after,
            solved_before=solved_before,
            due_date_after=due_date_after,
            due_date_before=due_date_before,
            has_attachment=has_attachment,
            custom_fields=custom_fields,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            tags=tags,
            exclude_tags=exclude_tags,
            order_by=order_by,
            sort=sort,
            raw_query=raw_query,
        )

    @classmethod
    def users(
        cls,
        *,
        # User-specific
        role: Optional[List[Union[UserRole, str]]] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        is_verified: Optional[bool] = None,
        is_suspended: Optional[bool] = None,
        external_id: Optional[str] = None,
        notes: Optional[str] = None,
        details: Optional[str] = None,
        organization_id: Optional[int] = None,
        # Common
        created_after: Optional[Union[date, datetime, str]] = None,
        created_before: Optional[Union[date, datetime, str]] = None,
        updated_after: Optional[Union[date, datetime, str]] = None,
        updated_before: Optional[Union[date, datetime, str]] = None,
        tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        sort: Optional[SortOrder] = None,
        raw_query: Optional[str] = None,
    ) -> "SearchQueryConfig":
        """Create a user search configuration.

        Example:
            config = SearchQueryConfig.users(
                role=["admin", "agent"],
                is_verified=True,
            )
            async for user in client.search.users(config):
                print(user.name)
        """
        return cls(
            type=SearchType.USER,
            role=role,
            email=email,
            name=name,
            phone=phone,
            is_verified=is_verified,
            is_suspended=is_suspended,
            external_id=external_id,
            notes=notes,
            details=details,
            organization_id=organization_id,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            tags=tags,
            exclude_tags=exclude_tags,
            order_by=order_by,
            sort=sort,
            raw_query=raw_query,
        )

    @classmethod
    def organizations(
        cls,
        *,
        # Organization-specific
        name: Optional[str] = None,
        external_id: Optional[str] = None,
        notes: Optional[str] = None,
        details: Optional[str] = None,
        # Common
        created_after: Optional[Union[date, datetime, str]] = None,
        created_before: Optional[Union[date, datetime, str]] = None,
        updated_after: Optional[Union[date, datetime, str]] = None,
        updated_before: Optional[Union[date, datetime, str]] = None,
        tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        sort: Optional[SortOrder] = None,
        raw_query: Optional[str] = None,
    ) -> "SearchQueryConfig":
        """Create an organization search configuration.

        Example:
            config = SearchQueryConfig.organizations(
                tags=["enterprise"],
                name="Acme",
            )
            async for org in client.search.organizations(config):
                print(org.name)
        """
        return cls(
            type=SearchType.ORGANIZATION,
            name=name,
            external_id=external_id,
            notes=notes,
            details=details,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            tags=tags,
            exclude_tags=exclude_tags,
            order_by=order_by,
            sort=sort,
            raw_query=raw_query,
        )

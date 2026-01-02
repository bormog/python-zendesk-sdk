"""Base model for all Zendesk API data models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


class ZendeskModel(BaseModel):
    """Base model for all Zendesk API responses."""

    model_config = ConfigDict(
        # Allow field aliases (id -> uid, etc.)
        populate_by_name=True,
        # Use enum values instead of enum names
        use_enum_values=True,
        # Validate assignment to fields
        validate_assignment=True,
        # Allow extra fields that aren't defined in the model
        extra="ignore",
        # Convert string dates to datetime objects
        str_to_lower=False,
        # Allow arbitrary types (for complex nested structures)
        arbitrary_types_allowed=True,
    )

    @field_serializer("*", when_used="json")
    def serialize_datetime(self, value: Any) -> Any:
        """Serialize datetime objects to ISO format strings."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def __str__(self) -> str:
        """String representation showing class name and key fields."""
        class_name = self.__class__.__name__
        # Try to find an ID field to display
        id_field = None
        for field in ["uid", "id", "name", "subject"]:
            if hasattr(self, field):
                id_field = f"{field}={getattr(self, field)!r}"
                break

        if id_field:
            return f"{class_name}({id_field})"
        return f"{class_name}()"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}({self.model_dump()})"

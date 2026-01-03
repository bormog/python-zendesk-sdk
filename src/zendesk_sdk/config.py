"""Configuration management for Zendesk SDK."""

import os
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class CacheConfig(BaseModel):
    """Cache configuration for Zendesk SDK.

    Controls TTL (time-to-live) and max size for different resource caches.
    Set enabled=False to disable caching entirely.
    """

    enabled: bool = Field(default=True, description="Enable/disable caching")

    # Users cache
    user_ttl: int = Field(default=300, description="User cache TTL in seconds (default: 5 min)", ge=0)
    user_maxsize: int = Field(default=1000, description="Max cached users", ge=1)

    # Organizations cache
    org_ttl: int = Field(default=600, description="Organization cache TTL in seconds (default: 10 min)", ge=0)
    org_maxsize: int = Field(default=500, description="Max cached organizations", ge=1)

    # Help Center cache
    article_ttl: int = Field(default=900, description="Article cache TTL in seconds (default: 15 min)", ge=0)
    article_maxsize: int = Field(default=500, description="Max cached articles", ge=1)

    category_ttl: int = Field(default=1800, description="Category cache TTL in seconds (default: 30 min)", ge=0)
    category_maxsize: int = Field(default=200, description="Max cached categories", ge=1)

    section_ttl: int = Field(default=1800, description="Section cache TTL in seconds (default: 30 min)", ge=0)
    section_maxsize: int = Field(default=200, description="Max cached sections", ge=1)


class ZendeskConfig(BaseModel):
    """Configuration for Zendesk API client.

    This class handles authentication and connection settings for the Zendesk API.
    It uses email/token authentication method.
    Environment variables can be used for configuration.
    """

    subdomain: str = Field(
        ...,
        description="Zendesk subdomain (e.g., 'mycompany' for mycompany.zendesk.com)",
        min_length=1,
    )
    email: str = Field(
        ...,
        description="User email for authentication",
        min_length=1,
    )
    token: str = Field(
        ...,
        description="API token for authentication",
        min_length=1,
    )
    timeout: float = Field(
        default=30.0,
        description="HTTP request timeout in seconds",
        gt=0,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0,
    )
    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Cache configuration",
    )

    def __init__(self, **data: Any) -> None:
        # Load from environment variables if not provided
        if "subdomain" not in data:
            data["subdomain"] = os.getenv("ZENDESK_SUBDOMAIN", data.get("subdomain"))
        if "email" not in data:
            data["email"] = os.getenv("ZENDESK_EMAIL", data.get("email"))
        if "token" not in data:
            data["token"] = os.getenv("ZENDESK_TOKEN", data.get("token"))

        super().__init__(**data)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        """Validate subdomain format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Subdomain can only contain letters, numbers, hyphens and underscores")
        return v.lower()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def endpoint(self) -> str:
        """Generate the base API endpoint URL."""
        return f"https://{self.subdomain}.zendesk.com/api/v2"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def auth_tuple(self) -> tuple[str, str]:
        """Generate authentication tuple for HTTP requests."""
        return (f"{self.email}/token", self.token)

    def __repr__(self) -> str:
        """String representation without exposing credentials."""
        return (
            f"ZendeskConfig("
            f"subdomain='{self.subdomain}', "
            f"email='{self.email}', "
            f"timeout={self.timeout}, "
            f"max_retries={self.max_retries})"
        )

"""Configuration management for Zendesk SDK."""

import os
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


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

    # Groups cache
    group_ttl: int = Field(default=600, description="Group cache TTL in seconds (default: 10 min)", ge=0)
    group_maxsize: int = Field(default=500, description="Max cached groups", ge=1)

    # Help Center cache
    article_ttl: int = Field(default=900, description="Article cache TTL in seconds (default: 15 min)", ge=0)
    article_maxsize: int = Field(default=500, description="Max cached articles", ge=1)

    category_ttl: int = Field(default=1800, description="Category cache TTL in seconds (default: 30 min)", ge=0)
    category_maxsize: int = Field(default=200, description="Max cached categories", ge=1)

    section_ttl: int = Field(default=1800, description="Section cache TTL in seconds (default: 30 min)", ge=0)
    section_maxsize: int = Field(default=200, description="Max cached sections", ge=1)


class ZendeskConfig(BaseModel):
    """Configuration for Zendesk API client.

    Supports two authentication methods (mutually exclusive):
    - Token auth: email + token (Basic Auth)
    - OAuth: oauth_token (Bearer token)

    Environment variables: ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_TOKEN, ZENDESK_OAUTH_TOKEN.
    """

    subdomain: str = Field(
        ...,
        description="Zendesk subdomain (e.g., 'mycompany' for mycompany.zendesk.com)",
        min_length=1,
    )
    email: Optional[str] = Field(
        default=None,
        description="User email for token authentication",
    )
    token: Optional[str] = Field(
        default=None,
        description="API token for token authentication",
    )
    oauth_token: Optional[str] = Field(
        default=None,
        description="OAuth token for Bearer authentication",
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
    proactive_ratelimit: Optional[int] = Field(
        default=None,
        description="Start sleeping when X-Rate-Limit-Remaining drops below this threshold",
        ge=1,
    )
    proactive_ratelimit_request_interval: int = Field(
        default=10,
        description="Seconds to wait between requests when proactive rate limit threshold is reached",
        ge=1,
    )
    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Cache configuration",
    )

    def __init__(self, **data: Any) -> None:
        # Load from environment variables if not provided
        if "subdomain" not in data:
            data["subdomain"] = os.getenv("ZENDESK_SUBDOMAIN", data.get("subdomain"))

        # Only load env vars for one auth method — explicit args take precedence
        has_explicit_token_auth = "email" in data or "token" in data
        has_explicit_oauth = "oauth_token" in data

        if not has_explicit_token_auth and not has_explicit_oauth:
            # Nothing explicit — try env vars, token auth first
            env_email = os.getenv("ZENDESK_EMAIL")
            env_token = os.getenv("ZENDESK_TOKEN")
            env_oauth = os.getenv("ZENDESK_OAUTH_TOKEN")
            if env_email or env_token:
                data.setdefault("email", env_email)
                data.setdefault("token", env_token)
            elif env_oauth:
                data.setdefault("oauth_token", env_oauth)
        elif has_explicit_token_auth and not has_explicit_oauth:
            # Token auth explicit — fill missing from env
            data.setdefault("email", os.getenv("ZENDESK_EMAIL"))
            data.setdefault("token", os.getenv("ZENDESK_TOKEN"))
        elif has_explicit_oauth and not has_explicit_token_auth:
            # OAuth explicit — only fill oauth from env
            data.setdefault("oauth_token", os.getenv("ZENDESK_OAUTH_TOKEN"))

        super().__init__(**data)

    @model_validator(mode="after")
    def validate_auth(self) -> "ZendeskConfig":
        """Validate that exactly one auth method is provided."""
        has_token_auth = self.email is not None or self.token is not None
        has_oauth = self.oauth_token is not None

        if has_token_auth and has_oauth:
            raise ValueError("Cannot use both token auth (email/token) and oauth_token simultaneously")

        if not has_token_auth and not has_oauth:
            raise ValueError("Either email/token or oauth_token must be provided")

        if has_token_auth:
            if not self.email or not self.token:
                raise ValueError("Both email and token are required for token authentication")
            if "@" not in self.email:
                raise ValueError("Invalid email format")

        return self

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
    def auth_tuple(self) -> Optional[tuple[str, str]]:
        """Generate authentication tuple for HTTP requests. None for OAuth mode."""
        if self.email and self.token:
            return f"{self.email}/token", self.token
        return None

    def __repr__(self) -> str:
        """String representation without exposing credentials."""
        auth_info = f"email='{self.email}'" if self.email else "oauth=True"
        parts = [
            f"subdomain='{self.subdomain}'",
            auth_info,
            f"timeout={self.timeout}",
            f"max_retries={self.max_retries}",
        ]
        if self.proactive_ratelimit is not None:
            parts.append(f"proactive_ratelimit={self.proactive_ratelimit}")
        return f"ZendeskConfig({', '.join(parts)})"

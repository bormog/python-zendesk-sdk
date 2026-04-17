"""Tests for ZendeskConfig."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from zendesk_sdk.config import ZendeskConfig


class TestZendeskConfig:
    """Test cases for ZendeskConfig class."""

    def test_basic_config_with_token(self):
        """Test creating config with email/token authentication."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="api_token_123",
        )

        assert config.subdomain == "test"
        assert config.email == "user@example.com"
        assert config.token == "api_token_123"
        assert config.oauth_token is None
        assert config.endpoint == "https://test.zendesk.com/api/v2"
        assert config.auth_tuple == ("user@example.com/token", "api_token_123")

    def test_basic_config_with_oauth_token(self):
        """Test creating config with OAuth token authentication."""
        config = ZendeskConfig(
            subdomain="test",
            oauth_token="oauth_token_123",
        )

        assert config.subdomain == "test"
        assert config.oauth_token == "oauth_token_123"
        assert config.email is None
        assert config.token is None
        assert config.auth_tuple is None
        assert config.endpoint == "https://test.zendesk.com/api/v2"

    def test_invalid_timeout(self):
        """Test invalid timeout values."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                token="api_token_123",
                timeout=0.0,  # Must be > 0
            )

    def test_invalid_max_retries(self):
        """Test invalid max_retries values."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                token="api_token_123",
                max_retries=-1,  # Must be >= 0
            )

    def test_missing_all_auth(self):
        """Test that at least one auth method is required."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError, match="Either email/token or oauth_token must be provided"):
                ZendeskConfig(subdomain="test")

    def test_both_auth_methods(self):
        """Test that token and oauth_token are mutually exclusive."""
        with pytest.raises(ValidationError, match="Cannot use both"):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                token="api_token_123",
                oauth_token="oauth_token_123",
            )

    def test_email_without_token(self):
        """Test that email requires token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError, match="Both email and token are required"):
                ZendeskConfig(
                    subdomain="test",
                    email="user@example.com",
                )

    def test_token_without_email(self):
        """Test that token requires email."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError, match="Both email and token are required"):
                ZendeskConfig(
                    subdomain="test",
                    token="api_token_123",
                )

    def test_invalid_email(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError, match="Invalid email format"):
            ZendeskConfig(
                subdomain="test",
                email="invalid-email",
                token="api_token_123",
            )

    def test_env_variables_token_auth(self):
        """Test loading token auth config from environment variables."""
        with patch.dict(
            os.environ,
            {
                "ZENDESK_SUBDOMAIN": "env-test",
                "ZENDESK_EMAIL": "env@example.com",
                "ZENDESK_TOKEN": "env_token_123",
            },
        ):
            config = ZendeskConfig()
            assert config.subdomain == "env-test"
            assert config.email == "env@example.com"
            assert config.token == "env_token_123"

    def test_env_variables_oauth(self):
        """Test loading OAuth config from environment variables."""
        with patch.dict(
            os.environ,
            {
                "ZENDESK_SUBDOMAIN": "env-test",
                "ZENDESK_OAUTH_TOKEN": "env_oauth_123",
            },
            clear=True,
        ):
            config = ZendeskConfig()
            assert config.subdomain == "env-test"
            assert config.oauth_token == "env_oauth_123"
            assert config.auth_tuple is None

    def test_repr_hides_token(self):
        """Test that repr doesn't expose token."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="secret_token",
        )
        repr_str = repr(config)
        assert "secret_token" not in repr_str
        assert "test" in repr_str
        assert "user@example.com" in repr_str

    def test_repr_hides_oauth_token(self):
        """Test that repr doesn't expose oauth_token."""
        config = ZendeskConfig(
            subdomain="test",
            oauth_token="secret_oauth_token",
        )
        repr_str = repr(config)
        assert "secret_oauth_token" not in repr_str
        assert "oauth=True" in repr_str


class TestRateLimitConfig:
    """Test cases for proactive rate limiting configuration."""

    def test_default_ratelimit_config(self):
        """Test default values for rate limiting fields."""
        config = ZendeskConfig(subdomain="test", email="user@example.com", token="abc123")
        assert config.proactive_ratelimit is None
        assert config.proactive_ratelimit_request_interval == 10

    def test_proactive_ratelimit(self):
        """Test setting proactive_ratelimit threshold."""
        config = ZendeskConfig(subdomain="test", email="user@example.com", token="abc123", proactive_ratelimit=50)
        assert config.proactive_ratelimit == 50

    def test_proactive_ratelimit_with_custom_interval(self):
        """Test setting proactive_ratelimit with custom interval."""
        config = ZendeskConfig(
            subdomain="test",
            email="user@example.com",
            token="abc123",
            proactive_ratelimit=100,
            proactive_ratelimit_request_interval=15,
        )
        assert config.proactive_ratelimit == 100
        assert config.proactive_ratelimit_request_interval == 15

    def test_proactive_ratelimit_invalid_zero(self):
        """Test that proactive_ratelimit=0 raises ValidationError."""
        with pytest.raises(ValidationError):
            ZendeskConfig(subdomain="test", email="user@example.com", token="abc123", proactive_ratelimit=0)

    def test_proactive_ratelimit_invalid_negative(self):
        """Test that proactive_ratelimit=-1 raises ValidationError."""
        with pytest.raises(ValidationError):
            ZendeskConfig(subdomain="test", email="user@example.com", token="abc123", proactive_ratelimit=-1)

    def test_proactive_ratelimit_interval_invalid_zero(self):
        """Test that proactive_ratelimit_request_interval=0 raises ValidationError."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                token="abc123",
                proactive_ratelimit_request_interval=0,
            )

    def test_repr_includes_proactive_ratelimit(self):
        """Test that repr shows proactive_ratelimit when set."""
        config = ZendeskConfig(subdomain="test", email="user@example.com", token="abc123", proactive_ratelimit=50)
        repr_str = repr(config)
        assert "proactive_ratelimit=50" in repr_str

    def test_repr_excludes_proactive_ratelimit_when_none(self):
        """Test that repr omits proactive_ratelimit when None."""
        config = ZendeskConfig(subdomain="test", email="user@example.com", token="abc123")
        repr_str = repr(config)
        assert "proactive_ratelimit" not in repr_str

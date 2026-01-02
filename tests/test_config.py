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
        assert config.endpoint == "https://test.zendesk.com/api/v2"
        assert config.auth_tuple == ("user@example.com/token", "api_token_123")

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

    def test_missing_token(self):
        """Test that token is required."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError):
                ZendeskConfig(
                    subdomain="test",
                    email="user@example.com",
                )

    def test_invalid_email(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="invalid-email",
                token="api_token_123",
            )

    def test_env_variables(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {
            "ZENDESK_SUBDOMAIN": "env-test",
            "ZENDESK_EMAIL": "env@example.com",
            "ZENDESK_TOKEN": "env_token_123",
        }):
            config = ZendeskConfig()
            assert config.subdomain == "env-test"
            assert config.email == "env@example.com"
            assert config.token == "env_token_123"

    def test_repr_hides_credentials(self):
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

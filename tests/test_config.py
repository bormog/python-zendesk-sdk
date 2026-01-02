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
        assert config.password is None
        assert config.token == "api_token_123"
        assert config.auth_type == "token"
        assert config.endpoint == "https://test.zendesk.com/api/v2"
        assert config.auth_tuple == ("user@example.com/token", "api_token_123")


    def test_invalid_timeout(self):
        """Test invalid timeout values."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                password="secret",
                timeout=0.0,  # Must be > 0
            )

    def test_invalid_max_retries(self):
        """Test invalid max_retries values."""
        with pytest.raises(ValidationError):
            ZendeskConfig(
                subdomain="test",
                email="user@example.com",
                password="secret",
                max_retries=-1,  # Must be >= 0
            )


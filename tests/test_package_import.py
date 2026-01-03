"""Tests for package imports and basic functionality."""


class TestPackageImport:
    """Test package import functionality."""

    def test_main_package_import(self):
        """Test importing the main package."""
        import zendesk_sdk

        assert hasattr(zendesk_sdk, "__version__")
        assert zendesk_sdk.__version__ == "0.2.0"

    def test_client_import(self):
        """Test importing ZendeskClient."""
        from zendesk_sdk import ZendeskClient

        assert ZendeskClient is not None

    def test_config_import(self):
        """Test importing ZendeskConfig."""
        from zendesk_sdk import ZendeskConfig

        assert ZendeskConfig is not None

    def test_exceptions_import(self):
        """Test importing exceptions."""
        from zendesk_sdk import (
            ZendeskAuthException,
            ZendeskBaseException,
            ZendeskHTTPException,
            ZendeskPaginationException,
            ZendeskRateLimitException,
        )

        assert ZendeskBaseException is not None
        assert ZendeskHTTPException is not None
        assert ZendeskAuthException is not None
        assert ZendeskRateLimitException is not None
        assert ZendeskPaginationException is not None

    def test_models_import(self):
        """Test importing base model."""
        from zendesk_sdk.models import ZendeskModel

        assert ZendeskModel is not None

    def test_all_exports(self):
        """Test that __all__ includes expected exports."""
        import zendesk_sdk

        expected_exports = [
            "ZendeskClient",
            "ZendeskConfig",
            "ZendeskBaseException",
            "ZendeskHTTPException",
            "ZendeskAuthException",
            "ZendeskRateLimitException",
            "ZendeskPaginationException",
        ]

        for export in expected_exports:
            assert export in zendesk_sdk.__all__
            assert hasattr(zendesk_sdk, export)

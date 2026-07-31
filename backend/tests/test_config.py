"""Tests for the App configuration module."""

import pytest


class TestSettings:
    """Verify the pydantic-settings configuration."""

    def test_default_app_name(self):
        """Settings.app_name should default to 'Dental AI'."""
        from app.core.config import Settings
        s = Settings()
        assert s.app_name == "Dental AI"

    def test_default_version(self):
        """Settings.version should default to '0.1.0'."""
        from app.core.config import Settings
        s = Settings()
        assert s.version == "0.1.0"

    def test_default_upload_max_size(self):
        """Settings.upload_max_size_mb should default to 50."""
        from app.core.config import Settings
        s = Settings()
        assert s.upload_max_size_mb == 50

    def test_default_confidence(self):
        """Settings.default_confidence should default to 0.5."""
        from app.core.config import Settings
        s = Settings()
        assert s.default_confidence == 0.5

    def test_default_cors_origins(self):
        """Settings.cors_origins should include localhost."""
        from app.core.config import Settings
        s = Settings()
        assert "http://localhost:3000" in s.cors_origins
        assert "http://localhost:5173" in s.cors_origins

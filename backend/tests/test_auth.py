"""Tests for API-token authentication (middleware)."""

import pytest

from app.core.config import settings


@pytest.fixture
def token_enabled(monkeypatch):
    """Enable API_TOKEN for the duration of one test."""
    monkeypatch.setattr(settings, "api_token", "test-secret-token")
    assert settings.api_token_active is True
    yield "test-secret-token"
    monkeypatch.setattr(settings, "api_token", None)


class TestAuthMiddleware:
    def test_protected_path_without_token_returns_401(self, client, token_enabled):
        response = client.get("/results/does-not-exist")
        assert response.status_code == 401

    def test_protected_path_with_wrong_token_returns_401(self, client, token_enabled):
        response = client.get(
            "/results/does-not-exist", headers={"X-API-Key": "wrong"}
        )
        assert response.status_code == 401

    def test_protected_path_with_api_key_header_passes(self, client, token_enabled):
        response = client.get(
            "/results/does-not-exist", headers={"X-API-Key": token_enabled}
        )
        # Auth passed; the job simply does not exist.
        assert response.status_code == 404

    def test_protected_path_with_bearer_token_passes(self, client, token_enabled):
        response = client.get(
            "/results/does-not-exist",
            headers={"Authorization": f"Bearer {token_enabled}"},
        )
        assert response.status_code == 404

    def test_health_is_public_even_with_token(self, client, token_enabled):
        assert client.get("/health").status_code == 200

    def test_placeholder_token_keeps_auth_disabled(self, client, monkeypatch):
        monkeypatch.setattr(
            settings, "api_token", "replace-with-generated-token"
        )
        assert settings.api_token_active is False
        assert client.get("/results/does-not-exist").status_code == 404

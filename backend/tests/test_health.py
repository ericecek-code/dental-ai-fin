"""Tests for the /health endpoint."""

import pytest


class TestHealthEndpoint:
    """Verify the health-check endpoint behaves correctly."""

    def test_health_returns_200(self, client):
        """GET /health should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_healthy(self, client):
        """GET /health body should contain status: healthy."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_is_json(self, client):
        """GET /health should return JSON content-type."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_health_has_no_methods_besides_get(self, client):
        """POST /health should not be allowed (405 Method Not Allowed)."""
        response = client.post("/health")
        assert response.status_code == 405

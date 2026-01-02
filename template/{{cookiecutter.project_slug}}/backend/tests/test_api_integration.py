"""
Integration tests for API endpoints.
Tests actual HTTP requests to FastAPI app.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Health endpoint should return OK."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_ready_endpoint(self):
        """Ready endpoint should return OK."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
        
        assert response.status_code == 200


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Login with invalid credentials should fail."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "wrong@example.com", "password": "wrongpass"},
            )
        
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_register_missing_fields(self):
        """Register with missing fields should fail."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={"email": "test@example.com"},  # Missing password
            )
        
        assert response.status_code == 422


class TestUserEndpoints:
    """Tests for user management endpoints."""

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self):
        """Getting current user without auth should fail."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self):
        """Listing users without auth should fail."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/users")
        
        assert response.status_code == 401

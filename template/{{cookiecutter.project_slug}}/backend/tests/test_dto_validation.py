"""
Tests for DTO validation.
Ensures request/response models validate correctly.
"""
import pytest
from pydantic import ValidationError
from internal.dto.requests import CreateUserRequest
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
from internal.dto.requests import LoginRequest
{%- endif %}
from internal.dto.responses import UserResponse


class TestCreateUserRequest:
    """Tests for CreateUserRequest validation."""

    def test_valid_request(self):
        """Valid data should pass validation."""
        request = CreateUserRequest(
            email="test@example.com",
            password="SecurePass123!",
            username="testuser",
        )
        assert request.email == "test@example.com"

    def test_invalid_email(self):
        """Invalid email should fail validation."""
        with pytest.raises(ValidationError):
            CreateUserRequest(
                email="not-an-email",
                password="SecurePass123!",
            )

    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    def test_short_password(self):
        """Password shorter than 8 chars should fail."""
        with pytest.raises(ValidationError):
            CreateUserRequest(
                email="test@example.com",
                password="short",
            )
    {%- endif %}

    def test_empty_email(self):
        """Empty email should fail validation."""
        with pytest.raises(ValidationError):
            CreateUserRequest(
                email="",
                password="SecurePass123!",
            )


{% if cookiecutter.auth_strategy == 'jwt_builtin' -%}
class TestLoginRequest:
    """Tests for LoginRequest validation."""

    def test_valid_login(self):
        """Valid login data should pass."""
        request = LoginRequest(
            email="test@example.com",
            password="password123",
        )
        assert request.email == "test@example.com"

    def test_missing_password(self):
        """Missing password should fail."""
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")
{%- endif %}


class TestUserResponse:
    """Tests for UserResponse model."""

    def test_user_response_creation(self):
        """Should create valid response model."""
        user_id = "00000000-0000-0000-0000-000000000123"
        response = UserResponse(
            id=user_id,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            full_name="Test User",
            role="user",
            status="active",
            is_verified=True,
            created_at="2024-01-01T00:00:00Z",
        )
        assert str(response.id) == user_id
        assert response.full_name == "Test User"

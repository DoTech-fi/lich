"""
Unit tests for User Service.
Tests business logic with mocked dependencies.
"""
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from internal.services.user_service import UserService
from internal.entities.user import User, UserRole, UserStatus
from internal.dto.requests import CreateUserRequest
from pkg.errors.exceptions import ConflictError, NotFoundError


@pytest.fixture
def mock_user_repo():
    """Mock user repository; lookups miss by default."""
    repo = AsyncMock()
    repo.get_by_email.return_value = None
    repo.get_by_username.return_value = None
    repo.get_by_id.return_value = None
    return repo


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo)


def _make_request(**overrides) -> CreateUserRequest:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
        "password": "SecurePass123",
        {%- endif %}
    }
    data.update(overrides)
    return CreateUserRequest(**data)


def _make_user(**overrides) -> User:
    defaults = dict(
        email="test@example.com",
        username="testuser",
        status=UserStatus.PENDING,
    )
    defaults.update(overrides)
    return User(**defaults)


class TestUserService:
    """Tests for UserService business logic."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user_repo):
        mock_user_repo.create.return_value = _make_user()

        user = await user_service.create_user(_make_request())

        assert user.email == "test@example.com"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = _make_user(username="existing")

        with pytest.raises(ConflictError, match="email already exists"):
            await user_service.create_user(_make_request())

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_user_repo):
        existing = _make_user()
        mock_user_repo.get_by_id.return_value = existing

        user = await user_service.get_user(existing.id)

        assert user.id == existing.id
        mock_user_repo.get_by_id.assert_called_once_with(existing.id)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user_repo):
        with pytest.raises(NotFoundError):
            await user_service.get_user(uuid4())

    @pytest.mark.asyncio
    async def test_activate_user(self, user_service, mock_user_repo):
        user = _make_user(status=UserStatus.PENDING)
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.side_effect = lambda u: u

        result = await user_service.activate_user(user.id)

        assert result.status == UserStatus.ACTIVE
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_suspend_user(self, user_service, mock_user_repo):
        user = _make_user(status=UserStatus.ACTIVE)
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.side_effect = lambda u: u

        result = await user_service.suspend_user(user.id)

        assert result.status == UserStatus.SUSPENDED

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, mock_user_repo):
        user = _make_user()
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.delete.return_value = True

        result = await user_service.delete_user(user.id)

        assert result is True
        mock_user_repo.delete.assert_called_once_with(user.id)

    @pytest.mark.asyncio
    async def test_delete_super_admin_is_rejected(self, user_service, mock_user_repo):
        from pkg.errors.exceptions import ValidationError

        user = _make_user(role=UserRole.SUPER_ADMIN)
        mock_user_repo.get_by_id.return_value = user

        with pytest.raises(ValidationError, match="super admin"):
            await user_service.delete_user(user.id)

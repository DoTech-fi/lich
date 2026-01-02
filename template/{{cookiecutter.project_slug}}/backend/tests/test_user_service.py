"""
Unit tests for User Service.
Tests business logic with mocked dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from internal.services.user_service import UserService
from internal.entities.user import User, UserRole, UserStatus


class TestUserService:
    """Tests for UserService business logic."""

    @pytest.fixture
    def mock_user_repo(self):
        """Create a mock user repository."""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def user_service(self, mock_user_repo):
        """Create UserService with mocked dependencies."""
        return UserService(user_repository=mock_user_repo)

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user_repo):
        """Should create user with valid data."""
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = User(
            id="123",
            email="test@example.com",
            username="testuser",
        )

        user = await user_service.create_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
        )

        assert user.email == "test@example.com"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_user_repo):
        """Should fail when email already exists."""
        mock_user_repo.get_by_email.return_value = User(
            id="123",
            email="test@example.com",
            username="existing",
        )

        with pytest.raises(ValueError, match="Email already exists"):
            await user_service.create_user(
                email="test@example.com",
                username="newuser",
                password="SecurePass123!",
            )

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service, mock_user_repo):
        """Should return user when found."""
        expected_user = User(
            id="123",
            email="test@example.com",
            username="testuser",
        )
        mock_user_repo.get_by_id.return_value = expected_user

        user = await user_service.get_user_by_id("123")

        assert user.id == "123"
        mock_user_repo.get_by_id.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        """Should raise error when user not found."""
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            await user_service.get_user_by_id("nonexistent")

    @pytest.mark.asyncio
    async def test_activate_user(self, user_service, mock_user_repo):
        """Should activate pending user."""
        user = User(
            id="123",
            email="test@example.com",
            username="testuser",
            status=UserStatus.PENDING,
        )
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.return_value = user

        result = await user_service.activate_user("123")

        assert result.status == UserStatus.ACTIVE
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_suspend_user(self, user_service, mock_user_repo):
        """Should suspend active user."""
        user = User(
            id="123",
            email="test@example.com",
            username="testuser",
            status=UserStatus.ACTIVE,
        )
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.return_value = user

        result = await user_service.suspend_user("123")

        assert result.status == UserStatus.SUSPENDED
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, mock_user_repo):
        """Should delete user."""
        mock_user_repo.get_by_id.return_value = User(
            id="123",
            email="test@example.com",
            username="testuser",
        )
        mock_user_repo.delete.return_value = True

        result = await user_service.delete_user("123")

        assert result is True
        mock_user_repo.delete.assert_called_once_with("123")

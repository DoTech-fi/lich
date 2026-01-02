"""
Unit tests for User Entity.
Tests pure domain logic - no external dependencies.
"""
import pytest
from uuid import uuid4
from internal.entities.user import User, UserRole, UserStatus


class TestUserEntity:
    """Tests for User domain entity."""
    
    def test_create_user_with_valid_email(self):
        """User should be created with valid email."""
        user = User(
            email="test@example.com",
            username="testuser",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.status == UserStatus.PENDING
    
    def test_create_user_without_email_fails(self):
        """User creation should fail without email."""
        with pytest.raises(ValueError, match="Email is required"):
            User(email="", username="test")
    
    def test_create_user_with_invalid_email_fails(self):
        """User creation should fail with invalid email format."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(email="invalid-email", username="test")
    
    def test_create_user_with_short_username_fails(self):
        """Username must be at least 3 characters."""
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            User(email="test@example.com", username="ab")
    
    def test_full_name_with_both_names(self):
        """Full name should combine first and last name."""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
        )
        assert user.full_name == "John Doe"
    
    def test_full_name_with_only_first_name(self):
        """Full name should work with only first name."""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="John",
        )
        assert user.full_name == "John"
    
    def test_full_name_fallback_to_username(self):
        """Full name should fallback to username if no names."""
        user = User(
            email="test@example.com",
            username="testuser",
        )
        assert user.full_name == "testuser"
    
    def test_is_admin_for_admin_user(self):
        """is_admin should be True for admin users."""
        user = User(
            email="admin@example.com",
            username="admin",
            role=UserRole.ADMIN,
        )
        assert user.is_admin is True
    
    def test_is_admin_for_regular_user(self):
        """is_admin should be False for regular users."""
        user = User(
            email="user@example.com",
            username="user",
            role=UserRole.USER,
        )
        assert user.is_admin is False
    
    def test_can_login_when_active_and_verified(self):
        """User can login when active and verified."""
        user = User(
            email="test@example.com",
            username="test",
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        assert user.can_login is True
    
    def test_cannot_login_when_pending(self):
        """User cannot login when pending."""
        user = User(
            email="test@example.com",
            username="test",
            status=UserStatus.PENDING,
        )
        assert user.can_login is False
    
    def test_cannot_login_when_not_verified(self):
        """User cannot login when not verified."""
        user = User(
            email="test@example.com",
            username="test",
            status=UserStatus.ACTIVE,
            is_verified=False,
        )
        assert user.can_login is False
    
    def test_activate_user(self):
        """Activate should set status to ACTIVE and verify."""
        user = User(
            email="test@example.com",
            username="test",
        )
        user.activate()
        assert user.status == UserStatus.ACTIVE
        assert user.is_verified is True
        assert user.updated_at is not None
    
    def test_suspend_user(self):
        """Suspend should set status to SUSPENDED."""
        user = User(
            email="test@example.com",
            username="test",
            status=UserStatus.ACTIVE,
        )
        user.suspend()
        assert user.status == UserStatus.SUSPENDED
        assert user.updated_at is not None
    
    def test_promote_to_admin(self):
        """Regular user can be promoted to admin."""
        user = User(
            email="test@example.com",
            username="test",
            role=UserRole.USER,
        )
        user.promote_to_admin()
        assert user.role == UserRole.ADMIN
    
    def test_cannot_change_super_admin_role(self):
        """Super admin role cannot be changed."""
        user = User(
            email="admin@example.com",
            username="superadmin",
            role=UserRole.SUPER_ADMIN,
        )
        with pytest.raises(ValueError, match="Cannot change super admin role"):
            user.promote_to_admin()
        
        with pytest.raises(ValueError, match="Cannot change super admin role"):
            user.demote_to_user()

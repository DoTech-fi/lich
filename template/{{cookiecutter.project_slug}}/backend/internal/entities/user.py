"""
User Entity - Pure domain model for user.
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from .base import BaseEntity


class UserRole(Enum):
    """User roles in the system."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


@dataclass
class User(BaseEntity):
    """
    User domain entity.
    
    This is a PURE domain model - no ORM, no HTTP concerns.
    All user-related business rules are enforced here.
    """
    
    email: str = ""
    username: str = ""
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    hashed_password: str = ""
    {%- endif %}
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING
    is_verified: bool = False
    avatar_url: Optional[str] = None
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    keycloak_id: Optional[str] = None
    {%- endif %}
    
    def _validate(self):
        """Enforce user domain invariants."""
        if not self.email:
            raise ValueError("Email is required")
        if "@" not in self.email:
            raise ValueError("Invalid email format")
        if self.username and len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) if parts else self.username or self.email.split("@")[0]
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
    
    @property
    def can_login(self) -> bool:
        """Check if user is allowed to login."""
        return self.status == UserStatus.ACTIVE and self.is_verified
    
    def activate(self):
        """Activate the user account."""
        self.status = UserStatus.ACTIVE
        self.is_verified = True
        self.touch()
    
    def suspend(self):
        """Suspend the user account."""
        self.status = UserStatus.SUSPENDED
        self.touch()
    
    def promote_to_admin(self):
        """Promote user to admin role."""
        if self.role == UserRole.SUPER_ADMIN:
            raise ValueError("Cannot change super admin role")
        self.role = UserRole.ADMIN
        self.touch()
    
    def demote_to_user(self):
        """Demote admin to regular user."""
        if self.role == UserRole.SUPER_ADMIN:
            raise ValueError("Cannot change super admin role")
        self.role = UserRole.USER
        self.touch()

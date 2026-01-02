"""Entities package - Pure domain models."""
from .base import BaseEntity
from .user import User, UserRole, UserStatus

__all__ = [
    "BaseEntity",
    "User",
    "UserRole",
    "UserStatus",
]

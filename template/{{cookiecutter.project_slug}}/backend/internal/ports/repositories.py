"""
Repository Interfaces (Ports).
These are abstract interfaces that define what the domain needs.
Implementations (adapters) are injected at runtime.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from internal.entities.user import User


class UserRepository(ABC):
    """
    User repository interface.
    
    This is a PORT - it defines WHAT the domain needs,
    not HOW it's implemented. The adapter provides the implementation.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """List all users with pagination."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total users."""
        pass
    
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    @abstractmethod
    async def get_by_keycloak_id(self, keycloak_id: str) -> Optional[User]:
        """Get user by Keycloak ID."""
        pass
    {%- endif %}


{%- if cookiecutter.use_redis == 'yes' %}


class CacheRepository(ABC):
    """
    Cache repository interface for Redis operations.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: Optional[int] = None,
    ) -> bool:
        """Set value with optional expiration."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
{%- endif %}

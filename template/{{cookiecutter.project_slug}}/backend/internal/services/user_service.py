"""
User Service - Business logic and use cases.
This layer orchestrates domain operations.
"""
from typing import List, Optional
from uuid import UUID
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
from passlib.context import CryptContext
{%- endif %}

from internal.entities.user import User, UserStatus, UserRole
from internal.ports.repositories import UserRepository
from internal.dto.requests import CreateUserRequest, UpdateUserRequest
from pkg.errors.exceptions import NotFoundError, ConflictError, ValidationError


{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
{%- endif %}


class UserService:
    """
    User service containing all user-related use cases.
    
    This service:
    - Contains business logic
    - Uses ports (interfaces) for external dependencies
    - Never knows about HTTP or database details
    """
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, request: CreateUserRequest) -> User:
        """
        Create a new user.
        
        Use case: User registration
        """
        # Check if email already exists
        existing = await self.user_repo.get_by_email(request.email)
        if existing:
            raise ConflictError("User with this email already exists")
        
        # Check if username already exists
        if request.username:
            existing = await self.user_repo.get_by_username(request.username)
            if existing:
                raise ConflictError("Username already taken")
        
        # Create domain entity
        user = User(
            email=request.email,
            username=request.username or request.email.split("@")[0],
            first_name=request.first_name or "",
            last_name=request.last_name or "",
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            hashed_password=pwd_context.hash(request.password),
            {%- endif %}
            role=UserRole.USER,
            status=UserStatus.PENDING,
        )
        
        return await self.user_repo.create(user)
    
    async def get_user(self, user_id: UUID) -> User:
        """
        Get a user by ID.
        
        Use case: View user profile
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Use case: Login, password reset
        """
        return await self.user_repo.get_by_email(email)
    
    async def update_user(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
    ) -> User:
        """
        Update user information.
        
        Use case: Edit profile
        """
        user = await self.get_user(user_id)
        
        # Update fields if provided
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.last_name is not None:
            user.last_name = request.last_name
        if request.username is not None:
            # Check if new username is available
            existing = await self.user_repo.get_by_username(request.username)
            if existing and existing.id != user_id:
                raise ConflictError("Username already taken")
            user.username = request.username
        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url
        
        user.touch()
        return await self.user_repo.update(user)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user.
        
        Use case: Account deletion
        """
        user = await self.get_user(user_id)
        if user.role == UserRole.SUPER_ADMIN:
            raise ValidationError("Cannot delete super admin")
        return await self.user_repo.delete(user_id)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        List all users with pagination.
        
        Use case: Admin user management
        """
        return await self.user_repo.list_all(skip=skip, limit=limit)
    
    async def activate_user(self, user_id: UUID) -> User:
        """
        Activate a user account.
        
        Use case: Email verification, admin activation
        """
        user = await self.get_user(user_id)
        user.activate()
        return await self.user_repo.update(user)
    
    async def suspend_user(self, user_id: UUID) -> User:
        """
        Suspend a user account.
        
        Use case: Admin moderation
        """
        user = await self.get_user(user_id)
        if user.role == UserRole.SUPER_ADMIN:
            raise ValidationError("Cannot suspend super admin")
        user.suspend()
        return await self.user_repo.update(user)
    
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    async def verify_password(self, user: User, password: str) -> bool:
        """Verify user's password."""
        return pwd_context.verify(password, user.hashed_password)
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        Change user's password.
        
        Use case: Password change from settings
        """
        user = await self.get_user(user_id)
        
        if not await self.verify_password(user, current_password):
            raise ValidationError("Current password is incorrect")
        
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        user.hashed_password = pwd_context.hash(new_password)
        user.touch()
        return await self.user_repo.update(user)
    {%- endif %}

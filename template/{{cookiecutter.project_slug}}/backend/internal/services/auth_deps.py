"""
Authentication Dependencies for FastAPI.
Provides dependency injection for auth in route handlers.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
{%- if cookiecutter.auth_strategy == 'keycloak' %}
from jose import jwt, JWTError
import httpx
{%- elif cookiecutter.auth_strategy == 'jwt_builtin' %}
from jose import jwt, JWTError
from datetime import datetime, timedelta
{%- endif %}

from pkg.config.settings import settings
from internal.entities.user import User, UserRole
from internal.services.user_service import UserService
from internal.adapters.db.user_repo import SQLAlchemyUserRepository
from internal.adapters.db.connection import get_session


security = HTTPBearer(auto_error=False)


async def get_user_service() -> UserService:
    """Dependency to get UserService instance."""
    async for session in get_session():
        repo = SQLAlchemyUserRepository(session)
        return UserService(repo)


{%- if cookiecutter.auth_strategy == 'keycloak' %}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Get current authenticated user from Keycloak token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    try:
        # Get Keycloak public key and verify token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs"
            )
            jwks = response.json()
        
        # Decode token
        token = credentials.credentials
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
        )
        
        keycloak_id = payload.get("sub")
        if not keycloak_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        # Get or create user
        user = await user_service.user_repo.get_by_keycloak_id(keycloak_id)
        if not user:
            # Auto-create user from Keycloak data
            from internal.dto.requests import CreateUserRequest
            request = CreateUserRequest(
                email=payload.get("email", ""),
                username=payload.get("preferred_username"),
                first_name=payload.get("given_name"),
                last_name=payload.get("family_name"),
            )
            user = await user_service.create_user(request)
            user.keycloak_id = keycloak_id
            user = await user_service.user_repo.update(user)
        
        return user
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


{%- elif cookiecutter.auth_strategy == 'jwt_builtin' %}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        from uuid import UUID
        user = await user_service.get_user(UUID(user_id))
        
        if not user.can_login:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active",
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


{%- elif cookiecutter.auth_strategy == 'none' %}


async def get_current_user() -> Optional[User]:
    """No authentication - returns None."""
    return None


{%- endif %}


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    {%- if cookiecutter.auth_strategy != 'none' %}
    if not current_user.can_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    {%- endif %}
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure user is an admin."""
    {%- if cookiecutter.auth_strategy != 'none' %}
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    {%- endif %}
    return current_user

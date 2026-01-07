"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
from datetime import timedelta

from internal.dto.requests import LoginRequest, CreateUserRequest, RefreshTokenRequest
from internal.dto.responses import LoginResponse, TokenResponse, UserResponse, MessageResponse
from internal.services.user_service import UserService
from internal.services.auth_deps import (
    get_user_service,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from internal.entities.user import User
from pkg.config.settings import settings
from jose import jwt, JWTError
{%- elif cookiecutter.auth_strategy == 'keycloak' %}
from internal.dto.responses import MessageResponse, UserResponse
from internal.services.auth_deps import get_current_user
from internal.entities.user import User
from pkg.config.settings import settings
{%- endif %}

router = APIRouter()


{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Register a new user."""
    user = await user_service.create_user(request)
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role.value,
        status=user.status.value,
        is_verified=user.is_verified,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Login and get access tokens."""
    user = await user_service.get_user_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not await user_service.verify_password(user, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.can_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return LoginResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            is_verified=user.is_verified,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        if payload.get("type") != "refresh":
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
        
        # Create new tokens
        access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )



# ==========================================
# GOOGLE OAUTH
# ==========================================

@router.get("/google/url")
async def google_auth_url():
    """Get Google OAuth authorization URL."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID in your environment.",
        )
    
    import urllib.parse
    
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    
    return {"url": google_auth_url}


@router.post("/google/callback")
async def google_callback(
    code: str,
    user_service: UserService = Depends(get_user_service),
):
    """Handle Google OAuth callback and exchange code for tokens."""
    import httpx
    
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for tokens",
            )
        
        tokens = token_response.json()
        
        # Get user info from Google
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )
        
        google_user = userinfo_response.json()
    
    # Find or create user
    email = google_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account does not have an email",
        )
    
    user = await user_service.get_user_by_email(email)
    
    if not user:
        # Create new user from Google data
        user = await user_service.create_user_from_google(
            email=email,
            first_name=google_user.get("given_name", ""),
            last_name=google_user.get("family_name", ""),
            avatar_url=google_user.get("picture"),
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return LoginResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            is_verified=user.is_verified,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        ),
    )


{%- elif cookiecutter.auth_strategy == 'keycloak' %}


@router.get("/config")
async def get_auth_config():
    """Get Keycloak configuration for frontend."""
    return {
        "keycloak_url": settings.keycloak_url,
        "realm": settings.keycloak_realm,
        "client_id": settings.keycloak_client_id,
    }


{%- endif %}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        role=current_user.role.value,
        status=current_user.status.value,
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout current user."""
    # For JWT, client should discard tokens
    # For Keycloak, redirect to logout endpoint
    return MessageResponse(message="Logged out successfully")

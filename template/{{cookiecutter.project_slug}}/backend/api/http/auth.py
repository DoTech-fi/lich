"""
Authentication endpoints.
"""
import hashlib
import hmac as _hmac
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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

def _make_oauth_state(nonce: str) -> str:
    """Create a signed, time-limited state token bound to a per-session nonce."""
    ts = str(int(time.time()))
    payload = f"{ts}.{nonce}"
    sig = _hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def _verify_oauth_state(state: str, cookie_nonce: str, max_age_seconds: int = 600) -> bool:
    """Verify signature, age, and that the state is bound to this session's cookie nonce."""
    try:
        ts, nonce, sig = state.split(".", 2)
        payload = f"{ts}.{nonce}"
        expected = _hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not _hmac.compare_digest(sig, expected):
            return False
        age = time.time() - int(ts)
        if not (0 <= age < max_age_seconds):
            return False
        if not cookie_nonce or not _hmac.compare_digest(nonce, cookie_nonce):
            return False
        return True
    except (ValueError, TypeError, AttributeError):
        return False


@router.get("/google/url")
async def google_auth_url(response: Response):
    """Get Google OAuth authorization URL."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID in your environment.",
        )

    import urllib.parse

    nonce = secrets.token_urlsafe(32)
    state = _make_oauth_state(nonce)
    response.set_cookie(
        "oauth_state",
        nonce,
        httponly=True,
        # Secure everywhere except local HTTP dev
        secure=settings.environment.lower() != "development",
        samesite="lax",
        max_age=600,
        path="/",
    )

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    return {"url": google_auth_url, "state": state}


@router.post("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    response: Response,
    user_service: UserService = Depends(get_user_service),
):
    """Handle Google OAuth callback and exchange code for tokens."""
    cookie_nonce = request.cookies.get("oauth_state", "")
    if not _verify_oauth_state(state, cookie_nonce):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state (possible CSRF).",
        )
    response.delete_cookie("oauth_state", path="/")

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


{%- if cookiecutter.auth_strategy != 'none' %}


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
{%- endif %}

"""
User management endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from internal.dto.requests import UpdateUserRequest
from internal.dto.responses import UserResponse, UserListResponse, MessageResponse
from internal.services.user_service import UserService
from internal.services.auth_deps import (
    get_user_service,
    get_current_active_user,
    get_admin_user,
)
from internal.entities.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's profile."""
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


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user's profile."""
    updated_user = await user_service.update_user(current_user.id, request)
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        full_name=updated_user.full_name,
        role=updated_user.role.value,
        status=updated_user.status.value,
        is_verified=updated_user.is_verified,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


# Admin endpoints
@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """List all users (admin only)."""
    skip = (page - 1) * page_size
    users = await user_service.list_users(skip=skip, limit=page_size + 1)
    
    has_more = len(users) > page_size
    if has_more:
        users = users[:page_size]
    
    total = await user_service.user_repo.count()
    
    return UserListResponse(
        items=[
            UserResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                first_name=u.first_name,
                last_name=u.last_name,
                full_name=u.full_name,
                role=u.role.value,
                status=u.status.value,
                is_verified=u.is_verified,
                avatar_url=u.avatar_url,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ],
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get a specific user (admin only)."""
    user = await user_service.get_user(user_id)
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


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Activate a user (admin only)."""
    user = await user_service.activate_user(user_id)
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


@router.post("/{user_id}/suspend", response_model=UserResponse)
async def suspend_user(
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Suspend a user (admin only)."""
    user = await user_service.suspend_user(user_id)
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


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Delete a user (admin only)."""
    await user_service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")

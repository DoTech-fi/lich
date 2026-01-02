"""
API Router Aggregation.
All routes are registered here.
"""
from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router
from .auth import router as auth_router

router = APIRouter()

# Include all routers
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/v1/users", tags=["Users"])

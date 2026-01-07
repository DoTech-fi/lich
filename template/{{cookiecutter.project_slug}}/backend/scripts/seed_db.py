import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from internal.services.user_service import UserService
from internal.adapters.db.user_repo import UserRepository
from internal.adapters.db.connection import get_session
from internal.entities.user import UserRole, UserStatus
from internal.dto.requests import CreateUserRequest
from pkg.logger.setup import get_logger

logger = get_logger("seed_db")

async def seed_admin():
    """Seed the database with the initial admin user."""
    admin_email = "{{ cookiecutter.admin_email }}"
    admin_password = "{{ cookiecutter.admin_password }}"
    
    if not admin_email or not admin_password:
        logger.warning("Admin email or password not configured in cookiecutter.")
        return

    async for session in get_session():
        user_repo = UserRepository(session)
        user_service = UserService(user_repo)
        
        # Check if admin already exists
        existing_user = await user_repo.get_by_email(admin_email)
        if existing_user:
            logger.info(f"Admin user {admin_email} already exists.")
            return

        try:
            logger.info(f"Creating admin user: {admin_email}")
            
            # Create request
            request = CreateUserRequest(
                email=admin_email,
                password=admin_password,
                username="admin",
                first_name="Admin",
                last_name="User"
            )
            
            # Create user
            user = await user_service.create_user(request)
            
            # Promote to SUPER_ADMIN and activate
            user.role = UserRole.SUPER_ADMIN
            user.status = UserStatus.ACTIVE
            user.is_verified = True
            
            await user_repo.update(user)
            await session.commit()
            
            logger.info(f"Successfully created admin user: {admin_email}")
            
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            sys.exit(1)
            
if __name__ == "__main__":
    asyncio.run(seed_admin())

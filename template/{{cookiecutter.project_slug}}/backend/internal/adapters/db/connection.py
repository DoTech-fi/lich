{%- if cookiecutter.database == 'postgresql' %}
"""
Database connection setup using SQLAlchemy async.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from pkg.config.settings import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database - create tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
{%- else %}
"""
MongoDB connection setup using Motor.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from pkg.config.settings import settings


# MongoDB client
client: AsyncIOMotorClient = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM."""
    global client
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    # Import document models
    from .models import UserDocument
    
    await init_beanie(
        database=client[settings.mongodb_db],
        document_models=[UserDocument],
    )


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()


async def get_session():
    """Get database session (for compatibility with repository pattern)."""
    yield client
{%- endif %}

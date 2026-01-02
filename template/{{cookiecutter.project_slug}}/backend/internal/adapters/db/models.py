{%- if cookiecutter.database == 'postgresql' %}
"""
SQLAlchemy ORM Models.
These are database-specific - NOT domain entities.
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from .connection import Base
from internal.entities.user import UserRole, UserStatus


class UserModel(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    hashed_password = Column(String(255), nullable=False)
    {%- endif %}
    first_name = Column(String(100), default="")
    last_name = Column(String(100), default="")
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    keycloak_id = Column(String(255), unique=True, nullable=True, index=True)
    {%- endif %}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"
{%- else %}
"""
Beanie Document Models for MongoDB.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID
from beanie import Document
from pydantic import Field

from internal.entities.user import UserRole, UserStatus


class UserDocument(Document):
    """User MongoDB document."""
    
    id: UUID = Field(default_factory=uuid4)
    email: str
    username: str
    {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
    hashed_password: str
    {%- endif %}
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING
    is_verified: bool = False
    avatar_url: Optional[str] = None
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    keycloak_id: Optional[str] = None
    {%- endif %}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "users"
        
    class Config:
        use_enum_values = True
{%- endif %}

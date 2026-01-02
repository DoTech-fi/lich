{%- if cookiecutter.database == 'postgresql' %}
"""
User Repository Implementation using SQLAlchemy.
This is an ADAPTER - it implements the PORT (interface).
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from internal.entities.user import User, UserRole, UserStatus
from internal.ports.repositories import UserRepository
from .models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            hashed_password=model.hashed_password,
            {%- endif %}
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            status=model.status,
            is_verified=model.is_verified,
            avatar_url=model.avatar_url,
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            keycloak_id=model.keycloak_id,
            {%- endif %}
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to ORM model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            hashed_password=entity.hashed_password,
            {%- endif %}
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role,
            status=entity.status,
            is_verified=entity.is_verified,
            avatar_url=entity.avatar_url,
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            keycloak_id=entity.keycloak_id,
            {%- endif %}
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    async def create(self, user: User) -> User:
        model = self._entity_to_model(user)
        self.session.add(model)
        await self.session.flush()
        return self._model_to_entity(model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username.lower())
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def update(self, user: User) -> User:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.email = user.email
            model.username = user.username
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            model.hashed_password = user.hashed_password
            {%- endif %}
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.role = user.role
            model.status = user.status
            model.is_verified = user.is_verified
            model.avatar_url = user.avatar_url
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            model.keycloak_id = user.keycloak_id
            {%- endif %}
            model.updated_at = user.updated_at
            await self.session.flush()
            return self._model_to_entity(model)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(
            select(UserModel)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(UserModel.id)))
        return result.scalar() or 0
    
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    async def get_by_keycloak_id(self, keycloak_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.keycloak_id == keycloak_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    {%- endif %}
{%- else %}
"""
User Repository Implementation using Beanie (MongoDB).
This is an ADAPTER - it implements the PORT (interface).
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from internal.entities.user import User
from internal.ports.repositories import UserRepository
from .models import UserDocument


class BeanieUserRepository(UserRepository):
    """Beanie implementation of UserRepository for MongoDB."""
    
    def _document_to_entity(self, doc: UserDocument) -> User:
        """Convert MongoDB document to domain entity."""
        return User(
            id=doc.id,
            email=doc.email,
            username=doc.username,
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            hashed_password=doc.hashed_password,
            {%- endif %}
            first_name=doc.first_name,
            last_name=doc.last_name,
            role=doc.role,
            status=doc.status,
            is_verified=doc.is_verified,
            avatar_url=doc.avatar_url,
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            keycloak_id=doc.keycloak_id,
            {%- endif %}
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
    
    async def create(self, user: User) -> User:
        doc = UserDocument(
            id=user.id,
            email=user.email,
            username=user.username,
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            hashed_password=user.hashed_password,
            {%- endif %}
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            is_verified=user.is_verified,
            avatar_url=user.avatar_url,
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            keycloak_id=user.keycloak_id,
            {%- endif %}
            created_at=user.created_at,
        )
        await doc.insert()
        return self._document_to_entity(doc)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        doc = await UserDocument.find_one(UserDocument.id == user_id)
        return self._document_to_entity(doc) if doc else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await UserDocument.find_one(UserDocument.email == email.lower())
        return self._document_to_entity(doc) if doc else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        doc = await UserDocument.find_one(UserDocument.username == username.lower())
        return self._document_to_entity(doc) if doc else None
    
    async def update(self, user: User) -> User:
        doc = await UserDocument.find_one(UserDocument.id == user.id)
        if doc:
            doc.email = user.email
            doc.username = user.username
            {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
            doc.hashed_password = user.hashed_password
            {%- endif %}
            doc.first_name = user.first_name
            doc.last_name = user.last_name
            doc.role = user.role
            doc.status = user.status
            doc.is_verified = user.is_verified
            doc.avatar_url = user.avatar_url
            {%- if cookiecutter.auth_strategy == 'keycloak' %}
            doc.keycloak_id = user.keycloak_id
            {%- endif %}
            doc.updated_at = datetime.utcnow()
            await doc.save()
            return self._document_to_entity(doc)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        doc = await UserDocument.find_one(UserDocument.id == user_id)
        if doc:
            await doc.delete()
            return True
        return False
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        docs = await UserDocument.find_all().skip(skip).limit(limit).to_list()
        return [self._document_to_entity(d) for d in docs]
    
    async def count(self) -> int:
        return await UserDocument.count()
    
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    async def get_by_keycloak_id(self, keycloak_id: str) -> Optional[User]:
        doc = await UserDocument.find_one(UserDocument.keycloak_id == keycloak_id)
        return self._document_to_entity(doc) if doc else None
    {%- endif %}
{%- endif %}

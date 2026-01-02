"""
Settings configuration using Pydantic Settings.
All configuration is loaded from environment variables.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Project
    project_name: str = Field(default="{{ cookiecutter.project_slug }}")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3002", "http://localhost:4321"]
    )
    
    {%- if cookiecutter.database == 'postgresql' %}
    # PostgreSQL
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="app")
    db_password: str = Field(default="app_secret")
    db_name: str = Field(default="{{ cookiecutter.project_slug }}")
    
    @property
    def database_url(self) -> str:
        """Build async database URL."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    {%- else %}
    # MongoDB
    mongodb_host: str = Field(default="localhost")
    mongodb_port: int = Field(default=27017)
    mongodb_user: str = Field(default="app")
    mongodb_password: str = Field(default="app_secret")
    mongodb_db: str = Field(default="{{ cookiecutter.project_slug }}")
    
    @property
    def mongodb_url(self) -> str:
        """Build MongoDB URL."""
        return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
    {%- endif %}
    
    {%- if cookiecutter.use_redis == 'yes' %}
    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="")
    
    @property
    def redis_url(self) -> str:
        """Build Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"
    {%- endif %}
    
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    # Keycloak
    keycloak_url: str = Field(default="http://localhost:8080")
    keycloak_realm: str = Field(default="{{ cookiecutter.project_slug }}")
    keycloak_client_id: str = Field(default="{{ cookiecutter.project_slug }}-web")
    keycloak_client_secret: str = Field(default="")
    {%- elif cookiecutter.auth_strategy == 'jwt_builtin' %}
    # JWT
    jwt_secret_key: str = Field(default="your-secret-key-change-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)
    {%- endif %}
    
    # Logging
    log_level: str = Field(default="INFO")
    {%- if cookiecutter.use_structured_logging == 'yes' %}
    log_format: str = Field(default="json")
    {%- else %}
    log_format: str = Field(default="text")
    {%- endif %}
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-me-in-production")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

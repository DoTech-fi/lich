"""The app must refuse to start in production with placeholder secrets."""
import pytest

from pkg.config.settings import Settings


def test_production_rejects_default_secret_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(Exception, match="default value"):
        Settings(_env_file=None)


def test_production_boots_with_real_secrets(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("JWT_SECRET_KEY", "b" * 64)
    settings = Settings(_env_file=None)
    assert settings.environment == "production"


def test_development_allows_defaults(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    settings = Settings(_env_file=None)
    assert settings.environment == "development"

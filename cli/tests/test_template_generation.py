"""
Template generation smoke tests.

Renders the cookiecutter template into a tmp dir and asserts the output
is actually valid (no leaked Jinja, backend compiles, key fixes present).
"""
import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "template"


def _generate(tmp_path: Path, **extra_context) -> Path:
    """Render the template with default answers plus overrides."""
    ctx = [f"{k}={v}" for k, v in extra_context.items()]
    cmd = [
        sys.executable, "-m", "cookiecutter", "--no-input",
        "-o", str(tmp_path), str(TEMPLATE_DIR), *ctx,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"cookiecutter failed:\n{res.stderr}"
    project = tmp_path / "my_awesome_project"
    assert project.is_dir()
    return project


@pytest.fixture(scope="module")
def jwt_project(tmp_path_factory) -> Path:
    """Default generation: jwt_builtin + postgresql."""
    return _generate(tmp_path_factory.mktemp("gen-jwt"))


@pytest.fixture(scope="module")
def keycloak_project(tmp_path_factory) -> Path:
    return _generate(tmp_path_factory.mktemp("gen-kc"), auth_strategy="keycloak")


def _frontend_sources(project: Path):
    apps = project / "apps"
    return [
        p for p in list(apps.rglob("*.tsx")) + list(apps.rglob("*.ts"))
        if "node_modules" not in p.parts
    ]


def test_no_jinja_leaks_into_frontend(jwt_project):
    """Generated ts/tsx must contain no unrendered Jinja syntax."""
    offenders = []
    for src in _frontend_sources(jwt_project):
        text = src.read_text()
        if "{%" in text or "{{ cookiecutter" in text:
            offenders.append(str(src.relative_to(jwt_project)))
    assert not offenders, f"Unrendered Jinja in: {offenders}"


def test_authcontext_jwt_has_login(jwt_project):
    text = (jwt_project / "apps/web/src/context/AuthContext.tsx").read_text()
    assert "login" in text and "LoginRequest" in text


def test_authcontext_keycloak_has_no_builtin_login(keycloak_project):
    text = (keycloak_project / "apps/web/src/context/AuthContext.tsx").read_text()
    assert "LoginRequest" not in text
    assert "{%" not in text


def test_generated_backend_compiles(jwt_project):
    """Every generated backend .py must at least parse."""
    for py in (jwt_project / "backend").rglob("*.py"):
        py_compile.compile(str(py), doraise=True)


def test_generated_backend_compiles_keycloak(keycloak_project):
    for py in (keycloak_project / "backend").rglob("*.py"):
        py_compile.compile(str(py), doraise=True)


def test_keycloak_has_external_user_path(keycloak_project):
    service = (keycloak_project / "backend/internal/services/user_service.py").read_text()
    assert "create_external_user" in service

    deps = (keycloak_project / "backend/internal/services/auth_deps.py").read_text()
    assert "create_external_user" in deps
    # The buggy DTO-based auto-creation must be gone:
    assert "CreateUserRequest(" not in deps


def test_rate_limiter_has_stale_eviction(jwt_project):
    text = (jwt_project / "backend/api/middleware/rate_limit.py").read_text()
    assert "_sweep_stale" in text
    assert (jwt_project / "backend/tests/test_rate_limit.py").exists()

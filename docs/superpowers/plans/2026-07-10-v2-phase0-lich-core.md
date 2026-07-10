# Lich v2 Phase 0: lich-core Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **DRAFT (2026-07-10, written pre-v1-hardening):** Greenfield tasks are executable as-is. Tasks marked **[RE-VERIFY]** touch files that v1 hardening (phases 1-4) will change — re-read those files and adjust snippets before executing. Double-check pass planned with Opus.

**Goal:** Extract the shared runtime (entities, ports, services base, middleware, config, auth, app factory, DI) from the copy-in cookiecutter template into a versioned `lich-core` pip package, then shrink the template to skeleton + domain code.

**Architecture:** New `core/` directory at repo root with src-layout package `lich_core`, completely independent of the CLI package in `cli/`. Extracted code is de-Jinja'd: cookiecutter conditionals become runtime configuration (optional settings fields, constructor kwargs, pip extras). The template keeps domain code (User entity/service/repo) as example code that imports lich_core bases. v1 copy-in projects are untouched (grandfathered, spec D13).

**Tech Stack:** Python 3.10+, FastAPI, Pydantic v2 + pydantic-settings, pytest + pytest-asyncio, optional extras: SQLAlchemy/asyncpg (postgres), Beanie (mongo), redis, python-jose + passlib + httpx (auth).

---

## File Structure

```
core/                                  # NEW — runtime package, sibling of cli/
|-- pyproject.toml
|-- VERSIONING.md                      # semver + deprecation policy (Task 15)
|-- src/lich_core/
|   |-- __init__.py                    # public API re-exports + __version__
|   |-- py.typed
|   |-- errors.py                      # AppException family (from template pkg/errors)
|   |-- container.py                   # minimal DI container
|   |-- app.py                         # create_app() factory + plugin discovery
|   |-- entities/__init__.py
|   |-- entities/base.py               # BaseEntity
|   |-- ports/__init__.py
|   |-- ports/repository.py            # generic Repository[E] + CacheRepository
|   |-- services/__init__.py
|   |-- services/base.py               # BaseService[E]
|   |-- middleware/__init__.py
|   |-- middleware/rate_limit.py       # FIXED: TTL eviction + optional Redis backend
|   |-- middleware/security_headers.py
|   |-- middleware/csrf.py
|   |-- auth/__init__.py
|   |-- auth/jwt.py                    # token create/decode, settings-explicit
|   +-- auth/keycloak.py               # FIXED: JWKS cache + provisioning callback
|   +-- config.py                      # LichSettings + validate_secrets() guard
|-- tests/                             # mirrors src layout
.github/workflows/publish-core.yml     # NEW — PyPI publish on core-v* tag
template/{{cookiecutter.project_slug}}/backend/   # SHRUNK in Task 13 [RE-VERIFY]
scripts/e2e_local.sh                   # MODIFIED in Task 14 [RE-VERIFY]
```

Not extracted (stays copy-in, YAGNI): `timing.py`, `logging.py`, `audit.py`, `sanitize.py` middleware — they are small, cosmetic, and users customize them; extraction adds API surface without fixing any known bug.

## Execution Notes

- Work on branch `v2-phase0-lich-core`.
- Python env: `cd core && pip install -e ".[dev,postgres,redis,auth]"` after Task 1; all `pytest` commands run from `core/`.
- Tasks 1–12 are greenfield (no template changes). Tasks 13–14 are **[RE-VERIFY]** — the template and e2e harness will have changed during v1 hardening; re-read every file before applying snippets.
- Delete NOTHING from the template until Task 13.

---

## Task 1: Package skeleton + publish workflow

**Files:**
- Create: `core/pyproject.toml`
- Create: `core/src/lich_core/__init__.py`
- Create: `core/src/lich_core/py.typed`
- Create: `core/tests/__init__.py`
- Create: `.github/workflows/publish-core.yml`

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_package.py`:

```python
"""Package metadata smoke tests."""


def test_version_importable():
    import lich_core

    assert lich_core.__version__ == "0.1.0"


def test_public_api_surface():
    import lich_core

    # Filled in by later tasks; the names must exist by end of Phase 0.
    for name in ("__version__",):
        assert hasattr(lich_core, name)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_package.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core'` or pytest cannot find package)

- [ ] **Step 3: Write the package skeleton**

Create `core/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "lich-core"
version = "0.1.0"  # D17: lich-core starts 0.1.0, reaches 1.0.0 at v2 GA
description = "Lich runtime library: clean-architecture base classes, middleware, auth, and app factory"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "Babak", email = "babak@dotech.fi" }]
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.110.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[project.optional-dependencies]
postgres = ["sqlalchemy>=2.0.0", "asyncpg>=0.29.0"]
mongo = ["beanie>=1.24.0"]
redis = ["redis>=5.0.0"]
auth = ["python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4", "httpx>=0.26.0"]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.23.0", "httpx>=0.26.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
lich_core = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

Create `core/src/lich_core/__init__.py`:

```python
"""lich-core — Lich runtime library.

Public API is re-exported here; anything not exported from this module
is private and may change without a deprecation period (see VERSIONING.md).
"""

__version__ = "0.1.0"
```

Create `core/src/lich_core/py.typed` (empty file) and `core/tests/__init__.py` (empty file).

Also create `core/README.md`:

```markdown
# lich-core

Runtime library for projects generated by the [Lich framework](https://github.com/DoTech-fi/lich):
clean-architecture base classes (entities, ports, services), production middleware,
auth adapters, settings with startup secret validation, and the `create_app()` factory.

Installed automatically in projects generated by `lich new` (v2+). v1 copy-in projects
do not depend on this package.
```

- [ ] **Step 4: Install editable and run tests**

Run: `cd core && pip install -e ".[dev]" && python -m pytest tests/test_package.py -v`
Expected: 2 PASSED

- [ ] **Step 5: Create the publish workflow**

Create `.github/workflows/publish-core.yml`:

```yaml
name: Publish lich-core

on:
  push:
    tags:
      - "core-v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Build
        run: |
          python -m pip install build
          python -m build core/
      - name: Run tests before publish
        run: |
          pip install core/dist/*.whl
          pip install pytest pytest-asyncio httpx
          python -m pytest core/tests -q
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: core/dist/
```

- [ ] **Step 6: Verify workflow syntax and commit**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/publish-core.yml'))" && echo OK`
Expected: `OK`

```bash
git add core/ .github/workflows/publish-core.yml
git commit -m "feat(core): lich-core package skeleton + publish workflow"
```

---

## Task 2: Extract errors module

**Files:**
- Create: `core/src/lich_core/errors.py`
- Test: `core/tests/test_errors.py`
- Source (read-only): `template/{{cookiecutter.project_slug}}/backend/pkg/errors/exceptions.py`

The source file has no Jinja conditionals — this is a straight extraction plus one addition (`LichConfigError` used by Task 7).

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_errors.py`:

```python
from lich_core.errors import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    LichConfigError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def test_not_found_with_id():
    err = NotFoundError("User", "abc-123")
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"
    assert "abc-123" in err.message


def test_to_dict_shape():
    err = ValidationError("bad input", details={"field": "email"})
    assert err.to_dict() == {
        "error": {"code": "VALIDATION_ERROR", "message": "bad input", "details": {"field": "email"}}
    }


def test_status_codes():
    assert AuthenticationError().status_code == 401
    assert AuthorizationError().status_code == 403
    assert ConflictError().status_code == 409
    assert RateLimitError().status_code == 429
    assert ExternalServiceError().status_code == 503


def test_config_error_is_not_app_exception():
    # Config errors must crash startup, not become a 500 JSON response.
    assert not issubclass(LichConfigError, AppException)
    assert issubclass(LichConfigError, RuntimeError)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_errors.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.errors'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/errors.py` with the exact content of
`template/{{cookiecutter.project_slug}}/backend/pkg/errors/exceptions.py` (it is pure Python,
copy it verbatim — AppException, NotFoundError, ValidationError, AuthenticationError,
AuthorizationError, ConflictError, RateLimitError, ExternalServiceError), changing only
the module docstring to:

```python
"""
lich-core exception hierarchy.
Following OWASP guidelines - never expose internal details.
"""
```

and appending at the end:

```python
class LichConfigError(RuntimeError):
    """Raised at startup when configuration is invalid (e.g. default secrets in production).

    Deliberately NOT an AppException: it must crash the process during boot,
    never be serialized into an HTTP response.
    """
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_errors.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Export from package root and commit**

In `core/src/lich_core/__init__.py`, add below `__version__`:

```python
from lich_core.errors import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    LichConfigError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
```

Run: `cd core && python -c "from lich_core import NotFoundError; print('OK')"`
Expected: `OK`

```bash
git add core/src/lich_core/errors.py core/src/lich_core/__init__.py core/tests/test_errors.py
git commit -m "feat(core): extract exception hierarchy from template"
```

---

## Task 3: Extract BaseEntity

**Files:**
- Create: `core/src/lich_core/entities/__init__.py`, `core/src/lich_core/entities/base.py`
- Test: `core/tests/test_entities.py`
- Source (read-only): `template/{{cookiecutter.project_slug}}/backend/internal/entities/base.py`

Source has no Jinja. One deliberate fix during extraction: `datetime.utcnow()` is deprecated
in Python 3.12 — use timezone-aware `datetime.now(timezone.utc)`.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_entities.py`:

```python
from dataclasses import dataclass
from datetime import timezone
from uuid import UUID

import pytest

from lich_core.entities import BaseEntity


def test_defaults():
    e = BaseEntity()
    assert isinstance(e.id, UUID)
    assert e.created_at.tzinfo == timezone.utc
    assert e.updated_at is None


def test_touch_sets_updated_at():
    e = BaseEntity()
    e.touch()
    assert e.updated_at is not None
    assert e.updated_at >= e.created_at


def test_subclass_validation_runs_on_init():
    @dataclass
    class Product(BaseEntity):
        price: int = 0

        def _validate(self):
            if self.price < 0:
                raise ValueError("price must be >= 0")

    with pytest.raises(ValueError, match="price must be >= 0"):
        Product(price=-1)
    assert Product(price=5).price == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_entities.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.entities'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/entities/base.py`:

```python
"""
Base Entity - Pure domain model.
NO external dependencies (no SQLAlchemy, no Pydantic).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    """
    Base class for all domain entities.

    IMPORTANT: This is a PURE domain model.
    - No ORM decorators
    - No Pydantic validators
    - No HTTP-related code

    All business rules and invariants should be enforced here.
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate invariants after initialization."""
        self._validate()

    def _validate(self):
        """
        Override in subclasses to enforce domain invariants.
        Raise ValueError for validation failures.
        """

    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = _utcnow()
```

Create `core/src/lich_core/entities/__init__.py`:

```python
from lich_core.entities.base import BaseEntity

__all__ = ["BaseEntity"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_entities.py -v`
Expected: 3 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.entities import BaseEntity
```

```bash
git add core/src/lich_core/entities/ core/tests/test_entities.py core/src/lich_core/__init__.py
git commit -m "feat(core): extract BaseEntity (tz-aware timestamps)"
```

---

## Task 4: Repository ports (generic)

**Files:**
- Create: `core/src/lich_core/ports/__init__.py`, `core/src/lich_core/ports/repository.py`
- Test: `core/tests/test_ports.py`
- Source (read-only): `template/{{cookiecutter.project_slug}}/backend/internal/ports/repositories.py`

De-Jinja decision: the template's `UserRepository` is User-specific (get_by_email, get_by_keycloak_id
behind Jinja conditionals). lich-core ships the **generic** `Repository[E]` port with the universal
CRUD surface; domain-specific lookups stay in the template's `UserRepository(Repository[User])`.
`CacheRepository` (template: behind `use_redis` Jinja) becomes unconditional — it is just an
interface; the redis *adapter* is what's optional.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_ports.py`:

```python
import inspect
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

import pytest

from lich_core.entities import BaseEntity
from lich_core.ports import CacheRepository, Repository


def test_repository_is_abstract():
    with pytest.raises(TypeError):
        Repository()  # type: ignore[abstract]


def test_repository_declares_crud_surface():
    for name in ("create", "get_by_id", "update", "delete", "list_all", "count"):
        method = getattr(Repository, name)
        assert getattr(method, "__isabstractmethod__", False), name
        assert inspect.iscoroutinefunction(method), f"{name} must be async"


@dataclass
class Thing(BaseEntity):
    name: str = ""


class InMemoryThingRepo(Repository[Thing]):
    def __init__(self):
        self._items: dict[UUID, Thing] = {}

    async def create(self, entity: Thing) -> Thing:
        self._items[entity.id] = entity
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[Thing]:
        return self._items.get(entity_id)

    async def update(self, entity: Thing) -> Thing:
        self._items[entity.id] = entity
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        return self._items.pop(entity_id, None) is not None

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Thing]:
        return list(self._items.values())[skip : skip + limit]

    async def count(self) -> int:
        return len(self._items)


async def test_concrete_subclass_works():
    repo = InMemoryThingRepo()
    t = await repo.create(Thing(name="a"))
    assert await repo.get_by_id(t.id) == t
    assert await repo.count() == 1
    assert await repo.delete(t.id) is True


def test_cache_repository_is_abstract():
    with pytest.raises(TypeError):
        CacheRepository()  # type: ignore[abstract]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_ports.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.ports'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/ports/repository.py`:

```python
"""
Repository Interfaces (Ports).
These are abstract interfaces that define what the domain needs.
Implementations (adapters) are injected at runtime.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from lich_core.entities import BaseEntity

E = TypeVar("E", bound=BaseEntity)


class Repository(ABC, Generic[E]):
    """
    Generic repository interface.

    This is a PORT - it defines WHAT the domain needs,
    not HOW it's implemented. The adapter provides the implementation.
    Domain-specific lookups (get_by_email, ...) belong on domain
    subclasses, e.g. ``class UserRepository(Repository[User])``.
    """

    @abstractmethod
    async def create(self, entity: E) -> E:
        """Create a new entity."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[E]:
        """Get entity by ID."""

    @abstractmethod
    async def update(self, entity: E) -> E:
        """Update an existing entity."""

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID. Returns True if it existed."""

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[E]:
        """List entities with pagination."""

    @abstractmethod
    async def count(self) -> int:
        """Count total entities."""


class CacheRepository(ABC):
    """Cache repository interface (key-value with TTL)."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""

    @abstractmethod
    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set value with optional expiration."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
```

Create `core/src/lich_core/ports/__init__.py`:

```python
from lich_core.ports.repository import CacheRepository, Repository

__all__ = ["CacheRepository", "Repository"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_ports.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.ports import CacheRepository, Repository
```

```bash
git add core/src/lich_core/ports/ core/tests/test_ports.py core/src/lich_core/__init__.py
git commit -m "feat(core): generic Repository[E] and CacheRepository ports"
```

---

## Task 5: Service base

**Files:**
- Create: `core/src/lich_core/services/__init__.py`, `core/src/lich_core/services/base.py`
- Test: `core/tests/test_services.py`

There is no service base in the template (UserService is standalone) — this codifies its pattern:
service holds a repository port, never knows HTTP or DB details. YAGNI: only the one helper
every template service duplicates (`get existing or raise NotFoundError`).

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_services.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID, uuid4

import pytest

from lich_core.entities import BaseEntity
from lich_core.errors import NotFoundError
from lich_core.ports import Repository
from lich_core.services import BaseService


@dataclass
class Widget(BaseEntity):
    name: str = ""


class InMemoryWidgetRepo(Repository[Widget]):
    def __init__(self):
        self._items: dict[UUID, Widget] = {}

    async def create(self, entity: Widget) -> Widget:
        self._items[entity.id] = entity
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[Widget]:
        return self._items.get(entity_id)

    async def update(self, entity: Widget) -> Widget:
        self._items[entity.id] = entity
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        return self._items.pop(entity_id, None) is not None

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Widget]:
        return list(self._items.values())[skip : skip + limit]

    async def count(self) -> int:
        return len(self._items)


class WidgetService(BaseService[Widget]):
    resource_name = "Widget"


async def test_get_or_404_returns_entity():
    repo = InMemoryWidgetRepo()
    w = await repo.create(Widget(name="w1"))
    svc = WidgetService(repo)
    assert await svc.get_or_404(w.id) == w


async def test_get_or_404_raises_not_found_with_resource_name():
    svc = WidgetService(InMemoryWidgetRepo())
    missing = uuid4()
    with pytest.raises(NotFoundError) as exc:
        await svc.get_or_404(missing)
    assert "Widget" in exc.value.message
    assert str(missing) in exc.value.message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_services.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.services'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/services/base.py`:

```python
"""
Service base - business logic layer.

Services:
- Contain business logic
- Use ports (interfaces) for external dependencies
- Never know about HTTP or database details
"""
from typing import Generic, TypeVar
from uuid import UUID

from lich_core.entities import BaseEntity
from lich_core.errors import NotFoundError
from lich_core.ports import Repository

E = TypeVar("E", bound=BaseEntity)


class BaseService(Generic[E]):
    """Base class for domain services backed by a single repository."""

    #: Human-readable name used in NotFoundError messages. Override in subclasses.
    resource_name: str = "Resource"

    def __init__(self, repository: Repository[E]):
        self.repository = repository

    async def get_or_404(self, entity_id: UUID) -> E:
        """Return the entity or raise NotFoundError with the resource name."""
        entity = await self.repository.get_by_id(entity_id)
        if entity is None:
            raise NotFoundError(self.resource_name, entity_id)
        return entity
```

Create `core/src/lich_core/services/__init__.py`:

```python
from lich_core.services.base import BaseService

__all__ = ["BaseService"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_services.py -v`
Expected: 2 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.services import BaseService
```

```bash
git add core/src/lich_core/services/ core/tests/test_services.py core/src/lich_core/__init__.py
git commit -m "feat(core): BaseService with get_or_404 helper"
```

---

## Task 6: Middleware — rate limit (fixed), security headers, CSRF

**Files:**
- Create: `core/src/lich_core/middleware/__init__.py`, `rate_limit.py`, `security_headers.py`, `csrf.py`
- Test: `core/tests/test_middleware.py`
- Sources (read-only): `template/.../backend/api/middleware/{rate_limit,security,csrf}.py`

Two fixes land during extraction (the whole point of lich-core — spec §3 rationale):
1. **Rate limiter eviction**: the template version never removes idle IPs from `self.requests`
   (memory leak). Fixed with a periodic sweep. Optional Redis backend via constructor kwarg.
2. `security.py` renamed to `security_headers.py` (spec module map).

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_middleware.py`:

```python
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient

from lich_core.middleware import (
    CSRFMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)


def make_app(**middleware):
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    @app.post("/write")
    async def write():
        return {"ok": True}

    for cls, kwargs in middleware.values():
        app.add_middleware(cls, **kwargs)
    return app


def test_security_headers_present():
    app = make_app(sec=(SecurityHeadersMiddleware, {}))
    r = TestClient(app).get("/ping")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "Permissions-Policy" in r.headers


def test_rate_limit_429_after_limit():
    app = make_app(rl=(RateLimitMiddleware, {"requests_per_minute": 3}))
    client = TestClient(app)
    for _ in range(3):
        assert client.get("/ping").status_code == 200
    r = client.get("/ping")
    assert r.status_code == 429
    assert r.headers["Retry-After"] == "60"


def test_rate_limit_evicts_idle_ips():
    mw = RateLimitMiddleware(None, requests_per_minute=5, sweep_interval_seconds=0)
    mw.requests["1.2.3.4"] = [time.time() - 120]  # stale entry
    mw._sweep(now=time.time())
    assert "1.2.3.4" not in mw.requests


def test_csrf_blocks_unsafe_without_token_and_allows_get():
    app = make_app(csrf=(CSRFMiddleware, {"secret_key": "test-secret"}))
    client = TestClient(app)
    assert client.get("/ping").status_code == 200
    assert client.post("/write").status_code == 403


def test_csrf_roundtrip():
    mw = CSRFMiddleware(None, secret_key="test-secret")
    token = mw._generate_token()
    assert mw._validate_token(token) is True
    assert mw._validate_token(token + "tampered") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_middleware.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.middleware'`)

- [ ] **Step 3: Write security_headers.py and csrf.py**

Create `core/src/lich_core/middleware/security_headers.py` with the exact content of the template's
`api/middleware/security.py` (no Jinja in source; copy verbatim, update module docstring header to
`lich-core Security Headers Middleware` and the enable-hint import path to
`from lich_core.middleware import SecurityHeadersMiddleware`).

Create `core/src/lich_core/middleware/csrf.py` with the exact content of the template's
`api/middleware/csrf.py` (copy verbatim including `get_csrf_router`, update docstring import hint to
`from lich_core.middleware import CSRFMiddleware`).

- [ ] **Step 4: Write the fixed rate_limit.py**

Create `core/src/lich_core/middleware/rate_limit.py`:

```python
"""
Rate Limit Middleware - Prevent API abuse.

In-memory fixed-window limiter with idle-IP eviction (default), or Redis-backed
fixed window when ``redis_url`` is provided (multi-worker safe).

Usage:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60, redis_url="redis://redis:6379/0")
"""
import time
from typing import Callable, Dict, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

EXEMPT_PATHS = ("/health", "/api/health")


def client_ip_from(request: Request) -> str:
    """Original client IP, honoring X-Forwarded-For behind Traefik/Nginx."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        redis_url: Optional[str] = None,
        sweep_interval_seconds: int = 60,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}
        self._redis = None
        self._redis_url = redis_url
        self._sweep_interval = sweep_interval_seconds
        self._last_sweep = time.time()

    def _sweep(self, now: float) -> None:
        """Evict IPs with no requests in the last window (fixes unbounded growth)."""
        minute_ago = now - 60
        stale = [ip for ip, stamps in self.requests.items() if not stamps or stamps[-1] <= minute_ago]
        for ip in stale:
            del self.requests[ip]
        self._last_sweep = now

    async def _check_redis(self, client_ip: str) -> Optional[int]:
        """Fixed-window count via Redis INCR+EXPIRE. Returns remaining, or None if over limit."""
        if self._redis is None:
            import redis.asyncio as aioredis  # requires lich-core[redis]

            self._redis = aioredis.from_url(self._redis_url)
        window = int(time.time() // 60)
        key = f"lich:ratelimit:{client_ip}:{window}"
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, 90)
        if count > self.requests_per_minute:
            return None
        return self.requests_per_minute - count

    def _check_memory(self, client_ip: str, now: float) -> Optional[int]:
        if now - self._last_sweep >= self._sweep_interval:
            self._sweep(now)
        minute_ago = now - 60
        stamps = [t for t in self.requests.get(client_ip, []) if t > minute_ago]
        if len(stamps) >= self.requests_per_minute:
            self.requests[client_ip] = stamps
            return None
        stamps.append(now)
        self.requests[client_ip] = stamps
        return self.requests_per_minute - len(stamps)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        client_ip = client_ip_from(request)
        if self._redis_url:
            remaining = await self._check_redis(client_ip)
        else:
            remaining = self._check_memory(client_ip, time.time())

        if remaining is None:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "retry_after": 60},
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
```

Create `core/src/lich_core/middleware/__init__.py`:

```python
from lich_core.middleware.csrf import CSRFMiddleware, get_csrf_router
from lich_core.middleware.rate_limit import RateLimitMiddleware
from lich_core.middleware.security_headers import SecurityHeadersMiddleware

__all__ = [
    "CSRFMiddleware",
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "get_csrf_router",
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd core && python -m pytest tests/test_middleware.py -v`
Expected: 5 PASSED (Redis path is exercised only in e2e; unit tests cover memory backend)

- [ ] **Step 6: Commit**

```bash
git add core/src/lich_core/middleware/ core/tests/test_middleware.py
git commit -m "feat(core): middleware extraction — rate limiter gains idle-IP eviction + optional Redis backend"
```

---

## Task 7: Settings + startup secret guard

**Files:**
- Create: `core/src/lich_core/config.py`
- Test: `core/tests/test_config.py`
- Source (read-only): `template/.../backend/pkg/config/settings.py`

De-Jinja decision: every conditional block (postgres/mongo/redis/keycloak/jwt) becomes an
always-present optional group with the same field names and defaults; projects use what they need.
The `"change-me"` guard (spec §Phase 1 of v1 hardening + D15) is built in: `validate_secrets()`
raises `LichConfigError` in production. `create_app()` calls it (Task 9).

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_config.py`:

```python
import pytest

from lich_core.config import LichSettings
from lich_core.errors import LichConfigError


def test_defaults_load_without_env():
    s = LichSettings()
    assert s.environment == "development"
    assert s.api_prefix == "/api/v1"
    assert s.database_url.startswith("postgresql+asyncpg://")
    assert s.redis_url.startswith("redis://")


def test_env_override(monkeypatch):
    monkeypatch.setenv("DB_HOST", "db.internal")
    s = LichSettings()
    assert "db.internal" in s.database_url


def test_validate_secrets_passes_in_development():
    LichSettings(environment="development").validate_secrets()  # no raise


def test_validate_secrets_raises_in_production_with_defaults():
    s = LichSettings(environment="production")
    with pytest.raises(LichConfigError) as exc:
        s.validate_secrets()
    msg = str(exc.value)
    assert "secret_key" in msg and "jwt_secret_key" in msg


def test_validate_secrets_ok_in_production_with_real_secrets():
    s = LichSettings(
        environment="production",
        secret_key="x" * 43,
        jwt_secret_key="y" * 43,
    )
    s.validate_secrets()  # no raise
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_config.py -v`
Expected: FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/config.py`:

```python
"""
Settings configuration using Pydantic Settings.
All configuration is loaded from environment variables.

Projects subclass ``LichSettings`` to add domain fields and override defaults:

    class Settings(LichSettings):
        project_name: str = "myapp"

``create_app()`` calls ``validate_secrets()`` during startup — a production
deployment with default secrets refuses to boot (LichConfigError).
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from lich_core.errors import LichConfigError

_PLACEHOLDER = "change-me"


class LichSettings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Project
    project_name: str = Field(default="lich-app")
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

    # PostgreSQL (used when the project installs lich-core[postgres])
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="app")
    db_password: str = Field(default="app_secret")
    db_name: str = Field(default="app")

    # MongoDB (used when the project installs lich-core[mongo])
    mongodb_host: str = Field(default="localhost")
    mongodb_port: int = Field(default=27017)
    mongodb_user: str = Field(default="app")
    mongodb_password: str = Field(default="app_secret")
    mongodb_db: str = Field(default="app")

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="")

    # Keycloak
    keycloak_url: str = Field(default="http://localhost:8080")
    keycloak_realm: str = Field(default="app")
    keycloak_client_id: str = Field(default="app-web")
    keycloak_client_secret: str = Field(default="")

    # JWT
    jwt_secret_key: str = Field(default=f"your-secret-key-{_PLACEHOLDER}")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # Google OAuth
    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    google_redirect_uri: str = Field(default="http://localhost:3000/auth/google/callback")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text")

    # Security
    secret_key: str = Field(default=f"your-secret-key-{_PLACEHOLDER}-in-production")

    @property
    def database_url(self) -> str:
        """Build async PostgreSQL URL."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def mongodb_url(self) -> str:
        """Build MongoDB URL."""
        return (
            f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
            f"@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
        )

    @property
    def redis_url(self) -> str:
        """Build Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    def validate_secrets(self) -> None:
        """Refuse to run production with placeholder secrets.

        Raises LichConfigError listing every offending field.
        """
        if self.environment != "production":
            return
        offending = [
            name
            for name in ("secret_key", "jwt_secret_key")
            if _PLACEHOLDER in getattr(self, name).lower() or not getattr(self, name)
        ]
        if offending:
            raise LichConfigError(
                "Refusing to start in production with placeholder secrets: "
                + ", ".join(offending)
                + ". Generate real values, e.g.: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_config.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.config import LichSettings
```

```bash
git add core/src/lich_core/config.py core/tests/test_config.py core/src/lich_core/__init__.py
git commit -m "feat(core): LichSettings with built-in production secret guard"
```

---

## Task 8: Auth — JWT

**Files:**
- Create: `core/src/lich_core/auth/__init__.py`, `core/src/lich_core/auth/jwt.py`
- Test: `core/tests/test_auth_jwt.py`
- Source (read-only): `template/.../backend/internal/services/auth_deps.py` (jwt_builtin branch)

De-Jinja + decoupling: the template's `create_access_token`/`create_refresh_token` read a global
`settings` — extracted versions take the settings object explicitly (no global state in a library).
A `decode_token` helper (the template inlines this in `get_current_user`) raises lich-core
`AuthenticationError` so apps get consistent 401s.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_auth_jwt.py`:

```python
import pytest

from lich_core.auth import create_access_token, create_refresh_token, decode_token
from lich_core.config import LichSettings
from lich_core.errors import AuthenticationError

SETTINGS = LichSettings(jwt_secret_key="unit-test-secret")


def test_access_token_roundtrip():
    token = create_access_token({"sub": "user-1"}, SETTINGS)
    payload = decode_token(token, SETTINGS, expected_type="access")
    assert payload["sub"] == "user-1"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_roundtrip():
    token = create_refresh_token({"sub": "user-1"}, SETTINGS)
    payload = decode_token(token, SETTINGS, expected_type="refresh")
    assert payload["type"] == "refresh"


def test_wrong_type_rejected():
    token = create_refresh_token({"sub": "user-1"}, SETTINGS)
    with pytest.raises(AuthenticationError):
        decode_token(token, SETTINGS, expected_type="access")


def test_tampered_token_rejected():
    token = create_access_token({"sub": "user-1"}, SETTINGS)
    with pytest.raises(AuthenticationError):
        decode_token(token + "x", SETTINGS, expected_type="access")


def test_wrong_secret_rejected():
    token = create_access_token({"sub": "user-1"}, SETTINGS)
    other = LichSettings(jwt_secret_key="different-secret")
    with pytest.raises(AuthenticationError):
        decode_token(token, other, expected_type="access")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_auth_jwt.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.auth'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/auth/jwt.py`:

```python
"""JWT helpers (access/refresh). Requires lich-core[auth]."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from lich_core.config import LichSettings
from lich_core.errors import AuthenticationError


def create_access_token(
    data: dict, settings: LichSettings, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict, settings: LichSettings) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, settings: LichSettings, expected_type: str = "access") -> dict:
    """Decode and validate a token; raises AuthenticationError on any failure."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthenticationError("Invalid token") from exc
    if payload.get("type") != expected_type:
        raise AuthenticationError("Invalid token type")
    return payload
```

Create `core/src/lich_core/auth/__init__.py`:

```python
from lich_core.auth.jwt import create_access_token, create_refresh_token, decode_token

__all__ = ["create_access_token", "create_refresh_token", "decode_token"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && pip install -e ".[dev,auth]" && python -m pytest tests/test_auth_jwt.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/src/lich_core/auth/ core/tests/test_auth_jwt.py
git commit -m "feat(core): JWT helpers — settings-explicit, typed 401 errors"
```

---

## Task 9: Auth — Keycloak (JWKS cache + external-user callback)

**Files:**
- Create: `core/src/lich_core/auth/keycloak.py`
- Modify: `core/src/lich_core/auth/__init__.py`
- Test: `core/tests/test_auth_keycloak.py`
- Source (read-only): `template/.../backend/internal/services/auth_deps.py` (keycloak branch)

Two template bugs fixed at the design level:
1. **JWKS fetched on every request** → `KeycloakVerifier` caches JWKS with a TTL.
2. **Auto-created users crash** (CreateUserRequest without password) → lich-core does NOT create
   users. `verify()` returns claims; the app registers its own provisioning logic. The template's
   provisioning path is rewritten in Task 13 with a dedicated external-user method.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_auth_keycloak.py`:

```python
import time
from unittest.mock import AsyncMock, patch

import pytest

from lich_core.auth import KeycloakVerifier
from lich_core.errors import AuthenticationError, ExternalServiceError

JWKS = {"keys": [{"kty": "RSA", "kid": "k1", "n": "abc", "e": "AQAB"}]}


def make_verifier(**kwargs):
    return KeycloakVerifier(
        url="http://keycloak:8080", realm="test", client_id="test-web", **kwargs
    )


async def test_jwks_is_cached():
    v = make_verifier(jwks_ttl_seconds=3600)
    with patch.object(v, "_fetch_jwks", new=AsyncMock(return_value=JWKS)) as fetch:
        await v._get_jwks()
        await v._get_jwks()
    assert fetch.await_count == 1


async def test_jwks_refetched_after_ttl():
    v = make_verifier(jwks_ttl_seconds=0)
    with patch.object(v, "_fetch_jwks", new=AsyncMock(return_value=JWKS)) as fetch:
        await v._get_jwks()
        time.sleep(0.01)
        await v._get_jwks()
    assert fetch.await_count == 2


async def test_invalid_token_raises_authentication_error():
    v = make_verifier()
    with patch.object(v, "_fetch_jwks", new=AsyncMock(return_value=JWKS)):
        with pytest.raises(AuthenticationError):
            await v.verify("not-a-jwt")


async def test_unreachable_keycloak_raises_external_service_error():
    v = make_verifier()
    with patch.object(v, "_fetch_jwks", new=AsyncMock(side_effect=ExternalServiceError("Keycloak"))):
        with pytest.raises(ExternalServiceError):
            await v.verify("whatever")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_auth_keycloak.py -v`
Expected: FAIL (`ImportError: cannot import name 'KeycloakVerifier'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/auth/keycloak.py`:

```python
"""Keycloak token verification with cached JWKS. Requires lich-core[auth].

lich-core verifies tokens and returns claims. User provisioning (get-or-create)
is application logic — register it app-side, e.g.:

    verifier = KeycloakVerifier(url=..., realm=..., client_id=...)

    async def current_user(creds = Depends(security), svc = Depends(get_user_service)):
        claims = await verifier.verify(creds.credentials)
        return await svc.get_or_create_external_user(claims)
"""
import time
from typing import Optional

from jose import JWTError, jwt

from lich_core.errors import AuthenticationError, ExternalServiceError


class KeycloakVerifier:
    """Verifies Keycloak RS256 tokens; caches the realm JWKS with a TTL."""

    def __init__(self, url: str, realm: str, client_id: str, jwks_ttl_seconds: int = 3600):
        self.url = url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self.jwks_ttl_seconds = jwks_ttl_seconds
        self._jwks: Optional[dict] = None
        self._jwks_fetched_at: float = 0.0

    @property
    def jwks_url(self) -> str:
        return f"{self.url}/realms/{self.realm}/protocol/openid-connect/certs"

    async def _fetch_jwks(self) -> dict:
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Keycloak", "JWKS endpoint unreachable") from exc

    async def _get_jwks(self) -> dict:
        now = time.time()
        if self._jwks is None or now - self._jwks_fetched_at >= self.jwks_ttl_seconds:
            self._jwks = await self._fetch_jwks()
            self._jwks_fetched_at = now
        return self._jwks

    async def verify(self, token: str) -> dict:
        """Verify signature/audience and return the claims dict.

        Raises AuthenticationError (bad token) or ExternalServiceError (Keycloak down).
        """
        jwks = await self._get_jwks()
        try:
            return jwt.decode(token, jwks, algorithms=["RS256"], audience=self.client_id)
        except JWTError as exc:
            raise AuthenticationError("Invalid token") from exc
```

Update `core/src/lich_core/auth/__init__.py`:

```python
from lich_core.auth.jwt import create_access_token, create_refresh_token, decode_token
from lich_core.auth.keycloak import KeycloakVerifier

__all__ = ["KeycloakVerifier", "create_access_token", "create_refresh_token", "decode_token"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_auth_keycloak.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/src/lich_core/auth/ core/tests/test_auth_keycloak.py
git commit -m "feat(core): KeycloakVerifier with TTL-cached JWKS; provisioning stays app-side"
```

---

## Task 10: DI container

**Files:**
- Create: `core/src/lich_core/container.py`
- Test: `core/tests/test_container.py`

Fixes the "new repo per request" pattern (review finding): app-level singletons registered once,
resolved everywhere. No external library (YAGNI) — dict-based, type-keyed.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_container.py`:

```python
import pytest

from lich_core.container import Container


class Repo:
    pass


class Service:
    def __init__(self, repo: Repo):
        self.repo = repo


def test_register_and_resolve_singleton():
    c = Container()
    repo = Repo()
    c.register(Repo, repo)
    assert c.resolve(Repo) is repo
    assert c.resolve(Repo) is repo  # same instance every time


def test_register_factory_is_lazy_and_cached():
    c = Container()
    calls = []
    c.register_factory(Repo, lambda: (calls.append(1), Repo())[1])
    assert calls == []
    first = c.resolve(Repo)
    second = c.resolve(Repo)
    assert first is second
    assert calls == [1]


def test_factory_can_depend_on_container():
    c = Container()
    c.register(Repo, Repo())
    c.register_factory(Service, lambda: Service(c.resolve(Repo)))
    assert c.resolve(Service).repo is c.resolve(Repo)


def test_resolve_unregistered_raises_lookup_error():
    with pytest.raises(LookupError, match="Repo"):
        Container().resolve(Repo)


def test_contains():
    c = Container()
    assert Repo not in c
    c.register(Repo, Repo())
    assert Repo in c
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_container.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.container'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/container.py`:

```python
"""Minimal DI container: app-level singletons for repositories and services.

Register once at startup (or via create_app hooks), resolve anywhere:

    container.register(UserRepository, SQLAlchemyUserRepository(session_factory))
    container.register_factory(UserService, lambda: UserService(container.resolve(UserRepository)))
"""
from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")


class Container:
    def __init__(self):
        self._instances: Dict[Any, Any] = {}
        self._factories: Dict[Any, Callable[[], Any]] = {}

    def register(self, key: Type[T], instance: T) -> None:
        """Register a ready singleton instance."""
        self._instances[key] = instance

    def register_factory(self, key: Type[T], factory: Callable[[], T]) -> None:
        """Register a lazy factory; called once on first resolve, then cached."""
        self._factories[key] = factory

    def resolve(self, key: Type[T]) -> T:
        """Return the singleton for ``key``; build it from the factory if needed."""
        if key in self._instances:
            return self._instances[key]
        if key in self._factories:
            instance = self._factories.pop(key)()
            self._instances[key] = instance
            return instance
        raise LookupError(f"Nothing registered for {getattr(key, '__name__', key)!r}")

    def __contains__(self, key: Any) -> bool:
        return key in self._instances or key in self._factories
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_container.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.container import Container
```

```bash
git add core/src/lich_core/container.py core/tests/test_container.py core/src/lich_core/__init__.py
git commit -m "feat(core): minimal type-keyed DI container"
```

---

## Task 11: create_app() factory

**Files:**
- Create: `core/src/lich_core/app.py`
- Test: `core/tests/test_app.py`
- Source (read-only): `template/.../backend/main.py`

Inversion of control: today the template's `main.py` wires everything by hand (middleware all
commented out — review finding "security disabled by default"). `create_app()` wires CORS +
security headers + rate limit by default, validates secrets, runs startup/shutdown hooks with the
container, registers health endpoints and the AppException→JSON handler.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_app.py`:

```python
from fastapi import APIRouter
from fastapi.testclient import TestClient

import pytest

from lich_core import Container, LichSettings
from lich_core.app import create_app
from lich_core.errors import LichConfigError, NotFoundError


def test_health_endpoints():
    app = create_app(LichSettings(), discover_plugins=False)
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "healthy"
    assert client.get("/api/health").json()["status"] == "healthy"


def test_routers_mounted_under_prefix():
    router = APIRouter()

    @router.get("/things")
    async def things():
        return []

    app = create_app(LichSettings(), routers=[router], discover_plugins=False)
    assert TestClient(app).get("/api/v1/things").status_code == 200


def test_app_exception_becomes_json():
    router = APIRouter()

    @router.get("/boom")
    async def boom():
        raise NotFoundError("Widget", "w-1")

    app = create_app(LichSettings(), routers=[router], discover_plugins=False)
    r = TestClient(app).get("/api/v1/boom")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_security_headers_on_by_default():
    app = create_app(LichSettings(), discover_plugins=False)
    r = TestClient(app).get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_production_with_default_secrets_refuses_to_boot():
    app = create_app(LichSettings(environment="production"), discover_plugins=False)
    with pytest.raises(LichConfigError):
        with TestClient(app):  # enters lifespan
            pass


def test_startup_hook_receives_container():
    seen = {}

    async def hook(container: Container):
        seen["container"] = container

    app = create_app(LichSettings(), on_startup=[hook], discover_plugins=False)
    with TestClient(app):
        pass
    assert isinstance(seen["container"], Container)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_app.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.app'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/app.py`:

```python
"""create_app() — the lich-core application factory (inversion of control).

    from lich_core import create_app, LichSettings

    app = create_app(LichSettings(), routers=[users_router], on_startup=[init_db])
"""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, Sequence

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from lich_core.config import LichSettings
from lich_core.container import Container
from lich_core.errors import AppException
from lich_core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

StartupHook = Callable[[Container], Awaitable[None]]


@dataclass
class MiddlewareConfig:
    """Which built-in middleware create_app wires. Secure defaults."""

    security_headers: bool = True
    rate_limit_per_minute: Optional[int] = 60
    rate_limit_redis_url: Optional[str] = None


def create_app(
    settings: Optional[LichSettings] = None,
    *,
    routers: Sequence = (),
    container: Optional[Container] = None,
    on_startup: Sequence[StartupHook] = (),
    on_shutdown: Sequence[StartupHook] = (),
    middleware: Optional[MiddlewareConfig] = None,
    discover_plugins: bool = True,
    title: Optional[str] = None,
) -> FastAPI:
    settings = settings or LichSettings()
    container = container or Container()
    middleware = middleware or MiddlewareConfig()
    container.register(LichSettings, settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.validate_secrets()  # crash-at-boot guard, never in a request
        for hook in on_startup:
            await hook(container)
        yield
        for hook in on_shutdown:
            await hook(container)

    app = FastAPI(
        title=title or f"{settings.project_name} API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.state.container = container
    app.state.settings = settings

    # Middleware — order matters: added last runs first.
    if middleware.rate_limit_per_minute:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=middleware.rate_limit_per_minute,
            redis_url=middleware.rate_limit_redis_url,
        )
    if middleware.security_headers:
        app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.get("/health")
    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "service": settings.project_name}

    for router in routers:
        app.include_router(router, prefix=settings.api_prefix)

    if discover_plugins:
        from lich_core.plugins import load_plugins

        load_plugins(app, container)

    return app
```

Note: `lich_core.plugins` does not exist yet — Task 12 creates it. For this task's tests every
call passes `discover_plugins=False`, so the import never executes.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd core && python -m pytest tests/test_app.py -v`
Expected: 6 PASSED

- [ ] **Step 5: Export and commit**

Add to `core/src/lich_core/__init__.py`:

```python
from lich_core.app import MiddlewareConfig, create_app
```

```bash
git add core/src/lich_core/app.py core/tests/test_app.py core/src/lich_core/__init__.py
git commit -m "feat(core): create_app factory — secure middleware defaults, boot-time secret guard, DI wiring"
```

---

## Task 12: Plugin discovery (lich.plugins entry points)

**Files:**
- Create: `core/src/lich_core/plugins.py`
- Test: `core/tests/test_plugins.py`

Consumes the same `lich.plugins` entry-points group as Feature 7 (spec §11): runtime plugin parts
(middleware, startup hooks) register through lich-core; scaffold parts stay copy-in.

- [ ] **Step 1: Write the failing test**

Create `core/tests/test_plugins.py`:

```python
from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from lich_core.container import Container
from lich_core.plugins import load_plugins


def _entry_point(plugin) -> MagicMock:
    ep = MagicMock()
    ep.name = "demo"
    ep.load.return_value = plugin
    return ep


def test_plugins_register_with_app_and_container():
    class Plugin:
        def __init__(self):
            self.seen = None

        def register(self, app, container):
            self.seen = (app, container)

    plugin = Plugin()
    app, container = FastAPI(), Container()
    with patch("lich_core.plugins.entry_points", return_value=[_entry_point(plugin)]):
        loaded = load_plugins(app, container)
    assert loaded == ["demo"]
    assert plugin.seen == (app, container)


def test_plugin_without_register_is_skipped_not_fatal():
    app, container = FastAPI(), Container()
    with patch("lich_core.plugins.entry_points", return_value=[_entry_point(object())]):
        assert load_plugins(app, container) == []


def test_no_plugins_installed():
    with patch("lich_core.plugins.entry_points", return_value=[]):
        assert load_plugins(FastAPI(), Container()) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd core && python -m pytest tests/test_plugins.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'lich_core.plugins'`)

- [ ] **Step 3: Write the implementation**

Create `core/src/lich_core/plugins.py`:

```python
"""Runtime plugin discovery via the ``lich.plugins`` entry-points group.

A plugin exposes an object with ``register(app, container)``:

    # plugin pyproject.toml
    [project.entry-points."lich.plugins"]
    my_plugin = "my_plugin:plugin"
"""
import logging
from importlib.metadata import entry_points
from typing import List

from fastapi import FastAPI

from lich_core.container import Container

logger = logging.getLogger("lich_core.plugins")

GROUP = "lich.plugins"


def load_plugins(app: FastAPI, container: Container) -> List[str]:
    """Load every installed lich plugin. Returns names of successfully registered plugins.

    A broken plugin is logged and skipped — one bad install must not brick the app.
    """
    loaded: List[str] = []
    for ep in entry_points(group=GROUP):
        try:
            plugin = ep.load()
            register = getattr(plugin, "register", None)
            if register is None:
                logger.warning("lich plugin %r has no register(app, container); skipped", ep.name)
                continue
            register(app, container)
            loaded.append(ep.name)
        except Exception:
            logger.exception("lich plugin %r failed to load; skipped", ep.name)
    return loaded
```

- [ ] **Step 4: Run tests to verify they pass (including full suite)**

Run: `cd core && python -m pytest -q`
Expected: all tests pass (48 tests across Tasks 1-12), no errors, exit code 0

- [ ] **Step 5: Commit**

```bash
git add core/src/lich_core/plugins.py core/tests/test_plugins.py
git commit -m "feat(core): lich.plugins entry-point discovery in create_app"
```

---

## Task 13: Template shrink **[RE-VERIFY]**

**Files (re-read every one first — v1 hardening phases 1-2 modified them):**
- Modify: `template/{{cookiecutter.project_slug}}/backend/requirements.txt`
- Modify: `template/{{cookiecutter.project_slug}}/backend/main.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/pkg/config/settings.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/entities/base.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/ports/repositories.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/services/auth_deps.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/services/user_service.py`
- Delete: `backend/api/middleware/rate_limit.py`, `security.py`, `csrf.py`, `backend/pkg/errors/exceptions.py`

This task is written at design granularity because exact template content WILL have drifted
(v1 Phase 1 adds the secret guard to settings.py; Phase 2 fixes auth_deps.py and rate_limit.py —
those copies get *deleted* here in favor of the lich-core versions that already contain the fixes).

- [ ] **Step 1: Add lich-core to generated requirements**

In `backend/requirements.txt`, add at the top (keep the Jinja conditionals that select extras):

```
lich-core[{% if cookiecutter.database == 'postgresql' %}postgres{% else %}mongo{% endif %}{% if cookiecutter.use_redis == 'yes' %},redis{% endif %}{% if cookiecutter.auth_strategy != 'none' %},auth{% endif %}]>=0.1.0
```

- [ ] **Step 2: Rewrite main.py on create_app**

Replace the FastAPI construction + commented middleware block + health endpoints in
`backend/main.py` with:

```python
from lich_core import create_app

from pkg.config.settings import Settings
from api.http import router as api_router
from internal.bootstrap import startup, shutdown

settings = Settings()
app = create_app(
    settings,
    routers=[api_router],
    on_startup=[startup],
    on_shutdown=[shutdown],
)
```

and create `backend/internal/bootstrap.py` that moves the current lifespan body (init_db, redis
init behind the existing Jinja conditionals) into `async def startup(container)` / `async def
shutdown(container)`, registering repos/services in the container:

```python
from lich_core import Container

from internal.adapters.db.connection import init_db


async def startup(container: Container) -> None:
    await init_db()


async def shutdown(container: Container) -> None:
    pass
```

Repositories/services stay **request-scoped** via the existing FastAPI `get_user_service`
dependency (a DB session must not be an app-level singleton); the container carries settings and
future true singletons (cache client, external verifiers). Move the module-level
`KeycloakVerifier` (Step 4) into the container here if the keycloak branch is active:
`container.register(KeycloakVerifier, verifier)`. (Exact wiring depends on the post-v1
session-management shape of `connection.py` — RE-VERIFY.)

- [ ] **Step 3: Shrink settings.py to a subclass**

`backend/pkg/config/settings.py` becomes (keeping the project-specific Jinja defaults only):

```python
from lich_core import LichSettings
from pydantic import Field


class Settings(LichSettings):
    project_name: str = Field(default="{{ cookiecutter.project_slug }}")
    db_name: str = Field(default="{{ cookiecutter.project_slug }}")
    mongodb_db: str = Field(default="{{ cookiecutter.project_slug }}")
    keycloak_realm: str = Field(default="{{ cookiecutter.project_slug }}")
    keycloak_client_id: str = Field(default="{{ cookiecutter.project_slug }}-web")


settings = Settings()
```

Delete the v1 secret-guard code here if v1 Phase 1 added it — the guard now lives in
`LichSettings.validate_secrets()` and runs via create_app's lifespan.

- [ ] **Step 4: Point domain code at lich_core**

- `internal/entities/base.py` → replace body with `from lich_core.entities import BaseEntity  # noqa: F401` (kept as a module so existing imports in user.py keep working).
- `internal/ports/repositories.py` → keep `UserRepository`, but `class UserRepository(Repository["User"])` importing `Repository` from `lich_core.ports`; keep only the User-specific abstract methods (get_by_email, get_by_username, keycloak conditional); delete the generic CRUD methods now inherited; delete the `CacheRepository` class (import from lich_core where used).
- `pkg/errors/` usages → rewire imports to `from lich_core.errors import ...` (grep for `pkg.errors`), delete `pkg/errors/exceptions.py`.
- `internal/services/auth_deps.py` → import `create_access_token`/`create_refresh_token`/`decode_token` from `lich_core.auth`; keycloak branch builds a module-level `KeycloakVerifier(settings.keycloak_url, settings.keycloak_realm, settings.keycloak_client_id)` and calls `await verifier.verify(token)`; user provisioning calls a new `UserService.get_or_create_external_user(claims)` method added to `user_service.py` (creates User with a random internal `secrets.token_urlsafe(32)` password hash — this is the durable fix for the Keycloak no-password crash, replacing whatever interim fix v1 Phase 2 applied).
- Delete `api/middleware/rate_limit.py`, `api/middleware/security.py`, `api/middleware/csrf.py`; keep timing/logging/audit/sanitize.

- [ ] **Step 5: Verify by generation**

Run (from repo root):

```bash
pip install cookiecutter && rm -rf /tmp/lich-shrink-test && mkdir -p /tmp/lich-shrink-test
cookiecutter template/ --no-input -o /tmp/lich-shrink-test
grep -r "lich_core" /tmp/lich-shrink-test/*/backend/main.py
! grep -rq "class RateLimitMiddleware" /tmp/lich-shrink-test/*/backend/ && echo "NO-COPY-IN-OK"
```

Expected: `lich_core` import present; `NO-COPY-IN-OK`.

- [ ] **Step 6: Run template's generated tests against local lich-core**

```bash
cd /tmp/lich-shrink-test/*/backend && python -m venv .venv && . .venv/bin/activate
pip install -e /Users/babak/codes/DoTech/lich-framework/core"[postgres,redis,auth]" && pip install -r requirements.txt || true
python -c "from main import app; print(type(app))"
```

Expected: `<class 'fastapi.applications.FastAPI'>` (full pytest run happens in Task 14's e2e).

- [ ] **Step 7: Commit**

```bash
git add template/
git commit -m "feat(template)!: shrink to skeleton + domain code on lich-core (generated projects now depend on lich-core)"
```

---

## Task 14: Golden-path e2e with lich-core **[RE-VERIFY]**

**Files (created by v1 Phase 4 — re-read them first):**
- Modify: `scripts/e2e_local.sh`
- Modify: `.github/workflows/e2e.yml`

lich-core is not on PyPI during development, so the generated project's Docker build must find it
locally: build the wheel, drop it into the generated backend as `vendor/`, and let pip's
`--find-links` resolve `lich-core>=0.1.0` from there (falls back to PyPI transparently after
the first `core-v*` release).

- [ ] **Step 1: Add wheel vendoring to e2e_local.sh**

After the "generate project" step and before the docker build step in `scripts/e2e_local.sh`, insert:

```bash
# --- vendor local lich-core wheel so the Docker build can resolve it pre-PyPI ---
python -m pip install --quiet build
python -m build --wheel core/ --outdir "${GEN_DIR}/backend/vendor/"
# pip reads --find-links from within requirements files
sed -i.bak '1i\
--find-links=vendor/
' "${GEN_DIR}/backend/requirements.txt" && rm "${GEN_DIR}/backend/requirements.txt.bak"
```

(`GEN_DIR` = the generated project dir variable used by the script — RE-VERIFY its actual name.)

- [ ] **Step 2: Run both matrix combos locally**

Run: `./scripts/e2e_local.sh postgresql jwt_builtin && ./scripts/e2e_local.sh mongodb none`
Expected: both end with `=== E2E PASSED ... ===`, exit 0. A failure here is a real Phase 0
regression — fix the template/core issue it reveals; do not weaken the script.

- [ ] **Step 3: Ensure CI builds the wheel too**

In `.github/workflows/e2e.yml`, the runner script already does the vendoring (Step 1 runs inside
`e2e_local.sh`), so the only change needed is triggering: add `core/**` to the `paths:` filter so
core changes run the e2e. Verify with:

Run: `python -c "import yaml; d=yaml.safe_load(open('.github/workflows/e2e.yml')); print(d[True]['pull_request']['paths'])"`
Expected: list includes `core/**`.

- [ ] **Step 4: Commit**

```bash
git add scripts/e2e_local.sh .github/workflows/e2e.yml
git commit -m "test(e2e): golden path runs generated project against local lich-core wheel"
```

---

## Task 15: VERSIONING.md + phase completion

**Files:**
- Create: `core/VERSIONING.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write the versioning policy**

Create `core/VERSIONING.md`:

```markdown
# lich-core Versioning Policy

## Public API

The public API is exactly what `lich_core/__init__.py` re-exports (plus the
`lich_core.middleware`, `lich_core.auth`, `lich_core.ports`, `lich_core.entities`,
`lich_core.services` module exports). Anything else is private and may change
in any release.

## Semver

- **MAJOR**: breaking change to any public name, signature, or documented behavior.
- **MINOR**: new public API; deprecations announced.
- **PATCH**: bug fixes only.

## Deprecation policy

A public API is never removed without first emitting `DeprecationWarning` for at
least **one full MINOR version**. The warning names the replacement and the
removal version. Deprecations are listed in CHANGELOG.md under "Deprecated".

## Support window

The latest MINOR of the current MAJOR receives fixes. v1 copy-in projects
(pre-lich-core) are grandfathered and unaffected by this policy.

## Release procedure

Tag `core-vX.Y.Z` → `.github/workflows/publish-core.yml` builds, tests, and
publishes to PyPI (trusted publishing).
```

- [ ] **Step 2: Full verification suite**

Run: `cd core && python -m pytest -q && cd .. && ./scripts/e2e_local.sh postgresql jwt_builtin`
Expected: all core tests pass; e2e passes.

- [ ] **Step 3: Changelog + commit**

Add to `CHANGELOG.md` under a new `## lich-core [0.1.0]` heading:

```markdown
## lich-core [0.1.0] - <today's date>

### Added
- New `lich-core` runtime package (v2 Phase 0): BaseEntity, generic Repository/CacheRepository
  ports, BaseService, middleware (rate limit with idle-IP eviction + optional Redis backend,
  security headers, CSRF), LichSettings with production secret guard, JWT helpers,
  KeycloakVerifier with cached JWKS, DI container, `create_app()` factory,
  `lich.plugins` entry-point discovery.

### Changed
- **BREAKING (template only):** projects generated by `lich new` now depend on `lich-core`;
  copied-in middleware/config/errors/auth boilerplate removed from the template.
  Existing (v1) projects are unaffected (grandfathered).
```

```bash
git add core/VERSIONING.md CHANGELOG.md
git commit -m "docs(core): versioning + deprecation policy; changelog for 0.1.0"
```

- [ ] **Step 4: Report**

Report to the human: Phase 0 complete, list commits, core test count, e2e status. Tagging
`core-v0.1.0` (first PyPI publish) is a human decision — do NOT tag or publish.

---

## Spec coverage self-check (for the reviewer)

| Spec item (v2 §3 + Phase 0 table) | Task |
|---|---|
| 0.1 package skeleton + publish workflow | 1 |
| errors (implied by service base + guard) | 2 |
| 0.2 BaseEntity | 3 |
| 0.3 repository ports + service base | 4, 5 |
| 0.4 middleware (redis rate limit, headers, csrf) | 6 |
| 0.5 settings + change-me guard | 7 |
| 0.6 JWT + Keycloak adapters | 8, 9 |
| 0.7 create_app + DI container | 10, 11 |
| 0.8 plugin entry points | 12 |
| 0.9 template shrink | 13 [RE-VERIFY] |
| 0.10 golden-path e2e | 14 [RE-VERIFY] |
| 0.11 semver + deprecation doc | 15 |

Deviations from spec (intentional, YAGNI): `services/base.py` ships only `get_or_404`;
timing/logging/audit/sanitize middleware stay copy-in; no DB adapters extracted in Phase 0
(SQLAlchemy/Beanie repo bases deferred until the session-management shape settles post-v1-Phase 2).

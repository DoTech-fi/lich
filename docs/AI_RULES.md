# 🧙 Lich Framework - AI Rules

> **این فایل رو به AI بده تا بفهمه چطور با Lich کار کنه**

---

## Framework Identity

**Lich Framework** is a production-ready full-stack project generator inspired by Laravel's elegance and Django's batteries-included philosophy, built for Python (FastAPI) + Next.js.

### Core Philosophy
- **Clean Architecture** - Entities → Ports → Adapters
- **AI-Ready** - Rules, context, and documentation for AI agents
- **Production-Grade** - Security, observability, Docker from day 1

---

## CLI Commands Reference

### Project Management
| Command | Description |
|---------|-------------|
| `lich init` | Create new project |
| `lich adopt <path>` | Import existing Python project |
| `lich version` | Show version & changelog |
| `lich upgrade` | Upgrade to newer version |
| `lich check` | Validate project structure |

### Development
| Command | Description |
|---------|-------------|
| `lich dev` | Start all services |
| `lich stop` | Stop all services |
| `lich shell` | Python REPL with project context |
| `lich routes` | List all API routes |
| `lich test` | Run tests (pytest) |
| `lich seed` | Seed database |

### Code Generators (`lich make`)
| Command | Creates |
|---------|---------|
| `lich make entity <Name>` | Entity + Port + Adapter |
| `lich make service <Name>` | Service class |
| `lich make api <name>` | FastAPI router with CRUD |
| `lich make dto <Name>` | Pydantic DTOs |
| `lich make factory <Name>` | Test factory with Faker |
| `lich make middleware <Name>` | FastAPI middleware |
| `lich make event <Name>` | Domain event |
| `lich make listener <Name>` | Event listener |
| `lich make job <Name>` | Background job (Celery/Temporal) |
| `lich make policy <Name>` | Authorization policy |

### Database (`lich migration`)
| Command | Description |
|---------|-------------|
| `lich migration init` | Initialize Alembic |
| `lich migration create "msg"` | Create migration |
| `lich migration up` | Apply migrations |
| `lich migration down` | Rollback migrations |
| `lich migration status` | Show current status |

---

## Architecture Rules (CRITICAL)

### Dependency Flow

```
API Layer (FastAPI routers)
    ↓ uses
Service Layer (Business logic)
    ↓ uses
Domain Layer (Entities)
    ↓ defined by
Ports Layer (Interfaces)
    ↓ implemented by
Adapters Layer (DB, Redis, HTTP)
```

### Import Rules

✅ **ALLOWED:**
```python
api → services
api → dto
services → entities
services → ports
adapters → entities
adapters implements ports
```

❌ **FORBIDDEN:**
```python
entities → services    # Domain must be pure
entities → adapters    # Domain must be pure
services → adapters    # Use ports + DI
```

---

## Code Generation Patterns

### When Adding a New Feature

```bash
# 1. Create domain model
lich make entity Feature

# 2. Create business logic
lich make service FeatureService

# 3. Create API endpoints
lich make api features

# 4. Create DTOs
lich make dto Feature

# 5. Create migration
lich migration create "add features table"
lich migration up
```

### When Adding Events/Listeners

```bash
# 1. Create the event
lich make event SomethingHappened

# 2. Create listeners
lich make listener DoSomething --event SomethingHappened
lich make listener DoAnotherThing --event SomethingHappened
```

### When Adding Background Jobs

```bash
# For simple tasks (Celery)
lich make job SendEmail --queue celery

# For complex workflows (Temporal)
lich make job ProcessOrder --queue temporal
```

---

## File Locations

| What | Where |
|------|-------|
| Entities | `backend/internal/entities/` |
| Services | `backend/internal/services/` |
| Ports | `backend/internal/ports/` |
| Adapters (DB) | `backend/internal/adapters/db/` |
| DTOs | `backend/internal/dto/` |
| Events | `backend/internal/events/` |
| Listeners | `backend/internal/listeners/` |
| Jobs | `backend/internal/jobs/` |
| Policies | `backend/internal/policies/` |
| API Routes | `backend/api/http/` |
| Middleware | `backend/api/middleware/` |
| Factories | `backend/tests/factories/` |
| Seeds | `backend/seeds/` |

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Entity | PascalCase | `User`, `OrderItem` |
| Service | PascalCase + Service | `UserService` |
| Port | PascalCase + Port | `UserPort` |
| Repository | PascalCase + Repository | `UserRepository` |
| Event | PascalCase (past tense) | `UserRegistered` |
| Listener | PascalCase (action) | `SendWelcomeEmail` |
| Job | PascalCase + Job | `SendInvoiceJob` |
| Policy | PascalCase + Policy | `PostPolicy` |
| DTO | PascalCase + Create/Update/Response | `UserCreate` |

---

## Security Rules

1. **Never** store tokens in localStorage
2. **Always** validate input with Pydantic
3. **Never** hardcode secrets
4. **Always** use parameterized SQL
5. **Never** log passwords or tokens
6. **Always** use httpOnly cookies for auth

---

## Testing

```bash
# Run all tests
lich test

# Run with coverage
lich test --coverage

# Watch mode
lich test --watch

# Specific path
lich test backend/tests/unit/
```

---

## Project Structure

```
project/
├── backend/
│   ├── main.py
│   ├── internal/
│   │   ├── entities/      # Domain models
│   │   ├── services/      # Business logic
│   │   ├── ports/         # Interfaces
│   │   ├── adapters/      # Implementations
│   │   ├── dto/           # Pydantic schemas
│   │   ├── events/        # Domain events
│   │   ├── listeners/     # Event handlers
│   │   ├── jobs/          # Background tasks
│   │   └── policies/      # Authorization
│   ├── api/
│   │   ├── http/          # API routes
│   │   └── middleware/    # Middleware
│   ├── seeds/             # Database seeders
│   └── tests/
│       └── factories/     # Test factories
├── apps/
│   ├── web/               # Next.js main app
│   ├── admin/             # Admin panel
│   └── landing/           # Landing page (Astro)
├── docs/                  # Documentation
├── docker-compose.yml
└── .lich                  # Project marker
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    LICH CLI CHEAT SHEET                     │
├─────────────────────────────────────────────────────────────┤
│ lich init                 Create new project                │
│ lich make entity User     Entity + Port + Adapter           │
│ lich make service User    Service class                     │
│ lich make api users       FastAPI CRUD router               │
│ lich make dto User        Pydantic schemas                  │
│ lich make factory User    Test factory                      │
│ lich make event Name      Domain event                      │
│ lich make listener Name   Event handler                     │
│ lich make job Name        Background job                    │
│ lich make policy Name     Authorization                     │
│ lich make middleware Name Request interceptor               │
│ lich migration up         Apply DB migrations               │
│ lich migration down       Rollback migrations               │
│ lich routes               List API endpoints                │
│ lich test                 Run tests                         │
│ lich seed                 Seed database                     │
│ lich shell                Python REPL                       │
└─────────────────────────────────────────────────────────────┘
```

---

**Lich Framework v1.3.0**

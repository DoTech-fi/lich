# Architecture Overview

Lich generates projects following **Clean Architecture** principles.

## Project Structure

```
your-project/
├── .lich/                         # Lich configuration
│   ├── config.yml                 # Project settings
│   └── rules/                     # Architecture rules for AI & humans
│
├── backend/                       # Python FastAPI backend
│   ├── api/
│   │   ├── http/                  # FastAPI routers (controllers)
│   │   │   ├── __init__.py        # Router registration
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User CRUD endpoints
│   │   │   └── health.py          # Health check endpoint
│   │   └── middleware/            # HTTP middlewares
│   │       ├── auth.py            # JWT validation
│   │       ├── cors.py            # CORS configuration
│   │       └── rate_limit.py      # Rate limiting
│   │
│   ├── internal/
│   │   ├── entities/              # Domain models (pure Python)
│   │   │   ├── user.py            # User entity
│   │   │   └── base.py            # Base entity class
│   │   │
│   │   ├── services/              # Business logic (use cases)
│   │   │   ├── user_service.py    # User operations
│   │   │   └── auth_service.py    # Auth operations
│   │   │
│   │   ├── ports/                 # Interfaces (abstractions)
│   │   │   ├── repositories/      # Repository interfaces
│   │   │   │   └── user_repo.py
│   │   │   └── external/          # External service interfaces
│   │   │       └── email_port.py
│   │   │
│   │   ├── adapters/              # Implementations
│   │   │   ├── repositories/      # Database implementations
│   │   │   │   └── postgres/
│   │   │   │       └── user_repo.py
│   │   │   ├── cache/             # Redis cache adapter
│   │   │   └── external/          # External API clients
│   │   │       └── smtp_adapter.py
│   │   │
│   │   ├── dto/                   # Data Transfer Objects
│   │   │   ├── requests/          # Request schemas
│   │   │   └── responses/         # Response schemas
│   │   │
│   │   ├── events/                # Domain events
│   │   │   └── user_events.py
│   │   │
│   │   ├── listeners/             # Event handlers
│   │   │   └── user_listeners.py
│   │   │
│   │   ├── jobs/                  # Background jobs (Celery/ARQ)
│   │   │   └── email_job.py
│   │   │
│   │   └── policies/              # Authorization policies
│   │       └── user_policy.py
│   │
│   ├── validators/                # Input validation schemas
│   │   └── user_validator.py
│   │
│   ├── alembic/                   # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                     # Backend tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration loader
│   └── requirements.txt           # Python dependencies
│
├── apps/                          # Frontend applications
│   ├── web/                       # Main Next.js application
│   │   ├── src/
│   │   │   ├── app/               # App Router pages
│   │   │   ├── components/        # React components
│   │   │   ├── hooks/             # Custom hooks
│   │   │   ├── services/          # API client services
│   │   │   ├── stores/            # State management
│   │   │   ├── types/             # TypeScript types
│   │   │   └── utils/             # Utility functions
│   │   ├── public/                # Static assets
│   │   ├── tailwind.config.js
│   │   └── package.json
│   │
│   ├── admin/                     # Admin dashboard (Next.js)
│   │   ├── src/
│   │   │   ├── app/               # Admin pages
│   │   │   ├── components/        # Admin components
│   │   │   └── services/          # Admin API services
│   │   └── package.json
│   │
│   └── landing/                   # SEO landing page (Astro)
│       ├── src/
│       │   ├── pages/             # Static pages
│       │   ├── components/        # Astro components
│       │   └── content/           # MDX content
│       ├── public/                # Static assets
│       └── astro.config.mjs
│
├── deployments/                   # Infrastructure & deployment
│   ├── docker/
│   │   ├── Dockerfile.backend     # Backend container
│   │   ├── Dockerfile.web         # Web app container
│   │   ├── Dockerfile.admin       # Admin container
│   │   └── Dockerfile.landing     # Landing container
│   │
│   ├── ansible/                   # Deployment automation
│   │   ├── playbooks/
│   │   │   ├── deploy.yml         # Main deployment
│   │   │   ├── backup.yml         # Database backup
│   │   │   └── rollback.yml       # Rollback procedure
│   │   ├── inventory/
│   │   │   ├── staging.yml
│   │   │   └── production.yml
│   │   └── roles/
│   │       ├── docker/
│   │       ├── traefik/
│   │       └── postgres/
│   │
│   └── swarm/                     # Docker Swarm configs
│       ├── stack.yml              # Swarm stack definition
│       └── secrets/               # Secret templates
│
├── .github/                       # GitHub configuration
│   └── workflows/
│       ├── ci.yml                 # Continuous Integration
│       ├── cd-staging.yml         # Deploy to staging
│       └── cd-production.yml      # Deploy to production
│
├── docs/                          # Project documentation
│   ├── runbooks/                  # Operation runbooks
│   ├── features/                  # Feature documentation
│   ├── architecture/              # Architecture docs
│   └── onboarding/                # Developer onboarding
│
├── scripts/                       # Utility scripts
│   ├── setup.sh                   # Initial setup
│   └── seed.py                    # Database seeding
│
├── docker-compose.yml             # Local development
├── docker-compose.override.yml    # Local overrides
├── Makefile                       # Common commands
├── agentlog.md                    # AI change log
└── README.md                      # Project overview
```

## Layer Diagram

```
┌─────────────────────────────────────────┐
│              API Layer                   │
│         (FastAPI routers)               │
└───────────────┬─────────────────────────┘
                │ calls
┌───────────────▼─────────────────────────┐
│           Service Layer                  │
│       (Business logic/Use cases)        │
└───────────────┬─────────────────────────┘
                │ uses
┌───────────────▼─────────────────────────┐
│           Domain Layer                   │
│    (Entities + Ports/Interfaces)        │
└───────────────┬─────────────────────────┘
                │ implemented by
┌───────────────▼─────────────────────────┐
│          Adapter Layer                   │
│      (Database, Cache, External)        │
└─────────────────────────────────────────┘
```

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Dependency Inversion** | High-level modules don't depend on low-level |
| **Single Responsibility** | Each module has one reason to change |
| **Interface Segregation** | Many specific interfaces over general |
| **Pure Domain** | Entities have no framework dependencies |

## Learn More

- [Entities](entities.md)
- [Services](services.md)
- [Ports & Adapters](ports-adapters.md)
- [API Layer](api.md)

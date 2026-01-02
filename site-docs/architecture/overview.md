# Architecture Overview

Lich generates projects following **Clean Architecture** principles.

## Project Structure

```
your-project/
├── backend/
│   ├── api/
│   │   ├── http/           # FastAPI routers
│   │   └── middleware/     # HTTP middlewares
│   ├── internal/
│   │   ├── entities/       # Domain models
│   │   ├── services/       # Business logic
│   │   ├── ports/          # Interfaces
│   │   ├── adapters/       # Implementations
│   │   ├── dto/            # Request/Response types
│   │   ├── events/         # Event classes
│   │   ├── listeners/      # Event handlers
│   │   ├── jobs/           # Background jobs
│   │   └── policies/       # Authorization
│   └── main.py
├── frontend/               # Next.js app
└── docker-compose.yml
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

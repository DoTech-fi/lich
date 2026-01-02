# Backend Architecture Rules

> As a Backend Architect, follow Lich Architecture principles.

## Core Principles

```
🧱 CLEAN ARCHITECTURE
🔌 PORTS & ADAPTERS
✅ SOLID PRINCIPLES
🧪 TESTABLE BY DESIGN
```

---

## 1. Project Structure (Lich Architecture)

```
backend/
├── api/http/           # HTTP Controllers
├── internal/
│   ├── entities/       # Pure domain models (NO dependencies)
│   ├── services/       # Use cases & business logic
│   ├── ports/          # Interfaces (repositories, external)
│   ├── adapters/       # Implementations (DB, Redis, HTTP)
│   ├── dto/            # Request/Response shapes
│   └── validators/     # Input validation
├── pkg/
│   ├── config/         # Configuration
│   ├── logger/         # Logging setup
│   └── errors/         # Error types
└── tests/
```

---

## 2. Dependency Rules

```
entities     → NOTHING (pure domain)
services     → entities, ports, dto
ports        → entities only
adapters     → entities, ports, pkg
api/http     → services, dto, validators
```

**NEVER**: adapters → services, entities → anything

---

## 3. Entity Rules

### DO ✅
- Pure Python dataclasses
- Domain logic inside entity
- No ORM/DB types
- No external dependencies

### DON'T ❌
- No SQLAlchemy in entities
- No Pydantic BaseModel
- No HTTP types

---

## 4. Service Rules

### DO ✅
- One service = one use case area
- Inject dependencies via constructor
- Return domain entities
- Raise domain exceptions

### DON'T ❌
- No HTTP request/response
- No direct DB access
- No framework dependencies

---

## 5. API Rules

### DO ✅
- Validate input with Pydantic
- Transform to/from DTOs
- Handle errors gracefully
- Document with OpenAPI

### DON'T ❌
- No business logic in controllers
- No raw SQL in handlers

---

## 6. Testing

### DO ✅
- Unit tests for entities
- Mock ports in service tests
- Integration tests for adapters
- API tests with test client

---

> **Mantra**: Simple → Modular → Testable

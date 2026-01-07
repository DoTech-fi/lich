# Backend Architecture Rules

> **Lich Architecture - Clean Architecture for Python (FastAPI)**

---

## ⚡ Core Identity

You are a **Senior Backend Architect** specializing in Python/FastAPI using Lich Architecture.

When working on backend code:
- Apply SOLID principles
- Use Clean Code practices
- Follow Domain-Driven Design thinking
- Prioritize simplicity and maintainability

---

## 📁 Project Structure

```
backend/
├── api/
│   ├── http/               # FastAPI routers
│   └── middleware/         # Request interceptors
├── internal/
│   ├── entities/           # Pure domain models (NO deps!)
│   ├── services/           # Use cases & business logic
│   ├── ports/              # Interfaces (repositories)
│   ├── adapters/           # Implementations (DB, Redis)
│   ├── dto/                # Request/Response shapes
│   ├── validators/         # Input validation
│   ├── events/             # Domain events
│   ├── listeners/          # Event handlers
│   ├── jobs/               # Background jobs
│   ├── workers/            # Temporal/Celery workers
│   └── policies/           # Authorization
├── pkg/
│   ├── config/             # Configuration
│   ├── logger/             # Logging
│   └── errors/             # Error types
├── seeds/                  # Seeders
└── tests/
    └── factories/          # Test factories
```

---

## 🔗 Dependency Rules (STRICT!)

```
entities     → NOTHING (pure domain, no imports)
services     → entities, ports, dto, validators
ports        → entities ONLY (interfaces)
adapters     → entities, ports, pkg
api/http     → services, dto, validators
```

**NEVER:**
- adapters → services
- entities → anything
- services → adapters directly

---

## 📦 Layer Rules

### Entities (internal/entities/)

**DO ✅:**
- Pure Python dataclasses
- Domain logic inside entity
- Domain validation rules
- Business invariants

**DON'T ❌:**
- No SQLAlchemy
- No Pydantic BaseModel
- No HTTP types
- No external imports

```python
# GOOD
@dataclass
class Payment:
    id: UUID
    amount: Decimal
    status: PaymentStatus
    
    def can_refund(self) -> bool:
        return self.status == PaymentStatus.COMPLETED

# BAD - Don't do this!
class Payment(Base):  # ❌ SQLAlchemy
    ...
```

---

### Services (internal/services/)

**DO ✅:**
- One service = one domain area
- Inject dependencies via constructor
- Return domain entities
- Raise domain exceptions
- All business decisions here

**DON'T ❌:**
- No HTTP request/response
- No direct DB access
- No framework dependencies

```python
# GOOD
class PaymentService:
    def __init__(self, payment_repo: PaymentPort):
        self._repo = payment_repo
    
    async def process_payment(self, dto: CreatePaymentDTO) -> Payment:
        # Business logic here
        payment = Payment.create(dto.amount, dto.currency)
        await self._repo.save(payment)
        return payment
```

---

### Ports (internal/ports/)

**DO ✅:**
- Define interfaces only
- One port = one capability
- Small, focused interfaces

**DON'T ❌:**
- No implementation code
- No god-repositories

```python
# GOOD
class PaymentPort(Protocol):
    async def save(self, payment: Payment) -> None: ...
    async def find_by_id(self, id: UUID) -> Payment | None: ...
```

---

### Adapters (internal/adapters/)

**DO ✅:**
- Implement ports
- Map DB models ↔ entities
- Handle infrastructure concerns
- Retries, circuit breakers

**DON'T ❌:**
- No business logic
- No leaking DB types

---

### API/HTTP (api/http/)

**DO ✅:**
- Validate with Pydantic DTOs
- Transform to/from DTOs
- Handle errors → HTTP responses
- OpenAPI documentation

**DON'T ❌:**
- No business logic
- No raw SQL

---

## 🔒 Security Rules

- All input validated in validators/dto
- No tokens in logs
- Secrets from .env only
- Rate limiting in API layer
- Auth checks before service calls

---

## 🧪 Testing

- **Unit**: entities, services (mock ports)
- **Integration**: adapters (real DB)
- **API**: routers (test client)
- Use `lich make factory <Name>` for test data

---

## 🔧 CLI Commands

```bash
lich make entity <Name>      # Entity + Port + Adapter
lich make service <Name>     # Service class
lich make api <name>         # FastAPI router
lich make dto <Name>         # Pydantic DTOs
lich make factory <Name>     # Test factory
lich migration create "desc" # Create migration
lich migration up            # Apply migrations
lich test -c                 # Tests with coverage
```

---

**Mantra: Simple → Modular → Testable → Secure**

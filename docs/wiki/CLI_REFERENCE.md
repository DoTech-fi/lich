# 🧙 Lich CLI - Complete Command Reference

> **Version: 1.3.0** | For Juniors & Seniors Alike

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Project Commands](#project-commands)
3. [Code Generators (make)](#code-generators-make)
4. [Database Commands (migration)](#database-commands-migration)
5. [Development Commands](#development-commands)
6. [Real-World Scenarios](#real-world-scenarios)

---

## Quick Start

```bash
# Install Lich CLI
pip install lich-cli

# Create new project
lich init

# Navigate to project
cd my-project

# Start development
lich dev

# Generate code
lich make entity User
lich make service UserService
lich make api users
```

---

## Project Commands

### `lich init`
Create a new Lich project.

```bash
lich init                    # Interactive mode
lich init --name my-project  # With name
lich init --no-input         # Use defaults
```

**Questions asked:**
- Project name
- Project type (saas_platform, trading_platform, etc.)
- Database (postgresql, mongodb)
- Auth strategy (jwt_builtin, keycloak, auth_proxy, none)
- Redis? (yes/no)
- Microservice? (yes/no)
- Admin panel? (yes/no)

---

### `lich adopt`
Import an existing Python project into Lich architecture.

```bash
lich adopt /path/to/existing/project         # Analyze and create
lich adopt /path/to/project --dry-run        # Only analyze, don't create
lich adopt /path/to/project --output ./new   # Output to different folder
```

**Use case:** You have an old FastAPI project and want to refactor it to Lich architecture.

---

### `lich version`
Show current version and available versions.

```bash
lich version             # Show version + available versions table
lich version --history   # Show full changelog
```

---

### `lich upgrade`
Upgrade project to a newer Lich version.

```bash
lich upgrade               # Interactive - pick version
lich upgrade --to 1.3.0    # Upgrade to specific version
lich upgrade --dry-run     # Preview changes without applying
```

---

### `lich check`
Validate project structure.

```bash
lich check   # Check if project follows Lich architecture
```

---

## Code Generators (make)

> All `make` commands generate production-ready code following Lich Architecture.

### `lich make entity <Name>`
Generate a domain entity with port (interface) and adapter (repository).

```bash
lich make entity User
lich make entity Product --force  # Overwrite existing
```

**Creates:**
- `backend/internal/entities/user.py` - Domain model
- `backend/internal/ports/user_port.py` - Repository interface
- `backend/internal/adapters/db/user_repo.py` - Database implementation

**Generated entity:**
```python
@dataclass
class User:
    id: UUID
    created_at: datetime
    # Add your fields here
    
    @classmethod
    def create(cls, **kwargs) -> "User":
        return cls(id=uuid4(), created_at=datetime.utcnow(), **kwargs)
```

---

### `lich make service <Name>`
Generate a service (use case) class.

```bash
lich make service UserService
lich make service OrderService
```

**Creates:** `backend/internal/services/user_service.py`

**Generated service:**
```python
class UserService:
    def __init__(self, repository):
        self.repo = repository
    
    async def get_by_id(self, id: UUID):
        return await self.repo.get_by_id(id)
    
    async def create(self, **data):
        # Business logic here
        pass
```

---

### `lich make api <Name>`
Generate FastAPI router with CRUD endpoints.

```bash
lich make api users
lich make api products
```

**Creates:** `backend/api/http/users.py`

**Generated endpoints:**
- `GET /users/` - List all
- `GET /users/{id}` - Get by ID
- `POST /users/` - Create
- `PUT /users/{id}` - Update
- `DELETE /users/{id}` - Delete

---

### `lich make dto <Name>`
Generate Pydantic DTOs (Data Transfer Objects).

```bash
lich make dto User
lich make dto Product
```

**Creates:** `backend/internal/dto/user_dto.py`

**Generated DTOs:**
```python
class UserCreate(BaseModel):
    name: str

class UserUpdate(BaseModel):
    name: Optional[str]

class UserResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
```

---

### `lich make factory <Name>`
Generate test factory using Faker.

```bash
lich make factory User
lich make factory Product
```

**Creates:** `backend/tests/factories/user_factory.py`

**Usage in tests:**
```python
from tests.factories.user_factory import UserFactory

user = UserFactory.make()
users = UserFactory.make_many(10)
user_with_email = UserFactory.make(email="test@test.com")
```

---

### `lich make middleware <Name>`
Generate FastAPI middleware.

```bash
lich make middleware RateLimit
lich make middleware Auth
lich make middleware Logging
```

**Creates:** `backend/api/middleware/ratelimit_middleware.py`

**Usage in main.py:**
```python
from api.middleware.ratelimit_middleware import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)
```

---

### `lich make event <Name>`
Generate a domain event class.

```bash
lich make event UserRegistered
lich make event OrderPlaced
lich make event PaymentReceived
```

**Creates:** `backend/internal/events/userregistered.py`

**Generated event:**
```python
@dataclass
class UserRegistered:
    user_id: UUID
    email: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

---

### `lich make listener <Name>`
Generate an event listener.

```bash
lich make listener SendWelcomeEmail --event UserRegistered
lich make listener NotifyAdmin
```

**Creates:** `backend/internal/listeners/sendwelcomeemail.py`

**Generated listener:**
```python
class SendWelcomeEmail:
    async def handle(self, event: UserRegistered) -> None:
        await self.email_service.send_welcome(event.email)
```

---

### `lich make job <Name>`
Generate a background job (Celery or Temporal).

```bash
lich make job SendInvoice                  # Asks for queue type
lich make job SendInvoice --queue celery   # Celery task
lich make job ProcessOrder --queue temporal # Temporal workflow
```

**Celery job:**
```python
@shared_task(bind=True, max_retries=3)
def send_invoice_job(self, data: dict):
    # Job logic
    return {"status": "completed"}
```

**Temporal workflow:**
```python
@workflow.defn
class SendInvoiceWorkflow:
    @workflow.run
    async def run(self, data: dict):
        result = await workflow.execute_activity(send_invoice_activity, data)
        return result
```

---

### `lich make policy <Name>`
Generate authorization policy.

```bash
lich make policy Post
lich make policy Comment
```

**Creates:** `backend/internal/policies/post_policy.py`

**Generated policy:**
```python
class PostPolicy:
    def can_view(self, user, post) -> bool:
        return True  # Public
    
    def can_edit(self, user, post) -> bool:
        return user.id == post.owner_id or user.is_admin
    
    def can_delete(self, user, post) -> bool:
        return self.can_edit(user, post)
```

**Usage:**
```python
if PostPolicy().can_edit(current_user, post):
    # Allow edit
```

---

## Database Commands (migration)

> Wrapper around Alembic for database migrations.

### `lich migration init`
Initialize Alembic in the project.

```bash
lich migration init
```

**Creates:** `backend/alembic/` folder with configuration.

---

### `lich migration create <message>`
Create a new migration.

```bash
lich migration create "add users table"
lich migration create "add email to users" --autogenerate
```

---

### `lich migration up [revision]`
Apply migrations.

```bash
lich migration up         # Apply all pending
lich migration up head    # Same as above
lich migration up abc123  # Up to specific revision
```

---

### `lich migration down [revision]`
Rollback migrations.

```bash
lich migration down       # Rollback one step
lich migration down -1    # Same as above
lich migration down base  # Rollback all
```

---

### `lich migration status`
Show current migration status.

```bash
lich migration status
```

---

## Development Commands

### `lich dev`
Start all development services.

```bash
lich dev   # Starts Docker, backend, frontend, etc.
```

---

### `lich stop`
Stop all development services.

```bash
lich stop
```

---

### `lich shell`
Interactive Python REPL with project context.

```bash
lich shell
>>> from internal.entities.user import User
>>> user = User.create(email="test@test.com")
```

---

### `lich routes`
List all API routes.

```bash
lich routes
```

**Output:**
```
┌────────┬─────────────────────┬──────────────┬───────────┐
│ Method │ Path                │ Function     │ File      │
├────────┼─────────────────────┼──────────────┼───────────┤
│ GET    │ /api/v1/users/      │ list_users   │ users.py  │
│ POST   │ /api/v1/users/      │ create_user  │ users.py  │
│ DELETE │ /api/v1/users/{id}  │ delete_user  │ users.py  │
└────────┴─────────────────────┴──────────────┴───────────┘
```

---

### `lich test`
Run tests with pytest.

```bash
lich test                    # All tests
lich test --unit             # Unit tests only
lich test --integration      # Integration tests only
lich test --coverage         # With coverage report
lich test --watch            # Watch mode (re-run on changes)
lich test backend/tests/     # Specific path
```

---

### `lich seed`
Seed database with test data.

```bash
lich seed              # Run all seeders
lich seed users        # Run specific seeder
lich seed --fresh      # Re-migrate and seed
lich seed --list       # List available seeders
```

---

## Real-World Scenarios

### Scenario 1: New User Registration Flow

```bash
# 1. Create the entity
lich make entity User

# 2. Create the service
lich make service UserService

# 3. Create the API
lich make api users

# 4. Create DTOs
lich make dto User

# 5. Create the event
lich make event UserRegistered

# 6. Create listeners
lich make listener SendWelcomeEmail --event UserRegistered
lich make listener CreateDefaultSettings --event UserRegistered

# 7. Create migration
lich migration create "add users table"
lich migration up
```

---

### Scenario 2: E-commerce Order Processing

```bash
# Entities & Services
lich make entity Order
lich make entity OrderItem
lich make service OrderService

# API
lich make api orders

# Events
lich make event OrderPlaced
lich make event PaymentReceived
lich make event OrderShipped

# Listeners
lich make listener SendOrderConfirmation --event OrderPlaced
lich make listener NotifyWarehouse --event PaymentReceived
lich make listener SendShippingNotification --event OrderShipped

# Background Jobs
lich make job GenerateInvoice --queue celery
lich make job SyncWithERP --queue temporal

# Authorization
lich make policy Order
```

---

### Scenario 3: Adding Authentication Middleware

```bash
# Create middleware
lich make middleware JWTAuth

# Edit the middleware
vim backend/api/middleware/jwtauth_middleware.py

# Register in main.py
app.add_middleware(JWTAuthMiddleware)
```

---

### Scenario 4: Testing with Factories

```bash
# Create factories
lich make factory User
lich make factory Product
lich make factory Order

# In your test file:
```

```python
from tests.factories.user_factory import UserFactory
from tests.factories.order_factory import OrderFactory

def test_user_can_place_order():
    user = UserFactory.make()
    order = OrderFactory.make(user_id=user.id)
    
    assert order.user_id == user.id
```

---

## 🎓 For Juniors: Key Concepts

### What is an Entity?
Domain model - pure Python, no database code.

### What is a Service?
Business logic - coordinates entities and ports.

### What is a Port?
Interface (abstract class) - defines what repository should do.

### What is an Adapter?
Implementation - actual database/Redis/HTTP code.

### What is a DTO?
Data Transfer Object - what API receives/sends.

### What is an Event?
Something that happened - `UserRegistered`, `OrderPlaced`.

### What is a Listener?
Reacts to events - send email, create records, etc.

### What is a Policy?
Authorization rules - who can do what.

---

## 🔄 Workflow Diagram

```
User Request
     │
     ▼
┌─────────────┐
│   API       │  ← DTO validation
│  (Router)   │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Service    │  ← Business logic
│ (Use Case)  │  ← Fires Events
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Port      │  ← Interface
│ (Interface) │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Adapter    │  ← Database/Redis
│  (Repo)     │
└─────────────┘
```

---

**Happy coding with Lich! 🧙**

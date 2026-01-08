# Lich CLI - Code Generation Rules

> Use Lich CLI to generate production-ready code quickly.

## CLI Commands Reference (v1.3.0)

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

## Common Workflows

### Adding a New Feature
```bash
lich make entity Feature
lich make service FeatureService
lich make api features
lich make dto Feature
lich migration create "add features table"
lich migration up
```

### Adding Event-Driven Flow
```bash
lich make event SomethingHappened
lich make listener DoSomething --event SomethingHappened
```

### Adding Background Jobs
```bash
lich make job SendEmail --queue celery     # Simple task
lich make job ProcessOrder --queue temporal # Complex workflow
```

### Adding Authorization
```bash
lich make policy Resource
```

---

> **Mantra**: Generate → Customize → Ship

---

## 🤖 MCP Tools

If you are an AI agents with access to the `lich` MCP server, you can use these tools directly instead of running CLI commands via shell:

| CLI Command | MCP Tool |
|-------------|----------|
| `lich check` | `mcp_lich_lich_check_project` |
| `lich version` | `mcp_lich_lich_version` |
| `lich start` | `mcp_lich_lich_dev_start` |
| `lich stop` | `mcp_lich_lich_dev_stop` |
| `lich make entity` | `mcp_lich_lich_make_entity` |
| `lich make service` | `mcp_lich_lich_make_service` |
| `lich make api` | `mcp_lich_lich_make_api` |
| `lich make dto` | `mcp_lich_lich_make_dto` |
| `lich make job` | `mcp_lich_lich_make_job` |
| `lich make middleware` | `mcp_lich_lich_make_middleware` |
| `lich make factory` | `mcp_lich_lich_make_factory` |
| `lich make event` | `mcp_lich_lich_make_event` |
| `lich make listener` | `mcp_lich_lich_make_listener` |
| `lich make policy` | `mcp_lich_lich_make_policy` |
| `lich migration init` | `mcp_lich_lich_migration_init` |
| `lich migration create` | `mcp_lich_lich_migration_create` |
| `lich migration up` | `mcp_lich_lich_migration_up` |
| `lich migration down` | `mcp_lich_lich_migration_down` |
| `lich migration heads` | `mcp_lich_lich_migration_heads` |
| `lich migration status` | `mcp_lich_lich_migration_status` |
| `lich seed` | `mcp_lich_lich_seed` |
| `lich backup` | `mcp_lich_lich_backup` |
| `lich test` | `mcp_lich_lich_test` |
| `lich lint` | `mcp_lich_lich_lint_backend` / `_frontend` |
| `lich security` | `mcp_lich_lich_security_scan` |
| `lich ci` | `mcp_lich_lich_ci_all` |
| `lich production-ready` | `mcp_lich_lich_production_ready_check` |
| `lich deploy` | `mcp_lich_lich_deploy` |
| `lich routes` | `mcp_lich_lich_routes` |
| `lich secret generate` | `mcp_lich_lich_secret_generate` |
| `lich secret rotate` | `mcp_lich_lich_secret_rotate` |

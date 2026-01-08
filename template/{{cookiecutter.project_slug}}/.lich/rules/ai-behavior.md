# 🤖 AI Behavior Rules (Lich-First Enforcement)

> **THIS FILE IS MANDATORY READING FOR ALL AI AGENTS.**  
> Before doing ANYTHING in this project, follow the decision logic below.

---

## 🚨 LICH-FIRST DECISION FLOWCHART

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHEN YOU RECEIVE ANY TASK:                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: Is this a Lich project?                                        │
│          ├── Check: Does `.lich/` folder exist?                         │
│          ├── Check: Does `AGENTS.md` reference Lich?                    │
│          │                                                              │
│          ├── YES → Continue to STEP 2                                   │
│          └── NO  → Use your own approach (Lich not applicable)         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 2: Does a Lich CLI command exist for this task?                   │
│          ├── Check the TASK-TO-COMMAND table below                      │
│          │                                                              │
│          ├── YES → ⚠️  YOU MUST USE THE LICH COMMAND                    │
│          │         Do NOT write files manually!                         │
│          │         Do NOT run raw shell commands!                       │
│          │                                                              │
│          └── NO  → Continue to STEP 3                                   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 3: Do Lich MCP tools exist for this task?                         │
│          ├── Check if you have access to `mcp_lich_*` tools             │
│          │                                                              │
│          ├── YES → Use MCP tools (they call Lich CLI under the hood)    │
│          └── NO  → NOW you may use manual coding approach               │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 4 (ALWAYS): Update `agentlog.md`                                  │
│          └── After EVERY change, append: WHAT, WHY, WHEN                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 TASK-TO-COMMAND MAPPING

Use this table to find the correct Lich command for your task:

### Code Generation

| Task | Lich Command | MCP Tool |
|------|--------------|----------|
| Create new Entity | `lich make entity <name>` | `mcp_lich_lich_make_entity` |
| Create new Service | `lich make service <name>` | `mcp_lich_lich_make_service` |
| Create new API | `lich make api <name>` | `mcp_lich_lich_make_api` |
| Create new DTO | `lich make dto <name>` | `mcp_lich_lich_make_dto` |
| Create Background Job | `lich make job <name>` | `mcp_lich_lich_make_job` |
| Create Middleware | `lich make middleware <name>` | `mcp_lich_lich_make_middleware` |
| Create Event | `lich make event <name>` | `mcp_lich_lich_make_event` |
| Create Listener | `lich make listener <name>` | `mcp_lich_lich_make_listener` |
| Create Policy | `lich make policy <name>` | `mcp_lich_lich_make_policy` |
| Create Test Factory | `lich make factory <name>` | `mcp_lich_lich_make_factory` |

### Database

| Task | Lich Command | MCP Tool |
|------|--------------|----------|
| Initialize migrations | `lich migration init` | `mcp_lich_lich_migration_init` |
| Create migration | `lich migration create "msg"` | `mcp_lich_lich_migration_create` |
| Apply migrations | `lich migration up` | `mcp_lich_lich_migration_up` |
| Rollback migrations | `lich migration down` | `mcp_lich_lich_migration_down` |
| Check migration status | `lich migration status` | `mcp_lich_lich_migration_status` |
| Seed database | `lich seed` | `mcp_lich_lich_seed` |
| Backup database | `lich backup` | `mcp_lich_lich_backup` |

### Quality & Testing

| Task | Lich Command | MCP Tool |
|------|--------------|----------|
| Run tests | `lich test` | `mcp_lich_lich_test` |
| Run backend linter | `lich lint` | `mcp_lich_lich_lint_backend` |
| Run frontend linter | `lich lint --frontend` | `mcp_lich_lich_lint_frontend` |
| Run security scan | `lich security` | `mcp_lich_lich_security_scan` |
| Full CI pipeline | `lich ci` | `mcp_lich_lich_ci_all` |

### Development

| Task | Lich Command | MCP Tool |
|------|--------------|----------|
| Start dev environment | `lich start` | `mcp_lich_lich_dev_start` |
| Stop dev environment | `lich stop` | `mcp_lich_lich_dev_stop` |
| Check project structure | `lich check` | `mcp_lich_lich_check_project` |
| List all routes | `lich routes` | `mcp_lich_lich_routes` |
| Show version | `lich version` | `mcp_lich_lich_version` |

### Deployment

| Task | Lich Command | MCP Tool |
|------|--------------|----------|
| Deploy | `lich deploy` | `mcp_lich_lich_deploy` |
| Production check | `lich production-ready` | `mcp_lich_lich_production_ready_check` |
| Generate secrets | `lich secret generate` | `mcp_lich_lich_secret_generate` |
| Rotate secrets | `lich secret rotate` | `mcp_lich_lich_secret_rotate` |

---

## ⚠️ FORBIDDEN ACTIONS

You are **FORBIDDEN** from doing the following when a Lich command exists:

| Forbidden ❌ | Correct ✅ |
|--------------|-----------|
| `write_to_file("entities/payment.py", ...)` | `lich make entity payment` |
| `write_to_file("services/user_service.py", ...)` | `lich make service user` |
| `run_command("alembic revision -m ...")` | `lich migration create "..."` |
| `run_command("alembic upgrade head")` | `lich migration up` |
| `run_command("pytest")` | `lich test` |
| `run_command("ruff check .")` | `lich lint` |
| `run_command("bandit -r .")` | `lich security` |
| `run_command("docker-compose up")` | `lich start` |
| `run_command("./dev-start.sh")` | `lich start` |

---

## ✅ WHEN MANUAL CODING IS ALLOWED

You MAY use manual coding (`write_to_file`, `replace_file_content`) for:

1. **Customizing generated files** - After `lich make entity X`, you may edit the generated files
2. **Frontend components** - No Lich generator for React/Next.js components yet
3. **Configuration files** - `.env`, `docker-compose.yml` tweaks
4. **Documentation** - README, docs/, etc.
5. **Tests** - Adding test cases to generated test files
6. **Bug fixes** - Editing existing code to fix issues

---

## 🔄 MCP TOOLS PRIORITY

If you have access to Lich MCP tools (`mcp_lich_*`), **prefer them over CLI commands**:

```
MCP Tool Available?
├── YES → Use MCP tool (faster, no shell overhead)
└── NO  → Fall back to CLI command via run_command
```

MCP tools provide the same functionality as CLI commands but are optimized for AI agent use.

---

## 📝 AGENTLOG UPDATE (MANDATORY)

After **EVERY** change, append to `agentlog.md`:

```markdown
## 2026-01-08 - [Brief Title]
- **What**: [What you changed]
- **Why**: [Why you made this change]
- **Commands used**: [Lich commands you used]
```

**This is not optional.** If you forget, your output is invalid.

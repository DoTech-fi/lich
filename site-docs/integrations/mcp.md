# 🤖 Lich MCP Integration

!!! success "47 MCP Tools - Full Control for AI Assistants"

Lich MCP (Model Context Protocol) enables AI coding assistants to directly interact with your Lich project - generating code, running tests, deploying, and more.

---

## 🎯 Quick Setup

### 1. Install Lich CLI

```bash
pip install lich
```

### 2. Configure Your AI Tool

=== "Antigravity (Google)"

    **Recommended:** Run `lich setup antigravity` to automatically configure.

    **Manual Configuration:**
    Create/Edit `~/.gemini/antigravity/mcp_config.json`:

    ```json
    {
      "mcpServers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

=== "Claude Desktop"

    Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

    ```json
    {
      "mcpServers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

    Then restart Claude Desktop.

=== "Cursor"

    Add to Cursor settings:

    ```json
    {
      "mcp.servers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

=== "VS Code + Continue"

    Add to `.continue/config.json`:

    ```json
    {
      "mcpServers": [
        {
          "name": "lich",
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      ]
    }
    ```

---

## 🛠️ Available Tools (47 Total)

### Project Management

| Tool | Description |
|------|-------------|
| `lich_init` | Create a new Lich project |
| `lich_check_project` | Validate project structure |
| `lich_version` | Show Lich version |
| `lich_upgrade` | Upgrade project to latest |
| `lich_adopt` | Adopt existing Python project |

### Code Generation (10 tools)

| Tool | Description |
|------|-------------|
| `lich_make_entity` | Create domain entity |
| `lich_make_service` | Create service (use case) |
| `lich_make_api` | Create API controller |
| `lich_make_dto` | Create DTO |
| `lich_make_factory` | Create test factory |
| `lich_make_middleware` | Create middleware |
| `lich_make_event` | Create domain event |
| `lich_make_listener` | Create event listener |
| `lich_make_job` | Create background job |
| `lich_make_policy` | Create authorization policy |

### Database Operations

| Tool | Description |
|------|-------------|
| `lich_migration_init` | Initialize Alembic |
| `lich_migration_create` | Create new migration |
| `lich_migration_up` | Apply migrations |
| `lich_migration_down` | Rollback migrations |
| `lich_migration_status` | Show migration status |
| `lich_migration_heads` | Show migration heads |
| `lich_seed` | Seed database |
| `lich_seed_list` | List available seeders |
| `lich_routes` | List all API routes |

### Git Workflow

| Tool | Description |
|------|-------------|
| `lich_git_commit` | Create semantic commit |
| `lich_git_tag` | Create version tag |
| `lich_git_push` | Push to remote |

### Quality Assurance

| Tool | Description |
|------|-------------|
| `lich_lint_backend` | Run Python linter (Ruff) |
| `lich_lint_frontend` | Run ESLint |
| `lich_test` | Run pytest |
| `lich_security_scan` | Run security scans |
| `lich_ci_all` | Run all CI checks |
| `lich_ci_backend` | Run backend CI |
| `lich_ci_web` | Run web app CI |
| `lich_ci_admin` | Run admin CI |
| `lich_production_ready_check` | Check production readiness |
| `lich_production_ready_fix` | Auto-fix issues |

### Secret Management

| Tool | Description |
|------|-------------|
| `lich_secret_generate` | Generate secure secrets |
| `lich_secret_rotate` | Rotate existing secrets |
| `lich_secret_check` | Check secret strength |

### Middleware Management

| Tool | Description |
|------|-------------|
| `lich_middleware_list` | List all middlewares |
| `lich_middleware_enable` | Enable a middleware |
| `lich_middleware_disable` | Disable a middleware |

### Development Environment

| Tool | Description |
|------|-------------|
| `lich_dev_start` | Start dev environment |
| `lich_dev_stop` | Stop dev environment |

### Deployment

| Tool | Description |
|------|-------------|
| `lich_deploy` | Deploy via Ansible |
| `lich_backup` | Database backup operations |

---

## 💬 Example Conversations

### Creating a New Feature

!!! example "You → AI"
    "Create a new Product entity with name, price, and stock fields, then create a ProductService and API endpoint."

The AI will use:

1. `lich_make_entity` → Creates `Product` entity
2. `lich_make_service` → Creates `ProductService`
3. `lich_make_api` → Creates Product API controller
4. `lich_make_dto` → Creates request/response DTOs
5. `lich_migration_create` → Creates database migration

### Deploying to Production

!!! example "You → AI"
    "Check if the project is production-ready, fix any issues, then deploy to staging."

The AI will use:

1. `lich_production_ready_check` → Scans for issues
2. `lich_production_ready_fix` → Auto-fixes problems
3. `lich_secret_check` → Validates secrets
4. `lich_ci_all` → Runs all quality checks
5. `lich_deploy` → Deploys to staging

### Database Changes

!!! example "You → AI"
    "Add a new email_verified field to the User entity and update the database."

The AI will use:

1. Edit the entity file
2. `lich_migration_create` → Creates migration
3. `lich_migration_up` → Applies migration
4. `lich_migration_status` → Verifies success

---

## 🔒 Security Notes

!!! warning "Production Deployments"
    
    By default, deployment tools run in `dry_run` mode. The AI must explicitly set `dry_run=False` for real deployments.

!!! tip "Secret Rotation"
    
    Secret rotation also defaults to `dry_run=True`. Always review proposed changes before applying.

---

## 🧪 Testing Your Setup

After configuring MCP, ask your AI:

> "What Lich tools are available?"

The AI should list all 47 tools with descriptions.

Then try:

> "Check if this is a valid Lich project"

The AI should use `lich_check_project` and report the result.

---

## 🐛 Troubleshooting

### "lich command not found"

Make sure Lich is installed and in your PATH:

```bash
pip install lich
which lich  # Should show the path
```

### "Not a Lich project"

Most tools require being in a Lich project directory. Either:

1. Set the correct `cwd` in your MCP config
2. Navigate to a Lich project before using tools

### MCP Server Won't Start

Check if the server starts manually:

```bash
cd /path/to/your/project
lich serve
```

You should see: `🤖 Lich MCP Server Starting...`

---

## 📚 Learn More

- [All CLI Commands](../commands/overview.md)
- [Architecture Guide](../architecture/overview.md)
- [Best Practices](../best-practices/ai.md)

# Commands Overview

Lich CLI provides commands for project management, code generation, and development.

## Command Categories

### 🚀 Project Management

| Command | Description |
|---------|-------------|
| [`lich init`](init.md) | Create a new Lich project |
| [`lich dev`](dev.md) | Start development servers |
| `lich stop` | Stop development servers |
| [`lich shell`](shell.md) | Open interactive Python shell |

### 🛠️ Code Generation

| Command | Description |
|---------|-------------|
| [`lich make entity`](make/entity.md) | Create domain entity |
| [`lich make service`](make/service.md) | Create service layer |
| [`lich make api`](make/api.md) | Create API router |
| [`lich make dto`](make/dto.md) | Create data transfer objects |
| [`lich make factory`](make/factory.md) | Create test factory |
| [`lich make middleware`](make/middleware.md) | Create middleware |
| [`lich make event`](make/event.md) | Create event class |
| [`lich make listener`](make/listener.md) | Create event listener |
| [`lich make job`](make/job.md) | Create background job |
| [`lich make policy`](make/policy.md) | Create authorization policy |

### 🗃️ Database

| Command | Description |
|---------|-------------|
| [`lich migration`](migration.md) | Database migration commands |
| [`lich seed`](seed.md) | Database seeding |

### 🔧 Utilities

| Command | Description |
|---------|-------------|
| [`lich middleware`](middleware.md) | Enable/disable middlewares |
| [`lich routes`](routes.md) | List all API routes |
| [`lich test`](test.md) | Run tests |
| `lich version` | Show version info |

## Getting Help

All commands support `--help`:

```bash
lich --help                  # Main help
lich make --help             # Make commands help
lich migration --help        # Migration help
```

## Command Context

Most commands require being in a Lich project directory (has `.lich/` folder):

```bash
cd your-lich-project
lich make entity User     # ✅ Works

cd /some/other/folder
lich make entity User     # ❌ Not a Lich project!
```

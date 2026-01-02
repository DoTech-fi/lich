# lich init

Create a new Lich Framework project with interactive prompts.

## Usage

```bash
lich init [OPTIONS]
```

## What It Does

1. Asks project configuration questions
2. Downloads the Lich project template
3. Generates a complete project structure
4. Sets up Docker, backend, and frontend

## Options

| Option | Description |
|--------|-------------|
| `--no-input` | Use all defaults, no prompts |
| `--help` | Show help |

## Interactive Prompts

When you run `lich init`, you'll be asked:

### Project Name
```
? Project name: my_awesome_app
```
Used for folder name and package names.

### Project Type
```
? Project type:
  > saas_platform
    trading_platform
    ai_application
```
Affects default configurations.

### Auth Strategy
```
? Auth strategy:
  > jwt_builtin    (Simple JWT auth built-in)
    keycloak       (Enterprise SSO)
    none           (No auth)
```

### Database
```
? Database:
  > postgresql
    mongodb
```

### Use Redis?
```
? Use Redis? [Y/n]: Y
```
For caching and sessions.

## Example

### Full Interactive

```bash
$ lich init

🧙 Lich Framework - Project Generator

? Project name: my_saas
? Project type: saas_platform
? Auth strategy: jwt_builtin
? Database: postgresql
? Use Redis? Yes

📦 Creating project 'my_saas'...
✅ Project created!

Next steps:
  cd my_saas
  lich dev
```

### Quick with Defaults

```bash
$ lich init --no-input

📦 Creating project with defaults...
✅ Project 'my_app' created!
```

## Generated Structure

After `lich init`, you'll have:

```
my_saas/
├── .lich/                 # Lich config & AI rules
├── backend/               # FastAPI application
│   ├── api/http/          # API routers
│   ├── internal/          # Business logic
│   └── main.py
├── frontend/              # Next.js application
├── docker-compose.yml     # Docker services
├── .env.example           # Environment template
└── README.md
```

## Best Use Cases

| Scenario | Command |
|----------|---------|
| New project with customization | `lich init` |
| Quick prototype | `lich init --no-input` |
| Team project with Keycloak | `lich init` → select keycloak |

## Common Issues

### Template Download Failed

If template download fails:

1. Check internet connection
2. Verify GitHub access
3. Try again: `lich init`

### Already in a Lich Project

If you get "Already in a Lich project" error:

```bash
cd ..
lich init
```

## See Also

- [`lich dev`](dev.md) - Start development after init
- [Quick Start Guide](../getting-started/quickstart.md)

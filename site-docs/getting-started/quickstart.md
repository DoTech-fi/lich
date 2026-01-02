# Quick Start

This guide will have you running a full-stack application in 5 minutes.

## 1. Create a New Project

```bash
lich init
```

You'll be prompted for:

| Prompt | Description | Default |
|--------|-------------|---------|
| Project name | Your application name | my_app |
| Project type | SaaS, Trading, etc. | saas_platform |
| Auth strategy | Keycloak, JWT, or none | jwt_builtin |
| Database | PostgreSQL or MongoDB | postgresql |
| Use Redis? | For caching | yes |

!!! tip "Quick Project"
    Use `lich init --no-input` to create a project with all defaults.

## 2. Navigate to Project

```bash
cd your-project-name
```

## 3. Start Development Servers

```bash
lich dev
```

This starts:

- 🐳 Docker containers (PostgreSQL, Redis)
- 🐍 FastAPI backend on http://localhost:8000
- ⚛️ Next.js frontend on http://localhost:3000

## 4. View Your Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

## 5. Stop Development

```bash
lich stop
```

Or press `Ctrl+C` in the terminal.

---

## What's Next?

### Generate Code

```bash
# Create a new entity
lich make entity Product

# Create a service
lich make service Product

# Create an API router
lich make api products
```

[:octicons-arrow-right-24: Learn about code generation](../commands/make/overview.md)

### Set Up Database

```bash
# Initialize migrations
lich migration init

# Create a migration
lich migration create "add products table"

# Apply migrations
lich migration up
```

[:octicons-arrow-right-24: Learn about migrations](../commands/migration.md)

### Run Tests

```bash
# Run all tests
lich test

# Run with coverage
lich test --coverage
```

[:octicons-arrow-right-24: Learn about testing](../commands/test.md)

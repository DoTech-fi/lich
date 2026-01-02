# 📚 Lich Framework Wiki

> **Documentation for Developers - Juniors to Seniors**

---

## 🚀 Quick Start
- [Getting Started](./GETTING_STARTED.md)
- [CLI Reference](./CLI_REFERENCE.md)

---

## 📖 Core Concepts

### Architecture
- [Lich Architecture Overview](./ARCHITECTURE.md)
- [Dependency Flow](./DEPENDENCY_FLOW.md)

### Code Generation
- [CLI Reference - All Commands](./CLI_REFERENCE.md)

---

## 🎯 Feature Guides

### Events & Listeners
- [Events & Listeners Guide](./EVENTS_LISTENERS.md)
  - Event چیست؟
  - Listener چیست؟
  - سناریوهای واقعی
  - Event Bus ساده

### Background Jobs
- [Background Jobs Guide](./BACKGROUND_JOBS.md)
  - Celery vs Temporal
  - کِی کدوم رو انتخاب کنیم؟
  - Setup و Configuration
  - Best Practices

### Authorization
- [Authorization Policies Guide](./AUTHORIZATION_POLICIES.md)
  - Policy چیست؟
  - RBAC
  - سناریوهای واقعی
  - تست نوشتن

---

## 🤖 AI Integration

- [AI Rules](../AI_RULES.md) - Rules for AI agents to understand Lich

---

## 📋 Reference

### Commands Quick Reference

```bash
# Project
lich init                    # New project
lich adopt <path>            # Import existing
lich version                 # Show version
lich upgrade                 # Upgrade version
lich check                   # Validate structure

# Development
lich dev                     # Start services
lich stop                    # Stop services
lich shell                   # Python REPL
lich routes                  # List routes
lich test                    # Run tests
lich seed                    # Seed database

# Code Generators
lich make entity <Name>      # Entity + Port + Adapter
lich make service <Name>     # Service class
lich make api <name>         # FastAPI router
lich make dto <Name>         # Pydantic DTOs
lich make factory <Name>     # Test factory
lich make middleware <Name>  # Middleware
lich make event <Name>       # Domain event
lich make listener <Name>    # Event listener
lich make job <Name>         # Background job
lich make policy <Name>      # Authorization policy

# Database
lich migration init          # Initialize Alembic
lich migration create "msg"  # Create migration
lich migration up            # Apply migrations
lich migration down          # Rollback
lich migration status        # Show status
```

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── internal/
│   │   ├── entities/        # Domain models
│   │   ├── services/        # Business logic
│   │   ├── ports/           # Interfaces
│   │   ├── adapters/        # Implementations
│   │   ├── dto/             # Pydantic schemas
│   │   ├── events/          # Domain events
│   │   ├── listeners/       # Event handlers
│   │   ├── jobs/            # Background tasks
│   │   └── policies/        # Authorization
│   ├── api/
│   │   ├── http/            # Routes
│   │   └── middleware/      # Middleware
│   ├── seeds/               # Seeders
│   └── tests/
│       └── factories/       # Test factories
├── apps/
│   ├── web/                 # Next.js main
│   ├── admin/               # Admin panel
│   └── landing/             # Astro landing
├── docs/                    # Documentation
└── docker-compose.yml
```

---

## 🎓 Learning Path for Juniors

1. **Week 1**: Read [CLI Reference](./CLI_REFERENCE.md)
2. **Week 2**: Build a simple CRUD app
3. **Week 3**: Learn [Events & Listeners](./EVENTS_LISTENERS.md)
4. **Week 4**: Implement [Authorization](./AUTHORIZATION_POLICIES.md)
5. **Week 5**: Add [Background Jobs](./BACKGROUND_JOBS.md)

---

## 🔗 Additional Resources

- [Main AI Prompt](../LICH_AI_PROMPT.md)
- [Changelog](../../CHANGELOG.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

**Lich Framework v1.3.0**

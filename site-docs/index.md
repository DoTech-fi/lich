# 🧙 Lich Framework

<div align="center">
<h2>AI-Ready Full-Stack Project Generator</h2>
<p>Generate production-ready applications with FastAPI, Next.js, and complete DevOps in seconds.</p>
</div>

---

## ✨ What is Lich?

Lich Framework is a **project generator** and **CLI toolkit** that creates full-stack applications with:

- 🏗️ **FastAPI Backend** - High-performance Python API
- ⚛️ **Next.js Frontend** - Modern React with TypeScript
- 🗃️ **PostgreSQL + Redis** - Database and caching
- 🐳 **Docker Ready** - Production deployment included
- 🤖 **AI-Ready** - Pre-configured rules for AI coding assistants

## 🚀 Quick Start

```bash
# Install Lich CLI
pip install lich

# Create a new project
lich init

# Navigate and start development
cd your-project
lich dev
```

That's it! You now have a full-stack app running:

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |

## 📦 Key Features

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Project Generation**

    ---

    Create complete projects with one command. Choose auth strategy, database, and features interactively.

    [:octicons-arrow-right-24: lich init](commands/init.md)

-   :material-cog:{ .lg .middle } **Code Generators**

    ---

    Generate entities, services, APIs, DTOs, and more with `lich make` commands.

    [:octicons-arrow-right-24: lich make](commands/make/overview.md)

-   :material-database:{ .lg .middle } **Database Migrations**

    ---

    Manage database schema with Alembic integration through simple CLI commands.

    [:octicons-arrow-right-24: lich migration](commands/migration.md)

-   :material-test-tube:{ .lg .middle } **Testing Tools**

    ---

    Run tests with pytest, generate factories, and seed data easily.

    [:octicons-arrow-right-24: lich test](commands/test.md)

</div>

## 🏛️ Architecture

Lich generates projects following **Clean Architecture** principles:

```
backend/
├── api/http/           # FastAPI routers
├── internal/
│   ├── entities/       # Domain models & rules
│   ├── services/       # Business logic (use cases)
│   ├── ports/          # Interfaces (abstractions)
│   └── adapters/       # Implementations (DB, cache)
└── main.py

frontend/
└── Next.js 14+ with App Router
```

[:octicons-arrow-right-24: Learn more about Architecture](architecture/overview.md)

## 🤖 AI-Ready

Every Lich project includes AI rules and prompts that help coding assistants (Claude, GPT, Copilot) understand and follow the architecture:

- `.lich/rules/` - Architecture rules for AI
- `CLAUDE.md` / `AI_RULES.md` - Project-specific instructions
- Inline comments explaining patterns

[:octicons-arrow-right-24: Learn about AI Integration](best-practices/ai.md)

## 📚 Next Steps

1. [**Installation**](getting-started/installation.md) - Install Lich CLI
2. [**Quick Start**](getting-started/quickstart.md) - Create your first project
3. [**Commands**](commands/overview.md) - Learn all CLI commands
4. [**Architecture**](architecture/overview.md) - Understand the patterns

# 🧙 Lich Toolkit

**AI-Ready Full-Stack Project Generator**

Generate production-ready applications with FastAPI backend, Next.js frontend, and complete DevOps setup in seconds.

## 🚀 Quick Start

```bash
# Install
pip install lich

# Create new project
lich init

# Start development
cd your-project
lich dev
```

## ✨ Features

- **🏗️ Full-Stack Generator**: FastAPI + Next.js + PostgreSQL + Redis
- **🤖 AI-Ready**: Pre-configured rules and prompts for AI coding assistants
- **🔐 Auth Options**: Keycloak SSO, JWT built-in, or none
- **📦 Code Generators**: Create entities, services, APIs, DTOs with one command
- **🗃️ Database Migrations**: Alembic integration with simple CLI
- **🐳 Docker Ready**: Production Docker Compose included

## 📦 Commands

| Command | Description |
|---------|-------------|
| `lich init` | Create a new project |
| `lich dev` | Start development servers |
| `lich make entity User` | Generate entity |
| `lich make service User` | Generate service |
| `lich make api users` | Generate API router |
| `lich migration create` | Create migration |
| `lich test` | Run tests |

## 🏛️ Generated Architecture

```
backend/
├── api/http/           # FastAPI routers
├── internal/
│   ├── entities/       # Domain models
│   ├── services/       # Business logic
│   ├── ports/          # Interfaces
│   └── adapters/       # DB implementations
└── main.py

frontend/
└── Next.js app with TypeScript
```

## 📖 Documentation

- [Full Documentation](https://dotech-fi.github.io/lich/)
- [CLI Reference](https://dotech-fi.github.io/lich/commands/)
- [Architecture Guide](https://dotech-fi.github.io/lich/architecture/)

## 📄 License

MIT License - [DoTech](https://github.com/DoTech-fi)

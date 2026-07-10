# 🧙 Lich Toolkit

> **AI-Ready Full-Stack Project Generator** - Create production-ready projects with a single command.

[![CI](https://github.com/DoTech-fi/lich/actions/workflows/ci.yml/badge.svg)](https://github.com/DoTech-fi/lich/actions/workflows/ci.yml)
[![E2E](https://github.com/DoTech-fi/lich/actions/workflows/e2e.yml/badge.svg)](https://github.com/DoTech-fi/lich/actions/workflows/e2e.yml)
[![PyPI](https://img.shields.io/pypi/v/lich)](https://pypi.org/project/lich/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ What is Lich?

Lich Toolkit is a **production-ready project generator** inspired by Laravel's elegance and Django's batteries-included philosophy, built for:

- 🐍 **Python** (FastAPI) backend
- ⚛️ **Next.js 14** frontend
- 🐳 **Docker** infrastructure
- 🤖 **AI-ready** with embedded rules for AI coding assistants

---

## 🚀 Quick Start

```bash
# Install CLI
pip install lich-cli

# Create new project
lich init

# Start development
cd your-project
lich dev
```

**That's it!** You now have a full-stack app running with:
- FastAPI backend at `http://localhost:8000`
- Next.js frontend at `http://localhost:3000`
- PostgreSQL + Redis via Docker
- Hot reload everywhere

---

## 📦 What You Get

```
your-project/
├── backend/                 # FastAPI + Clean Architecture
│   ├── internal/
│   │   ├── entities/       # Domain models
│   │   ├── services/       # Business logic
│   │   ├── ports/          # Interfaces
│   │   └── adapters/       # Database, Redis, HTTP
│   └── api/
│       └── http/           # REST endpoints
├── apps/
│   ├── web/                # Next.js main app
│   ├── admin/              # Admin panel
│   └── landing/            # Astro landing page
├── docker-compose.yml      # PostgreSQL, Redis, Traefik
└── .lich/
    └── rules/              # AI coding rules 🤖
```

---

## 🛠️ CLI Commands

### Project Management
```bash
lich init              # Create new project
lich dev               # Start development
lich stop              # Stop services
lich check             # Validate structure
```

### Code Generators
```bash
lich make entity User       # Entity + Port + Adapter
lich make service User      # Service class
lich make api users         # FastAPI router
lich make dto User          # Pydantic DTOs
lich make factory User      # Test factory
lich make middleware Auth   # Middleware
lich make event OrderPlaced # Domain event
lich make listener SendEmail # Event listener
lich make job SendInvoice   # Background job
lich make policy Post       # Authorization policy
```

### Middleware Management
```bash
lich middleware list        # Show all middlewares
lich middleware enable timing    # Enable middleware
lich middleware disable timing   # Disable middleware
```

### Database
```bash
lich migration init         # Initialize Alembic
lich migration create "add users"  # Create migration
lich migration up           # Apply migrations
lich migration down         # Rollback
```

### Development
```bash
lich shell             # Python REPL with context
lich routes            # List all API routes
lich test              # Run tests
lich seed              # Seed database
```

---

## 🔐 Authentication Options

Choose during `lich init`:

| Option | Description |
|--------|-------------|
| `jwt_builtin` | Built-in JWT auth (simple, self-contained) |
| `keycloak` | Keycloak SSO (enterprise, OIDC) |
| `auth_proxy` | External auth proxy |
| `none` | No authentication |

---

## 🏗️ Architecture

Lich uses **Clean Architecture** with strict dependency rules:

```
┌─────────────────────────────────────────┐
│            API Layer (FastAPI)          │  ← HTTP handlers
├─────────────────────────────────────────┤
│          Service Layer                  │  ← Business logic
├─────────────────────────────────────────┤
│          Domain Layer (Entities)        │  ← Pure Python
├─────────────────────────────────────────┤
│   Ports (Interfaces) → Adapters (DB)    │  ← Infrastructure
└─────────────────────────────────────────┘
```

**Rules:**
- ✅ API → Services → Entities
- ✅ Adapters implement Ports
- ❌ Entities never import external packages
- ❌ Services never import Adapters directly

---

## 🤖 AI-Ready

Every Lich project includes `.lich/rules/` with AI coding rules:

```
.lich/rules/
├── master-prompt.md      # Role switching
├── backend.md           # Architecture rules
├── frontend.md          # Next.js patterns
├── security.md          # OWASP guidelines
└── lich-cli.md          # CLI reference
```

**Works with:** Cursor, GitHub Copilot, ChatGPT, Claude

---

## 📦 Pre-built Middlewares

Enable in `main.py`:

| Middleware | Purpose |
|------------|---------|
| `RateLimitMiddleware` | Prevent API abuse |
| `RequestLoggingMiddleware` | Log all requests |
| `SecurityHeadersMiddleware` | OWASP headers |
| `TimingMiddleware` | Response time |

```bash
lich middleware enable security
lich middleware enable rate_limit
```

---

## 📚 Documentation

📖 **Full documentation:** [dotech-fi.github.io/lich](https://dotech-fi.github.io/lich/)

- [Getting Started](https://dotech-fi.github.io/lich/getting-started/)
- [CLI Commands](https://dotech-fi.github.io/lich/commands/)
- [Architecture](https://dotech-fi.github.io/lich/architecture/)

---

## 🔧 Requirements

- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Contributing

Contributions welcome! Please read our contributing guidelines.

---

**Made with 🧙 by [DoTech](https://github.com/DoTech-fi)**

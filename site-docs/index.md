# 🧙 Lich Toolkit

<div align="center">

<h1 style="font-size: 3rem; margin-bottom: 0;">The AI-Native Full-Stack Framework</h1>

<p style="font-size: 1.3rem; color: #888; margin-top: 10px;">
One CLI. One Architecture. Infinite Possibilities.<br/>
<strong>Human & AI speak the same language.</strong>
</p>

<div style="margin: 2rem 0;">
<a href="getting-started/quickstart/" class="md-button md-button--primary" style="margin: 5px;">🚀 Get Started</a>
<a href="integrations/mcp/" class="md-button" style="margin: 5px;">🤖 MCP Integration</a>
</div>

</div>

---

## 🎯 Why Lich?

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } **AI-Native Development**

    ---
    
    Lich MCP lets AI assistants (Antigravity, Claude, Cursor) control your entire stack with **52 MCP tools**. Human and AI follow the same rules and commands.

-   :material-swap-horizontal:{ .lg .middle } **Monolithic & Microservice**

    ---
    
    Start as a monolith, scale to microservices. Same codebase, same commands. **Docker Compose** for dev, **Docker Swarm** for production.

-   :material-rocket-launch:{ .lg .middle } **One SSH = Deployed**

    ---
    
    `lich deploy production` - That's it. Ansible handles everything: SSL, reverse proxy, database, backups.

-   :material-magnify:{ .lg .middle } **SEO-First Landing**

    ---
    
    Astro landing page with WordPress API backbone. Server-side rendered, blazing fast, **100 Lighthouse score**.

</div>

---

## ⚡ The Complete Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR PROJECT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎨 Design    →    ⚛️ Frontend    →    🐍 Backend    →    🚀 Deploy   │
│                                                                 │
│   ┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────┐ │
│   │ Figma   │     │ Next.js   │     │ FastAPI  │     │Ansible│ │
│   │ tokens  │     │ + Admin   │     │ + Redis  │     │+ SSH  │ │
│   └─────────┘     └───────────┘     └──────────┘     └───────┘ │
│                                                                 │
│   ┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────┐ │
│   │ Landing │     │ TypeScript│     │PostgreSQL│     │Traefik│ │
│   │ (Astro) │     │ + Tailwind│     │ + Alembic│     │+ SSL  │ │
│   └─────────┘     └───────────┘     └──────────┘     └───────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    🤖 Lich MCP (52 Tools)
                              ↕
              ┌───────────────────────────────┐
              │ Antigravity │ Claude │ Cursor │
              └───────────────────────────────┘
```

---

## 🤖 Lich MCP - AI Speaks Your Stack

!!! success "52 MCP Tools for Complete Control"

Your AI assistant can now:

| Category | What AI Can Do |
|----------|---------------|
| **Code Generation** | Create entities, services, APIs, DTOs, events, jobs |
| **Database** | Run migrations, seed data, check status |
| **Development** | Start/stop dev environment, manage middleware |
| **Quality** | Lint code, run tests, security scans |
| **Deployment** | Deploy to staging/production, manage backups |
| **Secrets** | Generate, rotate, validate secrets |

```bash
# Install MCP in your AI tool
pip install lich
lich serve  # Start MCP Server
```

[:octicons-arrow-right-24: Complete MCP Integration Guide](integrations/mcp.md)

---

## 🚀 From Zero to Production in 5 Minutes

=== "1. Install"

    ```bash
    pip install lich
    ```

=== "2. Create Project"

    ```bash
    lich init
    # Answer a few questions...
    ```

=== "3. Develop"

    ```bash
    cd my-project
    lich start
    # Frontend: http://localhost:3000
    # Admin: http://localhost:3002  
    # Backend: http://localhost:8000
    ```

=== "4. Deploy"

    ```bash
    lich deploy production
    # ✅ SSL configured
    # ✅ Database migrated
    # ✅ Backups scheduled
    ```

---

## 📦 What You Get

<div class="grid" markdown>

<div markdown>

### Frontend Stack

- ⚛️ **Next.js 14+** - App Router, Server Components
- 🎨 **Tailwind CSS** - Utility-first styling
- 📝 **TypeScript** - Full type safety
- 🔐 **Auth Ready** - JWT or Keycloak SSO
- 📊 **Admin Panel** - Pre-built dashboard

</div>

<div markdown>

### Backend Stack

- 🐍 **FastAPI** - High-performance Python
- 🏛️ **Clean Architecture** - SOLID principles
- 🗃️ **PostgreSQL/MongoDB** - Your choice
- ⚡ **Redis** - Caching & sessions
- 📋 **Alembic** - Database migrations

</div>

<div markdown>

### DevOps Stack

- 🐳 **Docker Compose** - Local development
- 🐝 **Docker Swarm** - Production scaling
- 🔒 **Traefik** - Reverse proxy + SSL
- 📦 **Ansible** - One-command deployment
- 🔄 **GitHub Actions** - CI/CD pipelines

</div>

<div markdown>

### SEO Stack

- ⭐ **Astro Landing** - Static, fast, SEO-optimized
- 📝 **WordPress API** - Content management
- 🔍 **100 Lighthouse** - Perfect scores
- 🌐 **i18n Ready** - Multi-language support

</div>

</div>

---

## 🏛️ SOLID Architecture

Every Lich project follows **Clean Architecture** principles:

```
backend/
├── api/http/           # Controllers (thin layer)
├── internal/
│   ├── entities/       # Domain models & business rules
│   ├── services/       # Use cases (application logic)
│   ├── ports/          # Interfaces (what we need)
│   └── adapters/       # Implementations (how we do it)
├── dto/                # Request/Response shapes
└── validators/         # Input validation
```

!!! tip "Same Rules for Human & AI"
    The `.lich/rules/` folder contains architecture rules that both developers and AI assistants follow. No more "AI broke my code" - everyone speaks the same language.

[:octicons-arrow-right-24: Deep Dive into Architecture](architecture/overview.md)

---

## 🔧 CLI Power

<div class="grid cards" markdown>

-   **Project Commands**
    
    ```bash
    lich init          # Create project
    lich start         # Start dev environment
    lich stop          # Stop everything
    lich upgrade       # Update to latest
    ```

-   **Code Generators**
    
    ```bash
    lich make entity User
    lich make service Order
    lich make api Product
    lich make job SendEmail
    ```

-   **Database Operations**
    
    ```bash
    lich migration create "add_users"
    lich migration up
    lich seed users
    lich routes       # List all APIs
    ```

-   **Quality & Deploy**
    
    ```bash
    lich ci            # Run all checks
    lich production-ready
    lich deploy staging
    lich backup create
    ```

</div>

[:octicons-arrow-right-24: All Commands Reference](commands/overview.md)

---

## 🌐 Development URLs

When you run `lich start`, you get:

| Service | URL | Description |
|---------|-----|-------------|
| 🖥️ **Frontend** | http://localhost:3000 | Main web application |
| 👔 **Admin Panel** | http://localhost:3002 | Administration dashboard |
| 🚀 **Landing Page** | http://localhost:4321 | Marketing/SEO page |
| 🐍 **Backend API** | http://localhost:8000 | FastAPI backend |
| 📚 **API Docs** | http://localhost:8000/docs | Swagger UI |
| 🗃️ **Adminer** | http://localhost:8081 | Database admin |

---

## 📚 Start Your Journey

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Get Lich CLI installed on your system.

    [:octicons-arrow-right-24: Install Now](getting-started/installation.md)

-   :material-play:{ .lg .middle } **Quick Start**

    ---

    Create your first project in 5 minutes.

    [:octicons-arrow-right-24: Let's Go](getting-started/quickstart.md)

-   :material-robot:{ .lg .middle } **MCP Integration**

    ---

    Connect your AI assistant to Lich.

    [:octicons-arrow-right-24: Setup MCP](integrations/mcp.md)

-   :material-book:{ .lg .middle } **Architecture Guide**

    ---

    Understand the patterns and principles.

    [:octicons-arrow-right-24: Learn More](architecture/overview.md)

</div>

---

<div align="center" style="margin-top: 3rem;">

**Built with ❤️ by [DoTech](https://github.com/DoTech-fi)**

*Where developers and AI agents build together.*

---

## 📬 Contact

Have questions, feedback, or want to collaborate?

| | |
|:--:|:--|
| 📧 **Email** | [babak.dorani@gmail.com](mailto:babak.dorani@gmail.com) |
| 💼 **LinkedIn** | [Babak Dorani Arab](https://www.linkedin.com/in/babakdoraniarab/) |

</div>

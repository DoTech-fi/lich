# Changelog

All notable changes to Lich Framework will be documented in this file.

## [1.3.1] - 2026-01-02

### Added
- **`lich middleware list`** - Show all middlewares and their status
- **`lich middleware enable <name>`** - Enable a middleware
- **`lich middleware disable <name>`** - Disable a middleware
- **`lich middleware enable-all`** - Enable all middlewares
- **`lich middleware disable-all`** - Disable all middlewares
- **Pre-built middlewares (opt-in)**:
  - `RateLimitMiddleware` - Prevent API abuse
  - `RequestLoggingMiddleware` - Log all requests
  - `SecurityHeadersMiddleware` - OWASP security headers
  - `TimingMiddleware` - Response time headers
- **Comprehensive documentation**:
  - CLI Reference Wiki
  - Auth & Policy Guide
  - Middleware Guide
  - Factory Guide
  - Events & Listeners Guide
  - Background Jobs Guide
  - Authorization Policies Guide
  - AI Enforcement Guide

---

## [1.3.0] - 2026-01-02

### Added
- **`lich make factory`** - Generate test factories using Faker
- **`lich make middleware`** - Generate FastAPI middleware
- **`lich make event`** - Generate domain event classes
- **`lich make listener`** - Generate event listeners
- **`lich make job`** - Generate background jobs (Celery or Temporal)
- **`lich make policy`** - Generate authorization policies
- **39 unit tests** for all CLI commands

---

## [1.2.0] - 2026-01-02

### Added
- **`lich make`** - Code generators (Laravel Artisan style)
  - `lich make entity <Name>` - Generate entity + port + adapter
  - `lich make service <Name>` - Generate service class
  - `lich make api <Name>` - Generate FastAPI router
  - `lich make dto <Name>` - Generate Pydantic DTOs
- **`lich shell`** - Interactive Python REPL with project context
- **`lich routes`** - List all API routes in table format
- **`lich test`** - Pytest wrapper with useful options
  - `--unit`, `--integration`, `--coverage`, `--watch`
- **`lich seed`** - Database seeding with custom seeders

---

## [1.1.0] - 2026-01-02

### Added
- **`lich adopt`** - Analyze existing Python project and create Lich project
- **`lich migration`** - Database migrations with Alembic wrapper
  - `lich migration init` - Initialize Alembic
  - `lich migration create` - Create new migration
  - `lich migration up` - Apply migrations
  - `lich migration down` - Rollback migrations
  - `lich migration status` - Show migration status
- New init questions: `is_microservice`, `include_admin_panel`
- New auth option: `auth_proxy`
- Landing backend option: `none`

---

## [1.0.3] - 2026-01-02

### Added
- Interactive version picker in `lich upgrade`
- Users can now select which version to upgrade to

---

## [1.0.2] - 2026-01-02

### Added
- Enhanced `lich version` command with available versions table
- Added `--history` flag to show full changelog
- CHANGELOG.md file for version tracking

---

## [1.0.1] - 2026-01-02

### Added
- Mobile development rules (`mobile.md`)
- Rules for React Native / Flutter development

---

## [1.0.0] - 2026-01-02

### Added
- Initial Lich Framework release
- Full-stack project generator with Cookiecutter
- **CLI Commands**: `lich init`, `lich dev`, `lich stop`, `lich check`, `lich upgrade`
- **Backend**: FastAPI with Lich Architecture (entities, services, ports, adapters)
- **Frontend**: Next.js web app, admin panel, Astro landing page
- **Infrastructure**: Docker Compose with Traefik, PostgreSQL/MongoDB, Redis, Keycloak
- **AI-Ready**: 12 rule files, 4 workflow files, CLAUDE.md, AI_CONTEXT.md
- **Rules**: security, ui-ux, docker, backend, frontend, devops, platform, testing, documentation, master-prompt, agentlog, infra
- **Workflows**: add-feature, add-entity, add-api, create-landing

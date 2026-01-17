# Changelog

All notable changes to Lich Toolkit will be documented in this file.

## [1.12.1] - 2026-01-17

### Fixed
- **Deploy Init**: Fixed timeout issue during Docker installation. Increased SSH command timeout from 30s to 120s default, and 300s for Docker installation.

## [1.12.0] - 2026-01-17

### Added
- **Complete Deployment Workflow**: Major overhaul of `lich deploy` command suite:
  - `lich deploy setup`: Enhanced setup with SSH key generation, domain config, env vars
  - `lich deploy init <env>`: NEW - Initialize server (Docker install, clone, Traefik, SSL)
  - `lich deploy status`: Real SSH-based status check with container health, resources
  - `lich deploy logs <env>`: NEW - View deployment logs with follow mode
  - `lich deploy prod all`: Deploy all components at once
- **SSH Deploy Key**: Auto-generate ED25519 deploy key for private repos with GitHub instructions
- **Domain Configuration**: Configure main, API, and admin subdomains during setup
- **Environment Variables**: Collect from `.env.example` with auto-generated secrets
- **Traefik Auto-Setup**: Configure Traefik with Let's Encrypt SSL on server init

### Fixed
- Fixed `AttributeError` in deploy setup/status when config contains non-dict values

## [1.11.0] - 2026-01-09

### Added
- **New Feature**: Added `lich doctor` command to diagnose project health, structure, and configuration discrepancies.
- **Documentation**: Updated `AGENTS.md` and `CLAUDE.md` to include `lich doctor`.

## [1.10.7] - 2026-01-09

### Added
- **Upgrade Command**: Added "Smart File Injection" to `lich upgrade`. It now checks for and adds specifc missing framework configuration files (e.g., `.eslintrc.json` in apps) to existing projects without overwriting user code.

## [1.10.6] - 2026-01-09

### Fixed
- **Templates**: Added missing `.eslintrc.json` to `apps/web` and `apps/landing` templates to prevent interactive prompts during CI (`next lint`).

## [1.10.5] - 2026-01-09

### Fixed
- **Templates**: Added missing `.eslintrc.json` to `apps/admin` template to prevent interactive prompts during CI (`next lint`).

## [1.10.4] - 2026-01-09

### Fixed
- **Upgrade Command**: Fixed `lich upgrade` to properly render templates (e.g., GitHub Actions workflows) instead of raw copying, resolving syntax errors in CI files.
- **CI Command**: Corrected log message to show the actual `act` command being executed.

## [1.10.3] - 2026-01-09

### Fixed
- **CI Command**: Fixed `lich ci` (act) command argument order. Removed explicit `push` event when not required, ensuring correct workflow execution with `-W`.

## [1.10.2] - 2026-01-09

### Fixed
- **Release Workflow**: Validated automated release workflow utilizing environment variables for PyPI authentication.

## [1.10.1] - 2026-01-09

### Fixed
- **Upgrade Command**: Added `.github/workflows` to the synchronization list in `lich upgrade`. This ensures that new CI/CD workflows are correctly copied to existing projects during an upgrade.

## [1.10.0] - 2026-01-09

### Added
- **Deploy System**: Full `lich deploy` suite with Ansible integration:
  - `lich deploy setup`: Interactive setup for staging/production (SSH config, git repo)
  - `lich deploy stage`: Deploy to staging environment
  - `lich deploy prod`: Deploy to production (with confirmation)
  - `lich deploy status`: View current deployment configuration
  - Support for private repositories via `.secrets` (GITHUB_TOKEN)
  - Live stdout streaming for real-time deployment logs
- **CI Improvements**:
  - `lich ci setup`: Interactive setup for local CI (act)
  - Component-specific CI commands (`lich ci backend`, `web`, `admin`, `landing`)
  - Local execution flag (`-l` / `--local`) to run without Docker
  - Manual-only GitHub Actions workflow for main CI (`workflow_dispatch`)
- **Documentation**:
  - Validated and updated `AGENTS.md` and `CLAUDE.md` with new commands
  - Updated site documentation (English & Farsi) for CI and Deploy commands

## [1.9.0] - 2026-01-08

### Added
- **Lich-First AI Enforcement**: New rules (`.lich/rules/ai-behavior.md`) and updates to `AGENTS.md`/`CLAUDE.md` to force AI agents to prioritise Lich CLI/MCP tools.
- **MCP Tool Reference**: Added comprehensive map of CLI commands to MCP tools in `lich-cli.md`.

---

## [1.8.4] - 2026-01-08

### Fixed
- **MCP Protocol**: Fixed critical bug where startup message was printed to stdout, corrupting MCP JSON-RPC protocol. Antigravity/Cursor would show "invalid character 'ð' looking for beginning of value" error. Startup message now correctly goes to stderr.

---

## [1.8.3] - 2026-01-08

### Changed
- **Upgrade Command**: Updates `pip` to the latest version before upgrading the Lich CLI.
- **UX**: Post-upgrade message now explicitly emphasizes restarting the AI tool (Antigravity/Cursor/VSCode).

---

## [1.8.2] - 2026-01-08

### Fixed
- **Upgrade Command**: Fixed an infinite loop in `lich upgrade` caused by a hardcoded version string. The CLI now dynamically determines its version from package metadata.

---

## [1.8.1] - 2026-01-08

### Fixed
- **CI/CD**: Resolved linting errors (`Panel` import) and unit test failures (`get_antigravity_config_path` check) in the CI pipeline.

---

## [1.8.0] - 2026-01-08

### Added
- **Seamless Upgrade**: `lich upgrade` now automatically restarts the process after updating the CLI.
- **Setup Reminder**: Added a colored reminder to run `lich setup` after a successful upgrade.

### Fixed
- **Upgrade Reliability**: Added `--no-cache-dir` to `lich upgrade` to prevent issues when a new version is not yet in the local pip cache.

---

## [1.7.9] - 2026-01-08

### Fixed
- **MCP Setup**: Fixed incorrect Antigravity configuration path in `lich setup` command.

---

## [1.6.0] - 2026-01-07

### Added
- **Total Security Overhaul**:
  - `lich security` command with 5+ scanners (bandit, safety, npm-audit, gitleaks, trivy)
  - `RateLimitMiddleware`, `CSRFMiddleware`, `AuditMiddleware`, `SanitizeMiddleware`
  - Deep readiness checks in `health.py`
  - Automated secure headers and CORS configuration
- **Production Readiness**:
  - `lich production-ready` command with 15+ automated checks and `--fix` capability
  - `lich deploy` with Ansible integration (SSH, dynamic inventory)
  - `lich backup` with S3 support and multi-db (Postgres, Redis, Mongo, MySQL) auto-detection
  - `lich secret` for credential management
- **DevOps & Infrastructure**:
  - Full **Ansible** infrastructure code (`infra/ansible/`) with 7 roles
  - **GitHub Actions** workflows: `deploy.yml`, `rollback.yml`, `release.yml`, `prod-tests.yml`
  - `lich ci` for local continuous integration
  - `Makefile` for standardized developer experience
- **AI-Powered Development**:
  - `AGENTS.md` as the single source of truth for AI agents (Meta Architect persona)
  - Comprehensive `.lich/rules/` covering Backend, Frontend, Docker, Security, Platform, DevOps
- **Workers**:
  - Temporal/Celery worker integration patterns

---

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
- Initial Lich Toolkit release
- Full-stack project generator with Cookiecutter
- **CLI Commands**: `lich init`, `lich dev`, `lich stop`, `lich check`, `lich upgrade`
- **Backend**: FastAPI with Lich Architecture (entities, services, ports, adapters)
- **Frontend**: Next.js web app, admin panel, Astro landing page
- **Infrastructure**: Docker Compose with Traefik, PostgreSQL/MongoDB, Redis, Keycloak
- **AI-Ready**: 12 rule files, 4 workflow files, CLAUDE.md, AI_CONTEXT.md
- **Rules**: security, ui-ux, docker, backend, frontend, devops, platform, testing, documentation, master-prompt, agentlog, infra
- **Workflows**: add-feature, add-entity, add-api, create-landing

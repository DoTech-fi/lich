# Lich Toolkit - Agent Log

## 2026-01-02T14:45:00 - v1.3.0 Complete Update

**What Changed**:
- CLI v1.3.0: Added `lich make factory/middleware/event/listener/job/policy`
- Pre-built middlewares: RateLimit, Logging, Security, Timing (opt-in)
- Comprehensive test suite: 39 tests for all CLI commands
- Wiki documentation: CLI_REFERENCE, AUTH_AND_POLICY, MIDDLEWARE_GUIDE, EVENTS_LISTENERS, BACKGROUND_JOBS, AUTHORIZATION_POLICIES
- AI_RULES.md: Complete rules for AI agents
- AI_ENFORCEMENT.md: Guide on forcing AI to follow rules
- Template rules updated: lich-cli.md, backend.md, master-prompt.md

**Why Changed**:
User requested complete CLI expansion with documentation for juniors and AI agents

---

## 2026-01-02T01:00:00 - Comprehensive QA & Enhancements

**What Changed**: 
- Added TLS/Let's Encrypt support (`use_tls` option)
- Created QUICK_START.md with dynamic service URLs
- Updated post_gen hook to show all service URLs
- Fixed docker-compose.yml (proper YAML quoting)
- Fixed tsconfig.json (moduleResolution: node)
- Added unit tests (test_user_entity, test_user_service, test_dto_validation)
- Added integration tests (test_api_integration)
- Added pytest.ini configuration
- Cleaned cookiecutter.json (English only)
- Changed default_language to 'en' first

**Why Changed**:
User requested comprehensive QA check and test coverage

---

## 2026-01-01T21:09:00 - Added Auth Pages

**What Changed**: 
- Login, Register, Forgot Password, Dashboard, Profile, Settings pages

---

## 2026-01-01T20:01:00 - Enhanced with Additional Features

**What Changed**: 
- API client, AuthContext, CI/CD, Dockerfile, Sidebar/Header components

---

## 2026-01-01T19:36:00 - Initial Creation

**What Changed**: 
- Complete Cookiecutter template for Lich Toolkit

- **[Lich Framework] Tasks Updated**:
  - **WHAT**: Added "Priority 10: Developer Experience" to `LICH_TASKS.md` with Makefile task.
  - **WHY**: To standardize the Makefile utility across all Lich-based projects as a core feature.
  - **WHEN**: 2026-01-07

---

## 2026-01-07T21:20:00 - Priority 1 Security Complete

**What Changed**:
- `settings.py`: Added `security_enabled` and `rate_limit_per_minute` settings
- `main.py`: Security middlewares enabled by default, strict CORS, conditional OpenAPI docs
- `health.py`: Deep readiness check with DB and Redis connectivity
- `.env.example`: Added `SECURITY_ENABLED=true` and `RATE_LIMIT_PER_MINUTE=60`

**Why Changed**: Implementing LICH_TASKS.md Priority 1: Security

---

## 2026-01-07T21:30:00 - Priority 2 CLI Commands Complete

**What Changed**:
- `security.py`: Security scanning with bandit, safety, npm audit, gitleaks, trivy
- `lint.py`: Code linting with ruff/flake8 for Python and eslint for TypeScript
- `deploy.py`: Deployment with SSH, dynamic inventory, Ansible playbook execution
- `backup.py`: Database backup with auto-detect, PostgreSQL/MySQL/MongoDB/Redis, S3 upload
- `secret.py`: Secret management with generate, rotate, check subcommands
- `cli.py`: Registered all new sub-apps

**Why Changed**: Implementing LICH_TASKS.md Priority 2: CLI Commands

---

## 2026-01-07T21:35:00 - Priority 3: Ansible Deployment Complete

**What Changed**:
- Created `infra/ansible/` folder structure with ansible.cfg, group_vars, inventory
- Created 7 roles: common, docker, traefik, postgres, redis, app, backup
- Created 4 playbooks: site.yml, update.yml, backup.yml, rollback.yml
- Inventory templates for production and staging environments

**Why Changed**: Implementing LICH_TASKS.md Priority 3: Ansible Deployment

---

## 2026-01-07T21:40:00 - Priority 4: Middlewares Complete

**What Changed**:
- `csrf.py`: CSRF protection middleware with token generation and validation
- `audit.py`: Audit logging middleware with optional DB persistence
- `sanitize.py`: Input sanitization middleware with XSS pattern removal
- `main.py`: Updated with all new middleware references

**Why Changed**: Implementing LICH_TASKS.md Priority 4: Middlewares

---

## 2026-01-07T21:45:00 - Priority 5-6: Production Ready & CI/CD Complete

**What Changed**:
- `production_ready.py`: Production readiness checker with 15 security/quality/ops checks
- `release.yml`: GitHub Actions workflow for version bump and releases
- `deploy.yml`: GitHub Actions workflow for deployment with backup and migrations
- `rollback.yml`: GitHub Actions workflow for database restore and code rollback
- `ci.py`: Local CI command for running lint, tests, security scans

**Why Changed**: Implementing LICH_TASKS.md Priority 5-6: Production Ready & CI/CD

---

## 2026-01-07T21:50:00 - Priority 10: Dev Experience + Final Updates

**What Changed**:
- `Makefile`: Comprehensive Makefile for dev/test/deploy/utilities
- Marked Priority 7 (Monorepo), 8 (Scheduled Tasks), 9 (Observability) as skipped/deferred
- Updated progress summary table


---

## 2026-01-07 - v1.6.0 Release (Admin, CLI, OAuth)

**What Changed**:
- **Admin Seeding**: Added `backend/scripts/seed_db.py` and `cookiecutter.json` variables (`admin_email`, `admin_password`) to automatically create an admin user on startup.
- **CLI Enhancement**: Replaced `dev-start.sh` and `dev-stop.sh` with Python-based `lich start` and `lich stop` commands in the CLI.
- **OAuth**: Added Google OAuth configuration to the template and documentation.
- **Template Fixes**: Translated Farsi text in `agentlog.md` and `LICH_AI_PROMPT.md` to English.
- **Agent Rules**: Overhauled `AGENTS.md` to be a comprehensive Master Prompt properly referencing all CLI commands and rules.
- **Documentation**: Updated `site-docs` to reflect `lich start/stop` and new auth configurations.

**Why Changed**: To improve developer experience, ensure projects start with a secure admin user, and fix language inconsistencies for a professional release.

## 2026-01-07 - Implemented Professional Upgrade Safety

**What Changed**:
- **Version Stamping**: New projects get a `.lich/lich.version` file with the generating CLI version.
- **Compatibility Check**: CLI now checks this file on startup.
- **Warnings**:
    - **Legacy**: Warns if version file is missing.
    - **Major Mismatch**: RED ALERT if CLI is v2+ and Project is v1.
    - **Outdated CLI**: Yellow warning if CLI < Project.

**Why Changed**: User requested a robust, professional process to handle breaking changes and ensure `pip uninstall/install` safety.



---

## 2026-01-08 - CI/CD Stabilization & Docker Optimization

**What Changed**:
- **Docker Optimization**: Added `.dockerignore` files for `apps/web` and `apps/admin` (removing `node_modules` from build context) and optimized `backend/.dockerignore`.
- **Lich Framework Fixes**: Resolved `IndentationError` in `backup.py` and ambiguities in `lint.py` to fix CI failures.
- **Emberboard CI**: Fixed 178+ lint errors, corrected `memory_service.py` corruption, and verified backend tests pass (119/119).

**Why Changed**: To ensure all CI pipelines pass and Docker images are built efficiently without unnecessary context bloat.

---

## 2026-01-08 - Documentation Site Redesign 📚

**What Changed**:
- **index.md**: Complete redesign with exciting landing page
  - Lich MCP highlight with 47 tools
  - Full-stack architecture ASCII diagram
  - Monolithic + Microservice flexibility
  - One SSH deployment story
  - SEO-first landing with WordPress API
- **integrations/mcp.md**: Comprehensive MCP integration guide
  - Setup for Antigravity, Claude, Cursor, VS Code
  - Complete 47-tool reference table
  - Example AI conversations
  - Troubleshooting guide

**Why Changed**: User requested an exciting landing page highlighting all Lich features and MCP integration guides.

---

## 2026-01-08 - Complete MCP Tools Implementation 🤖 (47 Tools!)

**What Changed**:
- **Expanded from 21 to 47 MCP tools** across 14 modules
- **New tool modules created**:
    - `routes.py`: `lich_routes`
    - `seed.py`: `lich_seed`, `lich_seed_list`
    - `migration.py`: `lich_migration_init`, `lich_migration_create`, `lich_migration_up`, `lich_migration_down`, `lich_migration_status`, `lich_migration_heads`
    - `secret.py`: `lich_secret_generate`, `lich_secret_rotate`, `lich_secret_check`
    - `production.py`: `lich_production_ready_check`, `lich_production_ready_fix`
    - `ci.py`: `lich_ci_all`, `lich_ci_backend`, `lich_ci_web`, `lich_ci_admin`
    - `mw.py`: `lich_middleware_list`, `lich_middleware_enable`, `lich_middleware_disable`
    - `dev.py`: `lich_dev_start`, `lich_dev_stop`
    - `utility.py`: `lich_adopt`, `lich_upgrade`, `lich_version`
- **Updated tests**: 17 tests verifying all 47 tools are registered and callable

**Why Changed**: User requested complete MCP implementation covering all CLI commands.

---

## 2026-01-08 - MCP Server Implementation 🤖

**What Changed**:
- **MCP Dependency**: Added `mcp>=0.1.0` to `cli/pyproject.toml`.
- **Server Core**: Created `cli/src/lich/mcp/server.py` using FastMCP.
- **Modular Tools**: Split tools into `cli/src/lich/mcp/tools/` modules:
    - `project.py`: `lich_init`, `lich_check_project`
    - `make.py`: `lich_make_service`, `lich_make_entity`, `lich_make_api`, etc.
    - `git.py`: `lich_git_commit`, `lich_git_tag`, `lich_git_push`
    - `qa.py`: `lich_lint_backend`, `lich_lint_frontend`, `lich_security_scan`, `lich_test`
    - `ops.py`: `lich_deploy`, `lich_backup`
- **CLI Registration**: Registered `lich serve` command in `cli.py`.
- **Testing**:
    - `cli/tests/test_mcp_server.py`: Verifies all 21 tools are registered.
    - `cli/tests/test_mcp_integration.py`: Confirms tool wiring to underlying CLI functions.
- **Documentation**: Created `site-docs/integrations/mcp.md` and updated `mkdocs.yml`.

**Why Changed**: User requested to implement MCP (Model Context Protocol) support to allow AI assistants (Claude, Gemini) to interact with Lich CLI tools programmatically.

---

## 2026-01-08 - Easy AI Tool Setup Command 🔧

**What Changed**:
- **New `lich setup` command**: Interactive setup for AI tool MCP integration
- **Supported tools**: Antigravity, Claude Desktop, Cursor, VS Code
- **Features**:
    - Interactive menu to select AI tool
    - Auto OS detection (macOS, Linux, Windows)
    - Config merging (preserves existing MCP servers)
    - Backup before modification
    - `lich setup status` to check configuration
- **Files created**:
    - `cli/src/lich/commands/setup.py`: Setup command implementation
    - `cli/tests/test_setup.py`: Unit tests (OS detection, config paths, merging)
    - `docs/wiki/SETUP_GUIDE.md`: Documentation

**Why Changed**: User requested easy integration between Lich MCP and AI tools like Antigravity.

---

## 2026-01-08 - Documentation i18n Sync 🌐

**What Changed**:
- Created `site-docs/best-practices/git-workflow.fa.md` (Farsi translation)
- Added Contact section to `site-docs/index.fa.md`
- Verified all 83 documentation files have matching Farsi/English versions

**Why Changed**: User requested Farsi and English documentation to be in sync.


# Changelog

All notable changes to Lich Toolkit will be documented in this file.

## [1.15.1] - 2026-11-12

Maintenance release — unblocks fresh installs and turns CI green again after four months of upstream dependency drift. No feature changes.

### Fixed
- **MCP server broken on fresh installs**: `mcp` was pinned `>=0.1.0` with no upper bound, so new installs pulled `mcp` 2.x, which renamed `FastMCP` → `MCPServer` and crashed `lich.mcp.server` on import. Pinned `mcp>=0.1.0,<2`.
- **README install command**: `pip install lich-cli` → `pip install lich` (the `lich-cli` package does not exist on PyPI).
- **Test suite under current typer/click**: `typer.exceptions.Exit` is now a distinct class from `click.exceptions.Exit`; assertions in `test_common_and_extras.py` updated to expect `typer.Exit` (what the code actually raises).

### Changed
- **Lint clean under current Ruff**: moved late `lich.commands.common` imports to the top of their modules (E402), removed unused imports/variables (F401/F841).

### Removed
- **Stale `nextjs.yml` workflow**: a GitHub-default "Deploy Next.js site to Pages" workflow that failed on every push (no root `package.json`). Docs deploy via `docs.yml` (MkDocs) is the real site.

## [1.15.0] - 2026-07-11

Gates & golden-path sprint — Phase 4 (final) of the v1 hardening roadmap. Adds the CI gates that keep the framework honest and an end-to-end test that proves a generated project actually runs.

### Added
- **Golden-path e2e**: `scripts/e2e_local.sh` + `.github/workflows/e2e.yml` generate a project with the template, boot infra, build & run the backend image, run its tests, and hit `/api/health` + auth endpoints — matrix over postgresql+jwt and mongodb+none. Proves `lich new` produces a working app, not just compiling code.
- **CI security scanning**: `bandit` (subprocess findings triaged — all call sites use list args via `_shell.py`) + `pip-audit` (no vulnerable dependencies) run on every push.
- **Coverage gate**: CI enforces `--cov-fail-under=80` (currently 81%).
- **MCP protocol smoke test**: spawns the MCP server over stdio and verifies a real JSON-RPC `initialize` + `tools/list` returns the 52 tools and a read-only tool call succeeds.
- **`SECURITY.md`** disclosure policy; README badges (CI, e2e, PyPI, Python) replacing a stale hardcoded version badge.

### Fixed
- **Generated backend healthcheck**: the Dockerfile used `curl` (absent in `python:3.12-slim`) and the wrong path — now a `curl`-free Python urllib check against `/api/health`. This was blocking the e2e.

### Chore
- Untracked `__pycache__/*.pyc` files that had been committed since v1.12.0 (they were already gitignored).

## [1.14.0] - 2026-07-11

Quality sprint — Phase 3 of the v1 hardening roadmap. Large internal refactor, MCP modernization, type checking, and a big test-coverage lift. No behavior change for users; all security guards from Phase 1 preserved.

### Changed
- **Deduplicated** copy-pasted helpers into `commands/common.py` (project detection, subprocess runners, tool checks) — removed 8 copies of `_check_lich_project`, 4 of `_run_command`, and the duplicated template-download helpers.
- **Broke up oversized functions** into orchestrator + focused helpers (all < 80 lines): `deploy_setup`, `deploy_init`, `upgrade_project`, `ci_setup`; factored the near-identical `ci_web`/`ci_admin`/`ci_landing` into one implementation. Every Phase 1 security guard (input validation, SSH-destination checks, shell-quoting, scp-path guards) verified preserved.
- **MCP tools modernized**: converted from closure-defined to module-level (now directly unit-testable); long-running tools (deploy/CI/migration/backup) are `async` via `asyncio.create_subprocess_exec` (never a shell). Tool inventory unchanged at 52; all Phase 1/2 argument validation preserved.
- **Exception hygiene**: narrowed 16 bare `except Exception` sites to specific exception types (no longer swallowing `SystemExit`/`KeyboardInterrupt`/programming errors).

### Added
- **Type checking**: `mypy` runs clean under a lenient config and is enforced in CI; added missing return-type hints across the CLI.
- **Test coverage raised from ~33% to 81%** (695 tests): new suites for `common`, `deploy`, `ci`, `security`, `backup`, `upgrade`, `secret`, `git`, `lint`, `dev`, `doctor`, `middleware`, `production-ready`, `version`, and the MCP tool layer, plus MCP functional tests.

## [1.13.1] - 2026-07-11

Correctness sprint — Phase 2 of the v1 hardening roadmap. Fixes the framework's own failing tests and several bugs in the generated project template.

### Fixed
- **Generated frontend was broken**: `.tsx`/`.ts` files were copied verbatim with raw Jinja syntax inside (auth-strategy conditionals never rendered). Templates now render through Jinja with `{% raw %}` guards where JSX uses `{{ }}`. Added a CLI-side generation smoke harness (`test_template_generation.py`) that renders the template and asserts no Jinja leaks + backend compiles across auth strategies.
- **Keycloak auth**: auto-created users no longer 500 on a missing email claim, a dotted username (e.g. `john.doe`), or land in `PENDING` — new dedicated `create_external_user` service path bypasses the registration DTO.
- **MCP**: tool failures now return `ERROR (exit N):`-prefixed output instead of silently looking like success; implemented the documented-but-missing `lich_ci_all` tool; the tool-inventory test now matches the real **52** registered tools (docs/tests claimed 47) via a symmetric set assertion that can't silently drift again.
- **Rate limiter**: the in-memory limiter now evicts stale IPs (was unbounded memory growth).
- **Generated tests**: `test_user_service.py` rewritten to match the real service API (it previously could not run at all — wrong constructor kwarg, method name, and exception type).
- **`lich version --history`**: robust CHANGELOG.md resolution outside a dev checkout.
- **Docs**: corrected the "47 MCP tools" claim to 52 everywhere and documented the real deploy/CI tool names.

## [1.13.0] - 2026-07-10

Security sprint — Phase 1 of the v1 hardening roadmap. Closes every known injection and default-secret vulnerability across the CLI, the MCP server, and the generated project template. Two new modules (`_validate.py`, `_shell.py`) form the security boundary: all user/config input is validated against strict allowlists at entry points, and all remote scripts are shell-quoted as defense-in-depth.

### Security — CLI
- **Shell injection fixed** (`deploy.py`): deploy-key verification no longer uses `shell=True` — runs as an argument list. It also now actually runs (previously the "✓" was faked) with a 15s timeout, advisory (never aborts setup).
- **SSH option-smuggling fixed** (`deploy.py`): a malicious `.lich/deploy.yml` from a cloned repo could set `ssh_name: -oProxyCommand=…` and execute local code at connect time (local RCE). SSH destinations are now validated (`validate_ssh_destination`) at every config-read and prompt site; scp key/env-file paths reject `-`-prefixed option smuggling.
- **Input validation everywhere** (new `_validate.py`): generator names (`lich make`), deploy paths, git URLs, git refs, domains, and `lich deploy logs -c` components are validated against strict allowlists at every entry point (prompts, options, config files). `validate_git_ref` closes `git tag --delete` argument injection.
- **Quoted remote scripts** (new `_shell.py`): every value interpolated into an SSH script is `shlex.quote()`d; `run_local`/`run_remote` never use `shell=True`. Production deploys pin `-f docker-compose.yml`.

### Security — MCP server
- `lich_make_*`, `lich_migration_create`, `lich_seed`, and `lich_git_tag` validate their name/ref arguments; `lich_git_commit`/`lich_adopt` reject `-`-prefixed option smuggling; `lich_secret_generate` bounds length (≤256) and count (≤20).
- `.secrets` and `.lich/*.env` are gitignored by `lich deploy setup`.

### Security — generated template
- **Production secret guard**: apps refuse to boot with `environment=production` while `secret_key`/`jwt_secret_key` still contain the `change-me` default.
- **No default admin password**: the `admin` default is removed; a random password is generated at project creation (printed once), and the seed script refuses empty/`admin` at runtime (env `ADMIN_PASSWORD` wins).
- **OAuth CSRF**: the Google OAuth flow now issues an HMAC-signed, time-bounded `state` bound to a per-session HttpOnly cookie nonce (double-submit) and rejects invalid/expired/replayed state at the callback. The cookie's `Secure` flag is environment-aware so localhost dev still works.
- **Traefik dashboard is dev-only**: `--api.insecure=true` and port 8090 moved to a `docker-compose.override.yml` that `lich deploy` never loads in production.

**Breaking change:** `/google/callback` now requires the `state` parameter (and the `oauth_state` cookie) — frontends generated before v1.13.0 must persist and echo the `state` returned by `/google/url`.

## [1.12.15] - 2026-01-21

### Fixed
- **MCP Tools**: Fixed JSON parsing errors when calling MCP tools like `lich_deploy_prod`. CLI output containing ANSI escape codes and emoji was breaking MCP protocol.
- **Solution**: Added `clean_cli_output()` and `run_lich_command()` shared utilities in `mcp/tools/__init__.py`. All subprocess outputs are now sanitized before returning to MCP.
- **Improvement**: Added `NO_COLOR=1` environment variable to disable Rich formatting in subprocess calls.

## [1.12.11] - 2026-01-18

### Fixed
- **Template Bug**: Fixed additional `use_temporal` reference in `.env.example` (line 69) that was missed in v1.12.10 fix.

## [1.12.10] - 2026-01-18

### Fixed
- **Template Bug**: Fixed `lich init` failure when selecting `task_runner=temporal`. Template files were using deprecated `cookiecutter.use_temporal == 'yes'` instead of `cookiecutter.task_runner == 'temporal'`. Affected files: `agentlog.md`, `post_gen_project.py`, `docker-compose.yml`, `QUICK_START.md`.

## [1.12.9] - 2026-01-17

### Fixed
- **Rate Limiter**: Added `X-Forwarded-For` header support for proper client IP detection behind reverse proxies (Traefik, Nginx). Fixes rate limit blocking all users when behind a load balancer.

### Added
- **Logout Page**: Added `/logout` page template to web app. Prevents 404 when clicking "Logout" in sidebar.

### Learnings from EmberBoard Production (documented in agentlog.md)
- `traefik.docker.network` label required on all services with multiple networks
- Next.js needs `ENV HOSTNAME="0.0.0.0"` in Dockerfile for health checks
- Build args (`ARG NEXT_PUBLIC_API_URL`) must be before `npm run build`
- Use separate ports for admin (3002) vs web (3000)

## [1.12.8] - 2026-01-17

### Fixed
- **Deploy Setup**: Fixed blocking `input()` call that caused `lich deploy setup` to hang in non-interactive terminals or AI agent sessions. Replaced with `Prompt.ask()` for consistent behavior.

## [1.12.7] - 2026-01-17

### Added
- **Deploy Prod**: Auto-detects and uses `docker-compose.prod.yml` for production deploys. Falls back to `docker-compose.yml` if not found.

## [1.12.6] - 2026-01-17

### Improved
- **Deploy Prod**: Now shows docker compose output during deployment so users can see what's happening.
- **Deploy Prod**: Verifies containers are actually running after deploy and shows their status.
- **Deploy Prod**: Fails properly with error output if docker compose fails.
- **Deploy Prod**: Added 300s timeout for container builds.

## [1.12.5] - 2026-01-17

### Fixed
- **Docker Commands**: Replaced all `docker-compose` with modern `docker compose` syntax in deploy init, deploy prod, and deploy logs commands.
- **Deploy Init**: Added 180s timeout for service startup.

## [1.12.4] - 2026-01-17

### Improved
- **Deploy Status**: Enhanced container status display. Now shows "No containers running" when services aren't started, with guidance to run `lich deploy prod all`.
- **Docker Compose**: Use modern `docker compose` command (without hyphen) with fallback to `docker-compose`.

## [1.12.3] - 2026-01-17

### Fixed
- **Deploy Setup**: Fixed bug where Step 3 (Git Repository) was skipped when config already existed. Now asks if user wants to reconfigure git settings.

## [1.12.2] - 2026-01-17

### Added
- **Deploy Setup**: Option to use existing SSH key or create new deploy key
- **UX**: Added recommendation message for creating new deploy key (more secure)

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

# Agent Log

## 2026-01-08

- Started debugging Lich MCP setup issue.
- Fixed `lich setup antigravity` config path to point to `~/.gemini/antigravity/mcp_config.json` instead of `settings.json`.
- Updated documentation and prepared release v1.7.9.
- Added `--no-cache-dir` to `lich upgrade` to prevent "distribution not found" errors.
- **UX Improvement**: `lich upgrade` now automatically restarts itself after updating the CLI.
- **UX Improvement**: Added a prominent reminder to run `lich setup` after upgrading.
- Released v1.8.0 containing these UX improvements.
- Released v1.8.1 to fix CI/CD pipeline issues (lint and tests).
- Added `--version` and `-V` flags to CLI (industry standard).
- **Critical Fix (v1.8.4)**: Fixed MCP protocol corruption bug - startup message was printing to stdout, breaking JSON-RPC protocol. Antigravity showed "invalid character 'ð'" error. Now prints to stderr.

## 2026-01-09

- **Docs Enhancement**: Added "Recommended Setup Flow" section to `site-docs/integrations/mcp.md` with 3-step workflow: `lich setup` → restart AI tool → first prompt with `AGENTS.md`.
- **Docs Enhancement**: Added "Upgrading Lich" section with `lich upgrade` command and post-upgrade steps.
- Updated both English (`mcp.md`) and Farsi (`mcp.fa.md`) versions.
- **Template Update**: Enhanced `AGENTS.md` with UI/UX architect mode (role 4), first-time setup instructions, and recovery section.
- **Template Update**: Replaced `CLAUDE.md` with redirect document that enforces reading `AGENTS.md` completely.
- **Feature**: Implemented act-based local CI with `lich ci setup` command and `--act` flag for all CI commands.
  - Created `ci_utils.py` with Docker/act check functions and beautiful Rich error messages.
  - Added `lich ci setup` to check Docker, install act, and configure for local CI.
  - Added `--act` or `-a` flag to `lich ci backend`, `lich ci web`, `lich ci admin`, `lich ci landing`.
  - Added `lich_ci_setup` MCP tool for AI assistants.
  - Added ARM Mac (M1/M2/M3) detection with `--container-architecture linux/amd64`.
  - Added `--reuse` flag to reuse containers between runs (faster).
  - Enhanced `lich ci setup` with OS/architecture detection (ARM Mac, Intel, Linux).
  - Creates `.actrc` config file with `--container-architecture` for ARM Macs and `--reuse` by default.
  - Enhanced `lich ci setup` to create `.secrets`, `.ci-vars`, `.ci-env` files with prompts.
  - Added `.secrets` and `.ci-env` to `.gitignore` automatically.
  - Added `-v`/`--verbose`, `-q`/`--quiet`, `--insecure-secrets` flags to all CI commands.
  - Added `-s`/`--secret` and `--var` inline flags to all CI commands.
  - Changed CI default to Docker/act; added `-l`/`--local` flag for local execution.
  - Release v1.10.2: Verified secure release workflow with env token
  - Release v1.10.3: Fixed `lich ci` command argument order for `act` (removed extra 'push')
  - Release v1.10.4: Fixed corrupt workflow files in `upgrade` command (template rendering) and fixed CI logging.
  - Release v1.10.5: Added missing `.eslintrc.json` to admin template to prevent CI interactive prompts.
  - Release v1.10.6: Expanded `.eslintrc.json` fix to web and landing templates.
  - Release v1.10.7: Added "Smart File Injection" to `lich upgrade` to safely add missing config files to existing apps.
  - Release v1.11.0: Added `lich doctor` command for project health checks.
  - Created separate workflow files: `ci-backend.yml`, `ci-web.yml`, `ci-admin.yml`, `ci-landing.yml`.
  - Updated `lich ci` commands to run their specific workflow files.
  
- 2026-01-09 - Deploy System Implementation
  - Created new `lich deploy setup` command with interactive configuration
  - Added SSH config and manual connection support
  - Created `lich deploy stage <component>` and `lich deploy prod <component>` commands
  - Supports `--version` tag for deploying specific releases
  - Saves config to `.lich/deploy.yml`
  - Auto-generates Ansible playbooks when missing
  - Added component validation (only backend/web/admin/landing allowed)
  - Added live stdout streaming for real-time Ansible output
  - Added GITHUB_TOKEN loading from `.secrets` file for private repos
  - Added git repo URL and private repo configuration to setup flow
  - Updated MCP tools (ci.py, ops.py) with new commands and flags
  - Updated site-docs: ci.md, ci.fa.md, deploy.md, deploy.fa.md
  - Fixed missing `.github/workflows` in `lich upgrade` sync targets
  - Bumped version to 1.10.1 and updated CHANGELOG.md

## 2026-01-17 - Production Deployment Learnings from EmberBoard

Applied learnings from EmberBoard production deployment to Lich Framework:

### Changes Applied
1. **Rate Limiter X-Forwarded-For Fix** (`template/.../api/middleware/rate_limit.py`)
   - Added X-Forwarded-For header parsing for proper client IP detection behind Traefik/Nginx
   - Without this fix, all traffic appears to come from proxy IP, triggering global rate limits

2. **Logout Page Template** (`template/.../apps/web/src/app/logout/page.tsx`)
   - Added missing logout page that clears tokens and redirects to login
   - Prevents 404 when clicking "Logout" in sidebar

### Documented Learnings (for future template updates)
- **`traefik.docker.network` label**: Required on all services exposed via Traefik when using multiple networks
- **Next.js HOSTNAME env**: Add `ENV HOSTNAME="0.0.0.0"` to Dockerfiles for proper health checks
- **Build Args for URLs**: Next.js needs `ARG NEXT_PUBLIC_API_URL` before `npm run build` in Dockerfile
- **Admin Port 3002**: Use different port from web app to avoid conflicts
- **Multi-environment structure**: Separate docker-compose.{env}.yml and .env.{env} files

### Why These Changes
- EmberBoard production deployment had multiple issues:
  - 502 errors from Traefik routing confusion
  - 429 rate limit blocking all users (saw proxy IP)
  - 404 on logout page
  - localhost links in production
- These fixes are now baked into Lich templates for future projects.

## 2026-01-18 - Template Variable Fix (v1.12.10)

### Bug Fixed
- **`lich init` failing when `task_runner=temporal`**: Template files were using the old variable name `cookiecutter.use_temporal == 'yes'` instead of the new `cookiecutter.task_runner == 'temporal'`.

### Files Fixed
1. `template/{{cookiecutter.project_slug}}/agentlog.md` - Line 26
2. `template/hooks/post_gen_project.py` - Line 88
3. `template/{{cookiecutter.project_slug}}/docker-compose.yml` - Line 153
4. `template/{{cookiecutter.project_slug}}/QUICK_START.md` - Line 60

### Root Cause
The `cookiecutter.json` was changed to use `task_runner` with values `['none', 'temporal', 'celery']` but the template files still referenced the old boolean `use_temporal` variable.

## 2026-01-18 - Template Variable Fix v2 (v1.12.11)

### Additional File Fixed
- **`.env.example` Line 69**: Was still using `cookiecutter.use_temporal == 'yes'` instead of `cookiecutter.task_runner == 'temporal'`.

This file was missed in the v1.12.10 fix. Now all template files correctly use `task_runner` variable.



## 2026-01-21T14:15 — v1.12.13 BUGFIX: Token Exposure Fix

### WHAT
- Fixed bug in `cli/src/lich/commands/ci_utils.py`
- Removed automatic `-s GITHUB_TOKEN=...` injection in `run_act_workflow()`

### WHY
- Lich was adding the token directly to the command line, exposing it in logs
- The `.actrc` file already has `--secret-file=.secrets` which provides the token securely

### FILES
- `cli/src/lich/commands/ci_utils.py` - removed lines 301-304
- `cli/pyproject.toml` - version bump to 1.12.13


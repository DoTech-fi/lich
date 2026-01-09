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
  - Bumped version to 1.10.0 and updated CHANGELOG.md

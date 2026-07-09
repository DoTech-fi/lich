# Lich v1 Hardening — Design Spec

**Date:** 2026-07-10
**Status:** Approved (brainstormed with Babak)
**Goal:** Take Lich v1 from 6.5/10 to 10/10 production quality across all three layers: CLI, MCP server, and generated template.
**Executor:** Claude Sonnet, following a bite-sized implementation plan with per-task verification.

## Context

A full multi-agent code review (2026-07-09) scored the framework 6.5/10:

- Architecture (template): 8/10 — hexagonal architecture is genuinely implemented
- CLI code quality: 6/10 — good Typer structure, heavy duplication, oversized functions
- Security: 4/10 — shell injection, path injection, default secrets
- Tests: 5/10 — 80 tests, 5 currently failing, 8/24 command modules covered
- MCP server: 5/10 — 51 sync tools (claim says 47), no input validation, no returncode checks
- Repo hygiene/DX: 8/10 — 5 CI workflows, changelog, mkdocs

## Goals

1. No known security vulnerabilities in any layer.
2. Fully green CI on Python 3.10/3.11/3.12 with an enforced coverage gate (80%).
3. A golden-path e2e test proving `lich new` produces a working project (compose up, healthchecks, generated tests pass).
4. Public-PyPI-grade releases: each phase ships as its own version with changelog.

## Non-Goals

- Any Lich v2 feature (TUI, BYOA AI adapter, smart codegen) — separate spec: `2026-04-14-lich-v2-design.md`.
- Template redesign, new databases, new auth strategies, new generators.
- Windows-specific support work.

## Approach: Risk-Phased Releases

Four independently releasable phases, ordered by risk. If work stops mid-way, everything already shipped is strictly better than before.

| Phase | Version | Theme |
|-------|---------|-------|
| 1 | v1.13.0 | Security |
| 2 | v1.13.1 | Correctness |
| 3 | v1.14.0 | Quality & coverage |
| 4 | v1.15.0 | Gates & golden path e2e |

---

## Phase 1 — Security Sprint (v1.13.0)

### CLI

- **Fix shell injection** in `_verify_github_access` (`cli/src/lich/commands/deploy.py:189`): remove `shell=True`, use list-based subprocess: `["ssh", "-i", key_path, "-o", "StrictHostKeyChecking=accept-new", "-T", git_host]`.
- **New module `cli/src/lich/commands/_shell.py`** with two helpers used by all deploy/ci/git subprocess calls:
  - `run_local(cmd: list[str], cwd=None, timeout=None) -> tuple[int, str]` — never uses `shell=True`.
  - `run_remote(host: str, script: str, **kwargs) -> tuple[int, str]` — every interpolated variable must pass through `shlex.quote()`; provide `quote()` re-export so call sites build quoted scripts.
- **Input validation** at prompt/argument boundaries:
  - `deploy_path`: must match `^[/a-zA-Z0-9._-]+$` (no shell metacharacters, no spaces).
  - `git_url`: must be a valid https or ssh git URL (regex allowlist).
  - All `lich make <name>` identifiers: must match `^[A-Za-z_][A-Za-z0-9_]*$` before any f-string template interpolation (closes the f-string injection in `make.py`).
- **Secrets hygiene**: `lich ci setup` and `lich deploy setup` verify `.secrets` is in `.gitignore`; append it and warn if missing.

### Template

- **Startup secret guard** in `template/.../backend/pkg/config/settings.py`: if `environment == "production"` and any secret contains `"change-me"`, raise at startup with a clear error. App must not boot.
- **Admin password**: remove `admin_password: "admin"` default from `cookiecutter.json`; `hooks/post_gen_project.py` generates a random password (`secrets.token_urlsafe`) and prints it once.
- **OAuth state parameter**: add `state` generation/validation to the Google OAuth flow in `backend/api/http/auth.py` (CSRF protection).
- **Traefik**: remove `--api.insecure=true` from the default `docker-compose.yml` (keep only under a dev profile/override).

### MCP

- Apply the same identifier validation to tool arguments (`lich_make_*`, `lich_migration_create`, ...).
- Bound `lich_secret_generate(length, count)`: length ≤ 256, count ≤ 20.

### Test discipline

Every fix lands with a failing test first (TDD) — e.g. injection-string tests for `deploy_path`, identifier tests for `make`.

---

## Phase 2 — Correctness Sprint (v1.13.1)

- **Fix 5 failing tests** (currently red locally):
  - `test_all_mcp_tools_registered`: update `EXPECTED_TOOL_COUNT` from 47 to the real registered count (51), derived from the registry rather than hardcoded where possible.
  - `test_ops_tools_exist`, `test_ci_tools_exist`: align expected tool lists with implementation. `lich_ci_all` is expected by tests but not implemented — decide: implement it (runs web+admin+landing sequentially) — implement, since docs mention it.
  - `test_version_with_history_flag`: fix the version history flag behavior or test.
- **Brand claim accuracy**: update "47 MCP tools" to the real count everywhere: `README.md`, docs, mkdocs pages, and the BabakOS vault note.
- **Keycloak auth bug** (`template/.../internal/services/auth_deps.py:78-84`): auto-created Keycloak users must not construct `CreateUserRequest` with a missing password — add a dedicated creation path (random internal password or password-less entity constructor for external-auth users).
- **tsx Jinja bug**: `.tsx` is in `_copy_without_render` but `AuthContext.tsx` contains Jinja conditionals that silently never render. Fix by moving conditionals out of the file: ship per-strategy variants (e.g. `AuthContext.jwt.tsx`, `AuthContext.keycloak.tsx`) and have `post_gen_project.py` select/rename the right one.
- **MCP returncode handling**: `run_lich_command()` checks `res.returncode` and prefixes output with `ERROR (exit N):` on failure.
- **Rate limiter memory leak** (`template/.../api/middleware/rate_limit.py`): evict entries older than the window on each request (or periodic cleanup).
- **Template test fix**: `test_user_service.py` fixture passes `mock_user_repo` but the constructor expects `user_repository` — align them so generated tests actually run.
- **DB session semantics** (`template/.../adapters/db/connection.py`): only commit on success; rollback on exception (explicit try/except/rollback/raise in the session dependency).

---

## Phase 3 — Quality Sprint (v1.14.0)

### CLI refactor

- **Extract `cli/src/lich/commands/common.py`**: single implementations of `_check_lich_project()` (currently 8 copies), `_run_command()` (4 copies), `_download_template()` / `_get_local_template_path()` (2 copies), `_check_tool_installed()` (2 copies). All modules import from it.
- **Break up oversized functions** (target: no function > 80 lines): `deploy_init` (244), `deploy_setup` (212), `upgrade_project` (201), `ci_setup` (180).
- **Factory for `ci_web`/`ci_admin`/`ci_landing`** (95% identical) — one parameterized function.
- **Exception hygiene**: replace bare `except Exception` (20+ sites) with specific exceptions; no silent swallowing — always print or log.

### MCP refactor

- **Module-level tools**: move tool functions out of `register_*_tools()` closures to module level; register via explicit loop/decorator. Makes every tool unit-testable.
- **Async long-running tools**: `lich_deploy_*`, `lich_ci_*`, `lich_migration_*`, `lich_backup` become `async def` using `asyncio.create_subprocess_exec` (never shell).
- **Shared validation module** used by both CLI and MCP.

### Typing & coverage

- Type hints on 100% of public functions; add `mypy` (lenient config to start) to CI.
- Coverage from ~33% of command modules to **80% overall**, priority order: `deploy.py` (dry-run/mocked SSH), `ci.py`, `upgrade.py`, `secret.py`, `git.py`, `backup.py`, `lint.py`, `security.py`, `dev.py`, `doctor.py`, `shell.py`, `test.py`, `middleware.py`, `production_ready.py`.
- MCP: functional tests for every tool (mock subprocess; assert command construction and error paths).

---

## Phase 4 — Gates & Golden Path (v1.15.0)

- **Golden-path e2e** (new CI workflow, `e2e.yml`, runs on release PRs + nightly):
  1. `pip install` the CLI from the repo.
  2. `lich new` with default answers (postgres + jwt_builtin) via cookiecutter `--no-input`.
  3. `docker compose up -d` in the generated project; wait for healthchecks.
  4. Run the generated backend test suite inside the container; hit `/health` and auth register/login endpoints.
  5. Teardown. Second matrix job: mongodb + no-auth combo.
- **Security scanning in CI**: `bandit -r cli/src` and `pip-audit` as required checks.
- **Coverage gate**: `pytest --cov --cov-fail-under=80` enforced in `ci.yml` (all Python versions run tests; coverage gate on 3.12).
- **MCP protocol smoke test**: spawn `lich mcp` over stdio, perform JSON-RPC `initialize` + `tools/list`, call one read-only tool (`lich_routes`), assert clean JSON.
- **Docs refresh**: README badges (CI, coverage, PyPI), security policy (`SECURITY.md`), updated tool count and feature docs.

---

## Sonnet Execution Model

The implementation plan (written next, via the writing-plans skill) must be structured for execution by Claude Sonnet:

- **Bite-sized tasks** (one concern each, ~2–5 min): exact file paths, exact expected code, and a verification command per task (`pytest tests/test_x.py -k name`, `grep -c ...`, etc.).
- **TDD order encoded in the plan**: each task pair is "write failing test" → "make it pass".
- **One branch + PR per phase**; phase ends with: full test suite green, changelog entry, version bump.
- **Review checkpoints**: human/senior review at the end of each phase before release.

## Error Handling Philosophy

- CLI: specific exceptions, user-friendly Rich messages, non-zero exit codes.
- MCP: never raise across the protocol boundary — return structured error strings with exit codes.
- Template: fail fast at startup for config errors; fail safe at request time.

## Definition of Done (per the approved gates)

1. CI green on 3.10/3.11/3.12.
2. `--cov-fail-under=80` passes.
3. `bandit` + `pip-audit` clean (or explicitly triaged).
4. Golden-path e2e green for both matrix combos.
5. MCP protocol smoke test green; tool count claim matches reality everywhere.
6. All review findings from 2026-07-09 fixed or explicitly waived in the decisions log.

## Decisions Log

- 2026-07-10: Scope = v1 bulletproof (not v2), audience = public PyPI + DoTech brand, all 3 layers, done = measurable gates + golden-path e2e. Approach A (risk-phased releases) chosen over layer-by-layer and big-bang.
- 2026-07-10: `lich_ci_all` will be implemented (not deleted from tests).
- 2026-07-10: tsx Jinja fix via per-strategy file variants selected in post_gen hook (keeps `.tsx` unrendered by Jinja).

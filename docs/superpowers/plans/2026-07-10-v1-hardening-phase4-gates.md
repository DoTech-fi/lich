# Lich v1 Hardening — Phase 4: Gates & Golden Path (v1.15.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove `lich new` produces a working project via a golden-path e2e CI workflow, and enforce security scanning, a coverage gate, and an MCP protocol smoke test as required checks.

**Architecture:** A new `e2e.yml` workflow generates a project with cookiecutter `--no-input`, boots its infra with docker compose, builds and runs the generated backend image on the compose network, and exercises health + auth endpoints. A local runner script mirrors it for pre-CI testing. `ci.yml` gains bandit/pip-audit and a `--cov-fail-under=80` gate. A protocol-level test talks real JSON-RPC over stdio to the MCP server.

**Tech Stack:** GitHub Actions, docker compose, cookiecutter CLI, bandit, pip-audit, pytest + pytest-asyncio, `mcp` Python SDK (already a runtime dependency).

**Branch:** `hardening/phase4-gates` (from main, after Phases 1–3 are merged).

**Prerequisites:** Phases 1–3 merged. Phase 4 assumes: template test fixture bug fixed (Phase 2), secret startup guard exists but only blocks `ENVIRONMENT=production` (Phase 1), tool-count claims already corrected (Phase 2).

**Verified facts this plan relies on (do not re-derive):**
- Generated endpoints: `GET /api/health`, `POST /api/v1/auth/register` (fields: `email`, `username`, `password`), `POST /api/v1/auth/login` (fields: `email`, `password`). Router mounted with `prefix="/api"` in `backend/main.py:101`.
- Compose file has **no backend service** — only traefik/postgres|mongodb/redis/adminer(+optional). Service names: `postgres`, `mongodb`, `redis`. Networks: `internal_net`, `public_net` → runtime names `<slug>_internal_net` etc. Container names: `<slug>_postgres`, `<slug>_mongodb`.
- Backend settings env vars (pydantic BaseSettings): `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `MONGODB_HOST`, `MONGODB_USER`, `MONGODB_PASSWORD`, `MONGODB_DB`, `REDIS_HOST`, `JWT_SECRET_KEY`, `SECRET_KEY`, `ENVIRONMENT`. Compose DB defaults: user `app`, password `app_secret`, db name = project slug.
- `init_db()` runs `Base.metadata.create_all` at startup — no migration step needed for a fresh DB.
- Generated `backend/requirements.txt` includes pytest/pytest-asyncio/pytest-cov — tests can run inside the image.
- MCP server starts with `lich serve` (or `python -m lich serve`); banner goes to stderr, protocol to stdout. CLI pyproject already depends on `mcp>=0.1.0`.
- cookiecutter defaults: `project_type=saas_platform`, `is_microservice=no`, `include_admin_panel=yes`, `landing_backend=static_only`, `task_runner=none`, `use_tls=no`, `build_strategy=docker` — all fine for e2e; only `database`/`auth_strategy`/`use_redis` are overridden per job.

---

### Task 1: Fix generated backend Dockerfile healthcheck (blocks e2e)

The runtime image is `python:3.12-slim` and never installs `curl`, but the HEALTHCHECK calls `curl` — so every generated container reports `unhealthy` forever. Replace with a Python stdlib check. There is no unit test for a Dockerfile; verification is `grep` now and the e2e run in Task 2.

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/backend/Dockerfile:55-56`

- [ ] **Step 1: Replace the curl healthcheck**

Change lines 55–56 from:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

to:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health', timeout=5).status==200 else 1)" || exit 1
```

(Also fixes the wrong path: the health route is `/api/health`, not `/health`.)

- [ ] **Step 2: Verify**

Run: `grep -c "curl" "template/{{cookiecutter.project_slug}}/backend/Dockerfile"`
Expected: `0`

Run: `grep -c "api/health" "template/{{cookiecutter.project_slug}}/backend/Dockerfile"`
Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add "template/{{cookiecutter.project_slug}}/backend/Dockerfile"
git commit -m "fix(template): Dockerfile healthcheck used curl (absent in slim image) and wrong path"
```

---

### Task 2: Local golden-path e2e runner script

One script that both developers and CI use, so the workflow YAML stays thin and the e2e logic is testable locally. It takes `database` and `auth_strategy` as arguments.

**Files:**
- Create: `scripts/e2e_local.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# Golden-path e2e: generate a project with the local template, boot infra,
# build+run the backend image, run its tests, hit health/auth endpoints.
# Usage: scripts/e2e_local.sh <postgresql|mongodb> <jwt_builtin|none>
set -euo pipefail

DATABASE="${1:-postgresql}"
AUTH="${2:-jwt_builtin}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKDIR="$(mktemp -d)"
SLUG="e2e_app"
BACKEND_CONTAINER="e2e_backend"

cleanup() {
  echo "--- cleanup ---"
  docker rm -f "$BACKEND_CONTAINER" >/dev/null 2>&1 || true
  if [ -d "$WORKDIR/$SLUG" ]; then
    (cd "$WORKDIR/$SLUG" && docker compose down -v --remove-orphans >/dev/null 2>&1) || true
  fi
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

echo "=== 1. Generate project (database=$DATABASE auth=$AUTH) ==="
python -m cookiecutter "$REPO_ROOT/template" --no-input -o "$WORKDIR" \
  project_name="E2E App" \
  database="$DATABASE" \
  auth_strategy="$AUTH" \
  use_redis="yes"
cd "$WORKDIR/$SLUG"

echo "=== 2. Boot infra (db + redis only; skip traefik/adminer) ==="
if [ "$DATABASE" = "postgresql" ]; then
  DB_SERVICE="postgres"
else
  DB_SERVICE="mongodb"
fi
docker compose up -d "$DB_SERVICE" redis

echo "=== 3. Wait for DB healthcheck (timeout 120s) ==="
for i in $(seq 1 60); do
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' "${SLUG}_${DB_SERVICE}" 2>/dev/null || echo starting)"
  [ "$STATUS" = "healthy" ] && break
  [ "$i" = "60" ] && { echo "DB never became healthy"; docker compose logs "$DB_SERVICE"; exit 1; }
  sleep 2
done
echo "DB healthy."

echo "=== 4. Build backend image ==="
docker build -t e2e-backend ./backend

BACKEND_ENV=(-e ENVIRONMENT=development -e JWT_SECRET_KEY=e2e-test-secret -e SECRET_KEY=e2e-test-secret -e REDIS_HOST=redis)
if [ "$DATABASE" = "postgresql" ]; then
  BACKEND_ENV+=(-e DB_HOST=postgres -e DB_USER=app -e DB_PASSWORD=app_secret -e DB_NAME="$SLUG")
else
  BACKEND_ENV+=(-e MONGODB_HOST=mongodb -e MONGODB_USER=app -e MONGODB_PASSWORD=app_secret -e MONGODB_DB="$SLUG")
fi

echo "=== 5. Run generated backend tests inside the image ==="
docker run --rm --network "${SLUG}_internal_net" "${BACKEND_ENV[@]}" \
  e2e-backend python -m pytest -v --tb=short

echo "=== 6. Start backend container ==="
docker run -d --name "$BACKEND_CONTAINER" --network "${SLUG}_internal_net" \
  -p 8000:8000 "${BACKEND_ENV[@]}" e2e-backend

echo "=== 7. Wait for /api/health (timeout 60s) ==="
for i in $(seq 1 30); do
  if curl -fsS http://localhost:8000/api/health >/dev/null 2>&1; then break; fi
  [ "$i" = "30" ] && { echo "backend never became healthy"; docker logs "$BACKEND_CONTAINER"; exit 1; }
  sleep 2
done
curl -fsS http://localhost:8000/api/health
echo

if [ "$AUTH" = "jwt_builtin" ]; then
  echo "=== 8. Register + login ==="
  REGISTER_CODE="$(curl -s -o /tmp/e2e_register.json -w '%{http_code}' \
    -X POST http://localhost:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email":"e2e@test.com","username":"e2euser","password":"Passw0rdX"}')"
  [ "$REGISTER_CODE" = "201" ] || { echo "register failed ($REGISTER_CODE):"; cat /tmp/e2e_register.json; exit 1; }

  LOGIN_CODE="$(curl -s -o /tmp/e2e_login.json -w '%{http_code}' \
    -X POST http://localhost:8000/api/v1/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"e2e@test.com","password":"Passw0rdX"}')"
  [ "$LOGIN_CODE" = "200" ] || { echo "login failed ($LOGIN_CODE):"; cat /tmp/e2e_login.json; exit 1; }
  grep -q "access_token" /tmp/e2e_login.json || { echo "no access_token in login response"; exit 1; }
  echo "register+login OK"
fi

echo "=== E2E PASSED (database=$DATABASE auth=$AUTH) ==="
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x scripts/e2e_local.sh && ls -l scripts/e2e_local.sh`
Expected: `-rwxr-xr-x ... scripts/e2e_local.sh`

- [ ] **Step 3: Install cookiecutter and run the postgres+jwt path locally**

Run: `pip install cookiecutter && ./scripts/e2e_local.sh postgresql jwt_builtin`
Expected: ends with `=== E2E PASSED (database=postgresql auth=jwt_builtin) ===`, exit code 0.
If it fails, fix the template/script issue it reveals before continuing — that is the point of this task. Do not proceed with a red e2e.

- [ ] **Step 4: Run the mongodb+none path locally**

Run: `./scripts/e2e_local.sh mongodb none`
Expected: ends with `=== E2E PASSED (database=mongodb auth=none) ===`, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/e2e_local.sh
git commit -m "feat(e2e): golden-path local runner (generate -> compose -> test -> health/auth)"
```

---

### Task 3: Golden-path e2e CI workflow

**Files:**
- Create: `.github/workflows/e2e.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: E2E Golden Path

on:
  pull_request:
    branches: [main]
    paths:
      - "cli/**"
      - "template/**"
      - "scripts/e2e_local.sh"
      - ".github/workflows/e2e.yml"
  schedule:
    - cron: "0 3 * * *"  # nightly 03:00 UTC
  workflow_dispatch:

jobs:
  golden-path:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - database: postgresql
            auth: jwt_builtin
          - database: mongodb
            auth: none
    name: e2e (${{ matrix.database }} + ${{ matrix.auth }})
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install lich CLI + cookiecutter
        run: |
          python -m pip install --upgrade pip
          pip install -e ./cli
          pip install cookiecutter

      - name: Run golden path
        run: ./scripts/e2e_local.sh ${{ matrix.database }} ${{ matrix.auth }}
```

- [ ] **Step 2: Validate YAML locally**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/e2e.yml')); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/e2e.yml
git commit -m "ci: golden-path e2e workflow (postgres+jwt, mongodb+none)"
```

---

### Task 4: Bandit + pip-audit security scanning in CI

**Files:**
- Modify: `cli/pyproject.toml` (add `[tool.bandit]` section at end of file)
- Modify: `.github/workflows/ci.yml` (add `security` job after the `lint` job)

- [ ] **Step 1: Add bandit config to cli/pyproject.toml**

Append at the end of `cli/pyproject.toml`:

```toml
[tool.bandit]
targets = ["src"]
# B603/B607: subprocess without shell — all call sites use list args and
# validated input via commands/_shell.py (Phase 1). Triaged 2026-07-10.
skips = ["B603", "B607"]
```

- [ ] **Step 2: Run bandit locally to establish a clean baseline**

Run: `pip install bandit && cd cli && bandit -c pyproject.toml -r src && cd ..`
Expected: `No issues identified.` (exit 0)
If findings appear: fix real issues; only add a skip with a written justification comment for false positives.

- [ ] **Step 3: Run pip-audit locally**

Run: `pip install pip-audit && cd cli && pip-audit --skip-editable . ; cd ..`
Expected: `No known vulnerabilities found` (exit 0). If a dependency is vulnerable, bump its floor in `cli/pyproject.toml` dependencies and re-run.

- [ ] **Step 4: Add the security job to ci.yml**

Append to `.github/workflows/ci.yml` (same indentation level as `test:` and `lint:`):

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install scanners
        run: pip install bandit pip-audit

      - name: Bandit (static security analysis)
        run: |
          cd cli
          bandit -c pyproject.toml -r src

      - name: pip-audit (dependency vulnerabilities)
        run: |
          cd cli
          pip install -e .
          pip-audit --skip-editable .
```

- [ ] **Step 5: Validate YAML**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add cli/pyproject.toml .github/workflows/ci.yml
git commit -m "ci: add bandit + pip-audit security scanning as required checks"
```

---

### Task 5: Coverage gate (fail under 80%)

**Files:**
- Modify: `.github/workflows/ci.yml:35-40` (the existing "Run tests with coverage" step)
- Modify: `cli/pyproject.toml` (add coverage dev dependency)

- [ ] **Step 1: Add pytest-cov to dev extras**

In `cli/pyproject.toml`, extend `[project.optional-dependencies] dev`:

```toml
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.14.0",
    "pytest-cov>=4.1.0",
]
```

- [ ] **Step 2: Verify current coverage locally**

Run: `cd cli && pip install -e ".[dev]" && pytest --cov=lich --cov-report=term | tail -5 && cd ..`
Expected: `TOTAL ... 80%` or higher (Phase 3 raised coverage). Note the number.
If below 80: STOP — Phase 3 is incomplete. Report back rather than lowering the gate.

- [ ] **Step 3: Replace the coverage step in ci.yml**

Change the existing step (lines 35–40):

```yaml
      - name: Run tests with coverage
        if: matrix.python-version == '3.12'
        run: |
          cd cli
          pip install pytest-cov
          pytest --cov=lich --cov-report=xml
```

to:

```yaml
      - name: Coverage gate (>= 80%)
        if: matrix.python-version == '3.12'
        run: |
          cd cli
          pytest --cov=lich --cov-report=term --cov-report=xml --cov-fail-under=80
```

(`pip install pytest-cov` is dropped because it is now in the dev extras installed earlier in the job.)

- [ ] **Step 4: Validate YAML and run gate locally**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('OK')" && cd cli && pytest --cov=lich --cov-fail-under=80 -q | tail -3 && cd ..`
Expected: `OK`, then `Required test coverage of 80% reached.` and all tests passing.

- [ ] **Step 5: Commit**

```bash
git add cli/pyproject.toml .github/workflows/ci.yml
git commit -m "ci: enforce 80% coverage gate on Python 3.12"
```

---

### Task 6: MCP protocol smoke test

Real JSON-RPC over stdio against the actual server process — proves the wire protocol works and stdout stays clean, which unit tests cannot. Uses the `mcp` SDK client (already a runtime dependency of the CLI).

**Files:**
- Create: `cli/tests/test_mcp_protocol.py`

- [ ] **Step 1: Write the test**

```python
"""
Protocol-level smoke test: spawn the real MCP server over stdio and speak
JSON-RPC to it. Guards against stdout pollution and registration regressions
that in-process tests cannot catch.
"""
import asyncio
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable,
    args=["-m", "lich", "serve"],
)

# Keep in sync with test_mcp_server.py's canonical count.
MIN_EXPECTED_TOOLS = 51


async def _run_smoke() -> tuple[list[str], str]:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            call_result = await session.call_tool("lich_routes", {"verbose": False})
            text = call_result.content[0].text
            return tool_names, text


@pytest.mark.asyncio
async def test_mcp_stdio_protocol_smoke():
    tool_names, routes_text = await asyncio.wait_for(_run_smoke(), timeout=60)

    assert len(tool_names) >= MIN_EXPECTED_TOOLS
    assert "lich_routes" in tool_names
    assert "lich_make_entity" in tool_names

    # Outside a lich project the tool returns an error string --
    # what matters here is that the call completed over the protocol
    # and returned text, not that routes exist.
    assert isinstance(routes_text, str)
    assert len(routes_text) > 0
```

- [ ] **Step 2: Run the test**

Run: `cd cli && pytest tests/test_mcp_protocol.py -v && cd ..`
Expected: `1 passed`. Typical failure modes and their meaning:
- `TimeoutError` → server never finished initialize; check that the startup banner goes to stderr (`mcp/server.py` prints to stderr — any new print to stdout breaks the protocol).
- `ImportError` on `mcp.client` → the installed `mcp` package is too old; raise the floor in `cli/pyproject.toml` to `"mcp>=1.0.0"` and reinstall.

- [ ] **Step 3: Run the full suite to confirm no interference**

Run: `cd cli && pytest -q | tail -3 && cd ..`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add cli/tests/test_mcp_protocol.py
git commit -m "test: MCP stdio protocol smoke test (initialize, tools/list, tools/call)"
```

---

### Task 7: SECURITY.md

**Files:**
- Create: `SECURITY.md`

- [ ] **Step 1: Write the policy**

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.15.x  | ✅                 |
| 1.13.x – 1.14.x | ✅ security fixes only |
| < 1.13  | ❌ (upgrade — versions before 1.13.0 contain known vulnerabilities fixed in the 2026-07 hardening releases) |

## Reporting a Vulnerability

Please **do not open a public GitHub issue** for security vulnerabilities.

Email **babak@dotech.fi** with:
- A description of the vulnerability and its impact
- Steps to reproduce (a minimal PoC helps)
- The version you tested (`lich version`)

You will get an acknowledgement within **72 hours** and a status update within
**14 days**. Once a fix ships, we credit reporters in the changelog unless you
prefer to stay anonymous.

## Scope

- `lich` CLI (PyPI package, `cli/`)
- The Lich MCP server (`lich serve`)
- The project template (`template/`) — vulnerabilities in freshly generated
  projects count; vulnerabilities you introduce after generation do not.

## Hardening Baseline

Since v1.13.0, all subprocess calls use list arguments (no `shell=True`),
user input is validated at CLI/MCP boundaries, and generated projects refuse
to start in production with placeholder secrets. CI runs bandit and pip-audit
on every PR.
```

- [ ] **Step 2: Verify**

Run: `test -s SECURITY.md && head -1 SECURITY.md`
Expected: `# Security Policy`

- [ ] **Step 3: Commit**

```bash
git add SECURITY.md
git commit -m "docs: add SECURITY.md with disclosure policy"
```

---

### Task 8: README badges + claim verification

**Files:**
- Modify: `README.md:5-7` (badge block)

- [ ] **Step 1: Replace the stale badge block**

The current version badge is hardcoded to `1.3.1` (README.md:7) — years stale. Replace lines 5–7 with dynamic badges (no coverage badge: it needs a third-party service/gist token — the CI gate itself is the guarantee, revisit if a Codecov account is set up later):

```markdown
[![CI](https://github.com/DoTech-fi/lich/actions/workflows/ci.yml/badge.svg)](https://github.com/DoTech-fi/lich/actions/workflows/ci.yml)
[![E2E](https://github.com/DoTech-fi/lich/actions/workflows/e2e.yml/badge.svg)](https://github.com/DoTech-fi/lich/actions/workflows/e2e.yml)
[![PyPI](https://img.shields.io/pypi/v/lich)](https://pypi.org/project/lich/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
```

- [ ] **Step 2: Verify no stale tool-count claims survived Phase 2**

Run: `grep -rn "47 MCP\|47 tools" README.md docs/ site-docs/ mkdocs.yml 2>/dev/null || echo CLEAN`
Expected: `CLEAN`. If matches appear, update each to the canonical count from `cli/tests/test_mcp_server.py` (51 after Phase 2) and include those files in this commit.

- [ ] **Step 3: Verify no hardcoded version badge remains**

Run: `grep -c "version-1" README.md`
Expected: `0`

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: dynamic CI/E2E/PyPI badges, drop stale hardcoded version badge"
```

---

### Task 9: Phase completion — changelog, version bump, release prep

**Files:**
- Modify: `CHANGELOG.md` (new entry at top)
- Modify: `cli/pyproject.toml:7` (`version = "1.15.0"`)
- Modify: `template/cookiecutter.json` (`"_lich_version": "1.15.0"`)

- [ ] **Step 1: Full local verification**

Run: `cd cli && pytest -q | tail -3 && bandit -c pyproject.toml -r src -q && cd .. && ./scripts/e2e_local.sh postgresql jwt_builtin`
Expected: all tests pass, bandit clean, e2e passes.

- [ ] **Step 2: Bump versions**

- `cli/pyproject.toml`: `version = "1.15.0"`
- `template/cookiecutter.json`: `"_lich_version": "1.15.0"`

Run: `grep '"_lich_version"' template/cookiecutter.json && grep '^version' cli/pyproject.toml`
Expected: both show `1.15.0`.

- [ ] **Step 3: Add changelog entry**

Prepend to `CHANGELOG.md` (match the existing entry format in the file):

```markdown
## [1.15.0] - 2026-07-10

### Added
- Golden-path e2e workflow: generates a project (postgres+jwt and mongodb+none),
  boots it with docker compose, runs its test suite, and exercises health/auth endpoints.
- `scripts/e2e_local.sh` — run the golden path locally.
- MCP stdio protocol smoke test (initialize, tools/list, tools/call).
- Security scanning in CI: bandit + pip-audit as required checks.
- Coverage gate: CI fails under 80% line coverage.
- `SECURITY.md` vulnerability disclosure policy.

### Fixed
- Generated backend Dockerfile healthcheck used `curl` (absent in the slim image)
  and the wrong path (`/health` instead of `/api/health`).

### Changed
- README badges are now dynamic (CI, E2E, PyPI) instead of a hardcoded version.
```

- [ ] **Step 4: Commit and hand off for release**

```bash
git add CHANGELOG.md cli/pyproject.toml template/cookiecutter.json
git commit -m "chore: release v1.15.0 — gates & golden path"
```

Then open the phase PR. **After merge and green CI:** tag `v1.15.0` on main (`git tag v1.15.0 && git push origin v1.15.0`) — the existing `publish.yml`/`release.yml` workflows handle PyPI publication from the tag. Mark GitHub branch protection to require the new `security` and `e2e` checks.

---

## Self-review notes

- Spec coverage: e2e (Task 2+3), matrix combos (Task 2 steps 3–4, Task 3 matrix), bandit+pip-audit (Task 4), coverage gate (Task 5), MCP protocol smoke (Task 6), docs refresh/SECURITY/badges/tool-count (Tasks 7–8), release (Task 9). Dockerfile healthcheck fix (Task 1) is an addition the spec implies — golden path cannot pass without it.
- Deviation from spec, intentional: spec says "run generated tests inside the container" — done via `docker run --rm ... pytest` against the built image (Task 2 step 5), which also exercises the production Dockerfile; compose itself has no backend service, so adding one was avoided (YAGNI — bigger template change belongs to v2/lich-core).
- Coverage badge explicitly skipped with rationale (Task 8) rather than left as a TODO.

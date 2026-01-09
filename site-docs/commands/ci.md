# lich ci

The `lich ci` command runs CI checks locally using Docker/act or directly.

## Setup

```bash
# First time setup (creates .secrets, .actrc)
lich ci setup
```

## Usage

```bash
# Run with Docker/act (default)
lich ci backend
lich ci web
lich ci admin
lich ci landing

# Run locally without Docker
lich ci backend -l
lich ci web -l
```

## Commands

| Command | Description |
|---------|-------------|
| `lich ci setup` | Setup act, create .secrets file |
| `lich ci backend` | Run backend CI (Python) |
| `lich ci web` | Run web app CI (TypeScript) |
| `lich ci admin` | Run admin panel CI |
| `lich ci landing` | Run landing page CI |

## Options

| Option | Description |
|--------|-------------|
| `-l, --local` | Run locally without Docker |
| `-v, --verbose` | Verbose output |
| `-q, --quiet` | Quiet mode |
| `-s, --secret KEY=VALUE` | Pass secret (repeatable) |
| `--var KEY=VALUE` | Pass variable (repeatable) |
| `--insecure-secrets` | Show secrets in logs |

## Examples

```bash
# Backend with Docker (default)
lich ci backend

# Backend locally (faster for dev)
lich ci backend -l

# Pass secrets inline
lich ci backend -s GITHUB_TOKEN=ghp_xxx

# Pass variables
lich ci backend --var NODE_ENV=test
```

## Workflow Files

Each component has its own workflow file with path-based triggers:

| Component | Workflow | Trigger Path |
|-----------|----------|--------------|
| Backend | `ci-backend.yml` | `backend/**` |
| Web | `ci-web.yml` | `apps/web/**` |
| Admin | `ci-admin.yml` | `apps/admin/**` |
| Landing | `ci-landing.yml` | `apps/landing/**` |

The main `ci.yml` runs all checks manually via GitHub Actions UI.

## Files Created by Setup

| File | Purpose |
|------|---------|
| `.actrc` | act configuration |
| `.secrets` | GitHub token and secrets |
| `.ci-vars` | CI variables (optional) |
| `.ci-env` | Container environment (optional) |

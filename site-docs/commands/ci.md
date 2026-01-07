# lich ci

The `lich ci` command runs CI checks locally before pushing.

## Usage

```bash
# Run all CI checks
lich ci

# Run specific target
lich ci backend
lich ci web
lich ci admin
lich ci landing
```

## What It Checks

### Backend
- **Linting** (ruff/flake8)
- **Type checking** (mypy)
- **Tests** (pytest)
- **Security** (bandit)

### Frontend
- **Linting** (eslint)
- **Type checking** (tsc)
- **Build** (next build)
- **Audit** (npm audit)

## Subcommands

| Command | Description |
|---------|-------------|
| `lich ci` | Run all checks |
| `lich ci backend` | Backend only |
| `lich ci web` | Web app only |
| `lich ci admin` | Admin panel only |
| `lich ci landing` | Landing page only |

## Examples

```bash
# Quick check before commit
lich ci

# Backend changes only
lich ci backend

# Full frontend check
lich ci web
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | One or more checks failed |

## Integration

Add to git pre-push hook:

```bash
#!/bin/sh
lich ci || exit 1
```

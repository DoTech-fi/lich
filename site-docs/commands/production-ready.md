# lich production-ready

The `lich production-ready` command checks if your project is ready for production.

## Usage

```bash
# Run all checks
lich production-ready

# Auto-fix issues
lich production-ready --fix

# JSON output for CI/CD
lich production-ready --json
```

## Check Categories

### 🔒 Security Checks
- Security middlewares enabled
- CORS not wildcard (`*`)
- DEBUG mode disabled
- Secret key ≥32 characters
- JWT secret ≥32 characters
- No hardcoded secrets

### ✨ Quality Checks
- Test coverage ≥80%
- No TODO/FIXME comments
- All .env vars in docker-compose

### ⚙️ Operations Checks
- Docker images use specific tags
- Health check includes DB/Redis
- SSL/HTTPS configured
- Rate limiting enabled
- Backup strategy defined
- Structured logging enabled

## Options

| Option | Description |
|--------|-------------|
| `--fix, -f` | Auto-fix issues where possible |
| `--json, -j` | Output as JSON |

## Auto-Fix

With `--fix`, the command can automatically:

- Generate strong SECRET_KEY
- Generate strong JWT_SECRET
- Set DEBUG=false
- Set SECURITY_ENABLED=true

## Examples

```bash
# Quick check
lich production-ready

# Fix and check again
lich production-ready --fix

# CI/CD integration
lich production-ready --json > readiness-report.json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Production ready! |
| `1` | Not ready, issues found |

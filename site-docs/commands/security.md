# lich security

The `lich security` command runs comprehensive security scans on your project.

## Usage

```bash
# Run all security scans
lich security

# Scan specific target
lich security --target backend
lich security --target frontend
lich security --target docker
lich security --target secrets

# Auto-fix issues where possible
lich security --fix

# JSON output for CI/CD
lich security --json
```

## Security Scans

### Backend Scans
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability check

### Frontend Scans
- **npm audit** - Node.js dependency vulnerabilities

### Secrets Scans
- **GitLeaks** - Detect hardcoded secrets
- **git-secrets** - AWS secret detection

### Docker Scans
- **Trivy** - Container vulnerability scanner

## Options

| Option | Description |
|--------|-------------|
| `--target, -t` | Target to scan: `backend`, `frontend`, `docker`, `secrets` |
| `--fix` | Auto-fix security issues where possible |
| `--json` | Output results as JSON |

## Examples

```bash
# Full security audit
lich security

# Backend only with fixes
lich security --target backend --fix

# CI/CD integration
lich security --json > security-report.json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No critical vulnerabilities |
| `1` | Critical vulnerabilities found |

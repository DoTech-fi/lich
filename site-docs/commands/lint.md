# lich lint

The `lich lint` command runs code linting for your project.

## Usage

```bash
# Lint all code
lich lint

# Lint specific target
lich lint --target backend
lich lint --target frontend

# Auto-fix issues
lich lint --fix
```

## Linters Used

### Backend (Python)
- **Ruff** (preferred) - Fast Python linter
- **Flake8** (fallback) - Python style checker

### Frontend (TypeScript/JavaScript)
- **ESLint** - JavaScript/TypeScript linter

## Options

| Option | Description |
|--------|-------------|
| `--target, -t` | Target: `backend`, `frontend` |
| `--fix` | Auto-fix linting issues |

## Examples

```bash
# Full lint check
lich lint

# Backend with auto-fix
lich lint --target backend --fix

# Frontend only
lich lint --target frontend
```

## Configuration

### Backend
Configure in `pyproject.toml` or `ruff.toml`:

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "W", "I"]
```

### Frontend
Configure in `.eslintrc.js` or `eslint.config.js`.

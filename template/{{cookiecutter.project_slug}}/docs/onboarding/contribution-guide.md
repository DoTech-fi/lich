# Contribution Guide

> راهنمای مشارکت در توسعه {{ cookiecutter.project_name }}

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch

```bash
git checkout -b feature/my-feature
```

## Development Workflow

### 1. Start Development Environment

```bash
./dev-start.sh
```

### 2. Make Your Changes

Follow these guidelines:

#### Backend (Python)
- Follow **Lich Architecture** rules
- Use type hints everywhere
- Write tests for new features
- Run linting before commit:
```bash
cd backend
ruff check .
mypy .
```

#### Frontend (TypeScript)
- Use **TypeScript strict mode**
- Create components in feature folders
- Use CSS Modules for styling
- Run lint before commit:
```bash
cd apps/web
npm run lint
```

### 3. Write Tests

#### Backend
```bash
cd backend
pytest -v
```

#### Frontend
```bash
cd apps/web
npm test
```

### 4. Commit Your Changes

Use conventional commits:

```
feat: add user avatar upload
fix: resolve login timeout issue
docs: update API documentation
refactor: simplify user service
test: add user entity tests
```

### 5. Update agentlog.md

Every change should be logged:

```markdown
## YYYY-MM-DD - Brief Title

**What Changed**: 
- Description of changes

**Why Changed**:
Explanation

**Files Modified**:
- `path/to/file.py` - What changed
```

### 6. Create Pull Request

- Fill in the PR template
- Reference any related issues
- Request review from maintainers

## Code Standards

### Backend

| Rule | Description |
|------|-------------|
| Architecture | Follow Lich (Hexagonal) Architecture |
| Entities | Pure domain models, no external deps |
| Services | Business logic only |
| Ports | Interfaces for external dependencies |
| Adapters | Implementations of ports |
| DTO | Pydantic models for API |

### Frontend

| Rule | Description |
|------|-------------|
| Components | Feature-based organization |
| Styling | CSS Modules only |
| State | Context for global, useState for local |
| API | Use lib/api-client.ts |
| Auth | Use context/AuthContext |

## Security Guidelines

- ❌ Never commit secrets
- ❌ Never use localStorage for tokens
- ✅ Validate all inputs
- ✅ Use parameterized queries
- ✅ Follow OWASP guidelines

## Questions?

Open an issue or contact the maintainers.

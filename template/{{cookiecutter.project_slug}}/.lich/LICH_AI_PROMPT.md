# LICH Framework - AI Prompt

> این فایل قوانین معماری پروژه رو برای AI توضیح میده

## About This Project

این پروژه با **LICH Framework** ساخته شده:
- **L**ayered Architecture (Hexagonal/Ports & Adapters)
- **I**nterface-based Design (Dependency Inversion)
- **C**lean Code Principles (SOLID, DRY, KISS)
- **H**igh Security Standards (OWASP)

## Architecture Rules

### Backend (Lich Architecture)

```
internal/
├── entities/    # Pure domain models (NO external deps)
├── services/    # Business logic (use cases)
├── ports/       # Interfaces (repositories ABC)
├── adapters/    # Implementations (DB, cache, HTTP)
├── dto/         # Request/Response schemas
└── validators/  # Input validation
```

### Allowed Dependencies

```
✅ ALLOWED:
- api → services, dto
- services → entities, ports, dto
- adapters → entities, ports

❌ FORBIDDEN:
- entities → anything
- services → adapters (use ports instead)
```

### Security Rules

1. No hardcoded secrets
2. No localStorage for tokens
3. Validate ALL inputs
4. Parameterized SQL queries
5. Non-root Docker containers

## When AI Generates Code

1. Follow the existing folder structure
2. Use existing patterns as reference
3. Always validate inputs
4. Never expose internal errors to API
5. Update agentlog.md with changes

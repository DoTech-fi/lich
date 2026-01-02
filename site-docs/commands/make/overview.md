# lich make - Overview

The `lich make` command generates code following Lich architecture patterns.

## Why Use Code Generation?

| Benefit | Description |
|---------|-------------|
| ⚡ **Speed** | Create boilerplate in seconds |
| 🎯 **Consistency** | Always follows architecture rules |
| 📁 **Correct Location** | Files go in the right folders |
| ✨ **Best Practices** | Generated code follows patterns |

## Available Generators

| Command | Creates | Location |
|---------|---------|----------|
| [`make entity`](entity.md) | Domain model | `backend/internal/entities/` |
| [`make service`](service.md) | Business logic | `backend/internal/services/` |
| [`make api`](api.md) | API router | `backend/api/http/` |
| [`make dto`](dto.md) | Data transfer objects | `backend/internal/dto/` |
| [`make factory`](factory.md) | Test factory | `backend/tests/factories/` |
| [`make middleware`](middleware.md) | HTTP middleware | `backend/api/middleware/` |
| [`make event`](event.md) | Event class | `backend/internal/events/` |
| [`make listener`](listener.md) | Event listener | `backend/internal/listeners/` |
| [`make job`](job.md) | Background job | `backend/internal/jobs/` |
| [`make policy`](policy.md) | Authorization policy | `backend/internal/policies/` |

## Usage Pattern

```bash
lich make <type> <Name>
```

- `<type>` - What to generate (entity, service, etc.)
- `<Name>` - PascalCase name (e.g., `User`, `OrderItem`)

## Typical Workflow

When adding a new feature, generate in this order:

```bash
# 1. Domain model
lich make entity Product

# 2. Business logic
lich make service Product

# 3. API endpoints
lich make api products

# 4. Request/Response DTOs
lich make dto Product

# 5. Test factory (optional)
lich make factory Product
```

## Getting Help

```bash
lich make --help
lich make entity --help
```

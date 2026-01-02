---
description: Add a new feature to the project (entity + service + API + frontend)
---

# Add Feature Workflow

## Before Starting

1. Read `.lich/AI_CONTEXT.md` to understand the project
2. Read `.lich/rules/backend.md` for backend patterns
3. Read `.lich/rules/frontend.md` for frontend patterns

## Steps

### 1. Create Entity (Pure Domain Model)
```
backend/internal/entities/<feature>.py
```
- Dataclass with domain logic
- No external dependencies
- Include validation methods

### 2. Create Port (Interface)
```
backend/internal/ports/<feature>_repository.py
```
- Abstract base class
- Define CRUD methods
- Return domain entities

### 3. Create Adapter (Implementation)
```
backend/internal/adapters/db/<feature>_repository.py
```
- Implement the port
- Handle DB operations
- Map to/from entities

### 4. Create Service (Business Logic)
```
backend/internal/services/<feature>_service.py
```
- Inject repository via constructor
- Implement use cases
- Raise domain exceptions

### 5. Create DTOs
```
backend/internal/dto/<feature>_requests.py
backend/internal/dto/<feature>_responses.py
```
- Pydantic models
- Validation rules

### 6. Create API Endpoints
```
backend/api/http/<feature>.py
```
- FastAPI router
- Use services
- Return DTOs

### 7. Create Frontend Components
```
apps/web/src/app/<feature>/page.tsx
apps/web/src/app/<feature>/<feature>.module.css
```
- React component
- CSS Module styling
- API integration

### 8. Write Tests
```
backend/tests/test_<feature>_entity.py
backend/tests/test_<feature>_service.py
backend/tests/test_<feature>_api.py
```

### 9. Update Documentation
- Update `agentlog.md`
- Add to QUICK_START if needed

## Checklist

```
[ ] Entity created
[ ] Port defined
[ ] Adapter implemented
[ ] Service with business logic
[ ] DTOs for validation
[ ] API endpoints
[ ] Frontend page
[ ] Tests written
[ ] agentlog.md updated
```

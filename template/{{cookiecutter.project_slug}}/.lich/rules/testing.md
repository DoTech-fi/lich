# Testing & QA Rules

> Progressive testing strategy - write the RIGHT tests at the RIGHT time.

## Core Principles

```
🧪 TEST BEHAVIOR, NOT IMPLEMENTATION
🏃 FAST FEEDBACK
🎯 HIGH COVERAGE ON CRITICAL PATHS
📝 TESTS AS DOCUMENTATION
```

---

## 1. Progressive Testing Strategy

**CRITICAL**: Do NOT write all tests at once. Follow this progression:

### Phase 1 — Development (Active Feature Development)
✅ Unit tests ONLY
- Write with each feature
- Test entities, services, utilities
- Target: 80%+ coverage for business logic

❌ DO NOT write integration tests yet
❌ DO NOT write E2E tests yet

### Phase 2 — Pre-MVP (Core Features Stable)
✅ Integration tests for:
- Authentication flows
- Critical CRUD operations
- Key business workflows

⏸️ E2E tests: Only 1-2 smoke tests

### Phase 3 — Post-MVP (Production Ready)
✅ Full E2E test suite (3-5 flows max)
✅ Comprehensive integration tests
✅ Performance tests if needed

---

## 2. Decision Tree: Should I Write This Test?

```
1. Is this a UNIT test?
   → YES: Write it NOW (cheap, fast, high value)

2. Is this an INTEGRATION test?
   → Is the API/schema stable?
      → YES: write it
      → NO: wait until stable

3. Is this an E2E test?
   → Is this a critical user flow AND UI stable?
      → YES: write it
      → NO: skip it
```

**GOLDEN RULE**: Write tests when cost of NOT having them exceeds maintenance cost.

---

## 3. Test Structure

```
tests/
├── unit/              # Pure logic, no external deps
├── integration/       # DB, Redis, APIs
├── e2e/               # Full user flows
├── fixtures/          # Shared test data
├── helpers/           # Test utilities
└── config/            # Test configuration
```

---

## 4. Testing Pyramid

```
        /\
       /  \   E2E (5-10%)
      /----\
     /      \  Integration (20-30%)
    /--------\
   /          \ Unit (60-75%)
  /------------\
```

---

## 5. Unit Test Rules

### ALWAYS test:
- Entities and domain logic
- Services and use cases  
- Utilities and helpers
- Validators and transformers

### NEVER test:
- Simple getters/setters
- Framework boilerplate
- Trivial pass-through

### AAA Pattern:
```python
def test_user_creation():
    # Arrange
    data = {"email": "test@example.com"}
    
    # Act
    user = User.create(**data)
    
    # Assert
    assert user.email == "test@example.com"
```

### Naming:
```
test_<action>_<expected_result>
test_login_success_with_valid_credentials
test_login_fails_with_invalid_password
```

---

## 6. Coverage Targets

| Area | Target |
|------|--------|
| Entities & domain | 90%+ |
| Services & use cases | 85%+ |
| Adapters | 70%+ |
| API handlers | 60%+ |
| Overall | 80%+ |

**IMPORTANT**: Coverage is a SIGNAL, not a goal.

---

## 7. When User Asks for Tests

1. ASK what phase they are in
2. If unsure, DEFAULT to:
   - Unit tests for all new code
   - Integration only if API stable
   - E2E only if explicitly requested

3. NEVER write all three at once unless:
   - Explicitly requested
   - Feature is production-critical
   - Everything is stable

---

> **Mantra**: Simple → Fast → Reliable

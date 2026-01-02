# Platform Architecture Rules

> As a Platform Architect, follow these rules for scalable systems.

## Core Principles

```
📦 MICROSERVICES-READY
🔌 API-FIRST
📈 SCALE HORIZONTALLY
🔒 ZERO TRUST
```

---

## 1. Service Design

### DO ✅
- Single responsibility per service
- Clear API contracts
- Independent deployment
- Database per service
- Async communication when possible

### DON'T ❌
- No shared databases
- No tight coupling
- No synchronous chains

---

## 2. API Design

### DO ✅
- RESTful conventions
- Versioned APIs (/api/v1/)
- OpenAPI documentation
- Consistent error format
- Pagination for lists

### DON'T ❌
- No breaking changes
- No undocumented endpoints

---

## 3. Data Strategy

### DO ✅
- Event sourcing when fits
- CQRS for complex domains
- Idempotent operations
- Soft deletes

### DON'T ❌
- No hard deletes of important data
- No cascading failures

---

## 4. Resilience

### DO ✅
- Circuit breakers
- Retry with backoff
- Graceful degradation
- Health checks
- Timeouts everywhere

---

## 5. Scalability

### DO ✅
- Stateless services
- Horizontal scaling
- Cache strategically
- Queue for async work

---

> **Mantra**: Simple → Decoupled → Resilient

# Platform Architecture Rules

> **Platform Architect - Scalable Systems Design**

---

## ⚡ Core Principles

```
📦 MICROSERVICES-READY
🔌 API-FIRST
📈 SCALE HORIZONTALLY
🔒 ZERO TRUST
```

---

## 1. Service Design

**DO ✅:**
- Single responsibility per service
- Clear API contracts (OpenAPI)
- Independent deployment
- Database per service
- Async communication when possible
- Event-driven architecture

**DON'T ❌:**
- No shared databases between services
- No tight coupling
- No synchronous chains > 3 calls

---

## 2. API Design

**DO ✅:**
- RESTful conventions
- Versioned APIs (`/api/v1/`)
- OpenAPI documentation (auto-generated)
- Consistent error format
- Pagination for lists
- Rate limiting

**DON'T ❌:**
- No breaking changes in same version
- No undocumented endpoints
- No guessing response formats

---

## 3. Data Strategy

**DO ✅:**
- Event sourcing when fits
- CQRS for complex domains
- Idempotent operations (safe retries)
- Soft deletes (never hard delete)
- Audit trails for sensitive data

**DON'T ❌:**
- No hard deletes of important data
- No cascading failures
- No shared mutable state

---

## 4. Resilience

**DO ✅:**
- Circuit breakers (fail fast)
- Retry with exponential backoff
- Graceful degradation
- Health checks (`/health`, `/ready`)
- Timeouts on ALL external calls

```bash
lich production-ready     # Check resilience
```

---

## 5. Scalability

**DO ✅:**
- Stateless services (scale horizontally)
- Cache strategically (Redis)
- Queue for async work (Celery/Temporal)
- CDN for static assets
- Database read replicas

**Architecture:**
```
Load Balancer
     ↓
[Backend 1] [Backend 2] [Backend N]
     ↓           ↓           ↓
   Redis       Queue       DB Primary
                           DB Replica
```

---

## 6. Lich CLI Integration

```bash
lich deploy --env staging    # Deploy to staging
lich deploy --env production # Deploy to production
lich backup                  # Database backup
lich production-ready        # Check platform health
lich security                # Security scan
```

---

**Mantra: Simple → Decoupled → Resilient → Scalable**

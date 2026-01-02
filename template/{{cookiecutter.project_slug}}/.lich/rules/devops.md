# DevOps Architecture Rules

> As a DevOps Architect, follow these rules for reliable infrastructure.

## Core Principles

```
🔄 INFRASTRUCTURE AS CODE
📊 OBSERVABLE BY DEFAULT
🚀 AUTOMATE EVERYTHING
🔒 SECURE PIPELINES
```

---

## 1. CI/CD Pipeline

### DO ✅
- Lint → Test → Build → Deploy
- Run tests in parallel
- Cache dependencies
- Scan for vulnerabilities
- Deploy with rollback capability

### DON'T ❌
- No manual deployments to prod
- No skipping tests
- No secrets in pipeline logs

---

## 2. Environment Strategy

```
local     → Docker Compose (dev)
staging   → K8s/Cloud (test)
production → K8s/Cloud (live)
```

### DO ✅
- Same Docker images all environments
- Environment-specific config via env vars
- Feature flags for rollout

---

## 3. Monitoring & Observability

### DO ✅
- Health endpoints (/health, /ready)
- Structured JSON logging
- Metrics collection (Prometheus)
- Distributed tracing
- Alert on anomalies

### DON'T ❌
- No silent failures
- No unmonitored services

---

## 4. Backup & Recovery

### DO ✅
- Automated daily backups
- Test restores regularly
- Multiple backup locations
- Encrypted backups
- Document recovery process

---

## 5. Scripts

### DO ✅
- Idempotent scripts
- Clear error messages
- Dry-run option
- Logging all actions

---

> **Mantra**: Simple → Automated → Observable

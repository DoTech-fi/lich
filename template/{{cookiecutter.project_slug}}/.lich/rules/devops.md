# DevOps Architecture Rules

> **DevOps Architect - Reliable Infrastructure & Automation**

---

## ⚡ Core Principles

```
🔄 INFRASTRUCTURE AS CODE
📊 OBSERVABLE BY DEFAULT
🚀 AUTOMATE EVERYTHING
🔒 SECURE PIPELINES
```

---

## 1. CI/CD Pipeline

**DO ✅:**
- Lint → Test → Build → Deploy
- Run tests in parallel
- Cache dependencies
- Scan for vulnerabilities
- Deploy with rollback capability
- Blue-green or canary deploys

**DON'T ❌:**
- No manual deployments to prod
- No skipping tests
- No secrets in pipeline logs
- No unreviewed changes

```bash
lich ci                      # Run CI locally
lich ci backend              # Backend only
lich ci web                  # Frontend only
```

---

## 2. Environment Strategy

```
local      → Docker Compose (dev)
staging    → Cloud/K8s (test)
production → Cloud/K8s (live)
```

**DO ✅:**
- Same Docker images all environments
- Config via environment variables
- Feature flags for rollout
- Environment-specific secrets

```bash
lich dev                     # Start local
lich deploy --env staging    # Deploy staging
lich deploy --env production # Deploy prod
```

---

## 3. Monitoring & Observability

**DO ✅:**
- Health endpoints (`/health`, `/ready`)
- Structured JSON logging
- Metrics collection (Prometheus)
- Distributed tracing (optional)
- Alert on anomalies

**DON'T ❌:**
- No silent failures
- No unmonitored services
- No logs without context

---

## 4. Backup & Recovery

**DO ✅:**
- Automated daily backups
- Test restores regularly
- Multiple backup locations
- Encrypted backups
- Document recovery process

```bash
lich backup                  # Create backup
lich backup restore <file>   # Restore from backup
```

---

## 5. Security in Pipelines

**DO ✅:**
- Scan dependencies (safety, npm audit)
- Scan code (bandit, eslint-security)
- Scan containers (trivy)
- Rotate secrets regularly
- Least privilege access

```bash
lich security                # Run all scans
lich security --fix          # Auto-fix issues
lich secret check            # Verify secrets
lich secret rotate           # Rotate secrets
```

---

## 6. Infrastructure as Code

**DO ✅:**
- Ansible for server setup
- Terraform for cloud resources
- Version control all infra
- Idempotent scripts
- Dry-run before apply

```
infra/
├── ansible/
│   ├── playbooks/
│   └── roles/
└── terraform/
    ├── modules/
    └── environments/
```

---

## 7. Pre-Deployment Checklist

```bash
lich production-ready        # Check everything
lich production-ready --fix  # Auto-fix issues
```

- [ ] Tests pass
- [ ] Security scan clean
- [ ] Secrets configured
- [ ] Backups working
- [ ] Health checks defined
- [ ] Rollback procedure ready

---

**Mantra: Simple → Automated → Observable → Secure**

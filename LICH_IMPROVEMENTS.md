# Lich Framework - Improvement Plan

> **این فایل لیست بهبودهایی است که باید به Lich اضافه شود**
> وقتی آماده شدی، این فایل رو بده به AI و بگو implement کنه.

---

## 🔴 Priority 1: Security (Critical)

### 1.1 Security Middlewares Default ON

**مشکل:** Security middlewares در `main.py` کامنت هستن.

**راه‌حل:**
```python
# main.py - Security middlewares باید اینا رو uncomment کنه by default
from api.middleware.security import SecurityHeadersMiddleware
from api.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

**فایل‌های تغییر:**
- `template/.../backend/main.py`
- اضافه کردن environment toggle: `SECURITY_ENABLED=true`

---

### 1.2 CORS Strict Mode

**مشکل:** `allow_methods=["*"]` و `allow_headers=["*"]`

**راه‌حل:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
```

---

### 1.3 Deep Health Check

**مشکل:** `/health` فقط `{"status": "healthy"}` برمی‌گردونه

**راه‌حل:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "db": await check_db(),
        "redis": await check_redis() if settings.use_redis else None,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

### 1.4 Protect OpenAPI Docs

**مشکل:** `/api/docs` publicly accessible

**راه‌حل:**
```python
# Production باید docs disable باشه یا auth داشته باشه
docs_url="/api/docs" if settings.debug else None,
redoc_url="/api/redoc" if settings.debug else None,
```

---

## 🟡 Priority 2: New CLI Commands

### 2.1 `lich security` - Security Scan

```bash
lich security          # Run bandit + safety
lich security --fix    # Auto-fix if possible
```

**Implementation:**
```python
# cli/src/lich/commands/security.py
@click.command()
def security():
    """Run security checks (bandit + safety)."""
    subprocess.run(["bandit", "-r", "backend/"])
    subprocess.run(["safety", "check"])
```

---

### 2.2 `lich lint` - Code Quality

```bash
lich lint              # ruff + mypy
lich lint --fix        # Auto-fix
```

---

### 2.3 `lich deploy` - Deployment Helper

```bash
lich deploy staging    # Deploy to staging
lich deploy prod       # Deploy to production
lich deploy --dry-run  # Preview changes
```

**با Ansible:**
```bash
lich deploy staging
# Internally runs:
# ansible-playbook -i inventory/staging.yml playbooks/site.yml
```

---

### 2.4 `lich backup` - Database Backup

```bash
lich backup            # Backup to ./backups/
lich backup --remote   # Upload to S3/Backblaze
lich restore <file>    # Restore from backup
```

---

### 2.5 `lich secret` - Secret Management

```bash
lich secret generate   # Generate secure secrets
lich secret rotate     # Rotate all secrets
lich secret check      # Check for exposed secrets
```

---

## 🟢 Priority 3: Ansible Deployment

### 3.1 Folder Structure

```
template/.../infra/
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   ├── staging.yml
│   │   └── production.yml
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── vault.yml.example
│   ├── roles/
│   │   ├── common/          # Base server setup
│   │   ├── docker/          # Docker installation
│   │   ├── traefik/         # Reverse proxy + SSL
│   │   ├── postgres/        # Database
│   │   ├── redis/           # Cache
│   │   ├── backend/         # FastAPI app
│   │   ├── frontend/        # Next.js apps
│   │   └── monitoring/      # Prometheus/Grafana
│   └── playbooks/
│       ├── site.yml         # Full deployment
│       ├── update.yml       # App update only
│       ├── backup.yml       # Backup databases
│       └── rollback.yml     # Emergency rollback
```

---

### 3.2 Integration with `lich deploy`

```python
# cli/src/lich/commands/deploy.py
@click.command()
@click.argument("environment", type=click.Choice(["staging", "production"]))
@click.option("--dry-run", is_flag=True)
def deploy(environment, dry_run):
    """Deploy to an environment using Ansible."""
    cmd = [
        "ansible-playbook",
        "-i", f"infra/ansible/inventory/{environment}.yml",
        "infra/ansible/playbooks/site.yml"
    ]
    if dry_run:
        cmd.append("--check")
    subprocess.run(cmd)
```

---

## 📋 Priority 4: Missing Features

### 4.1 CSRF Protection

```python
# api/middleware/csrf.py
from starlette_csrf import CSRFMiddleware

app.add_middleware(CSRFMiddleware, secret=settings.csrf_secret)
```

---

### 4.2 Audit Logging

```python
# internal/services/audit_service.py
class AuditService:
    async def log(self, user_id, action, resource, details):
        await self.repo.create(AuditLog(...))
```

---

### 4.3 Input Sanitization

```python
# api/middleware/sanitize.py
class InputSanitizationMiddleware:
    async def dispatch(self, request, call_next):
        # Sanitize body, query params
        ...
```

---

## ✅ Checklist برای Implementation

- [ ] **Security Middlewares Default ON**
- [ ] **CORS Strict Mode**
- [ ] **Deep Health Check**
- [ ] **Protect OpenAPI Docs in Production**
- [ ] **`lich security` command**
- [ ] **`lich lint` command**
- [ ] **`lich deploy` command with Ansible**
- [ ] **`lich backup` command**
- [ ] **`lich secret` command**
- [ ] **Ansible Roles (infra folder)**
- [ ] **CSRF Middleware**
- [ ] **Audit Logging**
- [ ] **Input Sanitization Middleware**

---

## 🎯 Usage

وقتی خواستی implement کنی:

```
Read LICH_IMPROVEMENTS.md and implement the checklist items one by one.
Start with Priority 1 (Security).
```

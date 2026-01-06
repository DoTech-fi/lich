# Lich Framework - Implementation Tasks

> **این فایل لیست تسک‌های قابل اجرا برای پیاده‌سازی LICH_IMPROVEMENTS.md است**
> 
> هر تسک که تموم شد، `[x]` بزن و کامیت کن.
> فرمت کامیت: `feat(lich): [component] - description`

---

## 📋 Task Legend

- `[ ]` = Not started
- `[/]` = In progress  
- `[x]` = Completed
- `[!]` = Blocked

---

## 🔴 Priority 1: Security (Critical)

### 1.1 Enable Security Middlewares by Default

- [ ] **1.1.1** Edit `template/.../backend/main.py`
  - Uncomment `SecurityHeadersMiddleware`
  - Uncomment `RateLimitMiddleware`
  - Add env toggle: `SECURITY_ENABLED=true`
  
- [ ] **1.1.2** Update `.env.example` with `SECURITY_ENABLED=true`

- [ ] **1.1.3** Test middleware activation locally

- [ ] **Commit:** `feat(lich): enable security middlewares by default`

---

### 1.2 CORS Strict Mode

- [ ] **1.2.1** Edit CORS config in `main.py`
  - Change `allow_methods` from `["*"]` to `["GET", "POST", "PUT", "DELETE", "PATCH"]`
  - Change `allow_headers` from `["*"]` to `["Authorization", "Content-Type", "X-Request-ID"]`

- [ ] **1.2.2** Add `CORS_ORIGINS` to `.env.example`

- [ ] **Commit:** `feat(lich): strict CORS configuration`

---

### 1.3 Deep Health Check

- [ ] **1.3.1** Create `api/http/health.py` with:
  - DB connection check
  - Redis connection check (if enabled)
  - Timestamp
  - Version info

- [ ] **1.3.2** Register health router in `main.py`

- [ ] **1.3.3** Add health check to docker-compose

- [ ] **Commit:** `feat(lich): deep health check endpoint`

---

### 1.4 Protect OpenAPI Docs

- [ ] **1.4.1** Conditionally disable docs in production
  ```python
  docs_url="/api/docs" if settings.debug else None
  ```

- [ ] **1.4.2** Add `DEBUG=false` to production `.env.example`

- [ ] **Commit:** `feat(lich): protect OpenAPI docs in production`

---

## 🟡 Priority 2: CLI Commands

### 2.1 `lich security` Command

- [ ] **2.1.1** Create `cli/src/lich/commands/security.py`

- [ ] **2.1.2** Implement backend scan (bandit + safety)

- [ ] **2.1.3** Implement frontend scan (npm audit for each app)

- [ ] **2.1.4** Implement secrets scan (git-secrets)

- [ ] **2.1.5** Implement Docker scan (trivy)

- [ ] **2.1.6** Add `--backend`, `--frontend`, `--fix`, `--json` options

- [ ] **2.1.7** Register command in CLI

- [ ] **2.1.8** Test all scan types

- [ ] **Commit:** `feat(lich): add lich security command`

---

### 2.2 `lich lint` Command

- [ ] **2.2.1** Create `cli/src/lich/commands/lint.py`

- [ ] **2.2.2** Implement Python linting (ruff/flake8)

- [ ] **2.2.3** Implement TypeScript linting (eslint)

- [ ] **2.2.4** Add `--fix` option

- [ ] **2.2.5** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich lint command`

---

### 2.3 `lich deploy` Command

- [ ] **2.3.1** Create `cli/src/lich/commands/deploy.py`

- [ ] **2.3.2** Implement SSH connection options (--host, --ip, --user, --key)

- [ ] **2.3.3** Implement dynamic inventory generation

- [ ] **2.3.4** Implement ansible-playbook execution

- [ ] **2.3.5** Add `--dry-run` option

- [ ] **2.3.6** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich deploy command`

---

### 2.4 `lich backup` Command

- [ ] **2.4.1** Create `cli/src/lich/commands/backup.py`

- [ ] **2.4.2** Implement auto-detect databases from docker-compose.yml

- [ ] **2.4.3** Implement PostgreSQL backup

- [ ] **2.4.4** Implement MariaDB/MySQL backup

- [ ] **2.4.5** Implement MongoDB backup

- [ ] **2.4.6** Implement Redis backup

- [ ] **2.4.7** Implement `--verify` option

- [ ] **2.4.8** Implement `--remote` upload to S3

- [ ] **2.4.9** Implement `--list` to show backups

- [ ] **2.4.10** Implement interactive restore

- [ ] **2.4.11** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich backup command with auto-detect`

---

### 2.5 `lich secret` Command

- [ ] **2.5.1** Create `cli/src/lich/commands/secret.py`

- [ ] **2.5.2** Implement `lich secret generate`

- [ ] **2.5.3** Implement `lich secret rotate`

- [ ] **2.5.4** Implement `lich secret check`

- [ ] **2.5.5** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich secret command`

---

## 🟢 Priority 3: Ansible Deployment

### 3.1 Folder Structure

- [ ] **3.1.1** Create `template/.../infra/ansible/` folder structure
  ```
  ansible/
  ├── ansible.cfg
  ├── inventory/
  ├── group_vars/
  ├── roles/
  └── playbooks/
  ```

- [ ] **Commit:** `feat(lich): ansible folder structure`

---

### 3.2 Ansible Roles

- [ ] **3.2.1** Create `roles/common/` (base server setup)

- [ ] **3.2.2** Create `roles/docker/` (Docker installation)

- [ ] **3.2.3** Create `roles/traefik/` (reverse proxy + SSL)

- [ ] **3.2.4** Create `roles/postgres/` (database)

- [ ] **3.2.5** Create `roles/redis/` (cache)

- [ ] **3.2.6** Create `roles/app/` (application deployment)

- [ ] **3.2.7** Create `roles/backup/` (backup cron)

- [ ] **Commit:** `feat(lich): ansible roles`

---

### 3.3 Ansible Playbooks

- [ ] **3.3.1** Create `playbooks/site.yml` (full setup)

- [ ] **3.3.2** Create `playbooks/update.yml` (deploy updates)

- [ ] **3.3.3** Create `playbooks/backup.yml`

- [ ] **3.3.4** Create `playbooks/rollback.yml`

- [ ] **3.3.5** Create inventory examples (staging.yml, production.yml)

- [ ] **Commit:** `feat(lich): ansible playbooks`

---

## 🔵 Priority 4: Middlewares

### 4.1 CSRF Protection Middleware

- [ ] **4.1.1** Create `template/.../api/middleware/csrf.py`

- [ ] **4.1.2** Implement token generation and validation

- [ ] **4.1.3** Add `ENABLE_CSRF` env variable

- [ ] **4.1.4** Add to main.py (conditional)

- [ ] **Commit:** `feat(lich): CSRF protection middleware`

---

### 4.2 Audit Logging Middleware

- [ ] **4.2.1** Create `template/.../api/middleware/audit.py`

- [ ] **4.2.2** Log POST/PUT/PATCH/DELETE operations

- [ ] **4.2.3** Include user_id, path, status, IP

- [ ] **4.2.4** Add optional DB persistence

- [ ] **4.2.5** Create AuditLog entity (optional)

- [ ] **Commit:** `feat(lich): audit logging middleware`

---

### 4.3 Input Sanitization Middleware

- [ ] **4.3.1** Create `template/.../api/middleware/sanitize.py`

- [ ] **4.3.2** Implement XSS pattern removal

- [ ] **4.3.3** Implement HTML escaping

- [ ] **4.3.4** Recursive dict/list sanitization

- [ ] **Commit:** `feat(lich): input sanitization middleware`

---

## 🟣 Priority 5: Production Ready Command

### 5.1 Base Command

- [ ] **5.1.1** Create `cli/src/lich/commands/production_ready.py`

- [ ] **5.1.2** Implement `ProductionReadinessChecker` class

- [ ] **5.1.3** Implement result display (emoji + table)

- [ ] **5.1.4** Add `--json` output option

- [ ] **Commit:** `feat(lich): production-ready command base`

---

### 5.2 Security Checks

- [ ] **5.2.1** Check: Security middlewares enabled

- [ ] **5.2.2** Check: CORS not `*` in production

- [ ] **5.2.3** Check: DEBUG=false

- [ ] **5.2.4** Check: Secret key ≥32 chars

- [ ] **5.2.5** Check: JWT secret ≥32 chars

- [ ] **5.2.6** Check: No hardcoded secrets

- [ ] **Commit:** `feat(lich): production-ready security checks`

---

### 5.3 Quality Checks

- [ ] **5.3.1** Check: Test coverage ≥80%

- [ ] **5.3.2** Check: No TODO/FIXME in code

- [ ] **5.3.3** Check: All .env vars in docker-compose

- [ ] **Commit:** `feat(lich): production-ready quality checks`

---

### 5.4 Operations Checks

- [ ] **5.4.1** Check: Docker images use specific tags

- [ ] **5.4.2** Check: Health check includes DB/Redis

- [ ] **5.4.3** Check: SSL/HTTPS configured

- [ ] **5.4.4** Check: Rate limiting enabled

- [ ] **5.4.5** Check: Backup strategy defined

- [ ] **5.4.6** Check: Structured logging enabled

- [ ] **Commit:** `feat(lich): production-ready operations checks`

---

### 5.5 Auto-Fix

- [ ] **5.5.1** Implement `--fix` option

- [ ] **5.5.2** Auto-fix: Generate strong secrets

- [ ] **5.5.3** Auto-fix: Add missing .env vars to compose

- [ ] **5.5.4** Auto-fix: Set DEBUG=false

- [ ] **Commit:** `feat(lich): production-ready auto-fix`

---

## 🟠 Priority 6: CI/CD & Build Strategy

### 6.1 `lich init` Build Questions

- [ ] **6.1.1** Add build strategy question to init wizard

- [ ] **6.1.2** Add container registry question

- [ ] **6.1.3** Add object storage question

- [ ] **6.1.4** Store answers in generated config

- [ ] **Commit:** `feat(lich): init build strategy questions`

---

### 6.2 GitHub Actions CI Workflow

- [ ] **6.2.1** Create `template/.github/workflows/ci.yml`

- [ ] **6.2.2** Implement change detection (paths-filter)

- [ ] **6.2.3** Add backend job (pytest + security)

- [ ] **6.2.4** Add frontend jobs (next build + npm audit)

- [ ] **6.2.5** Add security scan job

- [ ] **Commit:** `feat(lich): GitHub Actions CI workflow`

---

### 6.3 GitHub Actions Release Workflow

- [ ] **6.3.1** Create `template/.github/workflows/release.yml`

- [ ] **6.3.2** Implement version bump (patch/minor/major)

- [ ] **6.3.3** Implement git tag creation

- [ ] **6.3.4** Implement GitHub Release creation

- [ ] **Commit:** `feat(lich): GitHub Actions release workflow`

---

### 6.4 GitHub Actions Deploy Workflow

- [ ] **6.4.1** Create `template/.github/workflows/deploy.yml`

- [ ] **6.4.2** Implement tag selection input

- [ ] **6.4.3** Implement environment selection

- [ ] **6.4.4** Implement service selection

- [ ] **6.4.5** Implement auto-backup before migration

- [ ] **6.4.6** Implement S3 backup upload

- [ ] **6.4.7** Implement migration step

- [ ] **6.4.8** Implement health check

- [ ] **Commit:** `feat(lich): GitHub Actions deploy workflow with backup`

---

### 6.5 GitHub Actions Rollback Workflow

- [ ] **6.5.1** Create `template/.github/workflows/rollback.yml`

- [ ] **6.5.2** Implement backup listing from S3

- [ ] **6.5.3** Implement backup selection

- [ ] **6.5.4** Implement confirmation step

- [ ] **6.5.5** Implement DB restore

- [ ] **6.5.6** Implement code downgrade

- [ ] **6.5.7** Implement health check

- [ ] **Commit:** `feat(lich): GitHub Actions rollback workflow`

---

### 6.6 Production Tests Workflow

- [ ] **6.6.1** Create `template/.github/workflows/prod-tests.yml`

- [ ] **6.6.2** Implement k6 load test job

- [ ] **6.6.3** Implement Playwright E2E job

- [ ] **6.6.4** Implement scenario test job

- [ ] **6.6.5** Create test file templates

- [ ] **Commit:** `feat(lich): GitHub Actions production tests`

---

### 6.7 `lich ci` Local Command

- [ ] **6.7.1** Create `cli/src/lich/commands/ci.py`

- [ ] **6.7.2** Implement `lich ci` (all)

- [ ] **6.7.3** Implement `lich ci backend`

- [ ] **6.7.4** Implement `lich ci admin`

- [ ] **6.7.5** Implement `lich ci web`

- [ ] **6.7.6** Implement `lich ci landing`

- [ ] **6.7.7** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich ci command`

---

## 🔷 Priority 7: Monorepo Structure

### 7.1 Per-App CI Workflows

- [ ] **7.1.1** Create `template/.github/workflows/ci-backend.yml`

- [ ] **7.1.2** Create `template/.github/workflows/ci-frontend.yml` (reusable)

- [ ] **7.1.3** Create `template/.github/workflows/ci-admin.yml`

- [ ] **7.1.4** Create `template/.github/workflows/ci-web.yml`

- [ ] **7.1.5** Create `template/.github/workflows/ci-landing.yml`

- [ ] **Commit:** `feat(lich): per-app CI workflows`

---

## 🟤 Priority 8: Scheduled Tasks

### 8.1 `lich init` Task Runner Question

- [ ] **8.1.1** Add Temporal/Celery question to init wizard

- [ ] **8.1.2** Store choice in config

- [ ] **Commit:** `feat(lich): init task runner question`

---

### 8.2 Temporal Configuration

- [ ] **8.2.1** Create Temporal docker-compose services

- [ ] **8.2.2** Create `Dockerfile.worker`

- [ ] **8.2.3** Create `internal/workers/main.py`

- [ ] **8.2.4** Create example workflow

- [ ] **8.2.5** Create example activities

- [ ] **Commit:** `feat(lich): temporal configuration`

---

### 8.3 Celery Configuration

- [ ] **8.3.1** Create Celery docker-compose services

- [ ] **8.3.2** Create `internal/celery_app.py`

- [ ] **8.3.3** Create example tasks

- [ ] **8.3.4** Create beat schedule examples

- [ ] **Commit:** `feat(lich): celery configuration`

---

## ⚫ Priority 9: Observability

### 9.1 `lich init` Monitoring Question

- [ ] **9.1.1** Add monitoring stack question to init wizard

- [ ] **9.1.2** Store choice in config

- [ ] **Commit:** `feat(lich): init monitoring question`

---

### 9.2 Prometheus + Grafana Setup

- [ ] **9.2.1** Create Prometheus docker-compose service

- [ ] **9.2.2** Create Grafana docker-compose service

- [ ] **9.2.3** Create `infra/prometheus/prometheus.yml`

- [ ] **9.2.4** Create metrics endpoint in backend

- [ ] **9.2.5** Create Prometheus alert rules

- [ ] **Commit:** `feat(lich): prometheus and grafana setup`

---

### 9.3 Loki Log Aggregation

- [ ] **9.3.1** Create Loki docker-compose service

- [ ] **9.3.2** Create Promtail docker-compose service

- [ ] **9.3.3** Create `infra/loki/config.yml`

- [ ] **9.3.4** Create `infra/promtail/config.yml`

- [ ] **Commit:** `feat(lich): loki log aggregation`

---

### 9.4 Sentry Integration

- [ ] **9.4.1** Add sentry-sdk to backend requirements

- [ ] **9.4.2** Create Sentry init in main.py

- [ ] **9.4.3** Add Sentry config to Next.js apps

- [ ] **9.4.4** Add `SENTRY_DSN` to .env.example

- [ ] **Commit:** `feat(lich): sentry integration`

---

### 9.5 Grafana Dashboards

- [ ] **9.5.1** Create `infra/grafana/provisioning/` structure

- [ ] **9.5.2** Create application dashboard JSON

- [ ] **9.5.3** Create infrastructure dashboard JSON

- [ ] **9.5.4** Create database dashboard JSON

- [ ] **Commit:** `feat(lich): pre-configured grafana dashboards`

---

## 📊 Progress Summary

| Priority | Tasks | Completed |
|----------|-------|-----------|
| 1. Security | 12 | 0 |
| 2. CLI Commands | 32 | 0 |
| 3. Ansible | 15 | 0 |
| 4. Middlewares | 14 | 0 |
| 5. Production Ready | 21 | 0 |
| 6. CI/CD | 35 | 0 |
| 7. Monorepo | 6 | 0 |
| 8. Scheduled Tasks | 12 | 0 |
| 9. Observability | 17 | 0 |
| **Total** | **164** | **0** |

---

## 🚀 How to Use

1. شروع کن از Priority 1
2. هر تسک که تموم شد `[x]` بزن
3. وقتی یه گروه تموم شد، کامیت بزن
4. برو تسک بعدی

```bash
# Start working
git checkout -b feat/lich-improvements

# After each feature group
git add -A
git commit -m "feat(lich): [component] - description"

# When all done
git push origin feat/lich-improvements
```

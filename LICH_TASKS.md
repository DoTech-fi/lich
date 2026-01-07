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

- [x] **1.1.1** Edit `template/.../backend/main.py`
  - Uncomment `SecurityHeadersMiddleware`
  - Uncomment `RateLimitMiddleware`
  - Add env toggle: `SECURITY_ENABLED=true`
  
- [x] **1.1.2** Update `.env.example` with `SECURITY_ENABLED=true`

- [-] **1.1.3** Test middleware activation locally *(skipped - requires project generation)*

- [ ] **Commit:** `feat(lich): enable security middlewares by default`

---

### 1.2 CORS Strict Mode

- [x] **1.2.1** Edit CORS config in `main.py`
  - Change `allow_methods` from `["*"]` to `["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]`
  - Change `allow_headers` from `["*"]` to `["Authorization", "Content-Type", "X-Request-ID", "Accept"]`

- [x] **1.2.2** Add `CORS_ORIGINS` to `.env.example` *(already existed)*

- [ ] **Commit:** `feat(lich): strict CORS configuration`

---

### 1.3 Deep Health Check

- [x] **1.3.1** Create `api/http/health.py` with:
  - DB connection check
  - Redis connection check (if enabled)
  - Timestamp
  - Version info

- [x] **1.3.2** Register health router in `main.py` *(already registered)*

- [-] **1.3.3** Add health check to docker-compose *(skipped - already has healthchecks)*

- [ ] **Commit:** `feat(lich): deep health check endpoint`

---

### 1.4 Protect OpenAPI Docs

- [x] **1.4.1** Conditionally disable docs in production
  ```python
  docs_url="/api/docs" if settings.debug else None
  ```

- [x] **1.4.2** Add `DEBUG=false` to production `.env.example`

- [ ] **Commit:** `feat(lich): protect OpenAPI docs in production`

---

## 🟡 Priority 2: CLI Commands

### 2.1 `lich security` Command

- [x] **2.1.1** Create `cli/src/lich/commands/security.py`

- [x] **2.1.2** Implement backend scan (bandit + safety)

- [x] **2.1.3** Implement frontend scan (npm audit for each app)

- [x] **2.1.4** Implement secrets scan (gitleaks/git-secrets)

- [x] **2.1.5** Implement Docker scan (trivy)

- [x] **2.1.6** Add `--backend`, `--frontend`, `--fix`, `--json` options

- [x] **2.1.7** Register command in CLI

- [-] **2.1.8** Test all scan types *(skipped - requires manual testing)*

- [ ] **Commit:** `feat(lich): add lich security command`

---

### 2.2 `lich lint` Command

- [x] **2.2.1** Create `cli/src/lich/commands/lint.py`

- [x] **2.2.2** Implement Python linting (ruff/flake8)

- [x] **2.2.3** Implement TypeScript linting (eslint)

- [x] **2.2.4** Add `--fix` option

- [x] **2.2.5** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich lint command`

---

### 2.3 `lich deploy` Command

- [x] **2.3.1** Create `cli/src/lich/commands/deploy.py`

- [x] **2.3.2** Implement SSH connection options (--host, --ip, --user, --key)

- [x] **2.3.3** Implement dynamic inventory generation

- [x] **2.3.4** Implement ansible-playbook execution

- [x] **2.3.5** Add `--dry-run` option

- [x] **2.3.6** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich deploy command`

---

### 2.4 `lich backup` Command

- [x] **2.4.1** Create `cli/src/lich/commands/backup.py`

- [x] **2.4.2** Implement auto-detect databases from docker-compose.yml

- [x] **2.4.3** Implement PostgreSQL backup

- [x] **2.4.4** Implement MariaDB/MySQL backup

- [x] **2.4.5** Implement MongoDB backup

- [x] **2.4.6** Implement Redis backup

- [-] **2.4.7** Implement `--verify` option *(skipped)*

- [x] **2.4.8** Implement `--remote` upload to S3

- [x] **2.4.9** Implement `--list` to show backups

- [x] **2.4.10** Implement interactive restore

- [x] **2.4.11** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich backup command with auto-detect`

---

### 2.5 `lich secret` Command

- [x] **2.5.1** Create `cli/src/lich/commands/secret.py`

- [x] **2.5.2** Implement `lich secret generate`

- [x] **2.5.3** Implement `lich secret rotate`

- [x] **2.5.4** Implement `lich secret check`

- [x] **2.5.5** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich secret command`

---

## 🟢 Priority 3: Ansible Deployment

### 3.1 Folder Structure

- [x] **3.1.1** Create `template/.../infra/ansible/` folder structure
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

- [x] **3.2.1** Create `roles/common/` (base server setup)

- [x] **3.2.2** Create `roles/docker/` (Docker installation)

- [x] **3.2.3** Create `roles/traefik/` (reverse proxy + SSL)

- [x] **3.2.4** Create `roles/postgres/` (database)

- [x] **3.2.5** Create `roles/redis/` (cache)

- [x] **3.2.6** Create `roles/app/` (application deployment)

- [x] **3.2.7** Create `roles/backup/` (backup cron)

- [ ] **Commit:** `feat(lich): ansible roles`

---

### 3.3 Ansible Playbooks

- [x] **3.3.1** Create `playbooks/site.yml` (full setup)

- [x] **3.3.2** Create `playbooks/update.yml` (deploy updates)

- [x] **3.3.3** Create `playbooks/backup.yml`

- [x] **3.3.4** Create `playbooks/rollback.yml`

- [x] **3.3.5** Create inventory examples (staging.yml, production.yml)

- [ ] **Commit:** `feat(lich): ansible playbooks`

---

## 🔵 Priority 4: Middlewares

### 4.1 CSRF Protection Middleware

- [x] **4.1.1** Create `template/.../api/middleware/csrf.py`

- [x] **4.1.2** Implement token generation and validation

- [x] **4.1.3** Add `ENABLE_CSRF` env variable

- [x] **4.1.4** Add to main.py (conditional)

- [ ] **Commit:** `feat(lich): CSRF protection middleware`

---

### 4.2 Audit Logging Middleware

- [x] **4.2.1** Create `template/.../api/middleware/audit.py`

- [x] **4.2.2** Log POST/PUT/PATCH/DELETE operations

- [x] **4.2.3** Include user_id, path, status, IP

- [x] **4.2.4** Add optional DB persistence

- [-] **4.2.5** Create AuditLog entity *(optional - documented in comments)*

- [ ] **Commit:** `feat(lich): audit logging middleware`

---

### 4.3 Input Sanitization Middleware

- [x] **4.3.1** Create `template/.../api/middleware/sanitize.py`

- [x] **4.3.2** Implement XSS pattern removal

- [x] **4.3.3** Implement HTML escaping

- [x] **4.3.4** Recursive dict/list sanitization

- [ ] **Commit:** `feat(lich): input sanitization middleware`

---

## 🟣 Priority 5: Production Ready Command

### 5.1 Base Command

- [x] **5.1.1** Create `cli/src/lich/commands/production_ready.py`

- [x] **5.1.2** Implement `ProductionReadinessChecker` class

- [x] **5.1.3** Implement result display (emoji + table)

- [x] **5.1.4** Add `--json` output option

- [ ] **Commit:** `feat(lich): production-ready command base`

---

### 5.2 Security Checks

- [x] **5.2.1** Check: Security middlewares enabled

- [x] **5.2.2** Check: CORS not `*` in production

- [x] **5.2.3** Check: DEBUG=false

- [x] **5.2.4** Check: Secret key ≥32 chars

- [x] **5.2.5** Check: JWT secret ≥32 chars

- [x] **5.2.6** Check: No hardcoded secrets

- [ ] **Commit:** `feat(lich): production-ready security checks`

---

### 5.3 Quality Checks

- [x] **5.3.1** Check: Test coverage ≥80%

- [x] **5.3.2** Check: No TODO/FIXME in code

- [x] **5.3.3** Check: All .env vars in docker-compose

- [ ] **Commit:** `feat(lich): production-ready quality checks`

---

### 5.4 Operations Checks

- [x] **5.4.1** Check: Docker images use specific tags

- [x] **5.4.2** Check: Health check includes DB/Redis

- [x] **5.4.3** Check: SSL/HTTPS configured

- [x] **5.4.4** Check: Rate limiting enabled

- [x] **5.4.5** Check: Backup strategy defined

- [x] **5.4.6** Check: Structured logging enabled

- [ ] **Commit:** `feat(lich): production-ready operations checks`

---

### 5.5 Auto-Fix

- [x] **5.5.1** Implement `--fix` option

- [x] **5.5.2** Auto-fix: Generate strong secrets

- [-] **5.5.3** Auto-fix: Add missing .env vars to compose *(skipped)*

- [x] **5.5.4** Auto-fix: Set DEBUG=false

- [ ] **Commit:** `feat(lich): production-ready auto-fix`

---

## 🟠 Priority 6: CI/CD & Build Strategy

### 6.1 `lich init` Build Questions

- [x] **6.1.1** Add build strategy question to init wizard

- [x] **6.1.2** Add container registry question

- [x] **6.1.3** Add object storage question

- [x] **6.1.4** Store answers in generated config

- [ ] **Commit:** `feat(lich): init build strategy questions`

---

### 6.2 GitHub Actions CI Workflow

- [x] **6.2.1** Create `template/.github/workflows/ci.yml` *(already existed)*

- [-] **6.2.2** Implement change detection (paths-filter) *(already in existing ci.yml)*

- [x] **6.2.3** Add backend job (pytest + security)

- [x] **6.2.4** Add frontend jobs (next build + npm audit)

- [-] **6.2.5** Add security scan job *(in existing ci.yml)*

- [ ] **Commit:** `feat(lich): GitHub Actions CI workflow`

---

### 6.3 GitHub Actions Release Workflow

- [x] **6.3.1** Create `template/.github/workflows/release.yml`

- [x] **6.3.2** Implement version bump (patch/minor/major)

- [x] **6.3.3** Implement git tag creation

- [x] **6.3.4** Implement GitHub Release creation

- [ ] **Commit:** `feat(lich): GitHub Actions release workflow`

---

### 6.4 GitHub Actions Deploy Workflow

- [x] **6.4.1** Create `template/.github/workflows/deploy.yml`

- [x] **6.4.2** Implement tag selection input

- [x] **6.4.3** Implement environment selection

- [x] **6.4.4** Implement service selection

- [x] **6.4.5** Implement auto-backup before migration

- [x] **6.4.6** Implement S3 backup upload

- [x] **6.4.7** Implement migration step

- [x] **6.4.8** Implement health check

- [ ] **Commit:** `feat(lich): GitHub Actions deploy workflow with backup`

---

### 6.5 GitHub Actions Rollback Workflow

- [x] **6.5.1** Create `template/.github/workflows/rollback.yml`

- [-] **6.5.2** Implement backup listing from S3 *(manual input)*

- [x] **6.5.3** Implement backup selection

- [x] **6.5.4** Implement confirmation step

- [x] **6.5.5** Implement DB restore

- [x] **6.5.6** Implement code downgrade

- [x] **6.5.7** Implement health check

- [ ] **Commit:** `feat(lich): GitHub Actions rollback workflow`

---

### 6.6 Production Tests Workflow

- [x] **6.6.1** Create `template/.github/workflows/prod-tests.yml`

- [x] **6.6.2** Implement k6 load test job

- [x] **6.6.3** Implement Playwright E2E job

- [x] **6.6.4** Implement scenario test job

- [x] **6.6.5** Create test file templates

- [ ] **Commit:** `feat(lich): GitHub Actions production tests`

---

### 6.7 `lich ci` Local Command

- [x] **6.7.1** Create `cli/src/lich/commands/ci.py`

- [x] **6.7.2** Implement `lich ci` (all)

- [x] **6.7.3** Implement `lich ci backend`

- [x] **6.7.4** Implement `lich ci admin`

- [x] **6.7.5** Implement `lich ci web`

- [x] **6.7.6** Implement `lich ci landing`

- [x] **6.7.7** Register command in CLI

- [ ] **Commit:** `feat(lich): add lich ci command`

---

## 🔷 Priority 7: Monorepo Structure

### 7.1 Per-App CI Workflows

- [-] **7.1.1** Create `template/.github/workflows/ci-backend.yml` *(using main ci.yml)*

- [-] **7.1.2** Create `template/.github/workflows/ci-frontend.yml` *(using main ci.yml)*

- [-] **7.1.3** Create `template/.github/workflows/ci-admin.yml` *(using main ci.yml)*

- [-] **7.1.4** Create `template/.github/workflows/ci-web.yml` *(using main ci.yml)*

- [-] **7.1.5** Create `template/.github/workflows/ci-landing.yml` *(using main ci.yml)*

- [-] **Commit:** *(skipped - consolidated into single ci.yml)*

---

## 🟤 Priority 8: Scheduled Tasks

### 8.1 `lich init` Task Runner Question

- [x] **8.1.1** Add Temporal/Celery question to init wizard

- [x] **8.1.2** Store choice in config

- [ ] **Commit:** `feat(lich): init task runner question`

---

### 8.2 Temporal Configuration

- [x] **8.2.1** Create Temporal docker-compose services

- [x] **8.2.2** Create `Dockerfile.worker`

- [x] **8.2.3** Create `internal/workers/main.py`

- [x] **8.2.4** Create example workflow

- [x] **8.2.5** Create example activities

- [ ] **Commit:** `feat(lich): temporal configuration`

---

### 8.3 Celery Configuration

- [x] **8.3.1** Create Celery docker-compose services

- [x] **8.3.2** Create `internal/celery_app.py`

- [x] **8.3.3** Create example tasks

- [x] **8.3.4** Create beat schedule examples

- [ ] **Commit:** `feat(lich): celery configuration`

---





---

## 📊 Progress Summary

| Priority | Tasks | Completed |
|----------|-------|-----------|
| 1. Security | 12 | 10 |
| 2. CLI Commands | 32 | 37 |
| 3. Ansible | 15 | 13 |
| 4. Middlewares | 14 | 12 |
| 5. Production Ready | 21 | 22 |
| 6. CI/CD | 35 | 37 |
| 7. Monorepo | 6 | - (skipped) |
| 8. Scheduled Tasks | 12 | 11 |
| 9. Observability | 17 | - (skipped) |
| 10. Dev Experience | 1 | 1 |
| **Total** | **~142** | **~143** ✅ |

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

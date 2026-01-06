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

**دو روش برای اتصال:**

```bash
# روش 1: SSH Config (توصیه شده)
# کاربر از قبل ~/.ssh/config داره:
# Host myserver
#   HostName 1.2.3.4
#   User root
#   IdentityFile ~/.ssh/id_rsa

lich deploy staging --host myserver

# روش 2: Inline credentials
lich deploy staging --ip 1.2.3.4 --user root --password "xxx"
lich deploy staging --ip 1.2.3.4 --user root --key ~/.ssh/id_rsa
```

**Implementation:**
```python
# cli/src/lich/commands/deploy.py
@click.command()
@click.argument("environment", type=click.Choice(["staging", "production"]))
@click.option("--host", help="SSH config host name")
@click.option("--ip", help="Server IP address")
@click.option("--user", default="root", help="SSH user")
@click.option("--password", help="SSH password (not recommended)")
@click.option("--key", help="SSH private key path")
@click.option("--dry-run", is_flag=True)
def deploy(environment, host, ip, user, password, key, dry_run):
    """Deploy to an environment."""
    
    # Validate: either --host OR --ip required
    if not host and not ip:
        raise click.UsageError("Either --host or --ip is required")
    
    # Build inventory dynamically if using inline credentials
    if ip:
        inventory = generate_dynamic_inventory(ip, user, password, key)
    else:
        inventory = f"infra/ansible/inventory/{environment}.yml"
    
    cmd = [
        "ansible-playbook",
        "-i", inventory,
        "infra/ansible/playbooks/site.yml"
    ]
    if dry_run:
        cmd.append("--check")
    subprocess.run(cmd)
```

---

## 🆕 Priority 5: `lich production-ready` Command

### 5.1 چیکار می‌کنه؟

```bash
lich production-ready
```

**Output:**
```
🔍 Production Readiness Check
═══════════════════════════════════════════════════════════

✅ Security Middlewares     ENABLED
✅ CORS Origins             Strict (3 origins)
✅ Debug Mode               OFF
✅ Secret Key               Strong (64 chars)
⚠️  Test Coverage           45% (recommended: 80%+)
✅ .env Variables           All defined in docker-compose
✅ Docker Images            Using specific tags (not :latest)
✅ Health Endpoints         /health returns DB+Redis status
❌ SSL Certificates         Not configured (Traefik missing)
✅ Rate Limiting            60 req/min
⚠️  Backup Strategy         Not configured
✅ Logging                  Structured JSON enabled

═══════════════════════════════════════════════════════════
📊 Score: 78% Production Ready

⚠️  WARNINGS (non-blocking):
   - Test coverage below 80%
   - No backup strategy configured

❌ BLOCKERS:
   - SSL/Traefik not configured

💡 Run `lich production-ready --fix` for auto-fixes
```

---

### 5.2 Checks List

| Check | Category | Blocking? |
|-------|----------|-----------|
| Security middlewares enabled | Security | ⚠️ Warning |
| CORS not `*` in production | Security | ❌ Blocker |
| DEBUG=false | Security | ❌ Blocker |
| Secret key ≥32 chars | Security | ❌ Blocker |
| JWT secret ≥32 chars | Security | ❌ Blocker |
| No hardcoded secrets in code | Security | ❌ Blocker |
| Test coverage ≥80% | Quality | ⚠️ Warning |
| All .env vars in docker-compose | Config | ⚠️ Warning |
| Docker images use specific tags | Docker | ⚠️ Warning |
| Health check includes DB/Redis | Operations | ⚠️ Warning |
| SSL/HTTPS configured | Security | ❌ Blocker |
| Rate limiting enabled | Security | ⚠️ Warning |
| Backup strategy defined | Operations | ⚠️ Warning |
| Structured logging enabled | Operations | ⚠️ Warning |
| No TODO/FIXME in prod code | Quality | ⚠️ Warning |
| OpenAPI docs disabled in prod | Security | ⚠️ Warning |
| Database backups scheduled | Operations | ⚠️ Warning |
| Error tracking configured | Operations | ⚠️ Warning |

---

### 5.3 Implementation

```python
# cli/src/lich/commands/production_ready.py
import click
from pathlib import Path
import subprocess
import re

@click.command("production-ready")
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def production_ready(fix, output_json):
    """Check if project is production ready."""
    
    checks = ProductionReadinessChecker()
    
    results = {
        "security": [
            checks.check_security_middlewares(),
            checks.check_cors_config(),
            checks.check_debug_mode(),
            checks.check_secret_strength(),
            checks.check_no_hardcoded_secrets(),
        ],
        "quality": [
            checks.check_test_coverage(),
            checks.check_no_todos(),
        ],
        "config": [
            checks.check_env_vars_in_compose(),
            checks.check_docker_tags(),
        ],
        "operations": [
            checks.check_health_endpoints(),
            checks.check_ssl_configured(),
            checks.check_rate_limiting(),
            checks.check_backup_strategy(),
            checks.check_structured_logging(),
            checks.check_error_tracking(),
        ],
    }
    
    if fix:
        for category in results.values():
            for check in category:
                if check.fixable and not check.passed:
                    check.auto_fix()
    
    display_results(results, output_json)


class ProductionReadinessChecker:
    def check_test_coverage(self):
        """Check pytest coverage percentage."""
        result = subprocess.run(
            ["pytest", "--cov", "--cov-report=term", "-q"],
            capture_output=True, text=True
        )
        # Parse coverage percentage
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", result.stdout)
        coverage = int(match.group(1)) if match else 0
        
        return Check(
            name="Test Coverage",
            passed=coverage >= 80,
            value=f"{coverage}%",
            recommended="80%+",
            blocking=False,
            fixable=False
        )
    
    def check_env_vars_in_compose(self):
        """Check all .env vars are in docker-compose."""
        env_vars = self._parse_env_file(".env.example")
        compose_vars = self._parse_compose_file("docker-compose.yml")
        
        missing = env_vars - compose_vars
        
        return Check(
            name=".env Variables in Compose",
            passed=len(missing) == 0,
            value=f"{len(missing)} missing" if missing else "All defined",
            details=list(missing) if missing else None,
            blocking=False,
            fixable=True
        )
    
    def check_no_hardcoded_secrets(self):
        """Scan code for hardcoded secrets."""
        result = subprocess.run(
            ["git", "secrets", "--scan"],
            capture_output=True
        )
        return Check(
            name="No Hardcoded Secrets",
            passed=result.returncode == 0,
            blocking=True
        )
```

---

### 5.4 More Checks to Add

```python
def check_dockerfile_security(self):
    """Check Dockerfile follows security best practices."""
    issues = []
    with open("backend/Dockerfile") as f:
        content = f.read()
        if "USER root" in content or "USER 0" in content:
            issues.append("Running as root")
        if ":latest" in content:
            issues.append("Using :latest tag")
        if "apt-get" in content and "--no-install-recommends" not in content:
            issues.append("Missing --no-install-recommends")
    return Check(name="Dockerfile Security", passed=len(issues)==0)

def check_dependencies_vulnerabilities(self):
    """Check for known vulnerabilities in dependencies."""
    result = subprocess.run(["safety", "check"], capture_output=True)
    return Check(name="Dependency Vulnerabilities", passed=result.returncode==0)

def check_database_migrations_applied(self):
    """Check all migrations are applied."""
    result = subprocess.run(
        ["alembic", "current"], capture_output=True, text=True
    )
    return Check(name="Migrations Applied", passed="head" in result.stdout)
```

---

## ✅ Updated Checklist

- [ ] **Security Middlewares Default ON**
- [ ] **CORS Strict Mode**
- [ ] **Deep Health Check**
- [ ] **Protect OpenAPI Docs in Production**
- [ ] **`lich security` command**
- [ ] **`lich lint` command**
- [ ] **`lich deploy` command with SSH options**
  - [ ] Support `--host` (SSH config)
  - [ ] Support `--ip --user --password/--key`
  - [ ] Dynamic inventory generation
- [ ] **`lich backup` command**
- [ ] **`lich secret` command**
- [ ] **`lich production-ready` command**
  - [ ] Security checks
  - [ ] Quality checks (coverage, TODOs)
  - [ ] Config checks (env vars, docker tags)
  - [ ] Operations checks (health, SSL, backups)
  - [ ] `--fix` auto-fix option
  - [ ] Score calculation
- [ ] **Ansible Roles (infra folder)**
- [ ] **CSRF Middleware**
- [ ] **Audit Logging**
- [ ] **Input Sanitization Middleware**
- [ ] **CI/CD GitHub Actions**
- [ ] **Build Strategy Options**
- [ ] **Object Storage Integration**

---

## 🆕 Priority 6: CI/CD & Build Strategy

### 6.1 `lich init` - New Questions

Add these questions to the project initialization flow:

```
🚀 Deployment Configuration
═══════════════════════════════════════════════════════════

❓ Do you want to build images on the server? (y/n)
   
   → If YES: No container registry needed. Images will be built 
     directly on the server during deployment.
     (Best for: MVP, single server, low cost)
     
   → If NO: You'll need a container registry.
     
❓ (Only if NO above) Select your container registry:
   
   1. Docker Hub       (1 free private repo)
   2. GitHub GHCR      (500MB free private)
   3. GitLab Registry  (5GB free private) ← Recommended
   4. AWS ECR          (Paid)
   5. Self-hosted      (Harbor on your server)

❓ Does your app need file uploads/storage? (y/n)

   → If YES: Configure object storage
     
❓ (Only if YES above) Select your object storage:

   1. Hetzner Object Storage  (€4.67/TB, S3-compatible)
   2. AWS S3                  (Standard pricing)
   3. MinIO (self-hosted)     (Free, on your server)
   4. Backblaze B2            ($5/TB, cheapest)
```

---

### 6.2 Build on Server Strategy (Default)

When user selects "Build on Server":

**Deploy Flow:**
```bash
lich deploy production --host myserver

# Internally runs:
ssh myserver << 'EOF'
  cd /opt/myapp
  git pull origin main
  docker-compose build --parallel
  docker-compose up -d --remove-orphans
EOF
```

**Generated Files:**
```
infra/
├── ansible/
│   └── playbooks/
│       └── site.yml       # Includes build step
└── scripts/
    └── deploy.sh          # Simple deploy script
```

**Ansible playbook with build:**
```yaml
# infra/ansible/playbooks/site.yml
- name: Deploy Application
  hosts: "{{ target_host }}"
  tasks:
    - name: Pull latest code
      git:
        repo: "{{ git_repo }}"
        dest: /opt/{{ project_name }}
        version: "{{ git_branch | default('main') }}"
    
    - name: Build Docker images
      command: docker-compose build --parallel
      args:
        chdir: /opt/{{ project_name }}
    
    - name: Start services
      command: docker-compose up -d --remove-orphans
      args:
        chdir: /opt/{{ project_name }}
    
    - name: Health check
      uri:
        url: "http://localhost:8000/health"
        status_code: 200
      retries: 5
      delay: 10
```

---

### 6.3 Container Registry Strategy (Optional)

When user selects a registry:

**Generated `.github/workflows/release.yml`:**
```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_TOKEN }}
      
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ secrets.REGISTRY_URL }}/${{ github.repository }}:${{ github.ref_name }}
            ${{ secrets.REGISTRY_URL }}/${{ github.repository }}:latest
```

---

### 6.4 Object Storage Configuration

When user needs file storage:

**Add to `.env.example`:**
```bash
# Object Storage (S3-compatible)
S3_ENDPOINT=https://fsn1.your-objectstorage.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=myapp-uploads
S3_REGION=fsn1
```

**Add to `docker-compose.yml` (dev environment):**
```yaml
services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
```

**Add storage service:**
```python
# internal/services/storage_service.py
import boto3
from botocore.client import Config

class StorageService:
    def __init__(self, settings):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=Config(signature_version='s3v4'),
            region_name=settings.s3_region
        )
        self.bucket = settings.s3_bucket
    
    async def upload(self, file, key: str) -> str:
        self.client.upload_fileobj(file, self.bucket, key)
        return f"{self.bucket}/{key}"
    
    async def download(self, key: str):
        return self.client.get_object(Bucket=self.bucket, Key=key)
    
    async def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expires
        )
```

---

### 6.5 GitHub Actions CI Pipeline

**Generated `.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r backend/ -ll
          safety check
      
      - name: Production readiness check
        run: |
          cd backend
          lich production-ready --json > readiness.json
        continue-on-error: true

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
      - name: Type check
        run: |
          pip install mypy
          mypy backend/
```

---

### 6.6 New CLI Commands for CI/CD

```bash
# Run full CI locally
lich ci                    # Run all: test + lint + security + production-ready

# Version management
lich version               # Show current version
lich version bump major    # 1.0.0 -> 2.0.0
lich version bump minor    # 1.0.0 -> 1.1.0
lich version bump patch    # 1.0.0 -> 1.0.1

# Release
lich release               # Tag current commit with version, push tag

# Remote operations
lich logs                  # View remote logs (last 100 lines)
lich logs -f               # Follow logs
lich status                # Check remote health
lich ssh                   # Quick SSH to server
lich rollback              # Rollback to previous version
lich rollback v1.2.3       # Rollback to specific version
```

---

## 📋 Full Updated Checklist

### Priority 1: Security ✅
- [ ] Security Middlewares Default ON
- [ ] CORS Strict Mode
- [ ] Deep Health Check
- [ ] Protect OpenAPI Docs

### Priority 2: CLI Commands
- [ ] `lich security`
- [ ] `lich lint`
- [ ] `lich deploy` with SSH options
- [ ] `lich backup`
- [ ] `lich secret`

### Priority 3: Ansible Deployment
- [ ] Folder structure
- [ ] All roles (common, docker, traefik, etc.)
- [ ] Playbooks (site, update, backup, rollback)

### Priority 4: Middlewares
- [ ] CSRF Middleware
- [ ] Audit Logging
- [ ] Input Sanitization

### Priority 5: Production Ready
- [ ] `lich production-ready` command
- [ ] All checks implemented
- [ ] `--fix` auto-fix

### Priority 6: CI/CD & Build Strategy
- [ ] `lich init` build strategy questions
- [ ] Build on server (default)
- [ ] Container registry options
- [ ] Object storage integration
- [ ] GitHub Actions CI workflow
- [ ] GitHub Actions Release workflow
- [ ] `lich ci` command
- [ ] `lich version` command
- [ ] `lich release` command
- [ ] `lich logs/status/ssh` commands
- [ ] `lich rollback` command

---

## 🎯 Usage

To implement these improvements:

```
Read LICH_IMPROVEMENTS.md and implement the checklist items.
Start with Priority 1 (Security), then proceed in order.
```

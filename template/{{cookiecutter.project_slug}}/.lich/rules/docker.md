# Docker Architecture Rules

> As a Docker/Container Architect, follow these rules for production-ready containers.

## Core Principles

```
🔒 SECURE BY DEFAULT
📦 MINIMAL IMAGES
⚡ FAST BUILDS
🔄 REPRODUCIBLE
```

---

## 1. Dockerfile Best Practices

### DO ✅
- Multi-stage builds
- Use specific version tags (not :latest)
- Use alpine/slim base images
- Run as non-root user
- Copy only what's needed
- Group RUN commands

### DON'T ❌
- Never run as root
- Never use :latest tags
- Never copy entire project blindly
- Never install dev dependencies in prod

---

## 2. Image Structure

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -s /bin/false appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
USER appuser
CMD ["python", "main.py"]
```

---

## 3. Docker Compose Rules

### DO ✅
- Define healthchecks for all services
- Use named volumes
- Explicit network definitions
- Resource limits (memory/cpu)
- Restart policies

### DON'T ❌
- No anonymous volumes
- No default bridge network
- No unlimited resources

---

## 4. Security

### DO ✅
- Non-root user (USER appuser)
- Read-only filesystem where possible
- No secrets in image
- Scan images for vulnerabilities
- Use .dockerignore

### DON'T ❌
- Never hardcode secrets
- Never run privileged
- Never expose unnecessary ports

---

## 5. Networking

### DO ✅
- Internal network for services
- Public network only for proxy
- Database NOT on public network
- Use service discovery (names)

---

> **Mantra**: Simple → Minimal → Secure

# Docker & Infrastructure Rules

> **Senior DevOps & Docker Compose Architect**

---

## ⚡ Core Mission

Design secure, production-ready Docker Compose setups with:
- Least privilege
- Clean networking
- Observability
- Modular configuration

---

## 📁 Folder Structure

```
deployments/
└── docker/
    ├── docker-compose.yml
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    ├── backend/
    │   ├── Dockerfile
    │   └── env.example
    ├── frontend/
    │   ├── Dockerfile
    │   └── env.example
    └── proxy/
        ├── Dockerfile
        └── traefik.yml
```

---

## 🔧 Docker Compose Rules

### Services

- Use version "3.8" or higher
- Clear, descriptive service names
- Dedicated Dockerfile per service
- Environment from `.env` files (never inline)
- `healthcheck` on every service
- `restart: unless-stopped`

### Networks

Define at least:
- `internal_net` — backend ↔ DB/cache
- `public_net` — frontend/proxy

**RULE:** Databases/caches MUST NOT be on `public_net`

### Volumes

- Named volumes (no anonymous)
- Each stateful service = own volume
- Explicit host paths when needed

---

## 🔒 Security Rules

### Container Security

```yaml
# MANDATORY
user: "1000:1000"           # Non-root
read_only: true             # Stateless services
security_opt:
  - no-new-privileges:true
```

### Base Images

Use minimal images:
- `python:3.x-slim`
- `node:20-alpine`
- `golang:1.x-alpine`

### Secrets

- NEVER hardcode in docker-compose.yml
- Use `.env` files or secret mounts
- No secrets in build args

### Reverse Proxy

If using Traefik/nginx:
- Request size limits
- Rate limiting
- Forward only necessary headers
- Block internal paths

---

## 🏥 Health & Observability

### Health Checks

Every service must:
- Expose `/health` or `/livez`
- Have Docker healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logging

- Log to stdout/stderr (12-factor)
- Structured JSON logs preferred
- Optionally bind to `logs/` directory

---

## 🚀 Production Checklist

- [ ] Non-root containers
- [ ] Minimal base images
- [ ] Health checks on all services
- [ ] restart: unless-stopped
- [ ] Networks properly isolated
- [ ] Named volumes
- [ ] No secrets in compose file
- [ ] Resource limits (cpu/memory)

---

## 📝 Example compose.yml

```yaml
services:
  backend:
    build: ./backend
    user: "1000:1000"
    read_only: true
    security_opt:
      - no-new-privileges:true
    environment:
      - DATABASE_URL=${DATABASE_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    networks:
      - internal_net
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - internal_net
    restart: unless-stopped

networks:
  internal_net:
    internal: true
  public_net:

volumes:
  db_data:
```

---

**Mantra: Secure → Isolated → Observable → Minimal**

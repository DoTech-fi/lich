# {{ cookiecutter.project_name }} - Quick Start Guide

## 🚀 Getting Started

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services
lich start

# 3. Stop services when done
lich stop
```

---

## 🌐 Service URLs

### Core Applications

| Service | URL | Description |
|---------|-----|-------------|
| **Web App** | http://localhost:3000 | Main application |
| **Admin Panel** | http://localhost:3002 | Administration dashboard |
| **Landing Page** | http://localhost:4321 | Public landing page |
| **API Docs** | http://localhost:8000/api/docs | Swagger API documentation |
| **API ReDoc** | http://localhost:8000/api/redoc | ReDoc API documentation |

### Infrastructure Services

| Service | URL | Description |
|---------|-----|-------------|
| **Traefik Dashboard** | http://localhost:8090 | Reverse proxy dashboard |
{%- if cookiecutter.database == 'postgresql' %}
| **PostgreSQL** | localhost:5432 | Database (user: app, db: {{ cookiecutter.project_slug }}) |
{%- else %}
| **MongoDB** | localhost:27017 | Database |
{%- endif %}
{%- if cookiecutter.use_redis == 'yes' %}
| **Redis** | localhost:6379 | Cache server |
{%- endif %}
| **Adminer** | http://localhost:8091 | Database UI |

{%- if cookiecutter.auth_strategy == 'keycloak' %}

### Authentication

| Service | URL | Credentials |
|---------|-----|-------------|
| **Keycloak Admin** | http://localhost:8080 | admin / admin |
| **Keycloak Realm** | http://localhost:8080/realms/{{ cookiecutter.project_slug }} | Your app realm |

To setup Keycloak:
```bash
./scripts/setup-keycloak.sh
```
{%- endif %}

{%- if cookiecutter.task_runner == 'temporal' %}

### Background Jobs

| Service | URL | Description |
|---------|-----|-------------|
| **Temporal UI** | http://localhost:8088 | Workflow management |
| **Temporal Server** | localhost:7233 | Temporal gRPC |
{%- endif %}

{%- if cookiecutter.landing_backend == 'wordpress_api' %}

### CMS

| Service | URL | Description |
|---------|-----|-------------|
| **WordPress** | http://localhost:8081 | CMS admin |
| **WP REST API** | http://localhost:8081/wp-json/wp/v2 | WordPress API |
{%- endif %}

---

## 📁 Project Structure

```
{{ cookiecutter.project_slug }}/
├── apps/
│   ├── web/          # Next.js main app (:3000)
│   ├── admin/        # Next.js admin panel (:3002)
│   └── landing/      # Astro landing page (:4321)
├── backend/          # FastAPI backend (:8000)
{%- if cookiecutter.use_tls == 'yes' %}
├── certs/            # TLS certificates
{%- endif %}
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── docker-compose.yml
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

{%- if cookiecutter.database == 'postgresql' %}
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` - PostgreSQL credentials
{%- else %}
- `MONGODB_USER`, `MONGODB_PASSWORD`, `MONGODB_DB` - MongoDB credentials
{%- endif %}
{%- if cookiecutter.use_redis == 'yes' %}
- `REDIS_HOST`, `REDIS_PORT` - Redis connection
{%- endif %}
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
- `JWT_SECRET_KEY` - JWT signing key (CHANGE THIS!)
{%- elif cookiecutter.auth_strategy == 'keycloak' %}
- `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID` - Keycloak config
{%- endif %}
{%- if cookiecutter.use_tls == 'yes' %}
- `DOMAIN_NAME` - Your domain for TLS ({{ cookiecutter.domain_name }})
{%- endif %}

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements.txt
pytest -v

# Frontend tests
cd apps/web
npm test
```

---

## 📚 Documentation

- [Development Setup](docs/onboarding/dev-setup.md)
- [Architecture Overview](docs/architecture/system-overview.md)
- [API Guide](docs/runbooks/backend/api-guide.md)
- [Contribution Guide](docs/onboarding/contribution-guide.md)

---

## 🆘 Troubleshooting

See [docs/troubleshooting/](docs/troubleshooting/) for common issues.

**Port conflicts?**
```bash
lich stop  # Stop all services and clean ports
```

**Check service status?**
```bash
docker ps
curl http://localhost:8000/health
```

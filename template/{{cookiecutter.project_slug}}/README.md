# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

---

## 🚀 Quick Start

```bash
# Start all services
./dev-start.sh

# Stop all services
./dev-stop.sh
```

## 📍 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Web App | http://localhost:3000 | Main application |
| Admin Panel | http://localhost:3002 | Administration dashboard |
| Landing Page | http://localhost:4321 | Public landing page |
| API Docs | http://localhost:8000/api/docs | Swagger documentation |
{%- if cookiecutter.auth_strategy == 'keycloak' %}
| Keycloak | http://localhost:8080 | Identity management |
{%- endif %}
| Adminer | http://localhost:8090 | Database management |

## 🏗️ Architecture

This project follows the **Lich Architecture** - a clean, modular approach based on:

- **Hexagonal Architecture** (Ports & Adapters)
- **Clean Code** principles
- **SOLID** design patterns
- **Security-first** development

```
{{ cookiecutter.project_slug }}/
├── backend/              # FastAPI Backend (Lich Architecture)
│   ├── internal/
│   │   ├── entities/     # Pure domain models
│   │   ├── services/     # Business logic
│   │   ├── ports/        # Interfaces
│   │   └── adapters/     # Implementations
│   └── api/http/         # REST endpoints
├── apps/
│   ├── web/              # Next.js Main App
│   ├── admin/            # Next.js Admin Panel
│   └── landing/          # Astro Landing Page
├── docs/                 # Documentation
└── deployments/          # Docker configs
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12+, FastAPI |
| Frontend | Next.js 14+, TypeScript |
| Landing | Astro |
| Database | {{ cookiecutter.database | capitalize }} |
{%- if cookiecutter.use_redis == 'yes' %}
| Cache | Redis |
{%- endif %}
{%- if cookiecutter.auth_strategy == 'keycloak' %}
| Auth | Keycloak |
{%- elif cookiecutter.auth_strategy == 'jwt_builtin' %}
| Auth | JWT (Built-in) |
{%- endif %}
| Container | Docker, Docker Compose |

## 📚 Documentation

- [Development Setup](docs/onboarding/dev-setup.md)
- [Architecture Overview](docs/architecture/system-overview.md)
- [API Guide](docs/runbooks/backend/api-guide.md)
- [Contribution Guide](docs/onboarding/contribution-guide.md)

## 🔐 Security

This project follows security best practices:

- ✅ No hardcoded secrets
- ✅ Input validation everywhere
- ✅ Secure token handling
- ✅ Rate limiting
- ✅ Non-root Docker containers
- ✅ Parameterized SQL queries

## 📝 License

Copyright © {{ cookiecutter.author_name }}

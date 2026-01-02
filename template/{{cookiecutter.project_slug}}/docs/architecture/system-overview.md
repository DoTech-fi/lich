# System Overview

> معماری کلی سیستم {{ cookiecutter.project_name }}

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           Users                                  │
└─────────────────────────┬──────────────────────┬────────────────┘
                          │                      │
              ┌───────────▼──────────┐ ┌────────▼─────────┐
              │   Landing Page       │ │   Web App        │
              │   (Astro :4321)      │ │   (Next.js :3000)│
              └───────────┬──────────┘ └────────┬─────────┘
                          │                      │
                          │    ┌─────────────────┴──────────┐
                          │    │                            │
              ┌───────────▼────▼───────┐   ┌────────────────▼──────┐
              │      Traefik           │   │    Admin Panel        │
              │   (Reverse Proxy :80)  │   │   (Next.js :3002)     │
              └───────────┬────────────┘   └────────────────┬──────┘
                          │                                  │
              ┌───────────▼──────────────────────────────────▼─────┐
              │                    Backend API                      │
              │                   (FastAPI :8000)                   │
              │     ┌─────────────────────────────────────────┐    │
              │     │           Lich Architecture              │    │
              │     │  ┌─────────┐  ┌──────────┐  ┌─────────┐ │    │
              │     │  │ Entities│→ │ Services │→ │   API   │ │    │
              │     │  └─────────┘  └────┬─────┘  └─────────┘ │    │
              │     │                    │                     │    │
              │     │              ┌─────▼─────┐               │    │
              │     │              │   Ports   │               │    │
              │     │              └─────┬─────┘               │    │
              │     │                    │                     │    │
              │     │            ┌───────▼───────┐             │    │
              │     │            │   Adapters    │             │    │
              │     │            └───────────────┘             │    │
              │     └─────────────────────────────────────────┘    │
              └───────────┬──────────────────────────────┬─────────┘
                          │                              │
              ┌───────────▼──────────┐      ┌────────────▼─────────┐
              │     {{ cookiecutter.database | capitalize }}       │      │        Redis         │
              │      (Data Store)    │      │       (Cache)        │
              └──────────────────────┘      └──────────────────────┘
```

## Components

### Frontend
- **Landing Page** (Astro) - Public marketing site
- **Web App** (Next.js) - Main application
- **Admin Panel** (Next.js) - Administration dashboard

### Backend
- **API** (FastAPI) - RESTful API with Swagger docs
- **Architecture** - Lich Architecture (Clean/Hexagonal)

### Infrastructure
- **Database** - {{ cookiecutter.database | capitalize }}
{%- if cookiecutter.use_redis == 'yes' %}
- **Cache** - Redis
{%- endif %}
{%- if cookiecutter.auth_strategy == 'keycloak' %}
- **Auth** - Keycloak
{%- endif %}
- **Proxy** - Traefik

## Data Flow

1. User accesses Frontend
2. Frontend calls Backend API
3. API validates request (DTO)
4. Service executes business logic
5. Adapter interacts with database
6. Response flows back through layers

## Security

- All API calls require authentication
- Tokens stored in secure httpOnly cookies
- Input validation at every layer
- Rate limiting on public endpoints

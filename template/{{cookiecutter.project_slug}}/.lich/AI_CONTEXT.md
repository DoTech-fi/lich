# AI Context - {{ cookiecutter.project_name }}

> This file contains all context an AI needs to work with this project.

## Project Identity

```yaml
name: {{ cookiecutter.project_name }}
slug: {{ cookiecutter.project_slug }}
type: {{ cookiecutter.project_type }}
description: {{ cookiecutter.project_description }}
author: {{ cookiecutter.author_name }}
email: {{ cookiecutter.author_email }}
```

## Configuration

```yaml
authentication: {{ cookiecutter.auth_strategy }}
database: {{ cookiecutter.database }}
cache: {{ cookiecutter.use_redis }}
i18n: {{ cookiecutter.use_i18n }}
default_language: {{ cookiecutter.default_language }}
tls: {{ cookiecutter.use_tls }}
domain: {{ cookiecutter.domain_name }}
structured_logging: {{ cookiecutter.use_structured_logging }}
landing_backend: {{ cookiecutter.landing_backend }}
temporal: {{ cookiecutter.use_temporal }}
```

## Architecture Type

This is a **{{ cookiecutter.project_type }}** project with:

{%- if cookiecutter.project_type == 'trading_platform' %}
- Real-time data requirements
- Chart/visualization components
- Portfolio management
- Trading operations
{%- elif cookiecutter.project_type == 'saas_platform' %}
- Multi-tenant architecture
- Subscription management
- User dashboards
- Admin panel
{%- elif cookiecutter.project_type == 'ecommerce' %}
- Product catalog
- Shopping cart
- Payment integration
- Order management
{%- elif cookiecutter.project_type == 'content_platform' %}
- Content management
- User-generated content
- Media handling
- SEO optimization
{%- else %}
- Internal workflows
- Team collaboration
- Data management
{%- endif %}

## What I Need to Know

### Backend Rules
- Follow Lich Architecture (`.lich/rules/backend.md`)
- Entities are pure domain models
- Services contain business logic
- Ports are interfaces, Adapters are implementations

### Frontend Rules
- Use CSS Modules (no Tailwind)
- TypeScript strict mode
- Component-per-file
- RTL support for {{ cookiecutter.default_language }}

### Security Rules
- See `.lich/rules/security.md`
- No localStorage for tokens
- Validate ALL inputs
- Non-root Docker containers

## When Making Changes

1. Follow the appropriate rule file in `.lich/rules/`
2. Write tests for new code
3. Update documentation
4. Update `agentlog.md` with WHAT, WHY, WHEN

## Available Workflows

See `.lich/workflows/` for:
- add-feature.md
- add-entity.md
- add-api.md
- create-landing.md

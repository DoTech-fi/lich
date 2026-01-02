# {{ cookiecutter.project_name }}

> This file helps AI assistants (Claude, GPT, etc.) understand this project.

## Project Overview

**Name**: {{ cookiecutter.project_name }}
**Type**: {{ cookiecutter.project_type }}
**Description**: {{ cookiecutter.project_description }}

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (TypeScript)
- **Landing**: Astro
- **Database**: {{ cookiecutter.database }}
{%- if cookiecutter.use_redis == 'yes' %}
- **Cache**: Redis
{%- endif %}
- **Auth**: {{ cookiecutter.auth_strategy }}

## Architecture

This project follows **Lich Architecture** principles.
Read `.lich/rules/` for detailed rules on each area.

## Key Files

```
.lich/
├── AI_CONTEXT.md         # This project's context & config
├── LICH_AI_PROMPT.md     # Master architecture prompt
├── PROJECT_CONFIG.yaml   # Machine-readable config
└── rules/                # Architecture rules
    ├── security.md
    ├── ui-ux.md
    ├── docker.md
    ├── backend.md
    ├── frontend.md
    ├── devops.md
    ├── platform.md
    ├── testing.md
    └── documentation.md
```

## Workflows

When asked to do something, check `.lich/workflows/` for step-by-step guides.

## Important Rules

1. **Always update `agentlog.md`** after changes
2. **Follow Lich Architecture** in `.lich/rules/backend.md`
3. **Security first** - see `.lich/rules/security.md`
4. **Simple > Complex** - don't over-engineer

## Quick Commands

```bash
./dev-start.sh      # Start all services
./dev-stop.sh       # Stop all services
cd backend && pytest  # Run tests
```

## Service URLs

- Web: http://localhost:3000
- Admin: http://localhost:3002
- Landing: http://localhost:4321
- API: http://localhost:8000/api/docs

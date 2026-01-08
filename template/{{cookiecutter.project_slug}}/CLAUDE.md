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

## 🚨 AI Rules (MANDATORY)
 
 1. **LICH-FIRST POLICY**: If a `lich` command exists for a task, you **MUST** use it.
    - Creating an entity? Use `lich make entity` (NOT manual file creation)
    - Migrating DB? Use `lich migration create` (NOT alembic direct)
    - Running tests? Use `lich test` (NOT pytest direct)
 2. **Context**: Read `.lich/rules/ai-behavior.md` for the full decision tree.
 3. **Agent Log**: Always append to `agentlog.md` after changes.
 
 ## 🛠️ Lich CLI Reference
 
 | Category | Command | Use For |
 |----------|---------|---------|
 | **Dev** | `lich start` | Start backend, frontend, db, docker |
 | | `lich stop` | Stop everything & clean ports |
 | | `lich check` | Validate project structure |
 | **Make** | `lich make entity <name>` | Generate Entity + Port + Adapter |
 | | `lich make service <name>` | Generate Service (Use Case) |
 | | `lich make api <name>` | Generate FastAPI Router |
 | | `lich make dto <name>` | Generate Pydantic DTOs |
 | | `lich make job <name>` | Generate Background Job |
 | **DB** | `lich migration create "msg"` | Create migration file |
 | | `lich migration up` | Apply migrations |
 | | `lich seed` | Seed database |
 | **QA** | `lich test` | Run tests |
 | | `lich lint` | Run linters (Ruff/ESLint) |
 | | `lich security` | Run security scans |
 | **Ops** | `lich deploy` | Deploy via Ansible |
 | | `lich production-ready` | Pre-deploy checks |

## Service URLs

- Web: http://localhost:3000
- Admin: http://localhost:3002
- Landing: http://localhost:4321
- API: http://localhost:8000/api/docs

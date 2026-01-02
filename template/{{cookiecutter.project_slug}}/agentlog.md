# {{ cookiecutter.project_name }} Agent Log

> این فایل تاریخچه تمام تغییرات پروژه رو ثبت می‌کنه. هر تغییر کد باید اینجا لاگ بشه.

---

## Initial Project Setup - Project Initialized

**What Changed**: 
- Initial project structure created via Lich Cookiecutter
- Backend (FastAPI) with Lich Architecture
- Frontend apps (Next.js web, admin) + Astro landing
- Docker Compose configuration
- Development scripts (dev-start.sh, dev-stop.sh)

**Why Changed**:
New project initialization based on {{ cookiecutter.project_description }}

**Configuration**:
- Project Type: {{ cookiecutter.project_type }}
- Auth Strategy: {{ cookiecutter.auth_strategy }}
- Database: {{ cookiecutter.database }}
{%- if cookiecutter.use_redis == 'yes' %}
- Cache: Redis
{%- endif %}
{%- if cookiecutter.use_temporal == 'yes' %}
- Background Jobs: Temporal
{%- endif %}
- i18n: {{ cookiecutter.use_i18n }}

**Files Created**:
- All project structure as per Lich Toolkit

---

<!-- Add new entries above this line -->

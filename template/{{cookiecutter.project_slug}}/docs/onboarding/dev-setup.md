# Development Setup

> راهنمای راه‌اندازی محیط توسعه {{ cookiecutter.project_name }}

## Prerequisites

1. **Docker** - برای دیتابیس و سرویس‌های کمکی
2. **Python 3.12+** - برای Backend
3. **Node.js 20+** - برای Frontend
4. **Git**

## Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd {{ cookiecutter.project_slug }}

# Copy environment file
cp .env.example .env

# Start development environment
./dev-start.sh
```

## Manual Setup

### 1. Start Docker Services

```bash
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 3. Web App Setup

```bash
cd apps/web
npm install
npm run dev
```

### 4. Admin Panel Setup

```bash
cd apps/admin
npm install
npm run dev
```

### 5. Landing Page Setup

```bash
cd apps/landing
npm install
npm run dev
```

## Service URLs

| Service | URL |
|---------|-----|
| Web App | http://localhost:3000 |
| Admin Panel | http://localhost:3002 |
| Landing Page | http://localhost:4321 |
| API Docs | http://localhost:8000/api/docs |
{%- if cookiecutter.auth_strategy == 'keycloak' %}
| Keycloak | http://localhost:8080 |
{%- endif %}
| Adminer | http://localhost:8091 |

## Stopping Services

```bash
./dev-stop.sh
```

## Troubleshooting

### Port Already in Use

```bash
lsof -ti :3000 | xargs kill -9
```

### Database Connection Failed

```bash
docker-compose logs postgres
```

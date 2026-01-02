# lich dev / lich stop

Start and stop the development environment.

## Usage

```bash
lich dev    # Start development
lich stop   # Stop development
```

## What It Does

`lich dev` starts your entire development environment:

1. **Docker containers** - PostgreSQL, Redis, and other services
2. **Backend** - FastAPI server with hot reload
3. **Frontend** - Next.js development server

## Example

```bash
$ lich dev

🚀 Starting Development Environment

📦 Starting Docker services...
  ✅ PostgreSQL running on port 5432
  ✅ Redis running on port 6379

🐍 Starting Backend...
  ✅ FastAPI running on http://localhost:8000

⚛️ Starting Frontend...
  ✅ Next.js running on http://localhost:3000

---
Development servers running!

URLs:
  Frontend:  http://localhost:3000
  Backend:   http://localhost:8000
  API Docs:  http://localhost:8000/docs
---
```

## Stopping Development

### Option 1: lich stop

```bash
lich stop
```

### Option 2: Ctrl+C

Press `Ctrl+C` in the terminal where `lich dev` is running.

## Services Started

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching |
| Backend API | 8000 | FastAPI |
| Frontend | 3000 | Next.js |

## Best Practices

### Check Individual Service Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

### Reset Docker Data

```bash
docker compose down -v  # Remove volumes
lich dev                # Fresh start
```

## Common Issues

### Port Already in Use

If you see "port already in use":

```bash
# Find and kill the process
lsof -i :8000
kill <PID>

# Or use lich stop first
lich stop
lich dev
```

### Docker Not Running

Make sure Docker Desktop is running before `lich dev`.

## See Also

- [`lich init`](init.md) - Create a project first
- [Configuration](../getting-started/configuration.md) - Environment setup

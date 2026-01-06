# Lich Framework - AI Agent Reference

> **این فایل برای AI Agent‌هاست که با Lich کار می‌کنن**
> هر وقت پروژه‌ای `.lich` folder داره یا با `lich init` ساخته شده، این دستورات رو استفاده کن.

---

## 🔍 Detection

اگه یکی از این‌ها وجود داشت، پروژه Lich هست:
- `.lich/` folder
- `lich.toml` file
- `internal/entities/` + `internal/services/` structure

---

## 📦 Commands Reference

### Project Management

```bash
lich init <name>        # ساخت پروژه جدید
lich adopt <path>       # تبدیل پروژه موجود به Lich
lich check              # بررسی ساختار پروژه
lich upgrade            # آپگرید به آخرین نسخه
lich version            # نسخه Lich
```

### Development

```bash
lich dev                # شروع dev environment (docker-compose up)
lich stop               # متوقف کردن dev environment
lich shell              # Python shell با context پروژه
lich routes             # لیست همه API endpoints
```

### Code Generation (lich make)

```bash
lich make entity <name>      # Entity + Port + Adapter
lich make service <name>     # Service (use case)
lich make api <name>         # FastAPI router
lich make dto <name>         # Pydantic DTO
lich make factory <name>     # Test factory
lich make middleware <name>  # FastAPI middleware
lich make event <name>       # Domain event
lich make listener <name>    # Event listener
lich make job <name>         # Background job (Celery task)
lich make policy <name>      # Authorization policy
```

### Database

```bash
lich migration init      # Initialize Alembic
lich migration create    # Create new migration
lich migration up        # Apply migrations
lich migration down      # Rollback migrations
lich migration status    # Show current status
lich migration heads     # Show available heads
```

### Testing

```bash
lich test                    # Run all tests
lich test -u                 # Unit tests only
lich test -i                 # Integration tests only
lich test -c                 # With coverage report
lich test -v                 # Verbose output
lich test -w                 # Watch mode
lich test path/to/test.py   # Specific test file
```

### Seeding

```bash
lich seed                # Run all seeders
lich seed users          # Run specific seeder
lich seed --fresh        # Reset DB + seed
lich seed --list         # List available seeders
```

### Middleware Management

```bash
lich middleware list         # List all middlewares
lich middleware enable <n>   # Enable middleware
lich middleware disable <n>  # Disable middleware
lich middleware enable-all   # Enable all
lich middleware disable-all  # Disable all
```

---

## 🧠 AI Usage Guidelines

### وقتی Entity/Service جدید می‌سازی:

```bash
# بجای write_to_file از این استفاده کن:
lich make entity payment
lich make service payment_service
lich make api payments

# بعد فایل‌های تولید شده رو view + edit کن
```

### وقتی می‌خوای endpoints رو ببینی:

```bash
# بجای grep از این استفاده کن:
lich routes
```

### وقتی migration می‌زنی:

```bash
# بجای alembic مستقیم:
lich migration create "add_payments_table"
lich migration up
lich migration status
```

### وقتی تست می‌زنی:

```bash
# با coverage:
lich test -c

# فقط unit tests:
lich test -u
```

---

## 📁 Lich Project Structure

```
project/
├── .lich/               # Lich config folder
├── internal/
│   ├── entities/        # Domain models
│   ├── services/        # Business logic
│   ├── ports/           # Repository interfaces
│   └── adapters/db/     # Repository implementations
├── api/http/            # FastAPI routers
├── pkg/                 # Shared utilities
├── seeds/               # Database seeders
├── tests/
│   ├── unit/
│   └── integration/
└── lich.toml            # Project config
```

---

## ⚡ Quick Decisions

| Scenario | Command |
|----------|---------|
| New entity needed | `lich make entity` |
| New API endpoint | `lich make api` |
| See all routes | `lich routes` |
| Run tests | `lich test -c` |
| Check project health | `lich check` |
| Database change | `lich migration create` → `up` |
| Seed test data | `lich seed --fresh` |

---

## 🚫 Don't Do

- ❌ Don't write entity files from scratch → use `lich make entity`
- ❌ Don't use `alembic` directly → use `lich migration`
- ❌ Don't grep for routes → use `lich routes`
- ❌ Don't run `pytest` directly → use `lich test`

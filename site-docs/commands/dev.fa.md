# lich dev / lich stop

راه‌اندازی و توقف محیط توسعه.

## استفاده

```bash
lich dev    # راه‌اندازی توسعه
lich stop   # توقف توسعه
```

## چه کاری انجام می‌دهد

`lich dev` کل محیط توسعه را راه‌اندازی می‌کند:

1. **کانتینرهای Docker** - PostgreSQL، Redis و سرویس‌های دیگر
2. **بک‌اند** - سرور FastAPI با hot reload
3. **فرانت‌اند** - سرور توسعه Next.js

## مثال

```bash
$ lich dev

🚀 راه‌اندازی محیط توسعه

📦 راه‌اندازی سرویس‌های Docker...
  ✅ PostgreSQL روی پورت 5432
  ✅ Redis روی پورت 6379

🐍 راه‌اندازی بک‌اند...
  ✅ FastAPI روی http://localhost:8000

⚛️ راه‌اندازی فرانت‌اند...
  ✅ Next.js روی http://localhost:3000

---
سرورهای توسعه در حال اجرا!

آدرس‌ها:
  فرانت‌اند:  http://localhost:3000
  بک‌اند:    http://localhost:8000
  مستندات API: http://localhost:8000/docs
---
```

## توقف توسعه

### گزینه ۱: lich stop

```bash
lich stop
```

### گزینه ۲: Ctrl+C

در ترمینالی که `lich dev` در حال اجراست `Ctrl+C` بزنید.

## سرویس‌های راه‌اندازی شده

| سرویس | پورت | کاربرد |
|---------|------|---------|
| PostgreSQL | 5432 | دیتابیس |
| Redis | 6379 | کشینگ |
| API بک‌اند | 8000 | FastAPI |
| فرانت‌اند | 3000 | Next.js |

## همچنین ببینید

- [`lich init`](init.md) - اول پروژه بسازید
- [تنظیمات](../getting-started/configuration.md) - راه‌اندازی محیط

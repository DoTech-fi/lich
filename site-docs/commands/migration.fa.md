# lich migration

دستورات migration دیتابیس با Alembic.

## دستورات

| دستور | توضیحات |
|---------|-------------|
| `lich migration init` | راه‌اندازی Alembic |
| `lich migration create "message"` | ساخت migration جدید |
| `lich migration up` | اعمال همه migrations |
| `lich migration down` | Rollback یک migration |
| `lich migration status` | نمایش وضعیت migration |

## راه‌اندازی Migrations

```bash
lich migration init
```

## ساخت Migration

```bash
lich migration create "add users table"
```

## اعمال Migrations

```bash
lich migration up
```

## Rollback

```bash
lich migration down
```

## بررسی وضعیت

```bash
lich migration status
```

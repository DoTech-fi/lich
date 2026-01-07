# lich backup

دستور `lich backup` بکاپ دیتابیس ایجاد و بازیابی می‌کند.

## استفاده

```bash
# ایجاد بکاپ
lich backup

# بکاپ با دیتابیس خاص
lich backup --database postgres

# آپلود به S3
lich backup --s3 my-bucket

# بازیابی از بکاپ
lich backup restore backup_2024.sql.gz

# لیست بکاپ‌ها
lich backup list
```

## دیتابیس‌های پشتیبانی شده

| دیتابیس | تشخیص |
|---------|-------|
| PostgreSQL | خودکار از docker-compose |
| MySQL | خودکار از docker-compose |
| MongoDB | خودکار از docker-compose |
| Redis | RDB dump |

## آپشن‌ها

| آپشن | توضیحات |
|------|---------|
| `--database, -d` | نوع دیتابیس |
| `--s3` | باکت S3 برای آپلود |
| `--output, -o` | دایرکتوری خروجی |

## زیردستورها

### `lich backup list`
لیست بکاپ‌های محلی

### `lich backup restore <file>`
بازیابی از فایل بکاپ

### `lich backup clean`
حذف بکاپ‌های قدیمی (نگهداری ۵ تای آخر)

## مثال‌ها

```bash
# ایجاد و آپلود به S3
lich backup --s3 my-backups

# بازیابی بکاپ خاص
lich backup restore backups/db_2024-01-07.sql.gz

# بازیابی تعاملی
lich backup restore
```

## محل ذخیره‌سازی

بکاپ‌ها ذخیره می‌شوند در:
- محلی: `./backups/db/`
- S3: `s3://<bucket>/backups/`

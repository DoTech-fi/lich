# lich seed

دستورات seed کردن دیتابیس.

## استفاده

```bash
lich seed [OPTIONS]
```

## گزینه‌ها

| گزینه | توضیحات |
|--------|-------------|
| `--fresh` | ریست DB قبل از seed |
| `--list` | لیست seederهای موجود |
| `--only NAME` | اجرای seeder خاص |

## مثال‌ها

```bash
# اجرای همه seeders
lich seed

# لیست seeders
lich seed --list

# اجرای seeder خاص
lich seed --only users
```

## مثال خروجی

```bash
$ lich seed

🌱 اجرای Seeders دیتابیس

  ✅ users_seeder - ۱۰ رکورد
  ✅ products_seeder - ۵۰ رکورد

انجام شد! ۶۰ رکورد seed شد.
```

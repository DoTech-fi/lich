# lich middleware

فعال یا غیرفعال کردن middlewareهای از پیش ساخته.

## Middlewareهای موجود

| Middleware | توضیحات |
|------------|-------------|
| `rate-limit` | جلوگیری از سوءاستفاده API |
| `logging` | لاگ همه درخواست‌ها |
| `security` | اضافه کردن هدرهای امنیتی |
| `timing` | اضافه کردن هدرهای زمان پاسخ |

## دستورات

```bash
# لیست همه middlewares
lich middleware list

# فعال کردن
lich middleware enable rate-limit

# غیرفعال کردن
lich middleware disable rate-limit
```

## مثال

```bash
$ lich middleware list

🛡️ Middlewareهای موجود:

  ❌ rate-limit   - محدودسازی نرخ (۶۰ درخواست/دقیقه)
  ❌ logging      - لاگ درخواست‌ها
  ❌ security     - هدرهای امنیتی
  ❌ timing       - زمان پاسخ

$ lich middleware enable security
✅ Middleware هدرهای امنیتی فعال شد!
```

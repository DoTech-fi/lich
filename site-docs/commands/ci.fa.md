# lich ci

دستور `lich ci` برای اجرای تست‌های CI به صورت لوکال با Docker/act یا مستقیم.

## راه‌اندازی

```bash
# راه‌اندازی اولیه (ساخت .secrets، .actrc)
lich ci setup
```

## استفاده

```bash
# اجرا با Docker/act (پیش‌فرض)
lich ci backend
lich ci web
lich ci admin
lich ci landing

# اجرا بدون Docker (لوکال)
lich ci backend -l
lich ci web -l
```

## دستورات

| دستور | توضیح |
|-------|-------|
| `lich ci setup` | راه‌اندازی act و ساخت .secrets |
| `lich ci backend` | CI پایتون (backend) |
| `lich ci web` | CI وب (TypeScript) |
| `lich ci admin` | CI پنل ادمین |
| `lich ci landing` | CI صفحه لندینگ |

## فلگ‌ها

| فلگ | توضیح |
|-----|-------|
| `-l, --local` | اجرا بدون Docker |
| `-v, --verbose` | خروجی بیشتر |
| `-q, --quiet` | حالت ساکت |
| `-s, --secret KEY=VALUE` | پاس دادن secret |
| `--var KEY=VALUE` | پاس دادن variable |
| `--insecure-secrets` | نمایش secret در لاگ |

## مثال‌ها

```bash
# Backend با Docker (پیش‌فرض)
lich ci backend

# Backend لوکال (سریع‌تر)
lich ci backend -l

# پاس دادن secret
lich ci backend -s GITHUB_TOKEN=ghp_xxx

# پاس دادن variable
lich ci backend --var NODE_ENV=test
```

## فایل‌های Workflow

هر کامپوننت workflow جداگانه با path-based trigger داره:

| کامپوننت | Workflow | مسیر Trigger |
|----------|----------|--------------|
| Backend | `ci-backend.yml` | `backend/**` |
| Web | `ci-web.yml` | `apps/web/**` |
| Admin | `ci-admin.yml` | `apps/admin/**` |
| Landing | `ci-landing.yml` | `apps/landing/**` |

فایل اصلی `ci.yml` فقط دستی از GitHub Actions UI اجرا میشه.

## فایل‌های ساخته‌شده با Setup

| فایل | کاربرد |
|------|--------|
| `.actrc` | تنظیمات act |
| `.secrets` | توکن GitHub و secret ها |
| `.ci-vars` | متغیرهای CI (اختیاری) |
| `.ci-env` | Environment کانتینر (اختیاری) |

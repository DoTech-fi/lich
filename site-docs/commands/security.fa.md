# lich security

دستور `lich security` اسکن‌های امنیتی جامع روی پروژه شما اجرا می‌کند.

## استفاده

```bash
# اجرای همه اسکن‌های امنیتی
lich security

# اسکن هدف خاص
lich security --target backend
lich security --target frontend
lich security --target docker
lich security --target secrets

# رفع خودکار مشکلات
lich security --fix

# خروجی JSON برای CI/CD
lich security --json
```

## اسکن‌های امنیتی

### اسکن بک‌اند
- **Bandit** - بررسی امنیت کد پایتون
- **Safety** - بررسی آسیب‌پذیری وابستگی‌ها

### اسکن فرانت‌اند
- **npm audit** - آسیب‌پذیری‌های Node.js

### اسکن سکرت‌ها
- **GitLeaks** - تشخیص سکرت‌های هاردکد شده
- **git-secrets** - تشخیص سکرت‌های AWS

### اسکن داکر
- **Trivy** - اسکنر آسیب‌پذیری کانتینر

## آپشن‌ها

| آپشن | توضیحات |
|------|---------|
| `--target, -t` | هدف اسکن: `backend`, `frontend`, `docker`, `secrets` |
| `--fix` | رفع خودکار مشکلات امنیتی |
| `--json` | خروجی به فرمت JSON |

## مثال‌ها

```bash
# بررسی امنیتی کامل
lich security

# فقط بک‌اند با رفع خودکار
lich security --target backend --fix

# استفاده در CI/CD
lich security --json > security-report.json
```

## کدهای خروج

| کد | معنی |
|----|------|
| `0` | بدون آسیب‌پذیری بحرانی |
| `1` | آسیب‌پذیری بحرانی پیدا شد |

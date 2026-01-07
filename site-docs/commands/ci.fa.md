# lich ci

دستور `lich ci` بررسی‌های CI را به صورت محلی قبل از push اجرا می‌کند.

## استفاده

```bash
# اجرای همه بررسی‌ها
lich ci

# اجرای هدف خاص
lich ci backend
lich ci web
lich ci admin
lich ci landing
```

## چه چیزی بررسی می‌شود

### بک‌اند
- **لینت** (ruff/flake8)
- **تایپ چکینگ** (mypy)
- **تست‌ها** (pytest)
- **امنیت** (bandit)

### فرانت‌اند
- **لینت** (eslint)
- **تایپ چکینگ** (tsc)
- **بیلد** (next build)
- **آدیت** (npm audit)

## زیردستورها

| دستور | توضیحات |
|-------|---------|
| `lich ci` | همه بررسی‌ها |
| `lich ci backend` | فقط بک‌اند |
| `lich ci web` | فقط وب اپ |
| `lich ci admin` | فقط پنل ادمین |
| `lich ci landing` | فقط لندینگ |

## مثال‌ها

```bash
# بررسی سریع قبل از کامیت
lich ci

# فقط تغییرات بک‌اند
lich ci backend

# بررسی کامل فرانت‌اند
lich ci web
```

## کدهای خروج

| کد | معنی |
|----|------|
| `0` | همه بررسی‌ها پاس شد |
| `1` | یک یا چند بررسی فیل شد |

## یکپارچه‌سازی

اضافه به git pre-push hook:

```bash
#!/bin/sh
lich ci || exit 1
```

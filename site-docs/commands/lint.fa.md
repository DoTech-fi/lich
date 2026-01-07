# lich lint

دستور `lich lint` لینت کد پروژه شما را اجرا می‌کند.

## استفاده

```bash
# لینت همه کدها
lich lint

# لینت هدف خاص
lich lint --target backend
lich lint --target frontend

# رفع خودکار مشکلات
lich lint --fix
```

## لینترهای استفاده شده

### بک‌اند (پایتون)
- **Ruff** (ترجیحی) - لینتر سریع پایتون
- **Flake8** (جایگزین) - بررسی سبک پایتون

### فرانت‌اند (TypeScript/JavaScript)
- **ESLint** - لینتر جاوااسکریپت/تایپ‌اسکریپت

## آپشن‌ها

| آپشن | توضیحات |
|------|---------|
| `--target, -t` | هدف: `backend`, `frontend` |
| `--fix` | رفع خودکار مشکلات لینت |

## مثال‌ها

```bash
# بررسی کامل لینت
lich lint

# بک‌اند با رفع خودکار
lich lint --target backend --fix

# فقط فرانت‌اند
lich lint --target frontend
```

## پیکربندی

### بک‌اند
در `pyproject.toml` یا `ruff.toml`:

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "W", "I"]
```

### فرانت‌اند
در `.eslintrc.js` یا `eslint.config.js`.

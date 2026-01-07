# lich secret

دستور `lich secret` سکرت‌ها و اعتبارنامه‌های امن را مدیریت می‌کند.

## استفاده

```bash
# تولید کلید سکرت جدید
lich secret generate

# تولید با طول خاص
lich secret generate --length 64

# چرخش سکرت‌ها
lich secret rotate

# بررسی قدرت سکرت
lich secret check
```

## زیردستورها

### `lich secret generate`
تولید سکرت‌های امن کریپتوگرافیک.

```bash
# پیش‌فرض (۳۲ کاراکتر)
lich secret generate

# طول سفارشی
lich secret generate --length 64

# فرمت هگز
lich secret generate --format hex

# کپی به کلیپ‌بورد
lich secret generate --copy
```

### `lich secret rotate`
چرخش سکرت‌ها در فایل `.env`.

```bash
# چرخش همه سکرت‌ها
lich secret rotate

# چرخش کلید خاص
lich secret rotate --key SECRET_KEY

# پیش‌نمایش بدون اعمال
lich secret rotate --dry-run
```

### `lich secret check`
بررسی امنیتی سکرت‌ها.

```bash
lich secret check
```

بررسی می‌کند:
- رمزهای ضعیف
- مقادیر پیش‌فرض
- سکرت‌های کوتاه (< ۳۲ کاراکتر)

## آپشن‌ها

| آپشن | توضیحات |
|------|---------|
| `--length, -l` | طول سکرت (پیش‌فرض: ۳۲) |
| `--format, -f` | فرمت: `base64`, `hex`, `alphanumeric` |
| `--copy, -c` | کپی به کلیپ‌بورد |
| `--dry-run` | پیش‌نمایش تغییرات |

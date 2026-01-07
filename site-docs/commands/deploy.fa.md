# lich deploy

دستور `lich deploy` پروژه شما را با استفاده از Ansible دیپلوی می‌کند.

## استفاده

```bash
# دیپلوی به staging
lich deploy --env staging

# دیپلوی به production
lich deploy --env production

# دیپلوی با هاست خاص
lich deploy --host user@server.com

# اجرای آزمایشی
lich deploy --dry-run
```

## پیش‌نیازها

- **Ansible** نصب شده
- دسترسی SSH به سرورها
- Inventory پیکربندی شده در `infra/ansible/inventory/`

## آپشن‌ها

| آپشن | توضیحات |
|------|---------|
| `--env, -e` | محیط: `staging`, `production` |
| `--host, -h` | سرور هدف (user@hostname) |
| `--key, -k` | مسیر کلید SSH |
| `--dry-run` | نمایش عملیات بدون اجرا |
| `--playbook, -p` | پلی‌بوک خاص |

## پلی‌بوک‌ها

| پلی‌بوک | توضیحات |
|---------|---------|
| `site.yml` | ستاپ کامل سرور |
| `update.yml` | بروزرسانی کد |
| `backup.yml` | ایجاد بکاپ |
| `rollback.yml` | بازگشت به نسخه قبلی |

## مثال‌ها

```bash
# دیپلوی کامل
lich deploy --env production

# فقط بروزرسانی
lich deploy --env production --playbook update.yml

# تست بدون اجرا
lich deploy --env staging --dry-run
```

## پیکربندی

ویرایش `infra/ansible/group_vars/all.yml`:

```yaml
project_name: myproject
app_domain: example.com
db_name: myproject_db
ssl_enabled: true
```

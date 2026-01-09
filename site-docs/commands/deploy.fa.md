# lich deploy

دستور `lich deploy` برای دیپلوی کردن کامپوننت‌ها به staging یا production.

## راه‌اندازی

```bash
# راه‌اندازی اولیه (یک بار)
lich deploy setup
```

Setup سوال میپرسه:
- محیط (staging/production/both)
- روش اتصال (SSH config یا دستی)
- مسیر deploy در سرور
- Runtime (docker-compose یا bare-metal)
- آدرس Git repository

## استفاده

```bash
# Deploy به staging
lich deploy stage backend
lich deploy stage admin

# Deploy به production (با تایید)
lich deploy prod backend
lich deploy prod admin --version v1.2.3

# بدون تایید
lich deploy prod backend --force
```

## دستورات

| دستور | توضیح |
|-------|-------|
| `lich deploy setup` | کانفیگ اولیه |
| `lich deploy stage <component>` | Deploy به staging |
| `lich deploy prod <component>` | Deploy به production |
| `lich deploy status` | نمایش کانفیگ فعلی |

## کامپوننت‌ها

کامپوننت‌های معتبر: `backend`, `web`, `admin`, `landing`

## فلگ‌ها

| فلگ | توضیح |
|-----|-------|
| `--version, -v` | نسخه/تگ خاص |
| `--dry-run` | پیش‌نمایش بدون اجرا |
| `--force, -f` | بدون تایید (فقط prod) |

## کانفیگ

ذخیره در `.lich/deploy.yml`:

```yaml
staging:
  connection: ssh-config
  ssh_name: myserver-stage
  path: /opt/app
  runtime: docker-compose

production:
  connection: ssh-config
  ssh_name: myserver-prod
  path: /opt/app
  runtime: docker-compose

git_repo: git@github.com:user/repo.git
private_repo: true
```

## Secrets

برای repo خصوصی، اضافه کن به `.secrets`:

```
GITHUB_TOKEN=ghp_your_token_here
```

## مثال‌ها

```bash
# Deploy ادمین به staging
lich deploy stage admin

# Deploy backend نسخه v1.2.3 به production
lich deploy prod backend --version v1.2.3

# پیش‌نمایش deployment
lich deploy stage web --dry-run

# بررسی کانفیگ
lich deploy status
```

# 🤖 یکپارچه‌سازی Lich MCP

!!! success "۴۷ ابزار MCP - کنترل کامل برای دستیارهای AI"

Lich MCP (Model Context Protocol) به دستیارهای هوش مصنوعی اجازه می‌دهد مستقیماً با پروژه لیچ شما تعامل کنند - تولید کد، اجرای تست، دیپلوی و غیره.

---

## 🎯 راه‌اندازی سریع

### ۱. نصب Lich CLI

```bash
pip install lich
```

### ۲. تنظیم ابزار AI شما

=== "Antigravity (گوگل)"

    **توصیه شده:** دستور `lich setup antigravity` را اجرا کنید.

    **تنظیم دستی:**
    فایل `~/.gemini/antigravity/mcp_config.json` را ویرایش/ایجاد کنید:

    ```json
    {
      "mcpServers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

=== "Claude Desktop"

    فایل زیر را ویرایش کنید:
    `~/Library/Application Support/Claude/claude_desktop_config.json`

    ```json
    {
      "mcpServers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

=== "Cursor"

    به تنظیمات Cursor اضافه کنید:

    ```json
    {
      "mcp.servers": {
        "lich": {
          "command": "lich",
          "args": ["serve"],
          "cwd": "/path/to/your/lich-project"
        }
      }
    }
    ```

---

## 🛠️ ابزارهای موجود (۴۷ ابزار)

### مدیریت پروژه

| ابزار | توضیحات |
|------|---------|
| `lich_init` | ایجاد پروژه جدید |
| `lich_check_project` | بررسی ساختار پروژه |
| `lich_version` | نمایش نسخه |
| `lich_upgrade` | ارتقا به آخرین نسخه |

### تولید کد (۱۰ ابزار)

| ابزار | توضیحات |
|------|---------|
| `lich_make_entity` | ایجاد entity دامنه |
| `lich_make_service` | ایجاد سرویس |
| `lich_make_api` | ایجاد کنترلر API |
| `lich_make_dto` | ایجاد DTO |
| `lich_make_factory` | ایجاد factory تست |
| `lich_make_middleware` | ایجاد middleware |
| `lich_make_event` | ایجاد رویداد دامنه |
| `lich_make_listener` | ایجاد شنونده رویداد |
| `lich_make_job` | ایجاد job پس‌زمینه |
| `lich_make_policy` | ایجاد سیاست مجوز |

### عملیات دیتابیس

| ابزار | توضیحات |
|------|---------|
| `lich_migration_init` | مقداردهی Alembic |
| `lich_migration_create` | ایجاد migration جدید |
| `lich_migration_up` | اعمال migration |
| `lich_migration_down` | برگشت migration |
| `lich_migration_status` | وضعیت migration |
| `lich_seed` | seed دیتابیس |
| `lich_routes` | لیست همه APIها |

### کیفیت

| ابزار | توضیحات |
|------|---------|
| `lich_lint_backend` | Lint پایتون |
| `lich_lint_frontend` | ESLint |
| `lich_test` | اجرای pytest |
| `lich_security_scan` | اسکن امنیتی |
| `lich_ci_all` | همه بررسی‌های CI |
| `lich_production_ready_check` | بررسی آمادگی production |

### مدیریت secret

| ابزار | توضیحات |
|------|---------|
| `lich_secret_generate` | تولید secret امن |
| `lich_secret_rotate` | چرخش secretها |
| `lich_secret_check` | بررسی قدرت secret |

### محیط توسعه

| ابزار | توضیحات |
|------|---------|
| `lich_dev_start` | شروع محیط توسعه |
| `lich_dev_stop` | توقف محیط توسعه |

### دیپلوی

| ابزار | توضیحات |
|------|---------|
| `lich_deploy` | دیپلوی با Ansible |
| `lich_backup` | عملیات بکاپ |

---

## 💬 مثال مکالمات

### ایجاد یک feature جدید

!!! example "شما → AI"
    "یک entity محصول با فیلدهای نام، قیمت و موجودی بساز، سپس سرویس و API برایش ایجاد کن."

AI استفاده می‌کند:

1. `lich_make_entity` → ایجاد `Product`
2. `lich_make_service` → ایجاد `ProductService`
3. `lich_make_api` → ایجاد کنترلر
4. `lich_migration_create` → ایجاد migration

---

## 🔒 نکات امنیتی

!!! warning "دیپلوی production"
    ابزارهای دیپلوی به‌صورت پیش‌فرض در حالت `dry_run` هستند.

---

## 📚 بیشتر بخوانید

- [همه دستورات CLI](../commands/overview.md)
- [راهنمای معماری](../architecture/overview.md)

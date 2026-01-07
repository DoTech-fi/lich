# نمای کلی دستورات

Lich CLI دستوراتی برای مدیریت پروژه، تولید کد، DevOps و امنیت ارائه می‌دهد.

## دسته‌بندی دستورات

### 🚀 مدیریت پروژه

| دستور | توضیحات |
|---------|-------------|
| [`lich init`](init.md) | ساخت پروژه جدید لیچ |
| [`lich dev`](dev.md) | راه‌اندازی سرورهای توسعه |
| `lich stop` | توقف سرورهای توسعه |
| [`lich shell`](shell.md) | باز کردن shell تعاملی پایتون |

### 🛠️ تولید کد

| دستور | توضیحات |
|---------|-------------|
| [`lich make entity`](make/entity.md) | ساخت entity دامین |
| [`lich make service`](make/service.md) | ساخت لایه سرویس |
| [`lich make api`](make/api.md) | ساخت API router |
| [`lich make dto`](make/dto.md) | ساخت data transfer objects |
| [`lich make factory`](make/factory.md) | ساخت factory تست |
| [`lich make middleware`](make/middleware.md) | ساخت middleware |
| [`lich make event`](make/event.md) | ساخت کلاس event |
| [`lich make listener`](make/listener.md) | ساخت event listener |
| [`lich make job`](make/job.md) | ساخت background job |
| [`lich make policy`](make/policy.md) | ساخت authorization policy |

### 🗃️ دیتابیس

| دستور | توضیحات |
|---------|-------------|
| [`lich migration`](migration.md) | دستورات migration دیتابیس |
| [`lich seed`](seed.md) | seed کردن دیتابیس |
| [`lich backup`](backup.fa.md) | ایجاد/بازیابی بکاپ |

### 🔒 امنیت

| دستور | توضیحات |
|---------|-------------|
| [`lich security`](security.fa.md) | اجرای اسکن‌های امنیتی |
| [`lich secret`](secret.fa.md) | مدیریت سکرت‌ها |
| [`lich lint`](lint.fa.md) | لینت کردن کد |

### 🚀 DevOps و CI/CD

| دستور | توضیحات |
|---------|-------------|
| [`lich deploy`](deploy.fa.md) | دیپلوی با Ansible |
| [`lich ci`](ci.fa.md) | اجرای بررسی‌های CI محلی |
| [`lich production-ready`](production-ready.fa.md) | بررسی آمادگی پروداکشن |

### 🔧 ابزارها

| دستور | توضیحات |
|---------|-------------|
| [`lich middleware`](middleware.md) | فعال/غیرفعال کردن middlewares |
| [`lich routes`](routes.md) | لیست همه API routes |
| [`lich test`](test.md) | اجرای تست‌ها |
| `lich version` | نمایش اطلاعات نسخه |

## دریافت کمک

همه دستورات `--help` را پشتیبانی می‌کنند:

```bash
lich --help                  # کمک اصلی
lich make --help             # کمک دستورات Make
lich migration --help        # کمک Migration
lich security --help         # کمک اسکن امنیتی
lich deploy --help           # کمک دیپلوی
```

## زمینه دستور

بیشتر دستورات نیاز دارند در دایرکتوری پروژه لیچ باشید (پوشه `.lich/` داشته باشد):

```bash
cd your-lich-project
lich make entity User     # ✅ کار می‌کند

cd /some/other/folder
lich make entity User     # ❌ پروژه لیچ نیست!
```


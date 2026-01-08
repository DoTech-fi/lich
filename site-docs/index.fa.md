# 🧙 لیچ تولکیت

<div align="center">

<h1 style="font-size: 3rem; margin-bottom: 0;">فریم‌ورک فول‌استک هوش مصنوعی</h1>

<p style="font-size: 1.3rem; color: #888; margin-top: 10px;">
یک CLI. یک معماری. بی‌نهایت امکانات.<br/>
<strong>انسان و هوش مصنوعی یک زبان صحبت می‌کنند.</strong>
</p>

<div style="margin: 2rem 0;">
<a href="getting-started/quickstart/" class="md-button md-button--primary" style="margin: 5px;">🚀 شروع کنید</a>
<a href="integrations/mcp/" class="md-button" style="margin: 5px;">🤖 یکپارچه‌سازی MCP</a>
</div>

</div>

---

## 🎯 چرا لیچ؟

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } **توسعه با هوش مصنوعی**

    ---
    
    Lich MCP به دستیارهای هوش مصنوعی (Antigravity، Claude، Cursor) اجازه می‌دهد کل استک شما را با **۴۷ ابزار MCP** کنترل کنند.

-   :material-swap-horizontal:{ .lg .middle } **مونولیتیک و میکروسرویس**

    ---
    
    به عنوان مونولیت شروع کنید، به میکروسرویس مقیاس دهید. **Docker Compose** برای توسعه، **Docker Swarm** برای تولید.

-   :material-rocket-launch:{ .lg .middle } **یک SSH = دیپلوی شد**

    ---
    
    `lich deploy production` - همین! Ansible همه چیز را مدیریت می‌کند: SSL، پراکسی معکوس، دیتابیس، بکاپ.

-   :material-magnify:{ .lg .middle } **Landing سئو-محور**

    ---
    
    صفحه فرود Astro با backbone وردپرس. رندر سمت سرور، فوق‌العاده سریع، **امتیاز Lighthouse ۱۰۰**.

</div>

---

## ⚡ استک کامل

```
┌─────────────────────────────────────────────────────────────────┐
│                         پروژه شما                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎨 طراحی    →    ⚛️ فرانت‌اند    →    🐍 بک‌اند    →    🚀 دیپلوی   │
│                                                                 │
│   ┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────┐ │
│   │ Figma   │     │ Next.js   │     │ FastAPI  │     │Ansible│ │
│   │         │     │ + Admin   │     │ + Redis  │     │+ SSH  │ │
│   └─────────┘     └───────────┘     └──────────┘     └───────┘ │
│                                                                 │
│   ┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────┐ │
│   │ Landing │     │TypeScript │     │PostgreSQL│     │Traefik│ │
│   │ (Astro) │     │+ Tailwind │     │+ Alembic │     │+ SSL  │ │
│   └─────────┘     └───────────┘     └──────────┘     └───────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                    🤖 Lich MCP (۴۷ ابزار)
                              ↕
              ┌───────────────────────────────┐
              │ Antigravity │ Claude │ Cursor │
              └───────────────────────────────┘
```

---

## 🤖 Lich MCP - هوش مصنوعی با استک شما صحبت می‌کند

!!! success "۴۷ ابزار MCP برای کنترل کامل"

دستیار هوش مصنوعی شما اکنون می‌تواند:

| دسته‌بندی | کاری که AI انجام می‌دهد |
|----------|---------------|
| **تولید کد** | ایجاد entity، service، API، DTO، event، job |
| **دیتابیس** | اجرای migration، seed داده، بررسی وضعیت |
| **توسعه** | شروع/توقف محیط توسعه، مدیریت middleware |
| **کیفیت** | Lint کد، اجرای تست، اسکن امنیتی |
| **دیپلوی** | دیپلوی به staging/production، مدیریت بکاپ |
| **رمزها** | تولید، چرخش، اعتبارسنجی secret‌ها |

```bash
# نصب MCP در ابزار AI شما
pip install lich
lich serve  # شروع سرور MCP
```

[:octicons-arrow-right-24: راهنمای کامل یکپارچه‌سازی MCP](integrations/mcp.md)

---

## 🚀 از صفر تا Production در ۵ دقیقه

=== "۱. نصب"

    ```bash
    pip install lich
    ```

=== "۲. ایجاد پروژه"

    ```bash
    lich init
    # چند سوال پاسخ دهید...
    ```

=== "۳. توسعه"

    ```bash
    cd my-project
    lich start
    # فرانت‌اند: http://localhost:3000
    # ادمین: http://localhost:3002  
    # بک‌اند: http://localhost:8000
    ```

=== "۴. دیپلوی"

    ```bash
    lich deploy production
    # ✅ SSL تنظیم شد
    # ✅ دیتابیس migrate شد
    # ✅ بکاپ زمان‌بندی شد
    ```

---

## 📦 چه چیزی دریافت می‌کنید

<div class="grid" markdown>

<div markdown>

### استک فرانت‌اند

- ⚛️ **Next.js 14+** - App Router، Server Components
- 🎨 **Tailwind CSS** - استایل utility-first
- 📝 **TypeScript** - امنیت نوع کامل
- 🔐 **Auth آماده** - JWT یا Keycloak SSO
- 📊 **پنل ادمین** - داشبورد از پیش ساخته شده

</div>

<div markdown>

### استک بک‌اند

- 🐍 **FastAPI** - Python پرفورمنس بالا
- 🏛️ **معماری تمیز** - اصول SOLID
- 🗃️ **PostgreSQL/MongoDB** - انتخاب شما
- ⚡ **Redis** - کشینگ و session
- 📋 **Alembic** - migration دیتابیس

</div>

<div markdown>

### استک DevOps

- 🐳 **Docker Compose** - توسعه محلی
- 🐝 **Docker Swarm** - مقیاس‌دهی production
- 🔒 **Traefik** - پراکسی معکوس + SSL
- 📦 **Ansible** - دیپلوی یک‌دستوری
- 🔄 **GitHub Actions** - پایپ‌لاین CI/CD

</div>

<div markdown>

### استک SEO

- ⭐ **Astro Landing** - استاتیک، سریع، بهینه‌شده SEO
- 📝 **WordPress API** - مدیریت محتوا
- 🔍 **Lighthouse 100** - امتیازات عالی
- 🌐 **آماده i18n** - پشتیبانی چند زبانه

</div>

</div>

---

## 🏛️ معماری SOLID

هر پروژه لیچ از اصول **Clean Architecture** پیروی می‌کند:

```
backend/
├── api/http/           # کنترلرها (لایه نازک)
├── internal/
│   ├── entities/       # مدل‌های دامنه و قوانین کسب‌وکار
│   ├── services/       # Use caseها (منطق برنامه)
│   ├── ports/          # اینترفیس‌ها (چه چیزی نیاز داریم)
│   └── adapters/       # پیاده‌سازی‌ها (چگونه انجام می‌دهیم)
├── dto/                # شکل Request/Response
└── validators/         # اعتبارسنجی ورودی
```

!!! tip "قوانین یکسان برای انسان و AI"
    پوشه `.lich/rules/` شامل قوانین معماری است که هم توسعه‌دهندگان و هم دستیارهای AI از آن پیروی می‌کنند.

[:octicons-arrow-right-24: مطالعه عمیق معماری](architecture/overview.md)

---

## 🔧 قدرت CLI

<div class="grid cards" markdown>

-   **دستورات پروژه**
    
    ```bash
    lich init          # ایجاد پروژه
    lich start         # شروع محیط توسعه
    lich stop          # توقف همه چیز
    lich upgrade       # آپدیت به آخرین نسخه
    ```

-   **تولیدکننده‌های کد**
    
    ```bash
    lich make entity User
    lich make service Order
    lich make api Product
    lich make job SendEmail
    ```

-   **عملیات دیتابیس**
    
    ```bash
    lich migration create "add_users"
    lich migration up
    lich seed users
    lich routes       # لیست همه APIها
    ```

-   **کیفیت و دیپلوی**
    
    ```bash
    lich ci            # اجرای همه بررسی‌ها
    lich production-ready
    lich deploy staging
    lich backup create
    ```

</div>

[:octicons-arrow-right-24: مرجع همه دستورات](commands/overview.md)

---

## 🌐 URLهای توسعه

وقتی `lich start` اجرا می‌کنید:

| سرویس | URL | توضیحات |
|---------|-----|-------------|
| 🖥️ **فرانت‌اند** | http://localhost:3000 | اپلیکیشن وب اصلی |
| 👔 **پنل ادمین** | http://localhost:3002 | داشبورد مدیریت |
| 🚀 **Landing** | http://localhost:4321 | صفحه بازاریابی/SEO |
| 🐍 **API بک‌اند** | http://localhost:8000 | بک‌اند FastAPI |
| 📚 **مستندات API** | http://localhost:8000/docs | Swagger UI |
| 🗃️ **Adminer** | http://localhost:8081 | ادمین دیتابیس |

---

## 📚 سفر خود را شروع کنید

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **نصب**

    ---

    Lich CLI را روی سیستم خود نصب کنید.

    [:octicons-arrow-right-24: همین الان نصب کنید](getting-started/installation.md)

-   :material-play:{ .lg .middle } **شروع سریع**

    ---

    اولین پروژه خود را در ۵ دقیقه بسازید.

    [:octicons-arrow-right-24: بزن بریم](getting-started/quickstart.md)

-   :material-robot:{ .lg .middle } **یکپارچه‌سازی MCP**

    ---

    دستیار AI خود را به لیچ متصل کنید.

    [:octicons-arrow-right-24: تنظیم MCP](integrations/mcp.md)

-   :material-book:{ .lg .middle } **راهنمای معماری**

    ---

    الگوها و اصول را درک کنید.

    [:octicons-arrow-right-24: بیشتر بخوانید](architecture/overview.md)

</div>

---

<div align="center" style="margin-top: 3rem;">

**ساخته شده با ❤️ توسط [DoTech](https://github.com/DoTech-fi)**

*جایی که توسعه‌دهندگان و عامل‌های AI با هم می‌سازند.*

</div>

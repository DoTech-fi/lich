# تنظیمات

هر پروژه لیچ یک پوشه `.lich/` دارد که شامل تنظیمات و قوانین AI است.

## تنظیمات پروژه

```
your-project/
├── .lich/
│   ├── config.yml        # تنظیمات پروژه
│   └── rules/            # قوانین AI
├── .env                  # متغیرهای محیطی
└── docker-compose.yml    # سرویس‌های Docker
```

## متغیرهای محیطی

یک فایل `.env` در ریشه پروژه بسازید:

```env
# دیتابیس
DB_HOST=localhost
DB_PORT=5432
DB_USER=app_user
DB_PASSWORD=your_password
DB_NAME=app_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT (اگر از jwt_builtin استفاده می‌کنید)
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Keycloak (اگر از keycloak استفاده می‌کنید)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=your-client
```

!!! warning "تولید"
    هرگز فایل‌های `.env` را commit نکنید. در تولید از secret manager استفاده کنید.

## تنظیمات قوانین AI

پوشه `.lich/rules/` شامل فایل‌های markdown است که دستیارهای AI را راهنمایی می‌کنند:

```
.lich/rules/
├── backend.md      # قوانین معماری بک‌اند
├── frontend.md     # الگوهای فرانت‌اند
├── lich-cli.md     # مرجع دستورات CLI
└── master-prompt.md  # قوانین ترکیبی
```

## مراحل بعدی

[:octicons-arrow-right-24: یادگیری دستورات CLI](../commands/overview.md)

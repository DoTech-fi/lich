# lich make - نمای کلی

دستور `lich make` کد تولید می‌کند که از الگوهای معماری لیچ پیروی می‌کند.

## چرا از تولید کد استفاده کنیم؟

| مزیت | توضیحات |
|---------|-------------|
| ⚡ **سرعت** | boilerplate را در چند ثانیه بسازید |
| 🎯 **یکپارچگی** | همیشه از قوانین معماری پیروی می‌کند |
| 📁 **مکان صحیح** | فایل‌ها در پوشه‌های درست قرار می‌گیرند |
| ✨ **بهترین شیوه‌ها** | کد تولید شده از الگوها پیروی می‌کند |

## تولیدکننده‌های موجود

| دستور | می‌سازد | مکان |
|---------|---------|----------|
| [`make entity`](entity.md) | مدل دامین | `backend/internal/entities/` |
| [`make service`](service.md) | منطق کسب‌وکار | `backend/internal/services/` |
| [`make api`](api.md) | API router | `backend/api/http/` |
| [`make dto`](dto.md) | Data transfer objects | `backend/internal/dto/` |
| [`make factory`](factory.md) | Factory تست | `backend/tests/factories/` |
| [`make middleware`](middleware.md) | HTTP middleware | `backend/api/middleware/` |
| [`make event`](event.md) | کلاس Event | `backend/internal/events/` |
| [`make listener`](listener.md) | Event listener | `backend/internal/listeners/` |
| [`make job`](job.md) | Background job | `backend/internal/jobs/` |
| [`make policy`](policy.md) | Authorization policy | `backend/internal/policies/` |

## الگوی استفاده

```bash
lich make <type> <Name>
```

- `<type>` - چه چیزی تولید شود (entity، service و...)
- `<Name>` - نام به صورت PascalCase (مثلاً `User`، `OrderItem`)

## گردش کار معمول

وقتی ویژگی جدید اضافه می‌کنید، به این ترتیب تولید کنید:

```bash
# ۱. مدل دامین
lich make entity Product

# ۲. منطق کسب‌وکار
lich make service Product

# ۳. API endpoints
lich make api products

# ۴. DTOهای درخواست/پاسخ
lich make dto Product

# ۵. Factory تست (اختیاری)
lich make factory Product
```

## دریافت کمک

```bash
lich make --help
lich make entity --help
```

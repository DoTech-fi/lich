# lich make service

ساخت service - لایه منطق کسب‌وکار.

## Service چیست؟

یک **service** شامل اینهاست:

- **Use cases** - عملیات کسب‌وکار
- **قوانین کسب‌وکار** - اعتبارسنجی و منطق
- **هماهنگ‌سازی** - orchestrate کردن entities و adapters

Serviceها توسط کنترلرهای API فراخوانی می‌شوند و repositoryها را صدا می‌زنند.

## استفاده

```bash
lich make service <Name>
```

## مثال

```bash
$ lich make service Order

✅ Service OrderService ساخته شد!

فایل‌های ساخته شده:
  backend/internal/services/order_service.py
```

## کد تولید شده

```python
class OrderService:
    def __init__(self, order_repository):
        self.order_repository = order_repository
    
    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """دریافت سفارش با ID."""
        return await self.order_repository.get_by_id(order_id)
    
    async def create_order(self, data: dict) -> Order:
        """ساخت سفارش جدید."""
        order = Order(**data)
        return await self.order_repository.save(order)
```

## چرا از Service استفاده کنیم؟

| مزیت | توضیحات |
|---------|-------------|
| 🎯 **مسئولیت واحد** | یک service برای هر دامین |
| 🧪 **قابل تست** | Mock کردن repository برای تست |
| 🔄 **قابل استفاده مجدد** | فراخوانی از API، CLI، jobs |
| 📦 **جداسازی** | بدون وابستگی به framework |

## گردش کار معمول

```bash
# ۱. اول entity بسازید
lich make entity Order

# ۲. service بسازید
lich make service Order

# ۳. API برای expose کردنش بسازید
lich make api orders
```

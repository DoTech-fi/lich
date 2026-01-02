# Services (سرویس‌ها)

Services شامل منطق کسب‌وکار و orchestrate کننده use cases هستند.

## مکان

```
backend/internal/services/
├── user_service.py
├── order_service.py
└── notification_service.py
```

## ساختار

```python
class OrderService:
    def __init__(self, order_repo, product_repo, payment_service):
        # تزریق وابستگی‌ها
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_service = payment_service
    
    async def place_order(self, user_id: UUID, items: list) -> Order:
        """
        Use case: ثبت سفارش.
        
        Orchestrate: اعتبارسنجی، پرداخت، ذخیره.
        """
        # ۱. اعتبارسنجی آیتم‌ها
        products = await self.product_repo.get_by_ids(...)
        
        # ۲. ساخت entity سفارش
        order = Order(user_id=user_id, items=items)
        
        # ۳. پردازش پرداخت
        await self.payment_service.charge(user_id, order.total)
        
        # ۴. ذخیره و برگرداندن
        return await self.order_repo.save(order)
```

## قوانین

1. **یک service برای هر دامین** - `UserService`، `OrderService`
2. **تزریق repositories** - هرگز داخل نسازید
3. **برگرداندن اشیاء دامین** - نه مدل‌های دیتابیس

## ساخت با CLI

```bash
lich make service Order
```

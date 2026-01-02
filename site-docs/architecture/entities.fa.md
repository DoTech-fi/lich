# Entities (موجودیت‌ها)

Entities هسته دامین شما هستند - نمایانگر مفاهیم کسب‌وکار.

## مکان

```
backend/internal/entities/
├── user.py
├── user_repository.py
├── product.py
└── product_repository.py
```

## محتوای یک Entity

```python
@dataclass
class Order:
    """Entity دامین سفارش."""
    
    # هویت
    id: UUID
    
    # خصوصیات
    user_id: UUID
    items: List[OrderItem]
    total: float
    status: str
    
    # متدهای دامین
    def calculate_total(self) -> float:
        """منطق کسب‌وکار اینجاست."""
        return sum(item.price * item.quantity for item in self.items)
    
    def can_cancel(self) -> bool:
        """قوانین دامین."""
        return self.status in ['pending', 'processing']
```

## قوانین

1. **بدون import از framework** - فقط Python خالص
2. **منطق دامین داخلی** - اعتبارسنجی، محاسبات
3. **جفت شده با Repository** - اینترفیس برای دسترسی داده

## ساخت با CLI

```bash
lich make entity Order
```

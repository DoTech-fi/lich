# lich make dto

ساخت Data Transfer Objects برای درخواست‌ها و پاسخ‌های API.

## DTO چیست؟

یک **DTO (Data Transfer Object)** تعریف می‌کند:

- **شکل درخواست** - چه داده‌ای API قبول می‌کند
- **شکل پاسخ** - چه داده‌ای API برمی‌گرداند
- **اعتبارسنجی** - اعتبارسنجی خودکار ورودی

## استفاده

```bash
lich make dto <Name>
```

## مثال

```bash
$ lich make dto Product

✅ DTO Product ساخته شد!

فایل‌های ساخته شده:
  backend/internal/dto/product_dto.py
```

## کد تولید شده

```python
from pydantic import BaseModel, Field

class CreateProductRequest(BaseModel):
    """درخواست ساخت محصول."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ProductResponse(BaseModel):
    """پاسخ محصول."""
    
    id: UUID
    name: str
    price: float
    created_at: datetime
```

## چرا از DTO استفاده کنیم؟

| مزیت | توضیحات |
|---------|-------------|
| ✅ **اعتبارسنجی** | Pydantic خودکار اعتبارسنجی می‌کند |
| 📖 **مستندسازی** | خودکار OpenAPI docs تولید می‌کند |
| 🔒 **امنیت** | کنترل اینکه چه داده‌ای expose شود |
| 🧪 **تست** | contract واضح برای تست‌ها |

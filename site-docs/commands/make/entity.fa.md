# lich make entity

ساخت entity دامین - هسته اصلی منطق کسب‌وکار شما.

## Entity چیست؟

یک **entity** نشان‌دهنده یک مفهوم کسب‌وکاری با این ویژگی‌هاست:

- **خصوصیات** - فیلدهای داده
- **اعتبارسنجی** - قوانین داده
- **رفتار** - متدهای منطق دامین

Entityها **قلب** معماری تمیز هستند.

## استفاده

```bash
lich make entity <Name>
```

## مثال

```bash
$ lich make entity Product

✅ Entity Product ساخته شد!

فایل‌های ساخته شده:
  backend/internal/entities/product.py
  backend/internal/entities/product_repository.py
```

## کد تولید شده

### فایل Entity (`product.py`)

```python
@dataclass
class Product:
    """Entity دامین Product."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    price: float = 0.0
    created_at: datetime = None
    
    # متدهای دامین را اینجا اضافه کنید
    def apply_discount(self, percent: float) -> None:
        """اعمال تخفیف روی قیمت."""
        self.price = self.price * (1 - percent / 100)
```

## چرا از Entity استفاده کنیم؟

| مزیت | توضیحات |
|---------|-------------|
| 🏛️ **منطق دامین** | قوانین کسب‌وکار را در entities نگه دارید |
| 🔒 **اعتبارسنجی** | داده همیشه معتبر است |
| 🧪 **قابل تست** | به راحتی unit test می‌شود |
| 🔄 **قابل استفاده مجدد** | همان entity در همه لایه‌ها |

## قراردادهای نام‌گذاری

| ✅ خوب | ❌ بد |
|---------|--------|
| `User` | `user` |
| `OrderItem` | `order_item` |
| `ProductCategory` | `productCategory` |

همیشه از **PascalCase** برای نام entity استفاده کنید.

## مراحل بعدی

بعد از ساخت entity:

```bash
# ساخت service (منطق کسب‌وکار)
lich make service Product

# ساخت API (endpoints)
lich make api products
```

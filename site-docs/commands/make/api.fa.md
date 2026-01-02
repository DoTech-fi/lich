# lich make api

ساخت API router - HTTP endpoints برای سرویس شما.

## استفاده

```bash
lich make api <name>
```

از نام‌گذاری **حروف کوچک جمع** استفاده کنید: `products`، `orders`، `users`.

## مثال

```bash
$ lich make api products

✅ API products ساخته شد!

فایل‌های ساخته شده:
  backend/api/http/products.py
```

## کد تولید شده

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/")
async def list_products():
    """دریافت همه محصولات."""
    return []

@router.get("/{id}")
async def get_product(id: UUID):
    """دریافت محصول با ID."""
    raise HTTPException(status_code=404)

@router.post("/", status_code=201)
async def create_product(data: dict):
    """ساخت محصول جدید."""
    return {"message": "Created"}
```

## ثبت Router

بعد از ساخت، در `backend/main.py` ثبت کنید:

```python
from api.http.products import router as products_router

app.include_router(products_router, prefix="/api/v1")
```

## Use Cases

| الگوی Endpoint | استفاده |
|-----------------|----------|
| `GET /products` | لیست همه |
| `GET /products/{id}` | دریافت یکی |
| `POST /products` | ساخت |
| `PUT /products/{id}` | بروزرسانی |
| `DELETE /products/{id}` | حذف |

## همچنین ببینید

- [`make dto`](dto.md) - نوع‌های درخواست/پاسخ
- [`make service`](service.md) - منطق کسب‌وکار

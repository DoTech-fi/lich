# لایه API

اینترفیس HTTP برای اپلیکیشن شما.

## مکان

```
backend/api/
├── http/              # Routers
│   ├── users.py
│   └── orders.py
└── middleware/        # Middlewares
    └── auth.py
```

## ساختار Router

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/")
async def list_orders(
    service: OrderService = Depends(get_order_service)
):
    return await service.list_all()

@router.post("/", status_code=201)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service)
):
    return await service.create(request.model_dump())
```

## قوانین

1. **کنترلرهای نازک** - منطق در services
2. **استفاده از DTOs** - اعتبارسنجی ورودی/خروجی
3. **هندل کردن خطاها** - برگرداندن کدهای HTTP مناسب
4. **تزریق وابستگی‌ها** - استفاده از FastAPI Depends

## ثبت Routers

در `main.py`:

```python
from api.http.orders import router as orders_router

app.include_router(orders_router, prefix="/api/v1")
```

## ساخت با CLI

```bash
lich make api orders
```

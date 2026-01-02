# API Layer

The HTTP interface for your application.

## Location

```
backend/api/
├── http/              # Routers
│   ├── users.py
│   └── orders.py
└── middleware/        # Middlewares
    └── auth.py
```

## Router Structure

```python
from fastapi import APIRouter, Depends, HTTPException

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

## Rules

1. **Thin controllers** - Logic in services
2. **Use DTOs** - Validate input/output
3. **Handle errors** - Return proper HTTP codes
4. **Inject dependencies** - Use FastAPI Depends

## Register Routers

In `main.py`:

```python
from api.http.orders import router as orders_router

app.include_router(orders_router, prefix="/api/v1")
```

## Create with CLI

```bash
lich make api orders
```

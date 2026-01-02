# راهنمای تست

بهترین شیوه‌ها برای تست اپلیکیشن‌های لیچ.

## ساختار تست

```
backend/tests/
├── unit/
│   ├── test_user_service.py
│   └── test_order_service.py
├── integration/
│   └── test_api_orders.py
├── factories/
│   └── user_factory.py
└── conftest.py
```

## تست‌های Unit

تست services با mock شده repositories:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def order_service():
    mock_repo = AsyncMock()
    return OrderService(order_repository=mock_repo)

async def test_create_order(order_service):
    order_service.order_repository.save.return_value = Order(id=uuid4())
    
    result = await order_service.create({"user_id": "123"})
    
    assert result.id is not None
```

## تست‌های Integration

تست endpointهای واقعی API:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_list_orders():
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
```

## اجرای تست‌ها

```bash
lich test               # همه تست‌ها
lich test --unit        # فقط unit
lich test --coverage    # با coverage
```

## اهداف Coverage

| لایه | هدف |
|-------|--------|
| Services | ۹۰%+ |
| Entities | ۸۰%+ |
| API | ۷۰%+ |

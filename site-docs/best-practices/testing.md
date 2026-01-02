# Testing Guide

Best practices for testing Lich applications.

## Test Structure

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

## Unit Tests

Test services with mocked repositories:

```python
import pytest
from unittest.mock import AsyncMock
from internal.services.order_service import OrderService

@pytest.fixture
def order_service():
    mock_repo = AsyncMock()
    return OrderService(order_repository=mock_repo)

async def test_create_order(order_service):
    order_service.order_repository.save.return_value = Order(id=uuid4())
    
    result = await order_service.create({"user_id": "123"})
    
    assert result.id is not None
    order_service.order_repository.save.assert_called_once()
```

## Integration Tests

Test actual API endpoints:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_orders():
    response = client.get("/api/v1/orders")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Using Factories

```python
from tests.factories.user_factory import UserFactory

def test_with_factory():
    user = UserFactory.create(email="test@example.com")
    
    assert user.email == "test@example.com"
```

## Running Tests

```bash
lich test               # All tests
lich test --unit        # Unit only
lich test --coverage    # With coverage
lich test --watch       # Watch mode
```

## Coverage Goals

| Layer | Target |
|-------|--------|
| Services | 90%+ |
| Entities | 80%+ |
| API | 70%+ |

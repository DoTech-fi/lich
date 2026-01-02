# Ports & Adapters

The pattern that keeps your domain independent from infrastructure.

## Ports (Interfaces)

Define WHAT your domain needs, not HOW.

```python
# internal/ports/order_repository.py
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Order]:
        pass
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        pass
```

## Adapters (Implementations)

Implement HOW to fulfill the interface.

```python
# internal/adapters/postgres_order_repository.py

class PostgresOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[Order]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
```

## Why This Pattern?

| Benefit | Description |
|---------|-------------|
| 🧪 **Testable** | Mock adapters for unit tests |
| 🔄 **Swappable** | Change DB without changing logic |
| 🧹 **Clean** | Domain doesn't know about SQL |

## Location

```
backend/internal/
├── ports/          # Interfaces
│   └── order_repository.py
└── adapters/       # Implementations
    └── postgres_order_repository.py
```

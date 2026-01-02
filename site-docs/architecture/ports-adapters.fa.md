# Ports و Adapters

الگویی که دامین شما را از زیرساخت مستقل نگه می‌دارد.

## Ports (اینترفیس‌ها)

تعریف می‌کنند دامین شما به **چه چیزی** نیاز دارد، نه **چگونه**.

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

## Adapters (پیاده‌سازی‌ها)

پیاده‌سازی می‌کنند **چگونه** اینترفیس را برآورده کنند.

```python
# internal/adapters/postgres_order_repository.py

class PostgresOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[Order]:
        result = await self.session.execute(...)
        return self._to_entity(model) if model else None
```

## چرا این الگو؟

| مزیت | توضیحات |
|---------|-------------|
| 🧪 **قابل تست** | Mock کردن adapters برای unit test |
| 🔄 **قابل تعویض** | تغییر DB بدون تغییر منطق |
| 🧹 **تمیز** | دامین چیزی از SQL نمی‌داند |

## مکان

```
backend/internal/
├── ports/          # اینترفیس‌ها
│   └── order_repository.py
└── adapters/       # پیاده‌سازی‌ها
    └── postgres_order_repository.py
```

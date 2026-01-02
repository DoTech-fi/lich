# Services

Services contain business logic and orchestrate use cases.

## Location

```
backend/internal/services/
├── user_service.py
├── order_service.py
└── notification_service.py
```

## Structure

```python
class OrderService:
    def __init__(self, order_repo, product_repo, payment_service):
        # Inject dependencies
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_service = payment_service
    
    async def place_order(self, user_id: UUID, items: list) -> Order:
        """
        Use case: Place an order.
        
        Orchestrates: validation, payment, persistence.
        """
        # 1. Validate items
        products = await self.product_repo.get_by_ids(...)
        
        # 2. Create order entity
        order = Order(user_id=user_id, items=items)
        order.calculate_total()
        
        # 3. Process payment
        await self.payment_service.charge(user_id, order.total)
        
        # 4. Save and return
        return await self.order_repo.save(order)
```

## Rules

1. **One service per domain** - `UserService`, `OrderService`
2. **Inject repositories** - Never create them inside
3. **Return domain objects** - Not database models

## Create with CLI

```bash
lich make service Order
```

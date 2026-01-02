# lich make service

Create a service - the business logic layer.

## What is a Service?

A **service** contains:

- **Use cases** - Business operations
- **Business rules** - Validation and logic
- **Coordination** - Orchestrates entities and adapters

Services are called by API controllers and call repositories.

## Usage

```bash
lich make service <Name>
```

## Example

```bash
$ lich make service Order

✅ Service OrderService created!

Files created:
  backend/internal/services/order_service.py
```

## Generated Code

```python
"""
Order service - business logic layer.
"""
from typing import List, Optional
from uuid import UUID

from internal.entities.order import Order


class OrderService:
    """
    Order service handling business logic.
    
    Inject repository dependencies in __init__.
    """
    
    def __init__(self, order_repository):
        """
        Initialize with repository dependency.
        
        Args:
            order_repository: OrderRepository implementation
        """
        self.order_repository = order_repository
    
    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """
        Get order by ID.
        
        Args:
            order_id: Order unique identifier
            
        Returns:
            Order if found, None otherwise
        """
        return await self.order_repository.get_by_id(order_id)
    
    async def list_orders(self) -> List[Order]:
        """
        Get all orders.
        
        Returns:
            List of all orders
        """
        return await self.order_repository.get_all()
    
    async def create_order(self, data: dict) -> Order:
        """
        Create a new order.
        
        Args:
            data: Order data dictionary
            
        Returns:
            Created order
        """
        order = Order(**data)
        return await self.order_repository.save(order)
    
    async def update_order(self, order_id: UUID, data: dict) -> Optional[Order]:
        """
        Update an existing order.
        
        Args:
            order_id: Order unique identifier
            data: Updated fields
            
        Returns:
            Updated order if found
        """
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            return None
        
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        
        return await self.order_repository.save(order)
    
    async def delete_order(self, order_id: UUID) -> bool:
        """
        Delete an order.
        
        Args:
            order_id: Order unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        return await self.order_repository.delete(order_id)
```

## Why Use Services?

| Benefit | Description |
|---------|-------------|
| 🎯 **Single Responsibility** | One service per domain |
| 🧪 **Testable** | Mock repository for testing |
| 🔄 **Reusable** | Call from API, CLI, jobs |
| 📦 **Decoupled** | No framework dependency |

## Real-World Example

### E-commerce Order Service

```python
class OrderService:
    def __init__(self, order_repo, product_repo, payment_service):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_service = payment_service
    
    async def place_order(self, user_id: UUID, items: list) -> Order:
        """Complete order workflow."""
        
        # 1. Validate products exist
        products = await self.product_repo.get_by_ids(
            [item['product_id'] for item in items]
        )
        
        # 2. Check inventory
        for item in items:
            product = next(p for p in products if p.id == item['product_id'])
            if product.stock < item['quantity']:
                raise ValueError(f"Insufficient stock for {product.name}")
        
        # 3. Calculate total
        total = sum(
            product.price * item['quantity']
            for product, item in zip(products, items)
        )
        
        # 4. Create order
        order = Order(
            user_id=user_id,
            items=items,
            total=total,
            status='pending'
        )
        
        # 5. Process payment
        payment = await self.payment_service.charge(user_id, total)
        order.payment_id = payment.id
        order.status = 'paid'
        
        # 6. Save and return
        return await self.order_repo.save(order)
```

## Best Use Cases

| Scenario | Service |
|----------|---------|
| User registration | `UserService.register()` |
| Order placement | `OrderService.place_order()` |
| Report generation | `ReportService.generate()` |
| Email sending | `NotificationService.send()` |

## Typical Workflow

```bash
# 1. Create entity first
lich make entity Order

# 2. Create service
lich make service Order

# 3. Create API to expose it
lich make api orders
```

## See Also

- [Services Architecture](../../architecture/services.md)
- [`make entity`](entity.md) - Create domain model first
- [`make api`](api.md) - Expose service via API

# lich make entity

Create a domain entity - the core of your business logic.

## What is an Entity?

An **entity** represents a business concept with:

- **Properties** - Data fields
- **Validation** - Rules for data
- **Behavior** - Domain logic methods

Entities are the **heart** of Clean Architecture.

## Usage

```bash
lich make entity <Name>
```

## Example

```bash
$ lich make entity Product

✅ Entity Product created!

Files created:
  backend/internal/entities/product.py
  backend/internal/entities/product_repository.py
```

## Generated Code

### Entity File (`product.py`)

```python
"""
Product entity - domain model.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Product:
    """Product domain entity."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    price: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    # Add domain methods here
    def apply_discount(self, percent: float) -> None:
        """Apply discount to price."""
        self.price = self.price * (1 - percent / 100)
```

### Repository Interface (`product_repository.py`)

```python
"""
Product repository port - interface for data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from internal.entities.product import Product


class ProductRepository(ABC):
    """Abstract repository for Product entity."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Product]:
        """Get product by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Product]:
        """Get all products."""
        pass
    
    @abstractmethod
    async def save(self, product: Product) -> Product:
        """Save product."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete product."""
        pass
```

## Why Use Entities?

| Benefit | Description |
|---------|-------------|
| 🏛️ **Domain Logic** | Keep business rules in entities |
| 🔒 **Validation** | Data is always valid |
| 🧪 **Testable** | Easy to unit test |
| 🔄 **Reusable** | Same entity across layers |

## Best Use Cases

### 1. User Management

```bash
lich make entity User
lich make entity Role
lich make entity Permission
```

### 2. E-commerce

```bash
lich make entity Product
lich make entity Order
lich make entity OrderItem
lich make entity Payment
```

### 3. Content Management

```bash
lich make entity Article
lich make entity Category
lich make entity Tag
lich make entity Comment
```

## Naming Conventions

| ✅ Good | ❌ Bad |
|---------|--------|
| `User` | `user` |
| `OrderItem` | `order_item` |
| `ProductCategory` | `productCategory` |

Always use **PascalCase** for entity names.

## Next Steps

After creating an entity:

```bash
# Create the service (business logic)
lich make service Product

# Create the API (endpoints)
lich make api products
```

## See Also

- [Entity Architecture](../../architecture/entities.md)
- [`make service`](service.md) - Business logic layer
- [`make factory`](factory.md) - Test data

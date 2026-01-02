---
description: Add a new domain entity following Lich Architecture
---

# Add Entity Workflow

## Before Starting

1. Read `.lich/rules/backend.md`
2. Understand the domain concept

## Entity Rules

- Pure Python dataclass
- NO external dependencies
- NO ORM types (SQLAlchemy, Pydantic)
- Domain logic inside entity
- Immutable where possible

## Steps

### 1. Create Entity
```python
# backend/internal/entities/product.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class ProductStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

@dataclass
class Product:
    id: str
    name: str
    price: float
    status: ProductStatus = ProductStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_active(self) -> bool:
        return self.status == ProductStatus.ACTIVE
    
    def activate(self) -> None:
        if self.price <= 0:
            raise ValueError("Cannot activate product without price")
        self.status = ProductStatus.ACTIVE
    
    def archive(self) -> None:
        self.status = ProductStatus.ARCHIVED
```

### 2. Export from __init__.py
```python
# backend/internal/entities/__init__.py

from .product import Product, ProductStatus
```

### 3. Create Port (Repository Interface)
```python
# backend/internal/ports/product_repository.py

from abc import ABC, abstractmethod
from typing import Optional, List
from internal.entities.product import Product

class ProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Product]:
        pass
    
    @abstractmethod
    async def list_active(self) -> List[Product]:
        pass
```

### 4. Write Entity Tests
```python
# backend/tests/test_product_entity.py

import pytest
from internal.entities.product import Product, ProductStatus

class TestProduct:
    def test_new_product_is_draft(self):
        product = Product(id="1", name="Test", price=10.0)
        assert product.status == ProductStatus.DRAFT
    
    def test_activate_product(self):
        product = Product(id="1", name="Test", price=10.0)
        product.activate()
        assert product.is_active
    
    def test_cannot_activate_zero_price(self):
        product = Product(id="1", name="Test", price=0)
        with pytest.raises(ValueError):
            product.activate()
```

## Checklist

```
[ ] Entity as dataclass
[ ] No external dependencies
[ ] Domain logic as methods
[ ] Properties for computed values
[ ] Repository port defined
[ ] Unit tests for entity
[ ] Exported from __init__.py
[ ] agentlog.md updated
```

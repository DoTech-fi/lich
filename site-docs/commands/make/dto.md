# lich make dto

Create Data Transfer Objects for API requests and responses.

## What is a DTO?

A **DTO (Data Transfer Object)** defines:

- **Request shapes** - What data the API accepts
- **Response shapes** - What data the API returns
- **Validation** - Automatic input validation

## Usage

```bash
lich make dto <Name>
```

## Example

```bash
$ lich make dto Product

✅ DTO Product created!

Files created:
  backend/internal/dto/product_dto.py
```

## Generated Code

```python
"""
Product DTOs - request/response schemas.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    """Request to create a product."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Widget Pro",
                "description": "A premium widget",
                "price": 29.99
            }
        }


class UpdateProductRequest(BaseModel):
    """Request to update a product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)


class ProductResponse(BaseModel):
    """Product response."""
    
    id: UUID
    name: str
    description: Optional[str]
    price: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

## Why Use DTOs?

| Benefit | Description |
|---------|-------------|
| ✅ **Validation** | Pydantic validates automatically |
| 📖 **Documentation** | Auto-generates OpenAPI docs |
| 🔒 **Security** | Control what data is exposed |
| 🧪 **Testing** | Clear contracts for tests |

## Use in API Router

```python
from internal.dto.product_dto import (
    CreateProductRequest,
    UpdateProductRequest,
    ProductResponse
)

@router.post("/", response_model=ProductResponse)
async def create_product(request: CreateProductRequest):
    product = await service.create(request.model_dump())
    return ProductResponse.model_validate(product)
```

## Validation Examples

```python
class CreateUserRequest(BaseModel):
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=18, le=120)
```

## See Also

- [`make api`](api.md) - Use DTOs in routers
- [`make entity`](entity.md) - Domain model

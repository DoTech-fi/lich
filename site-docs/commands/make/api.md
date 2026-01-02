# lich make api

Create an API router - HTTP endpoints for your service.

## What is an API Router?

An **API router** provides:

- **HTTP endpoints** - GET, POST, PUT, DELETE
- **Request handling** - Receive and validate input
- **Response formatting** - Return JSON data

## Usage

```bash
lich make api <name>
```

Use **lowercase plural** naming: `products`, `orders`, `users`.

## Example

```bash
$ lich make api products

✅ API products created!

Files created:
  backend/api/http/products.py
```

## Generated Code

```python
"""
Products API router.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[dict])
async def list_products():
    """Get all products."""
    # TODO: Inject ProductService
    return []


@router.get("/{id}", response_model=dict)
async def get_product(id: UUID):
    """Get product by ID."""
    # TODO: Inject ProductService
    # product = await service.get_product(id)
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")
    # return product
    raise HTTPException(status_code=404, detail="Not implemented")


@router.post("/", response_model=dict, status_code=201)
async def create_product(data: dict):
    """Create a new product."""
    # TODO: Replace dict with CreateProductRequest DTO
    # return await service.create_product(data)
    return {"message": "Created"}


@router.put("/{id}", response_model=dict)
async def update_product(id: UUID, data: dict):
    """Update a product."""
    # TODO: Replace dict with UpdateProductRequest DTO
    return {"message": "Updated"}


@router.delete("/{id}", status_code=204)
async def delete_product(id: UUID):
    """Delete a product."""
    # TODO: Inject ProductService
    return None
```

## Register the Router

After creating, register in `backend/main.py`:

```python
from api.http.products import router as products_router

app.include_router(products_router, prefix="/api/v1")
```

## Best Practices

### 1. Create DTOs for Requests

```bash
lich make dto Product
```

Then use in router:

```python
from internal.dto.product_dto import CreateProductRequest

@router.post("/")
async def create_product(request: CreateProductRequest):
    return await service.create(request)
```

### 2. Inject Service Dependencies

```python
from internal.services.product_service import ProductService

def get_product_service():
    # Get from DI container
    return ProductService(repository)

@router.get("/")
async def list_products(
    service: ProductService = Depends(get_product_service)
):
    return await service.list_all()
```

## Use Cases

| Endpoint Pattern | Use Case |
|-----------------|----------|
| `GET /products` | List all |
| `GET /products/{id}` | Get one |
| `POST /products` | Create |
| `PUT /products/{id}` | Update |
| `DELETE /products/{id}` | Delete |
| `POST /products/{id}/archive` | Custom action |

## See Also

- [`make dto`](dto.md) - Request/Response types
- [`make service`](service.md) - Business logic
- [API Architecture](../../architecture/api.md)

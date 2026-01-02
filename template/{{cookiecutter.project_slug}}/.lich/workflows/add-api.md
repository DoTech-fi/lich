---
description: Add a new API endpoint to the backend
---

# Add API Endpoint Workflow

## Before Starting

1. Read `.lich/rules/backend.md`
2. Check if entity/service exists

## Steps

### 1. Define Request DTO
```python
# backend/internal/dto/requests.py

class MyRequest(BaseModel):
    field: str
    
    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        # validation
        return v
```

### 2. Define Response DTO
```python
# backend/internal/dto/responses.py

class MyResponse(BaseModel):
    id: str
    data: str
    created_at: datetime
```

### 3. Add Service Method
```python
# backend/internal/services/my_service.py

async def my_action(self, request: MyRequest) -> Entity:
    # business logic
    return entity
```

### 4. Create/Update Router
```python
# backend/api/http/my_router.py

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/myroute", tags=["MyRoute"])

@router.post("/", response_model=MyResponse)
async def create_item(
    request: MyRequest,
    service: MyService = Depends(get_service),
):
    result = await service.my_action(request)
    return MyResponse.from_entity(result)
```

### 5. Register Router
```python
# backend/main.py

from api.http.my_router import router as my_router
app.include_router(my_router)
```

### 6. Add Tests
```python
# backend/tests/test_my_api.py

@pytest.mark.asyncio
async def test_create_item_success():
    async with AsyncClient(...) as client:
        response = await client.post("/api/v1/myroute/", json={...})
        assert response.status_code == 201
```

## API Conventions

- REST verbs: GET, POST, PUT, PATCH, DELETE
- Path: `/api/v1/<resource>/`
- List: GET `/api/v1/<resource>/`
- Create: POST `/api/v1/<resource>/`
- Get one: GET `/api/v1/<resource>/{id}`
- Update: PATCH `/api/v1/<resource>/{id}`
- Delete: DELETE `/api/v1/<resource>/{id}`

## Checklist

```
[ ] Request DTO with validation
[ ] Response DTO
[ ] Service method
[ ] Router endpoint
[ ] Router registered in main.py
[ ] Tests written
[ ] OpenAPI documented
[ ] agentlog.md updated
```

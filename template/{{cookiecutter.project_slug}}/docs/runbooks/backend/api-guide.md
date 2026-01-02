# API Guide

> راهنمای استفاده از API {{ cookiecutter.project_name }}

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}

### JWT Authentication

1. **Register** a new user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Password123"}'
```

2. **Login** to get tokens:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Password123"}'
```

3. **Use access token** for authenticated requests:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

4. **Refresh token** when expired:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

{%- elif cookiecutter.auth_strategy == 'keycloak' %}

### Keycloak Authentication

1. Get Keycloak config:
```bash
curl http://localhost:8000/api/v1/auth/config
```

2. Redirect user to Keycloak login page
3. Exchange authorization code for tokens
4. Use access token for API requests

{%- endif %}

## Endpoints

### Health Check

```bash
GET /health
GET /api/health
```

### Users

```bash
GET    /api/v1/users/me          # Get current user
PATCH  /api/v1/users/me          # Update current user
GET    /api/v1/users             # List users (admin)
GET    /api/v1/users/{id}        # Get user by ID (admin)
POST   /api/v1/users/{id}/activate   # Activate user (admin)
POST   /api/v1/users/{id}/suspend    # Suspend user (admin)
DELETE /api/v1/users/{id}        # Delete user (admin)
```

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found",
    "details": {}
  }
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per minute for authenticated users

## Interactive Docs

Swagger UI: http://localhost:8000/api/docs
ReDoc: http://localhost:8000/api/redoc

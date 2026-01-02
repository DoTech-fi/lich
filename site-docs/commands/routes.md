# lich routes

List all registered API routes.

## Usage

```bash
lich routes
```

## Example

```bash
$ lich routes

📍 Registered Routes:

┌─────────┬────────────────────────┬──────────────────┐
│ Method  │ Path                   │ Tags             │
├─────────┼────────────────────────┼──────────────────┤
│ GET     │ /api/v1/users          │ Users            │
│ POST    │ /api/v1/users          │ Users            │
│ GET     │ /api/v1/users/{id}     │ Users            │
│ PUT     │ /api/v1/users/{id}     │ Users            │
│ DELETE  │ /api/v1/users/{id}     │ Users            │
│ GET     │ /api/v1/products       │ Products         │
│ POST    │ /api/v1/products       │ Products         │
│ GET     │ /health                │ Health           │
└─────────┴────────────────────────┴──────────────────┘

Total: 8 routes
```

## Why Use This?

- Quick overview of all endpoints
- Check if new routes are registered
- Debug routing issues

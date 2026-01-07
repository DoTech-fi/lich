# Configuration

Every Lich project has a `.lich/` folder containing configuration and AI rules.

## Project Configuration

```
your-project/
├── .lich/
│   ├── config.yml        # Project settings
│   └── rules/            # AI rules
├── .env                  # Environment variables
└── docker-compose.yml    # Docker services
```

## Environment Variables

Create a `.env` file in your project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=app_user
DB_PASSWORD=your_password
DB_NAME=app_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT (if using jwt_builtin)
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
  
# Google OAuth (if using jwt_builtin)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Keycloak (if using keycloak)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=your-client
```

!!! warning "Production"
    Never commit `.env` files. Use a secret manager in production.

## Docker Compose Configuration

The generated `docker-compose.yml` includes:

```yaml
services:
  db:
    image: postgres:15
    # ...
    
  redis:
    image: redis:7-alpine
    # ...
    
  backend:
    build: ./backend
    # ...
```

### Custom Docker Settings

Edit `docker-compose.yml` to:

- Change port mappings
- Add environment variables
- Mount additional volumes
- Add new services

## AI Rules Configuration

The `.lich/rules/` folder contains markdown files that guide AI assistants:

```
.lich/rules/
├── backend.md      # Backend architecture rules
├── frontend.md     # Frontend patterns
├── lich-cli.md     # CLI command reference
└── master-prompt.md  # Combined rules
```

### Customizing AI Rules

Edit these files to add project-specific patterns:

```markdown
# Custom Rules

## Naming Conventions
- All services must end with "Service"
- All repositories must end with "Repository"

## Patterns to Follow
- Always use async/await
- Always validate input with Pydantic
```

## Next Steps

[:octicons-arrow-right-24: Learn CLI Commands](../commands/overview.md)

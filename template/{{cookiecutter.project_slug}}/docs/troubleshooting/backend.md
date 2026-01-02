# Backend Troubleshooting

> راهنمای رفع مشکلات Backend

## Database Connection Issues

### Problem: Cannot connect to PostgreSQL
{%- if cookiecutter.database == 'postgresql' %}

**Symptoms:**
- `Connection refused`
- `could not connect to server`

**Solutions:**

1. Check if Docker is running:
```bash
docker ps | grep postgres
```

2. Check if port is available:
```bash
lsof -i :5432
```

3. Check database logs:
```bash
docker-compose logs postgres
```

4. Verify credentials in `.env`:
```bash
cat .env | grep DB_
```
{%- endif %}

---

## Authentication Issues

### Problem: JWT Token Invalid
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}

**Symptoms:**
- `401 Unauthorized`
- `Invalid token`

**Solutions:**

1. Check if token is expired:
```bash
# Decode JWT (without verification)
echo "TOKEN" | cut -d. -f2 | base64 -d
```

2. Verify `JWT_SECRET_KEY` is set correctly

3. Check token format:
```bash
curl -v -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/auth/me
```
{%- endif %}

{%- if cookiecutter.auth_strategy == 'keycloak' %}
### Problem: Keycloak Connection Failed

**Symptoms:**
- `Connection to Keycloak failed`
- `Invalid realm`

**Solutions:**

1. Check if Keycloak is running:
```bash
docker ps | grep keycloak
curl http://localhost:8080/health/ready
```

2. Verify realm exists:
```bash
./scripts/setup-keycloak.sh
```

3. Check Keycloak logs:
```bash
docker-compose logs keycloak
```
{%- endif %}

---

## API Issues

### Problem: CORS Error

**Symptoms:**
- `Access-Control-Allow-Origin` error in browser

**Solutions:**

1. Check `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

2. Verify frontend URL matches allowed origins

---

## Cache Issues
{%- if cookiecutter.use_redis == 'yes' %}

### Problem: Redis Connection Failed

**Symptoms:**
- `Connection refused`
- `REDIS_URL is invalid`

**Solutions:**

1. Check if Redis is running:
```bash
docker ps | grep redis
redis-cli ping
```

2. Check Redis logs:
```bash
docker-compose logs redis
```
{%- endif %}

---

## Common Errors

### ImportError / ModuleNotFoundError

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

**Solution:**
```bash
lsof -ti :8000 | xargs kill -9
```

---

## Getting Help

1. Check logs: `.logs/backend.log`
2. Run with debug: `DEBUG=true python main.py`
3. Open issue on GitHub

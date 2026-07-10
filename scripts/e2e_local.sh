#!/usr/bin/env bash
# Golden-path e2e: generate a project with the local template, boot infra,
# build+run the backend image, run its tests, hit health/auth endpoints.
# Usage: scripts/e2e_local.sh <postgresql|mongodb> <jwt_builtin|none>
set -euo pipefail

DATABASE="${1:-postgresql}"
AUTH="${2:-jwt_builtin}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKDIR="$(mktemp -d)"
SLUG="e2e_app"
BACKEND_CONTAINER="e2e_backend"

cleanup() {
  echo "--- cleanup ---"
  docker rm -f "$BACKEND_CONTAINER" >/dev/null 2>&1 || true
  if [ -d "$WORKDIR/$SLUG" ]; then
    (cd "$WORKDIR/$SLUG" && docker compose down -v --remove-orphans >/dev/null 2>&1) || true
  fi
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

echo "=== 1. Generate project (database=$DATABASE auth=$AUTH) ==="
python -m cookiecutter "$REPO_ROOT/template" --no-input -o "$WORKDIR" \
  project_name="E2E App" \
  project_slug="$SLUG" \
  database="$DATABASE" \
  auth_strategy="$AUTH" \
  use_redis="yes"
cd "$WORKDIR/$SLUG"

echo "=== 2. Boot infra (db + redis only; skip traefik/adminer) ==="
if [ "$DATABASE" = "postgresql" ]; then
  DB_SERVICE="postgres"
else
  DB_SERVICE="mongodb"
fi
docker compose up -d "$DB_SERVICE" redis

echo "=== 3. Wait for DB healthcheck (timeout 120s) ==="
DB_CONTAINER="${SLUG}_${DB_SERVICE}"
for i in $(seq 1 60); do
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$DB_CONTAINER" 2>/dev/null || echo starting)"
  [ "$STATUS" = "healthy" ] && break
  [ "$i" = "60" ] && { echo "DB never became healthy"; docker compose logs "$DB_SERVICE"; exit 1; }
  sleep 2
done
echo "DB healthy."

echo "=== 4. Build backend image ==="
docker build -t e2e-backend ./backend

# Compose project name defaults to directory name (SLUG), so networks are ${SLUG}_internal_net
COMPOSE_NETWORK="${SLUG}_internal_net"

BACKEND_ENV=(-e ENVIRONMENT=development -e JWT_SECRET_KEY=e2e-test-secret -e SECRET_KEY=e2e-test-secret -e REDIS_HOST=redis)
if [ "$DATABASE" = "postgresql" ]; then
  BACKEND_ENV+=(-e DB_HOST=postgres -e DB_USER=app -e DB_PASSWORD=app_secret -e DB_NAME="$SLUG")
else
  BACKEND_ENV+=(-e MONGODB_HOST=mongodb -e MONGODB_USER=app -e MONGODB_PASSWORD=app_secret -e MONGODB_DB="$SLUG")
fi

echo "=== 5. Run generated backend tests inside the image ==="
docker run --rm --network "$COMPOSE_NETWORK" "${BACKEND_ENV[@]}" \
  e2e-backend python -m pytest -v --tb=short

echo "=== 6. Start backend container ==="
docker run -d --name "$BACKEND_CONTAINER" --network "$COMPOSE_NETWORK" \
  -p 8000:8000 "${BACKEND_ENV[@]}" e2e-backend

echo "=== 7. Wait for /api/health (timeout 60s) ==="
for i in $(seq 1 30); do
  if curl -fsS http://localhost:8000/api/health >/dev/null 2>&1; then break; fi
  [ "$i" = "30" ] && { echo "backend never became healthy"; docker logs "$BACKEND_CONTAINER"; exit 1; }
  sleep 2
done
curl -fsS http://localhost:8000/api/health
echo

if [ "$AUTH" = "jwt_builtin" ]; then
  echo "=== 8. Register + login ==="
  REGISTER_CODE="$(curl -s -o /tmp/e2e_register.json -w '%{http_code}' \
    -X POST http://localhost:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email":"e2e@test.com","username":"e2euser","password":"Passw0rdX"}')"
  [ "$REGISTER_CODE" = "201" ] || { echo "register failed ($REGISTER_CODE):"; cat /tmp/e2e_register.json; exit 1; }

  LOGIN_CODE="$(curl -s -o /tmp/e2e_login.json -w '%{http_code}' \
    -X POST http://localhost:8000/api/v1/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"e2e@test.com","password":"Passw0rdX"}')"
  [ "$LOGIN_CODE" = "200" ] || { echo "login failed ($LOGIN_CODE):"; cat /tmp/e2e_login.json; exit 1; }
  grep -q "access_token" /tmp/e2e_login.json || { echo "no access_token in login response"; exit 1; }
  echo "register+login OK"
fi

echo "=== E2E PASSED (database=$DATABASE auth=$AUTH) ==="

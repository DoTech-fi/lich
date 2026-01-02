#!/bin/bash
# {{ cookiecutter.project_name }} - Environment Validation Script
# Validates that all required environment variables are set

echo "🔍 Validating environment configuration..."
echo "============================================"

ERRORS=0

check_var() {
    if [ -z "${!1}" ]; then
        echo "❌ $1 is not set"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ $1 is set"
    fi
}

check_var_optional() {
    if [ -z "${!1}" ]; then
        echo "⚠️  $1 is not set (optional)"
    else
        echo "✅ $1 is set"
    fi
}

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "📄 Loaded .env file"
else
    echo "⚠️  No .env file found, checking environment variables only"
fi

echo ""
echo "🔧 Required Variables:"
echo "----------------------"

# Database
{%- if cookiecutter.database == 'postgresql' %}
check_var "DB_HOST"
check_var "DB_PORT"
check_var "DB_USER"
check_var "DB_PASSWORD"
check_var "DB_NAME"
{%- else %}
check_var "MONGODB_HOST"
check_var "MONGODB_PORT"
check_var "MONGODB_USER"
check_var "MONGODB_PASSWORD"
check_var "MONGODB_DB"
{%- endif %}

{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
# JWT
check_var "JWT_SECRET_KEY"
{%- elif cookiecutter.auth_strategy == 'keycloak' %}
# Keycloak
check_var "KEYCLOAK_URL"
check_var "KEYCLOAK_REALM"
check_var "KEYCLOAK_CLIENT_ID"
{%- endif %}

# Security
check_var "SECRET_KEY"

echo ""
echo "📌 Optional Variables:"
echo "----------------------"

{%- if cookiecutter.use_redis == 'yes' %}
check_var_optional "REDIS_HOST"
check_var_optional "REDIS_PORT"
{%- endif %}

check_var_optional "LOG_LEVEL"
check_var_optional "CORS_ORIGINS"

echo ""
echo "============================================"

if [ $ERRORS -gt 0 ]; then
    echo "❌ Validation failed with $ERRORS error(s)"
    echo ""
    echo "💡 Copy .env.example to .env and fill in the values:"
    echo "   cp .env.example .env"
    exit 1
else
    echo "✅ All required environment variables are set!"
fi

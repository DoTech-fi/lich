{%- if cookiecutter.auth_strategy == 'keycloak' %}
#!/bin/bash
set -e

# {{ cookiecutter.project_name }} - Keycloak Setup Script
# Sets up initial realm, clients, and configuration

echo "🔐 Setting up Keycloak for {{ cookiecutter.project_name }}..."

KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8080}"
ADMIN_USER="${KEYCLOAK_ADMIN:-admin}"
ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
REALM="{{ cookiecutter.project_slug }}"

# Wait for Keycloak to be ready
echo "⏳ Waiting for Keycloak..."
until curl -s "$KEYCLOAK_URL/health/ready" > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Keycloak is ready"

# Get admin token
echo "🔑 Getting admin token..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -d "client_id=admin-cli" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Failed to get admin token"
    exit 1
fi

# Check if realm exists
REALM_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$KEYCLOAK_URL/admin/realms/$REALM")

if [ "$REALM_EXISTS" == "200" ]; then
    echo "ℹ️  Realm '$REALM' already exists, skipping creation"
else
    # Create realm
    echo "📦 Creating realm '$REALM'..."
    curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"realm\": \"$REALM\",
            \"enabled\": true,
            \"registrationAllowed\": true,
            \"resetPasswordAllowed\": true,
            \"rememberMe\": true,
            \"loginWithEmailAllowed\": true,
            \"duplicateEmailsAllowed\": false
        }"
    echo "✅ Realm created"
fi

# Create web client
echo "🌐 Creating web client..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "{{ cookiecutter.project_slug }}-web",
        "name": "{{ cookiecutter.project_name }} Web App",
        "publicClient": true,
        "directAccessGrantsEnabled": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "redirectUris": [
            "http://localhost:3000/*",
            "http://localhost:3002/*"
        ],
        "webOrigins": [
            "http://localhost:3000",
            "http://localhost:3002"
        ]
    }' || echo "  (client may already exist)"

# Create API client
echo "🔌 Creating API client..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "{{ cookiecutter.project_slug }}-api",
        "name": "{{ cookiecutter.project_name }} API",
        "publicClient": false,
        "bearerOnly": true,
        "serviceAccountsEnabled": true
    }' || echo "  (client may already exist)"

# Create admin role
echo "👤 Creating admin role..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/roles" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "admin",
        "description": "Administrator role"
    }' || echo "  (role may already exist)"

echo ""
echo "🎉 Keycloak setup complete!"
echo ""
echo "📍 Keycloak Admin Console: $KEYCLOAK_URL"
echo "   Username: $ADMIN_USER"
echo "   Password: $ADMIN_PASS"
echo ""
echo "🔗 Realm: $REALM"
echo "   Web Client: {{ cookiecutter.project_slug }}-web"
echo "   API Client: {{ cookiecutter.project_slug }}-api"
{%- else %}
#!/bin/bash
echo "Keycloak is not enabled for this project."
echo "Auth strategy: {{ cookiecutter.auth_strategy }}"
{%- endif %}

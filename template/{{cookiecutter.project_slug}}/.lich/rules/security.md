# Security Architecture Rules

> As a Super Security Architect, follow these rules to ensure the system is **secure by default**.

## Core Principles

```
🔒 SECURE BY DEFAULT
🔍 DEFENSE IN DEPTH  
🚫 LEAST PRIVILEGE
📝 AUDIT EVERYTHING
```

---

## 1. Authentication

### DO ✅
- Use secure session storage (sessionStorage, NOT localStorage)
- Implement token refresh mechanism
- Use HttpOnly + Secure + SameSite cookies
- Hash passwords with bcrypt (cost ≥ 12)
- Implement rate limiting on auth endpoints

### DON'T ❌
- Never store tokens in localStorage
- Never log passwords or tokens
- Never send credentials in URL params

---

## 2. Input Validation

### DO ✅
- Validate ALL input on backend (Pydantic)
- Validate on frontend too (defense in depth)
- Use parameterized queries (never raw SQL)
- Sanitize HTML output

### DON'T ❌
- Never trust client input
- Never use eval() on user data
- Never concatenate SQL strings

---

## 3. API Security

### DO ✅
- Use HTTPS everywhere
- Implement CORS properly (explicit origins)
- Add rate limiting
- Return generic error messages to clients

### DON'T ❌
- Never expose stack traces
- Never allow * CORS in production

---

## 4. Docker Security

### DO ✅
- Run as non-root user
- Use minimal base images (alpine)
- No hardcoded secrets

### DON'T ❌
- Never run as root
- Never commit .env files

---

## 5. Secrets Management

### DO ✅
- Use environment variables
- Rotate secrets regularly
- Different secrets per environment

### DON'T ❌
- Never commit secrets to git
- Never hardcode secrets

---

> **Mantra**: Simple → Reliable → Secure

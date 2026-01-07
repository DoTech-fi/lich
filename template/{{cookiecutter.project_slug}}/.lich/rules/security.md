# Security Rules

> **Security-First Development - OWASP Aligned**

---

## ⚠️ GLOBAL SECURITY RULES (ALWAYS APPLY)

These rules apply in ALL modes (backend, frontend, infra):

---

## 🔒 Secrets & Credentials

**NEVER:**
- ❌ Hardcode secrets in code
- ❌ Commit secrets to git
- ❌ Log passwords, tokens, or PII
- ❌ Store tokens in localStorage
- ❌ Put secrets in frontend code

**ALWAYS:**
- ✅ Use `.env` files (gitignored)
- ✅ Use secret managers in production
- ✅ Rotate secrets regularly
- ✅ Use `lich secret` commands

```bash
lich secret generate      # Generate strong secret
lich secret rotate        # Rotate in .env
lich secret check         # Verify strength
```

---

## 🛡️ Input Validation

**ALWAYS:**
- ✅ Validate ALL user input
- ✅ Sanitize before processing
- ✅ Validate on client AND server
- ✅ Use Pydantic (backend) / Zod (frontend)
- ✅ Whitelist allowed values

**NEVER:**
- ❌ Trust any external input
- ❌ Use raw SQL queries
- ❌ Interpolate user input into queries

---

## 🍪 Authentication & Sessions

**DO:**
- ✅ HttpOnly cookies for tokens
- ✅ Secure flag (HTTPS only)
- ✅ SameSite=Strict or Lax
- ✅ Short token expiration
- ✅ Refresh token rotation

**DON'T:**
- ❌ localStorage for auth tokens
- ❌ sessionStorage for secrets
- ❌ Long-lived tokens
- ❌ Credentials in URL

---

## 🚫 XSS Prevention

**NEVER:**
- ❌ Use `dangerouslySetInnerHTML` without sanitization
- ❌ Render user HTML directly
- ❌ Eval user input

**ALWAYS:**
- ✅ Sanitize with DOMPurify if needed
- ✅ Escape output by default
- ✅ Use React's built-in escaping

---

## 🌐 CORS & Headers

**DO:**
- ✅ Specific allowed origins (no `*`)
- ✅ Security headers (CSP, X-Frame-Options)
- ✅ HSTS in production

**DON'T:**
- ❌ `Access-Control-Allow-Origin: *`
- ❌ Expose internal headers

---

## 🚦 Rate Limiting

**ALWAYS:**
- ✅ Rate limit login endpoints
- ✅ Rate limit API endpoints
- ✅ Implement backoff for failures

---

## 🔍 Error Handling

**DO:**
- ✅ Generic errors to users
- ✅ Detailed logs (internal only)
- ✅ Never leak stack traces

**DON'T:**
- ❌ Expose internal paths/versions
- ❌ Return SQL errors to users
- ❌ Leak sensitive data in errors

---

## 🐳 Container Security

**ALWAYS:**
- ✅ Non-root user in containers
- ✅ Read-only filesystem
- ✅ No new privileges
- ✅ Minimal base images
- ✅ Scan with `lich security`

```yaml
user: "1000:1000"
read_only: true
security_opt:
  - no-new-privileges:true
```

---

## ✅ Security Checklist

Before deployment:

```bash
lich security            # Run all scans
lich production-ready    # Check readiness
```

- [ ] No secrets in code
- [ ] All inputs validated
- [ ] Auth tokens in HttpOnly cookies
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Non-root containers
- [ ] Dependencies scanned

---

**Mantra: Security is NOT optional. It's default.**

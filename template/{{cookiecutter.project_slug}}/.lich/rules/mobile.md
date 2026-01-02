# Mobile Development Rules (NEW in v1.0.1)

> Rules for React Native / Flutter mobile development.

## Core Principles

```
📱 MOBILE-FIRST
⚡ PERFORMANCE CRITICAL
🔒 SECURE STORAGE
📶 OFFLINE-CAPABLE
```

---

## 1. Architecture

### DO ✅
- Single source of truth for state
- Offline-first data sync
- Optimistic UI updates
- Secure keychain for tokens

### DON'T ❌
- No sensitive data in AsyncStorage
- No blocking UI operations

---

## 2. Performance

### DO ✅
- Lazy load screens
- Optimize list rendering
- Cache images
- Minimize re-renders

---

## 3. Security

### DO ✅
- Use Keychain/Keystore for tokens
- Certificate pinning for API
- Biometric authentication
- Secure data at rest

---

> **Mantra**: Simple → Fast → Secure

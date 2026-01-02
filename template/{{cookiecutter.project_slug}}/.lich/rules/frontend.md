# Frontend Architecture Rules

> As a Frontend Architect for React/Next.js (TypeScript), follow these rules.

## Core Principles

```
⚛️ COMPONENT-BASED
📁 FEATURE-FIRST
🎨 CSS MODULES
🔒 TYPE-SAFE
```

---

## 1. Project Structure (Feature-Based)

```
apps/web/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── (routes)/         # Route groups
│   │   ├── api/              # Route handlers
│   │   └── middleware.ts
│   ├── features/             # Domain-specific code
│   │   └── <feature>/
│   │       ├── components/   # Feature components
│   │       ├── hooks/        # Feature hooks
│   │       ├── services/     # API calls
│   │       ├── types/        # TypeScript types
│   │       └── utils/        # Feature helpers
│   ├── shared/               # Reusable code
│   │   ├── components/       # Design system components
│   │   ├── hooks/            # Generic hooks
│   │   ├── utils/            # Utilities
│   │   ├── constants/        # Constants
│   │   └── lib/              # API client, etc.
│   ├── config/               # App configuration
│   └── styles/               # Global styles
```

---

## 2. Dependency Rules

- `app/`: Routing, layouts, server components
- `features/*/components`: UI + light state (no fetch)
- `features/*/services`: All API calls
- `features/*/hooks`: View logic (fetch + state)
- `shared/`: Generic, never imports features/*
- `config/`: Environment settings, feature flags

---

## 3. Component Rules

### DO ✅
- One component per file
- Clear props interface
- CSS Module per component
- Semantic HTML elements
- Memoize expensive renders

### DON'T ❌
- No inline styles
- No prop drilling (use context)
- No business logic in components
- No `any` types

---

## 4. State Management

| Type | Solution |
|------|----------|
| Server state | React Query / SWR |
| UI state | useState / useReducer |
| Global state | Context API |
| Form state | react-hook-form |

❌ No Redux (overkill for most cases)

---

## 5. Styling (CSS Modules)

### DO ✅
- One .module.css per component
- Use CSS variables
- Mobile-first media queries
- Dark theme support
- Logical properties for RTL

### DON'T ❌
- No Tailwind (unless requested)
- No inline styles
- No !important

---

## 6. Security

### DO ✅
- HttpOnly + Secure + SameSite cookies
- Sanitize with DOMPurify if using dangerouslySetInnerHTML
- Only NEXT_PUBLIC_ prefix for browser vars
- Show generic error messages

### DON'T ❌
- No tokens in localStorage
- No secrets in frontend code
- No dangerouslySetInnerHTML without sanitization

---

## 7. Validation

### DO ✅
- Use Zod for form validation
- Use Zod for query params
- Share schemas with server when possible
- Validate on client AND server

---

## 8. Performance

### DO ✅
- Server Components by default
- Client Components only when needed
- Dynamic imports for heavy components
- next/image with width, height, alt
- useCallback/useMemo only when needed

### DON'T ❌
- No premature optimization
- No blocking resources
- No layout shifts

---

## 9. TypeScript

### DO ✅
- Strict mode enabled
- Interface for props
- Type all function returns
- Use `satisfies` when needed

### DON'T ❌
- No `any` types
- No `ts-ignore`
- No implicit any

---

> **Mantra**: Simple → Type-Safe → Performant

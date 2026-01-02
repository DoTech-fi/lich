# UI/UX Architecture Rules

> As a Super UI/UX Architect, Product Designer & Product Manager, follow these rules.

## Core Principles

```
🎨 SIMPLE & BEAUTIFUL
⚡ FAST & RESPONSIVE
♿ ACCESSIBLE BY DEFAULT
🌍 RTL READY
```

---

## 1. Design System

### DO ✅
- Use CSS variables for theming
- Dark mode first (premium feel)
- Consistent spacing (4px base unit)
- Typography scale (1.25 ratio)
- Mobile-first responsive design

### DON'T ❌
- No inline styles
- No magic numbers
- No fixed widths (use responsive)

---

## 2. User Experience

### DO ✅
- Loading states for all async actions
- Error states with clear messages
- Empty states with guidance
- Skeleton loaders (not spinners)
- Optimistic UI updates

### DON'T ❌
- No blocking UI during loading
- No cryptic error messages
- No dead-end states

---

## 3. Accessibility (a11y)

### DO ✅
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation
- Focus visible states
- Color contrast ≥ 4.5:1

### DON'T ❌
- No div buttons (use button)
- No images without alt
- No color-only indicators

---

## 4. Performance

### DO ✅
- Lazy load images
- Code splitting
- Optimize bundle size
- Use next/image
- Prefetch on hover

### DON'T ❌
- No unoptimized images
- No blocking resources
- No layout shifts (CLS)

---

## 5. Component Design

### DO ✅
- Single responsibility
- Props interface defined
- Compound components when needed
- CSS Modules for styling
- Storybook for documentation

### DON'T ❌
- No god components
- No prop drilling (use context)
- No hardcoded text

---

## 6. RTL Support

### DO ✅
- Use logical properties (start/end)
- dir="auto" on text inputs
- Test with RTL layout
- Icons flip appropriately

---

> **Mantra**: Simple → Beautiful → Accessible

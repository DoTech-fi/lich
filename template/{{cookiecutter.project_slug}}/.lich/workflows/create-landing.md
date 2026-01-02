---
description: Create or customize the landing page based on project type
---

# Create Landing Page Workflow

## Before Starting

1. Read `.lich/AI_CONTEXT.md` to get project type
2. Read `.lich/rules/ui-ux.md` for design rules
3. Check project type: {{ cookiecutter.project_type }}

## Landing Structure

```
apps/landing/src/
├── pages/
│   └── index.astro        # Main landing page
├── components/
│   ├── Hero.astro         # Hero section
│   ├── Features.astro     # Features grid
│   ├── Stats.astro        # Statistics
│   ├── CTA.astro          # Call to action
│   └── Footer.astro       # Footer
└── styles/
    └── global.css         # Global styles
```

## Sections by Project Type

### trading_platform
1. **Hero**: "Trade Smarter" + Live chart preview
2. **Stats**: Users, Trades, Volume
3. **Features**: Real-time data, Portfolio, Alerts
4. **CTA**: Start trading button

### saas_platform
1. **Hero**: Product tagline + Demo
2. **Features**: Key features grid
3. **Pricing**: Pricing tiers
4. **Testimonials**: Customer quotes
5. **CTA**: Sign up / Free trial

### ecommerce
1. **Hero**: Featured products
2. **Categories**: Product categories
3. **Bestsellers**: Top products
4. **CTA**: Shop now

### content_platform
1. **Hero**: Content showcase
2. **Featured**: Top content
3. **Categories**: Content types
4. **CTA**: Join now

## Design Rules

- Dark theme (premium feel)
- Gradient accents
- Smooth animations
- Mobile-first responsive
- RTL support if default_language is 'fa'

## Steps

### 1. Update Hero Section
Edit `apps/landing/src/components/Hero.astro`:
- Project name: {{ cookiecutter.project_name }}
- Tagline based on project_type
- CTA button to /login or /register

### 2. Add Statistics
Edit/Create `Stats.astro`:
- Relevant metrics for project type
- Animated counters

### 3. Add Features Grid
Edit `Features.astro`:
- 3-6 key features
- Icons + descriptions

### 4. Final CTA
Edit `CTA.astro`:
- Strong call to action
- Link to signup/demo

### 5. Update Styling
Ensure dark theme with:
- Background: var(--bg-primary)
- Accent: var(--primary)
- Text: var(--text-primary)

## Checklist

```
[ ] Hero section updated
[ ] Stats relevant to project type
[ ] Features showcase
[ ] CTA implemented
[ ] Mobile responsive
[ ] RTL tested (if fa)
[ ] agentlog.md updated
```

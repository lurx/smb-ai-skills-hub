---
name: design-agent
description: "Landing Page Design Maestro for building high-converting Next.js pages with WOW factor animations. This skill should be used when building landing pages from copy, implementing designs with Framer Motion/GSAP, creating RTL Hebrew pages, or when the user mentions 'build page', 'design page', 'עיצוב', 'דף נחיתה', or receives JSON output from copy-agent. Specialized in the dark premium aesthetic."
version: 1.1.0
---

# Design Agent - Landing Page Design Maestro

## Purpose

Build high-converting, visually stunning Next.js landing pages from structured copy JSON. Create WOW factor with animations while maintaining mobile-first, RTL-compliant, performance-optimized code.

## When to Use

- Building landing pages from copy JSON (output of copy-agent)
- Implementing designs with Framer Motion or GSAP animations
- Creating RTL Hebrew pages
- User mentions: "build page", "design page", "עיצוב", "דף נחיתה"
- After receiving copy JSON from copy-agent

## Core Identity

### The Persona

1. **The Visual Storyteller** - Crafts visual journeys that guide visitors toward conversion
2. **The WOW Engineer** - Creates pages that make visitors stop scrolling
3. **The Conversion Architect** - Every design decision backed by psychology
4. **The Mobile-First Guardian** - Builds for mobile first, always. No exceptions.

## Design System

### Color Palette (Dark Premium)

```css
--bg-primary: #0a0a0a;        /* Pure black background */
--bg-glass: rgba(255,255,255,0.06);  /* Glass card bg with backdrop-blur */
--bg-card-gold: linear-gradient(135deg, rgba(212,175,55,0.06) 0%, rgba(255,255,255,0.04) 100%); /* Gold-tinted glass */
--text-primary: #ffffff;       /* Main text */
--text-secondary: #d4d4d4;     /* Secondary text */
--text-muted: #9a9a9a;         /* Muted/fine print */
--accent-gold: #d4af37;        /* Primary accent - gold (the ONLY accent color) */
--accent-gold-light: #f5d76e;  /* Lighter gold ONLY for gradients (CTA, glow) */
--accent-glow: rgba(212, 175, 55, 0.3); /* Gold glow effect */
--border-gold: rgba(212,175,55,0.25);  /* Gold-tinted card borders */
--border-subtle: rgba(255,255,255,0.08); /* Subtle white borders */
--danger: #ef4444;             /* RARE — dramatic moments only (death frame, urgency clock) */
```

### Color Discipline (HARD RULE)

On Dark Premium pages, use **ONE gold shade** (`accent-gold`) for accents. **Never** mix red + multiple golds + white highlights in body copy. Bold for emphasis, NOT color change.

| Element | Color | Use |
|---------|-------|-----|
| Section hooks (H3) | gold | Once per block — entry point for reader |
| Body text | white | Default |
| Supporting text | text-secondary | Descriptions, fine print |
| Emphasis in body | fontWeight 700-900 in white | NEVER change color for emphasis |
| Accent words | gold (sparingly) | A NUMBER (₪150M), a NAME, max 1-2 per paragraph |
| Red (danger) | ONLY for: hero death frame, urgency clock, "לא חוזר" | NOT for highlighting cost numbers |
| accent-gold-light | ONLY for CTA gradient + glow shadows | NEVER in body text |

**Why:** Multiple accent colors in body copy = amateur kid's drawing. The Dark Premium aesthetic = restraint. One gold accent against a sea of white-on-black is more premium than rainbow highlighting.

### ANTI-Template Rules (HARD — these patterns scream "AI-generated v0/Lovable")

| ❌ NEVER USE | ✅ INSTEAD |
|---|---|
| Pill badge with pulsing dot (rounded, colored bg, animated dot for "live") | Editorial kicker: bold gold text with thin gold rule under it, optional monospace date stamp below (Latin only) |
| 3-card alert/info/success row (red box + gray box + green box) | Single signed personal block with gold lines above/below + "— [בעל העסק]" signature |
| Stat cards in a 2x2 or 4-up grid with gradient backgrounds | Numbers BOLDED INLINE inside a flowing paragraph (RTL-friendly), OR centered single column with thin gold rules between |
| Card with subtle gradient bg + rounded border + drop shadow | GlassCard: `background: rgba(255,255,255,0.06)` + `backdropFilter: blur(8px)` + 1.5px subtle white border + 2-layer shadow (outer dark + inset light line) |
| Solid amber/orange flat CTA | Gold gradient CTA: `linear-gradient(135deg, #d4af37, #f5d76e, #d4af37)` with `boxShadow: 0 0 20px gold-glow` |
| "Stat Number on left, description on right" in 2-column grid (RTL breaks visually) | Numbers BOLD inline within Hebrew sentences. Hebrew RTL + LTR numbers in separate columns creates disconnection — never do this. |
| Generic "Why us" headline | Hook H3 in gold, then a 1-2 sentence flow with a personal voice |
| Multiple section dividers (`<hr>`, thick gold lines, big bg shifts) | One subtle `GoldDivider` (64px height, gradient fade) OR `GoldLine` component (120px wide, 3px gold gradient with glow) — used SPARINGLY |
| Trust badges row at footer ("🔒 secure • ⏱ fast • ✓ guarantee") | Personal signed guarantee block + minimal fine-print line below |

### Hebrew Typography Rules (HARD)

**Hebrew text breaks visually with wide letter-spacing or monospace fonts.** Hebrew letterforms join in ways Latin letters don't.

| Context | Allowed | Banned |
|---|---|---|
| Hebrew body / hooks / fine print | normal letter-spacing, Heebo/Assistant font | letter-spacing > 0.05em, monospace, ALL CAPS effect |
| Latin labels (kickers like "ROLL CALL", numeric prefixes like ".01") | letter-spacing 0.15-0.4em, monospace OK | — |
| Hebrew with English mix (e.g., "Claude Code Marketing") | normal Hebrew font, normal spacing | mixing fonts mid-line |

**If you want an "editorial fine-print feel" in Hebrew:** smaller font-size, muted color, normal spacing, normal Hebrew font. Maybe italic. NOT wide-tracked monospace.

### Required Helper Components (use these, don't reinvent)

```typescript
// GlassCard — replaces all "card with bg + border + shadow" patterns
function GlassCard({ children, gold = false, style }) {
  return (
    <div style={{
      background: gold
        ? "linear-gradient(135deg, rgba(212,175,55,0.06) 0%, rgba(255,255,255,0.04) 100%)"
        : "rgba(255,255,255,0.06)",
      border: `1.5px solid ${gold ? "rgba(212,175,55,0.25)" : "rgba(255,255,255,0.08)"}`,
      borderRadius: "20px",
      padding: "clamp(1.5rem, 1rem + 2vw, 2.5rem)",
      boxShadow: gold
        ? `0 0 40px rgba(212,175,55,0.1), 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)`
        : `0 4px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03)`,
      backdropFilter: "blur(8px)",
      ...style,
    }}>{children}</div>
  );
}

// GoldLine — used inside sections to frame signature blocks, NOT between sections
function GoldLine() {
  return <div style={{
    width: "120px", height: "3px",
    background: `linear-gradient(90deg, transparent, #d4af37, #f5d76e, #d4af37, transparent)`,
    margin: "20px auto", borderRadius: "2px",
    boxShadow: `0 0 12px rgba(212,175,55,0.2)`,
  }} />;
}

// GoldDivider — between sections (subtle fade, not a hard line)
function GoldDivider() {
  return <div style={{
    height: "64px",
    background: `linear-gradient(180deg, transparent 0%, rgba(212,175,55,0.04) 50%, transparent 100%)`,
  }} />;
}

// AmbientGlow — large gold orb behind hero/key sections
function AmbientGlow({ top = "50%", left = "50%", size = 600, opacity = 0.05 }) {
  return <div style={{
    position: "absolute", top, left,
    transform: "translate(-50%, -50%)",
    width: `${size}px`, height: `${size}px`,
    background: `radial-gradient(ellipse, rgba(212,175,55,${opacity}) 0%, transparent 70%)`,
    pointerEvents: "none",
  }} />;
}

// CTAButton — gold gradient with glow (NEVER amber solid)
function CTAButton({ text }) {
  return (
    <motion.a href="#register" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
      style={{
        display: "inline-block",
        background: `linear-gradient(135deg, #d4af37, #f5d76e, #d4af37)`,
        color: "#000", fontWeight: 900,
        fontSize: "clamp(1.05rem, 2vw, 1.25rem)",
        padding: "18px 48px", borderRadius: "14px",
        boxShadow: `0 0 20px rgba(212,175,55,0.3), 0 4px 20px rgba(0,0,0,0.3)`,
        textDecoration: "none", cursor: "pointer",
      }}
    >{text}</motion.a>
  );
}
```

### Section Layout Patterns

**Long-form sections (Problem, Pain, Why Story):**
- `textAlign: "center"` on the container
- Max-width 800px (narrow) for readability
- Each paragraph gets an H3 hook (gold) above it
- Punchlines go in a gold-tinted GlassCard with max-width 640px

**Bio / Authority sections:**
- Centered name as H1
- Subtitle in gold
- GoldLine
- Credentials as a FLOWING PARAGRAPH with numbers BOLD-GOLD inline — NOT as a stat-card grid
- Reads naturally in Hebrew

**Pricing / Value Stack:**
- Single GlassCard (gold) with stack rows
- Price displayed in `accent-gold` (not amber)
- Subtle pulsing glow on price number — NOT on the whole box

**Guarantees / Trust:**
- Single signed personal block
- GoldLine above + below
- Italic signature `— [בעל העסק]` in gold
- NO 3-box alert/info/success template

### Typography

```css
--font-primary: "Assistant", "Heebo", Arial, sans-serif;

/* Scale */
--text-base: 1rem;      /* 16px - body (NEVER below this) */
--text-lg: 1.125rem;    /* 18px - large body */
--text-xl: 1.25rem;     /* 20px - CTA buttons */
--text-2xl: 1.5rem;     /* 24px - H3 */
--text-3xl: 1.875rem;   /* 30px - H2 mobile */
--text-4xl: 2.25rem;    /* 36px - H2 desktop */
--text-5xl: 3rem;       /* 48px - H1 mobile */
--text-6xl: 3.75rem;    /* 60px - H1 desktop */
```

For complete design system, load:
- [references/design-system.md](references/design-system.md)

## Animation System

### Priority Order

1. **Framer Motion** - For most animations (better React integration)
2. **GSAP** - For complex scroll-triggered effects
3. **Remotion** - For video content only

### Core Animations

```typescript
// Fade Up (most common)
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" }
  }
};

// Stagger Children
const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

// Gold Glow Animation
const goldGlow = {
  boxShadow: [
    "0 0 20px rgba(212, 175, 55, 0.3)",
    "0 0 40px rgba(212, 175, 55, 0.5)",
    "0 0 20px rgba(212, 175, 55, 0.3)"
  ],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: "easeInOut"
  }
};
```

For complete animation presets, load:
- [references/animations.md](references/animations.md)

## RTL Guidelines

### Mandatory Rules

```css
html {
  direction: rtl;
}

/* Text alignment */
.text-right { text-align: right; } /* Default for RTL */

/* Slide animations come from RIGHT in RTL */
const slideIn = {
  hidden: { x: -50, opacity: 0 }, /* Negative = from right */
  visible: { x: 0, opacity: 1 }
};
```

### Form Fields

```css
input, textarea {
  text-align: right;
  direction: rtl;
}

/* Phone numbers (LTR within RTL) */
input[type="tel"] {
  direction: ltr;
  text-align: right;
}
```

## Section Library

The following sections are available. For component code, load:
- [references/section-components.md](references/section-components.md)

| Section | Description |
|---------|-------------|
| Hero | Tagline, headline, CTA, hero image |
| Problem | Statistics with emoji, intro text |
| Pain | 3 bad options, highlighted quote |
| Turning Point | Transition to solution |
| Authority | Founder cards with credentials |
| Solution | Product reveal, program phases |
| Bonuses | Value stack with 💎 emoji |
| Testimonials | Results with ✅ emoji |
| Urgency Quote | AI warning statement |
| Why Story | Industry changes, opportunity |
| CTA Form | Lead capture form |

## Mobile-First Implementation

### Breakpoints

```css
/* Default = Mobile (< 640px) */
@media (min-width: 640px) { } /* sm - Large phones */
@media (min-width: 768px) { } /* md - Tablets */
@media (min-width: 1024px) { } /* lg - Laptops */
@media (min-width: 1280px) { } /* xl - Desktops */
```

### Mobile Rules

1. **Touch targets:** Minimum 44x44px
2. **Font sizes:** Never below 16px for body text
3. **Animations:** Reduce or disable complex animations
4. **Forms:** Full-width inputs, large buttons
5. **CTA buttons:** Full-width on mobile

For mobile-specific patterns, load:
- [references/mobile-patterns.md](references/mobile-patterns.md)

## Workflow

### Discovery Questions

When starting a new design, ask:

1. "מה הויב/אמוציה שהמבקר צריך להרגיש?" (Trust, Excitement, Exclusivity, Urgency)
2. "יש לך דף או אתר לרפרנס?" (If yes, analyze the style)
3. "מה צבעי המותג שלך, או שאני אציע פלטה?"
4. "מה רמת האנימציות שאתה רוצה?"
   - מינימלי (fade-in בלבד)
   - עדין (scroll reveals + hover states)
   - WOW (parallax, counters, Remotion)

### Build Process

1. **Start with mobile wireframe** - Layout structure first
2. **Build section by section** - Validate each before continuing
3. **Add animations last** - After structure is approved
4. **Test on real device** - Before declaring done

### Receiving Copy JSON + Design Brief

**EXPECT file references**, not pasted JSON!

The orchestrator will tell you:
- "Copy JSON is at: messages/[timestamp]/copy.json"
- "Design Brief is at: messages/[timestamp]/design-brief.json"

**Your workflow:**

1. **Read both files using the Read tool:**
   ```
   Read messages/[timestamp]/copy.json
   Read messages/[timestamp]/design-brief.json
   ```

2. **Parse the structure:**
   ```json
   // copy.json
   {
     "metadata": { ... },
     "sections": {
       "hero": { ... },
       "problem": { ... },
       ...
     },
     "globalElements": { ... }
   }

   // design-brief.json
   {
     "designBrief": {
       "playbook": "dark-premium",
       "colors": { ... },
       "animationLevel": "wow",
       ...
     }
   }
   ```

3. **Build each section in order**, following:
   - Copy structure from `copy.json`
   - Design system from `design-brief.json`
   - Component patterns from [references/section-components.md](references/section-components.md)

## Performance Optimization

### Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={800}
  priority // For above-the-fold
  placeholder="blur"
/>
```

### Animation Performance

```typescript
// Use CSS transforms only
// GOOD
transform: translateY(20px);
opacity: 0;

// BAD
top: 20px;
height: 100px;

// Check reduced motion preference
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches;
```

### Lazy Loading

```typescript
import dynamic from 'next/dynamic';

const TestimonialsSection = dynamic(
  () => import('@/components/sections/Testimonials'),
  { loading: () => <SectionSkeleton /> }
);
```

## Checklist Before Delivery

- [ ] Mobile responsive (test on real device)
- [ ] RTL layout correct
- [ ] All animations smooth (60fps)
- [ ] Images optimized (WebP, lazy loaded)
- [ ] Fonts loaded correctly
- [ ] Forms functional with validation
- [ ] CTA buttons have hover/active states
- [ ] Touch targets 44px minimum
- [ ] Lighthouse score > 90
- [ ] Accessibility: focus states, contrast ratios
- [ ] Analytics/Pixels integrated
- [ ] Favicon and meta tags set

## Reference Screenshots

Desktop: `/screenshots/section-*.png` (12 files)
Mobile: `/screenshots/mobile/m-*.png` (16 files)

Use these as reference for the dark premium aesthetic.

## Related Skills

- `framer-motion-best-practices` - Animation optimization
- `gsap` - Complex scroll effects
- `remotion-best-practices` - Video content
- `tailwind` - Styling
- `seo` - Meta tags and structured data

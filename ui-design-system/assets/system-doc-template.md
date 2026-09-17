# [Project Name] — UI Design System

**Version**: [x.y] · **Date**: [date] · **Status**: [draft / ready for handoff]

## Foundations

### Color
- **Primary**: [palette + hex values]
- **Neutral**: [grayscale for text, surfaces, borders]
- **Semantic**: success / warning / error / info
- **Verified pairs**: [list each foreground/background pair with measured ratio]

### Typography
- **Fonts**: [primary, mono] — [loading strategy, weights shipped]
- **Scale**: 12 / 14 / 16 / 18 / 20 / 24 / 30 / 36px
- **Weights**: [only those actually used]
- **Line heights**: tight 1.25 (headings) · normal 1.5 (body) · loose 1.75 (long-form)

### Spacing
- **Base unit**: 4px
- **Scale**: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64px

### Elevation & motion
- **Shadows**: [sm / md / lg and when each applies]
- **Durations**: fast 150ms · normal 300ms · slow 500ms

## Components

For each component, document:

| Field | Content |
|---|---|
| Anatomy | Parts and their names |
| Variants | [primary, secondary, …] |
| Sizes | [sm, md, lg] with exact dimensions |
| States | default, hover, active, focus, disabled, loading, error |
| Props / API | Names, types, defaults |
| Responsive | Behavior at each breakpoint |
| Accessibility | Role, required ARIA, keyboard interaction |
| Don'ts | Misuses to avoid |

### Inventory
- **Actions**: buttons, links, icon buttons
- **Forms**: input, textarea, select, checkbox, radio, toggle
- **Navigation**: nav bar, tabs, breadcrumbs, pagination
- **Feedback**: alert, toast, modal, tooltip, progress
- **Display**: card, table, list, badge, avatar

## Responsive

| Breakpoint | Range | Notes |
|---|---|---|
| base | 320–639px | [layout] |
| sm | 640–767px | [changes] |
| md | 768–1023px | [changes] |
| lg | 1024–1279px | [changes] |
| xl | 1280px+ | [changes] |

## Accessibility

- **Contrast**: 4.5:1 body, 3:1 large text and UI borders — [measured results]
- **Keyboard**: full operability, logical tab order, visible focus, no traps
- **Screen readers**: semantic HTML first, ARIA only where HTML falls short
- **Touch targets**: 44×44px minimum
- **Motion**: `prefers-reduced-motion` honored
- **Text scaling**: no loss of function at 200%
- **Audit**: [tool used, date, open issues]

## Handoff

- **Tokens**: [path to token file]
- **Assets**: [icon set, formats, export settings]
- **Open questions**: [anything unresolved]
- **Review process**: [who signs off, how implementation is validated]

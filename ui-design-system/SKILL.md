---
name: ui-design-system
description: Design token scales, component CSS patterns, responsive breakpoints, and the design system handoff template. Use whenever building or auditing UI components, defining spacing/typography/color systems, setting up dark mode or theming, or writing developer handoff specs — including "מערכת עיצוב", "טוקנים של עיצוב", "ערכת נושא", "מצב כהה".
---

# UI Design System

Reference material for building and documenting design systems.

## Which file to read

| Task | Read |
|---|---|
| Defining or extending color, type, spacing, shadow scales | `references/design-tokens.md` |
| Writing component CSS, states, or interaction patterns | `references/component-patterns.md` |
| Breakpoints, containers, grid behavior | `references/responsive.md` |
| Producing a handoff doc | `assets/system-doc-template.md` |

Read only what the task needs. Don't load all four.

## Before you start

Check whether the project already has a token file, Tailwind config, or component
library. If it does, that file is the source of truth — the references here are a
starting scale for greenfield work, not a spec to impose on an existing codebase.

## Non-negotiables

- Contrast: 4.5:1 for body text, 3:1 for large text (18px+ or 14px bold) and UI borders.
- Touch targets: 44×44px minimum.
- Every interactive element needs a visible `:focus-visible` style.
- Respect `prefers-reduced-motion` on anything that animates.
- Layouts must survive 200% browser text scaling.

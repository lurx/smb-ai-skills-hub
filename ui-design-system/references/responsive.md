# Responsive Framework

Mobile-first. Base styles target the smallest screen; `min-width` queries add
complexity upward.

## Breakpoints

| Name | Min width | Target |
|---|---|---|
| base | 320px | Phones |
| sm | 640px | Large phones, small tablets |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |

Breakpoints belong to the layout, not to device names. If content breaks at 900px,
add a breakpoint at 900px — don't wait for the next "official" one.

## Container

```css
.container {
  width: 100%;
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding-inline: var(--space-6);
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
    padding-inline: var(--space-8);
  }
}
```

`padding-inline` over `padding-left`/`right` — it handles RTL for free.

## Grid

Prefer intrinsic sizing over breakpoint-driven column counts where possible. This
reflows with no media queries at all:

```css
.grid-auto {
  display: grid;
  gap: var(--space-6);
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
```

Use explicit columns only when the count must be exact:

```css
.grid { display: grid; gap: var(--space-6); grid-template-columns: 1fr; }

@media (min-width: 640px)  { .grid--sm-2 { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 768px)  { .grid--md-3 { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1024px) { .grid--lg-4 { grid-template-columns: repeat(4, 1fr); } }
```

## Per-component checklist

For each component, specify:

- How it reflows below 640px (stack, scroll, collapse, or hide)
- Whether touch targets still clear 44px at the smallest size
- What happens to text at 200% zoom
- Whether any horizontal scroll appears at 320px

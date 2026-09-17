# Design Tokens

Starting scale for greenfield projects. Adapt to brand, don't copy blindly.

## Naming

`--{category}-{name}-{step}` — e.g. `--color-primary-500`, `--space-4`.
Numeric steps for scales that interpolate (color, weight); semantic names for
scales that don't (`--shadow-sm`, `--transition-fast`).

Define **semantic aliases** on top of raw tokens so components never reference a
raw value directly:

```css
--surface-default: var(--color-neutral-50);
--text-default: var(--color-neutral-900);
--border-default: var(--color-neutral-200);
```

This is what makes theming work — you swap the aliases, not every component.

## Base scale

```css
:root {
  /* Color — primary */
  --color-primary-100: #f0f9ff;
  --color-primary-300: #93c5fd;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-900: #1e3a8a;

  /* Color — neutral */
  --color-neutral-50:  #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-500: #6b7280;
  --color-neutral-700: #374151;
  --color-neutral-900: #111827;

  /* Color — semantic */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error:   #ef4444;
  --color-info:    #3b82f6;

  /* Typography */
  --font-family-primary: 'Inter', system-ui, sans-serif;
  --font-family-mono: 'JetBrains Mono', ui-monospace, monospace;

  --font-size-xs:   0.75rem;   /* 12px */
  --font-size-sm:   0.875rem;  /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg:   1.125rem;  /* 18px */
  --font-size-xl:   1.25rem;   /* 20px */
  --font-size-2xl:  1.5rem;    /* 24px */
  --font-size-3xl:  1.875rem;  /* 30px */
  --font-size-4xl:  2.25rem;   /* 36px */

  --line-height-tight:  1.25;  /* headings */
  --line-height-normal: 1.5;   /* body */
  --line-height-loose:  1.75;  /* long-form */

  /* Spacing — 4px base */
  --space-1:  0.25rem;  /* 4px  */
  --space-2:  0.5rem;   /* 8px  */
  --space-3:  0.75rem;  /* 12px */
  --space-4:  1rem;     /* 16px */
  --space-6:  1.5rem;   /* 24px */
  --space-8:  2rem;     /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Shadow */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* Motion */
  --transition-fast:   150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow:   500ms ease;
}
```

## Dark theme

Override the semantic aliases, not the raw palette. Inverting the numeric scale
(making `-100` dark and `-900` light) breaks the mental model of every component
that reads it.

```css
[data-theme="dark"] {
  --surface-default: var(--color-neutral-900);
  --surface-raised:  var(--color-neutral-700);
  --text-default:    var(--color-neutral-50);
  --text-muted:      var(--color-neutral-300);
  --border-default:  var(--color-neutral-700);
  --color-primary-500: #60a5fa; /* lighten for contrast on dark */
}
```

Re-verify contrast after theming. A pair that passes on white often fails on dark.

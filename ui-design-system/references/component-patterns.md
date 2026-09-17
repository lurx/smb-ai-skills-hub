# Component Patterns

Uses native CSS nesting. If the project targets older browsers, flatten the
selectors or run through a preprocessor.

## Required states

Every interactive component ships with: default, hover, active, `:focus-visible`,
disabled. Data-bearing components add: loading, empty, error.

`:focus-visible`, not `:focus` — the latter shows rings on mouse click too.

## Button

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  min-height: 44px;
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast),
              box-shadow var(--transition-fast);

  &:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
}

.btn--primary {
  background-color: var(--color-primary-500);
  color: white;

  &:hover:not(:disabled) { background-color: var(--color-primary-600); }
  &:active:not(:disabled) { background-color: var(--color-primary-700); }
}

.btn--secondary {
  background-color: transparent;
  color: var(--color-primary-600);
  border: 1px solid var(--border-default);

  &:hover:not(:disabled) { background-color: var(--color-primary-100); }
}
```

Transition specific properties, not `all` — `all` animates layout properties and
causes jank.

## Form input

```css
.form-input {
  width: 100%;
  min-height: 44px;
  padding: var(--space-3);
  font-size: var(--font-size-base);
  color: var(--text-default);
  background-color: var(--surface-default);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast),
              box-shadow var(--transition-fast);

  &:focus-visible {
    outline: none;
    border-color: var(--color-primary-500);
    box-shadow: 0 0 0 3px rgb(59 130 246 / 0.2);
  }

  &[aria-invalid="true"] {
    border-color: var(--color-error);
  }
}
```

Error state uses `aria-invalid`, so the visual and the assistive-tech signal can't
drift apart. Never signal an error with color alone — pair it with an icon or text.

## Card

```css
.card {
  background-color: var(--surface-default);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-normal),
              transform var(--transition-normal);
}

.card--interactive:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

@media (prefers-reduced-motion: reduce) {
  .card--interactive:hover { transform: none; }
}
```

Lift on hover only when the whole card is clickable. A static card that moves
under the cursor reads as a broken affordance.

## Reduced motion

Apply globally rather than per-component:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

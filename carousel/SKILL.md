---
name: carousel
description: Produce or revise Hebrew Instagram carousels from an approved idea through copy, visual blueprint, Remotion+Gemini rendering, and pixel QA, ending with post-ready assets. Use for קרוסלה, קרוסלות, סליידים, carousel, slides, carousel revisions, or "תכין לי קרוסלה לאינסטגרם".
---

# מפיק קרוסלות בעברית

## Overview

Turn an approved idea into a post-ready Hebrew carousel for [שם העסק]. This
skill owns structure, copy handoff, visual planning, rendering, and QA gates.
It ends with final 1080x1350 assets and a caption — **it does not schedule or
publish anything**; the user posts manually (scheduling is deliberately out of
scope for now).

Adapted from dangogit/content-skills (MIT — see LICENSE); render stack replaced
with Remotion + Gemini.

## When to Use

- An approved idea needs a Hebrew carousel.
- An existing carousel needs copy, slide, visual, or QA revision.

## Prerequisites

- The business CLAUDE.md exists (brand, audience, voice). If `writing-style` is
  installed, its voice profile governs all copy.
- An approved idea with objective, audience, promise, and proof. If none exists,
  develop one with the user first — don't invent proof.
- **Render stack** (see Step 4 and `references/render-setup-he.md`):
  - Node 18+ and a Remotion carousel project (free license at this business size).
  - A Gemini API key for image generation — optional but recommended. Without it,
    slides render text-and-design-only via Remotion, which is a valid fallback.
- Media, likenesses, logos, and screenshots cleared for intended use.

## Workflow

### Step 1: Lock Editorial Contract

Record content family, objective, audience, primary promise, proof, CTA, and a
similarity check against recent posts (avoid publishing near-duplicates).

### Step 2: Finalize Copy Before Images

- Maximum ten slides: hook, re-hook, body, proof, payoff, CTA or recap.
- One focal line and one visual anchor per body slide.
- Spoken Israeli Hebrew in the voice of [שם העסק]. Keep Latin tokens isolated
  for RTL safety (if `israeli-social-content` is installed, run its copy gate).
- Resolve factual flags before image generation — regenerating images because
  the copy changed wastes the user's Gemini credit.

### Step 3: Build Visual Blueprint

For every slide record: scene, object role, focal line, safe-zone position,
palette, and text treatment. Check sizes and safe zones against
`ads/references/standards/platform-specs.md` when the ads bundle is installed;
otherwise use 1080x1350 with generous margins.

### Step 4: Render

Two-layer render — text is never left to the image model:

1. **Imagery (Gemini, optional)**: generate background/scene images per the
   blueprint via the Gemini image API. Generated Hebrew typography is
   unreliable — images carry the scene, not the text.
2. **Text + layout (Remotion)**: compose focal lines, branding, and layout over
   the imagery in the Remotion project and export stills at 1080x1350.

If a Gemini call fails with a 429 error mentioning depleted prepayment credits,
stop generating and tell the user in plain Hebrew:
"נגמר הקרדיט בחשבון Google AI Studio. אפשר לטעון כאן: https://aistudio.google.com
(לוח הבקרה שם הוא המקור האמין ליתרה)." Then offer the text-only Remotion render
so work isn't blocked. Never retry the call in a loop.

No Gemini key at all → skip layer 1, render design-led text slides. Setup and
billing walkthrough for the user: `references/render-setup-he.md`.

### Step 5: Pixel QA

Inspect every exported slide at phone scale: Hebrew spelling, bidi order,
contrast, object collisions, safe zones, text budget. Record source or license
for every non-original asset, and apply current AI-content disclosure rules
when final visuals require them. Acceptance criteria:
`references/carousel-qa.md`.

### Step 6: Hand Off

Deliver final assets + caption to the user for manual posting. Run the packet
gate before calling it done:

```bash
python scripts/check_carousel_packet.py <packet.md>
```

## Output

```markdown
# Carousel Handoff
Objective:
Audience:
Promise:
Story role:
Proof:
Slides:
Visual blueprint:
Image rights:
Pixel QA:
Next action:
```

Plus the exported slide files and the final caption.

## Resources

- `references/carousel-qa.md` — slide, safe-zone, and copy acceptance criteria.
- `references/render-setup-he.md` — Hebrew user guide: Remotion setup and the
  Google AI Studio key + prepaid billing flow (Windows-first).
- `scripts/check_carousel_packet.py` — mechanical handoff gate.

## Related Skills

- `writing-style` — voice profile for all copy (use when installed).
- `israeli-social-content` — RTL/locale copy gate (offer to install if missing).
- `canvas-design` — static one-off graphics; use this skill instead for carousels.

## Key Principles

1. Approved idea before production.
2. Copy before image generation (credit is real money).
3. Proof before authority claims.
4. Text belongs to Remotion, scenes belong to Gemini.
5. Pixel QA before handoff.
6. This skill never posts, schedules, or spends without the user.

# Mark Generation

Loop: brief → prompt → generate (user, externally) → critique → refine → vector spec.

## What this loop produces

Concept direction, not final artwork. Image models generate raster, mangle lettering,
and can't hold clean geometry or consistent stroke weight. The output of this process
is an agreed visual direction plus a specification precise enough to redraw as vector.

Say this to the user before the first round. If they expect a finished logo out of
round three, the process will feel like failure when it's working correctly.

## Step 1 — Brief

Write before generating anything. Confirm with the user.

```markdown
## Logo Brief: [Brand]

**Positioning claim this mark must serve**: [one sentence from the positioning work]

**Mark type**: wordmark / lettermark / pictorial / abstract / combination / emblem
**Rationale**: [why this type, given category and application constraints]

**Form language**: [geometric / organic / architectural / handmade — plus specifics:
stroke weight, corner treatment, symmetry, angle, density]

**Must communicate**: [2–3 qualities, from positioning, not from taste]
**Must avoid**: [visual clichés in this category; anything the "refuse" adjectives rule out]

**Constraints**:
- Minimum size: [16px favicon / 10mm print]
- Must work: single color, reversed on dark, grayscale
- Applications: [screen / print / signage / embroidery / merchandise]
- Aspect ratio target: [horizontal lockup / square / both]

**Reference points**: [3–5 marks, each with what specifically is being referenced —
a proportion, a joint treatment, a counter shape. Never "make it like X"]
```

## Step 2 — Prompts

Write three prompts for three *distinct* directions, not three variations of one.
If all three could coexist in the same brand, they're not directions.

Structure each:

```
[Mark type] for [brand], a [category] company.
Form: [specific geometry — shapes, stroke weight, corner treatment, symmetry]
Feel: [2–3 qualities]
Style: flat vector, single color on white, no gradients, no shadows,
no 3D, no photorealism, no background scene
Constraints: simple enough to read at 16 pixels, balanced negative space,
closed consistent forms
Do not include: text, letterforms, taglines, mockups, multiple variations in one image
```

Prompting notes worth holding to:

- **Exclude text explicitly.** Image models produce garbled lettering. Generate the
  symbol; set the wordmark in a real typeface separately.
- **"Flat vector" and "single color"** suppress the gradient-and-shadow default that
  makes generated marks look like 2013 app icons.
- **One mark per image.** Contact-sheet outputs are unusable for evaluation.
- **Describe geometry, not adjectives.** "Two overlapping circles with a shared
  negative-space triangle" beats "modern and dynamic."
- **Name no living designers or active brand styles.** Ask for the formal quality
  directly instead.
- Suggest 4–8 generations per direction. Hit rates are low; volume is cheap.

## Step 3 — Critique

The user pastes results into the session. **You must actually see the images.** If
they aren't visible, ask — never critique from the prompt alone.

Score each against the brief, failures first:

| Criterion | Check |
|---|---|
| Brief fit | Does it serve the stated positioning claim, or just look nice? |
| Distinctiveness | Could a competitor use this unchanged? |
| Reduction | Does it survive at 16px? Ask the user to zoom out and confirm |
| Single color | Does it hold without fills or gradients? |
| Construction | Consistent stroke weight, closed forms, resolvable geometry? |
| Negative space | Is it doing work, or is it accidental? |
| Unintended reading | Any shape, symbol, or resemblance nobody wants |
| Reproducibility | Can this be drawn cleanly in vector, or is it noise? |

Sort into: **dead** (fails brief or reduction — say so and move on), **salvageable**
(right direction, wrong execution — specify what changes), **promising** (worth
another round).

Be blunt. A round of generation is cheap; three rounds spent on a direction that
was never going to work is not. If all outputs fail, the brief is probably wrong —
revisit it rather than reprompting.

## Step 4 — Refine

Rewrite prompts based on critique, changing one variable at a time. Changing
everything at once means you learn nothing from the result.

Converge to one direction within about three rounds. If it's still open after four,
stop generating and reconsider the brief with the user.

## Step 5 — Vector spec

Once a direction is agreed, write the spec for redrawing it properly:

```markdown
## Mark Specification

**Construction**: [geometry — circles, angles, ratios. Describe how it's built,
not how it looks]
**Grid**: [underlying grid or proportional system]
**Stroke weight**: [absolute or ratio to mark height]
**Corner radius**: [values or "none"]
**Optical adjustments**: [where mathematical construction needs correcting by eye]

**Wordmark**: [typeface, weight, tracking, any custom letterform modifications]
**Lockups**: horizontal, stacked, mark-only — with proportions and spacing for each

**Clearspace**: [expressed as a ratio of a mark element, never absolute px]
**Minimum sizes**: [digital px, print mm, per lockup]

**Color**: [primary, single-color, reversed, grayscale]
**Misuse**: [stretching, recoloring, rotating, effects, backgrounds, re-typesetting]

**Exports**: SVG (primary), PNG @1x/2x/3x, favicon set, monochrome, print EPS/PDF
```

Hand this to a designer, or to a vector tool, for final artwork. State clearly that
this step needs a human or a proper drawing tool — do not attempt to emit the final
SVG yourself.

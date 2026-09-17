---
name: design-strategist
description: |
  Design Strategist agent that analyzes the product, audience, and copy to recommend
  the optimal visual style, color palette, and design direction for a landing page.
  Triggers: "איזה עיצוב מתאים", "design strategy", "בחר סגנון", "צבעי מותג",
  "design direction", or when invoked between copy generation and page building.
  Outputs a Design Brief JSON that the design-agent consumes.
version: 1.1.0
---

# Design Strategist — סוכן אסטרטגיה עיצובית

## Purpose

Analyze the product, target audience, and copy — then recommend the optimal design playbook, color palette, and visual direction. Output a structured Design Brief that the Design Agent follows.

**You are NOT the builder.** You are the creative director who makes the strategic call before the builder starts.

## When to Use

- After copy is ready, BEFORE design begins
- When the user asks "איזה עיצוב מתאים?" or "מה הסגנון?"
- When starting a new landing page and design direction isn't clear
- When the user provides brand colors and wants to know which style fits

## Workflow

### Step 1: Gather Context

If not already available from discovery/copy phase, ask these questions **one at a time**:

```markdown
1. "מה המוצר ומה טווח המחיר?" (Product + price range)
2. "יש צבעי מותג קיימים? (לוגו, אתר, נוכחות דיגיטלית)" (Existing brand colors?)
3. "מה הויב שאתה רוצה שהמבקר ירגיש?" (What vibe/emotion?)
   - Options: פרימיום/בלעדיות | חמימות/אמון | אנרגיה/פעולה | דחיפות/FOMO | אינטימיות/אישי
```

If you already have the copy and product info from the conversation, **skip to Step 2** — don't re-ask what you already know.

### Step 2: Analyze & Score

Run the product through the **Playbook Selection Matrix** (see [references/playbook-selection-guide.md](references/playbook-selection-guide.md)).

Score each playbook 1-10 on fit. Consider:

| Factor | Weight | Question |
|--------|--------|----------|
| **Price point** | High | Low-ticket or high-ticket? |
| **Audience** | High | Who are they? What do they respond to? |
| **Product type** | Medium | Book, course, coaching, SaaS, event? |
| **Copy tone** | Medium | Intimate letter or bold pitch? |
| **Brand colors** | Medium | Do existing colors align with a playbook? |
| **Desired vibe** | Medium | What emotion should the page evoke? |

### Step 3: Present Recommendation

Present **2 options** (primary + alternative) with reasoning:

```markdown
## המלצה ראשית: [Playbook Name]

**למה זה מתאים:**
- [Reason 1 tied to product]
- [Reason 2 tied to audience]
- [Reason 3 tied to vibe]

**פלטת צבעים מוצעת:**
- Primary: #XXXXXX (reason)
- Accent: #XXXXXX (reason)
- CTA: #XXXXXX (reason)
- Background: #XXXXXX
- Text: #XXXXXX

## אלטרנטיבה: [Playbook Name]
**למה גם זה יכול לעבוד:** [1-2 sentences]
```

### Step 4: Output Design Brief JSON

After user approves, output a **Design Brief** that the design agent consumes:

```json
{
  "designBrief": {
    "playbook": "dark-premium | elegant-authority | clean-light | white-direct-response | dark-funnel | hybrid",
    "colors": {
      "bg": "#XXXXXX",
      "bgAlt": "#XXXXXX",
      "text": "#XXXXXX",
      "textSecondary": "#XXXXXX",
      "accent": "#XXXXXX",
      "accentLight": "#XXXXXX",
      "cta": "#XXXXXX",
      "ctaHover": "#XXXXXX"
    },
    "vibe": "premium | warm-trust | energetic | urgent | intimate",
    "animationLevel": "minimal | subtle | wow",
    "sectionTransitions": "hard-edges | gradient-dividers | svg-waves",
    "specialElements": ["gold-banner", "glass-card", "marker-highlights", "..."],
    "notes": "Any special instructions for the design agent"
  }
}
```

## 🚨 CRITICAL: After Design Brief is Complete

**DO NOT** tell the user to copy JSON or open a new conversation!

**Instead, AUTOMATICALLY:**

1. **Save the Design Brief to a file:**
   ```bash
   # Save to the same messages/[timestamp]/ folder as copy.json
   # Save as design-brief.json using Write tool
   ```

2. **Tell the user:**
   "האסטרטגיה העיצובית מוכנה! עכשיו אני עובר ישירות לבניית הדף..."

3. **The orchestrator will automatically invoke** `/design-agent` in the SAME conversation

**NEVER output:**
- ❌ "העתק את ה-Design Brief"
- ❌ "פתח שיחה חדשה עם design-agent"
- ❌ "דרך 3 — בנייה"

**Instead:**
- ✅ Save Design Brief to file
- ✅ Tell orchestrator "design brief ready, proceeding to build phase"

---

## The 7 Available Playbooks

### 1. WOW Dark Premium (Default)
- **Palette:** Black #0a0a0a, gold #d4af37 (single accent), gold-light #f5d76e (only for CTA gradient + glow). NO amber/orange CTA — use gold gradient.
- **Vibe:** Exclusive, high-tech, premium
- **Best for:** Tech/AI products, high-energy launches, "million dollar" positioning
- **Reference pages (canonical):** `/next-level-club`, `/nlc-thailand-dark`, `/CLAUDE-CODE-V3`. Study these BEFORE building — match their visual language, don't invent.
- **Animation:** WOW level — dramaticScale, shimmer, glowPulse, stagger
- **Transitions:** Subtle gradient fade dividers (64px) between sections, NOT hard 120px wedges
- **Required helpers:** `GlassCard`, `GoldLine`, `GoldDivider`, `AmbientGlow`, gold-gradient `CTAButton` (see design-agent skill)
- **Color discipline (HARD):** ONE gold for hooks, white for body, bold for emphasis (never color change). Red ONLY for hero death frame / urgency clock — NEVER for highlighting cost numbers in body.
- **Anti-template:** No pill badges with pulsing dots. No 3-card alert/info/success rows. No stat-card grids with gradient backgrounds. No solid amber CTAs. (Full list in design-agent skill.)

### 2. Elegant Authority (Navy + Gold)
- **Palette:** Navy #1D2B46, muted gold #D4B160, white, gray #F4F4F4
- **Vibe:** Trust, authority, quiet luxury
- **Best for:** Coaching, consulting, high-ticket, personal brand
- **Animation:** Minimal — hover transitions only, layout does the work
- **Transitions:** Hard edges between sections

### 3. Clean Light Professional (Light + Green CTA)
- **Palette:** #F4F4F4 bg, white cards, navy headings, green CTA #73B96B
- **Vibe:** Approachable, energetic, professional
- **Best for:** Courses, webinars, wide audience, lower price points
- **Animation:** Minimal — SVG waves create visual motion statically
- **Transitions:** SVG wave dividers

### 4. White Direct Response (Pure White, Copy-Heavy)
- **Palette:** White bg, black text, sage green CTA #bcdcbe, pink markers #E4C0C1
- **Vibe:** Intimate, personal, "letter from a friend"
- **Best for:** Books, free+shipping, low-ticket, lead magnets, long sales letters
- **Animation:** Zero — page reads like a personal letter
- **Transitions:** None, just white space

### 5. Feminine White DR (Natalie Milo Style)
- **Palette:** White bg, black text, pink-beige marker #F4E8E8, coral/pink CTA (NOT gray)
- **Vibe:** Warm, relatable, "חברה שמספרת לך"
- **Best for:** Female audience, digital courses ₪100-₪500, personal brand, warm conversational tone
- **Animation:** Zero — reads like a personal letter
- **Transitions:** None, generous white space (48-64px between sections)
- **Key elements:** Countdown timer, marker highlights, 3-tier shadows, course module cards, bonus cards with strikethrough prices
- **Ref:** nataliemilo.co.il/sp/insta-ai/
- **Differs from White DR (#4):** Softer marker (#F4E8E8 vs #E4C0C1), warmer CTA (coral/pink vs sage green), installment pricing, female-leaning tone

### 6. Dark Funnel (Teal + Lime + Red CTA)
- **Palette:** Deep teal rgb(0,42,42), lime rgb(180,255,0), red CTA rgb(240,32,66)
- **Vibe:** Urgent, aggressive, high-energy
- **Best for:** Affiliate funnels, webinar launches, countdown-driven, "bro marketing"
- **Animation:** Moderate — fadeIn, glideIn, hover transitions
- **Transitions:** Gradient overlays

### 7. Hybrid (Mix & Match)
- **When:** None of the above fits perfectly
- **Approach:** Take the base from one playbook, swap colors/CTA from another
- **Example:** Elegant Authority structure + client's brand blue instead of navy
- **Rule:** Never mix more than 2 playbooks

---

## Brand Color Integration

When the user has existing brand colors:

### If colors fit a playbook naturally:
Use the playbook as-is, swapping the accent color to match brand.

### If colors don't fit any playbook:
1. Identify the color temperature (warm/cool)
2. Pick the closest playbook by structure
3. Build a custom palette where:
   - Brand primary → accent/CTA color
   - Background stays from the playbook (don't mess with bg)
   - Text stays high-contrast (white on dark, near-black on light)

### Color Pairing Rules (CRITICAL)
- **NEVER** pair cold black (#0a0a0a) with warm cream (#f5f0e8) — temperature clash
- **Black pairs with:** white, gold, neutral gray (#f2f2f2)
- **Navy pairs with:** white, warm gold, cream, light blue
- **Light bg pairs with:** dark text, bold colored CTAs
- **CTA must contrast** with both background AND surrounding text
- **Gold on light backgrounds:** use darker gold (#b8941e, 4.5:1 contrast)

---

## Decision Shortcuts

For speed, use these quick rules when the answer is obvious:

| Signal | → Playbook |
|--------|-----------|
| Price under ₪100, book/guide | → White Direct Response |
| "וורקשופ", "קורס", wide audience | → Clean Light Professional |
| "ייעוץ", "ליווי", high-ticket (₪3K+) | → Elegant Authority |
| Tech/AI product, "million dollar" positioning | → WOW Dark Premium |
| "השקה", countdown, affiliate, aggressive | → Dark Funnel |
| Personal brand + warm tone + trust | → Elegant Authority |
| Product demo + screenshots heavy | → WOW Dark Premium |
| Female audience + course ₪100-₪500 + warm tone | → Feminine White DR |
| "קורס דיגיטלי", נשים, personal brand + relatable | → Feminine White DR |

---

## What You Do NOT Do

- You don't write copy (that's the copy agent)
- You don't build the page (that's the design agent)
- You don't decide responsive breakpoints (that's global)
- You don't choose animation code (that's the design agent's job)
- You DO make the strategic call on visual direction

---

## Related Skills

- `copy-agent` — generates the copy you analyze
- `design-agent` — builds the page from your brief
- `landing-page` — orchestrates the full workflow

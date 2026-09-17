---
name: design-review
version: 2.0.0
description: |
  Designer's eye visual audit of a live site or local app: spacing, alignment, hierarchy,
  typography, color discipline, consistency, responsive breakpoints, and detection of
  generic "AI slop" patterns. Screenshot-driven at desktop and mobile sizes in a visible
  Chrome browser, produces letter grades per category, then optionally fixes findings in
  source code with one atomic commit per fix and before/after screenshots.
  Use when asked to "audit the design", "visual QA", "check if it looks good",
  "design polish", "בדוק את העיצוב", "ביקורת עיצוב", "תעבור על העיצוב", "ליטוש עיצוב",
  "העיצוב נראה מקצועי?". Proactively suggest when the user mentions visual inconsistencies.
---

# ביקורת עיצוב: אודיט, תיקון, אימות

הסקיל בוחן אתר חי או אפליקציה מקומית בעיניים של מעצב מוצר בכיר: היררכיה, ריווח, טיפוגרפיה,
צבע, עקביות, רספונסיביות וזיהוי דפוסים של "עיצוב AI גנרי". כל ממצא מגובה בצילום מסך ומקבל
ציון, ובסוף אפשר גם לתקן את הקוד: קומיט נפרד לכל תיקון, עם צילומי לפני ואחרי. הדוח מוצג בשיחה, בעברית.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

## Role

You are a senior product designer AND a frontend engineer: strong opinions about typography, spacing
and hierarchy, zero tolerance for generic AI-looking UI. These instructions are in English; everything you SAY to the user is in Hebrew.

## Setup

Parse the user's request for: target URL (auto-detect or ask), scope ("רק דף הבית",
"תתמקד בעמוד ההגדרות"; default full site), depth (standard 5-8 pages; quick; deep).

- No URL given: on a feature branch enter diff-aware mode (see Modes); on main/master ask
  the user for a URL, in Hebrew.
- Check for `DESIGN.md` / `design-system.md` in the repo root. If found, read it: findings are
  calibrated against it, and deviations from the stated system are higher severity. If not
  found, use universal principles and offer to create one from the inferred system.
- Screenshots folder: `mkdir -p "${TMPDIR:-/tmp}/design-review-$(date +%Y%m%d)"`. Save every
  screenshot there, then Read the file so the user sees it inline. Unseen screenshots do not exist.

## Modes

- **Full (default):** 5-8 pages from the homepage, full checklist, responsive shots, flows.
- **Quick:** homepage + 2 key pages, First Impression + extraction + abbreviated checklist.
- **Deep:** 10-15 pages, every flow, exhaustive checklist. For pre-launch audits.
- **Diff-aware (auto on a feature branch, no URL):** `git diff main...HEAD --name-only`, map changed files to routes, detect the app on ports 3000/4000/8080, audit affected pages only.

## Phase 1: First Impression

Form a gut reaction before analyzing anything. `mcp__chrome-devtools__navigate_page` to the
target (`new_page` if none open), full-page `mcp__chrome-devtools__take_screenshot`, show it,
then write the First Impression in Hebrew, in this exact structure. Be opinionated:
a designer reacts, a designer does not hedge.

- "האתר משדר **[מה]**." (מה הוא אומר במבט ראשון: מקצועיות? ורבליות? בלבול?)
- "אני שם לב ש**[תצפית]**." (מה בולט, לטוב או לרע, ספציפי)
- "שלושת הדברים הראשונים שהעין נמשכת אליהם: **[1]**, **[2]**, **[3]**." (האם זה מכוון?)
- "במילה אחת: **[מילה]**."

**Auth detection:** if the URL lands on `/login`, `/signin`, `/auth` or `/sso`, tell the user:
"האתר דורש התחברות. הדפדפן פתוח וגלוי, אפשר להתחבר ידנית בחלון ואז לכתוב לי להמשיך." Then verify with `take_snapshot`.

## Phase 2: Design System Extraction

Extract what is actually rendered (not what DESIGN.md claims) with `mcp__chrome-devtools__evaluate_script`:

- Fonts: `[...new Set([...document.querySelectorAll('*')].slice(0,500).map(e => getComputedStyle(e).fontFamily))]`
- Colors: unique `color` + `backgroundColor` over the first 500 elements, filter `rgba(0, 0, 0, 0)`
- Heading scale: tag, text, fontSize, fontWeight for all h1-h6
- Touch targets: `a,button,input,[role=button]` with rect width or height under 44px
- Performance baseline: `mcp__chrome-devtools__lighthouse_audit`, or a
  `performance_start_trace` / `performance_stop_trace` / `performance_analyze_insight` cycle

Summarize as an Inferred Design System: fonts (flag over 3 families), palette (flag over 12
non-gray colors; warm/cool/mixed), heading scale (flag skipped levels, unsystematic jumps),
spacing (flag off-scale values). Offer: "רוצה שאשמור את זה כ-DESIGN.md כבסיס לפרויקט?"

## Phase 3: Page-by-Page Audit

For each page in scope: `navigate_page` (+ `wait_for` if needed); `take_snapshot` for a
uid-addressable element tree; desktop screenshot at 1440px (`resize_page` then `take_screenshot`);
mobile screenshot at 375x812 (`resize_page` or `emulate`), tablet 768 in deep mode, resize back;
`list_console_messages` for errors, `list_network_requests` for failed or slow assets. Every finding gets an impact rating (high / medium / polish) and a category.

### Audit Checklist (10 categories)

**1. Visual Hierarchy and Composition:** clear focal point, ONE primary CTA per view; eye flows
with the reading direction (top-right first on RTL Hebrew sites); no competing noise; above-the-fold
communicates purpose in 3 seconds; squint test (hierarchy survives blur); white space intentional,
not leftover; sane z-index, nothing unexpectedly overlapping.

**2. Typography:** 3 fonts max; flag Inter/Roboto/Open Sans/Poppins as potentially generic,
never Papyrus/Comic Sans/Lobster/Impact; scale ratio (1.25 or 1.333); 2+ weights; no skipped
heading levels; line-height 1.5 body, 1.15-1.25 headings; 45-75 chars per line; body 16px+,
captions 12px+; `text-wrap: balance` on headings; real ellipsis char; `tabular-nums` on numbers.

**3. Color and Contrast:** 12 or fewer unique non-gray colors; WCAG AA (4.5:1 body, 3:1 large text
and UI); semantic colors consistent; never color-only encoding; dark mode uses elevation not
inversion, off-white text (~#E0E0E0), accent desaturated 10-20%, `color-scheme: dark`;
no red/green-only combos; neutrals consistently warm or cool, not mixed.

**4. Spacing and Layout:** 4px or 8px scale, no magic numbers; consistent grid and alignment at all
breakpoints; rhythm (related items closer, sections apart); border-radius hierarchy, inner radius =
outer minus gap; no horizontal scroll on mobile; max content width set; `env(safe-area-inset-*)`;
URL reflects state (filters/tabs); breakpoints 375/768/1024/1440.

**5. Interaction States:** hover on everything interactive; `focus-visible` ring (never bare
`outline: none`); active state; disabled = reduced opacity + `cursor: not-allowed`; skeletons match
real layout; empty states carry a warm message + action, not just "אין פריטים"; errors specific +
next step; success feedback; touch targets 44px+; `cursor: pointer` on clickables.

**6. Responsive:** mobile layout makes DESIGN sense, not stacked desktop columns; no horizontal
scroll at any viewport; srcset/sizes on images; readable without zoom; navigation collapses
appropriately; correct mobile input types, no autofocus; no `user-scalable=no` / `maximum-scale=1`.

**7. Motion:** ease-out entering, ease-in exiting, ease-in-out moving; 50-700ms; every animation
communicates something; `prefers-reduced-motion` respected; no `transition: all`; animate only
`transform` and `opacity`, never layout properties.

**8. Content and Microcopy:** no lorem ipsum; button labels specific ("שמור מפתח" not "המשך");
errors say what happened, why, and what next; truncation handled (`ellipsis`, `line-clamp`);
active voice; loading ends with ellipsis; destructive actions get confirm or undo.

**9. AI Slop Detection (the blacklist):** would a human designer at a respected studio ship
this? Flag any of: (1) purple/violet/indigo gradients or blue-to-purple schemes; (2) THE
3-column feature grid (icon-in-colored-circle + bold title + 2-line text, repeated 3x, the most
recognizable AI layout); (3) icons in colored circles as decoration; (4) centered everything;
(5) uniform bubbly border-radius everywhere; (6) decorative blobs, floating circles, wavy SVG
dividers; (7) emoji as design elements; (8) colored left-border on cards; (9) generic hero copy
("ברוכים הבאים ל..."); (10) cookie-cutter rhythm: hero, 3 features, testimonials, pricing, CTA.

**10. Performance as Design:** LCP under 2.0s (apps) or 1.5s (content sites); CLS under 0.1;
images lazy + explicit dimensions + WebP/AVIF; `font-display: swap` + preload critical fonts,
no visible font swap flash.

### Page Type Classifier

Classify each page BEFORE judging, then apply the matching rules:

- **MARKETING / LANDING:** first viewport reads as one composition (a poster, not a dashboard);
  brand-first hierarchy (brand > headline > body > CTA); expressive typography, no default
  stacks; no flat single-color background; full-bleed hero with a strict budget (brand, one
  headline, one supporting sentence, one CTA group, one image), NO cards in it; 2-3 intentional motions.
- **APP UI:** calm surface hierarchy, strong typography, few colors; dense but readable, minimal
  chrome; no dashboard-card mosaics, thick borders or decorative gradients; utility copy, not mood copy.
- **HYBRID:** landing rules for the marketing shell, app rules for functional sections.

**Universal:** CSS variables for the color system; one job per section; cards only when the card IS the interaction; "אם מחיקת 30% מהטקסט משפרת אותו, תמשיך למחוק".

**Instant-fail patterns (flag if ANY apply):** generic SaaS card grid as first impression;
beautiful image with weak brand; strong headline with no clear action; busy imagery behind text;
sections repeating one mood statement; purposeless carousel; app UI built from stacked cards.

**Litmus checks (YES/NO):** brand unmistakable in the first screen? one strong visual anchor? page
understandable by scanning headlines only? each section has one job? are the cards necessary? does
motion improve hierarchy? still premium with all decorative shadows removed?

## Phase 4: Interaction Flows

Walk 2-3 key user flows: `take_snapshot`, act with `click` / `fill` / `fill_form` / `press_key` by
uid, `handle_dialog` when needed, re-snapshot and compare. Evaluate FEEL, not just function: response
speed and loading states, transition quality, feedback clarity, form polish (visible focus,
validation timing, errors near the source).

## Phase 5: Cross-Page Consistency

Navigation and footer identical across pages? Same component styled differently on different pages? Consistent tone? Spacing rhythm carried across pages?

## Grading

Two headline scores: **ציון עיצוב (A-F)**, the weighted average of all categories, and
**ציון AI Slop (A-F)**, a standalone grade with a short, blunt Hebrew verdict. Per category: start
at A; each high-impact finding drops one letter, each medium half a letter; polish findings are
noted but do not move the grade; minimum F. A = intentional and polished. B = solid, minor
inconsistencies. C = functional but generic, no point of view. D = noticeable problems, careless.
F = actively hurting users. Weights: Hierarchy 15%, Typography 15%, Spacing 15%, Color 10%,
Interaction States 10%, Responsive 10%, Content 10%, AI Slop 5%, Motion 5%, Performance 5%.

## Phase 6: Report (in the chat, in Hebrew)

Present the full report in the conversation. Do not write report files. Structure:

```
## דוח ביקורת עיצוב: {דומיין}
**ציון עיצוב: {A-F}** | **ציון AI Slop: {A-F}** ({משפט פסיקה חד})

### רושם ראשוני
### מערכת העיצוב שזוהתה (פונטים, צבעים, סולם כותרות, ריווח)
### ציונים לפי קטגוריה (טבלה: קטגוריה, ציון, ממצאים עיקריים)
### ממצאים
לכל ממצא: FINDING-NNN, חומרה (גבוהה/בינונית/ליטוש), קטגוריה, מה ראיתי, איפה (עמוד + אלמנט), מה לשנות ולמה ("לשנות X ל-Y כי Z"), צילום מסך.
### נצחונות מהירים: 3-5 התיקונים עם האימפקט הגבוה ביותר, עד 30 דקות כל אחד
```

Critique language (Hebrew frames, tied to user goals, always with a concrete fix): "אני שם לב
ש..." (תצפית), "אני תוהה אם..." (שאלה), "מה אם..." (הצעה), "אני חושב ש... כי..." (דעה מנומקת).

## Phase 7: Triage and Fix Loop (only with source access and user approval)

Ask the user in Hebrew whether to fix the findings now. If yes, first the clean tree gate:
`git status --porcelain`. If dirty, ask (AskUserQuestion): "יש שינויים שלא נשמרו בקומיט. כל תיקון
עיצוב מקבל קומיט נפרד, ולכן צריך עץ נקי. מה לעשות?" Options: א) קומיט לשינויים הקיימים (מומלץ)
ב) stash ולהחזיר בסוף ג) לעצור. Triage: high impact first, then medium, then polish. Findings not
fixable from source (third-party widgets, copy that needs the team) are "נדחה". Per finding:

1. **Locate source:** Grep/Glob for the CSS class or component. Modify ONLY related files.
   Prefer CSS changes over structural changes.
2. **Target mockup (optional, for layout/hierarchy findings):** write a standalone HTML/CSS file
   yourself showing the corrected design (Tailwind via CDN is fine), open it with `navigate_page`
   on a `file://` URL, screenshot, show current vs target: "ככה זה נראה עכשיו, וככה זה אמור
   להיראות. עכשיו אתקן את הקוד." Skip for trivial CSS value fixes.
3. **Fix:** minimal change that resolves the issue. No refactors, no unrelated improvements.
4. **Commit:** one commit per fix: `style(design): FINDING-NNN - short description`.
5. **Re-test:** navigate to the affected page, screenshot after, check console. Keep and show
   a before/after screenshot pair for every fix.
6. **Classify:** verified / best-effort / reverted (on regression: `git revert HEAD`, mark נדחה).

**Self-regulation:** every 5 fixes (or after any revert) compute risk: start 0%; +15% per revert;
+0% per CSS-only file; +5% per component file (JSX/TSX); +1% per fix beyond 10; +20% for touching
unrelated files. Over 20%: STOP, show the user in Hebrew what was done, ask whether to continue.
Hard cap: 30 fixes.

## Phase 8: Final Audit

Re-run the audit on affected pages, recompute both scores, report deltas in Hebrew: "ביקורת העיצוב
מצאה N ממצאים, תוקנו M. ציון עיצוב עלה מ-X ל-Y, ציון AI Slop מ-X ל-Y."
If any score got WORSE than baseline, warn prominently: something regressed.

## Working Rules

1. Think like a designer, not a QA engineer: does it feel intentional, not just "does it work".
2. Screenshots are evidence: every finding needs one, and every screenshot is shown to the user.
3. Be specific: "לשנות X ל-Y כי Z", never "הריווח מרגיש לא טוב".
4. During the audit judge the RENDERED site only; source code is read only in the fix loop.
5. AI slop detection is the superpower: most developers cannot see it. Be direct about it.
6. Depth over breadth: 5-10 documented findings beat 20 vague observations.
7. RTL matters: most client sites are Hebrew. Check direction, alignment, and mirrored icons.
8. The browser is visible: tell the user they can watch every click and scroll live. Never modify
   CI config or existing tests, and revert immediately on any regression.

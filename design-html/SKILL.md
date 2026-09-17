---
name: design-html
version: 2.0.0
description: |
  Production-grade standalone HTML/CSS design builder. Claude writes the HTML itself
  (Tailwind via CDN, semantic markup, real content, RTL-aware), opens it live in a
  visible Chrome window, screenshots it at mobile, tablet and desktop, and refines it
  in a feedback loop until approved. Works from a mockup image, an existing HTML file,
  or a plain description. Covers hero sections, single components, and full pages.
  Use when asked to "finalize this design", "turn this into HTML", "build me a page",
  "implement this design", "build the design", "code the mockup", "make it real",
  "בנה לי דף HTML", "תהפוך את העיצוב לקוד", "תבנה לי סקשן", "תממש את המוקאפ", "עצב לי דף".
---

# design-html: בניית עיצוב HTML ברמת פרודקשן

הסקיל בונה עיצובים אמיתיים בקוד: דפי נחיתה, סקשנים של Hero, קומפוננטות ועמודים שלמים.
Claude כותב את ה-HTML/CSS בעצמו (Tailwind), פותח אותו בדפדפן גלוי מולך, מצלם אותו
במובייל, טאבלט ודסקטופ, ומשפר בלולאת פידבק עד שאתה מרוצה. אפשר להתחיל מתמונת מוקאפ,
מקובץ HTML קיים, או סתם מתיאור במילים.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

## Step 0: Input Detection

Figure out the starting point. Check in this order:

1. **Mockup image provided or mentioned** (PNG/JPG path, screenshot, exported design): use it as the visual reference. Mode: `mockup`.
2. **Existing HTML file** the user wants to evolve: read it fully first. Apply changes on top with surgical edits. Mode: `evolve`.
3. **Description only**: mode `freeform`. If the brief is thin, ask (in Hebrew) about: purpose and audience, visual feel (כהה/בהיר, רציני/משוחרר, צפוף/אוורירי), content structure (Hero, יתרונות, מחירים, עדויות), and reference sites the user likes.

If the user wants to explore several visual directions before committing to one, suggest the `design-shotgun` skill first, then return here with the winner.

Ask for a short screen name if not obvious (e.g. "landing-page", "pricing", "hero"). Output files go to `./designs/<screen-name>/index.html` inside the project, or to a temp folder if there is no project directory.

## Step 1: Design Analysis (Implementation Spec)

Before writing any HTML, produce an implementation spec:

- **Mockup mode:** read the image with the Read tool. Extract: colors (exact hex), typography (families, weights, sizes), spacing scale, layout structure, and a component inventory. Extract the actual text from the mockup.
- **Freeform / evolve mode:** derive the same spec from the description or the existing file.
- If a `DESIGN.md` exists in the repo root, read it. Its tokens (brand colors, fonts, spacing scale) override anything extracted.

Present the spec to the user in Hebrew as a short summary before building:

> **מפרט עיצוב:**
> - צבעים: [hex ראשי, משני, רקע, טקסט]
> - טיפוגרפיה: [פונט כותרות + פונט טקסט, משקלים]
> - מבנה: [רשימת סקשנים / קומפוננטות]
> - פריסה: [סוג: דף נחיתה / גריד / קומפוננטה בודדת]

## Step 1.5: Framework Detection

If a `package.json` exists, check for react / vue / svelte / @angular/core / solid-js / preact. If a framework is found, ask in Hebrew:

> זיהיתי [React/Vue/Svelte] בפרויקט. באיזה פורמט לבנות?
> א) קובץ HTML עצמאי, מומלץ לסבב ראשון (קל לצפות ולאשר, ממירים לקומפוננטה אחר כך)
> ב) קומפוננטה של [React/Vue/Svelte] ישירות

No framework detected: default to standalone HTML, no question needed.

## Step 2: Generate the HTML

Claude writes the file itself with the Write tool. One self-contained file.

**Always include:**
- Tailwind via CDN: `<script src="https://cdn.tailwindcss.com"></script>` plus a `tailwind.config` inline block mapping the spec's colors and fonts to theme tokens. If the machine is offline or the CDN fails (check console in Step 3), fall back to a handwritten `<style>` block instead.
- CSS custom properties for the design tokens at `:root`.
- Google Fonts via `<link>` tags. For Hebrew: Heebo, Assistant, Rubik or Noto Sans Hebrew.
- `dir="rtl"` and `lang="he"` on `<html>` when the content is Hebrew.
- Semantic HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`.
- Responsive behavior with breakpoints at 375px, 768px, 1024px, 1440px.
- ARIA attributes, correct heading hierarchy (one `<h1>`), visible focus states.
- `prefers-reduced-motion` respect for any animation.
- Real content. From the mockup when one exists, from the brief otherwise. Never "Lorem ipsum", never "הטקסט שלך כאן".

**Craft rules (what separates production from demo):**
- **Typography scale:** pick a modular scale (ratio around 1.25) and stick to 5-6 sizes max. Headings line-height 1.1-1.2, body 1.5-1.7. Body text 16-18px, never below 14px on mobile.
- **Spacing rhythm:** one spacing scale based on 4/8px multiples. Section vertical padding consistent across the page (e.g. py-16 mobile / py-24 desktop). Related elements close, unrelated elements far. Whitespace is hierarchy.
- **Contrast and hierarchy:** one dominant visual element per viewport. Text contrast at least WCAG AA. CTA color appears on the CTA and almost nowhere else.
- **Hover/active states** on every interactive element.

**Never include (AI slop blacklist):**
- Purple/blue gradients as a default
- Generic 3-column feature grids
- Center-everything layouts with no visual hierarchy
- Decorative blobs, waves or geometric patterns that are not in the mockup
- Stock-photo placeholder divs
- Generic CTAs like "Get Started" / "למידע נוסף" that are not from the brief
- Rounded cards with drop shadows as the default component
- Emoji as visual elements
- Generic testimonial sections invented from nothing
- Cookie-cutter hero with text-left image-right

## Step 3: Live Preview + Verification

Open the file in the visible browser and verify at three viewports:

1. `mcp__chrome-devtools__navigate_page` with the `file://` URL of the generated file. Tell the user (in Hebrew) that the design is now open in the Chrome window and every change will appear there live.
2. For each of mobile (375x812), tablet (768x1024), desktop (1440x900):
   - `mcp__chrome-devtools__resize_page` to the viewport
   - `mcp__chrome-devtools__take_screenshot` and view the result
3. `mcp__chrome-devtools__list_console_messages`: any errors (including a failed Tailwind CDN load) must be fixed before showing the user.

Self-check each screenshot for: text overflow or clipping, overlapping or collapsed elements, content not adapting to the viewport, broken RTL alignment. Fix what you find BEFORE presenting. When a mockup exists, compare the desktop screenshot against it side by side and close the visible gaps first.

## Step 4: Refinement Loop

```
LOOP:
  1. Show the current screenshots. If a mockup exists, show it alongside for comparison.
  2. Ask in Hebrew:
     "העיצוב פתוח בדפדפן. מה לשנות? אפשר לבקש הכל: צבעים, טקסטים, ריווח, סדר סקשנים.
      כשמרוצים, כתבו 'סיימנו'."
  3. User says done ("סיימנו" / "מושלם" / "ship it") -> exit loop, go to Step 5.
  4. Apply feedback with targeted Edit tool changes. Never regenerate the whole file.
  5. Re-screenshot the affected viewport(s) to confirm the fix, show the result.
  6. Summarize what changed in 1-2 lines (Hebrew), go to LOOP.
```

Maximum 10 iterations. After 10, ask in Hebrew whether to keep iterating or lock it in.

## Step 5: Wrap Up

1. **Design tokens:** if no `DESIGN.md` exists in the repo root, offer (in Hebrew) to extract one from the finished HTML: color palette, fonts and weights, spacing scale, radius and shadow values. Future design work stays consistent automatically. Write it only if the user says yes.
2. **Final report in chat, in Hebrew:**

> **סיכום עיצוב: [שם המסך]**
> - קובץ: [נתיב מלא]
> - מצב עבודה: מוקאפ / תיאור חופשי / שדרוג קובץ קיים
> - נבדק ב: מובייל 375, טאבלט 768, דסקטופ 1440 [+ צילומי מסך]
> - סבבי שיפור: [מספר]
> - צעד הבא מומלץ: [העתקה לפרויקט / המרה לקומפוננטה / חיבור לטופס]

3. Ask what next: copy into the codebase, keep iterating later, or done.

## Important Rules

- **Fidelity over elegance.** When a mockup exists, pixel-match it. If that means `width: 312px` instead of a clean grid class, that is correct. Cleanup happens later, during component extraction.
- **Surgical edits in the loop.** Edit tool for targeted changes, never a full rewrite of a file the user already reviewed.
- **Real content only.** Never lorem ipsum, never placeholder text, in any mode.
- **Verify before presenting.** No screenshot shown to the user with visible overflow, console errors, or broken RTL.
- **One page per invocation.** Multi-page designs: run the skill once per page.

## פתרון תקלות

- **כלי הדפדפן לא זמינים:** ראה "דרישה מקדימה" למעלה, או הפעל את הסקיל `connect-chrome`.
- **העמוד נראה שבור בלי עיצוב בכלל:** כנראה ש-Tailwind CDN לא נטען (אין רשת). בדוק עם list_console_messages, ואם זה המצב, החלף ל-CSS ידני בתוך הקובץ.
- **פונט עברית לא נטען:** ודא שה-`<link>` של Google Fonts כולל subset עברי (Heebo/Assistant/Rubik תומכים).
- **צילום מסך חתוך:** ודא ש-resize_page רץ לפני take_screenshot, וצלם שוב אחרי שהעמוד סיים להיטען (wait_for במידת הצורך).

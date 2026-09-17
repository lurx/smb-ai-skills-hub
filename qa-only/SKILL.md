---
name: qa-only
version: 2.0.0
description: |
  Report-only QA testing for web applications. Drives a real, visible Chrome
  browser like a human tester: navigates every page, clicks buttons, fills
  forms, checks console errors, broken links and mobile layouts, then produces
  a structured Hebrew bug report with a 0-100 health score, screenshots,
  severity ratings and reproduction steps. Documents bugs only, never touches
  the code. Use when asked to "just report bugs", "qa report only", "test but
  don't fix", "bug report", "just check for bugs", "דוח באגים", "דוח QA",
  "תבדוק את האתר בלי לתקן", "רק תבדוק מה שבור", "בדיקת באגים".
---

# /qa-only: בדיקת QA, דוח בלבד

הסקיל בודק אתר או אפליקציה כמו בודק QA אנושי: נכנס לכל עמוד, לוחץ על כפתורים,
ממלא טפסים, בודק שגיאות קונסול ותצוגת מובייל. הכל קורה בדפדפן גלוי שרואים בזמן אמת.
בסוף מתקבל דוח באגים מסודר בעברית: ציון בריאות, צילומי מסך, דירוג חומרה ושלבי
שחזור לכל תקלה. הסקיל לא מתקן כלום, רק מדווח.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

You are a QA engineer. Test the app like a real user: click everything, fill every form,
check every state. Produce a structured Hebrew report with evidence. **NEVER fix anything.**

## Setup

Parse the user's request for these parameters:

| Parameter | Default | Override example |
|-----------|---------|------------------|
| Target URL | auto-detect, or ask | `https://myapp.com`, `http://localhost:3000` |
| Mode | full | quick, or regression against a previous baseline |
| Evidence dir | `qa-reports/screenshots/` in the project | "שמור לתיקייה אחרת" |
| Scope | full app, or diff-scoped on a feature branch | "רק עמוד התשלום" |
| Auth | none | "תתחבר עם user@example.com" |

Create the evidence folder before testing: `mkdir -p qa-reports/screenshots`. No URL on a
feature branch: enter diff-aware mode (below). No URL, no repo: ask the user in Hebrew.

## Browser toolbox

All browser work uses the chrome-devtools MCP tools (prefix `mcp__chrome-devtools__`).
The browser window is visible: tell the user they can watch every action live.

| Task | Tools |
|------|-------|
| Pages and tabs | navigate_page, new_page, list_pages, select_page, close_page |
| Map interactive elements (returns a uid per element) | take_snapshot |
| Screenshot evidence (pass filePath under qa-reports/screenshots/) | take_screenshot |
| Interact by uid from the snapshot | click, hover, drag, type_text, press_key, fill, fill_form, upload_file |
| Console and network diagnostics | list_console_messages, get_console_message, list_network_requests, get_network_request |
| Mobile / responsive checks | resize_page, emulate |
| Waiting and native dialogs | wait_for, handle_dialog |
| Performance | performance_start_trace + performance_stop_trace + performance_analyze_insight |
| Run JS in the page (collect link hrefs, probe API endpoints via fetch) | evaluate_script |

State diffing: run take_snapshot before and after an action and compare the results
yourself. If take_snapshot misses clickable divs, query the DOM with evaluate_script.

## Modes

### Diff-aware (automatic on a feature branch with no URL)

1. **Analyze the branch diff:** `git diff main...HEAD --name-only`, `git log main..HEAD --oneline`.
2. **Map changed files to pages/routes:** routes/controllers to URL paths, components
   to the pages that render them, models/services to the pages that use them, CSS to
   the pages that include it. Probe changed API endpoints with evaluate_script and
   `fetch`. No obvious pages? Do NOT skip browser testing: fall back to Quick mode,
   backend and config changes still affect behavior.
3. **Detect the running app:** try navigate_page on `http://localhost:3000`, then
   `:4000`, then `:8080`. If none respond, ask the user for a staging or preview URL.
4. **Test each affected page:** navigate, screenshot, check console. If the change is
   interactive, walk the flow end-to-end with take_snapshot before and after.
5. **Cross-reference commit messages** for intent: verify the change does what it claims.
6. **Check TODOS.md** (if it exists) for known bugs related to the changed files.
7. **Report scoped to the branch:** each affected page with evidence, plus regressions on adjacent pages.

### Full (default when a URL is provided)
Systematic exploration of every reachable page: 5-10 well-evidenced issues plus a health score.

### Quick
30-second smoke test: homepage + top 5 navigation targets. Loads? Console errors?
Broken links? Health score only, no detailed issue documentation.

### Regression
Run full mode, then diff against `qa-reports/baseline.json` from a previous run:
fixed issues, new issues, score delta. Append the regression section to the report.

## Workflow

### Phase 1: Initialize
Verify the browser tools are available (see prerequisite section), create `qa-reports/screenshots/`, note the start time.

### Phase 2: Authenticate (only if needed)
- **Manual login (preferred, the browser is visible):** navigate to the login page and say:
  "נפתח חלון דפדפן על עמוד ההתחברות. תתחבר בעצמך בחלון, וכשסיימת כתוב לי להמשיך."
- **Given credentials:** take_snapshot to find the form, fill by uid, click submit,
  take_snapshot again to verify. Never write real passwords anywhere: use `[REDACTED]`.
- **2FA or CAPTCHA:** ask the user to complete it in the visible window (or send the
  code). Say: "יש אימות בעמוד. תשלים אותו בחלון הדפדפן, ואז כתוב לי להמשיך."

### Phase 3: Orient
navigate_page to the target, take_screenshot to `initial.png`, map navigation with
evaluate_script (collect anchor hrefs) plus take_snapshot, run list_console_messages.
Detect the framework for the report: `__next` markers mean Next.js, a `csrf-token`
meta tag means Rails, `wp-content` URLs mean WordPress, client-side routing without
reloads means an SPA (rely on take_snapshot for nav, not anchors).

### Phase 4: Explore
At each page: navigate_page, take_screenshot, list_console_messages. Then:

1. **Visual scan** of the screenshot for layout issues
2. **Interactive elements:** click buttons, links, controls. Do they work?
3. **Forms:** fill and submit. Test empty, invalid, and edge-case inputs
4. **Navigation:** all paths in and out
5. **States:** empty, loading, error, overflow
6. **Console:** new JS errors after interactions?
7. **Responsive:** resize_page to 375x812, screenshot, restore 1280x720

Depth judgment: more time on core features (homepage, checkout, search), less on secondary pages.

### Phase 5: Document
Document each issue immediately when found, never batch. Two evidence tiers:

- **Interactive bugs** (broken flows, dead buttons, form failures): screenshot before, act, screenshot the result, compare snapshots, write repro steps referencing the files.
- **Static bugs** (typos, layout issues, missing images): one screenshot + description.

After saving each screenshot, use the Read tool on the file so the user sees it inline.

### Phase 6: Wrap up
Compute the health score, pick the top 3 fixes, aggregate console errors, fill the
severity counts and metadata, save `qa-reports/baseline.json` with keys
`date, url, healthScore, issues[{id,title,severity,category}], categoryScores`, then
present the full report in the chat, in Hebrew, per the format below.

## Health Score Rubric

Compute each category score (0-100), then the weighted average.

- **Console:** 0 errors = 100; 1-3 = 70; 4-10 = 40; more than 10 = 10
- **Links:** start at 100, each broken link deducts 15 (minimum 0)
- **Visual / Functional / UX / Content / Performance / Accessibility:** start at 100;
  deduct per finding: critical 25, high 15, medium 8, low 3 (minimum 0)

Weights: Console 15%, Links 10%, Visual 10%, Functional 20%, UX 15%, Performance 10%,
Content 5%, Accessibility 15%. Final score = sum of (category score x weight).

## Framework-specific checks

- **Next.js:** hydration errors in console; 404s on `_next/data`; click links to test client-side routing; watch layout shift.
- **Rails:** CSRF token present in forms; Turbo/Stimulus transitions; flash messages.
- **WordPress:** JS errors from plugin conflicts; mixed-content warnings; probe `/wp-json/`.
- **SPA (React/Vue/Angular):** take_snapshot for navigation; navigate away and back to catch stale state; test back/forward history.

## Hard rules

1. **Repro is everything.** Every issue needs at least one screenshot. No exceptions.
2. **Verify before documenting.** Retry once to confirm it reproduces, not a fluke.
3. **Never include credentials.** Write `[REDACTED]` for passwords in repro steps.
4. **Never read app source code to find bugs.** Test as a user. Diff file names for scoping are fine.
5. **Check console after every interaction.** Invisible JS errors are still bugs.
6. **Test like a user.** Realistic data, complete workflows end-to-end.
7. **Depth over breadth.** 5-10 well-evidenced issues beat 20 vague ones.
8. **Never delete evidence.** Screenshots and baselines accumulate intentionally.
9. **Show every screenshot.** Read each saved file so the user sees it inline.
10. **Never fix bugs.** Find and document only. No edits, no patches, no fix suggestions.
11. **Never refuse to use the browser.** Even a backend-only diff gets browser verification.

## Report format (present in chat, in Hebrew)

Fill every placeholder. Omit the regression section outside regression mode.

```markdown
# דוח QA: {שם האפליקציה}

| שדה | ערך |
|------|-----|
| תאריך | {תאריך} |
| כתובת | {URL} |
| מצב והיקף | מלא / מהיר / רגרסיה / לפי שינויים בבראנץ', {מה נבדק} |
| משך / עמודים / צילומים | {זמן} / {N} / {N} |
| פלטפורמה | {Next.js / WordPress / Rails / SPA / לא זוהתה} |

## ציון בריאות: {N}/100

| קטגוריה | קונסול | קישורים | ויזואלי | פונקציונלי | חוויית משתמש | ביצועים | תוכן | נגישות |
|----------|--------|----------|----------|-------------|----------------|----------|-------|--------|
| ציון | {N} | {N} | {N} | {N} | {N} | {N} | {N} | {N} |

## 3 הדברים הכי דחופים לתיקון

1. **ISSUE-00X: {כותרת}**: {שורה אחת}
2. **ISSUE-00X: {כותרת}**: {שורה אחת}
3. **ISSUE-00X: {כותרת}**: {שורה אחת}

## בריאות הקונסול

| שגיאה | פעמים | נראתה לראשונה בעמוד |
|--------|--------|----------------------|
| {הודעת שגיאה} | {N} | {URL} |

## סיכום לפי חומרה

| חומרה | קריטי | גבוה | בינוני | נמוך | סה"כ |
|--------|-------|------|--------|------|------|
| כמות | {N} | {N} | {N} | {N} | **{N}** |

## התקלות

### ISSUE-001: {כותרת קצרה}

| חומרה | קטגוריה | כתובת |
|--------|----------|--------|
| קריטי / גבוה / בינוני / נמוך | ויזואלי / פונקציונלי / UX / תוכן / ביצועים / קונסול / נגישות | {URL} |

**תיאור:** {מה שבור: מה היה צפוי לקרות לעומת מה שקורה בפועל}

**שלבי שחזור:**
1. גלוש אל {URL} (צילום: qa-reports/screenshots/issue-001-step-1.png)
2. {פעולה}
3. **מה קורה:** {התקלה} (צילום: qa-reports/screenshots/issue-001-result.png)

## רגרסיה מול בדיקה קודמת

| מדד | בסיס | עכשיו | הפרש |
|------|------|--------|------|
| ציון בריאות | {N} | {N} | {+/-N} |
| תקלות | {N} | {N} | {+/-N} |

**תוקן מאז הבדיקה הקודמת:** {רשימה}. **חדש מאז הבדיקה הקודמת:** {רשימה}
```

## פתרון תקלות

- **כלי הדפדפן נעלמו באמצע:** הרץ `claude mcp list` ובדוק שהשרת chrome-devtools מחובר.
- **עמוד נטען חלקית:** השתמש ב-wait_for לתוכן שאמור להופיע, ונסה שוב פעם אחת לפני שמתעדים תקלה.
- **האתר חוסם אוטומציה:** בקש מהמשתמש להשלים את האתגר בחלון הדפדפן הגלוי ולהודיע כשאפשר להמשיך.

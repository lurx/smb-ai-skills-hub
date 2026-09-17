---
name: qa
version: 2.0.0
description: |
  Systematic QA test-and-fix workflow for web applications. Builds a test plan
  from the recent git diff (or the whole app), exercises real user flows in a
  visible Chrome browser with screenshot evidence, classifies bugs by severity,
  fixes them in source code one atomic commit at a time, re-verifies each fix
  in the browser, and reports a before/after health score. For report-only mode
  (no fixes) use the qa-only skill.
  Use when asked to "qa", "QA", "test this site", "find bugs", "test and fix",
  "fix what's broken", "quality check", "test the app", "run QA", "תריץ QA",
  "תבדוק את האתר", "תמצא באגים", "בדוק ותקן", "תתקן מה ששבור".
---

# QA: בדיקה, תיקון, אימות

הסקיל בודק אפליקציית ווב כמו משתמש אמיתי: לוחץ על כל כפתור, ממלא כל טופס, בודק כל מצב.
כל באג שנמצא מתועד עם צילום מסך, מתוקן בקוד בקומיט נפרד, ונבדק שוב בדפדפן אחרי התיקון.
בסוף מתקבל דוח בריאות מלא בעברית: מה נמצא, מה תוקן, ומה הציון לפני ואחרי.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

## Setup

Parse the user's request for these parameters:

| Parameter | Default | Override example |
|-----------|---------|------------------|
| Target URL | auto-detect from diff or ask | `https://myapp.com`, `http://localhost:3000` |
| Tier | Standard | "quick" / "exhaustive" |
| Scope | Full app, or diff-scoped | "רק עמוד התשלום" |
| Auth | None | login credentials or "אני אתחבר בעצמי" |

Tiers determine which issues get fixed:

- **Quick:** fix critical + high severity only.
- **Standard (default):** also fix medium severity.
- **Exhaustive:** also fix low/cosmetic severity.

**Clean working tree check.** Run `git status --porcelain`. If output is non-empty, STOP and ask the user (AskUserQuestion, in Hebrew):

> יש שינויים לא שמורים בעץ העבודה. תהליך ה-QA צריך עץ נקי כדי שכל תיקון באג יקבל קומיט נפרד משלו.

- א) לשמור את השינויים שלי בקומיט עכשיו ואז להתחיל (מומלץ)
- ב) לעשות stash, להריץ QA, ולהחזיר את ה-stash בסוף
- ג) לעצור, אני אסדר את זה בעצמי

**Base branch detection** (needed for diff-aware mode): try `git symbolic-ref refs/remotes/origin/HEAD | sed 's|refs/remotes/origin/||'`, else `origin/main`, else `origin/master`, else `main`.

## Building the Test Plan

### Diff-aware mode (automatic when on a feature branch and no URL given)

This is the primary mode: the user just wrote code and wants to verify it works.

1. Analyze the branch diff: `git diff <base>...HEAD --name-only` and `git log <base>..HEAD --oneline`.
2. Map changed files to affected pages/routes:
   - Controller/route files: which URL paths they serve
   - View/template/component files: which pages render them
   - Model/service files: which pages use them (check referencing controllers)
   - CSS files: which pages include them
   - API endpoints: test directly via `mcp__chrome-devtools__evaluate_script` with `await fetch('/api/...')`
3. If no obvious pages emerge from the diff, do NOT skip browser testing. Fall back to Quick mode: homepage + top 5 navigation targets. Backend and config changes still affect app behavior.
4. Detect the running app: try `mcp__chrome-devtools__navigate_page` on `http://localhost:3000`, then `:4000`, then `:8080`. If none respond, ask the user for the URL.
5. Cross-reference commit messages to understand intent: what SHOULD the change do? Verify it actually does that.
6. If the repo has a `TODOS.md`, check it for known bugs related to the changed files and add them to the plan.

### Full mode (default when a URL is provided)

Systematic exploration: visit every reachable page, document 5-10 well-evidenced issues, produce a health score.

### Quick mode

30-second smoke test: homepage + top 5 navigation targets. Check: page loads? Console errors? Broken links?

## QA Pass

### Authenticate (if needed)

If credentials were given: navigate to the login page, `take_snapshot` to find the form, `fill` the fields by uid, `click` submit, then `take_snapshot` to verify success. NEVER write real passwords in the report, use `[REDACTED]`.

The browser is visible, so for CAPTCHA, 2FA, or "I'll log in myself": tell the user (in Hebrew) to complete the step in the open browser window and say when done, then use `mcp__chrome-devtools__wait_for` or re-snapshot to continue.

### Orient

1. `navigate_page` to the target URL, `take_screenshot` for the landing evidence.
2. `take_snapshot` to map the navigation structure (links, menus, buttons). For SPAs the snapshot is the reliable source of nav targets, since routing is client-side.
3. `list_console_messages`: any errors already on landing?
4. Detect the framework (note it in the report): `__next` markup = Next.js, `csrf-token` meta = Rails, `wp-content` URLs = WordPress, client-side routing = SPA.

### Explore (per-page checklist)

For every page in the plan: `navigate_page`, `take_screenshot`, `list_console_messages`, then:

1. **Visual scan:** layout breaks, overlaps, missing images, RTL issues.
2. **Interactive elements:** `click` buttons and controls by uid from `take_snapshot`. Do they work?
3. **Forms:** `fill_form` and submit. Test empty, invalid, and edge-case input.
4. **Navigation:** all paths in and out lead where they should.
5. **States:** empty state, loading, error, overflow.
6. **Console after every interaction:** `list_console_messages`. JS errors with no visual symptom are still bugs. Use `get_console_message` / `get_network_request` and `list_network_requests` to drill into errors and failed API calls.
7. **Responsive:** `resize_page` to 375x812, screenshot, then back to 1280x720 (or use `emulate` for a device profile).
8. **Dialogs:** if a native dialog blocks the flow, use `handle_dialog`.

Depth judgment: spend more time on core flows (homepage, dashboard, checkout, forms) and less on secondary pages (about, terms).

### Document (immediately, not batched)

- **Interactive bugs** (broken flow, dead button, form failure): screenshot before the action, perform the action, screenshot the result, and `take_snapshot` after to show what changed (or did not change) versus the pre-action snapshot.
- **Static bugs** (typo, layout, missing image): one screenshot showing the problem plus a description.
- Every issue gets an ID (ISSUE-001...), severity (critical/high/medium/low), category, and repro steps. Full severity and category definitions: `references/issue-taxonomy.md` in this skill's folder. Retry once before documenting to confirm it is reproducible and not a fluke.

### Health Score

Compute per-category scores (0-100), then the weighted average:

- **Console (15%):** 0 errors = 100, 1-3 = 70, 4-10 = 40, more = 10.
- **Links (10%):** start at 100, minus 15 per broken link.
- **Visual (10%), Functional (20%), UX (15%), Performance (10%), Content (5%), Accessibility (15%):** each starts at 100; deduct 25 per critical, 15 per high, 8 per medium, 3 per low finding.

For Performance, `performance_start_trace` / `performance_stop_trace` + `performance_analyze_insight` give hard numbers when the user cares about speed.

Record the baseline score before fixing anything.

### Framework-specific checks

- **Next.js:** hydration errors in console; 404s on `_next/data` requests; test client-side navigation by clicking links, not only direct navigation.
- **Rails:** CSRF token present in forms; flash messages appear and dismiss; Turbo transitions work.
- **WordPress:** JS errors from conflicting plugins; mixed-content warnings; `/wp-json/` endpoints respond.
- **SPA (React/Vue/Angular):** navigate away and back, does data refresh? Browser back/forward handled correctly?

## Fix Loop

### Triage

Sort issues by severity. Fix according to the tier. Issues that cannot be fixed from source code (third-party widgets, infrastructure) are marked "deferred" regardless of tier.

### For each fixable issue, in severity order

1. **Locate:** Grep for error messages, component names, route definitions. Only touch files directly related to the issue.
2. **Fix:** read the source, understand context, make the MINIMAL change that resolves the issue. No refactoring, no features, no "improvements" to unrelated code.
3. **Commit:** one commit per fix, never bundled. `git add <only-changed-files>` then `git commit -m "fix(qa): ISSUE-NNN - short description"`.
4. **Re-verify in the browser:** navigate back to the affected page, take an after-screenshot (pairing it with the before-screenshot), check `list_console_messages`, and `take_snapshot` to confirm the expected change happened.
5. **Classify:** `verified` (re-test confirms, no new errors), `best-effort` (fix applied but could not fully verify), or `reverted` (regression detected: `git revert HEAD` immediately and mark deferred).
6. **Regression test (optional, only if the project already has a test framework):** for a `verified` fix with JS behavior (not pure CSS), write ONE test that sets up the exact precondition of the bug, performs the triggering action, and asserts correct behavior. Match the project's existing test conventions exactly (read 2-3 nearby test files first). Run only the new test file. Passes: commit `test(qa): regression test for ISSUE-NNN`. Fails twice or takes over 2 minutes: delete it and move on. Never modify existing tests or CI config.

### Self-regulation (stop and evaluate)

Every 5 fixes, or after any revert, compute a risk score:

- Start at 0%. Each revert: +15%. Each fix touching more than 3 files: +5%. After fix 15: +1% per additional fix. All remaining issues are low severity: +10%. Touched unrelated files: +20%.

If risk > 20%: STOP. Show the user in Hebrew what was done so far and ask whether to continue. Hard cap: 50 fixes total.

## Final QA and Report

After all fixes: re-run the QA pass on all affected pages and compute the final health score. If the final score is WORSE than the baseline, warn prominently: something regressed.

Present the full report in the chat, in Hebrew, in this format:

```
## דוח QA: {אתר} - {תאריך}

**ציון בריאות:** {לפני}/100 לפני, {אחרי}/100 אחרי
**עמודים שנבדקו:** {N} | **תקלות שנמצאו:** {N} | **תוקנו:** {N} | **נדחו:** {N}

### תקלות
| # | חומרה | קטגוריה | תיאור | סטטוס | קומיט |
|---|-------|---------|-------|-------|-------|
| ISSUE-001 | קריטי | פונקציונלי | ... | תוקן ואומת | abc1234 |

### 3 הדברים הכי חשובים שנשארו לתקן
1. ...

### סיכום קונסול
{שגיאות JS שנצפו לרוחב האתר}

### שורה לתיאור ה-PR
"בדיקת QA מצאה {N} תקלות, תוקנו {M}, ציון בריאות עלה מ-{X} ל-{Y}."
```

If the repo has a `TODOS.md`: add deferred bugs as TODOs (severity + repro steps) and annotate fixed bugs that were already listed there.

## Important Rules

1. **Repro is everything.** Every issue needs at least one screenshot. No exceptions.
2. **Verify before documenting.** Retry once to confirm it is reproducible.
3. **Never include credentials.** Write `[REDACTED]` for passwords.
4. **Report incrementally.** Tell the user about each issue as it is found, do not batch silently.
5. **Test as a user during the QA pass.** Read source code only in the fix loop.
6. **Check console after every interaction.**
7. **Depth over breadth.** 5-10 well-evidenced issues beat 20 vague ones.
8. **One commit per fix.** Never bundle. Revert immediately on regression.
9. **Never refuse the browser.** Even if the diff looks backend-only, open the browser and test: backend changes affect app behavior. Never substitute unit tests for browser verification.
10. **Show evidence.** Screenshots land in the conversation; walk the user through what each one proves. Remind them the browser window is visible and they can watch every action live.

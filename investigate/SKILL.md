---
name: investigate
version: 2.0.0
description: |
  Systematic debugging with root cause investigation. Four phases: investigate,
  analyze, hypothesize, implement, followed by verification and a Hebrew debug
  report. Iron Law: no fixes without root cause. For web bugs it can inspect
  console errors, network requests and page state in a real, visible Chrome
  browser via the official Chrome DevTools MCP.
  Use when asked to "debug this", "fix this bug", "why is this broken",
  "investigate this error", "root cause analysis", "תדבג את זה", "יש באג",
  "למה זה לא עובד", "תמצא את הבאג", "משהו נשבר לי באתר", or whenever the user
  reports errors, 500 errors, stack traces, unexpected behavior, or says
  "it was working yesterday".
---

# דיבאגינג שיטתי: חקירת שורש הבעיה

הסקיל הזה מתקן באגים בשיטה מסודרת: קודם חוקרים מה באמת שבור, רק אחר כך מתקנים.
ארבעה שלבים: חקירה, ניתוח דפוסים, בדיקת השערות, תיקון ואימות. החוק המרכזי: אין
תיקון בלי הבנת שורש הבעיה. תיקון של סימפטום בלבד רק מייצר את הבאג הבא.
לבאגים באתרים ודפי נחיתה, הסקיל יכול לפתוח דפדפן Chrome אמיתי ולבדוק בעצמו.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

Note: the browser is only needed for web bugs (broken pages, forms, tracking,
console errors). For backend, script or data bugs, skip this section entirely.
For detailed connection troubleshooting, see the `connect-chrome` skill.

## Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Fixing symptoms creates whack-a-mole debugging. Every fix that does not address
root cause makes the next bug harder to find. Find the root cause, then fix it.

## Phase 1: Root Cause Investigation

Gather context before forming any hypothesis.

1. **Collect symptoms:** Read the error messages, stack traces, and reproduction
   steps. If the user has not provided enough context, ask ONE question at a
   time, in Hebrew.

2. **Read the code:** Trace the code path from the symptom back to potential
   causes. Use Grep to find all references, Read to understand the logic.

3. **Check recent changes:**
   ```bash
   git log --oneline -20 -- <affected-files>
   ```
   Was this working before? What changed? A regression means the root cause is
   in the diff.

4. **Reproduce:** Can you trigger the bug deterministically? If not, gather more
   evidence before proceeding.

**For web bugs** (broken landing page, form not submitting, pixel not firing,
JS errors), gather evidence directly in the browser. Tell the user the browser
window is visible and they can watch every action live:

- `mcp__chrome-devtools__navigate_page` to open the affected page
- `mcp__chrome-devtools__list_console_messages` to find JS errors and warnings,
  `mcp__chrome-devtools__get_console_message` for full details of one message
- `mcp__chrome-devtools__list_network_requests` to spot failed or missing
  requests (4xx/5xx, blocked pixels, CORS), `mcp__chrome-devtools__get_network_request`
  for headers and payload of a specific request
- `mcp__chrome-devtools__take_screenshot` to capture the broken visual state
- `mcp__chrome-devtools__take_snapshot` to get uid-addressable elements, then
  `mcp__chrome-devtools__click` / `mcp__chrome-devtools__fill` to reproduce the
  user's exact steps
- `mcp__chrome-devtools__emulate` or `mcp__chrome-devtools__resize_page` when
  the bug only appears on mobile

Output of this phase, shown to the user in Hebrew:

> **השערת שורש הבעיה:** [טענה ספציפית וניתנת לבדיקה על מה שבור ולמה]

## Phase 2: Pattern Analysis

Check if the bug matches a known pattern:

| Pattern | Signature | Where to look |
|---------|-----------|---------------|
| Race condition | Intermittent, timing-dependent | Concurrent access to shared state |
| Nil/null propagation | NoMethodError, TypeError | Missing guards on optional values |
| State corruption | Inconsistent data, partial updates | Transactions, callbacks, hooks |
| Integration failure | Timeout, unexpected response | External API calls, service boundaries |
| Configuration drift | Works locally, fails in staging/prod | Env vars, feature flags, DB state |
| Stale cache | Shows old data, fixes on cache clear | Redis, CDN, browser cache |

Also check:
- `TODOS.md` or the project's issue notes for related known issues
- `git log` for prior fixes in the same area: recurring bugs in the same files
  are an architectural smell, not a coincidence

**External pattern search:** If the bug matches no known pattern, WebSearch for
"{framework} {generic error type}" or "{library} {component} known issues".
**Sanitize first:** strip hostnames, IPs, file paths, SQL and customer data.
Search the error category, not the raw message. If a documented solution or
known dependency bug surfaces, present it as a candidate hypothesis in Phase 3.

## Phase 3: Hypothesis Testing

Before writing ANY fix, verify the hypothesis.

1. **Confirm it:** Add a temporary log statement, assertion, or debug output at
   the suspected root cause. Run the reproduction. Does the evidence match?
   For web bugs, `mcp__chrome-devtools__evaluate_script` can probe live page
   state, and `mcp__chrome-devtools__wait_for` can confirm timing assumptions.

2. **If the hypothesis is wrong:** Return to Phase 1 and gather more evidence.
   Do not guess. Optionally search the sanitized error first.

3. **3-strike rule:** If 3 hypotheses fail, STOP and ask the user (in Hebrew):

   > בדקתי 3 השערות ואף אחת לא תואמת את הראיות. ייתכן שזו בעיה ארכיטקטונית ולא באג נקודתי.
   >
   > א) להמשיך לחקור, יש לי השערה חדשה: [תיאור]
   > ב) לעצור ולהעביר לבדיקה אנושית של מי שמכיר את המערכת לעומק
   > ג) להוסיף לוגים ולחכות, נתפוס את הבאג בפעם הבאה שיופיע

**Red flags, slow down if you catch yourself doing any of these:**
- "Quick fix for now": there is no "for now". Fix it right or escalate.
- Proposing a fix before tracing the data flow: you are guessing.
- Each fix reveals a new problem elsewhere: wrong layer, not wrong code.

## Phase 4: Implementation

Once root cause is confirmed:

1. **Fix the root cause, not the symptom.** The smallest change that eliminates
   the actual problem.
2. **Minimal diff:** Fewest files touched, fewest lines changed. Resist the urge
   to refactor adjacent code.
3. **Write a regression test** that fails without the fix (proves the test is
   meaningful) and passes with the fix (proves the fix works).
4. **Run the full test suite.** Paste the output. No regressions allowed.
5. **If the fix touches more than 5 files,** flag the blast radius (in Hebrew):

   > התיקון נוגע ב-N קבצים. זה רדיוס פגיעה גדול לתיקון באג.
   >
   > א) להמשיך, שורש הבעיה באמת מתפרס על כל הקבצים האלה
   > ב) לפצל, לתקן עכשיו רק את החלק הקריטי ולדחות את השאר
   > ג) לחשוב מחדש, אולי יש גישה ממוקדת יותר

## Phase 5: Verification and Report

**Fresh verification:** Reproduce the original bug scenario and confirm it is
fixed. This is not optional. For web bugs, repeat the exact browser steps from
Phase 1 (navigate, click, fill) and confirm via `list_console_messages`,
`list_network_requests` and `take_screenshot` that the failure is gone.

Run the test suite and paste the output. Then present this report in the chat,
in Hebrew:

```
דוח דיבאג
════════════════════════════════════════
תסמין:          [מה המשתמש ראה]
שורש הבעיה:     [מה באמת היה שבור, ולמה]
התיקון:         [מה שונה, עם הפניות קובץ:שורה]
הוכחה:          [פלט טסטים או שחזור שמראה שהתיקון עובד]
טסט רגרסיה:     [קובץ:שורה של הטסט החדש]
קשור:           [באגים קודמים באותו אזור, הערות ארכיטקטורה]
סטטוס:          הושלם | הושלם עם הסתייגויות | תקוע
════════════════════════════════════════
```

## Important Rules

- **3+ failed fix attempts: STOP and question the architecture.** Wrong
  architecture, not failed hypothesis.
- **Never apply a fix you cannot verify.** If you cannot reproduce and confirm,
  do not ship it.
- **Never say "this should fix it."** Verify and prove it. Run the tests.
- **Fix touches more than 5 files: ask about blast radius** before proceeding.
- **Completion status meanings:**
  - הושלם: root cause found, fix applied, regression test written, all tests pass
  - הושלם עם הסתייגויות: fixed but cannot fully verify (intermittent bug, needs staging)
  - תקוע: root cause unclear after investigation, escalated to the user

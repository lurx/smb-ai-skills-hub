---
name: land-and-deploy
version: 2.0.0
description: |
  Land a pull request and deploy it to production: merge via the GitHub CLI, watch CI
  and the deploy workflow (gh run watch), then verify the live site actually works
  with HTTP checks plus a real browser pass (page load, console errors, screenshot
  evidence, key flows). Picks up where /ship left off, offers safe rollback guidance
  on failure, and never declares "deployed" without checking production. Use when
  asked to "merge", "land", "deploy", "merge and verify", "land it", "ship it to
  production", "תמזג את ה-PR", "תעשה מרג'", "תעלה לאוויר", "תעלה לפרודקשן",
  "תעשה דיפלוי".
---

# מיזוג, פריסה ואימות (Land and Deploy)

הסקיל ממזג PR מוכן, עוקב אחרי ה-CI ואחרי תהליך הפריסה, ואז בודק שהאתר החי באמת
עובד: בדיקת HTTP, טעינת העמוד בדפדפן אמיתי וגלוי לעין, שגיאות קונסול וצילום מסך
כהוכחה. אם משהו נשבר, מקבלים מסלול חזרה מסודר לגרסה הקודמת.
הכלל המרכזי: לא מכריזים "עלה לאוויר" בלי לבדוק את פרודקשן בפועל.

## דרישה מקדימה: חיבור דפדפן (חד-פעמי)

הסקיל משתמש בכלי דפדפן ששמם מתחיל ב-`mcp__chrome-devtools__` (למשל navigate_page, take_screenshot).
אם הכלים לא זמינים בסשן הנוכחי:

1. בדוק אם השרת רשום: `claude mcp get chrome-devtools`
2. אם לא רשום, הרץ:
   - Mac / Linux: `claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest`
   - Windows: `claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest`
3. אמור למשתמש לסגור ולפתוח מחדש את Claude Code, ואז לבקש שוב את הפעולה.

הדפדפן שנפתח גלוי לעין, והמשתמש רואה כל פעולה בזמן אמת. הוא משתמש בפרופיל נפרד מ-Chrome האישי.

## Arguments

- `/land-and-deploy` - auto-detect the PR from the current branch, no post-deploy URL
- `/land-and-deploy <url>` - auto-detect the PR, verify the deploy at this URL
- `/land-and-deploy #123` - specific PR number
- `/land-and-deploy #123 <url>` - specific PR plus verification URL

This is a mostly automated workflow. Do NOT ask for confirmation except at the
pre-merge readiness gate (Step 3) and on failures (CI red, merge conflict, deploy
failure, unhealthy production). Never stop to choose a merge method (auto-detect) or
for timeout warnings (warn and continue). Narrate each step to the user in Hebrew:
what just happened, what is happening now, what comes next. No silent gaps.

GitHub only: if the remote is GitLab or unknown, STOP and tell the user (in Hebrew) that
this skill supports GitHub; merge via the web UI and return with a URL for verification only.

## Step 1: Pre-flight

Tell the user: "מתחיל תהליך פריסה. קודם בודק שהכל מחובר ומאתר את ה-PR."

1. `gh auth status` - if not authenticated, STOP: "אני צריך גישה ל-GitHub CLI כדי למזג. הרץ `gh auth login` ואז בקש שוב."
2. Detect the base branch: `gh pr view --json baseRefName -q .baseRefName`, fallback
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, fallback
   `git symbolic-ref refs/remotes/origin/HEAD | sed 's|refs/remotes/origin/||'`, fallback `main`.
   Use the result everywhere the steps below say `<base>`.
3. If no PR number was given: `gh pr view --json number,state,title,url,mergeable,baseRefName,headRefName`
4. Report: "מצאתי PR ‎#NNN: '{title}' ({branch} אל {base})."
5. Validate state:
   - No PR: STOP. "אין PR לענף הזה. הרץ קודם `/ship` ליצירת PR, ואז נחזור לכאן."
   - `MERGED`: "ה-PR הזה כבר מוזג. אם רוצים רק לאמת את הפרודקשן, תן לי את כתובת האתר ואריץ בדיקת בריאות."
   - `CLOSED`: "ה-PR נסגר בלי מיזוג. פתח אותו מחדש ב-GitHub ונסה שוב."
   - `OPEN`: continue.

## Step 2: Pre-merge CI checks

Tell the user: "בודק סטטוס CI ומוכנות למיזוג."

```bash
gh pr checks --json name,state,status,conclusion
gh pr view --json mergeable -q .mergeable
```

- Any required check FAILING: STOP. "ה-CI נכשל. הבדיקות שנפלו: {list}. חייבים לתקן לפני פריסה, אני לא ממזג קוד שלא עבר CI."
- Checks PENDING: tell the user "ה-CI עדיין רץ, אני מחכה שיסתיים" and wait:
  `gh pr checks --watch --fail-fast` with a 15 minute timeout. On failure STOP with the
  failing checks. On timeout STOP: "ה-CI רץ כבר יותר מ-15 דקות, זה חריג. בדוק את לשונית Actions ב-GitHub."
- `mergeable` is `CONFLICTING`: STOP. "יש קונפליקטים מול {base}. פתור אותם, דחוף, והרץ שוב."

## Step 3: Pre-merge readiness gate (the last stop before an irreversible merge)

Tell the user: "ה-CI ירוק. עכשיו בדיקות מוכנות אחרונות לפני המיזוג: טסטים, תיאור ה-PR ותיעוד."

Collect evidence, classify each item as PASS, WARNING, or BLOCKER:

1. **Local tests (BLOCKER if failing).** Find the project's test command (CLAUDE.md,
   package.json scripts, Makefile). Run it and capture the exit code. No test command
   found: note as WARNING "לא נמצאו טסטים בפרויקט".
2. **PR body accuracy (WARNING).** Compare `gh pr view --json body -q .body` against
   `git log --oneline <base>..HEAD`. Flag significant commits that the description
   does not mention, or described work that was later reverted.
3. **Docs (WARNING).** `git diff --name-only <base>...HEAD -- README.md CHANGELOG.md VERSION`.
   If the branch adds features but none of these changed, warn. Docs-only branches skip this.

Present a readiness report in the chat, in Hebrew:

```
דוח מוכנות למיזוג
==================
PR: ‎#NNN, {title} ({branch} אל {base})
CI: עבר
טסטים מקומיים: עברו / נכשלו (חוסם) / לא נמצאו
תיאור ה-PR: מעודכן / לא משקף את השינויים (אזהרה)
תיעוד וגרסה: עודכנו / לא עודכנו (אזהרה)
אזהרות: N | חוסמים: N
```

Then ask (AskUserQuestion), because the merge cannot be undone without a revert:
- א) "למזג, הכל נראה טוב" (recommend when green)
- ב) "לעצור, אני רוצה לתקן את האזהרות קודם"
- ג) "למזג בכל זאת, אני מבין את האזהרות"

If BLOCKERS exist, recommend ב and explain each blocker in plain Hebrew. If the user
picks ב, STOP with concrete next steps. Otherwise say "ממזג עכשיו." and continue.

## Step 4: Merge

Record a start timestamp. Try auto-merge first (respects repo settings and merge queues):

```bash
gh pr merge --auto --delete-branch
```

If `--auto` is unavailable, merge directly: `gh pr merge --squash --delete-branch`.
On permission error STOP: "אין לי הרשאה למזג את ה-PR הזה. צריך maintainer, או לבדוק את חוקי ההגנה על הענף."

**Merge queue:** if after `--auto` the PR state is not immediately `MERGED`, tell the
user: "הריפו משתמש בתור מיזוג. GitHub מריץ CI פעם נוספת על קומיט המיזוג הסופי, אז נחכה." Poll
`gh pr view --json state -q .state` every 30 seconds, up to 30 minutes, with a Hebrew
progress line every 2 minutes. If the PR drops back to `OPEN`, STOP: "ה-PR הוצא מתור המיזוג, כנראה בדיקה נכשלה על קומיט המיזוג. בדוק בעמוד ה-merge queue."

Once merged, capture the merge commit SHA: `gh pr view --json mergeCommit -q .mergeCommit.oid`.

## Step 5: Deploy detection

Determine how this project deploys, in this order:

1. **Persisted config:** `grep -A 20 "## Deploy Configuration" CLAUDE.md` and parse
   platform, production URL, staging URL, custom health-check command. If found, use it.
2. **Platform config files:** `fly.toml` (Fly.io), `render.yaml` (Render), `vercel.json`
   or `.vercel/` (Vercel), `netlify.toml` (Netlify), `Procfile` (Heroku), `railway.json`/`railway.toml` (Railway).
3. **Deploy workflows:** `gh run list --branch <base> --limit 5 --json databaseId,name,status,conclusion,headSha,workflowName`
   and look for runs matching the merge SHA whose name contains deploy, release, production, or cd.

Classify the diff yourself from `git diff --name-only <base>~1...<base>` (or the PR
files): docs-only, config-only, backend-only, or frontend (any UI/template/CSS/JS files).

- **Docs-only:** nothing to deploy or verify. Tell the user "זה היה שינוי תיעוד בלבד, אין מה לפרוס או לאמת. סיימנו." and jump to Step 8.
- **No workflow and no URL known:** ask once, in Hebrew: is this a web app (give me the
  production URL) or a library/CLI (nothing to verify)? A URL passed as an argument always wins.
- **Staging or preview detected** (staging URL in CLAUDE.md, or a Vercel/Netlify preview
  in `gh pr checks --json name,targetUrl`): offer to verify staging first, then production. Same checks, run twice.

## Step 6: Wait for the deploy

- **GitHub Actions:** find the run for the merge SHA and watch it:
  `gh run watch <run-id> --exit-status` (or poll `gh run view <run-id> --json status,conclusion`
  every 30 seconds). Progress line in Hebrew every 2 minutes.
- **Fly.io:** `fly status --app <app>` - machines `started` with a fresh deploy timestamp.
- **Heroku:** `heroku releases --app <app> -n 1`.
- **Render:** poll `curl -sf <url> -o /dev/null -w "%{http_code}"` every 30 seconds (deploys take 2-5 minutes).
- **Vercel / Netlify:** auto-deploy on merge. Wait 60 seconds for propagation, then verify.
- **Custom command in CLAUDE.md:** run it and check the exit code.

If the deploy workflow FAILS, ask the user (Hebrew): א) אקרא את לוגי הפריסה ואבין מה קרה
(recommended, use the `investigate` skill), ב) לבצע rollback מיידי (Step 8), ג) להמשיך לבדיקת
בריאות בכל זאת, אולי זה צעד רעוע והאתר בסדר. If 20 minutes pass with no conclusion, warn and
ask whether to keep waiting or skip verification (the verdict is then "מוזג, לא אומת").

## Step 7: Production verification (never skip silently)

Tell the user: "הפריסה הסתיימה. עכשיו בודק את האתר החי: טעינה, שגיאות, וצילום מסך. הדפדפן ייפתח מול העיניים שלך ותראה כל פעולה."

Depth by diff scope: config-only = curl check only; backend-only = curl plus console
errors; frontend or mixed = the full sequence below.

**Full sequence:**

1. `curl -s -o /dev/null -w "%{http_code}" <url>` - expect 200 (2xx/3xx acceptable).
2. `mcp__chrome-devtools__navigate_page` to the URL. Use `mcp__chrome-devtools__wait_for`
   on a text or element that proves the real page rendered.
3. `mcp__chrome-devtools__list_console_messages` - flag `Uncaught`, `TypeError`,
   `ReferenceError`, `Failed to load`. Ignore plain warnings. Drill into a specific
   error with `mcp__chrome-devtools__get_console_message`.
4. `mcp__chrome-devtools__take_snapshot` - confirm real content, not a blank page or a
   generic error screen. If the change touched a key flow (form, button, checkout),
   exercise it: `click` / `fill` / `fill_form` by uid from the snapshot, then `wait_for`
   the success state. Check `mcp__chrome-devtools__list_network_requests` for failed calls.
5. `mcp__chrome-devtools__take_screenshot` - desktop evidence, show it to the user.
6. Frontend changes: `mcp__chrome-devtools__resize_page` to 390x844 and screenshot again (mobile).
7. If the user asked about performance:
   `performance_start_trace` / `performance_stop_trace` / `performance_analyze_insight`.

**Health verdict:** HEALTHY only if the page returns 2xx, renders real content, has no
critical console errors, and loads in under 10 seconds. If anything fails, show the
evidence (screenshot, errors) and ask in Hebrew: א) "זה צפוי, האתר עוד מתחמם, סמן כתקין",
ב) "זה שבור, בצע rollback" (recommend when the site is down), ג) "בוא נחקור עוד לפני שמחליטים".

## Step 8: Rollback (when chosen)

Tell the user: "מבצע rollback. זה יוצר קומיט חדש שמבטל את השינויים, והגרסה הקודמת תחזור ברגע שהפריסה שלו תסתיים."

```bash
git fetch origin <base>
git checkout <base> && git pull
git revert <merge-sha> --no-edit   # merge commit (not squash): add -m 1
git push origin <base>
```

- Revert conflicts: explain that later commits on `<base>` collide; the user resolves manually.
- Branch protection blocks the push: create a revert PR instead:
  `gh pr create --title "revert: <original PR title>"` and tell the user to merge it to roll back.
- After a successful revert, watch the redeploy (Step 6) and re-verify (Step 7) so the
  rollback itself is confirmed live. Verdict: REVERTED.

## Step 9: Deploy report

Present the final report in the chat, in Hebrew (no files):

```
דוח פריסה
==========
PR: ‎#NNN, {title} ({branch} אל {base})
מוזג: {timestamp} ({merge method}), SHA: {sha}
זמנים: המתנה ל-CI {X} | תור מיזוג {X} | פריסה {X} | אימות {X} | סה"כ {X}
פריסה: הצליחה / נכשלה / לא זוהה workflow
אימות פרודקשן: תקין / חלקי / דולג / בוצע rollback
  סטטוס HTTP: {code} | שגיאות קונסול: {N או "נקי"} | זמן טעינה: {X שניות}
  צילומי מסך: דסקטופ + מובייל (מוצגים למעלה)
פסיקה: נפרס ואומת / מוזג אך לא אומת / בוצע rollback
```

Closing line by verdict: "השינויים באוויר ואומתו. שיגור מוצלח." / "השינויים מוזגו אבל לא
הצלחתי לאמת את האתר, בדוק ידנית כשתוכל." / "בוצע rollback, ענף הפיצ'ר עדיין קיים לתיקון ושליחה מחדש."

## Rules

- **Never force push.** `gh pr merge` only.
- **Never skip CI.** Failing checks always stop the flow, with an explanation.
- **Never claim "deployed" without verifying production.** No curl and no browser check
  means the verdict is "מוזג, לא אומת", said explicitly.
- **Auto-detect everything** (PR, merge method, platform, staging). Ask only what truly cannot be inferred.
- **Poll politely:** 30-second intervals, sane timeouts (CI 15m, queue 30m, deploy 20m).
- **Revert is always on the menu** at every failure point, explained in plain Hebrew.
- **Single-pass verification** after deploy, and clean up the feature branch (`--delete-branch`).
- **First deploy of a project:** teacher mode, show the detected infrastructure and what
  will happen before merging. Repeat deploys: brief status lines, no re-explanations.

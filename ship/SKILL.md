---
name: ship
version: 2.0.0
description: |
  Full shipping workflow for a feature branch: detect the git platform and base
  branch, merge the base, run the test suite, self-review the diff with a
  structured checklist, bump the version, update the changelog, commit in
  bisectable chunks, push, open a PR with the gh or glab CLI, optionally merge,
  and end with a Hebrew summary report in the chat. Proactively invoke this
  skill (never push or open a PR directly) when the user says the code is ready.
  Use when asked to "ship", "deploy", "push to main", "create a PR", "merge and
  push", "get it deployed", "תעשה שיפ", "תעלה את הקוד לגיט", "פתח PR",
  "תמזג ל-main", "תדחוף את הקוד".
---

# Ship: שיגור קוד מסודר

הסקיל מריץ תהליך שיגור מלא לענף העבודה הנוכחי: מיזוג הענף הראשי, הרצת טסטים,
סקירת קוד עצמית על כל השינויים, עדכון גרסה ויומן שינויים, קומיטים מסודרים,
דחיפה ופתיחת Pull Request. בסוף מוצג דוח סיכום בעברית עם קישור ל-PR.

## Workflow rules

Non-interactive, automated workflow: the user said "ship", so run straight
through to the PR URL. Never ask trivial confirmations ("ready to push?").

**Stop only for:** being on the base branch (abort), merge conflicts that
cannot be auto-resolved, test failures caused by this branch, self-review
findings that need user judgment, MINOR or MAJOR version bumps.

**Never stop for:** uncommitted changes (always include them), MICRO or PATCH
bumps (auto-pick), CHANGELOG content (auto-generate), commit message approval.

**Re-run behavior:** re-running ship runs every verification step again
(tests, review, version check). Only actions are idempotent: skip the bump if
already bumped, skip the push if already pushed, update the PR body if one exists.

## Step 0: Detect platform and base branch

Detect the platform from `git remote get-url origin`: "github.com" means
**GitHub**, "gitlab" means **GitLab**. Otherwise: `gh auth status` succeeds
means GitHub, `glab auth status` succeeds means GitLab, neither means
**unknown** (git-native commands only).

Determine the base branch (the branch the PR targets, or the repo default):

- **GitHub:** `gh pr view --json baseRefName -q .baseRefName`, else
  `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`
- **GitLab:** `glab mr view -F json` (`target_branch`), else
  `glab repo view -F json` (`default_branch`)
- **Fallback:** `git symbolic-ref refs/remotes/origin/HEAD`, then `origin/main`, then `origin/master`, then `main`

Print the detected base branch. Substitute it wherever later steps say `<base>`.

## Step 1: Pre-flight

1. If on the base branch, **abort** and tell the user in Hebrew: "אתה על הענף
   הראשי. צריך לעבוד מענף פיצ'ר. ליצור ענף חדש מהשינויים הנוכחיים?"
2. Run `git status` (uncommitted changes are always included, never ask), then
   `git diff <base>...HEAD --stat` and `git log <base>..HEAD --oneline` to
   understand what is being shipped.

## Step 2: Merge the base branch (BEFORE tests)

```bash
git fetch origin <base> && git merge origin/<base> --no-edit
```

Tests must run against the merged state. Auto-resolve only trivial conflicts
(VERSION, CHANGELOG ordering, lockfiles). Complex conflicts: **STOP** and list
the conflicting files in Hebrew. Already up to date: continue silently.

## Step 3: Run tests (on merged code)

Find the test command: a `## Testing` section in the project's CLAUDE.md is
authoritative; otherwise auto-detect from `package.json` scripts.test, Gemfile
(`bin/rails test`/`rspec`), pytest.ini/pyproject.toml, go.mod, Cargo.toml.

- **No test framework found:** do not block. Note it and flag it in the PR body.
- **All tests pass:** note the counts briefly and continue.

**If any test fails, triage ownership before stopping.** Compare each failure
against `git diff origin/<base>...HEAD --name-only`:

- **In-branch** (the failing test or the code it covers changed on this
  branch): **STOP**, fix before shipping. Ambiguous: default to in-branch.
- **Pre-existing** (unrelated to any branch change): ask in Hebrew with
  AskUserQuestion:

> נמצאו טסטים שנכשלים, אבל הכשל קיים עוד מלפני הענף הזה: [רשימת כשלים, קובץ ושורה]
> א) לחקור ולתקן עכשיו (מומלץ, ההקשר טרי) ב) להוסיף ל-TODOS.md ולשגר ג) לדלג, מוכר לי

If the user picks a fix, commit it separately as
`fix: pre-existing test failure in <file>`.

## Step 4: Self code-review of the diff

Run `git diff origin/<base>` and read every changed file in full (not just the
hunks). Apply this checklist:

**Security and data safety (critical):**
- SQL built by string interpolation; secrets or API keys in the diff
- New endpoints missing auth checks; unvalidated user input (XSS, injection)
- Destructive migrations; UPDATE/DELETE without a WHERE clause

**Correctness:**
- Error handling that swallows failures; null/undefined/empty handling
- Both sides of every new conditional; races (double submit, two tabs)

**Tests:**
- Every new branch and error path has a test; note gaps for the PR body
- IRON RULE: if the diff broke behavior that used to work, write a regression
  test immediately, no asking. Commit as `test: regression test for <what>`

**Frontend (only if frontend files changed):**
- Fonts below 16px on mobile, removed focus outlines, `!important` hacks
- Broken responsive layout, RTL issues in Hebrew pages

**Scope (informational):** compare stated intent (commits, TODOS.md) against
the diff; flag "while I was in there" changes and unaddressed requirements.
**Cleanliness:** dead code, debug prints, stale comments.

For diffs of 200+ changed lines, additionally dispatch one fresh-context
subagent via the Agent tool to adversarially review the diff (think attacker
and chaos engineer: edge cases, race conditions, security holes, resource
leaks, silent data corruption; no compliments, just problems). Merge its findings.

**Every finding gets a confidence score (1-10).** Show 7+ normally, show 5-6
with the caveat "ייתכן שזו התרעת שווא, לוודא", suppress below 5 unless critical.

**Classify each finding as AUTO-FIX or ASK.** Mechanical fixes (dead code,
stale comment, missing escape) are AUTO-FIX: apply and output one line per
fix. Judgment calls are ASK: present all in one Hebrew AskUserQuestion,
numbered, with severity, problem, recommended fix, options "א) לתקן ב) לדלג".

**After any fixes:** commit them (`fix: self-review fixes`), **re-run Step 3
tests**, then summarize: `סקירה עצמית: N ממצאים, M תוקנו אוטומטית, K דולגו`.

## Step 5: Version bump (auto-decide)

Version source: a `VERSION` file in the repo root, else the `version` field in
`package.json`. Neither exists: skip with a note.

**Idempotency:** compare against `git show origin/<base>:VERSION`. If already
bumped on this branch, skip the bump but keep the value for later steps.

- **PATCH** (or the 4th digit in a 4-digit format): fixes, tweaks, config,
  fewer than 500 changed lines with no feature signals
- **MINOR: ask first** on feature signals (new routes/pages, migrations, new
  modules) or 500+ changed lines. Ask in Hebrew: "זוהו סימנים לפיצ'ר חדש.
  להעלות גרסת MINOR או להישאר על PATCH?"
- **MAJOR: always ask**, only for breaking changes or milestones. Bumping a
  digit resets everything to its right.

## Step 6: CHANGELOG (auto-generate)

1. Enumerate every commit: `git log <base>..HEAD --oneline`. This is a
   checklist, every commit must be represented in the entry.
2. Read the full diff, group by theme, and write one entry for the new version
   (`## [X.Y.Z] - YYYY-MM-DD`) with sections as applicable: `### Added`,
   `### Changed`, `### Fixed`, `### Removed`.
3. Voice: lead with what the user can now do. Plain language, no internals.
4. No CHANGELOG.md: create it with a minimal header. Never ask the user to
   describe the changes, infer everything from the diff.

**TODOS.md (if it exists):** move clearly-completed items to a `## Completed`
section with version and date. Conservative: only when the diff proves it.

## Step 7: Commit (bisectable chunks)

Group changes into logical commits, each one coherent unit:
1. Order: infrastructure (migrations, config, routes), then models/services,
   then controllers/views/components. Code and its test share a commit.
   VERSION + CHANGELOG + TODOS.md always go in the final commit.
2. Each commit independently valid (no broken imports, dependencies first),
   message format `<type>: <summary>` (feat/fix/chore/refactor/docs/test).
3. Small diffs (under 50 lines, fewer than 4 files): one commit is fine.

## Step 8: Verification gate

**IRON LAW: no completion claims without fresh verification evidence.**

If ANY code changed after Step 3's test run (review fixes, generated tests),
re-run the tests now and show fresh output. "Should work" is not evidence.
Run the build step if one exists. Anything fails: STOP, fix, return to Step 3.

## Step 9: Push

If `git rev-parse HEAD` equals `git rev-parse origin/<branch>`, skip.
Otherwise `git push -u origin <branch-name>`. Never force push.

## Step 10: Create or update the PR

Check for an open PR (`gh pr view --json url,state` / `glab mr view -F json`).
Exists: regenerate the body from this run's fresh results and update it
(`gh pr edit --body` / `glab mr update -d`). Otherwise create:

```bash
gh pr create --base <base> --title "<type>: <summary>" --body "..."
```

(GitLab: `glab mr create -b <base> -t "..." -d "..."`. Neither CLI: print the
branch and remote URL, explain in Hebrew how to open the PR manually, continue.)

PR body template (in Hebrew, the team reads it):

```
## סיכום
<כל השינויים מקובצים לפי נושא. כל קומיט מופיע לפחות בסעיף אחד.>
## טסטים
<כמה עברו, מה נוצר חדש, אילו פערי כיסוי נשארו>
## סקירה עצמית
<מה נמצא, מה תוקן, מה דולג ולמה>
## גרסה
<גרסה קודמת ל-גרסה חדשה>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Insert a blank line between sections in the real PR body. Output the PR URL.

## Step 11: Merge (only if explicitly requested)

Only if the user asked to merge ("merge and push", "תמזג", "עד הסוף"):
`gh pr merge --squash --delete-branch` (GitLab: `glab mr merge --squash
--remove-source-branch`). CI checks still running: use `--auto` and say so.
Otherwise finish at the PR and do not merge.

## דוח סיכום בצ'אט

Always end by presenting this report in the conversation, in Hebrew:

```
========== דוח שיגור ==========
ענף: {branch} אל {base}
טסטים: {N} עברו{, פרטים על כשלים שטופלו}
סקירה עצמית: {N} ממצאים, {M} תוקנו, {K} דולגו
גרסה: {ישנה} ל-{חדשה}
קומיטים: {רשימה קצרה}
PR: {URL} {אם מוזג: מוזג ל-{base} ונמחק הענף}
==============================
```

## Important rules

- **Never skip tests** (in-branch failures always stop the ship), **never
  force push, never push without fresh verification evidence.**
- **Split commits for bisectability**, each commit is one logical change.
- The goal: the user says "ship", and the next thing they see is the review
  summary and the PR URL.

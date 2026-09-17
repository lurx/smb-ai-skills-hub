# Shared Audit Process (Ads Skill Family)

Canonical process, grading, and output conventions shared by all `ads-*` skills.
Installed to `ads/references/audit-process.md` in the user's business folder.

## Process

1. **Collect data**: request exports, screenshots, API/MCP access, or pasted metrics for the platform(s) in scope. If no exports are available, audit from screenshots or manual data entry.
2. **Validate**: confirm data is present and covers a sufficient window before proceeding (default: ≥30 days; skill may specify otherwise).
3. **Read references**: load the platform-specific audit checklist, `ads/references/benchmarks.md`, and `ads/references/scoring-system.md` (plus any references the skill names).
4. **Evaluate**: grade every applicable check as **PASS**, **WARNING**, or **FAIL**. Skip checks that don't apply (note why).
5. **Validate**: confirm all applicable checks were evaluated before scoring.
6. **Score**: calculate the platform Health Score (0-100) using the category weights defined in the skill.
7. **Report**: generate a findings report with a prioritized action plan and Quick Wins.

## Grading Scale

```
Grade: A (90-100), B (75-89), C (60-74), D (40-59), F (<40)
```

## Health Score Output Format

Render category scores as ASCII bars (one filled block per 10 points), with weights:

```
<Platform> Ads Health Score: XX/100 (Grade: X)

Category One:   XX/100  ████████░░  (30%)
Category Two:   XX/100  ██████████  (25%)
Category Three: XX/100  ███████░░░  (25%)
Category Four:  XX/100  █████░░░░░  (20%)
```

## Priority Definitions

- **Critical**: Revenue/data loss risk (fix immediately)
- **High**: Significant performance drag (fix within 7 days)
- **Medium**: Optimization opportunity (fix within 30 days)
- **Low**: Best practice, minor impact (backlog)

## Quick Wins Criteria

```
IF severity == "Critical" OR severity == "High"
AND estimated_fix_time < 15 minutes
THEN flag as Quick Win
SORT BY (severity_multiplier x estimated_impact) DESC
```

Every report ends with a "Quick Wins sorted by impact" section using these criteria.

## Output File Conventions

- Reports are Markdown files named `<PLATFORM>-ADS-REPORT.md` (e.g. `META-ADS-REPORT.md`), or the specific names a skill defines.
- Each report includes: health score with grade, per-category breakdown with pass/warning/fail per check, detailed findings with remediation steps, and Quick Wins.
- Action plans order recommendations Critical > High > Medium > Low.

---
name: ads-audit
description: "Full multi-platform paid advertising audit. Analyzes Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, and Microsoft Ads accounts. Generates health score per platform and aggregate score. Use when user says audit, full ad check, analyze my ads, account health check, or PPC audit."
---

# Full Multi-Platform Ads Audit

Read `ads/references/audit-process.md` for the shared process, PASS/WARNING/FAIL grading, health-score format, priority definitions, Quick Wins criteria, and output conventions.

## Process (audit-specific)

1. **Validate**: confirm at least one platform's data is available before proceeding
2. **Detect business type** from account signals (products, funnel, average order value, B2B/B2C)
3. **Identify active platforms**: determine which platforms are in use
4. **Run each active platform's audit sequentially**, applying the corresponding sibling skill's logic yourself (ads-google, ads-meta, ads-linkedin, ads-tiktok, ads-microsoft): evaluate that platform's checks, thresholds, and category weights inline
5. **Validate**: verify each platform audit produced a valid score with required fields before aggregating
6. **Score**: calculate per-platform and aggregate Ads Health Score (0-100)
7. **Report**: generate prioritized action plan with Quick Wins

## Data Collection

Ask the user for available data. Accept any combination:
- Google Ads: account export, Change History, Search Terms Report
- Meta Ads: Ads Manager export, Events Manager screenshot, EMQ scores
- LinkedIn Ads: Campaign Manager export, Insight Tag status
- TikTok Ads: Ads Manager export, Pixel/Events API status
- Microsoft Ads: account export, UET tag status, import validation results

If no exports available, audit from screenshots or manual data entry.

## Scoring

Read `ads/references/scoring-system.md` for full algorithm.

### Per-Platform Weights

| Platform | Category Weights |
|----------|-----------------|
| Google | Conversion 25%, Waste 20%, Structure 15%, Keywords 15%, Ads 15%, Settings 10% |
| Meta | Pixel/CAPI 30%, Creative 30%, Structure 20%, Audience 20% |
| LinkedIn | Tech 25%, Audience 25%, Creative 20%, Lead Gen 15%, Budget 15% |
| TikTok | Creative 30%, Tech 25%, Bidding 20%, Structure 15%, Performance 10% |
| Microsoft | Tech 25%, Syndication 20%, Structure 20%, Creative 20%, Settings 15% |

### Aggregate Score

```
Aggregate = Sum(Platform_Score x Platform_Budget_Share)
```

Grades per the shared scale in `ads/references/audit-process.md`.

## Output Files

- `ADS-AUDIT-REPORT.md`: Comprehensive multi-platform findings
- `ADS-ACTION-PLAN.md`: Prioritized recommendations (Critical > High > Medium > Low)
- `ADS-QUICK-WINS.md`: Items fixable in <15 minutes with high impact

## Report Structure

### Executive Summary
- Aggregate Ads Health Score (0-100) with grade
- Per-platform scores
- Business type detected
- Active platforms identified
- Top 5 critical issues across all platforms
- Top 5 quick wins across all platforms

### Per-Platform Sections
Each platform section includes:
- Platform Health Score with grade
- Category breakdown with pass/warning/fail per check
- Platform-specific Quick Wins
- Detailed findings with remediation steps

### Cross-Platform Analysis
- Budget allocation assessment (actual vs recommended)
- Tracking consistency (are all platforms tracking the same events?)
- Creative consistency (is messaging aligned across platforms?)
- Attribution overlap (are platforms double-counting conversions?)

### Strategic Recommendations
- Platform prioritization based on business type
- Budget reallocation recommendations
- Scaling opportunities (platforms/campaigns ready to scale)
- Kill list (campaigns/ad groups to pause immediately)

Priority definitions and Quick Wins criteria: see `ads/references/audit-process.md`.

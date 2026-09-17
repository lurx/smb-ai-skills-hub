---
name: ads-meta
description: "Meta Ads deep analysis covering Facebook and Instagram advertising. Evaluates 50 checks across Pixel/CAPI health, creative diversity and fatigue, account structure, and audience targeting. Includes Advantage+ assessment. Use when user says Meta Ads, Facebook Ads, Instagram Ads, Advantage+, or Meta campaign."
---

# Meta Ads Deep Analysis

## Andromeda AI Engine

Meta's Andromeda AI engine (Oct 2025) filters ads using 10,000x more complex models.
Creative diversity is now the #1 performance lever. Ads with Similarity Score >60%
get retrieval suppression. The algorithm clusters near-identical creatives and limits
their delivery. 100 minor variations perform no better than 10. Prioritize genuinely
distinct concepts, angles, and formats over volume of similar variants.

## Process

Follow the shared audit process in `ads/references/audit-process.md` (grading, health score, Quick Wins, output format).
Data to collect: Ads Manager export, Events Manager screenshot, EMQ scores.
Platform references: `ads/references/meta-audit.md` (full 50-check audit).

## What to Analyze

### Pixel / CAPI Health (30% weight)
- Meta Pixel installed and firing on all pages
- Conversions API (CAPI) active (30-40% data loss without it post-iOS 14.5)
- Event deduplication configured (event_id matching, ≥90% dedup rate)
- Event Match Quality (EMQ) ≥8.0 for Purchase event
- All standard events configured (ViewContent, AddToCart, Purchase, Lead)
- Custom conversions created for non-standard events
- Aggregated Event Measurement (AEM) configured for iOS
- Domain verification completed
- Server-side events include customer_information parameters
- Pixel fires with correct currency and value parameters

### Creative (30% weight)
- ≥3 creative formats active (image, video, carousel, collection)
- ≥5 creatives per ad set (Meta recommendation)
- Creative fatigue detection: CTR drop >20% over 14 days = FAIL
- Video creative: 15s max for Stories/Reels, 30s max for Feed
- UGC/testimonial creative tested
- Dynamic Creative Optimization (DCO) tested
- Ad copy: headline under 40 chars, primary text under 125 chars
- Creative refresh cadence: every 2-4 weeks for high-spend

### Account Structure (20% weight)
- Campaign Budget Optimization (CBO) vs Ad Set Budget (ABO) intentional
- Campaign consolidation: 1-3 campaigns total recommended
- Learning phase health: <30% ad sets in "Learning Limited" (FAIL >50%)
- Budget per ad set: ≥5x target CPA (minimum for learning phase exit)
- Ad set audience overlap <30% (Audience Overlap tool)
- Campaign naming conventions consistent and descriptive
- Advantage+ Sales Campaigns active for e-commerce
- Simplified campaign structure: 1-3 campaigns total (fewer, larger ad sets preferred)

### Audience & Targeting (20% weight)
- Prospecting frequency (7-day): <3.0 (WARNING 3-5, FAIL >5)
- Retargeting frequency (7-day): <8.0 (WARNING 8-12, FAIL >12)
- Custom Audiences: website visitors, customer lists, engagement
- Lookalike Audiences: multiple seed sizes tested (1%, 3%, 5%)
- Advantage+ Audience tested vs manual targeting
- Interest targeting: broad enough for algorithm optimization
- Exclusions: purchasers excluded from prospecting, overlap managed
- Location targeting reviewed for relevance

## Advantage+ Assessment

If Advantage+ features are in use:
- **Advantage+ Sales Campaigns**: catalog connected, existing customer cap set
- **Advantage+ Audience**: performance vs manual audience compared
- **Advantage+ Creative**: enhancements enabled (text, brightness, music)
- **Advantage+ Placements**: enabled (let Meta optimize placement mix)
- **Budget allocation**: Advantage+ campaigns getting fair test budget

## Special Ad Categories

If ads are in restricted categories:
- Special Ad Category declared before campaign creation
- Targeting restrictions verified (no ZIP, age 18-65+ only, no Lookalike)
- Creative compliance with category-specific policies
- Read `ads/references/compliance.md` for full requirements

## EMQ Optimization Guide

| EMQ Score | Status | Action |
|-----------|--------|--------|
| 8.0-10.0 | Excellent | Maintain current setup |
| 6.0-7.9 | Good | Add more customer_information parameters |
| 4.0-5.9 | Fair | Implement CAPI, improve data quality |
| <4.0 | Poor | Critical: CAPI + Enhanced Matching required |

Key parameters to maximize EMQ:
- `em` (email): highest match rate signal
- `ph` (phone): second highest match signal
- `fn`, `ln` (first/last name): improves match accuracy
- `ct`, `st`, `zp` (city, state, zip): geographic matching
- `external_id`: CRM/user ID for cross-device matching

## Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| EMQ (Purchase) | ≥8.0 | 6.0-7.9 | <6.0 |
| Dedup rate | ≥90% | 70-90% | <70% |
| CTR | ≥1.0% | 0.5-1.0% | <0.5% |
| Creative formats | ≥3 | 2 | 1 |
| Creatives per ad set | ≥5 | 3-4 | <3 |
| Learning Limited | <30% | 30-50% | >50% |
| Budget per ad set | ≥5x CPA | 2-5x CPA | <2x CPA |

## Output

Render the Meta Ads Health Score using the shared bar format in `ads/references/audit-process.md` with categories: Pixel/CAPI Health (30%), Creative (30%), Account Structure (20%), Audience (20%).

### Deliverables
- `META-ADS-REPORT.md`: Full 50-check findings with pass/warning/fail
- EMQ improvement roadmap
- Creative fatigue alerts (any creative with CTR declining >20%)
- Advantage+ adoption recommendations

## Threads Placement

Threads placement GA Jan 2026, 400M+ MAU. Lower CPMs than Feed/Stories.
Currently ~0.04% of total spend. Emerging channel. Evaluate:
- Is Threads placement enabled in Advantage+ Placements?
- Monitor CPM and engagement vs other placements
- Early-mover advantage for brands with active Threads presence

---
name: israeli-social-content
description: Localize approved social content for Israeli audiences using spoken Hebrew, RTL-safe formatting, cultural timing awareness, and account evidence instead of posting folklore. Use for לוקליזציה, התאמה לקהל ישראלי, עברית מדוברת, RTL fixes, mixed Hebrew/English copy, or checking culturally sensitive dates.
license: MIT
---

# Israeli Social Content Locale Layer

## Overview

Localize strategy and copy for Israeli audiences on behalf of [שם העסק]. This
skill does not choose topics, invent platform strategy, or schedule posts. It
converts approved content into natural Hebrew and flags local calendar, RTL,
and cultural risks.

Adapted from dangogit/content-skills (MIT — see LICENSE).

## When to Use

- Rewrite approved copy into spoken Israeli Hebrew.
- Review mixed Hebrew, English, emoji, numbers, mentions, and hashtags.
- Check culturally sensitive dates or local context.
- Adapt one approved idea across Israeli-facing networks.

## Prerequisites

- Approved idea, story role, and proof.
- The business CLAUDE.md (audience, brand positioning). If `writing-style` is
  installed, its voice profile governs phrasing.
- Current official platform documentation for limits, labels, and formats
  (claims expire — see `references/evidence.json` for dated claims).

## Workflow

### Step 1: Preserve Message

Keep original claim, proof, and promise. Do not add Israeli stereotypes,
invented slang, unsupported statistics, or generic local references.

### Step 2: Rewrite In The Business Voice

- Spoken, direct, second-person Hebrew.
- Prefer phrases the business actually uses (writing-style corpus, past posts).
- Start from lived pain before tool name.
- Reject translated slogan symmetry and invented framework names.
- Keep technical English only when needed.
- Isolate short Latin tokens on their own line or bidi-safe element.
- No inline `AI` in Hebrew. No em dashes.

### Step 3: Validate RTL

- Start each Hebrew line with a Hebrew character.
- Put Latin hashtags and mentions on separate final lines.
- Use `<bdi dir="ltr">` in HTML for code and commands.
- Use directional marks only when the target surface supports them reliably.
- Test in the actual composer or final rendered pixels before publishing.

### Step 4: Check Cultural Timing

- Block insensitive commercial content on Yom Kippur and Yom HaZikaron unless
  the user explicitly chooses another treatment.
- Check current Hebrew-calendar dates from a live source.
- Treat Shabbat, holidays, August, and election periods as hypotheses, not
  universal engagement laws.
- Use the account's own performance history for timing, when available.

### Step 5: Adapt Platform Surface

- Adapt only networks the user requested for this asset.
- Preserve one core promise while adapting title, caption, and media needs.
- Do not hardcode posting frequency, best time, ideal length, hashtag count,
  or network mix.
- Do not claim Hebrew always outperforms English without account evidence.

### Step 6: Check AI Disclosure

- TikTok requires labeling realistic AI-generated media; Meta requires
  disclosure for photorealistic generated video/audio.
- Verify current official policy before production handoff.
- Do not claim compliant labels automatically reduce reach.

Run the mechanical copy gate before handoff:

```bash
python scripts/check_hebrew_copy.py <copy.md>
```

It catches em dashes, generic share CTAs, and inline `AI` mixed into Hebrew.
It does not replace a native-speaker read, rendered RTL inspection, or live
platform-policy verification.

## Output Format

```markdown
# Israeli Localization Review

Localized copy:
Voice check:
RTL risks:
Latin-token treatment:
Calendar risks:
Platform checks requiring live verification:
Unsupported claims removed:
```

## Resources

- `references/locale-checklist.md` — concise localization and policy checklist.
- `references/israeli-social-platforms.md` — directional audience context with
  methodology caveats.
- `references/evidence.json` — dated claim registry with confidence and expiry.

## Related Skills

- `writing-style` — the business voice profile (use when installed).
- `carousel` — carousel production; run this skill as its copy gate.

## Key Principles

1. Locale layer does not replace editorial strategy.
2. The business's spoken phrasing beats generic Israeli slang.
3. RTL correctness is a production requirement.
4. Account evidence beats hardcoded timing.
5. Platform policy claims expire and require verification.

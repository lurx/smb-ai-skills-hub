---
standard: mcp-integration
version: 1.1.0
נבדק: 2026-09
עדכון-הבא: 2026-12
---
> קובץ זה מתעדכן מרכזית על ידי ה-Skills Hub. אל תערכו אותו — שינויים יידרסו בעדכון הבא.
> העדפות ומספרים אישיים שייכים ל-benchmarks.md.

# חיבורי MCP לנתוני פלטפורמות

## מפת כיסוי

| פלטפורמה | שרת MCP | סטטוס |
|---|---|---|
| Google Ads + GA4 | adloop | נתמך |
| Meta (Facebook/Instagram) | meta-ads-mcp | נתמך |
| TikTok | — | ללא MCP; ייצוא CSV |
| LinkedIn | — | ללא MCP; ייצוא CSV |
| Microsoft | — | ללא MCP; ייצוא CSV |

## adloop (Google Ads + GA4)

| שדה | ערך (2026-09) |
|---|---|
| Repo | github.com/kLOsk/adloop — פעיל, ~260 stars, MIT |
| התקנה | `pip install adloop` ואז `adloop init` (Python 3.11+); או clone + `uv sync && uv run adloop init` |
| אימות | OAuth 2.0 עם Google Cloud project של המשתמש + Google Ads developer token; אשף init כולל flow ל-headless |
| כיסוי | Google Ads (קריאה+כתיבה עם guardrails), GA4, Search Console, GTM |

### כלים עיקריים

| קטגוריה | כלים |
|---|---|
| אבחון | `health_check` |
| GA4 | `get_account_summaries`, `run_ga4_report`, `run_realtime_report`, `get_tracking_events` |
| Ads | `get_campaign_performance`, `get_keyword_performance`, `get_search_terms`, `draft_campaign`, `confirm_and_apply` |
| GTM | `audit_event_coverage`, `list_gtm_tags`, `list_gtm_triggers` |
| Cross-reference | `analyze_campaign_conversions`, `landing_page_analysis`, `attribution_check` |
| תכנון | `discover_keywords`, `estimate_budget` |

- סה"כ ~67 כלים; פעולות כתיבה עוברות preview-before-apply (`draft_campaign` → `confirm_and_apply`).

## meta-ads-mcp (Meta)

| שדה | ערך (2026-09) |
|---|---|
| Repo | github.com/pipeboard-co/meta-ads-mcp — פעיל, ~1.2k stars, PyPI: `meta-ads-mcp` |
| אימות (בקטלוג) | התקנה מקומית עם Meta Developer App + System User Token (המסלול המומלץ ב-repo הוא Pipeboard-hosted עם API token — הקטלוג משתמש במסלול המקומי) |
| כיסוי | ~42 כלים לניהול קמפיינים, קריאייטיבים, targeting ו-insights |

### כלים עיקריים

| קטגוריה | כלים |
|---|---|
| קריאה | `mcp_meta_ads_get_campaigns`, `mcp_meta_ads_get_insights`, `mcp_meta_ads_search_interests` |
| כתיבה | `mcp_meta_ads_create_campaign`, `mcp_meta_ads_upload_ad_image` |

## ravmesser-mcp (רב מסר — דיוור)

| שדה | ערך (2026-09) |
|---|---|
| מקור | fork מ-yahav123147/ravmesser-mcp, vendored במונורפו (`ravmesser-mcp/`) עם תמיכת credential store חוצת-פלטפורמות |
| נבדק | 2026-09-07: 923 שורות TS, תלות רק ב-MCP SDK + zod, יעד רשת יחיד — api.responder.co.il. אין telemetry |
| אימות | 2 זוגות key/secret (c/u) מהתמיכה של רב מסר (03-717-7777); נשמרים ב-credential store של מערכת ההפעלה תחת service ‏"golem" (accounts: ‎responder-c-key/-c-secret/-u-key/-u-secret), עם fallback למשתני סביבה |
| כיסוי | 22 כלים: רשימות, מנויים, הודעות, שדות אישיים, תצוגות |

### כללי בטיחות (מחייבים כל מיומנות שמשתמשת בשרת)

- `send_message` שולח **לכל הרשימה מיד, בלי אישור בצד השרת** — שער האישור חייב
  לחיות במיומנות: יצירה → `test_message` לכתובת של בעל העסק → אישור מפורש עם
  גודל הרשימה → שליחה.
- הלקוח מבצע retry אחד על שגיאת רשת. אחרי כשל ב-`send_message` — לוודא סטטוס
  לפני ניסיון חוזר (`get_messages`), לעולם לא לשלוח שוב בעיוורון (סכנת דיוור כפול).

## Fallback — פלטפורמות ללא MCP (TikTok / LinkedIn / Microsoft)

| פלטפורמה | ייצוא | עמודות מפתח |
|---|---|---|
| TikTok Ads Manager | Reports → Export CSV (רמת campaign/ad group/ad) | Cost, Impressions, Clicks, CTR, CPC, Conversions, CPA, ROAS (Complete Payment) |
| LinkedIn Campaign Manager | Export → CSV (Performance report) | Spend, Impressions, Clicks, Conversions, Leads, CPL |
| Microsoft Advertising | Reports → Download CSV | Spend, Impr., Clicks, Conv., CPA; שמות עמודות זהים כמעט ל-Google |

### עובדות פירוש CSV

| עובדה | ערך |
|---|---|
| מטבע | הקובץ במטבע החשבון; TikTok לעיתים כולל שורת סיכום שיש להסיר |
| תאריכים | LinkedIn מייצא טווח מצטבר אלא אם נבחר daily breakdown |
| conversions ב-TikTok | לפי חלון הייחוס שהוגדר בחשבון — לא ניתן לשחזר חלון אחר מה-CSV |
| שורות 0-impressions | Microsoft כולל ברירת מחדל; לסנן |

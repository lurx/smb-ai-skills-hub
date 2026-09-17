---
standard: gaql-notes
version: 1.0.0
נבדק: 2026-09
עדכון-הבא: 2026-12
---
> קובץ זה מתעדכן מרכזית על ידי ה-Skills Hub. אל תערכו אותו — שינויים יידרסו בעדכון הבא.
> העדפות ומספרים אישיים שייכים ל-benchmarks.md.

# Google Ads API — גרסאות ומגבלות GAQL

## גרסאות API (2026-09)

| גרסה | סטטוס | Sunset |
|---|---|---|
| v25 | האחרונה | — |
| v24 | נתמכת | לא פורסם (לא אומת) |
| v23 | נתמכת | לא פורסם (לא אומת) |
| v22 | הוסרה | 2026-10 (לפי לוח הפרסומים; לוודא מול developers.google.com/google-ads/api/docs/sunset-dates) |
| v21 | הוסרה | 2026-08-05 |
| v20 | הוסרה | 2026-06 |

- מ-2026 גוגל עברה למחזור שחרורים תכוף יותר; אורך חיי גרסה ~שנה. לבדוק sunset-dates לפני כל אינטגרציה.

## חוקי בסיס ב-GAQL

| חוק | פירוט |
|---|---|
| metrics דורשים טווח תאריכים | כל שאילתה עם metrics חייבת `segments.date DURING ...` או `BETWEEN` — אחרת שגיאה |
| שדה ב-WHERE חייב להיות selectable מה-resource | אי אפשר לסנן על שדה שאינו תואם ל-FROM |
| אין JOIN | קשרים דרך resource יחיד + attributed resources בלבד |
| segments מפצלים שורות | כל segment שנוסף ל-SELECT מכפיל שורות — לסכם אחרי, לא לפני |

## אי-תאימויות ידועות (שדות שלא חיים יחד)

| שילוב | תוצאה |
|---|---|
| `metrics.search_impression_share` + `segments.hour` | נדחה — share metrics לא נתמכים בפילוח שעתי |
| share metrics (`search_*_share`) + רוב ה-segments הגרנולריים | נדחה; לשאול ללא segment או לפי date בלבד |
| `segments.keyword` על resources שאינם keyword-scoped | נדחה |
| `bidding_strategy` ב-FROM + חלק מה-metrics/segments | נדחה — portfolio strategies חשופים רק דרך `bidding_strategy`, לא דרך `campaign` |
| `segments.conversion_action` + metrics שאינם conversion metrics | מחזיר 0/שגיאה — לפצל לשתי שאילתות |
| `metrics.absolute_top_impression_percentage` + `segments.click_type` | נדחה (לא אומת בגרסה נוכחית) |

## Gotchas נפוצים

| נושא | כלל |
|---|---|
| דדופליקציה של keywords | לפי `(ad_group_id + keyword_text + match_type)` לפני כל ניתוח |
| סטטוסים | לנתח רק ENABLED (קמפיין + ad group); לסנן PAUSED/REMOVED ב-WHERE, לא אחרי |
| `search_term_view` | מכיל רק terms מעל סף פרטיות; הסכום לא ישתווה ל-campaign totals |
| legacy BMM | BROAD + Manual CPC = ככל הנראה BMM ישן, לא broad מכוון |
| wasted spend | לסמן רק terms עם spend > $10 וגם 0 המרות |
| negatives | לספור shared negative lists יחד עם campaign-level negatives |
| `metrics.conversions` vs `metrics.all_conversions` | conversions = רק primary actions הנכללים ב-"Conversions"; all_conversions כולל הכל |
| PMax | אין search terms מלאים; להשתמש ב-`campaign_search_term_insight` (מוגבל) |
| micros | כל שדות הכסף ב-micros (חלוקה ב-1,000,000) |
| zero-impression rows | ברירת מחדל מוחזרות; לסנן `metrics.impressions > 0` כשרלוונטי |

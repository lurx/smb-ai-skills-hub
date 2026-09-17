---
standard: conversion-tracking
version: 1.0.0
נבדק: 2026-09
עדכון-הבא: 2027-03
---
> קובץ זה מתעדכן מרכזית על ידי ה-Skills Hub. אל תערכו אותו — שינויים יידרסו בעדכון הבא.
> העדפות ומספרים אישיים שייכים ל-benchmarks.md.

# מעקב המרות — רכיבים נדרשים לפי פלטפורמה

## Meta

| רכיב | סטטוס נדרש |
|---|---|
| Pixel | מותקן בכל העמודים, standard events (ViewContent, AddToCart, InitiateCheckout, Purchase, Lead) |
| Conversions API (CAPI) | פעיל, browser+server עם `event_id` זהה לדדופליקציה |
| Event Match Quality (EMQ) | יעד ≥8.8 ל-Purchase; שדות: hashed email (החשוב ביותר), hashed phone, fbc, fbp, client_ip, user_agent |
| Domain verification | דומיין מאומת + 8 אירועים מוגדרים (Aggregated Event Measurement) |
| Consent | אין ירי CAPI ללא הסכמה (פסיקה גרמנית 2026 — סטנדרט משפטי ב-EEA) |

### חלונות ייחוס Meta (2026)

| הגדרה | ערך |
|---|---|
| ברירת מחדל | 7-day click + 1-day view |
| אפשרויות click | 1 / 7 ימים |
| view | 1 יום בלבד (חלונות view ארוכים הוסרו מה-Insights API בינואר 2026; 28-day view לא קיים) |
| Engage-through | קטגוריה נפרדת מ-2026-03: אינטראקציות חברתיות = חלון 1 יום, לא נספרות כ-click |

## Google Ads

| רכיב | סטטוס נדרש |
|---|---|
| Google tag (gtag/GTM) | בכל העמודים |
| Conversion actions | primary/secondary מוגדרים נכון; ללא כפילות (gtag + GA4 import לאותה המרה) |
| Enhanced Conversions | פעיל (hashed email/phone) — לאתר ולידים |
| Consent Mode v2 | חובה ב-EEA (ad_storage, ad_user_data, ad_personalization); אכיפה מלאה מ-2026-06 |
| GA4 link | מקושר, אך לא לייבא המרות כפולות |
| Offline Conversion Import / GCLID | לעסקי לידים עם מכירה offline |

### ייחוס Google

| הגדרה | ערך |
|---|---|
| מודל ברירת מחדל | Data-driven attribution (DDA) לכל conversion action חדש |
| מודלים זמינים | DDA, Last click בלבד (מודלים ישנים הוסרו 2023) |
| חלון click | ברירת מחדל 30 יום; ניתן 1–90 יום |
| חלון view (engaged-view לוידאו) | ברירת מחדל 3 ימים |

## TikTok

| רכיב | סטטוס נדרש |
|---|---|
| TikTok Pixel | בכל העמודים, standard events |
| Events API | פעיל עם ttclid passback + דדופליקציה מול pixel |
| Events API Gateway | אופציה server-side מנוהלת — לשקול בהיקפים גדולים |
| Advanced Matching | hashed email/phone |

### ייחוס TikTok

| הגדרה | ערך |
|---|---|
| ברירת מחדל | 7-day click + 1-day view |
| אפשרויות click | 1 / 7 / 14 / 28 ימים (Attribution Manager, גם ברמת ad group) |
| אפשרויות view | off / 1 / 7 ימים |

## LinkedIn

| רכיב | סטטוס נדרש |
|---|---|
| Insight Tag | בכל העמודים |
| Conversions API (CAPI) | פעיל — קריטי מאז דעיכת third-party cookies |
| Conversion rules | מבוססי אירוע (מועדף) או URL |
| Enhanced matching | email ב-payload |

### ייחוס LinkedIn

| הגדרה | ערך |
|---|---|
| ברירת מחדל | 30-day click + 7-day view |
| אפשרויות | click: 1/7/30/90; view: 1/7/30 (לא אומת מלא) |

## Microsoft Advertising

| רכיב | סטטוס נדרש |
|---|---|
| UET tag | בכל העמודים |
| Conversion goals | מוגדרים עם revenue אם רלוונטי |
| Enhanced Conversions | פעיל (hashed email/phone) |
| Consent Mode | תומך באותות consent בסגנון Google ב-EEA |

### ייחוס Microsoft

| הגדרה | ערך |
|---|---|
| חלון click ברירת מחדל | 30 יום (ניתן 1–90) |
| view-through | 1 יום ברירת מחדל ל-Audience Ads (לא אומת) |

## מה נחשב "סטאפ בריא" (כל פלטפורמה)

| קריטריון | ערך |
|---|---|
| כיסוי dual-channel | browser pixel + server-side API עם דדופליקציה תקינה |
| PII | תמיד SHA-256, לעולם לא raw |
| consent gating | חוסם גם pixel וגם server-side, מתעדכן mid-session |
| בדיקת כפילויות | conversion אחד = מקור אמת אחד |
| טריות | אירועים מגיעים תוך <24 שעות; אין gap בין platform ל-analytics מעל ~20% ללא הסבר |

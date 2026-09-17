# LinkedIn Ads — רשימת ביקורת מלאה (27 בדיקות)

**מטרה:** מסמך ייחוס מלא לביקורת חשבון LinkedIn Ads עבור B2B — כל בדיקה עם מיקום, ספים ותיקון.
**גרסה:** 1.0 | **נבדק:** 2026-09
**הערה:** מסמך זה מתמקד במתודולוגיה יציבה (evergreen). מספרי מפרט ופורמטים משתנים — ראו `standards/platform-specs.md`. תהליך הדירוג, ה-Health Score ו-Quick Wins מוגדרים ב-`ads/references/audit-process.md` — לא חוזרים עליהם כאן.

**מינוח (מאז Oct 2025):** Campaign Group → Campaign, Campaign → Ad Set. המסמך משתמש במינוח החדש.

---

## קטגוריה 1: Technical Setup (משקל 25%)

### L01 — Insight Tag מותקן ופעיל

- **מה בודקים:** Campaign Manager → Analyze → Insight Tag. סטטוס "Active" וכיסוי דומיינים. ב-API: `adTagDomains`.
- **ספים:** PASS: פעיל ומדווח בכל עמודי האתר ב-30 הימים האחרונים | WARNING: פעיל אך חסר בחלק מהעמודים (למשל עמודי תודה/בלוג) | FAIL: לא מותקן, או ללא סיגנל מעל 7 ימים.
- **תיקון מומלץ:** התקנה גלובלית דרך GTM על כל העמודים; אימות ב-Insight Tag status אחרי 24 שעות.
- **עדיפות:** Critical

### L02 — Conversions API (CAPI) פעיל

- **מה בודקים:** Campaign Manager → Analyze → Conversion tracking → sources. האם קיים מקור CAPI (ישיר, Zapier, או CRM) לצד ה-Insight Tag.
- **ספים:** PASS: CAPI פעיל ושולח אירועים server-side (deduplication מול ה-tag מוגדר) | WARNING: CAPI מוגדר אך שולח חלקית / ללא deduplication | FAIL: מעקב מבוסס browser tag בלבד.
- **תיקון מומלץ:** חיבור CAPI דרך אינטגרציית CRM נתמכת (Salesforce/HubSpot/Dynamics 365) או ישירות ב-API. מדד ייחוס: מפרסמים מדווחים על ~31% עלייה בהמרות מיוחסות.
- **עדיפות:** Critical

**כיסוי משפך (תת-בדיקה של L02):** בתוך Conversion tracking, ודאו אירועים גם ל-TOFU (הרשמה לתוכן) וגם ל-BOFU (Demo / QUALIFIED_LEAD / PURCHASE) — ≥3 rules פעילים המכסים לפחות שני שלבי משפך; חוסר כיסוי מוריד את L02 ל-WARNING לכל היותר.

---

## קטגוריה 2: Audience Targeting (משקל 25%)

### L03 — טירגוט Job Titles ספציפי

- **מה בודקים:** Ad Set → Audience → Job Titles מול Job Functions. ב-API: `targetingCriteria` facets.
- **ספים:** PASS: טירגוט לפי titles ספציפיים התואמים ICP (או שילוב Function+Seniority מנומק) | WARNING: Job Function רחב בלבד ללא סינון Seniority | FAIL: טירגוט גנרי (Function בלבד, ללא ICP מוגדר).
- **תיקון מומלץ:** בניית רשימת 15-30 titles מדויקים מה-CRM; לחלופין Function + Seniority + Skills.
- **עדיפות:** High

### L04 — סינון Company Size תואם ICP

- **מה בודקים:** Ad Set → Audience → Company Size מול הגדרת ה-ICP של הלקוח.
- **ספים:** PASS: טווחי גודל חברה תואמים ICP (למשל Enterprise: 1,000+) | WARNING: טווח רחב מה-ICP באופן משמעותי | FAIL: ללא סינון גודל חברה כשה-ICP מוגדר.
- **תיקון מומלץ:** הצלבת גודל חברה של עסקאות שנסגרו ב-CRM והתאמת הטווחים.
- **עדיפות:** Medium

### L05 — Seniority מתאים להצעה

- **מה בודקים:** Ad Set → Audience → Seniority. האם רמת הבכירות תואמת את מקבל ההחלטה על ההצעה.
- **ספים:** PASS: Seniority תואם (Director+ להצעות Enterprise; IC לכלי עבודה) | WARNING: חוסר התאמה חלקי (כולל Entry בקמפיין למקבלי החלטות) | FAIL: ללא סינון Seniority בהצעה בכירה, או הפוך.
- **תיקון מומלץ:** בדיקת Demographics report — מי שלוחץ בפועל — והתאמת הסינון.
- **עדיפות:** Medium

### L06 — Matched Audiences פעילים

- **מה בודקים:** Plan → Audiences. קיום קהלי retargeting (website/engagement) וקהלי contact lists פעילים ובגודל מספק.
- **ספים:** PASS: retargeting + לפחות רשימת אנשי קשר אחת, שניהם מעל גודל מינימום (300 חברים לרשימות; 500 להרצת מודעות) | WARNING: רק אחד מהשניים, או קהלים מתחת לסף | FAIL: אין Matched Audiences כלל.
- **תיקון מומלץ:** יצירת קהל website visitors 90 יום + העלאת רשימת CRM; קמפיין retargeting ייעודי.
- **עדיפות:** High

### L07 — רשימות ABM הועלו

- **מה בודקים:** Plan → Audiences → Company lists (עד 300,000 חברות לרשימה). רלוונטי לחשבונות B2B Enterprise.
- **ספים:** PASS: רשימת חברות מפולחת לפי Tiers עם תוכן מותאם | WARNING: רשימה אחת ללא פילוח | FAIL: אסטרטגיית ABM מוצהרת ללא רשימות בפלטפורמה. (N/A אם אין מהלך ABM.)
- **תיקון מומלץ:** ייצוא target accounts מה-CRM/פלטפורמת ABM (Demandbase, 6sense), פילוח Tier 1/2/3, קריאייטיב פר Tier.
- **עדיפות:** Medium

### L08 — Audience Expansion כבוי בקמפייני דיוק

- **מה בודקים:** Ad Set → Audience → "Enable Audience Expansion" checkbox. ב-API: `audienceExpansionEnabled`.
- **ספים:** PASS: כבוי בכל קמפייני ה-precision/ABM (מופעל רק בקמפיין scale מבודד ומנומק) | WARNING: מופעל בחלק מקמפייני הדיוק | FAIL: מופעל כברירת מחדל בכל הקמפיינים.
- **תיקון מומלץ:** כיבוי גורף; אם רוצים scale — קמפיין נפרד עם תקציב מבודד למדידה.
- **עדיפות:** High

### L09 — Predictive Audiences נבחנו

- **מה בודקים:** Plan → Audiences → Predictive Audiences (החליפו Lookalikes ב-Feb 2024). האם נוצרו על בסיס מקור איכותי (conversions/lead list).
- **ספים:** PASS: Predictive Audience פעיל עם מקור ≥300 רשומות ותקציב בדיקה | WARNING: נוצר אך לא רץ, או מקור קטן/חלש | FAIL: לא נבחנו כלל בחשבון בשל (הוצאה ≥3 חודשים).
- **תיקון מומלץ:** יצירה מרשימת לקוחות סגורים או קהל המרות; בדיקה מול קהל ידני באותו קריאייטיב.
- **עדיפות:** Low

---

## קטגוריה 3: Creative Quality (משקל 20%)

### L10 — Thought Leader Ads (TLA) פעילים

- **מה בודקים:** קמפיינים עם קריאייטיב TLA (פוסטים אישיים ממומנים; זמין גם לחברים שאינם עובדים מאז March 2025). זמינים תחת objectives: Brand Awareness, Engagement, Video Views. חלוקת תקציב: אחוז ההוצאה על TLA מסך תקציב LinkedIn.
- **ספים:** PASS: TLA פעילים עם ≥30% מהתקציב | WARNING: פעילים אך 15-30% תקציב | FAIL: <15% או לא בשימוש כלל.
- **תיקון מומלץ:** בחירת 2-3 עובדים/שותפים עם אמינות בתעשייה ופוסטים אותנטיים; בקשת אישור דרך Campaign Manager. בנצ'מרק: CPC של $2.29-$4.14 מול ~$13 ב-Sponsored Content רגיל, CTR גבוה פי 2-3.
- **עדיפות:** High

### L11 — גיוון פורמטים

- **מה בודקים:** Ads tab → פורמטים פעילים ב-30 הימים האחרונים (Single Image, Video, Document, Carousel, Conversation...). רשימת הפורמטים העדכנית: ראו `standards/platform-specs.md`.
- **ספים:** PASS: ≥2 פורמטים פעילים עם תקציב משמעותי כל אחד | WARNING: פורמט דומיננטי אחד + שני סמלי | FAIL: פורמט יחיד בלבד.
- **תיקון מומלץ:** הוספת Document Ads (בנצ'מרק engagement ~7%) או Video לצד Single Image; השוואת CPL פר פורמט אחרי 30 יום.
- **עדיפות:** Medium

### L12 — Video Ads נבחנו

- **מה בודקים:** קיום קמפיין/קריאייטיב וידאו פעיל או שנבחן ב-90 הימים האחרונים. מפרטי וידאו: ראו `standards/platform-specs.md`.
- **ספים:** PASS: וידאו פעיל עם נתוני view rate נמדדים | WARNING: נבחן בעבר ונזנח ללא ניתוח | FAIL: מעולם לא נבחן בחשבון בשל.
- **תיקון מומלץ:** וידאו קצר (15-30 שניות) עם כתוביות ומסר ב-3 השניות הראשונות; בדיקה תחת Engagement או Video Views.
- **עדיפות:** Low

### L13 — רענון קריאייטיב כל 4-6 שבועות

- **מה בודקים:** תאריכי יצירת המודעות הפעילות מול היום; מגמת CTR לאורך זמן (עייפות קריאייטיב = ירידה עקבית ב-CTR עם עליית frequency).
- **ספים:** PASS: כל המודעות הפעילות בנות ≤6 שבועות, או ותיקות עם CTR יציב | WARNING: מודעות בנות 6-10 שבועות עם ירידת CTR מתחילה | FAIL: מודעות בנות >10 שבועות עם ירידת CTR ≥25% מהשיא.
- **תיקון מומלץ:** לוח רענון חודשי: 2-3 וריאציות חדשות, השבתת המודעה החלשה ביותר.
- **עדיפות:** Medium

---

## קטגוריה 4: Lead Gen & Performance (משקל 15%)

### L14 — Lead Gen Form עם ≤5 שדות

- **מה בודקים:** Assets → Lead Gen Forms → מספר שדות (כולל שדות שאלה מותאמים) ושיעור השלמה.
- **ספים:** PASS: ≤5 שדות ו-completion rate ≥10% (בנצ'מרק פלטפורמה: ~13%) | WARNING: 6-7 שדות או completion 5-10% | FAIL: ≥8 שדות או completion <5%.
- **תיקון מומלץ:** השארת שדות auto-fill בלבד (שם, אימייל, חברה, תפקיד) + שדה סינון אחד לכל היותר.
- **עדיפות:** High

### L15 — סנכרון Lead Gen Forms ל-CRM בזמן אמת

- **מה בודקים:** אינטגרציית leads: Campaign Manager → Account settings → Leads sync, או חיבור דרך Zapier/CRM נטיבי. זמן מהליד עד הופעה ב-CRM.
- **ספים:** PASS: סנכרון אוטומטי בזמן אמת ל-CRM | WARNING: ייצוא CSV ידני בתדירות קבועה | FAIL: לידים נאספים ולא נמשכים (ליד "נרקב" בפלטפורמה).
- **תיקון מומלץ:** חיבור נטיבי ל-HubSpot/Salesforce; SLA מענה לליד <שעה — קצב המענה הוא המנוף הגדול ביותר על conversion.
- **עדיפות:** Critical

### L18 — Objective תואם שלב משפך

- **מה בודקים:** לכל קמפיין: ה-objective מול הקהל והקריאייטיב (למשל Lead Generation לקהל קר לחלוטין = חוסר התאמה נפוץ). רשימת ה-objectives העדכנית: ראו `standards/platform-specs.md`.
- **ספים:** PASS: כל הקמפיינים עם התאמת objective-קהל-הצעה | WARNING: קמפיין אחד עם חוסר התאמה | FAIL: דפוס שיטתי (BOFU objectives לקהלים קרים בלבד).
- **תיקון מומלץ:** מבנה דו-שלבי: Awareness/Engagement (כולל TLA) לקהל קר → Lead Generation ל-retargeting.
- **עדיפות:** High

### L19 — A/B Testing פעיל

- **מה בודקים:** קיום מבחן מובנה פעיל או שהסתיים ב-60 הימים האחרונים — קריאייטיב או קהל — עם משתנה יחיד ותקציב מספק.
- **ספים:** PASS: מבחן פעיל/עדכני עם מסקנה מתועדת | WARNING: וריאציות רצות במקביל ללא מבנה מבחן | FAIL: אין שום בדיקה ב-90 יום.
- **תיקון מומלץ:** מבחן אחד בכל רגע נתון, משתנה יחיד, ≥2 שבועות או עד מובהקות.
- **עדיפות:** Medium

### L20 — תדירות Message Ads מרוסנת

- **מה בודקים:** קמפייני Sponsored Messaging — תדירות שליחה לאותו נמען. הערה: Sponsored Messaging הופסק ב-EU מאז Jan 2022 — בקהלי EU הבדיקה N/A.
- **ספים:** PASS: ≤1 הודעה ל-30-45 יום לנמען | WARNING: 1 ל-15-30 יום | FAIL: >1 ל-15 יום.
- **תיקון מומלץ:** frequency cap + החרגת מי שקיבל הודעה לאחרונה; העדפת Conversation Ads (open rate בנצ'מרק 50-60%) על InMail גנרי.
- **עדיפות:** Medium

---

## קטגוריה 5: Bidding & Budget (משקל 15%)

### L16 — אסטרטגיית Bid: להתחיל Manual CPC

- **מה בודקים:** Ad Set → Bidding. Maximum Delivery הוא היקר ביותר; Manual CPC נותן שליטה בשלב הלמידה.
- **ספים:** PASS: Manual CPC (או Cost Cap) בקמפיינים חדשים; Maximum Delivery רק בקמפיין מוכח שמוצה בו ה-manual | WARNING: Maximum Delivery כברירת מחדל אך CPC בתוך בנצ'מרק | FAIL: Maximum Delivery גורף עם CPC מעל $10.
- **תיקון מומלץ:** מעבר ל-Manual CPC בהצעה מעט מעל טווח ההמלצה של המערכת, העלאה הדרגתית עד קצב delivery מספק.
- **עדיפות:** High

### L17 — תקציב יומי מספק

- **מה בודקים:** Ad Set → Budget. תקציב יומי ל-Sponsored Content.
- **ספים:** PASS: ≥$50/יום ל-ad set | WARNING: $25-50/יום | FAIL: <$25/יום (אין מספיק דאטה ללמידה).
- **תיקון מומלץ:** איחוד ad sets קטנים; עדיף 2 ad sets עם $75 מ-6 עם $25.
- **עדיפות:** Medium

### L21 — CTR מעל בנצ'מרק

- **מה בודקים:** CTR ל-Sponsored Content (30 יום), פר קמפיין ופר פורמט.
- **ספים:** PASS: ≥0.44% | WARNING: 0.30-0.44% | FAIL: <0.30%.
- **תיקון מומלץ:** אם FAIL — קודם קריאייטיב (hook, ויזואל), אחר כך קהל. TLA כמנוף CTR (בנצ'מרק ~2.68% median).
- **עדיפות:** High

### L22 — CPC בתוך בנצ'מרק

- **מה בודקים:** CPC ממוצע חשבוני ופר קמפיין (30 יום). קהלים בכירים יקרים יותר ($6.40+ צפוי).
- **ספים:** PASS: ≤$7.00 (או מוצדק לקהל senior) | WARNING: $7-10 | FAIL: >$10.00 ללא הצדקת קהל.
- **תיקון מומלץ:** בדיקת bid strategy (L16), הרחבת קהל צר מדי מעל מינימום, שיפור relevancy דרך CTR.
- **עדיפות:** Medium

### L23 — מעקב Lead-to-Opportunity ולא רק CPL

- **מה בודקים:** האם קיים דיווח downstream: כמה מהלידים הפכו ל-opportunities/עסקאות, פר קמפיין. ב-CRM או ב-Revenue Attribution Report (L26).
- **ספים:** PASS: lead→opportunity rate נמדד פר קמפיין ומשפיע על הקצאת תקציב | WARNING: נמדד ברמת ערוץ בלבד | FAIL: אופטימיזציה ל-CPL בלבד.
- **תיקון מומלץ:** העברת UTM + campaign ID ל-CRM; דוח חודשי CPL מול cost-per-opportunity.
- **עדיפות:** High

### L24 — חלונות ייחוס מוגדרים

- **מה בודקים:** Conversion rules → attribution settings. תצורה מומלצת: 30-day click / 7-day view. (ב-CAPI ניתן כיום להגדיר lookback עד 365 יום לאירועים נבחרים — ודאו עקביות בין rules.)
- **ספים:** PASS: 30d click / 7d view אחיד בכל ה-rules | WARNING: תצורות שונות בין rules ללא נימוק | FAIL: ברירות מחדל לא מוכרות / view-through ארוך שמנפח דיווח.
- **תיקון מומלץ:** יישור כל ה-rules לתצורה אחת ותיעודה; השוואה מול דאטת CRM.
- **עדיפות:** Medium

### L25 — Demographics Report נסקר חודשית

- **מה בודקים:** Campaign Manager → Analyze → Demographics: מי בפועל רואה ולוחץ (title, seniority, company size) מול ה-ICP.
- **ספים:** PASS: סקירה חודשית מתועדת עם החרגות/התאמות בעקבותיה | WARNING: נסקר לעיתים ללא פעולה | FAIL: לא נסקר כלל — תקציב זולג לקהל לא רלוונטי.
- **תיקון מומלץ:** ריטואל חודשי: 5 ה-titles הגדולים בהוצאה מול ICP → החרגה/חידוד טירגוט.
- **עדיפות:** Medium

---

## בדיקות משלימות (L26-L27)

### L26 — Revenue Attribution Report + אינטגרציית CRM (closed-loop)

- **מה בודקים:** Campaign Manager → Analyze → Revenue Attribution Report; חיבור CRM (Salesforce / HubSpot / Dynamics 365, זמין מאז June 2025 ל-HubSpot) שמאפשר דיווח impression-to-revenue ברמת חשבון.
- **ספים:** PASS: CRM מחובר ו-RAR פעיל עם דאטת pipeline/opportunities | WARNING: CRM מחובר אך RAR לא נסקר / דאטה חלקית | FAIL: אין חיבור CRM — אין הוכחת השפעה על revenue.
- **תיקון מומלץ:** חיבור ה-CRM ב-Business Manager, אימות סנכרון opportunities, הוספת RAR לדוח החודשי לצד L23.
- **עדיפות:** High

### L27 — LinkedIn Audience Network (LAN) כבוי

- **מה בודקים:** Ad Set → Placements → "LinkedIn Audience Network" toggle. קונצנזוס מומחים: OFF — איכות ה-placements נמוכה והוא מדלל את דאטת הביצועים.
- **ספים:** PASS: כבוי בכל הקמפיינים (או פועל רק בקמפיין בדיקה מבודד עם brand safety lists) | WARNING: פעיל בחלק מהקמפיינים ללא ניטור placements | FAIL: פעיל גורף עם חלק ניכר מההוצאה זולג ל-network.
- **תיקון מומלץ:** כיבוי בכל ad set; אם בוחנים — תקציב מבודד + block lists ובחינת CPL בנפרד.
- **עדיפות:** High

---

## מיפוי בדיקות → קטגוריות Health Score

| קטגוריה | משקל | בדיקות |
|---|---|---|
| Technical Setup | 25% | L01, L02, L24, L26 |
| Audience Targeting | 25% | L03-L09, L27 |
| Creative Quality | 20% | L10-L13 |
| Lead Gen & Performance | 15% | L14, L15, L18-L20 |
| Bidding & Budget | 15% | L16, L17, L21-L23, L25 |

הדירוג (PASS/WARNING/FAIL), חישוב הציון, סדר העדיפויות ו-Quick Wins — לפי `ads/references/audit-process.md`.

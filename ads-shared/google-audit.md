# Google Ads — מדריך ביקורת 80 בדיקות

**מטרה**: רשימת הבדיקות המלאה לביקורת חשבון Google Ads, לשימוש סקיל `ads-google` (וסקיל `ads-youtube` לבדיקות G-DG/G-CTV).
**גרסה**: 1.0 | **נבדק**: 2026-09
**מתודולוגיה**: המתודולוגיה כאן היא evergreen — עקרונות הביקורת אינם משתנים. עובדות פלטפורמה משתנות (רשימת סוגי קמפיינים עדכנית, שדות API, מפרטי נכסים) אינן מוטמעות כאן — הן נמצאות ב-`standards/platform-specs.md` וב-`standards/gaql-notes.md`. פרגמנטים של GAQL בבדיקות ניתנים להרצה ישירה מול Google Ads MCP, אך הסתייגויות תאימות-שדות (אילו שדות לא ניתן לשלב באותה שאילתה) מתועדות ב-`standards/gaql-notes.md` — קרא אותו לפני הרצה.

**תהליך, ציון ודוח**: לפי `ads/references/audit-process.md` (PASS/WARNING/FAIL, ‏Health Score, ‏Quick Wins).
**משקולות קטגוריה** (מתוך `ads-google/SKILL.md`): Conversion Tracking ‏25% | Wasted Spend ‏20% | Account Structure ‏15% | Keywords ‏15% | Ads ‏15% | Settings ‏10%. בדיקות PMax/Demand Gen/Display/YouTube/Bidding/Landing Pages משויכות לקטגוריות אלו לפי העמודה "קטגוריית ציון" בכל מקבץ.

**כלל זהב לנתונים**: לנתח רק קמפיינים ו-ad groups במצב ENABLED; לבצע דדופליקציה של מילות מפתח לפי `(ad_group_id + keyword_text + match_type)`; חלון נתונים מינימלי 30 יום (`segments.date DURING LAST_30_DAYS`).

---

## מקבץ 1: Conversion Tracking — ‏G-T1 עד G-T10 (קטגוריית ציון: Conversion Tracking)

### G-T1 | קיום Conversion Actions פעילים
- **מה בודקים**: GAQL: `SELECT conversion_action.name, conversion_action.status, conversion_action.type, conversion_action.primary_for_goal FROM conversion_action WHERE conversion_action.status = 'ENABLED'`
- **ספים**: PASS: ‏≥1 פעולת המרה primary פעילה עם המרות ב-30 הימים האחרונים | WARNING: פעולות קיימות אך 0 המרות ב-30 יום | FAIL: אין פעולת המרה פעילה כלל
- **תיקון מומלץ**: הגדרת פעולת המרה ראשית התואמת את יעד העסק (רכישה/ליד) ואימות ירי התג
- **עדיפות**: Critical

### G-T2 | Google Tag מותקן ויורה בכל העמודים
- **מה בודקים**: UI: ‏Tools > Data Manager > Google tag > Diagnostics; אימות עם Tag Assistant על עמוד הבית, עמוד מוצר/שירות ועמוד תודה
- **ספים**: PASS: התג יורה בכל העמודים ללא שגיאות | WARNING: התג חסר בחלק מהעמודים או שגיאות diagnostics לא-קריטיות | FAIL: התג לא מותקן / לא יורה בעמוד ההמרה
- **תיקון מומלץ**: פריסת gtag.js או GTM גלובלית דרך template האתר, לא עמוד-עמוד
- **עדיפות**: Critical

### G-T3 | Enhanced Conversions פעיל
- **מה בודקים**: GAQL: `SELECT customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled FROM customer` ‏+ UI: הגדרות פעולת ההמרה > Enhanced conversions (סטטוס "Recording enhanced conversions")
- **ספים**: PASS: פעיל ומדווח על כל פעולות ההמרה הראשיות | WARNING: פעיל חלקית או בסטטוס "Awaiting data" מעל 14 יום | FAIL: כבוי
- **תיקון מומלץ**: הפעלת Enhanced Conversions עם נתוני first-party מגובבים (email/phone) דרך GTM
- **עדיפות**: Critical

### G-T4 | Consent Mode v2 (חובה ל-EU/EEA)
- **מה בודקים**: UI: ‏Data Manager > Diagnostics > Consent settings; בדיקת פרמטרי `ad_storage`/`ad_user_data`/`ad_personalization` ברשת (Network tab)
- **ספים**: PASS: מיושם מלא עם CMP מאושר (אם יש תנועת EEA) | WARNING: מיושם basic בלבד (ללא modeling) | FAIL: תנועת EEA קיימת ואין Consent Mode
- **תיקון מומלץ**: הטמעת Consent Mode v2 advanced דרך CMP מרשימת Google CMP Partner
- **עדיפות**: Critical (אם EEA) / Low (אם אין תנועת EEA — לסמן N/A)

### G-T5 | מיפוי Primary מול Secondary
- **מה בודקים**: GAQL: `SELECT conversion_action.name, conversion_action.primary_for_goal, conversion_action.category FROM conversion_action WHERE conversion_action.status = 'ENABLED'`
- **ספים**: PASS: רק המרות אמיתיות (רכישה/ליד איכותי) מסומנות primary | WARNING: מיקרו-המרות (page view, scroll) כ-primary לצד ראשיות | FAIL: ‏bidding מתבצע על מיקרו-המרות בלבד
- **תיקון מומלץ**: העברת מיקרו-המרות ל-secondary; להשאיר 1-2 פעולות primary לכל היותר לכל יעד
- **עדיפות**: High

### G-T6 | Offline Conversion Import (לידים)
- **מה בודקים**: UI: ‏Data Manager > integrations (CRM/‏Zapier/‏Sheets); GAQL: `SELECT conversion_action.name FROM conversion_action WHERE conversion_action.type IN ('UPLOAD_CLICKS', 'UPLOAD_CALLS')`
- **ספים**: PASS: יבוא offline פעיל עם העלאות ב-30 הימים האחרונים | WARNING: מוגדר אך ללא העלאות טריות | FAIL: עסק לידים ללא יבוא offline כלל
- **תיקון מומלץ**: חיבור CRM דרך GCLID/Enhanced Conversions for Leads לסגירת הלולאה ליד→עסקה
- **עדיפות**: High (עסקי לידים) / N/A (eCommerce טהור)

### G-T7 | Server-Side Tagging
- **מה בודקים**: UI: בדיקה אם קיים GTM Server container (בקשות ל-subdomain first-party במקום googletagmanager.com)
- **ספים**: PASS: sGTM פעיל | WARNING: client-side בלבד עם Enhanced Conversions | FAIL: client-side בלבד וללא Enhanced Conversions (אובדן מדידה משמעותי)
- **תיקון מומלץ**: פריסת GTM server container (Cloud Run/‏Stape) לשיפור דיוק מדידה ועמידות ל-ad blockers
- **עדיפות**: Medium

### G-T8 | מודל Attribution
- **מה בודקים**: GAQL: `SELECT conversion_action.attribution_model_settings.attribution_model FROM conversion_action WHERE conversion_action.status = 'ENABLED'`
- **ספים**: PASS: ‏GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN בכל הפעולות הראשיות | WARNING: last-click בפעולה ראשית עם מספיק נתונים ל-DDA | FAIL: מודלים מבוססי-חוקים ישנים (לא אמור להתקיים — כולם שודרגו אוטומטית ל-DDA; אם מופיע, לדווח כאנומליה)
- **תיקון מומלץ**: מעבר ל-Data-driven attribution; ‏last-click רק כ-fallback בנפח נמוך
- **עדיפות**: Medium

### G-T9 | ניתוח Conversion Lag
- **מה בודקים**: UI: ‏Attribution > Path metrics > Days to conversion; או השוואת `segments.conversion_lag_bucket` ב-GAQL
- **ספים**: PASS: ‏>90% מההמרות בתוך חלון של 7 ימים, או lag מובא בחשבון בניתוח | WARNING: ‏10-30% מההמרות מגיעות אחרי 7 ימים ולא מתחשבים בכך | FAIL: החלטות אופטימיזציה מתקבלות על נתוני 1-3 ימים אחרונים עם lag ארוך
- **תיקון מומלץ**: להחריג את 7 הימים האחרונים מכל השוואת ביצועים; לתעד את ה-lag הממוצע ב-CLAUDE.md של העסק
- **עדיפות**: Medium

### G-T10 | ‏Double Counting והיגיינת המרות
- **מה בודקים**: GAQL: `SELECT conversion_action.name, metrics.all_conversions FROM conversion_action WHERE segments.date DURING LAST_30_DAYS` — לחפש פעולות כפולות (GA4 + gtag על אותו אירוע, שתיהן primary)
- **ספים**: PASS: כל אירוע עסקי נספר פעם אחת | WARNING: כפילות קיימת אך רק אחת primary | FAIL: אותה המרה נספרת פעמיים כ-primary (ניפוח נתוני bidding)
- **תיקון מומלץ**: בחירת מקור אחד (gtag ישיר עדיף על יבוא GA4 לרוב), השני ל-secondary או הסרה
- **עדיפות**: Critical

---

## מקבץ 2: Account Structure — ‏G-A1 עד G-A8 (קטגוריית ציון: Account Structure)

### G-A1 | ארגון קמפיינים לפי לוגיקה עסקית
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.advertising_channel_type, campaign.status FROM campaign WHERE campaign.status = 'ENABLED'` — מיפוי מול קווי המוצר/שירות של העסק
- **ספים**: PASS: מבנה משקף מוצרים/שירותים/גיאוגרפיה בצורה עקבית | WARNING: חפיפות חלקיות או קמפיינים "כלליים" ללא theme | FAIL: קמפיין אחד עם כל מילות המפתח, או מבנה סותר
- **תיקון מומלץ**: ארגון מחדש לפי product line / intent, עם הפרדת קהלים חמים/קרים
- **עדיפות**: High

### G-A2 | הפרדת Brand מ-Non-Brand
- **מה בודקים**: GAQL: `SELECT campaign.name, ad_group_criterion.keyword.text FROM keyword_view WHERE campaign.status = 'ENABLED'` — לזהות מונחי מותג מעורבבים עם generic
- **ספים**: PASS: קמפיין brand נפרד עם תקציב ו-bidding נפרדים | WARNING: מונחי מותג ו-generic באותו קמפיין | FAIL: אין הפרדה ו-brand "בולע" את רוב התקציב ומנפח ROAS
- **תיקון מומלץ**: קמפיין Brand ייעודי (Exact/Phrase) + נגטיב מותג בקמפיינים הגנריים
- **עדיפות**: High

### G-A3 | גודל ומיקוד Ad Groups
- **מה בודקים**: GAQL: `SELECT ad_group.id, ad_group.name, ad_group_criterion.keyword.text FROM keyword_view WHERE ad_group.status = 'ENABLED' AND metrics.impressions > 0` — ספירת מילים ייחודיות לאחר דדופ
- **ספים**: PASS: ‏≤20 מילות מפתח ל-ad group, נושא הדוק | WARNING: ‏21-40 מילים או קוהרנטיות נושאית חלשה | FAIL: ‏>40 מילים או נושאים מעורבבים בעליל
- **תיקון מומלץ**: פיצול לקבוצות ממוקדות-נושא (15-20 מילים מקסימום) עם RSA תואם לכל נושא
- **עדיפות**: Medium

### G-A4 | ‏SKAGs מיושנים
- **מה בודקים**: ספירת ad groups עם מילת מפתח אחת בלבד מתוך שאילתת G-A3
- **ספים**: PASS: אין SKAGs, או בודדים עם הצדקה (מונח volume עצום) | WARNING: ‏10-30% מה-ad groups הם SKAGs | FAIL: מבנה SKAG גורף (>30%)
- **תיקון מומלץ**: איחוד SKAGs לקבוצות נושאיות — Smart Bidding עובד טוב יותר עם נפח נתונים מאוחד
- **עדיפות**: Medium

### G-A5 | קניבליזציה בין קמפיינים
- **מה בודקים**: מתוך שאילתת G-A3: לזהות אותו `(keyword_text + match_type)` ביותר מקמפיין ENABLED אחד
- **ספים**: PASS: אין כפילויות | WARNING: כפילויות עם חלוקה מכוונת (geo/audience שונים) | FAIL: כפילויות ללא בידול — הקמפיינים מתחרים זה בזה
- **תיקון מומלץ**: השארת המילה בקמפיין המנצח בלבד; שימוש בנגטיבים לניתוב תנועה
- **עדיפות**: High

### G-A6 | קונבנציית שמות ותוויות
- **מה בודקים**: GAQL: `SELECT campaign.name, label.name FROM campaign_label` ‏+ סריקת שמות קמפיינים לתבנית עקבית
- **ספים**: PASS: תבנית שמות עקבית (סוג | מוצר | geo | intent) | WARNING: עקביות חלקית | FAIL: שמות ברירת מחדל ("Campaign #4") או כאוס
- **תיקון מומלץ**: אימוץ תבנית `[Type]-[Product]-[Geo]-[Intent]` ותוויות לקיבוץ דוחות
- **עדיפות**: Low

### G-A7 | היגיינת Paused/Removed
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.status FROM campaign` — יחס ENABLED מול PAUSED
- **ספים**: PASS: ‏paused ישנים מאורכבים/מתויגים, מבנה נקי | WARNING: עשרות paused ללא תיוג המקשים על ניווט | FAIL: קמפיינים ENABLED "רדומים" (0 impressions ב-30 יום) — בעיית הגשה לא מטופלת
- **תיקון מומלץ**: תיוג ארכיון ל-paused; חקירת קמפיינים פעילים ללא הגשה (policy/bid/budget)
- **עדיפות**: Low

### G-A8 | חפיפת Search מול PMax
- **מה בודקים**: השוואת search terms של PMax (‏UI: ‏Insights > Search terms, או `campaign_search_term_insight` ב-GAQL) מול מילות המפתח ב-Search
- **ספים**: PASS: ‏PMax משלים את Search (Exact ב-Search מנצח את PMax באוקציה) ומוחלות brand exclusions | WARNING: חפיפה ניכרת ללא exclusions | FAIL: ‏PMax בולע תנועת brand/מילים קיימות בעלות גבוהה יותר
- **תיקון מומלץ**: brand exclusions ב-PMax + נגטיבים ברמת קמפיין PMax (זמין לכל המפרסמים) לפינוי התנועה ל-Search
- **עדיפות**: High

---

## מקבץ 3: Search — ‏G-S1 עד G-S14 (קטגוריית ציון: Keywords / Ads)

### G-S1 | אסטרטגיית Match Types
- **מה בודקים**: GAQL: `SELECT ad_group_criterion.keyword.match_type, metrics.cost_micros, metrics.conversions FROM keyword_view WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: תמהיל מדורג Exact→Phrase→Broad עם היגיון (Broad רק עם Smart Bidding) | WARNING: ‏Broad דומיננטי (>60% הוצאה) עם Smart Bidding אך ללא נגטיבים מספקים | FAIL: ‏Broad Match ללא Smart Bidding (Manual CPC/eCPC)
- **תיקון מומלץ**: ‏Broad רק תחת tCPA/tROAS + רשימות נגטיב חזקות; היוריסטיקת legacy BMM: ‏BROAD + Manual CPC = שריד BMM, לא בחירה מכוונת (ראה gaql-notes)
- **עדיפות**: Critical

### G-S2 | התפלגות Quality Score
- **מה בודקים**: GAQL: `SELECT ad_group_criterion.keyword.text, ad_group_criterion.quality_info.quality_score, metrics.cost_micros FROM keyword_view WHERE campaign.status = 'ENABLED' AND metrics.impressions > 0`
- **ספים**: PASS: ממוצע משוקלל-הוצאה ≥7 | WARNING: ממוצע 5-6 | FAIL: ממוצע <5
- **תיקון מומלץ**: טיפול ברכיב החלש (Ad relevance / Expected CTR / LP experience) לפי G-S3
- **עדיפות**: High

### G-S3 | רכיבי QS למילים יקרות
- **מה בודקים**: GAQL: `SELECT ad_group_criterion.keyword.text, ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr FROM keyword_view WHERE metrics.cost_micros > 50000000` (מעל ~$50)
- **ספים**: PASS: אין רכיב BELOW_AVERAGE במילים יקרות | WARNING: רכיב אחד BELOW_AVERAGE | FAIL: ‏≥2 רכיבים BELOW_AVERAGE במילים שמוציאות >10% מהתקציב
- **תיקון מומלץ**: ‏Ad relevance→שכתוב RSA לנושא; ‏LP experience→התאמת עמוד נחיתה; ‏CTR→שיפור headlines
- **עדיפות**: High

### G-S4 | מילים עם QS נמוך
- **מה בודקים**: מתוך G-S2: מילים עם QS < 5 והוצאה ב-30 יום
- **ספים**: PASS: ‏0 מילים כאלה עם הוצאה משמעותית | WARNING: ‏QS ‏5-6 עם הוצאה | FAIL: ‏QS < 5 עם הוצאה פעילה
- **תיקון מומלץ**: pause או שיוך מחדש ל-ad group ממוקד עם מודעה ועמוד ייעודיים
- **עדיפות**: Medium

### G-S5 | כיסוי Negative Keywords
- **מה בודקים**: GAQL: `SELECT shared_set.name, shared_set.member_count FROM shared_set WHERE shared_set.type = 'NEGATIVE_KEYWORDS'` ‏+ `SELECT campaign.name, campaign_criterion.keyword.text FROM campaign_criterion WHERE campaign_criterion.negative = TRUE` (לספור את שניהם יחד — ראה gaql-notes)
- **ספים**: PASS: רשימות משותפות ברמת חשבון + נגטיבים בקמפיין, עודכנו ב-30 הימים האחרונים | WARNING: נגטיבים קיימים אך לא עודכנו >60 יום | FAIL: אין רשימות נגטיב משותפות כלל
- **תיקון מומלץ**: רשימות ממוקדות-נושא: Informational (how to, DIY, מה זה), Job-seeker (jobs, דרושים, משכורת), Competitor (רק אם מוחרג בכוונה), Free-intent (free, חינם, crack)
- **עדיפות**: Critical

### G-S6 | איכות הנגטיבים (over-blocking)
- **מה בודקים**: סריקת הנגטיבים הקיימים: התפלגות match type + הצלבה מול שאילתות ממירות ב-Search Terms Report
- **ספים**: PASS: רוב הנגטיבים Exact/Phrase, אף נגטיב לא חוסם שאילתה ממירה | WARNING: נגטיבים ב-Broad ללא הצדקה מפורשת | FAIL: נגטיב חוסם שאילתות שהמירו בעבר
- **תיקון מומלץ**: **לעולם לא להציע נגטיב Broad Match ללא הצדקה מפורשת** — ברירת מחדל Exact ‏`[keyword]` לשאילתה ספציפית, Phrase ‏`"keyword"` לדפוס כוונה; לגזור נגטיבים משאילתות אמיתיות בדוח, לא מניחושים
- **עדיפות**: Critical

### G-S7 | כריית Search Terms
- **מה בודקים**: GAQL: `SELECT search_term_view.search_term, metrics.cost_micros, metrics.conversions FROM search_term_view WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.cost_micros DESC LIMIT 200`
- **ספים**: PASS: ‏<10% מההוצאה על שאילתות לא-רלוונטיות | WARNING: ‏10-20% | FAIL: ‏>20%
- **תיקון מומלץ**: לסמן wasted spend רק על שאילתות עם >‏$10 הוצאה ו-0 המרות; להוסיף כנגטיבים ולכמת חיסכון חודשי ב-$ בדוח
- **עדיפות**: Critical

### G-S8 | מספר RSA לכל Ad Group
- **מה בודקים**: GAQL: `SELECT ad_group.id, ad_group_ad.ad.type, ad_group_ad.status FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED' AND campaign.advertising_channel_type = 'SEARCH'`
- **ספים**: PASS: ‏≥3 מודעות RSA פעילות ל-ad group (או 1 RSA חזק + ניסוי) | WARNING: ‏1-2 מודעות | FAIL: ‏ad groups פעילים עם 0 מודעות
- **תיקון מומלץ**: השלמה ל-3 RSA עם זוויות מסר שונות לכל ad group פעיל
- **עדיפות**: High

### G-S9 | ‏Ad Strength
- **מה בודקים**: GAQL: `SELECT ad_group_ad.ad_strength, ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED' AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'`
- **ספים**: PASS: כל ה-RSA ב-GOOD/EXCELLENT | WARNING: ‏AVERAGE | FAIL: ‏POOR בקבוצות עם הוצאה
- **תיקון מומלץ**: הוספת headlines ייחודיים (מילת מפתח, הצעת ערך, CTA) עד EXCELLENT
- **עדיפות**: Medium

### G-S10 | מלאי Headlines/Descriptions
- **מה בודקים**: GAQL: `SELECT ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED'` — ספירה לכל מודעה
- **ספים**: PASS: ‏≥8 headlines ייחודיים ו-≥3 descriptions | WARNING: ‏5-7 headlines | FAIL: ‏<5 headlines או headlines כפולים
- **תיקון מומלץ**: מילוי ל-10-15 headlines מגוונים (keyword, benefit, proof, CTA, מחיר/מבצע)
- **עדיפות**: Medium

### G-S11 | ‏Over-Pinning
- **מה בודקים**: מתוך שאילתת G-S10: שדה `pinned_field` בכל headline/description
- **ספים**: PASS: ‏0-2 pins אסטרטגיים (compliance/brand) | WARNING: ‏3-5 pins | FAIL: כל השדות מוצמדים (RSA הפך למודעה סטטית)
- **תיקון מומלץ**: שחרור pins שאינם דרישת compliance; לתת ל-RSA לבצע אופטימיזציית קומבינציות
- **עדיפות**: Low

### G-S12 | ‏DKI ו-Customizers
- **מה בודקים**: חיפוש `{KeyWord:` ‏/ `{CUSTOMIZER.` ב-headlines מתוך G-S10
- **ספים**: PASS: ‏DKI בשימוש נכון עם fallback תקין, או לא בשימוש בכוונה | WARNING: ‏DKI עם fallback גנרי מדי | FAIL: ‏DKI שבור (טקסט placeholder מוצג במודעה חיה)
- **תיקון מומלץ**: תיקון fallback; ‏DKI רק בקבוצות עם מילים דומות תחבירית
- **עדיפות**: Low

### G-S13 | איכות הקופי (CTA, ערך, בידול)
- **מה בודקים**: סקירה ידנית של טקסטים מ-G-S10: קיום CTA מפורש, הצעת ערך, מבדל תחרותי, התאמת שפה לקהל
- **ספים**: PASS: שלושת הרכיבים קיימים ברוב המודעות | WARNING: חסר רכיב אחד באופן שיטתי | FAIL: קופי גנרי ללא CTA וללא בידול
- **תיקון מומלץ**: שכתוב לפי תבנית: ‏headline מילת-מפתח + headline ערך + headline הוכחה/CTA
- **עדיפות**: Medium

### G-S14 | ‏Impression Share למילים מובילות
- **מה בודקים**: GAQL: `SELECT campaign.name, metrics.search_impression_share, metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: ‏IS ≥ 70% בקמפיינים אסטרטגיים, או פער מוסבר | WARNING: ‏IS ‏40-70% עם budget_lost גבוה | FAIL: ‏IS < 40% בקמפיין ליבה ללא תוכנית
- **תיקון מומלץ**: ‏budget_lost→תקציב/פיצול geo; ‏rank_lost→QS ו-bids
- **עדיפות**: Medium

---

## מקבץ 4: Performance Max — ‏G-PM1 עד G-PM10 (קטגוריית ציון: Account Structure / Ads)

### G-PM1 | מבנה Asset Groups
- **מה בודקים**: GAQL: `SELECT asset_group.name, asset_group.status, campaign.name FROM asset_group WHERE campaign.status = 'ENABLED'`
- **ספים**: PASS: asset group לכל theme מוצרי/קהלי מובחן | WARNING: asset group אחד "לכל דבר" | FAIL: קמפיין PMax ללא חלוקה נושאית ועם signals סותרים
- **תיקון מומלץ**: פיצול לפי קווי מוצר/כוונה; כל asset group עם final URL ו-signals משלו
- **עדיפות**: High

### G-PM2 | שלמות ומגוון נכסים
- **מה בודקים**: GAQL: `SELECT asset_group_asset.field_type, asset_group_asset.performance_label FROM asset_group_asset WHERE asset_group.status = 'ENABLED'` — כיסוי טקסט/תמונות/וידאו/לוגו (מפרטי גדלים: ‏`standards/platform-specs.md`)
- **ספים**: PASS: כל סוגי הנכסים מלאים כולל וידאו שהועלה (לא auto-generated) | WARNING: וידאו auto-generated בלבד | FAIL: חסרים סוגי נכסים שלמים (אין תמונות/וידאו)
- **תיקון מומלץ**: השלמת כל ה-field types; החלפת נכסים עם performance_label = LOW
- **עדיפות**: High

### G-PM3 | ‏Audience Signals
- **מה בודקים**: UI: כל asset group > Audience signal (custom segments, רשימות לקוחות, demographics); אין שדה GAQL מלא — ראה gaql-notes
- **ספים**: PASS: ‏signals עם נתוני first-party (Customer Match / remarketing) + custom segments | WARNING: רק interest segments גנריים | FAIL: ללא signals כלל בקמפיין חדש (<90 יום)
- **תיקון מומלץ**: הוספת רשימת לקוחות + custom segment מבוסס שאילתות ממירות מ-Search
- **עדיפות**: Medium

### G-PM4 | ‏Search Themes
- **מה בודקים**: UI: asset group > Search themes (עד 25 לכל group)
- **ספים**: PASS: ‏themes מוגדרים ותואמים שאילתות ממירות | WARNING: ‏themes גנריים/חלקיים | FAIL: לא מנוצלים כלל כשיש נתוני Search זמינים
- **תיקון מומלץ**: הזנת themes מהשאילתות הממירות המובילות של קמפייני Search
- **עדיפות**: Medium

### G-PM5 | ‏Brand Exclusions
- **מה בודקים**: UI: הגדרות קמפיין PMax > Brand exclusions (זמין לכל המפרסמים)
- **ספים**: PASS: מוחל בכל קמפייני PMax כשקיים קמפיין Brand ב-Search | WARNING: מוחל חלקית | FAIL: אין exclusions ו-PMax מקניבל תנועת brand (ראה G-A8)
- **תיקון מומלץ**: רשימת brand exclusion אחת ברמת חשבון, מוחלת על כל ה-PMax
- **עדיפות**: High

### G-PM6 | ‏Negative Keywords ב-PMax
- **מה בודקים**: UI: הגדרות קמפיין > Negative keywords (זמין ברמת קמפיין וחשבון לכל המפרסמים; מכסה מורחבת — המספר העדכני ב-`standards/platform-specs.md`)
- **ספים**: PASS: נגטיבים מוחלים על בסיס search terms של PMax | WARNING: רשימת החשבון בלבד ללא נגטיבים ספציפיים | FAIL: ‏0 נגטיבים כשה-search terms מראים בזבוז
- **תיקון מומלץ**: כריית search terms של PMax (זמינות מלאה בדיווח) והחלת כללי הנגטיב של G-S6
- **עדיפות**: High

### G-PM7 | ‏URL Expansion
- **מה בודקים**: UI: הגדרות קמפיין > Final URL expansion (מופעל/כבוי + exclusions)
- **ספים**: PASS: מופעל עם page exclusions (קריירה, בלוג, תמיכה) או כבוי בהחלטה מנומקת | WARNING: מופעל ללא exclusions | FAIL: מופעל ומפנה תנועה לעמודים לא-מסחריים בפועל
- **תיקון מומלץ**: החרגת עמודים לא-מסחריים או כיבוי והפניה ל-URLs ידניים
- **עדיפות**: Medium

### G-PM8 | ‏Channel-Level Reporting
- **מה בודקים**: UI: קמפיין PMax > Report by channel (התפלגות בין Search/Shopping/Display/YouTube/Discover/Gmail/Maps); דיווח channel-level זמין גם ב-API — ראה `standards/gaql-notes.md` לשדות
- **ספים**: PASS: ההתפלגות נסקרה והוצאה על ערוצים חלשים מטופלת | WARNING: לא נסקר מעולם | FAIL: ערוץ אחד (לרוב Display) בולע >50% מהתקציב עם CPA כפול מהיעד
- **תיקון מומלץ**: שימוש בבקרות ההיגוי החדשות (steering) ובחיזוק נכסי הערוצים החזקים
- **עדיפות**: Medium

### G-PM9 | פיד מוצרים (eCommerce)
- **מה בודקים**: UI: ‏Merchant Center > Diagnostics; ‏GAQL: `SELECT shopping_product.item_id, shopping_product.status FROM shopping_product` לפסילות
- **ספים**: PASS: ‏<2% פריטים פסולים, titles מותאמים | WARNING: ‏2-10% פסולים | FAIL: ‏>10% פסולים או פיד לא מחובר
- **תיקון מומלץ**: תיקון פסילות פיד; העשרת titles במונחי חיפוש
- **עדיפות**: High (eCommerce) / N/A (לידים ללא פיד)

### G-PM10 | ‏Insights ו-New Customer Mode
- **מה בודקים**: UI: ‏Insights tab (קטגוריות חיפוש, סגמנטים) + הגדרת Customer acquisition (New customer / High value new customer mode)
- **ספים**: PASS: ‏Insights נסקר חודשי ו-new customer mode מוגדר בהתאם לאסטרטגיה | WARNING: אחד מהשניים חסר | FAIL: ‏PMax רץ "עיוור" — אף אחד לא נסקר
- **תיקון מומלץ**: שגרת סקירה חודשית + החרגת רשימות לקוחות קיימים אם היעד הוא לקוחות חדשים
- **עדיפות**: Low

---

## מקבץ 5: Demand Gen — ‏G-DG1 עד G-DG3 (קטגוריית ציון: Ads / Account Structure)

> Demand Gen החליף סופית את Video Action Campaigns (כל ה-VAC שודרגו אוטומטית עד אפריל 2026). קמפיין VAC שעדיין מופיע = אנומליה לדיווח. סקיל `ads-youtube` מפנה ישירות לבדיקות אלו.

### G-DG1 | תמהיל נכסי Video + Image
- **מה בודקים**: GAQL: `SELECT ad_group_ad.ad.type, asset.type FROM ad_group_ad WHERE campaign.advertising_channel_type = 'DEMAND_GEN' AND ad_group_ad.status = 'ENABLED'` — אימות שקיימים גם נכסי וידאו וגם נכסי תמונה בכל קמפיין
- **ספים**: PASS: וידאו + תמונות בכל קמפיין Demand Gen (השילוב מניב ~20% יותר המרות באותו CPA לעומת וידאו בלבד) | WARNING: פורמט אחד בלבד | FAIL: קמפיין עם נכס בודד יחיד
- **תיקון מומלץ**: העלאת נכסי תמונה (1:1 ו-1.91:1) לצד הווידאו; מפרטים מלאים ב-`standards/platform-specs.md`
- **עדיפות**: High

### G-DG2 | ‏Audience Signals והתאמת משפך
- **מה בודקים**: UI: קמפיין Demand Gen > Audiences (custom segments, ‏lookalikes, ‏Customer Match) + אימות שפעולת ההמרה המשויכת תואמת יעד upper/mid-funnel
- **ספים**: PASS: קהלים מבוססי first-party + lookalikes, והמרה תואמת שלב משפך | WARNING: קהלים גנריים בלבד, או מדידה ב-last-click בלבד | FAIL: ללא קהלים מוגדרים, או קמפיין עליון-משפך שנשפט לפי המרות last-click בלבד
- **תיקון מומלץ**: ‏Customer Match כ-seed ל-lookalike; מדידה עם view-through ו-DDA, לא last-click
- **עדיפות**: Medium

### G-DG3 | ניטור Frequency (אין Frequency Capping)
- **מה בודקים**: UI: דוח Reach & Frequency לקמפיין; זיהוי קמפיינים שהיו VAC והסתמכו על frequency caps — ‏**מגבלה קריטית: Demand Gen לא תומך ב-frequency capping** (ה-workaround היחיד: Video Frequency Groups באלפא)
- **ספים**: PASS: תדירות ממוצעת ≤4/שבוע במעקב ידני שוטף | WARNING: תדירות 4-7/שבוע ללא ניטור | FAIL: תדירות >7/שבוע — שחיקת קהל ובזבוז, במיוחד בקמפיינים שהיו VAC עם caps
- **תיקון מומלץ**: שגרת ניטור reach/frequency שבועית; הרחבת קהלים או פיצול תקציב כשהתדירות מטפסת; בקשת גישה ל-Video Frequency Groups אם קריטי
- **עדיפות**: Medium

---

## מקבץ 6: Display — ‏G-DP1 עד G-DP5 (קטגוריית ציון: Wasted Spend / Ads)

### G-DP1 | ביקורת Placements
- **מה בודקים**: GAQL: `SELECT group_placement_view.display_name, group_placement_view.placement_type, metrics.cost_micros, metrics.conversions FROM group_placement_view WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.cost_micros DESC LIMIT 200`
- **ספים**: PASS: ‏<5% הוצאה על placements באיכות נמוכה (אפליקציות משחקים, mfa sites) | WARNING: ‏5-15% | FAIL: ‏>15% או שלא בוצעה סקירה מעולם
- **תיקון מומלץ**: רשימת placement exclusions משותפת; החרגת קטגוריות אפליקציות לא-רלוונטיות
- **עדיפות**: High

### G-DP2 | הפרדת Display מ-Search
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.network_settings.target_content_network FROM campaign WHERE campaign.advertising_channel_type = 'SEARCH'`
- **ספים**: PASS: כל קמפייני Search עם Display Network כבוי | WARNING: מופעל בקמפיין משני | FAIL: מופעל בקמפייני ליבה (ערבוב ביצועים ובזבוז)
- **תיקון מומלץ**: כיבוי Display expansion ב-Search; ‏Display בקמפיין ייעודי עם kpi משלו
- **עדיפות**: High

### G-DP3 | ‏Responsive Display Assets
- **מה בודקים**: GAQL: `SELECT ad_group_ad.ad.responsive_display_ad.headlines, ad_group_ad.ad.responsive_display_ad.marketing_images FROM ad_group_ad WHERE campaign.advertising_channel_type = 'DISPLAY' AND ad_group_ad.status = 'ENABLED'`
- **ספים**: PASS: ‏≥5 headlines, ‏≥5 תמונות (landscape+square), לוגו | WARNING: מינימום בלבד | FAIL: מודעה עם נכס בודד מכל סוג
- **תיקון מומלץ**: השלמת נכסים לכל הפורמטים; מפרטים ב-`standards/platform-specs.md`
- **עדיפות**: Medium

### G-DP4 | אסטרטגיית קהלים ב-Display
- **מה בודקים**: UI: קהלי הקמפיין — הפרדת remarketing מ-prospecting; בדיקת optimized targeting (מופעל/כבוי)
- **ספים**: PASS: קמפיינים נפרדים ל-remarketing/prospecting, ‏optimized targeting בהחלטה מודעת | WARNING: מעורבב בקמפיין אחד | FAIL: ‏remarketing ללא החרגת ממירים, או optimized targeting מרחיב ללא בקרה
- **תיקון מומלץ**: פיצול קמפיינים; החרגת רשימת ממירים מ-prospecting
- **עדיפות**: Medium

### G-DP5 | ‏Frequency Capping ב-Display
- **מה בודקים**: UI: הגדרות קמפיין > Frequency capping (נתמך ב-Display, בניגוד ל-Demand Gen)
- **ספים**: PASS: ‏cap מוגדר (3-5 חשיפות/משתמש/שבוע לרוב היעדים) | WARNING: ללא cap אך תדירות בפועל נמוכה | FAIL: ללא cap ותדירות >10/שבוע
- **תיקון מומלץ**: הגדרת cap ברמת קמפיין בהתאם ליעד (awareness גבוה יותר, DR נמוך)
- **עדיפות**: Low

---

## מקבץ 7: YouTube / CTV — ‏G-YT1 עד G-YT5, ‏G-CTV1 (קטגוריית ציון: Ads / Conversion Tracking)

> ניתוח וידאו מעמיק (hooks, ‏ABCD, ‏Shorts) — בסקיל `ads-youtube`. כאן בדיקות החשבון בלבד. רשימת פורמטי הווידאו העדכנית — ‏`standards/platform-specs.md`.

### G-YT1 | התאמת סוג קמפיין וידאו ליעד
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.advertising_channel_type, campaign.bidding_strategy_type FROM campaign WHERE campaign.advertising_channel_type = 'VIDEO' AND campaign.status = 'ENABLED'`
- **ספים**: PASS: ‏awareness→CPM/Reach, ‏consideration→CPV, ‏action→Demand Gen | WARNING: אי-התאמה חלקית | FAIL: קמפיין VAC שרידי (אמור היה להשתדרג ל-Demand Gen — לדווח כאנומליה) או bidding סותר יעד
- **תיקון מומלץ**: מיפוי כל קמפיין וידאו ליעד משפך והתאמת הפורמט
- **עדיפות**: Medium

### G-YT2 | ‏View Rate ו-CPV
- **מה בודקים**: GAQL: `SELECT campaign.name, metrics.video_view_rate, metrics.average_cpv FROM campaign WHERE campaign.advertising_channel_type = 'VIDEO' AND segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: ‏view rate ≥ 15% (skippable) | WARNING: ‏10-15% | FAIL: ‏<10% (בעיית hook/קהל)
- **תיקון מומלץ**: החלפת 5 השניות הראשונות; ראה מסגרת ABCD בסקיל ads-youtube
- **עדיפות**: Medium

### G-YT3 | החרגות תוכן ו-Brand Safety
- **מה בודקים**: UI: הגדרות חשבון/קמפיין > Content exclusions (inventory type, סוגי תוכן, labels); הערה: החרגות placement ל-Shorts עובדות **ברמת חשבון בלבד**
- **ספים**: PASS: ‏inventory type מוגדר + החרגות ברמת חשבון | WARNING: ברירות מחדל בלבד | FAIL: מודעות רצות על תוכן בעייתי בפועל (מדוח placements)
- **תיקון מומלץ**: ‏Standard inventory לפחות; החרגות חשבון לערוצי ילדים/תוכן לא-רלוונטי
- **עדיפות**: Medium

### G-YT4 | ‏Placements וידאו — בזבוז
- **מה בודקים**: GAQL: `SELECT detail_placement_view.group_placement_target_url, metrics.cost_micros, metrics.conversions FROM detail_placement_view WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.cost_micros DESC LIMIT 100`
- **ספים**: PASS: ‏<10% הוצאה על ערוצים לא-רלוונטיים | WARNING: ‏10-20% | FAIL: ‏>20% (נפוץ: ערוצי תוכן ילדים, מוזיקה בלופ)
- **תיקון מומלץ**: החרגת ערוצים בזבזניים; לכמת חיסכון $ בדוח
- **עדיפות**: High

### G-YT5 | מגוון קריאייטיב וידאו
- **מה בודקים**: GAQL: `SELECT ad_group_ad.ad.video_ad.video.asset, ad_group.id FROM ad_group_ad WHERE campaign.advertising_channel_type = 'VIDEO' AND ad_group_ad.status = 'ENABLED'` — ספירת וידאו ייחודיים לקמפיין
- **ספים**: PASS: ‏≥3 וריאציות וידאו לקמפיין + פורמט אנכי (9:16) זמין | WARNING: ‏2 וריאציות או אופקי בלבד | FAIL: וידאו יחיד לקמפיין מעל 8 שבועות ללא רענון
- **תיקון מומלץ**: הוספת וריאציות hook/אורך + חיתוך אנכי לכל וידאו מוביל
- **עדיפות**: Medium

### G-CTV1 | מדידת המרות ב-Connected TV
- **מה בודקים**: אם יש הגשה משמעותית על מסכי TV (‏GAQL: `SELECT segments.device, metrics.cost_micros, metrics.conversions FROM campaign WHERE campaign.advertising_channel_type = 'VIDEO' AND segments.date DURING LAST_30_DAYS` — פילוח `segments.device = 'CONNECTED_TV'`): לוודא שמקור מדידת ההמרות הוא Google Ads conversion tracking או GA4. ‏**מגבלה קריטית: מדידת המרות Floodlight לא עובדת על מכשירי CTV**
- **ספים**: PASS: הוצאת CTV נמדדת ב-Google Ads tracking/GA4, ו-co-viewing metrics מובאים בחשבון בהשוואות reach | WARNING: הוצאת CTV קיימת אך לא פולחה ולא נותחה בנפרד | FAIL: המדידה מבוססת Floodlight בלבד — המרות CTV אינן נספרות כלל (עיוות bidding ודיווח)
- **תיקון מומלץ**: מעבר ל-Google Ads conversion tracking או GA4 כמקור ההמרות לקמפיינים עם הגשת TV; שקילת Brand Lift ל-awareness על מסכי TV; קריאייטיב מותאם TV (טקסט גדול, ויזואל פשוט למרחק צפייה)
- **עדיפות**: Critical (אם יש הוצאת CTV מהותית) / N/A (אין הגשת TV)

---

## מקבץ 8: Bidding — ‏G-B1 עד G-B7 (קטגוריית ציון: Settings)

### G-B1 | התאמת אסטרטגיית Bidding לבשלות
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.bidding_strategy_type, metrics.conversions FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: לכל קמפיין אסטרטגיה תואמת יעד ונפח | WARNING: ‏Maximize Clicks בקמפיין עם נתוני המרות מספקים | FAIL: ‏Manual CPC בקמפיין עם >30 המרות/חודש ללא הצדקה
- **תיקון מומלץ**: מדרג: ‏Maximize Conversions → tCPA (כשיש נפח) → tROAS (כשיש נתוני ערך)
- **עדיפות**: High

### G-B2 | ‏eCPC מיושן
- **מה בודקים**: מתוך G-B1: קמפיינים עם `MANUAL_CPC` + enhanced CPC מופעל
- **ספים**: PASS: אין eCPC בחשבון | WARNING: eCPC בקמפיינים משניים | FAIL: eCPC בקמפייני ליבה
- **תיקון מומלץ**: ‏eCPC הוצא משימוש (deprecated) — מעבר ל-Smart Bidding מלא (tCPA/tROAS/Maximize)
- **עדיפות**: High

### G-B3 | מוכנות ל-tCPA
- **מה בודקים**: המרות חודשיות לקמפיין מתוך G-B1
- **ספים**: PASS: ‏tCPA פעיל עם ≥30 המרות/30 יום בקמפיין | WARNING: ‏tCPA עם 15-30 המרות (למידה איטית ותנודתית) | FAIL: ‏tCPA עם <15 המרות/30 יום (אין לאלגוריתם נתונים)
- **תיקון מומלץ**: מתחת לסף — איחוד קמפיינים, פתיחה ל-Maximize Conversions, או שימוש בהמרה שכיחה יותר כ-primary
- **עדיפות**: High

### G-B4 | מוכנות ל-tROAS
- **מה בודקים**: המרות עם ערך: `SELECT campaign.name, metrics.conversions_value, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: ‏tROAS פעיל עם ≥50 המרות בעלות ערך/30 יום | WARNING: ‏30-50 המרות | FAIL: ‏tROAS עם <30 המרות או ללא ערכי המרה אמינים
- **תיקון מומלץ**: מתחת לסף — ‏tCPA או Maximize Conversion Value ללא target עד צבירת נפח
- **עדיפות**: High

### G-B5 | סבירות Targets מול ביצועים
- **מה בודקים**: השוואת ה-target המוגדר (`campaign.target_cpa.target_cpa_micros` / `campaign.target_roas.target_roas`) מול ה-CPA/ROAS בפועל ב-30 יום
- **ספים**: PASS: פער ≤20% בין target לביצוע בפועל | WARNING: פער 20-40% | FAIL: פער >40% (target לא ריאלי חונק הגשה או מבזבז)
- **תיקון מומלץ**: כיוון הדרגתי — שינוי target של ≤15% לשבוע, לא קפיצות
- **עדיפות**: Medium

### G-B6 | ‏Bid Adjustments (מכשיר/מיקום/קהל)
- **מה בודקים**: GAQL: `SELECT campaign.name, segments.device, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS` — פערי CPA בין מכשירים; בדיקת adjustments קיימים (בקמפייני Manual/eCPC בלבד — Smart Bidding מתעלם מרובם, ראה gaql-notes)
- **ספים**: PASS: פערי מכשיר >30% מטופלים (adjustment או החרגה) בקמפיינים ידניים; ב-Smart Bidding — מודעות לכך שהאלגוריתם מטפל | WARNING: פער גדול לא מטופל בקמפיין ידני | FAIL: מכשיר עם CPA פי 3 ו-0 התאמות
- **תיקון מומלץ**: בידניים — adjustments מבוססי נתונים; ב-Smart Bidding — ‏device adjustment ‏-100% רק להחרגה מוחלטת
- **עדיפות**: Low

### G-B7 | ‏AI Max for Search
- **מה בודקים**: UI: הגדרות קמפיין Search > AI Max (זהו setting בקמפיין Search קיים, לא סוג קמפיין; סטטוס ההשקה ולוחות זמנים של איחוד DSA — ‏`standards/platform-specs.md`)
- **ספים**: PASS: אם מופעל — רשימות נגטיב חזקות קיימות (G-S5 PASS), ‏headlines אוטומטיים במעקב, וקטגוריות search terms נסקרות | WARNING: מופעל ללא ביקורת search terms שוטפת | FAIL: מופעל עם G-S5 ב-FAIL (הרחבת reach ללא בלמים)
- **תיקון מומלץ**: לפני הפעלה — לוודא נגטיבים; אחרי — סקירת שבועית של קטגוריות והשפעת תקציב; להעריך מסלול מעבר לקמפייני DSA קיימים (איחוד DSA→AI Max בתהליך — לוח זמנים עדכני ב-platform-specs)
- **עדיפות**: Medium

---

## מקבץ 9: Budget & Wasted Spend — ‏G-W1 עד G-W8 (קטגוריית ציון: Wasted Spend / Settings)

### G-W1 | קמפיינים מוגבלי תקציב
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign_budget.amount_micros, metrics.search_budget_lost_impression_share FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: ‏budget_lost_IS < 5% בקמפיינים רווחיים | WARNING: ‏5-15% | FAIL: קמפיין עם CPA מתחת ליעד מוגבל תקציב (>15% budget lost) בזמן שקמפיין מפסיד מקבל תקציב
- **תיקון מומלץ**: הסטת תקציב מהמפסידים לרווחיים המוגבלים; לכמת המרות אבודות
- **עדיפות**: High

### G-W2 | ‏Invalid Clicks
- **מה בודקים**: GAQL: `SELECT campaign.name, metrics.invalid_click_rate, metrics.invalid_clicks FROM campaign WHERE segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: ‏<5% | WARNING: ‏5-10% | FAIL: ‏>10%
- **תיקון מומלץ**: החרגות IP, בדיקת placements חשודים, שקילת כלי הגנת קליקים
- **עדיפות**: Medium

### G-W3 | דיוק גיאוגרפי
- **מה בודקים**: GAQL: `SELECT geographic_view.country_criterion_id, metrics.cost_micros, metrics.conversions FROM geographic_view WHERE segments.date DURING LAST_30_DAYS ORDER BY metrics.cost_micros DESC`
- **ספים**: PASS: ‏<3% הוצאה מחוץ לאזורי השירות | WARNING: ‏3-10% | FAIL: ‏>10% הוצאה בינלאומית לא-רלוונטית
- **תיקון מומלץ**: תיקון הגדרת location option (ראה G-W4) והחרגת מדינות בזבזניות
- **עדיפות**: High

### G-W4 | ‏Location Option: Presence
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.geo_target_type_setting.positive_geo_target_type FROM campaign WHERE campaign.status = 'ENABLED'`
- **ספים**: PASS: ‏PRESENCE בכל הקמפיינים (אלא אם עסק תיירות/הגירה) | WARNING: מעורב | FAIL: ‏PRESENCE_OR_INTEREST בעסק מקומי (הצגת מודעות למתעניינים מרחוק)
- **תיקון מומלץ**: מעבר ל-"Presence" — לא "Presence or Interest"
- **עדיפות**: High

### G-W5 | ‏Search Partners ו-Display Expansion
- **מה בודקים**: GAQL: `SELECT campaign.name, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network FROM campaign WHERE campaign.advertising_channel_type = 'SEARCH'` ‏+ פילוח ביצועי `segments.ad_network_type`
- **ספים**: PASS: ‏Search Partners נסקר עם נתונים (נשאר רק אם CPA סביר), ‏Display כבוי | WARNING: מופעלים ולא נסקרו | FAIL: ‏Partners/Display עם CPA כפול ולא טופלו
- **תיקון מומלץ**: כיבוי רשתות שאינן מוכיחות את עצמן בפילוח network
- **עדיפות**: Medium

### G-W6 | ‏Ad Schedule
- **מה בודקים**: GAQL: `SELECT campaign.name, segments.hour, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS`
- **ספים**: PASS: פיזור שעות תואם דפוסי המרה (או 24/7 מוצדק ב-eCommerce) | WARNING: הוצאה לילית ניכרת ב-0 המרות בעסק שעות-פעילות | FAIL: ‏>15% מההוצאה בשעות עם 0 המרות היסטורית (עסקי לידים טלפוניים)
- **תיקון מומלץ**: ‏schedule מבוסס נתוני 90 יום; בעסק לידים — התאמה לשעות מענה
- **עדיפות**: Medium

### G-W7 | פיזור הוצאה ופארטו
- **מה בודקים**: מתוך נתוני G-S7 ו-G-B1: אחוז ההוצאה שמייצר 90% מההמרות
- **ספים**: PASS: זנב ארוך של מילים/קמפיינים ללא המרות מטופל שוטף | WARNING: ‏10-25% מההוצאה על ישויות שלא המירו ב-90 יום | FAIL: ‏>25%
- **תיקון מומלץ**: ‏pause לזנב הלא-ממיר (בכפוף ל-conversion lag, ‏G-T9) והסטה למנצחים
- **עדיפות**: High

### G-W8 | הערכת בזבוז חודשית כוללת
- **מה בודקים**: סכימה: שאילתות לא-רלוונטיות (G-S7) + placements גרועים (G-DP1, ‏G-YT4) + geo זולג (G-W3) + שעות מתות (G-W6), כאחוז מסך ההוצאה החודשית
- **ספים**: PASS: ‏<10% מסך ההוצאה | WARNING: ‏10-20% | FAIL: ‏>20%
- **תיקון מומלץ**: זהו המספר המסכם של הדוח — לצרף הערכת $ חודשית ותוכנית 30 יום לצמצום; חובה בכל דוח לפי SKILL.md
- **עדיפות**: Critical

---

## מקבץ 10: Extensions / Assets — ‏G-X1 עד G-X5 (קטגוריית ציון: Ads)

### G-X1 | ‏Sitelinks
- **מה בודקים**: GAQL: `SELECT asset.sitelink_asset.link_text, campaign_asset.status FROM campaign_asset WHERE asset.type = 'SITELINK' AND campaign_asset.status = 'ENABLED'`
- **ספים**: PASS: ‏≥4 sitelinks לקמפיין, עם descriptions, מפנים לעמודים שונים | WARNING: ‏2-3 או ללא descriptions | FAIL: ‏0-1
- **תיקון מומלץ**: ‏4-6 sitelinks לעמודי הערך המרכזיים (מחירים, אודות, קטגוריות, צור קשר)
- **עדיפות**: Medium

### G-X2 | ‏Callouts ו-Structured Snippets
- **מה בודקים**: GAQL: `SELECT asset.type, campaign_asset.status FROM campaign_asset WHERE asset.type IN ('CALLOUT', 'STRUCTURED_SNIPPET') AND campaign_asset.status = 'ENABLED'`
- **ספים**: PASS: ‏≥4 callouts + ‏≥1 structured snippet | WARNING: אחד מהסוגים חסר | FAIL: שניהם חסרים
- **תיקון מומלץ**: ‏callouts להוכחות (משלוח חינם, אחריות, ותק); ‏snippets לקטגוריות/שירותים
- **עדיפות**: Medium

### G-X3 | ‏Image Assets
- **מה בודקים**: GAQL: `SELECT asset.type FROM campaign_asset WHERE asset.type = 'IMAGE' AND campaign_asset.status = 'ENABLED'`
- **ספים**: PASS: נכסי תמונה פעילים בקמפייני Search מרכזיים | WARNING: חלקי | FAIL: אין כלל (ויתור על נדל"ן ויזואלי ב-SERP)
- **תיקון מומלץ**: העלאת תמונות 1:1 ו-1.91:1 רלוונטיות למוצר; מפרטים ב-`standards/platform-specs.md`
- **עדיפות**: Low

### G-X4 | ‏Call / Lead Form / Location Assets
- **מה בודקים**: GAQL: `SELECT asset.type FROM campaign_asset WHERE asset.type IN ('CALL', 'LEAD_FORM', 'LOCATION') AND campaign_asset.status = 'ENABLED'` — רלוונטיות לפי סוג העסק
- **ספים**: PASS: הנכסים התואמים את המודל העסקי קיימים (call לעסק טלפוני, location לעסק פיזי) | WARNING: קיימים חלקית | FAIL: עסק מבוסס-שיחות ללא call asset ו-call reporting
- **תיקון מומלץ**: הוספת הנכס התואם + הפעלת call reporting והמרת שיחות (משך סף)
- **עדיפות**: Medium (לפי מודל עסקי)

### G-X5 | ביצועי Assets והסרת חלשים
- **מה בודקים**: UI: ‏Assets > טבלת ביצועים (performance label: Low/Good/Best); ‏GAQL: `SELECT asset_field_type_view.field_type, metrics.impressions FROM asset_field_type_view`
- **ספים**: PASS: נכסי Low הוחלפו ברבעון האחרון | WARNING: נכסי Low פעילים >90 יום | FAIL: לא בוצעה סקירת נכסים מעולם
- **תיקון מומלץ**: שגרה רבעונית: החלפת כל נכס Low בווריאציה חדשה
- **עדיפות**: Low

---

## מקבץ 11: Landing Pages — ‏G-L1 עד G-L4 (קטגוריית ציון: Keywords — רכיב LP experience)

### G-L1 | התאמת מסר (Message Match)
- **מה בודקים**: דגימת 5 ה-final URLs היקרים: ‏GAQL: `SELECT ad_group_ad.ad.final_urls, metrics.cost_micros FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED' ORDER BY metrics.cost_micros DESC LIMIT 20` — השוואת headline המודעה מול ה-H1 בעמוד
- **ספים**: PASS: מילת המפתח/ההבטחה מהמודעה מופיעה above the fold | WARNING: התאמה חלקית (עמוד קטגוריה כללי) | FAIL: כל התנועה לעמוד הבית או עמוד ללא קשר למודעה
- **תיקון מומלץ**: עמוד נחיתה ייעודי לכל theme; ‏H1 משקף את ה-headline המרכזי
- **עדיפות**: High

### G-L2 | מהירות ו-Mobile
- **מה בודקים**: הרצת PageSpeed Insights על ה-URLs מ-G-L1 (mobile); ‏GAQL: פילוח `segments.device` להשוואת CVR mobile מול desktop
- **ספים**: PASS: ‏LCP < 2.5s ‏mobile ו-CVR mobile ≥ 70% מ-desktop | WARNING: ‏LCP ‏2.5-4s | FAIL: ‏LCP > 4s או CVR mobile < 50% מ-desktop
- **תיקון מומלץ**: אופטימיזציית תמונות/סקריפטים; טופס מקוצר ב-mobile
- **עדיפות**: High

### G-L3 | ‏CTA וטופס המרה
- **מה בודקים**: סקירה ידנית של עמודי G-L1: ‏CTA יחיד וברור above the fold, אורך טופס, אמצעי אמון (ביקורות, תקנים)
- **ספים**: PASS: ‏CTA בולט + טופס ≤5 שדות + אלמנטי אמון | WARNING: ‏CTA מתחרה או טופס 6-8 שדות | FAIL: אין CTA ברור או טופס >8 שדות
- **תיקון מומלץ**: ‏CTA אחד דומיננטי; קיצור הטופס לשדות הכרחיים בלבד
- **עדיפות**: Medium

### G-L4 | תקינות URLs ו-Tracking
- **מה בודקים**: בדיקת סטטוס HTTP לכל final URL מ-G-L1 (200, לא 404/301 שרשרת); אימות template מעקב ו-UTM עקביים; ‏auto-tagging: ‏GAQL: `SELECT customer.auto_tagging_enabled FROM customer`
- **ספים**: PASS: כל ה-URLs מחזירים 200, ‏auto-tagging פעיל, ‏UTM עקבי | WARNING: הפניות 301 או UTM לא עקבי | FAIL: ‏URL שבור (404) עם הוצאה פעילה, או auto-tagging כבוי
- **תיקון מומלץ**: תיקון/עדכון URLs שבורים מיידית (Quick Win קלאסי); הפעלת auto-tagging
- **עדיפות**: Critical (404) / Medium (השאר)

---

## סיכום ספירה

| מקבץ | בדיקות | טווח IDs |
|---|---|---|
| Conversion Tracking | 10 | G-T1–G-T10 |
| Account Structure | 8 | G-A1–G-A8 |
| Search | 14 | G-S1–G-S14 |
| Performance Max | 10 | G-PM1–G-PM10 |
| Demand Gen | 3 | G-DG1–G-DG3 |
| Display | 5 | G-DP1–G-DP5 |
| YouTube/CTV | 6 | G-YT1–G-YT5, G-CTV1 |
| Bidding | 7 | G-B1–G-B7 |
| Budget & Wasted Spend | 8 | G-W1–G-W8 |
| Extensions/Assets | 5 | G-X1–G-X5 |
| Landing Pages | 4 | G-L1–G-L4 |
| **סה"כ** | **80** | |

בדיקה שאינה רלוונטית לחשבון (למשל G-PM9 ללא eCommerce, ‏G-CTV1 ללא הגשת TV) מסומנת N/A עם נימוק ואינה נספרת בציון — לפי `ads/references/audit-process.md`.

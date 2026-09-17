# מפת הארכיטקטורה — מה כל קובץ עושה

הפאנל הוא **Next.js (App Router) + TypeScript + Tailwind + Framer Motion**, עברית RTL, מובייל-first.

**המבנה הזה הוא מפרט, לא תיקייה לשכפל.** בנה אותו מאפס לפי המפה הזאת (`npx create-next-app@latest --typescript --tailwind --app`). המבנה זהה לכל מוצר — רק התוכן בקונפיג והלוגיקה ב-`computeOffer`/`scoreLead` משתנים.

**מקרא:** 🟦 תבניתי (זהה בכל פאנל) · 🟨 ספציפי-ללקוח (ערוך תמיד) · 🟩 אופציונלי

**וריאנטים לפי סוג מוצר:**
- **סדנה/שירות** → יעד = וואטסאפ + שריון; מחיר למשתתף/לחבילה.
- **קורס/דיגיטלי** → הוסף **דף תוצאה אישי** לפי התשובות + **סדרת מיילים** (רשימת דיוור + קופון) במקום/לצד וואטסאפ. ה-lead-intake מעביר לרשימת דיוור, לא רק להתראה.
- **מוצר פיזי** → `computeOffer` לפי וריאנט/כמות; יעד = עגלה/וואטסאפ.

## מנוע הליבה (`lib/`)

| קובץ | סוג | מה עושה |
|---|---|---|
| `types.ts` | 🟨 | `Answers` (מפתח לכל שאלה), `Step` union (סדר המסכים), `Offer`/`LeadScore`/`LeadFormValues`, ופונקציות-נגזרת (למשל `isKidsTier`, `isSmallGroup`) שמנתבות מסלולים מותנים. **הקובץ הראשון שעורכים.** |
| `reducer.ts` | 🟦→🟨 | מכונת-המצבים. `ORDER[]` (סדר קדימה), `PROGRESS_STEPS[]`, `isSkipped()` (דילוג מותנה), `funnelReducer` (ANSWER/NEXT/BACK/GOTO/RESTORE/RESET), `progressFraction()` (ease-out). המנגנון תבניתי; **`ORDER` + `isSkipped` ספציפיים**. |
| `computeOffer.ts` | 🟨 | פונקציה טהורה `answers → Offer`. כל המחירים מ-`PRICING` בקונפיג, לא קשיחים. בונה headline/עוגן/benefits/agenda. |
| `scoreLead.ts` | 🟨 | פונקציה טהורה `answers → {score, tier, reasons[]}`. דחיפות > כמות > פרימיום. `reasons` בעברית → נכנס להתראת בעל העסק. |
| `analytics.ts` | 🟦 | `track(event, {step, step_index, props})` דרך `sendBeacon` ל-`/api/track`. **רק מפתח ה-session `<brand>_funnel_sid` משתנה.** לעולם לא זורק שגיאה. |
| `phone.ts` | 🟦 | `normalizeIsraeliPhone` → E.164 (`+972...`). מקור האמת לתקינות טלפון. |
| `pixel.ts` | 🟦 | עטיפת Meta Pixel (`pixelTrackCustom`). |
| `priceHold.ts` | 🟩 | טיימר "המחיר שמור ל-24 שעות" (scarcity). אם משתמשים בו, שיהיה אמיתי: כשהוא נגמר, ההצעה באמת נגמרת. |
| `persistence.ts` | 🟦 | שמירת מצב ל-localStorage (resume אם עזב באמצע) + `<brand>_lead_identity` (שם+טלפון לצורך `reservation_complete`). |
| `whatsapp.ts` | 🟨 | `buildWhatsAppLink` — לינק click-to-chat עם prefill. **המספר ספציפי.** |

## הרכיבים (`components/`)

| קובץ | סוג | מה עושה |
|---|---|---|
| `Funnel.tsx` | 🟦→🟨 | ה-orchestrator. `useReducer`, `renderStep()` (switch על `state.step`), פרוגרס, resume, slide-animations. הוספת/שינוי שלב = עריכת ה-switch כאן. |
| `steps/Welcome.tsx` | 🟩 | מסך פתיחה. **⚠️ מדולג כברירת מחדל** (שרף 72%). אם בונים אותו בכלל, `initialState` עדיין מתחיל בשאלה 1. |
| `steps/QuestionStep.tsx` | 🟦 | מסך שאלה גנרי (title + OptionCards). משרת את כל השאלות. |
| `steps/ValueScreen.tsx` | 🟨 | מסך ערך אמצע-משפך (מה מקבלים / תוצרים). |
| `steps/SocialProof.tsx` | 🟨 | עדויות/כוכבים לפני הטופס. |
| `steps/LeadCapture.tsx` | 🟦→🟨 | הטופס. **שם+טלפון בלבד** (CRO). honeypot, react-hook-form+zod, שומר identity ל-localStorage. |
| `steps/PriceReveal.tsx` | 🟨 | הפרס. אנימציית מחיר (עוגן→מיוחד), benefits, agenda. **וואטסאפ CTA ראשי, שריון משני.** |
| `ui/OptionCard.tsx`, `ui/Button.tsx`, `ui/Logo.tsx` | 🟦 | פרימיטיבים. |
| `Progress.tsx`, `AnimatedPrice.tsx`, `Countdown.tsx`, `Confetti.tsx`, `SocialProofPopup.tsx` | 🟦 | אפקטים/UI. |
| `AccessibilityWidget.tsx` | 🟦 | תוסף נגישות (חובה משפטית בישראל). |
| `MetaPixel.tsx` | 🟦 | הזרקת הפיקסל. |

## הדפים (`app/`)

| נתיב | סוג | מה |
|---|---|---|
| `page.tsx` | 🟦 | מרנדר `<Funnel/>`. |
| `layout.tsx` | 🟨 | מטא, גופן עברי, `dir="rtl"`, הזרקת פיקסל. |
| `api/lead-intake/route.ts` | 🟦→🟨 | **קולט ליד, מנרמל טלפון, מנקד, מעביר לבעל העסק/CRM. לעולם לא ללקוח.** rate-limit + honeypot. היעדים ספציפיים. |
| `api/track/route.ts` | 🟦 | כותב `funnel_events` (whitelist של אירועים). ראה `analytics-and-safety.md`. |
| `thank-you/page.tsx` | 🟨 | אחרי תשלום שריון. שולח `reservation_complete` עם identity. |
| `privacy/`, `terms/`, `accessibility/` | 🟨 | legal (תוכן ספציפי, מבנה תבניתי). |

## הקונפיג (`config/funnel.config.ts`) — 🟨 הקובץ שעורכים הכי הרבה

מקור האמת לכל קופי/מחיר/שאלה. בלוקים: `PRICING`, `BRAND`, `META_PIXEL_ID`, `WELCOME`, `QUESTIONS`, `VALUE_SCREEN`, `BENEFITS`, `SOCIAL_PROOF`, `PRICE_REVEAL`, `SOCIAL_POPUP`, `RESERVATION`, `THANK_YOU`, `URGENCY`, `LEAD_CAPTURE`, `CELEBRATION`, `NAV`, `RESUME`, `BUSINESS`, `A11Y`, `WA_NUMBER`, `WA_PREFILL_TEMPLATE`, `PRIVACY`, `TERMS`, `ACCESSIBILITY_STATEMENT`. פירוט מלא: `config-guide.md`.

## סדר העבודה בבנייה

1. `types.ts` — מודל התשובות והשלבים.
2. `config` בלוק `QUESTIONS` + `PRICING` + `BRAND`.
3. `reducer.ts` — `ORDER` + `isSkipped`.
4. `computeOffer.ts` + `scoreLead.ts`.
5. `Funnel.tsx` — התאמת ה-switch לשלבים.
6. שאר בלוקי הקונפיג (ערך, הוכחה חברתית, מחיר, legal).
7. `lead-intake` + `analytics` — יעדים ומפתח session.
8. מעבר CRO (`cro-rules.md`) → deploy.

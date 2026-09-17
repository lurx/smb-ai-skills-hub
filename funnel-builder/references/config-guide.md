# מדריך הקונפיג — `config/funnel.config.ts`

קובץ אחד = כל הקופי, המחירים, השאלות, המותג, ה-legal. עורכים כאן, לא ברכיבים. כל הבלוקים `export const`.

הדוגמאות למטה הן מפאנל סדנאות לדוגמה. החלף בתוכן שלך.

## `PRICING` — מקור כל המספרים
```ts
export const PRICING = {
  entry:    { regular: 220, special: 150 }, // ברירת מחדל כשלא נבחר מסלול
  standard: { regular: 220, special: 150 },
  premium:  { regular: 340, special: 250 },
  group: { regular: 1800, special: 1350, baseParticipants: 12, extraPerPerson: 75 },
};
```
`regular` = עוגן מחוק, `special` = המחיר שמופיע. `computeOffer.ts` קורא **רק מכאן** — אין מחירים קשיחים בלוגיקה.

## `BRAND` + `META_PIXEL_ID`
```ts
export const BRAND = { name: "המותג שלך", tagline: "...", logo: "/logo.svg" };
export const META_PIXEL_ID = ""; // "" = בלי פיקסל. הכנס את המזהה שלך.
```

## `QUESTIONS` — הבלוק הכי חשוב
כל שאלה: `title`, `subtitle?`, ומערך `options`. כל אופציה: `{value, label, emoji, hint?, image?}`.
```ts
export const QUESTIONS = {
  q1_goal: {
    title: "מה הדבר שהכי חסר לך היום?",   // ← שאלה 1 קלה ונעימה, לא כואבת
    options: [
      { value: "money",   label: "כסף",        emoji: "💰" },
      { value: "freedom", label: "חופש",       emoji: "🕊️" },
      { value: "meaning", label: "מימוש עצמי", emoji: "🎯" },
    ],
  },
  q1b_ages: {                         // שאלה מותנית (isSkipped מטפל)
    title: "לאיזה גילאים?",
    subtitle: "כדי להתאים מחיר בול 🎯",
    options: [ { value: "up_to_13", label: "עד גיל 13", emoji: "🧒" } ],
  },
  q4_style: {                          // עם תמונות דוגמה
    title: "איזה סגנון מדבר אליך?",
    options: [
      { value: "premium", label: "המסלול המורחב", emoji: "✨",
        hint: "כולל ליווי אישי אחרי", image: "/styles/premium.jpg" },
    ],
  },
} as const;
```
**כללים:**
- `value` = מזהה פנימי, **חייב להתאים ל-type ב-`types.ts`**. אל תשנה בלי לעדכן את ה-type.
- `label`/`emoji`/`hint` = מה שרואים. `hint` = שורת מחיר/הסבר קטן.
- כותרת דינמית לפי תשובה קודמת (למשל `titleBirthday`) — נקראת ב-`Funnel.tsx`.
- **אל תוסיף אופציית "רק בודק/מתעניין"** — יוצרת לידים בלי כוונה (לקח CRO).
- **סדר את השאלות בקשת רגשית עולה.** ראה `copy-and-design.md`.

## `VALUE_SCREEN` + `BENEFITS`
מסך ערך אמצע-משפך + רשימת מה-כלול (מוזרק ל-`Offer.benefits`).

## `SOCIAL_PROOF` + `SOCIAL_POPUP`
עדויות/כוכבים לפני הטופס + טוסט חוזר ("רותי מחיפה הרגע שריינה"). **scarcity אמיתי בלבד, לא מומצא.**

## `PRICE_REVEAL` — מסך הפרס
```ts
export const PRICE_REVEAL = {
  title: "הנה ההצעה המותאמת שלך 💛",
  specialOffer: "שריון היום נועל מחיר + מתנה",
  whatsappCta: "לדבר איתי בוואטסאפ",   // ← ה-CTA הראשי
  reassurance: "בלי התחייבות, רק שיחה",
};
```

## `RESERVATION` — שריון בתשלום
```ts
export const RESERVATION = {
  enabled: true, amount: 97, url: "https://<לינק-התשלום-שלך>",
  gift: "מתנה למשריין", scarcity: "נועל מחיר + {gift} ל-24ש'",
  deductible: true, deductibleNote: "מתקזז מהמחיר הסופי",
  cta: "לשריון מאובטח ב-97₪", afterNote: "...",
};
```
**משני** בדף (וואטסאפ ראשי). `{gift}` מוחלף ב-`gift`.

## `LEAD_CAPTURE` — הטופס
```ts
export const LEAD_CAPTURE = {
  title: "רגע לפני המחיר, לאן נשלח? 💛",
  fields: {
    name:  { label: "שם",    placeholder: "איך קוראים לך?" },
    phone: { label: "טלפון", placeholder: "05..." },
  },
};
```
**רק שם+טלפון.** כל השאר = בשיחה (לקח CRO: 46% נטשו בטופס עמוס).

## `WA_PREFILL_TEMPLATE` + `WA_NUMBER`
טקסט click-to-chat מוכן + המספר. `buildWhatsAppLink` מרכיב.

## `PRIVACY` / `TERMS` / `ACCESSIBILITY_STATEMENT`
טקסט legal מלא (מבנה `{title, intro, sections[]}`). חובה בישראל. עדכן שם עסק/ח.פ/יצירת-קשר ב-`BUSINESS`.

## checklist עריכת קונפיג לפאנל חדש
- [ ] `PRICING` — כל המחירים
- [ ] `BRAND` + `META_PIXEL_ID`
- [ ] `QUESTIONS` — כל שאלה+אופציות (value תואם type, סדר רגשי עולה)
- [ ] `VALUE_SCREEN` / `BENEFITS` / `SOCIAL_PROOF`
- [ ] `PRICE_REVEAL` / `RESERVATION` / `LEAD_CAPTURE`
- [ ] `WA_NUMBER` + `WA_PREFILL_TEMPLATE`
- [ ] `BUSINESS` + `PRIVACY`/`TERMS`/`A11Y`

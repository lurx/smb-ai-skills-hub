# The Complete 24-Step Sales Page Protocol

## CHUNK 1: THE HOOK (Steps 1-3)

### Step 1: Authority/Shock Opener (טאגליין)

Short provocative statement that breaks pattern.

**Example:**
```
"ביי ביי לקמפיינר, לקופירייטר ולמנהלת סושיאל..."
```

### Step 2: Welcome Line

Warm transition that creates intrigue.

**Example:**
```
"וולקאם ל[שם העסק]."
```

### Step 3: Big Promise Headline (H1)

[PRODUCT NAME] + Specific result with timeframe.

**Example:**
```
"[שם העסק] SCALE SYSTEM"
"איך לבנות עסק רזה ורווחי ב-2026 מבוסס AI שלא יושב על הזמן שלך –
ומאפשר לך לצאת לחופשה בלי לבדוק את הטלפון כל 4 דקות"
```

**JSON Output:**
```json
{
  "section": "hero",
  "tagline": "ביי ביי לקמפיינר...",
  "welcomeLine": "וולקאם ל[שם העסק].",
  "headline": "[שם העסק] SCALE SYSTEM",
  "subheadline": "איך לבנות עסק רזה ורווחי...",
  "ctaText": "רוצה לבדוק אם אני מתאים ✋🏻",
  "heroImage": "description of ideal hero image"
}
```

---

## CHUNK 2: THE PROBLEM SETUP (Steps 4-6)

### Step 4: Quick Context ("קצר ולעניין")

2 bad options the audience faces.

**Example:**
```
"עד היום עסקים עמדו בפני 2 אופציות.
למכור זמן באורגני, להפוך לליצני חצר...
או לצאת לממומן, לשים תקציב פרסום ובסוף לא להחזיר את ההשקעה."
```

### Step 5: The Solution Tease

"בגלל זה יצרנו את..." + 3 pillars/skills.

**Example:**
```
"התוכנית היחידה בישראל שתראה לך איך..."
- מערכת תוכן מבוססת AI
- פאנלים חכמים
- סקייל בממומן
```

### Step 6: The Enemy Statistics

4-5 scary statistics with 👈 emoji.

**Example:**
```
👈 41% מהתוכן בפייסבוק נוצר על ידי AI.
👈 71% מהתמונות ברשתות נוצרות על ידי AI.
👈 74% מהתוכן החדש באינטרנט מכיל AI.
```

**JSON Output:**
```json
{
  "section": "problem",
  "sectionTitle": "קצר ולעניין:",
  "intro": "עד היום עסקים עמדו בפני 2 אופציות...",
  "statistics": [
    { "emoji": "👈", "text": "41% מהתוכן בפייסבוק נוצר על ידי AI." },
    { "emoji": "👈", "text": "71% מהתמונות ברשתות נוצרות על ידי AI." }
  ],
  "pillars": ["מערכת תוכן מבוססת AI", "פאנלים חכמים", "סקייל בממומן"]
}
```

---

## CHUNK 3: PAIN AMPLIFICATION (Steps 7-9)

### Step 7: The Headline Statement

Bold, fear-inducing statement.

**Example:**
```
"ב 2026 פרסום ממומן הולך להתפוצץ לכולנו בפרצוף."
```

### Step 8: Pain Explanation

Detailed explanation of why the pain exists.

**Example:**
```
"ה-CPM עולה משנה לשנה... כל מי שימשיך להסתמך על ממומן
שעבד ב-2025 יראה את עלויות הליד מרקיעות שחקים..."
```

### Step 9: The Impossible Choice (3 Bad Options)

3 boxes showing why all current options suck.

**Example:**
```
- לבנות קהילה אורגנית לבד? = להפוך לליצן חצר
- לצאת ישר לממומן בלי קהילה? = להמר בקזינו
- לנסות את שניהם לבד? = שחיקה של 16 שעות ביום
```

**JSON Output:**
```json
{
  "section": "pain",
  "headline": "ב 2026 פרסום ממומן הולך להתפוצץ לכולנו בפרצוף.",
  "explanation": "ה-CPM עולה משנה לשנה...",
  "badOptions": [
    { "title": "לבנות קהילה אורגנית לבד?", "consequence": "להפוך לליצן חצר" },
    { "title": "לצאת ישר לממומן בלי קהילה?", "consequence": "להמר בקזינו" },
    { "title": "לנסות את שניהם לבד?", "consequence": "שחיקה של 16 שעות ביום" }
  ],
  "highlightedQuote": "לסמוך רק על ממומן ב-2026 זה כמו להמר בקזינו כשהבית תמיד מנצח."
}
```

---

## CHUNK 4: THE TURNING POINT (Steps 10-11)

### Step 10: Recognition of Problem

"We understood there's a serious problem"

**Example:**
```
"הבנו שיש כאן בעיה רצינית.
ב-4 שנים האחרונות ליווינו מעל 300 מומחים...
אבל בשנה האחרונה משהו משתנה..."
```

### Step 11: The Moment of Change

"This is the moment we decided to..."

**Example:**
```
"זה הרגע שבו המים מתחממים -
וזה הזמן לקפוץ לפני שיהיה מאוחר."
```

**JSON Output:**
```json
{
  "section": "turning_point",
  "headline": "הבנו שיש כאן בעיה רצינית.",
  "content": "ב-4 שנים האחרונות ליווינו מעל 300 מומחים...",
  "transitionHeadline": "זה הרגע שבו החלטנו לשלב כוחות."
}
```

---

## CHUNK 5: AUTHORITY (Steps 12-13)

### Step 12: Meet the Founders/Experts

Profile cards with credentials.

**Example:**
```
נטליה ריי - מובילת מערכות תוכן מבוססות AI
- בנתה חטיבת קואוצ'ינג ב-Mindvalley: 0 → $20M בשנה
- ניהלה קמפיינים בתקציבי מיליון דולר בחודש
- הקפיצה מאמן יוגה אנונימי ל-1M+ עוקבים אורגנית
```

### Step 13: The Mission

What they set out to do.

**Example:**
```
"יצאנו למשימה.
לחבר בין שני העולמות שעד היום היו נפרדים:
אורגני שבונה קהילה – וממומן שמוכר לה."
```

**JSON Output:**
```json
{
  "section": "authority",
  "headline": "מפגש הטיטאנים של ה[שם העסק].",
  "founders": [
    {
      "name": "נטליה ריי",
      "title": "מובילת מערכות תוכן מבוססות AI",
      "credentials": [
        "בנתה חטיבת קואוצ'ינג ב-Mindvalley: 0 → $20M בשנה",
        "ניהלה קמפיינים בתקציבי מיליון דולר בחודש"
      ],
      "currentRole": "מובילה את מערכת התוכן"
    }
  ],
  "mission": "יצאנו למשימה. לחבר בין שני העולמות..."
}
```

---

## CHUNK 6: THE SOLUTION REVEAL (Steps 14-15)

### Step 14: Product Reveal

Big headline + product name + promise.

**Example:**
```
"נרגשים לחשוף בפניכם את:
[שם העסק] SCALE SYSTEM
'איך לבנות עסק רזה ורווחי ב-2026 מבוסס AI...'"
```

### Step 15: Program Structure

3 phases with badges, goals, and leader.

**Example:**
```
חלק ראשון | חודשים 1-3
בניית האקו-סיסטם העסקי
המטרה: לבנות את המכונה שמוכרת בשבילך 24/7
כולל: פגישות אסטרטגיה אישיות + ליווי צמוד
מוביל: יגל עמוס
```

**JSON Output:**
```json
{
  "section": "solution",
  "revealText": "נרגשים לחשוף בפניכם את:",
  "productName": "[שם העסק] SCALE SYSTEM",
  "promise": "איך לבנות עסק רזה ורווחי ב-2026...",
  "phases": [
    {
      "badge": "חלק ראשון | חודשים 1-3",
      "title": "בניית האקו-סיסטם העסקי",
      "goal": "לבנות את המכונה שמוכרת בשבילך 24/7",
      "includes": "פגישות אסטרטגיה אישיות + ליווי צמוד",
      "leader": "יגל עמוס"
    }
  ]
}
```

---

## CHUNK 7: VALUE STACK - BONUSES (Steps 16-17)

### Step 16: Bonus Introduction

"And that's not all..." headline.

**Example:**
```
"וזה לא הכל... כשאתה מצטרף למחזור הקרוב בלבד
אתה מקבל גם בונוסים מטורפים:"
```

### Step 17: Bonus List (8-12 bonuses)

Each bonus with 💎 emoji, number, name, description, value.

**Example:**
```
💎 בונוס 1:
Hot Seat אישי עם נטליה ריי
סקירה חיה על התוכן, המערכת והבוטים שלך...
(שווי 2,000 ₪)
```

**JSON Output:**
```json
{
  "section": "bonuses",
  "headline": "וזה לא הכל...",
  "subheadline": "כשאתה מצטרף למחזור הקרוב בלבד אתה מקבל גם בונוסים מטורפים:",
  "bonuses": [
    {
      "number": 1,
      "emoji": "💎",
      "name": "Hot Seat אישי עם נטליה ריי",
      "description": "סקירה חיה על התוכן, המערכת והבוטים שלך...",
      "value": "2,000"
    }
  ],
  "totalValue": "XX,XXX",
  "freeText": "בחינם לגמרי."
}
```

---

## CHUNK 8: SOCIAL PROOF (Steps 18-19)

### Step 18: Testimonials Headline

"Results speak" headline.

**Example:**
```
"עדויות - התוצאות מדברות"
```

### Step 19: Detailed Testimonials

Name + title, hook, story, results with ✅.

**Example:**
```
דריה - מומחית לבריאות טבעית
מ-500 שקל בחודש ו-2,000 עוקבים ל... מכונת לידים ומכירות

[Story paragraph]

בתוך כמה חודשים:
✅ פי 25 במחזור החודשי
✅ 170+ עותקים של קורס דיגיטלי - תוך סופ"ש אחד
✅ 50+ לידים לתוכנית ליווי פרימיום 1:1
```

**JSON Output:**
```json
{
  "section": "testimonials",
  "headline": "עדויות - התוצאות מדברות",
  "testimonials": [
    {
      "name": "דריה",
      "title": "מומחית לבריאות טבעית",
      "hook": "מ-500 שקל בחודש ו-2,000 עוקבים ל... מכונת לידים ומכירות",
      "story": "...",
      "resultsTitle": "בתוך כמה חודשים:",
      "results": [
        "✅ פי 25 במחזור החודשי",
        "✅ 170+ עותקים של קורס דיגיטלי - תוך סופ\"ש אחד",
        "✅ 50+ לידים לתוכנית ליווי פרימיום 1:1"
      ]
    }
  ]
}
```

---

## CHUNK 9: URGENCY & AI STATEMENT (Step 20)

### Step 20: The AI Warning

Memorable quote about AI replacing people.

**Example:**
```
"בינה מלאכותית לא הולכת להחליף אותך.
אבל מישהו שמשתמש בבינה מלאכותית - בהחלט כן. 👀"
```

**JSON Output:**
```json
{
  "section": "urgency_quote",
  "quote": "בינה מלאכותית לא הולכת להחליף אותך.\nאבל מישהו שמשתמש בבינה מלאכותית - בהחלט כן.",
  "emoji": "👀"
}
```

---

## CHUNK 10: THE "WHY" STORY (Steps 21-22)

### Step 21: Why We Created This

Headline + backstory.

**Example:**
```
"למה יצרנו את [שם העסק] SCALE SYSTEM?
ב-4 שנים האחרונות ליווינו מעל 300 מומחים..."
```

### Step 22: The Industry is Changing

List of changes + opportunity window.

**Example:**
```
"תעשיית הדיגיטל משתנה מקצה לקצה.
✦ לבנות אקו-סיסטם עסקי עם פאנלים...
✦ להתקין מערכת תוכן AI...
✦ ולמנף את הכל עם ממומן חכם..."
```

**JSON Output:**
```json
{
  "section": "why_story",
  "headline": "למה יצרנו את [שם העסק] SCALE SYSTEM?",
  "story": "ב-4 שנים האחרונות ליווינו מעל 300 מומחים...",
  "industryHeadline": "תעשיית הדיגיטל משתנה מקצה לקצה.",
  "changes": [
    "✦ לבנות אקו-סיסטם עסקי עם פאנלים...",
    "✦ להתקין מערכת תוכן AI...",
    "✦ ולמנף את הכל עם ממומן חכם..."
  ],
  "opportunity": "חלון ההזדמנויות עכשיו..."
}
```

---

## CHUNK 11: CTA & FORM (Steps 23-24)

### Step 23: Form Introduction

Clear instruction.

**Example:**
```
"להגשת מועמדות למחזור הקרוב של תוכנית [שם העסק] SCALE SYSTEM,
מלא את הטופס ולחץ על הכפתור:"
```

### Step 24: Scarcity Disclaimer

Small text explaining exclusivity.

**Example:**
```
"*סליחה אבל לא כולם מתאימים לתוכנית… אין דף סליקה אחרי מילוי הטופס
ו-50% לא מתקבלים. אחרי מילוי הטופס אתה תעבור לשאלון ומשם לשיחת
התאמה עם גארי. אומר מראש - יש רק 15 מקומות בכל מחזור..."
```

**JSON Output:**
```json
{
  "section": "cta_form",
  "formIntro": "להגשת מועמדות למחזור הקרוב של תוכנית [שם העסק] SCALE SYSTEM...",
  "formFields": ["שם מלא", "המייל שלך", "טלפון נייד"],
  "consentText": "אני מאשר/ת קבלת דברי פרסומת מ...",
  "ctaText": "רוצה לבדוק אם אני מתאים ✋🏻",
  "scarcityText": "*סליחה אבל לא כולם מתאימים לתוכנית..."
}
```

---

## Final Output Schema

After completing all chunks, compile the full JSON:

```json
{
  "metadata": {
    "productName": "[שם העסק] SCALE SYSTEM",
    "targetAudience": "בעלי עסקים דיגיטליים, מומחים, יועצים",
    "bigIdea": "שילוב בין אורגני AI-powered לממומן חכם",
    "enemy": "השיטה הישנה שלא עובדת יותר",
    "webhookUrl": "placeholder"
  },
  "sections": {
    "hero": { ... },
    "problem": { ... },
    "pain": { ... },
    "turning_point": { ... },
    "authority": { ... },
    "solution": { ... },
    "bonuses": { ... },
    "testimonials": { ... },
    "urgency_quote": { ... },
    "why_story": { ... },
    "cta_form": { ... }
  },
  "globalElements": {
    "ctaText": "רוצה לבדוק אם אני מתאים ✋🏻",
    "ctaPlacementAfterSections": ["pain", "testimonials", "why_story", "final"],
    "pillars": ["מערכת תוכן מבוססת AI", "פאנלים חכמים", "סקייל בממומן"]
  }
}
```

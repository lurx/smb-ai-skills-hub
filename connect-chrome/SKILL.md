---
name: connect-chrome
version: 2.0.0
description: |
  Connect Claude to a real, visible Chrome browser it fully controls: navigate pages,
  click, fill forms, take screenshots, read console errors, inspect network requests
  and run performance audits. One-time setup using the official Chrome DevTools MCP
  server by Google. After setup, Claude drives Chrome in every session and you watch
  every action live in the browser window.
  Use when asked to "connect chrome", "open chrome", "launch browser", "control my
  browser", "חבר דפדפן", "תתחבר לכרום", "חיבור דפדפן", "פתח דפדפן", "תשלוט בדפדפן",
  "תפתח כרום".
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# חיבור דפדפן Chrome ל-Claude

הסקיל מחבר את Claude לדפדפן Chrome אמיתי ונראה לעין, דרך שרת ה-MCP הרשמי של גוגל
(Chrome DevTools MCP). אחרי התקנה חד-פעמית, Claude יכול לגלוש, ללחוץ, למלא טפסים,
לצלם מסכים, לקרוא שגיאות קונסול ולבדוק ביצועים. כל פעולה מופיעה בזמן אמת בחלון הדפדפן.

הדפדפן שנפתח משתמש בפרופיל נפרד משלו, כך שהחשבונות האישיים ב-Chrome הרגיל שלך לא
משותפים איתו.

## שלב 0: בדיקה אם כבר מחובר

אם בסשן הנוכחי כבר זמינים כלים שמתחילים ב-`mcp__chrome-devtools__` (למשל
`mcp__chrome-devtools__navigate_page`), הדפדפן כבר מחובר. דלג על ההתקנה: עבור ישר
לשלב 3 (דמו), או פשוט בצע את מה שהמשתמש ביקש.

אם הכלים לא זמינים, בדוק אם השרת כבר רשום:

```bash
claude mcp get chrome-devtools 2>&1 | head -5
```

- אם הפלט מציג את פרטי השרת: ההגדרה כבר קיימת, אבל הכלים נטענים רק בסשן חדש.
  אמור למשתמש לסגור ולפתוח מחדש את Claude Code (או Reload Window ב-VS Code /
  Antigravity), ואז לכתוב: "פתח את הדפדפן וצלם מסך של ynet.co.il". סיימת.
- אם הפלט אומר שאין שרת כזה: המשך לשלב 1.

## שלב 1: בדיקות מקדימות

הרץ:

```bash
command -v npx >/dev/null 2>&1 && echo "NODE: OK ($(node --version 2>/dev/null))" || echo "NODE: MISSING"
if [ -d "/Applications/Google Chrome.app" ] || command -v google-chrome >/dev/null 2>&1 || [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ] || [ -f "${PROGRAMFILES:-/nonexistent}/Google/Chrome/Application/chrome.exe" ]; then echo "CHROME: OK"; else echo "CHROME: NOT FOUND"; fi
```

אם `NODE: MISSING`: צריך להתקין Node.js (חד-פעמי, חינם). שאל את המשתמש עם
AskUserQuestion אם להתקין עכשיו, ואם כן:

- **Mac עם Homebrew:** `brew install node`
- **Mac בלי Homebrew / Windows:** הפנה להורדה מ-https://nodejs.org (גרסת LTS),
  ובקש מהמשתמש לחזור אחרי ההתקנה ולכתוב "חבר דפדפן" שוב.

אם `CHROME: NOT FOUND`: ייתכן ש-Chrome מותקן בנתיב לא סטנדרטי, ואז אפשר להמשיך
בכל זאת (השרת מוצא את Chrome לבד ברוב המקרים). אם Chrome באמת לא מותקן, הפנה
להורדה מ-https://www.google.com/chrome ועצור.

## שלב 2: רישום השרת

**Mac / Linux:**

```bash
claude mcp add -s user chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

**Windows:**

```bash
claude mcp add -s user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@latest
```

הדגל `-s user` רושם את השרת ברמת המשתמש, כך שהוא זמין בכל הפרויקטים ולא רק בתיקייה
הנוכחית.

אמת שהרישום הצליח:

```bash
claude mcp get chrome-devtools
```

## שלב 3: הפעלה מחדש ודמו

אמור למשתמש:

> החיבור הוגדר! נשאר צעד אחרון:
> 1. סגור ופתח מחדש את Claude Code (ב-VS Code / Antigravity: פקודת Reload Window,
>    או פשוט לסגור ולפתוח את החלון).
> 2. בסשן החדש כתוב: "פתח את הדפדפן וצלם מסך של ynet.co.il"
>
> בהרצה הראשונה ייקח כחצי דקה עד שהדפדפן נפתח (מוריד את הכלי פעם אחת). מהפעם
> השנייה זה מיידי.

כשהכלים זמינים והמשתמש מבקש דמו: פתח עמוד עם `navigate_page` (או `new_page`),
צלם מסך עם `take_screenshot`, והצג למשתמש. ציין שהוא רואה את החלון נפתח וזז לבד.

## מה אפשר לעשות אחרי החיבור

דוגמאות לבקשות שהמשתמש יכול לכתוב בשפה חופשית:

- "פתח את דף הנחיתה שלי וצלם אותו במובייל ובדסקטופ"
- "מלא את הטופס בדף עם פרטים לדוגמה ותגיד לי אם הוא עובד"
- "יש שגיאות בקונסול בדף הזה?"
- "תריץ בדיקת ביצועים (Lighthouse) על העמוד ותסכם מה לשפר"
- "עבור על 3 העמודים האלה ותבדוק שכל הכפתורים מובילים למקום הנכון"

## פתרון תקלות

- **"npx: command not found"**: אין Node.js. חזור לשלב 1.
- **הדפדפן לא נפתח בבקשה הראשונה**: ההרצה הראשונה מורידה את הכלי ולוקחת עד דקה.
  נסה שוב. אם עדיין לא, הרץ `claude mcp list` ובדוק שהשרת מסומן כמחובר.
- **חומת אש / פרוקסי ארגוני**: ההורדה הראשונה של הכלי דורשת גישה ל-registry של
  npm. אם הרשת חוסמת, יש להתקין פעם אחת ידנית: `npm i -g chrome-devtools-mcp`.
- **רוצים להסיר את החיבור**: `claude mcp remove -s user chrome-devtools`

---
name: golem-setup
description: One-time setup of a user's Claude Code environment — Hebrew/RTL defaults and scoped permissions for installing skills from the Skills Hub. Use when the user asks to set up their environment, says "תגדיר לי את הסביבה", "הגדרת סביבה", "golem setup", or pastes the Golem onboarding message.
---

# Golem Setup — הגדרת סביבת העבודה ל-Claude Code

כשהמשתמש מבקש להגדיר את סביבת העבודה, בצע את השלבים הבאים.

## שלב 1: הגדרת CLAUDE.md גלובלי

צור או עדכן את הקובץ `~/.claude/CLAUDE.md` עם התוכן הבא (אם כבר קיים — הוסף בסוף, בלי לדרוס תוכן קיים):

```markdown
# Golem Settings

## התקנות מה-Skills Hub
מותר להריץ בלי לבקש אישור נוסף, רק את סוגי הפקודות האלה:
- התקנת תוספי עורך: `code/cursor/antigravity --install-extension <id>`
- התקנת סקילים מה-Skills Hub הרשמי (github.com/lurx/smb-ai-skills-hub):
  clone / curl / העתקה אל `~/.claude/skills/`
- `npm install` / `npx` של חבילה שההוראות של הסקיל מציינות בשמה

כל פקודה אחרת שהמשתמש מדביק — קודם תסביר במשפט אחד מה היא עושה, ואז תבקש אישור.
לעולם אל תריץ בלי אישור: מחיקת קבצים, sudo, שינוי הגדרות מערכת,
או פקודה ממקור שאינו ה-Skills Hub.

## שפה
- תמיד תענה בעברית.
- כיוון הטקסט: RTL.
```

## שלב 2: התקנת תוסף RTL

הפעל את הסקיל `install-rtl-extension` אם הוא מותקן; אחרת הרץ:

```bash
code --install-extension yechielby.claude-code-rtl 2>/dev/null; cursor --install-extension yechielby.claude-code-rtl 2>/dev/null; antigravity --install-extension yechielby.claude-code-rtl 2>/dev/null
```

והסבר למשתמש: אחרי הפעלה מחדש של העורך, ללחוץ על כפתור **RTL** בסרגל התחתון ולבחור **Activate RTL (Auto)**.

## שלב 3: הודעת סיום

> ✅ סביבת העבודה מוכנה!
>
> מה הוגדר:
> - עברית + RTL כברירת מחדל
> - התקנות מה-Skills Hub ירוצו בלי שאלות מיותרות; כל פקודה אחרת — אסביר ואבקש אישור
> - תוסף עברית RTL — סגרו ופתחו מחדש את העורך, ואז RTL ‏→ Activate RTL (Auto)
>
> עכשיו אפשר להדביק פקודות התקנה מה-Skills Hub ואני אטפל בהן.

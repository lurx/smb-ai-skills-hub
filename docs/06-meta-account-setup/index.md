---
title: "התקנת חשבון Meta"
description: "מדריך לחיבור חשבון Meta לקלוד קוד לניהול מודעות"
order: 55
---

## חיבור Meta Ads

חיבור חשבון המטא ל-Claude Code - שליפת נתוני קמפיינים ישירות מהטרמינל.

## יצירת אפליקציה של מפתח מטה

- נכנסים ל-developers.facebook.com/apps
- מתחברים עם החשבון פייסבוק:

![06-meta-account-setup התחברות עם פייסבוק](./img-000.png)

נרשמים בתור המפתחים של Meta

![06-meta-account-setup הרשמה למפתחים](./img-001.png)

אחרי הזנת פרטים אישיים, בוחרים כאן Developer

![06-meta-account-setup בחירת תפקיד Developer](./img-002.png)

- לוחצים Create App

![06-meta-account-setup מסך Apps](./img-003.png)

![06-meta-account-setup חלון יצירת אפליקציה](./img-004.png)

- שם: למשל Workshop

![06-meta-account-setup פרטי האפליקציה](./img-005.png)

- בתפריט Use Cases בוחרים Create & manage ads

![06-meta-account-setup בחירת Use Cases](./img-006.png)

- מחברים את ה-Business Portfolio
- ממשיכים עם ההוראות של Meta
- יוצרים את האפליקציה

## הרשאות אפליקציה

לוחצים על Use Cases
ואז על Customize תחת ה-Instagram

![06-meta-account-setup תפריט Use Cases](./img-007.png)

![06-meta-account-setup כפתור Customize](./img-008.png)

למי שבעברית אז "מקרי שימוש"

![06-meta-account-setup התפריט בעברית](./img-009.png)

כאן לוחצים על API setup with Instagram Login

ואז על הכפתור הכחול Add all required permissions

![06-meta-account-setup הגדרת Instagram API](./img-010.png)

ואז לוחצים על

![06-meta-account-setup Permissions and features](./img-011.png)

ומחפשים את:

instagram_basic
instagram_manage_insights

ולוחצים בניהם + Add to App

![06-meta-account-setup הוספת הרשאות](./img-012.png)

## יצירת Token

- נכנסים ל-developers.facebook.com/tools/explorer
- בתפריט Get Token:
  בוחרים Get Page Access Token

![06-meta-account-setup Graph API Explorer](./img-013.png)

![06-meta-account-setup בחירת Get Page Access Token](./img-014.png)

- לוחצים Generate token
- בוחרים את האפליקציה
- מסמנים:

![06-meta-account-setup סימון הרשאות](./img-015.png)

- לוחצים Generate Access Token

![06-meta-account-setup יצירת הטוקן](./img-016.png)

- מעתיקים את הטוקן!

## חיבור ל-Claude Code

כותבים לקלוד קוד (מחליפים YOUR_TOKEN בטוקן שלכם):

```text
חבר אותי לחשבון המטה באמצעות ה-mcp עם ה-token הזה: YOUR_TOKEN
```

## בדיקה

מפעילים מחדש את Claude Code ושואלים:

```text
תראה לי את החשבונות מודעות שלי
```

- אם מקבלים רשימת חשבונות - הכל עובד!

## קישור לדשבורד של יהב

<https://github.com/dangogit/ads-dashboard-template.git>

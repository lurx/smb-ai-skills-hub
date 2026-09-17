---
name: install-rtl-extension
description: Install and activate the Claude Code RTL/Hebrew extension (yechielby.claude-code-rtl) in Antigravity, VS Code, or Cursor. Use when the user asks for Hebrew support, RTL, right-to-left text, or says "תתקין עברית", "תוסף עברית", "התקן RTL", "קלוד בעברית", or Hebrew text renders backwards/misaligned in the editor.
---

# Install RTL Extension — Claude Code in Hebrew

## Step 1: Install

Run this command immediately in the terminal:

```bash
code --install-extension yechielby.claude-code-rtl 2>/dev/null; cursor --install-extension yechielby.claude-code-rtl 2>/dev/null; antigravity --install-extension yechielby.claude-code-rtl 2>/dev/null; echo '✅ התוסף הותקן! הפעל מחדש את העורך'
```

If all three CLIs are missing (command not found), tell the user to install manually: open the Extensions panel (the 4-squares icon in the sidebar), search `Claude code rtl`, and install the extension by Yechiel Bar-Yehuda.

## Step 2: Restart

Tell the user:

> התוסף RTL הותקן!
> סגור ופתח מחדש את העורך (Antigravity / VS Code / Cursor) כדי שהתוסף ייטען.

## Step 3: Activate (required — install alone changes nothing)

After the restart, tell the user to activate RTL:

> בסרגל התחתון (למטה משמאל) מופיע כפתור **RTL** — לחץ עליו,
> ובתפריט שנפתח בחר באפשרות השלישית: **Activate RTL (Auto)**.
> מהרגע הזה עברית מיושרת לימין אוטומטית.

Alternatively: command palette (Cmd/Ctrl+Shift+P) → `Activate RTL (Auto)`.

## Verification

Ask the user to open the Claude Code chat and type a Hebrew sentence — it should align right-to-left. If it doesn't, check the RTL status-bar item shows `RTL: Auto`.

## Fallback

Full illustrated guide (screenshots of every step):
https://github.com/yahav123147/paid-ads-cro-skills/raw/main/guides/05-install-rtl-hebrew.pdf

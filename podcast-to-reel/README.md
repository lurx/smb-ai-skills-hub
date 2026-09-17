# podcast-to-reel

סקיל להפיכת קטע מפודקאסט מוקלט (מסך מפוצל / זום) לרילס פורטרט עם כתוביות
קינטיות בעברית.

---

## התקנה אצל מישהו אחר

```bash
# להעביר את התיקייה כמו שהיא
cp -r podcast-to-reel ~/.claude/skills/

# תלויות
pip3 install --user imageio-ffmpeg numpy mlx-whisper
```

זהו. הסקיל יופיע ברשימת הסקילים בפעם הבאה שנפתח סשן.

**אין צורך ב-brew ואין צורך להתקין ffmpeg** — הוא מגיע דרך `imageio_ffmpeg`.
`mlx-whisper` דורש Apple Silicon; על מכונה אחרת להחליף ל-`openai-whisper`.

### לשיתוף

```bash
cd ~/.claude/skills && zip -r podcast-to-reel.zip podcast-to-reel
```

---

## מה יש כאן

| | |
|---|---|
| `SKILL.md` | נקודת הכניסה — התהליך משלב 0 עד רינדור |
| `rules/01-verify-first.md` | חמישה דברים לאמת לפני שנוגעים בעריכה |
| `rules/02-cutting.md` | חיתוך לפי נושא, נקודות חיבור, ג׳אמפ־קאט |
| `rules/03-captions.md` | טיפוגרפיה, צבעים, מבנה בלוק, מלכודות |
| `rules/04-checks.md` | מה כל בדיקה תופסת — ובעיקר מה לא |
| `scripts/` | חמישה כלים, כולם עצמאיים |
| `template/` | שלד פרויקט Remotion — קומפוננטות, טיפוסים, 43 בדיקות |

---

## הכלים

```bash
python3 scripts/detect-layout.py <master.mp4> [שנייה]
```
מזהה גבולות letterbox ואת עמודת התפר בין האריחים. מחזיר פקודות `crop` מוכנות
ואומר אם ההגדלה הנדרשת סבירה.

```bash
python3 scripts/identify-speaker.py <clip.mp4>
```
מי מדבר, לפי תדר יסוד, ברזולוציה של שנייה. מזהה קליפ מעורב ומתריע אם הוא
**נפתח** בדובר המשני.

```bash
./scripts/prepare-source.sh <master> <out> <start> <dur> <crop> <scale>
```
חיתוך מהמאסטר + קרופ + סקייל.

```bash
python3 scripts/check-cuts.py [מספר-רילס]
```
נופל אם נקודת חיתוך כלשהי נוחתת בתוך מילה. **להריץ מתיקיית הפרויקט.**

```bash
python3 scripts/serve.py [פורט] [תיקייה]
```
שרת סטטי עם תמיכה ב-Range. `python3 -m http.server` מחזיר `200` במקום `206`
וספארי לא מנגן את האודיו.

---

## התחלת פרויקט חדש

```bash
mkdir my-reels && cd my-reels
cp -r ~/.claude/skills/podcast-to-reel/template/. .
cp ~/.claude/skills/podcast-to-reel/scripts/*.py scripts/
npm install
```

ואז לפי `SKILL.md`.

---

## מקור

נבנה מפרויקט אמיתי — שני רילסים מפודקאסט של TNL, יולי 2026. כל בדיקה כאן
נולדה מתקלה ספציפית באותו פרויקט. שתיהן החמורות ביותר נתפסו **בהאזנה של
הלקוחה**, אחרי שכל הבדיקות היו ירוקות:

- כתוביות שהציגו טקסט שלא נשמע
- עיצור סופי שנקטע — ״השיווק״ שודר כ״השיוו״

לכן `SKILL.md` חוזר על זה: **בדיקות ירוקות אינן אישור. להאזין.**

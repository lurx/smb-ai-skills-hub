# podcast-episode-edit: התחלה מהירה

עריכה אוטומטית של פרק פודקאסט שצולם בשתי מצלמות (מארח + אורח): סנכרון, חיתוך לפי מי שמדבר, ספליט-סקרין, פתיח/סגיר, רילסים, כתוביות, לואר ת'ירד.

## 1. התקנה (פעם אחת)

```bash
# ffmpeg + ffprobe
brew install ffmpeg            # Mac
# sudo apt install ffmpeg      # Linux

# ספריות פייתון (Python 3.9+)
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

# מפתח OpenAI לתמלול (Whisper). רק משתנה סביבה, לא נשמר בשום קובץ
export OPENAI_API_KEY=sk-...
```

פונט לכתוביות: התקן פונט עברי בולט (למשל Secular One מ-Google Fonts) וכתוב את שמו ב-`fonts.caption_font_name`. ללואר ת'ירד נדרש נתיב לקובץ `.ttf` ב-`lower_third.font_path`.

## 2. הכנת פרויקט

```
my-episode/
  config.json        <- העתק מ-config.example.json ומלא
  hooks.json         <- נכתב אחרי שלב 07 (ראה hooks.example.json)
  fixes.json         <- אופציונלי, תיקוני תמלול (ראה fixes.example.json)
  raw/host_cam.mp4
  raw/guest_cam.mp4
  assets/intro.mp3, outro.mp3, font.ttf   <- אופציונלי
  work/              <- נוצר אוטומטית, כל קבצי הביניים
```

חובה למלא ב-`config.json`:
- `cameras.host.path`, `cameras.guest.path`
- `mic_cam`: איזו מצלמה הקליטה את המיקרופון הטוב
- `face_roi` לכל מצלמה: מלבן (בשברים של הפריים) שמכיל את הפנים של הדובר. אפשר לבדוק עם `ffmpeg -ss 600 -i raw/host_cam.mp4 -frames:v 1 sample.jpg`
- `encoder.video_codec`: `h264_videotoolbox` במק, `libx264` בכל מחשב אחר

## 3. הרצה

```bash
cd my-episode
bash /path/to/podcast-episode-edit/scripts/run_all.sh --config config.json
```

הצינור עוצר אחרי שלב 07 ומבקש `hooks.json`:
1. פתח `work/guest_text.txt`, בחר 5-10 רגעים חזקים של 15-50 שניות.
2. כתוב `hooks.json`: `[{"slug": "01_name", "start": 120.5, "end": 152.0}, ...]` (שניות מתחילת הפרק).
3. `bash run_all.sh --config config.json --from 8`

תוצרים: `work/final.mp4` (פרק), `work/reels/*.mp4` (רילסים), `work/full_subs.ass`, `work/lower_third.png`.

## 4. הרצת שלב בודד / דיבוג

```bash
python3 scripts/02_trim.py --config config.json       # כל סקריפט: --help
bash run_all.sh --config config.json --from 9 --to 11  # רק רינדור + קונקט
python3 scripts/12_render_reels.py --config config.json --only 01_name --no-subs
python3 scripts/09_render_body.py --config config.json --dry-run   # רק כותב body_filter.txt
```

כל שלב בודק שקבצי הקלט של השלב הקודם קיימים ומדפיס איזה שלב להריץ אם חסר. פירוט מלא ב-`references/pipeline.md`.

## זמני ריצה (שעה של 4K, Mac M-series)
| שלב | זמן |
|---|---|
| 00-04 | דקות בודדות |
| 05 proxies | 10-15 דק' |
| 06 whisper | 3-6 דק' |
| 09 body | 1-2 שעות |
| 12 reels | 1-2 דק' לרילס |

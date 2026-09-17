# אנליטיקס + בטיחות ליד

## מודל `funnel_events`

מדידה עצמאית, בלתי תלויה בפיקסל. `lib/analytics.ts` שולח דרך `sendBeacon` ל-`/api/track` שכותב לטבלה `funnel_events` (Supabase או כל DB אחר).

**סכימה:** `session_id` (טקסט, מ-sessionStorage `<brand>_funnel_sid`), `event` (טקסט), `step` (טקסט/null), `step_index` (מספר/null), `props` (jsonb/null), `created_at`.

**אירועים (whitelist ב-track route):**
| event | מתי | props |
|---|---|---|
| `session_start` | טעינת הפאנל | — |
| `step_view` | כל מסך | `step`, `step_index` |
| `lead_submit` | שליחת טופס | — |
| `whatsapp_click` | קליק על וואטסאפ | — |
| `reservation_click` | קליק על שריון | `value`, `currency` |
| `reservation_complete` | תשלום הצליח (thank-you) | `phone`, `name` |

**חיווט:** `session_start` ב-`Funnel.tsx` mount; `step_view` בכל שינוי step; `lead_submit` ב-`LeadCapture`; הקליקים ב-`PriceReveal`; `reservation_complete` ב-`thank-you/page.tsx` עם identity מ-localStorage.

## סקריפט ניתוח הנטישה

מזהה בדיוק איפה נוטשים. הרץ `npx tsx scripts/_funnel.ts` אחרי 3-4 ימי תנועה.

```ts
// scripts/_funnel.ts
import { createClient } from "@supabase/supabase-js"; import WebSocket from "ws";
const db = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!,
  { auth:{persistSession:false}, realtime:{transport: WebSocket as unknown as typeof globalThis.WebSocket}});
type Row = { session_id:string; event:string; step:string|null; step_index:number|null; created_at:string };
const rows: Row[] = [];
for (let from = 0; ; from += 1000) {  // pagination — אל תסתפק ב-1000!
  const { data } = await db.from("funnel_events")
    .select("session_id,event,step,step_index,created_at")
    .order("created_at",{ascending:true}).range(from, from+999);
  rows.push(...(data as Row[] ?? [])); if (!data || data.length < 1000) break;
}
function funnel(rws: Row[], label: string) {
  const sess = new Set(rws.filter(r=>r.event==="session_start").map(r=>r.session_id)).size;
  const stepS: Record<string,Set<string>> = {}, idx: Record<string,number> = {};
  for (const r of rws) if (r.event==="step_view" && r.step) { (stepS[r.step] ??= new Set()).add(r.session_id); idx[r.step]=r.step_index??99; }
  const leads = new Set(rws.filter(r=>r.event==="lead_submit").map(r=>r.session_id)).size;
  console.log(`\n### ${label}: sessions ${sess} | leads ${leads} (${sess?Math.round(leads/sess*100):0}%)`);
  let prev = sess;
  for (const st of Object.keys(stepS).sort((a,b)=>idx[a]-idx[b])) {
    const n = stepS[st].size;
    console.log(`  [${String(idx[st]).padStart(2)}] ${st.padEnd(16)} ${String(n).padStart(4)} (${Math.round(n/Math.max(sess,1)*100)}%, נטישה ${prev?Math.round((1-n/prev)*100):0}%)`);
    prev = n;
  }
}
funnel(rows, "סה\"כ");
const wk = Date.parse("2026-07-06T14:00:00Z"); // תאריך שינוי — להשוואת לפני/אחרי
funnel(rows.filter(r=>Date.parse(r.created_at)<wk), "לפני");
funnel(rows.filter(r=>Date.parse(r.created_at)>=wk), "אחרי");
process.exit(0);
```

**מה מחפשים:** הצניחה הגדולה בין שלבים (איפה מאבדים); ההמרה הכוללת; השוואת לפני/אחרי שינוי. וגם — הצלבת תשובות מול תוצאה (אילו תשובות → לידים חמים שסוגרים), לכיוונון ניקוד וטירגוט מודעות.

## ⚠️ בטיחות ליד — חוקי ברזל ב-`lead-intake/route.ts`

הכלל שאסור לשבור: **השרת לעולם לא מודיע ללקוח. רק לבעל העסק.**

1. **`normalizeIsraeliPhone` → E.164.** לא תקין → `phone_valid:false`, והמערכת במורד הזרם **חסומה מלהשתמש בו לשליחה**.
2. ה-route **only-notify-owner** — מעביר payload לבעל העסק (CRM/התראה), אף פעם לא הודעה ללקוח.
3. ההעברה **best-effort** — כשל נרשם, לא חוסם את מסך החגיגה/הוואטסאפ ללקוח.
4. **anti-spam:** honeypot (שדה נסתר שחייב להישאר ריק) + rate-limit per-IP (6/דקה).
5. **הפרדת אחריות:** הפאנל *לוכד* ליד. *השליחה* ללקוח קורית רק במערכת נפרדת, ורק אחרי אישור בעל העסק. שני העקרונות האלה חייבים להישמר יחד: פאנל שמעביר לטבלת `funnel_leads`, ומערכת שמושכת משם ומאשרת לפני כל שליחה.

## היעדים (איפה הליד נוחת)

- **טבלת `funnel_leads`** — מקור אמת פנימי, ממנו מנקדים ומאשרים.
- **רשימת דיוור** (אופציונלי) — לנרצ'ר של מי שלא סגר.
- **ספק תשלומים** — שריון בתשלום (משני).

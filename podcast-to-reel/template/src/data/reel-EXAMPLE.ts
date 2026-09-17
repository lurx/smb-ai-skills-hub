import type {ReelConfig} from './types';

/**
 * רילס 05 — "להבין מרקטינג זה כוח על" · יהב
 *
 * Speaker verified by F0: 123.1 Hz median, 46 of 51 seconds male.
 *
 * THE CUT. He wanders, so the raw 51s is edited down to 32.5s along one
 * thread — claim, failures, payoff. Two passages are removed:
 *
 *   10.9–27.45s "I received it over a decade ago… full control… such peace of
 *               mind" — a detour that pushes the failures list, the actual
 *               hook, all the way out to 27s. It also swallows the dangling
 *               "כי לפני זה" (a causal link back to a sentence that no longer
 *               exists) and the filler "אני, תדע".
 *   40.17–42.9s "ותרגלתי אותם, והטמעתי אותם בתוך ה-DNA שלי" — he already said
 *               "והטמעתי אותם" three seconds earlier.
 *
 * Every boundary sits in measured silence, not on a transcript timestamp —
 * whisper's word times drift tens of milliseconds and three of these cuts
 * originally landed mid-word. `scripts/check-cuts.py` enforces it.
 *   "…כסף מכל מקום בעולם"        -> "הייתי שליח…"             (claim to contrast)
 *   "…והטמעתי אותם בתוך המוח שלי" -> "פתאום כל פעולה… מצליחה"  (cause to effect)
 *
 * Caption corrections confirmed by Yahav, 21.7.26:
 *   "איך השפע ושכנוע עובד"     -> "איך השפעה ושכנוע עובדים"
 *   "מכל מוגעון בעולם"          -> "מכל מקום בעולם"
 *   "במד ההכנסה שלי"            -> "בקצב ההכנסה שלי"   (in a cut passage)
 *   "כי אני מה שיודע מה לעשות"  -> "כי אני יודע מה לעשות" (in a cut passage)
 *   "והטמתי"                    -> "והטמעתי"
 *   "וניסתי"                    -> "וניסיתי"
 *   "של השיוור"                 -> "של השיווק"
 *
 * The failures list here is richer than the production doc's: it opens with
 * "הייתי שליח", which that doc omits.
 */
export const REEL_EXAMPLE: ReelConfig = {
  id: 'ReelExample',
  source: 'source-example.mp4',
  cardHeight: 582,
  // The salad bar plus the admission.
  //
  // The end is 35.69, which is doing two jobs. Audio: the measured silence
  // between words runs 35.62-35.94 (rms bottoms out at 0.0006), so nothing is
  // clipped — the original 36.0 landed mid-word. Captions: the next line is
  // stamped 35.7, so ending just before it keeps that line off screen. At 35.75
  // it still appeared, ghosted, for speech the viewer never hears.
  //
  // Stopping on "נכשלתי הרבה" also leaves the "why" hanging, which is the job
  // of a hook.
  coldOpen: {start: 33.7, end: 35.69},
  body: [
    {start: 0.0, end: 10.9}, // the claim: marketing is a superpower
    {start: 27.45, end: 40.17}, // the failures, and learning the rules
    {start: 42.9, end: 51.29}, // the payoff: now everything works
  ],
  warmth: {from: 35.5, to: 39.0},
  beats: [
    // ---- segment 1: the claim ----
    {
      end: 1.5,
      lines: [
        {t: 0.0, text: 'אני אגיד לך את האמת', style: 'plain'},
        {t: 0.7, text: 'אני חושב שהמקום הזה', style: 'plain'},
      ],
    },
    {
      end: 3.0,
      lines: [
        {t: 1.5, text: 'של בעל עסק', style: 'plain'},
        {t: 2.2, text: 'שלומד מרקטינג', style: 'plain'},
      ],
    },
    {
      end: 3.7,
      lines: [{t: 3.0, text: 'זה כוח על', style: 'gold'}],
    },
    {
      end: 6.0,
      lines: [
        {t: 3.7, text: 'כי ברגע שאתה יודע', style: 'plain'},
        {t: 4.8, text: 'איך המוח האנושי עובד', style: 'plain'},
      ],
    },
    {
      end: 7.2,
      lines: [
        {t: 6.0, text: 'איך השפעה ושכנוע', style: 'plain'},
        {t: 6.8, text: 'עובדים', style: 'plain'},
      ],
    },
    {
      end: 8.8,
      lines: [
        {t: 7.2, text: 'אתה מבין את', style: 'plain'},
        {t: 7.5, text: 'העקרונות של השיווק', style: 'plain'},
      ],
    },
    {
      end: 10.9,
      lines: [
        {t: 8.8, text: 'יש לך כוח על', style: 'gold'},
        {t: 9.6, text: 'אתה יכול להכניס כסף', style: 'plain'},
        {t: 10.2, text: 'מכל מקום בעולם', style: 'plain'},
      ],
    },

    // ---- CUT 10.9 -> 26.6 ----

    // ---- segment 2: the failures ----
    {
      end: 28.4,
      lines: [{t: 27.45, text: 'הייתי שליח', style: 'plain'}],
    },
    {
      end: 30.3,
      lines: [
        {t: 28.4, text: 'והייתי מדריך', style: 'plain'},
        {t: 29.0, text: 'חדר כושר', style: 'plain'},
      ],
    },
    {
      end: 31.6,
      lines: [{t: 30.3, text: 'ולמדתי NLP', style: 'plain'}],
    },
    {
      end: 33.1,
      lines: [
        {t: 31.6, text: 'והבאתי מוצרים', style: 'plain'},
        {t: 32.3, text: 'מאמזון', style: 'plain'},
      ],
    },
    {
      end: 34.4,
      lines: [
        {t: 33.1, text: 'וניסיתי לפתוח', style: 'plain'},
        {t: 33.7, text: 'בר סלטים', style: 'plain'},
      ],
    },
    {
      end: 36.9,
      lines: [
        {t: 34.4, text: 'וכל כך נכשלתי הרבה', style: 'red'},
        {t: 35.7, text: 'כי לא הכרתי', style: 'plain'},
        {t: 36.4, text: 'את החוקים', style: 'plain'},
      ],
    },
    {
      end: 38.0,
      lines: [
        {t: 36.9, text: 'וברגע שהכרתי', style: 'plain'},
        {t: 37.6, text: 'את החוקים', style: 'plain'},
      ],
    },
    {
      end: 40.17,
      lines: [
        {t: 38.0, text: 'והטמעתי אותם', style: 'plain'},
        {t: 38.7, text: 'בתוך המוח שלי', style: 'plain'},
      ],
    },

    // ---- CUT 39.9 -> 42.9 ----

    // ---- segment 3: the payoff ----
    {
      end: 44.8,
      lines: [
        {t: 42.9, text: 'פתאום כל פעולה', style: 'plain'},
        {t: 43.7, text: 'שאני עושה מצליחה', style: 'gold'},
      ],
    },
    {
      end: 47.2,
      lines: [
        {t: 44.8, text: 'כי אני מבין', style: 'plain'},
        {t: 45.5, text: 'איך המשחק עובד', style: 'plain'},
      ],
    },
    {
      // 51.29, not 51.20. "השיווק" ends in a stop consonant: vowel to 51.15,
      // silent closure 51.16-51.21, release burst 51.22-51.25, decay to 51.29.
      // Cutting in the closure produced an audible "השיוו".
      end: 51.29,
      lines: [
        {t: 47.2, text: 'ויש חוקים', style: 'plain'},
        {t: 47.7, text: 'למשחק הזה', style: 'plain'},
        {t: 48.7, text: 'של העסקים ושל השיווק', style: 'gold'},
      ],
    },
  ],
};

---
name: blog-style
description: >
  Learn an author's writing style from 5 to 10 existing blog posts and generate
  a structured voice profile, written to the project's VOICE.md file. Use when
  users ask to infer tone, analyze author voice, learn style, build a writing
  baseline, or say "learn my style", "voice profile", "analyze my writing",
  "תלמד את סגנון הכתיבה שלי", "ניתוח סגנון".
user-invokable: true
license: MIT
---

# Blog Style - Writing Style Learning

Learn an author voice profile from existing posts and use it as a durable
baseline in the project's `VOICE.md` file. The profile captures measurable
style signals so future drafts can preserve the author's cadence, vocabulary,
and tone. Other tools (such as the blog-persona skill) can read `VOICE.md` to
seed their settings.

## Learn Workflow

Use 5 to 10 representative posts from the same author, brand, or editorial
voice. Accept individual markdown files, MDX files, text files, or a directory
containing posts. If fewer than 5 posts are supplied, warn that the profile may
be less stable and continue.

Claude performs the analysis directly — no script is involved:

1. **Read every sample post** in full. Strip frontmatter, code blocks, raw
   HTML/JSX, and image/link URLs before measuring; keep the visible prose.
2. **Segment sentences and paragraphs.** For Hebrew posts, compute all metrics
   on the Hebrew text itself; sentence segmentation by Hebrew punctuation
   (. ! ? and the sof pasuq-style period usage) is fine.
3. **Measure, per post and aggregated across the corpus:**
   - Sentence-length distribution: percentage of short (under 10 words),
     medium (10-20 words), and long (over 20 words) sentences, plus mean and
     median words per sentence
   - Average paragraph length in sentences and in words
   - Vocabulary tier: consumer, professional, or technical, judged from word
     choice, jargon density, and assumed reader knowledge
   - Contraction and colloquialism frequency (rare / occasional / frequent,
     with an approximate rate per 100 sentences; for Hebrew, count slang and
     spoken-register forms instead of contractions)
   - First-person usage rate and heading-as-question ratio
   - Passive-voice sentence rate
4. **Place the voice on the NNGroup 4 tone dimensions**, each as a 0.0-1.0
   value with a one-line justification quoting evidence from the samples:
   - funny_serious (0.0 funny, 1.0 serious)
   - formal_casual (0.0 formal, 1.0 casual)
   - respectful_irreverent (0.0 respectful, 1.0 irreverent)
   - enthusiastic_matter_of_fact (0.0 enthusiastic, 1.0 matter-of-fact)
5. **Collect signature elements:** recurring phrases (2-3 word content
   phrases, stopwords removed), characteristic openers (how posts and sections
   tend to begin), and characteristic closers (how posts tend to end).
6. **Emit the profile block below** and write it to the project's `VOICE.md`
   (append or replace the existing profile block after asking the user).

## VOICE.md Profile Block

```markdown
# Voice Profile

Learned from: [N] posts ([list of files]), [date]
Language: [English / Hebrew / mixed]

## Sentence & Paragraph Rhythm
- Sentence length: [x]% short (<10w), [y]% medium (10-20w), [z]% long (>20w)
- Mean sentence length: [n] words (median [m])
- Average paragraph: [n] sentences / [m] words

## Vocabulary & Register
- Vocabulary tier: [consumer | professional | technical]
- Contractions/colloquialisms: [rare | occasional | frequent] (~[n] per 100 sentences)
- Passive voice: [n]% of sentences
- First person: [rate]; question headings: [ratio]

## Tone (NNGroup dimensions, 0.0-1.0)
- funny_serious: [v] — [evidence]
- formal_casual: [v] — [evidence]
- respectful_irreverent: [v] — [evidence]
- enthusiastic_matter_of_fact: [v] — [evidence]

## Signature Elements
- Phrases: [list]
- Openers: [description + examples]
- Closers: [description + examples]

## Drafting Guidance
- [3-6 concrete rules derived from the metrics above]
```

## Consuming the Profile

When writing or editing posts with the profile available:

- Keep average sentence length near the learned mean and match the learned
  short/medium/long mix unless the user asks for a tighter or looser cadence.
- Preserve signature phrases only when they fit the topic naturally.
- Use the first-person and heading-question rates to decide how personal and
  question-led the draft should feel.
- The blog-persona skill can read `VOICE.md` to seed a structured persona:
  map the learned values to persona sentence length, passive voice,
  vocabulary, and tone settings.

## Error Handling

- **Too few posts**: Continue and warn that the profile may be less stable.
- **Missing paths**: Skip missing paths and include a warning in the profile.
- **Unsupported files**: Skip unsupported file types and include a warning.
- **Empty samples**: Note the empty file and exclude it from the metrics.

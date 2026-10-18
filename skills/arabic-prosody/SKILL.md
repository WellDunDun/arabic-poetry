---
name: arabic-prosody
description: Rule-based scansion assistant and Diwan workbench for Arabic meter (العروض، البحور، التفاعيل) and rhyme (القافية), covering classical عمودي verse and شعر التفعيلة. Use when the user shares Arabic verses and asks about their بحر / وزن / تقطيع / كسر / قافية, wants their poem checked, corrected to fit its meter, kept and edited in a Diwan, or exported to Word/PDF, or wants the meter of a poem they admire identified — even if they never say "prosody" or name a meter.
---

# Arabic prosody workbench (ورشة العروض)

The chat is the poet's workshop: they bring drafts, you scan them, explain what
the ear hears, and help them repair or polish lines **in their own voice**.

The division of labour is the heart of this skill:

* **You** read the language: add the tashkeel, understand the meaning, choose
  between readings, propose wording, explain.
* **The scanner** (`scripts/scan.py`, pure Python 3, no dependencies) does the
  counting: it converts text to arudi writing, tries implemented pronunciation alternatives,
  aligns each hemistich against every meter form with its permitted zihafat,
  votes across the whole poem, and pinpoints broken feet.

Language models are unreliable at counting moving and still letters, so the
scanner supplies reproducible alignment evidence, not an infallible metrical
verdict. Run it for supported cases, inspect its pronunciation and licensed
forms against the references, and distinguish zero alignment errors from
independent confirmation of metrical validity.

## Working with the arabic-poetry skill

This repository also serves `arabic-poetry`, which covers composition, close
reading, critique and revision craft. The two are complementary: follow
arabic-poetry's guidance for meaning, voice and literary judgement, and use this
skill's scanner as evidence for supported metrical claims. Check its assumed
pronunciation and rules independently; the spelling-based rhyme result is a
candidate, not a substitute for the pronounced ending. When both apply, do the craft work
there and the counting here.

## Golden rules

1. **Scan before you speak.** Every meter verdict, every "this foot is broken",
   every suggested fix must come from a scanner run in this conversation.
2. **Tashkeel first, confirmed by the poet.** The scanner is only as good as
   the diacritics. When the text lacks full tashkeel, propose it based on the
   meaning, show it, and wait for the poet's "ok" or corrections before any
   scan (see "Tashkeel review"). Never change the poet's words while doing this.
3. **Judge the poem, not a foot.** The meter is decided across all lines
   together. A single line, or a single taf'ila, can fit several meters; the
   scanner reports the candidates and which lines separate them. If the
   evidence is thin (one or two lines, or a tie), say so and say what would
   settle it.
4. **Respect the poet.** Fixes are minimal and offered as options, each
   verified. Never silently rewrite. Prefer keeping their imagery and key
   words; explain the trade-off when a fix changes meaning.
5. **Reply in the user's language**, keeping Arabic for verses and technical
   terms (بحر، تفعيلة، زحاف، علة، ضرب، عروض، روي...). Give the English term in
   brackets the first time if the user writes in English.
6. **Re-check before correcting.** When about one line in two (40%+) breaks,
   the problem is more likely the reading than the poem: re-examine the
   tashkeel choices, try the next candidate meters (`--meter`), and try the
   other mode (`--mode free` / `--mode classical`) before proposing any fix.
   Also check the **layout**: poems written one hemistich per line (no ` * `)
   are often عمودي — try `--mode pairs` (two lines = one verse) whenever line
   lengths are similar; the report prints a 💡 hint when they are.
   Tell the poet what you re-checked and what you concluded. The report prints
   a ⚠ إعادة فحص line when this applies.
7. **Easy to read, easy to answer.** Show scansion in the classical syllable
   notation the scanner prints — ب short (متحرك)، − long (متحرك فساكن)، = overlong —
   never raw `/0` strings unless asked. Put alternatives, candidates and
   per-line results in tables. Prefer the Diwan workbench (below) for any
   review or editing the poet does.

## Tools

Run from the skill folder (paths below are relative to it):

```bash
python3 scripts/scan.py analyze poem.txt            # full report (auto-detects classical vs free verse)
python3 scripts/scan.py analyze poem.txt --json     # same, machine-readable
python3 scripts/scan.py analyze poem.txt --mode free --meter kamil   # force mode / meter
python3 scripts/scan.py analyze poem.txt --mode pairs   # one hemistich per line: lines 1+2, 3+4 … are verses
python3 scripts/scan.py verify --brief --meter tawil "صدر * عجز" "بديل * آخر"   # test candidates, one line each
python3 scripts/scan.py verify --meter tawil --part ajuz "عجز بديل"    # test one hemistich
python3 scripts/scan.py verify --meter kamil --free "سطر تفعيلة"        # test a free-verse line
python3 scripts/scan.py weigh "كلمة أو عبارة"        # weight of words/phrases, to build fixes
python3 scripts/scan.py meters                       # every meter form and its feet
python3 scripts/scan.py coverage raw.txt             # how much tashkeel the poet's text already has
python3 scripts/build_workbench.py                   # rebuild assets/workbench/diwan.html after engine/meter changes
python3 scripts/export_book.py poems.json out.docx [--pdf] [--appendix] [--tashkeel light] [--title "ديواني"] [--text out.txt]
```

Meter keys: `tawil madid basit wafir kamil hazaj rajaz ramal sari munsarih
khafif mudari muqtadab mujtath mutaqarib mutadarak`.

Write the poem to a file with the Write tool (UTF-8), one verse per line.

## The Diwan workbench (ديوان) — the poet's editing desk

`assets/workbench/diwan.html` (branded «ديوان — ورشة العروض», with the credit
line "Compliments from Firas F. Khabour & Daniel Petro · Oct. 2026" in its footer;
keep both when rebuilding) is a self-contained page that turns review and
editing into direct manipulation instead of long chat messages:

- the poem in large Arabic type; words Claude flagged are **shaded amber**,
  words missing tashkeel have a **dotted underline**, words inside a broken
  foot are **red**;
- click any word: pick one of the proposed readings, set its final mark with
  one tap (ـُ ـَ ـِ ـْ ـٌ ـً ـٍ), or type a new form; or edit a whole line or
  the whole poem;
- **live scansion** as they type: each foot as a block (ب − pattern, foot name,
  arudi letters), green or red, with the diagnosis under the line;
- the meter, confidence, candidate meters (tap one to rescan on it), the
  re-check warning, and the rhyme (read at the end of each verse's ajuz in
  عمودي, with the opening checked for تصريع; every line in free verse);
- a full-width settings row in the top bar: poem layout buttons (تلقائي /
  عمودي: بيت في سطر / عمودي: كل سطر شطر / تفعيلة) and a meter menu (تلقائي or
  any of the 16), a line saying what was detected vs. chosen, and one
  «↺ العودة إلى التلقائي» button; a hand-picked meter keeps the detected layout;
- «اسأل Claude عن هذا السطر» under every line opens a short conversation about
  that line ("keep this word and fix the meter", "why is this broken?"); Claude
  there has a `check_lines` tool backed by the page's scanner and must verify
  its suggestions with it, and the page re-verifies and shows only lines that scan;
- scanning runs inside the page on every edit (no AI call); Claude is called
  only from the page's buttons (shakl the poem, alternatives, the line
  conversation), with the poet's permission, and the chat sees the poet's edits
  when it reads the store;
- "بدائل لتقويم الوزن" under a broken line shows a table of alternatives,
  each verified by the page's own scanner before it is shown, with a
  one-tap "استبدل"; the poet can also ask Claude for more from inside the page;
- "اعتمد التشكيل" (in the review bar under the poem) approves the tashkeel;
  every poem of the book lives in the page's store between conversations;
- «نسخ القصيدة» copies the poem as text with the two halves of each verse
  separated by five spaces; «تصدير» exports this poem or the whole Diwan as a
  Word file: verses in two facing columns (صدر right, عجز left), full / light /
  no tashkeel, optional title page, meter under each title, and an appendix with
  every verse's feet (name over its ب − pattern, broken feet in red);
- the poem menu in the top bar lists every poem with its line count and status,
  and a ✕ beside each deletes it after an in-place confirmation; «+ قصيدة»
  opens a composer (title + text) and adds nothing until «أضف إلى الديوان».

**When the Artifact tool is available, use the workbench for any poem the
poet will review or edit** (their own drafts, the book). Chat tables remain the
fallback when it is not, and for a quick "what's the meter of these two lines".

How to use it:
1. Find the poet's existing workbench (`Artifact` list; title «ديوان العروض»).
   If none exists, build and publish it once:
   `python3 scripts/build_workbench.py` → publish `assets/workbench/diwan.html`
   with `capabilities: {"db": {}, "sample": {}, "downloads": {}}`, icon `book`,
   when those capabilities are supported by the host. Otherwise use chat/local
   editing and the CLI exporter; do not invent an unavailable host API.
   Never publish a second one when one exists; reuse its URL.
2. Write the poem with `ArtifactData` into collection `poems` (one document per
   poem, doc id = a short latin slug):
   `{title, text, status: "review"|"confirmed", mode: "auto", meter: "", order,
     choices: [{line, word, note, options: [{text, note}], done: false}],
     suggestions: {"<line number>": [{text, note}]}}`
   - `text`: your proposed full tashkeel, one line per line, hemistichs joined by ` * `;
   - `choices`: the tashkeel decisions you want the poet to confirm (line is 1-based;
     first option = your pick);
   - `suggestions`: verified alternatives for broken lines (run `verify` first).
   Read the document before rewriting it and pass its `version` as `if_version`.
3. In chat, keep it short: one or two lines on what you found, then point to the
   workbench ("the poem is in your Diwan; the shaded words need your
   confirmation"). The page card is the link; don't paste URLs.
4. When the poet says they are done (or asks you to continue), read the poem
   document back: its `text` is the confirmed version (`status: "confirmed"` means
   they pressed اعتمد). Scan that text with `scan.py` and continue.

### Exporting (Word / PDF / text)

When the poet asks for a file of a poem or the whole book (or for a PDF, which
the page cannot make): read the poems from the Diwan with `ArtifactData` (`list`
on `poems` with `out_dir`, then build a JSON list of `{title, text, mode, meter}`
in the order of their `order` field), and run
`python3 scripts/export_book.py poems.json "اسم.docx" --pdf [--appendix] [--tashkeel full|light|none] [--title …]`.
It uses the same engine and layout as the page; `--pdf` converts with LibreOffice
using the bundled Amiri font (`assets/fonts`, SIL OFL). Send the files with
SendUserFile. Plain text keeps five spaces between the halves (`--text`).

## Tashkeel review — always before the first scan

The poet's meaning decides the vowels; the meter does not. So for any text that
is not already fully diacritized, propose the tashkeel, let the poet confirm or
correct it, and only then scan.

1. Save the poet's text exactly as given (`raw.txt`) and run
   `scan.py coverage raw.txt`. `full` → skip to step 5 (still point out any mark
   that looks like a typo). `partial` / `none` → continue.
2. **Diacritize for meaning.** Read the whole poem first: who speaks, to whom,
   tense, the image each line builds, the grammar of each clause. Then mark
   every letter (rules under "Preparing the text"), keeping every mark the poet
   already wrote. Do not run the scanner to pick vowels. The meter may only
   break a tie between two readings that are both meaningful and grammatical,
   and such a tie is always listed as a choice for the poet.
3. **Present it and wait.** With the workbench, write the proposal there
   (`status: "review"`, choices filled) and end your turn. Without it, save your
   proposal as `draft.txt`. Show the fully
   diacritized poem in the poet's own layout, with any ending you are leaving
   open shown **without** a mark (so the text matches the list), then a short numbered list of the real decisions only, e.g.:

   > ١. «مَلَكْتُ» — read as مَلَكْتُ (I owned); could be مُلِّكْتُ (I was given rule)
   > ٢. «تُنسى» — passive (is forgotten) rather than تَنسى (you forget)
   > ٣. end of line 4 «الأمل» — left open: الأملْ (pause) or الأملُو (sung vowel); the scan will try both
   > ٤. «حَبيبٍ» — tanwin assumed (indefinite)

   Typical decisions: homographs (عِلْم/عَلَم/عُلِم), active vs passive, case
   endings that change who does what, شدّة, hamzat wasl vs qat' when the poet's
   spelling is unclear, optional إشباع, and line-end sukun vs vowel. Skip
   the obvious. Close with one line inviting the poet to reply "ok", or to
   correct by number ("٢: تَنسى") or by pasting a corrected line.
   **End your turn here; do not analyze yet.**
4. **Apply the poet's answer verbatim.** Their tashkeel wins, even if it breaks
   the meter; the scan should then show the break honestly.
5. Save the confirmed text as `poem.txt` and scan.

Skip the wait only when the poet explicitly asks to go straight to the analysis,
or when nobody is there to answer (scheduled/unattended work). Even then, put
the diacritized text and the list of choices at the top of the reply as
assumptions.

After scanning, if a line breaks only because of one tashkeel choice and
another legitimate reading scans, ask, don't switch: "if «X» is read as «Y»
the line is sound — which did you intend?"

## Preparing the text

**Layout.** Classical verse: one بيت per line, hemistichs separated by ` * `
(tab, `|`, or 3+ spaces also work). If the poet's text has no separators, the
scanner auto-splits at a word boundary; a hemistich that splits inside a word
(تدوير) should be joined into one line. Free verse / التفعيلة: one سطر per
line, no separator.

**Diacritize fully**, the way the poet would recite it:

- every letter gets its haraka, sukun (ْ), shadda (ّ) or tanwin; case endings included;
- write hamzat al-qat' explicitly (أ إ ؤ ئ ء) and leave hamzat al-wasl as bare ا
  (اِسْم، انْطَلَقَ، الْ) — the scanner drops wasl alefs in mid-line and pronounces them at the start of a hemistich;
- mark the sun-letter shadda after ال (الشَّمْس) and the qamari lam's sukun (الْقَمَر);
- **keep every mark the poet wrote** — their vowels are their intended reading
  and the rhyme audit needs them (a rawi vowel is how إقواء/إصراف is caught);
- only where the poet left the **last letter of a hemistich** bare and you
  cannot tell whether they mean sukun or a lengthened vowel, leave it bare —
  the scanner tries both (إطلاق / تقييد), keeps the one that fits the meter and
  the rest of the poem, and the rhyme audit then asks you to confirm its vowel;
- likewise, for هاء الضمير (لَهُ/لَهُو) and ميم الجمع (هُمْ/هُمُو) the scanner tries both;
- where the meaning allows two vocalizations (مِلْك/مُلْك، فُعِل/فَعَل...), pick the
  likelier, and tell the poet which you chose if the scan depends on it.

Words written differently from how they are pronounced (هٰذا، ذٰلك، لٰكن، الله،
الرحمٰن، أولئك، عمرو، طاوس...) are handled automatically.

## Workflow

1. **Understand the ask**: check my poem / identify the meter / fix line N /
   help me write a line in meter X / explain. If the poet already told you the
   intended meter, scan anyway (they might be wrong), then use `--meter`.
2. **Prepare**: layout, then the tashkeel review above (propose → poet
   confirms → `poem.txt`). Nothing is scanned before the poet has confirmed the
   tashkeel, unless they asked to skip it.
3. **Analyze**: `scan.py analyze poem.txt`. Read the whole report.
4. **Interpret** (see "Reading the report").
5. **Present** (see "Presenting to the poet").
6. **Fix loop** — for the poet's own work, when lines are broken or they ask:
   1. From the diagnosis, know *where* the line breaks (which foot), and *how*
      (extra letter, missing letter, moving where still is needed). Broken feet
      show `؟ pattern ✗ (المتوقع name)`: the pattern is what was found, the name
      what that position needs. A 💡 line is only a clue to *where* the surplus
      sits (deleting that word restores the weight) — it is rarely the fix itself.
   2. Draft 3–5 alternatives that keep the meaning: swap a word for one of
      equal or required weight (`weigh` helps), reorder, change a particle,
      add/remove a conjunction, use an alternative form (تسهيل الهمزة، إشباع، صرف
      الممنوع للضرورة ...) — see `references/fixing.md`.
   3. Verify them all in one call: `scan.py verify --brief --meter X "alt1" "alt2" ...`
      (one ✓/✗ line each; drop `--brief` for the full تقطيع of the winners).
   4. `verify` checks weight only. For each passing candidate also check
      yourself: grammar and agreement (e.g. «الطيورُ العابرُ» scans but is wrong),
      the rhyme word (same rawi, rawi vowel, ridf/ta'sis as the poem, and **never a
      rhyme word that already ends another verse** — إيطاء; pass `--poem poem.txt
      --line N` to `verify` and it flags such candidates), and that
      the meaning stays the poet's. Then put the chosen line into the poem copy
      and re-run `analyze` on the whole poem to confirm darb and rhyme.
   5. Show the poet only candidates that pass all of this (2–3 is plenty), each
      with what changed and its تقطيع. If none pass, iterate before replying.
7. **Keep the working copy current.** When the poet accepts a change, update
   `poem.txt` and re-run `analyze` on the whole poem — a fix can disturb the
   darb or the rhyme consistency.

For **composing** a line in a meter: draft several candidate lines, verify them
all, keep only the passing ones, and make sure the darb and rawi match the
rest of the poem.

## Reading the report

- **Verdict and confidence.** Confidence reflects how clearly the top meter
  beats the runner-up across all lines, not whether every line is sound.
  `منخفضة` means: tell the poet the meter is uncertain and why.
- **Candidates table.** Lower cost = better fit. The line "الأبيات التي تحسم..."
  lists the verses that fit the winner but not the runner-up — mention them.
  "التباس" means every line fits both meters; well-known twins:
  - مجزوء الوافر vs الهزج — identical when every foot is مفاعلْتن (عصب); one
    مفاعَلَتن (//0///0) anywhere proves الوافر.
  - الكامل vs الرجز — متْفاعلن (مضمر) = مستفعلن; one متَفاعلن (///0//0) proves الكامل.
  - المتدارك/الخبب under the implemented shared-family convention vs other short lines; المجتث/المقتضب/المضارع are rare —
    prefer a common meter on a tie and say so.
- **Per verse**: arudi writing split by foot, each foot with name and /0
  pattern. ✗ marks a broken foot with a diagnosis ("زيادة/نقص/حركة في موضع
  سكون") and the patterns allowed at that position.
- `ـ` in arudi writing is a lengthening (إشباع) letter whose vowel was not marked.
- **قراءات مفترضة**: decisions the scanner made (e.g. «منزل»: آخر الشطر حركة
  مشبعة, «لهُ» غير مشبعة, تدوير). Mention the ones that matter to the poet.
- **⚠ حرفًا بلا تشكيل**: you left letters undiacritized; the scan guessed.
  Diacritize and re-run before relying on it (the scanner cannot invent a
  missing shadda or tanwin).
- **الضرب**: the last foot of the ajuz must keep one form across the poem.
  "اختلاف الضرب" is a real flaw to report. Ambiguous endings are re-read
  to agree with the poem's dominant darb automatically.
- **القافية**: rawi, majra (its vowel), ridf/ta'sis, type, tasree', and faults
  (إقواء، إصراف، سناد، إيطاء، اختلاف الروي). The rhyme checker uses the last
  word's spelling; double-check its findings against your own reading.
- **Free verse**: the taf'ila family, a verdict (موزون / مواضع خلل / not on one
  taf'ila), feet per line, ↵ for a foot that runs into the next line (تدوير).
  Line lengths vary in التفعيلة; pronunciation, structural choices and the
  intended convention still matter. If no family fits, report that no supported
  match was established. A failed scan alone does not classify قصيدة النثر.

Permitted zihafat are not errors; a rare one (كفّ in الطويل، وقص in الكامل) is
allowed but heavier — mention it as a stylistic note, not a fault.

**⚠ warnings (not breaks)** cover rules that span more than one foot:
- **التصريع** — an عروض in its تصريع form (e.g. مفاعيلن in الطويل) outside a
  مصرّع opening verse.
- **الاعتماد** — in الطويل, فعولن (unchanged) right before the محذوف darb; the
  usual form is فعولُ فعولن.
- **المعاقبة** — in الرمل، المديد، الخفيف، المجتث, a كفّ foot followed by a خبن
  foot (both sakins of adjacent sababs dropped).
Report them as stylistic or classical-rule notes the poet may choose to fix.
Forms marked «عند المحدثين» (e.g. ضرب مرفّل in تام الخبب، ضرب مقطوع in مجزوء
الرجز) are later practice, not Khalilian — accepted, but say so if it matters.
**قطع همزة الوصل** — mid-line, a hamzat wasl is dropped and the sakin or
tanween before it moves (نَجْمٌ اخْتَفَى → نَجْ مُ نِخْ تَ فَى). Pronouncing it as a
full hamza (نَجْ مُنْ إِخْ تَ فَى) is a recognised poetic licence: the scanner takes
it only when it saves the meter and shows it as «قطع همزة الوصل (ضرورة شعرية)».
Tell the poet it is a licence, not the default reading.
الخرم (dropping the first moving letter of a verse in الطويل، الوافر، الهزج،
المتقارب، المضارع) is accepted at the opening foot only, as a rare licence.

## Presenting to the poet

Lead with the answer, then the evidence, then the offers:

1. **Verdict**: the meter (and form: تام، مجزوء، مخلّع...), confidence in plain
   words, and the decisive lines if there was a rival.
2. **Line by line**: for each verse, its تقطيع (taf'ilat with /0 patterns).
   For long poems show all sound verses compactly and spend the detail on
   problems.
3. **Problems**: each broken foot in plain language — what the ear hears,
   which word causes it — and any rhyme/darb issues.
4. **Offers**: verified fixes (2–3 per line), or ask whether they want them.

Use the user's language for explanations; keep scanner jargon out; never paste
the raw report unless asked. Arabic verses read best on their own lines.

Chat layout for results and fixes (when the workbench is not used):

| # | السطر | التقطيع | الحالة |
|---|---|---|---|
| ٢ | قُمْ وَاتْرُكِ الْأَحْزَانَ … | − ✗ ⁞ − ب − − ⁞ − ب − − ⁞ − ب = | مقطع زائد في أول السطر |

| البديل | التقطيع | الأثر في المعنى |
|---|---|---|
| وَاتْرُكِ الْأَحْزَانَ لِلَّيْلِ الطَّوِيلْ | − ب − − ⁞ − ب − − ⁞ − ب = | حذف «قُمْ» والمعنى باقٍ |

Number lines with Arabic digits, separate feet with ⁞, keep one table per
purpose, and end with the single question the poet needs to answer.

## Reference files (load when needed)

- `references/meters.md` — the 16 meters, their forms, feet, zihafat and the
  rhythm "feel" of each; mnemonic lines (مفاتيح البحور).
- `references/zihafat.md` — zihaf and 'illa definitions and where each applies.
- `references/qafiya.md` — rhyme letters, types and faults.
- `references/arudi-writing.md` — rules of الكتابة العروضية (what is pronounced
  and counted), useful when explaining a scan.
- `references/free-verse.md` — taf'ila poetry rules, endings, تدوير.
- `references/fixing.md` — practical repair techniques and licensed poetic
  necessities (الضرورات الشعرية).
- [`references/sources.md`](references/sources.md) — primary sources, coverage limits, and
  the source behind each rule the scanner applies, where it lives in the code, and which rules are later practice,
  licences or engineering choices. Cite it when the poet asks "according to whom?".

## Limits (say so when relevant)

- Meter tables, ending-pair constraints, pronunciation alternatives and tests
  cover implemented cases, not every licensed classical or modern practice.
  Ranking costs and confidence are heuristics, not accuracy probabilities.
  Keep multiple plausible readings or meters visible instead of certifying a
  unique result from a short or ambiguous passage.
- The Diwan database and AI buttons require the host's Claude capabilities; an
  ordinary browser uses local storage and manual editing; page Word download
  additionally needs the host downloads capability. Provider features
  require a compatible host and do not imply integration with every agent.
  The page fetches fonts and JSZip from CDNs, so it is not fully offline.
- CLI Word export requires Node.js. PDF additionally requires LibreOffice and
  font support; check these before promising a PDF.

- Colloquial / نبطي poetry follows different pronunciation and meters; scan it
  only as an approximation and tell the poet.
- Muwashshahat, mixed-taf'ila free verse and very rare forms are only
  partially covered.
- A hemistich split inside a word (تدوير in classical verse) must be joined
  into one line.
- The rhyme audit is spelling-based and may misjudge unusual endings; your
  reading is the final word on rhyme.

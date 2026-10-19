# Scanner workflow

Use for meter/rhyme identification, metered composition or repair. The scanner is Firas F. Khabour's rule-based engine, integrated into this skill. It runs locally with Python's standard library; Diwan uses its JavaScript counterpart. See [primary rules and coverage limits](SCANNER-SOURCES.md) and the general [prosody method](PROSODY.md).

## Prepare the reading

Preserve the original text before adding tashkeel. Choose vowels from meaning and grammar, not from a target pattern. Follow the entrypoint's confirmation policy: ordinary preliminary analysis may use disclosed assumptions; requested review-first work pauses, and consequential unresolved ambiguity may need clarification. Do not require confirmation of already supplied readings or your own newly composed drafts.

For consequential homographs, active/passive readings, negation, case endings or optional lengthening, keep the alternatives separate. If a legitimate alternative alone resolves a mismatch, describe it as an alternative, not a silent correction. User-supplied marks win even when they produce a break.

- Classical verse: one بيت per line, with ` * ` between hemistichs. A tab, `|` or three spaces also separate halves. If each printed line is one hemistich, use `--mode pairs`. Automatic splitting searches word boundaries; for a classical تدوير that divides a word between halves, keep the complete verse in one input line so its shared word can be inspected.
- Taf‘ila: one poetic line per input line. Inspect connected reading and actual foot crossings rather than assuming every line break is a pause.
- Fully mark the intended reading where possible, including shadda, tanwin, case endings and sun-letter assimilation. Use explicit hamzat al-qat‘; leave wasl alif as ا. Preserve pronounced long vowels and tanwin nun.
- A bare final letter lets the engine try implemented pause/lengthening alternatives. Report consequential choices. The engine cannot reliably supply missing shadda/tanwin or infer all intended pronunciation from unmarked text.
- For dialect, muwashshah, mixed-foot or other unsupported practices, establish the tradition and limits before interpreting a failed scan.

Use `coverage raw.txt` when checking how much tashkeel the poet supplied. `full` measures written coverage, not grammatical correctness; `partial` or `none` means the intended reading still needs preparation. Do not use a meter match to invent missing marks.

## When the poet requests tashkeel review

Keep the raw text and proposed reading separate. Present the fully vocalized proposal in the poet's layout and list the consequential choices only, such as an unmarked pronoun’s addressee/referent («كتابكَ / كتابكِ»), active/passive «عَلِمَ / عُلِمَ», a shadda, a role-changing case ending, or a line-end pause versus lengthening. If the poet left a hemistich-final letter bare and its reading remains undecided, leave that final mark open in the proposal so the text agrees with the choice list. Never remove a supplied mark to create that ambiguity.

For example, a real decision list can say: «١. عَلِمَ أم عُلِمَ؟ اخترتُ المعلوم مؤقتًا» and «٢. نهاية الأمل تركتُها مفتوحة: وقف أم إشباع؟». Use only choices actually present in the poem.

Invite corrections by choice number or by a corrected line, then stop before metrical analysis. Apply the poet's answer verbatim, even if it breaks the meter. For preliminary analysis that the user wants immediately, label those same choices as assumptions; do not silently choose a different reading after a mismatch.

## Commands

Run from the installed `arabic-poetry` folder or use absolute script paths. Write UTF-8 input files in the working/output directory, not over the installed package.

```sh
python3 scripts/scan.py coverage raw.txt
python3 scripts/scan.py analyze poem.txt
python3 scripts/scan.py analyze poem.txt --json
python3 scripts/scan.py analyze poem.txt --mode pairs
python3 scripts/scan.py analyze poem.txt --mode free --meter kamil
python3 scripts/scan.py verify --brief --meter tawil "صدر * عجز" "بديل * آخر"
python3 scripts/scan.py verify --meter tawil --part ajuz "عجز بديل"
python3 scripts/scan.py verify --meter kamil --free "سطر تفعيلة"
python3 scripts/scan.py verify --meter tawil --poem poem.txt --line 2 "صدر * عجز"
python3 scripts/scan.py weigh "كلمة أو عبارة"
python3 scripts/scan.py meters
```

`--line` counts physical source-file rows, including blanks. With `--poem`, candidate verification excludes the replaced row, uses its known verse position and applies the strict repeated-rhyme spelling filter in either mode. That editing filter does not establish the semantic conditions of الإيطاء.

Meter keys: `tawil madid basit wafir kamil hazaj rajaz ramal sari munsarih khafif mudari muqtadab mujtath mutaqarib mutadarak`. Mode auto-detection and ranking are aids, not a form definition. Force the intended mode/meter when testing a specific claim, while keeping rival plausible readings visible.

## Read and verify the result

1. Inspect the chosen reading and عروض letters before accepting a meter, using the [transcription rules](arudi-writing.md) for sound expansion and connected pronunciation. Keep supplied text, inferred reading, normalized output and proposed correction distinct. A famous verse's attribution does not validate altered wording.
2. Read whole-poem candidates, decisive lines, per-foot patterns, alignment errors, ending forms and rhyme candidates. A zero alignment error still needs plausible pronunciation and position-appropriate rules. Check unfamiliar endings against [meters](meters.md), [zihafat](zihafat.md) and primary references.
3. Confidence describes ranking separation, not a probability or comprehensive accuracy. Short passages can fit multiple meters. If common and rare forms tie, a common form may be presented first as a ranking preference, with the tie disclosed; frequency does not rule out the rarer reading. Preserve ambiguity such as الكامل/الرجز or مجزوء الوافر/الهزج when the actual sounds do not distinguish them.
4. If many lines fail, recheck reading, layout, paired halves, mode and rival candidates before proposing extensive edits. The report's 40% warning is an implementation heuristic, not evidence that the poet is wrong. Tell the poet which readings, layouts and candidate meters you rechecked and what that resolved.
5. For taf‘ila, inspect [line crossings and ending conventions](free-verse.md). Never delete a pronounced tanwin nun just to join a foot. State the implementation's shared المتدارك/الخبب convention without treating it as settled theory.
6. Check عروض/ضرب compatibility, first-verse تصريع conditions and consistency in the poem's intended form. The tables encode selected constraints, not every classical permission. A spelling-based rhyme audit is provisional; use the [rhyme definitions and fault checks](qafiya.md) to inspect pronounced روي، مجرى، ردف، تأسيس and optional وصل/خروج independently.

### Interpret the report's signals

- In «؟ pattern ✗ (المتوقع name)», the pattern is the observed sound material and the named foot is the expected target. Locate the spoken phrase causing the mismatch; the expected name is not a report that the foot was already sound.
- «الأبيات التي تحسم…» identifies lines separating competing meters. Mention the decisive lines; if every line fits both candidates, preserve the ambiguity.
- مجزوء الوافر can coincide with الهزج when all relevant feet are مفاعلْتن. A genuine مفاعَلَتن reading can distinguish the الوافر candidate. Likewise متْفاعلن in الكامل has the same sound pattern as مستفعلن in الرجز; an actual متَفاعلن can distinguish the candidates. Use the whole passage and applicable form, not a single familiar foot, to settle the verdict.
- «قراءات مفترضة» records pronunciation choices, including inferred endings, pronoun lengthening or تدوير. Explain consequential choices. In عروض writing, «ـ» can represent lengthening whose vowel was unmarked; it is not a supplied vowel confirmed by the poet.
- «⚠ حرفًا بلا تشكيل» calls for completing the intended reading and rechecking it before relying on the scan. The engine cannot supply a missing shadda or tanwin reliably.
- Keep «✗» alignment breaks separate from «⚠» rule notes. For التصريع, recheck opening-verse context; for المعاقبة or الاعتماد, explain the applicable source and convention rather than treating every note as a broken foot or dismissing it automatically. The strength of الاعتماد varies by source. See the [rule map](SCANNER-SOURCES.md).
- A reported «قطع همزة الوصل (ضرورة شعرية)» must be disclosed as a licence, not presented as the ordinary connected reading. الخرم is an opening-foot licence in the supported meters, not permission to delete an arbitrary internal sound. A permitted but rare زحاف can be a stylistic note rather than a break; consult the [sources and positions](SCANNER-SOURCES.md).
- «عند المحدثين» marks later practice rather than a Khalilian table form. Name that distinction when relevant, without rejecting an intentionally modern convention solely for being modern.
- In classical work with a fixed ضرب, report «اختلاف الضرب» and inspect the poem's dominant ending. For taf‘ila, distinguish a real crossing foot marked «↵» from a mere printed line break and use the intended ending convention.

For repairs, draft a few minimal phrase alternatives using [repair techniques](fixing.md), verify candidates in one call, then check grammar, rhyme and meaning yourself. Put a chosen repair into a separate poem copy and analyze the whole affected line/poem again. Verification of an isolated half cannot establish first-verse context or whole-poem consistency. If no candidate passes, revise and verify again before offering a fix; if the constraints remain unresolved, say that no verified repair is ready. Do not present a failing candidate as a successful correction.

## Keep the accepted working copy current

Keep a raw original and a separate current poem file, typically `raw.txt` and `poem.txt`, in the output workspace. A repair proposal is not acceptance. When the poet accepts a repair, update the current copy with exactly that choice and analyze the full current poem again, checking ضرب and rhyme consistency as well as the edited line. Use the [Diwan workflow](DIWAN.md) when the active copy lives in the editor: read its latest text first and do not overwrite a newer edit with an older chat version.

## Explain proportionally

Lead with the requested conclusion and the important reading assumptions. For a quick metrical explanation, show one complete hemistich (or the whole shorter fragment) in a compact table: pronounced group in عروض writing | observed syllable pattern | fitted foot or located mismatch. Cover every sound once, including across word boundaries; do not truncate the text or substitute a generic foot sequence for its scan. Derive the groups and patterns from the inspected reading and alignment, not merely from the expected meter. The JSON report's per-foot `letters`, `got` and `name` fields help locate these groups; convert letter-level patterns to syllable notation and review the inferred pronunciation before displaying them.

Use per-line tables for a full audit. Explain `ب` short, `−` long and `=` overlong syllable notation if used; external letter-level notation must be converted before comparison. Keep Arabic text and symbol display order unambiguous. For a full review, present the verdict, line-by-line evidence, located problems and a few verified offers, in that order. End with the one choice the poet needs to make when a choice is needed; do not add a routine approval question to a completed quick analysis. Do not paste the raw report unless useful or requested.

If tools are unavailable, say what was and was not checked. A manual analysis can remain useful, but do not claim the scanner ran or certify an unresolved reading.

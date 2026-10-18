# Scanner workflow

Use for meter/rhyme identification, metered composition or repair. The scanner is Firas F. Khabour's rule-based engine, integrated into this skill. It runs locally with Python's standard library; Diwan uses its JavaScript counterpart. See [primary rules and coverage limits](SCANNER-SOURCES.md) and the general [prosody method](PROSODY.md).

## Prepare the reading

Preserve the original text before adding tashkeel. Choose vowels from meaning and grammar, not from a target pattern. Follow the entrypoint's confirmation policy: ordinary preliminary analysis may use disclosed assumptions; requested review-first work pauses, and consequential unresolved ambiguity may need clarification. Do not require confirmation of already supplied readings or your own newly composed drafts.

For consequential homographs, active/passive readings, negation, case endings or optional lengthening, keep the alternatives separate. If a legitimate alternative alone resolves a mismatch, describe it as an alternative, not a silent correction. User-supplied marks win even when they produce a break.

- Classical verse: one بيت per line, with ` * ` between hemistichs. A tab, `|` or three spaces also separate halves. If each printed line is one hemistich, use `--mode pairs`.
- Taf‘ila: one poetic line per input line. Inspect connected reading and actual foot crossings rather than assuming every line break is a pause.
- Fully mark the intended reading where possible, including shadda, tanwin, case endings and sun-letter assimilation. Use explicit hamzat al-qat‘; leave wasl alif as ا. Preserve pronounced long vowels and tanwin nun.
- A bare final letter lets the engine try implemented pause/lengthening alternatives. Report consequential choices. The engine cannot reliably supply missing shadda/tanwin or infer all intended pronunciation from unmarked text.
- For dialect, muwashshah, mixed-foot or other unsupported practices, establish the tradition and limits before interpreting a failed scan.

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
3. Confidence describes ranking separation, not a probability or comprehensive accuracy. Short passages can fit multiple meters. Preserve ambiguity such as الكامل/الرجز or مجزوء الوافر/الهزج when the actual sounds do not distinguish them.
4. If many lines fail, recheck reading, layout, paired halves, mode and rival candidates before proposing extensive edits. The report's 40% warning is an implementation heuristic, not evidence that the poet is wrong.
5. For taf‘ila, inspect [line crossings and ending conventions](free-verse.md). Never delete a pronounced tanwin nun just to join a foot. State the implementation's shared المتدارك/الخبب convention without treating it as settled theory.
6. Check عروض/ضرب compatibility, first-verse تصريع conditions and consistency in the poem's intended form. The tables encode selected constraints, not every classical permission. A spelling-based rhyme audit is provisional; use the [rhyme definitions and fault checks](qafiya.md) to inspect pronounced روي، مجرى، ردف، تأسيس and optional وصل/خروج independently.

For repairs, draft a few minimal phrase alternatives using [repair techniques](fixing.md), verify candidates in one call, then check grammar, rhyme and meaning yourself. Put a chosen repair into a separate poem copy and analyze the whole affected line/poem again. Verification of an isolated half cannot establish first-verse context or whole-poem consistency.

## Explain proportionally

Lead with the requested conclusion and the important reading assumptions. Show a compact scan for a quick question; use per-line tables for a full audit. Explain `ب` short, `−` long and `=` overlong syllable notation if used; external letter-level notation must be converted before comparison. Keep Arabic text and symbol display order unambiguous. Do not paste the raw report unless useful or requested.

If tools are unavailable, say what was and was not checked. A manual analysis can remain useful, but do not claim the scanner ran or certify an unresolved reading.

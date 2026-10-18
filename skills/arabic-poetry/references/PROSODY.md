# Prosody and rhyme

Use this page to judge metrical and rhyme claims while composing, revising or explaining. The detailed rules live beside it: pronunciation in [arudi-writing](arudi-writing.md), meters and forms in [meters](meters.md), variations in [zihafat](zihafat.md), rhyme in [qafiya](qafiya.md), free verse in [free-verse](free-verse.md), and the scanner's rule sources in [SCANNER-SOURCES](SCANNER-SOURCES.md). When execution is available, let the [scanner](SCANNER.md) do the counting and use this page for the judgement around it.

## Keep four layers separate

1. The text as supplied, including diacritics and line breaks.
2. A grammatically and semantically plausible pronunciation. Mark added vocalization as inferred when the user did not supply it.
3. The عروض transcription (الكتابة العروضية) and its syllable pattern.
4. The proposed feet, their variants, and the verdict.

If a layer changes, recompute the layers that follow. Do not correct the original silently, infer a reading solely because it matches a target, or use the known meter of a famous poem to validate an altered quotation. When a scanner proposes a reading (its «قراءات مفترضة»), check that reading before accepting the scan.

## Notation

Use the notation that the scanner and the Diwan workbench display:

| Symbol | Meaning |
| --- | --- |
| ب | short syllable: a moving letter not followed by a still one |
| − | long syllable: a moving letter followed by a still one (including a long vowel) |
| = | overlong syllable, allowed only in pause at a line end |
| ⁞ | foot boundary |
| ✗ | broken foot |

Read the pattern right to left with the Arabic text. Name each foot with its pattern (فعولن ب − −), and name a variation by its foot form (فعولُ ب − ب). Keep to this notation rather than letter-by-letter moving/still strings; when a source or tool writes letters that way, convert its pattern to syllables and say so.

| Foot | Pattern |
| --- | --- |
| فعولن | ب − − |
| مفاعيلن | ب − − − |
| فاعلن | − ب − |
| فاعلاتن | − ب − − |
| مستفعلن | − − ب − |
| متفاعلن | ب ب − ب − |
| مفاعلتن | ب − ب ب − |
| مفعولاتُ | − − − ب |

These are building blocks, not meter definitions. Identical patterns can hide different سبب and وتد structures (مستفعلن and مستفع لن), and that structure decides which variations are permitted.

## Pronunciation essentials

الكتابة العروضية records what is pronounced; it is an analysis, not a corrected spelling. Expand shadda and tanwin, count unwritten long vowels, drop silent letters, apply همزة الوصل and the solar article by position, and choose the actual الوصل or الوقف reading. Explain any terminal إشباع or poetic licence; do not lengthen arbitrary vowels to fit a template. For dialect poetry, establish the spoken wording first.

## Match a meter

- Foot boundaries need not coincide with word boundaries. Cover every sound once, with nothing deleted, inserted or duplicated.
- Compare the whole line with the applicable form, including its عروض and ضرب. Distinguish حشو, عروض and ضرب; a variation allowed in one position does not authorize it everywhere.
- Consider مجزوء، مشطور، منهوك forms before calling a shorter line broken.
- Check both halves of a بيت and several lines of a poem. If a passage fits only partially, say where the match stops.
- Locate a mismatch in a pronounced phrase and state the assumed target form. Recheck the whole line after proposing a repair.
- For تفعيلة, check the recurring foot across line breaks where تدوير applies, and state the الوصل/الوقف treatment at the break. Do not equate الخبب with every occurrence of المتدارك without explaining the convention.

## Judge uncertainty

| Evidence | Appropriate conclusion |
| --- | --- |
| All supplied sounds fit a documented form with a plausible reading | Name the meter and show the supporting scan |
| Different plausible vocalizations or short fragments fit different meters | Give candidates and the reading or extra context that distinguishes them |
| Surrounding lines establish a meter but one passage fails | Show the mismatch and assess whether it is a transcription issue, reading issue, or metrical fault |
| No supported fit and little context | Say that the meter is not established; request vocalization or more lines only if needed |

Use qualitative confidence tied to evidence, not invented percentages. A failed scan does not prove قصيدة نثر, and a fitting fragment does not prove that the whole text is a classical poem.

## Rhyme

- Analyze the pronounced ending and compare endings across the poem. Separate **الروي**, the anchoring letter, from **القافية**, the fuller ending.
- Distinguish قافية مطلقة from مقيدة by the movement of the روي. A terminal long vowel may be وصل rather than روي.
- Diagnose a named defect, such as إقواء، سناد or إيطاء, only after establishing the scheme and the exact inconsistent part. In modern forms, a changing rhyme may be deliberate.

See the [worked examples](EXAMPLES.md) for complete scans in this notation.

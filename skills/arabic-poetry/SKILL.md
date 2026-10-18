---
name: arabic-poetry
description: Write, revise, continue, explain and analyze classical and modern Arabic poetry, with a local meter scanner and optional Diwan editor. Use when asked to compose or complete أبيات or قصيدة, critique imagery or meaning, identify نوع الشعر or البحر, perform تقطيع عروضي, repair الوزن or القافية, or edit and export a poetry collection.
---

# Arabic poetry

Support classical and modern Arabic poetry equally. Judge each poem by its intended form. Follow the user's requested response language; otherwise match their language, keeping verses and Arabic prosody terms in Arabic with brief explanations when needed.

## Choose the relevant workflow

- For composition, continuation, revision or critique, read [craft and revision](references/CRAFT.md). For explanation and interpretation, read [close reading](references/READING.md).
- For meter or rhyme claims, read [prosody](references/PROSODY.md) and the [scanner workflow](references/SCANNER.md). The bundled scanner supplies reproducible alignment evidence; interpretation still requires plausible pronunciation and licensed forms.
- For a requested editor, a collection or export, read [Diwan](references/DIWAN.md). Keep ordinary writing, critique and quick analysis in chat unless an editor helps the requested work. Diwan is optional; unavailable host capabilities must not block chat or local-file work.
- Use [worked examples](references/EXAMPLES.md) when teaching or checking a detailed scan. [Tools](references/TOOLS.md) distinguishes the scanner and external analyzers. [Sources](references/SOURCES.md), [scanner coverage](references/SCANNER-SOURCES.md) and [similar skills](references/SIMILAR_SKILLS.md) explain evidence and limits. Load only relevant resources.

## Establish intent and preserve the text

- Determine whether the request is composition, continuation, revision, identification, explanation, critique, editing or export. Combine workflows only as needed.
- Extract form, language variety, subject, speaker, tone, length, audience, meter, rhyme and editing scope. Infer routine choices; ask one focused question only when missing information would materially change the result.
- For "ما نوع هذا الشعر؟", distinguish الشكل such as عمودي، تفعيلة، قصيدة نثر, البحر, القافية والروي, and الغرض such as غزل or رثاء. Theme, date and line breaks do not establish a meter. "شعر حر" is context-dependent; شعر مرسل may remain metered without fixed rhyme.
- Preserve supplied wording, marks, line breaks and dialect. Keep originals, inferred vocalization and proposed corrections separate. Do not silently convert نبطي، زجل or other dialectal traditions to الفصحى or force them into unsupported tables.
- For موشح or another stanza tradition, establish repeating units and rhyme structure before judging it. Length labels do not identify a meter; avoid universal قصيدة length cutoffs.

## Vocalization and confirmation

- Choose tashkeel from meaning and grammar, preserving the poet's existing marks. A meter match cannot justify changing who acts, negation or meaning. Keep meaningful alternative readings visible.
- For an ordinary preliminary analysis, state consequential reading and الوصل/الوقف assumptions and proceed provisionally. A short or unvocalized passage may not establish a unique meter.
- If unresolved ambiguity prevents a reliable answer or a meaning-preserving repair, ask a focused reading question. Do not silently select vowels just to obtain a passing scan.
- If the user asks to review tashkeel before analysis, show the proposed reading and consequential choices, then stop without scanning. Honor their corrections even when the resulting reading breaks the meter.
- Already confirmed or fully supplied vocalization needs no routine approval turn. For newly composed drafts, verify your own reading without asking the user to approve every vowel first.

## Compose and continue

1. Choose a movement and voice suited to the subject and length. Develop images, encounters or changes in feeling rather than repeating a premise. Preserve purposeful abstraction, symbolism and ambiguity.
2. For عمودي, honor the بحر, applicable عروض/ضرب and rhyme plan; write complete صدر/عجز pairs. For تفعيلة, honor the rhythmic basis and inspect the sequence across relevant line breaks. For قصيدة نثر, shape imagery, syntax, recurrence and pacing without imposing Khalilian meter or monorhyme.
3. Review diction, grammar, imagery, progression and sound. Remove padding or forced phrasing when it weakens meaning. A metrical match does not prove literary quality.
4. Before claiming metrical regularity, check every supplied or generated line using the scanner when execution is available, inspect its reading and forms, and check relevant rhyme endings. Rescan affected lines after edits. If verification remains unresolved, label the passage a draft and locate the uncertainty.
5. Deliver the poem first, with only useful or requested verification notes. For continuation, retain the supplied passage, label the added portion as new, develop its established voice and check the join. Do not silently restart or repair it.

## Revise or critique

1. Preserve the original and identify intended meaning, voice, form and constraints. For critique-only requests, diagnose without rewriting.
2. Separate meter/rhyme faults, grammar/meaning problems and aesthetic preferences. A permitted زحاف is not automatically a fault; unusual imagery is not automatically an error.
3. Establish the intended meter from context before repairing a line. Locate the mismatch in the actual pronounced span; recheck reading, layout and candidate meters when many lines appear broken.
4. Compare a few grammatical phrase repairs and choose the smallest viable change. Preserve required words, imagery and dialect. Explain lost or gained meaning, including removed emphasis. Offer a broader rewrite separately if it changes voice or form.
5. Verify promising metrical repairs, then check subject/object roles, negation, pronouns, agreement, modifiers and rhyme. Put the repair into the poem copy and recheck the full affected line and surrounding ending consistency.
6. When the poet accepts a repair, update the current working copy and scan the whole poem again for ending/rhyme consistency. Return the revised passage with concrete reasons for significant changes. If constraints conflict, explain the conflict rather than silently changing the brief. Preserve authorship and distinguish supplied lines from newly composed text.

## Identify, scan and explain

1. Establish pronunciation before metrical classification. For supported metered text, execute the local scanner as described in [SCANNER.md](references/SCANNER.md); inspect the inferred عروض writing, actual sound sequence, foot boundaries and licensed variants. Never invent a tool run.
2. Keep notation explicit and cover all sounds exactly once. Use ب short, − long and = overlong syllables in pause, ⁞ between feet, ✗ for a broken foot and Arabic line digits (١، ٢). Name a زحاف by its foot form, such as فعولُ; use [syllable notation](references/PROSODY.md#notation), not letter-by-letter moving/still strings. Verify that the scan covers the supplied sounds; a matching pattern does not license a variant.
3. Compare the whole supplied passage, both halves of a بيت, and relevant connected taf‘ila sequences. A familiar quotation, first match or nearest-pattern score does not establish uniqueness or validate changed wording.
4. Analyze الروي and the pronounced rhyme ending separately. The scanner's spelling-based rhyme candidate needs review; the final printed character is not automatically الروي.
5. Report a supported fit, plausible candidates with distinguishing readings, or insufficient evidence. Locate mismatches before proposing repair. A failed scan alone does not establish قصيدة نثر or invalidate an unsupported tradition.
6. For a concise request, give the likely form/meter, compact evidence and consequential assumptions. For full analysis, use النص، القراءة، الكتابة العروضية، التفعيلات، الملاحظة. Explain symbols and keep technical detail proportional.
7. For interpretation, ground each major reading in quoted wording, its linguistic/formal feature and its effect. Separate speaker from historical author, check consequential alternative meanings, and avoid invented biography or conclusions such as death from absence alone. Meter analysis is optional when it does not answer the literary question.

## Evidence, tools and delivery

- Verify unfamiliar variants, rhyme rules, dialectal conventions and historical attribution against appropriate sources. Name unavailable evidence and keep claims provisional; do not invent a poetic license or citation.
- Treat scanner ranking and confidence as heuristic, not accuracy probabilities. Its implemented pronunciation alternatives and metrical forms are incomplete. Inspect normalized readings; two runtimes agreeing does not establish linguistic correctness.
- If execution is unavailable, explain that limit, give checkable manual analysis where justified, and keep unresolved claims provisional. Never present an unrun scanner check as completed evidence.
- Use the editor and exporter only through capabilities actually available. Local files/browser storage do not imply host synchronization or future-chat access. Preserve Firas F. Khabour's scanner/Diwan credit and the Amiri font license when copying or rebuilding assets.
- Review request adherence, technical validity, language/meaning and literary effect separately. Do not promise a perfect poem, originality, attribution or comprehensive accuracy on the basis of a scan.

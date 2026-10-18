---
name: arabic-poetry
description: Write, revise, continue, and explain Arabic poetry; identify form, meter, rhyme, and theme through explicit analysis. Use when asked to write or complete an Arabic poem, improve أبيات or قصيدة, explain imagery or meaning, repair كسر الوزن or القافية, perform تقطيع عروضي, identify البحر or نوع الشعر, or critique classical, taf‘ila, or prose poetry.
---

# Arabic poetry

Support classical and modern Arabic poetry equally. Judge each poem by its intended form. Respond in Arabic unless the user requests another language; use Arabic prosody terms with brief explanations suited to the reader.

## Choose the task and constraints

- Determine whether the user wants composition, continuation, revision, identification, explanation, or critique. Combine modes only where useful to the request.
- For "ما نوع هذا الشعر؟", distinguish **الشكل** such as عمودي، تفعيلة، قصيدة نثر, **البحر**, **القافية والروي**, and **الغرض** such as غزل، رثاء، وصف. A theme does not identify a meter; a modern date does not identify a form.
- Treat "شعر حر" as context-dependent terminology. Name the intended form; metered شعر مرسل can omit a fixed rhyme without becoming prose poetry.
- These form labels are not exhaustive. For a موشح or another stanza tradition, identify its repeating units and rhyme scheme before judging an excerpt. Length labels such as مقطوعة do not identify a meter; avoid universal قصيدة length cutoffs.
- Extract the intended form, language variety, subject, speaker, tone, length, audience, and any required meter or rhyme from the request and supplied draft. Preserve explicit constraints.
- Infer routine choices. If an unspecified form would substantially change the result, ask one focused question; otherwise choose a suitable form and state the assumption briefly. Never require a beginner to name a بحر before helping.
- Keep dialectal poetry in its dialect. For نبطي، زجل، شعر شعبي, establish pronunciation and the relevant tradition before applying a meter label. Do not silently convert it to الفصحى.

Read [craft and revision](references/CRAFT.md) for composition or editing, [close reading](references/READING.md) for explanation or literary critique, [prosody](references/PROSODY.md) for metrical or rhyme claims, and [worked examples](references/EXAMPLES.md) when teaching or checking the output shape. For counting, use the companion [arabic-prosody](../arabic-prosody/SKILL.md) scanner when it is installed. [Sources](references/SOURCES.md) and [similar skills](references/SIMILAR_SKILLS.md) explain the evidence and its limits.

## Explain and read closely

1. Establish the literal reading, difficult words, speaker, addressee, and situation. Keep the poem's speaker distinct from its historical author; verify any claimed occasion, quotation, or historical allusion.
2. Support each major interpretation with a short phrase, its specific linguistic or formal feature, and the effect that supports the reading. Explain how imagery, syntax, sound, or a break works here rather than merely naming a device.
3. Check consequential alternative grammar or meanings and neighboring lines. Mark a plausible interpretation as an interpretation; do not invent biography to resolve purposeful ambiguity.
4. Give a clear overall reading and focus on the details the user asked about. Offer a competing reading only when the text supports it. Include meter analysis when relevant to the request, rather than requiring every explanation to identify a بحر.

## Compose

1. Choose a movement suited to the brief, such as a situation, a concrete image or encounter, and a change in feeling or understanding. Let the subject, voice, and requested length govern how much develops.
2. For **عمودي**, choose or honor a بحر, its applicable عروض and ضرب, and a rhyme plan. Write complete أبيات with صدر and عجز, keeping the chosen metrical form consistent. Make rhyme serve the meaning.
3. For **تفعيلة**, choose or honor the rhythmic basis, scan the actual foot sequence, and vary line length with the sense. Allow enjambment and rhyme choices supported by the poem. Visible line breaks alone do not prove meter.
4. For **قصيدة نثر**, shape imagery, syntax, sonic recurrence, pacing, and the ending. Do not impose a Khalilian meter or monorhyme unless the user requests a change of form.
5. Review diction, grammar, imagery, voice, and progression. Remove padding or forced sound effects where they weaken meaning; preserve purposeful abstraction, symbolism, repetition, and ambiguity. Avoid explaining an image that already carries its meaning.
6. Check every line when claiming metrical regularity and every relevant ending when claiming rhyme consistency. Revise and rescan any changed line. If verification remains unresolved, describe the text as a draft and identify the uncertain passage.

Deliver the poem first. Add a short form or verification note only when it helps or was requested. Keep detailed scansion available for a technical request; do not overwhelm a simple creative request.

For continuation, retain the supplied lines, speaker, imagery, and established form; label only the added passage as new. Develop what follows without silently repairing or restarting the poem. Check the transition and any ongoing meter/rhyme against the supplied passage.

## Revise or critique

1. Preserve the original text and identify its intended meaning, voice, form, and constraints before changing it.
2. Separate metrical or rhyme faults, grammar or unclear meaning, and aesthetic preferences. A permitted زحاف is not automatically a flaw; unusual imagery is not automatically an error.
3. If the meter is unspecified, analyze the surrounding poem before repairing one line. Do not rewrite a poem onto a guessed بحر without stating the uncertainty.
4. Locate the faulty span and keep surrounding sound material where possible. Compare a few meaningful repairs when constraints compete, then choose the smallest viable change. Foot boundaries may cross words; repair a grammatical phrase rather than remove letters mechanically. For critique-only requests, diagnose without rewriting the whole poem.
5. Show the original passage, proposed passage, and concrete reason for each significant change. Explain meaning lost or gained when a repair has a tradeoff.
6. Check subject/object roles, negation, pronoun reference, and modifiers for meaning changes; rescan the whole affected line and compare rhyme endings. Do not fix one foot by breaking another or changing the intended pronunciation without disclosure. Offer a broader rewrite separately when it changes the voice or form.

Return the revised passage and a few actionable notes. Preserve the user's authorship and distinguish their supplied lines from newly composed lines.

## Identify and scan

1. Preserve the exact wording and line breaks. Separate the supplied text, an inferred vocalization, and any proposed correction.
2. Establish pronunciation, then write the relevant passage in الكتابة العروضية. Record meaningful alternatives for unvocalized words and for الوصل والوقف.
3. Show the sound sequence, foot boundaries, and actual تفعيلات. Ensure foot segments cover every sound exactly once and that the syllable pattern agrees with the transcription; run the arabic-prosody scanner (`scan.py analyze`) for detailed scans when it is available. Account for each claimed زحاف or علة by its position and permitted use in that meter.
4. Compare the entire supplied passage with candidate meters. Locate a mismatch in the actual pronounced span before proposing a repair. A recognizable phrase or memorized attribution is not a substitute for scanning this wording; a first or nearest tool match does not establish uniqueness.
5. For a بيت, examine both hemistichs. For تفعيلة, examine the rhythmic sequence across line breaks where appropriate. A short fragment may fit several meters or establish a rhythm without establishing the whole form.
6. Analyze الروي and the pronounced rhyme ending separately. Do not label the final printed letter as الروي automatically.
7. State what the evidence supports: clear fit, plausible candidates with the distinguishing reading, or insufficient evidence. If no fit is established, show the mismatch; do not conclude that the text is قصيدة نثر solely from a failed scan.

For a concise answer, give the likely form and meter, one compact scan, and any pronunciation assumption. For a full analysis, use columns for النص، الكتابة العروضية، التقطيع، الملاحظة.

Use the notation shared with arabic-prosody and its Diwan workbench: **ب** short syllable (متحرك), **−** long (متحرك فساكن), **=** overlong (only in pause at a line end); feet separated by **⁞**, each foot named over or beside its pattern (فعولن ب − −); a broken foot marked ✗; lines numbered with Arabic digits (١، ٢). Name a زحاف by its foot form (فعولُ، فعِلن، مستعلن). Explain the symbols once before using them, and do not switch to `/0` or `1/0` strings unless the user asks.

## Evidence and final check

- Verify unfamiliar meter variants, rhyme rules, and dialectal conventions against an appropriate reference. Use the linked sources when accessible; name unavailable evidence and keep the claim provisional. Do not invent a citation, poetic necessity, or license to excuse a mismatch.
- Treat scanner output as alignment evidence, not a verdict. Check its assumed pronunciation (shown as «قراءات مفترضة») and the licensed forms it accepted; zero errors does not prove the intended reading. Third-party analyzers, when used, need the same audit: record the tool, its normalized input, and what it changed.
- Quote existing poems accurately and verify attribution when requested. Do not present generated lines as a historical poet's words. If provenance is uncertain, say so.
- Review adherence to the request, technical validity where applicable, language/meaning, and literary effect separately. Confirm form, dialect, length, editing scope, and preserved voice. Evidence for meter does not prove artistry, originality, or historical attribution; do not promise a "perfect" poem.

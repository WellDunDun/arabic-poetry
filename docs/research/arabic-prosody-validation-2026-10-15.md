# arabic-prosody — validation notes (2026-10-15)

## What was checked

- **Gold verses** (`skills/arabic-prosody/tests/gold_verses.tsv`): 24 well-known verses covering all 16 meters, including rare ones (المضارع، المقتضب، المجتث). The scanner identifies the expected meter with no broken foot for 24/24 (`tests/run_gold.py`).
- **Free verse**: an original تفعيلة passage on متفاعلن with one run-on foot (تدوير) scans with zero errors.
- **Ending ambiguity**: unmarked final letters are read as إطلاق or تقييد to agree with the poem's dominant ضرب (امرؤ القيس، «قفا نبك»).
- **Browser/Python parity** (`tests/parity.js`): the Diwan page's engine reproduces the Python results on the same set.
- **Layout detection**: al-Mutanabbi's «واحرّ قلباه» written one hemistich per line is read as البسيط التام, 18/18 hemistichs sound, rhyme م across all nine verses, opening مصرَّع.

## Method

Text is converted to a lattice of pronunciations (arudi writing), branching where the written text is ambiguous; each hemistich is aligned against every meter form with its permitted زحاف and علة by weighted edit distance, so broken lines are still located foot by foot. The meter is chosen across the whole poem (sound hemistichs, consistency of the ضرب), never from a single foot.

## Limits

- Results depend on the tashkeel; the skill proposes it and asks the poet to confirm before scanning.
- Colloquial and نبطي poetry are only approximated; موشحات and mixed-taf'ila free verse are partially covered.
- The rhyme audit is spelling-based and reports candidates for the poet to confirm.

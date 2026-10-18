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

## Rule review (2026-10-17)

An independent review compared the meter tables with الهاشمي (ميزان الذهب) and التبريزي (الكافي). Every rule is now mapped to its source in [`skills/arabic-prosody/references/sources.md`](../../skills/arabic-prosody/references/sources.md).

**Corrected**
- مشطور السريع and منهوك المنسرح: only the two classical endings, مفعولاتْ (موقوف) and مفعولن (مكشوف).
- الكامل: a non-standard ضرب («مفاعلْ») removed.
- الهزج in free verse: the pattern of «مفاعيلانْ» fixed; عروض مكفوفة marked rare.
- Later practice is now labelled «عند المحدثين» at a higher cost instead of being mixed with the Khalilian forms: مذيّل/مرفّل in تام الخبب، مقطوع in مجزوء الرجز، مقصور in مجزوء الرمل، full forms in مجزوء المتقارب، مقصور in مخلّع البسيط.

**Added**
- الخرم on the opening foot (الطويل، الوافر، الهزج، المتقارب، المضارع) with its named variants.
- المراقبة in المضارع (مفاعيلن never unchanged); النقص in الوافر; شكل in الخفيف; عروض مقطوعة in مجزوء البسيط; ضرب أبتر in مجزوء المتقارب; مذيّل مخبون in الخبب; السريع as a free-verse family; خبن مع ترفيل and قصر as free-verse line endings.
- Cross-foot rules reported as warnings, not faults: المعاقبة (الرمل، المديد، الخفيف، المجتث)، التصريع outside a مصرّع opening، الاعتماد in الطويل.
- البيت المدوّر (a foot completed across the two halves); قطع همزة الوصل as a licence used only when it saves the meter.
- Free verse: a run-on foot across lines is kept only when that foot is sound.

**Tests added** (`tests/parity.js`): a مدوّر verse, a free-verse line whose complete last foot must not run on, and قطع همزة الوصل taken only where it saves the meter. Gold set still 24/24.

**Still medium confidence**: الاعتماد and some «عند المحدثين» forms; they are notes for the poet, not breaks.

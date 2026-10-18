# البحور الستة عشر — reference

These compact summaries support the implemented scanner; they are not exhaustive permissions for every position. Check [primary sources and coverage](SCANNER-SOURCES.md), ending pairs and pronunciation before accepting an alignment. Common "feel" descriptions are associations, not constraints on a poem's theme.

Notation: ب = short syllable (a moving letter alone), − = long syllable (a moving letter followed by a still one), = = overlong (only in pause).
سبب خفيف −، سبب ثقيل ب ب، وتد مجموع ب −، وتد مفروق − ب.

The ten feet (التفاعيل العشر):

| التفعيلة | النمط | البنية |
|---|---|---|
| فعولن | ب − − | وتد مجموع + سبب خفيف |
| فاعلن | − ب − | سبب خفيف + وتد مجموع |
| مفاعيلن | ب − − − | وتد مجموع + سببان خفيفان |
| مستفعلن | − − ب − | سببان خفيفان + وتد مجموع |
| فاعلاتن | − ب − − | سبب + وتد + سبب |
| مفاعلتن | ب − ب ب − | وتد مجموع + سبب ثقيل + سبب خفيف |
| متفاعلن | ب ب − ب − | سبب ثقيل + سبب خفيف + وتد مجموع |
| مفعولاتُ | − − − ب | سببان خفيفان + وتد مفروق |
| مستفعِ لن (مفروقة) | − − ب − | سبب + وتد مفروق + سبب (الخفيف والمجتث) |
| فاعِ لاتن (مفروقة) | − ب − − | وتد مفروق + سببان (المضارع) |

Rule of thumb: zihaf touches only the **second letter of a sabab** (أسباب); the
**watad** stays intact in the hashw. A changed watad means either an 'illa
(in the arud/darb) or a broken line.

---

## الطويل — فعولن مفاعيلن فعولن مفاعيلن (×2)
- Used تامًّا. العروض مقبوضة (مفاعلن ب − ب −) outside the supported first-verse تصريع exceptions; those require matching ending weight and rhyme.
- الضرب: صحيح (مفاعيلن)، مقبوض (مفاعلن)، محذوف (فعولن).
- Hashw zihaf: قبض in فعولن → فعولُ (ب − ب) common; قبض in مفاعيلن → مفاعلن; كفّ (مفاعيلُ) rare.
- Feel: long, grave, narrative; the meter of the great pre-Islamic odes.
- مفتاح: طويلٌ له دون البحور فضائلُ — فعولن مفاعيلن فعولن مفاعلُ

## المديد — فاعلاتن فاعلن فاعلاتن (×2، مجزوء وجوبًا)
- Original: فاعلاتن فاعلن فاعلاتن فاعلن; always used majzu'.
- Arud: صحيحة، محذوفة (فاعلن)، محذوفة مخبونة (فعِلن).
- Darb: صحيح، مقصور (فاعلانْ)، محذوف، أبتر (فعْلن)، and their khabn forms.
- These endings cannot be combined independently; verify the applicable عروض/ضرب pair in the source and implemented tables.
- Rare in practice; confusable with مجزوء الرمل — the middle فاعلن decides.
- مفتاح: لمديد الشعر عندي صفاتُ — فاعلاتن فاعلن فاعلاتُ

## البسيط — مستفعلن فاعلن مستفعلن فاعلن (×2)
- تام: العروض مخبونة (فعِلن ب ب −)؛ الضرب مخبون (فعِلن) أو مقطوع (فعْلن − −).
- مجزوء: مستفعلن فاعلن مستفعلن؛ الضرب صحيح، مذيّل (مستفعلانْ)، مقطوع (مستفعلْ).
- مخلّع البسيط: مستفعلن فاعلن فعولن — very popular, light and singable.
- Hashw: خبن in مستفعلن (متفعلن) and فاعلن (فعِلن) common; طي (مستعلن) acceptable.
- Feel: broad, eloquent; second most used classical meter.
- مفتاح: إنّ البسيط لديه يُبسط الأملُ — مستفعلن فاعلن مستفعلن فعِلُ

## الوافر — مفاعلتن مفاعلتن فعولن (×2)
- تام: العروض والضرب مقطوفة (فعولن ب − −).
- مجزوء: مفاعلتن مفاعلتن؛ الضرب صحيح أو معصوب (مفاعلْتن ب − − −).
- Hashw: عصب (مفاعلْتن) very common.
- Twin: مجزوء الوافر when all feet are معصوبة = الهزج.
- Feel: abundant, flowing, emphatic.
- مفتاح: بحور الشعر وافرها جميلُ — مفاعلتن مفاعلتن فعولُ

## الكامل — متفاعلن متفاعلن متفاعلن (×2)
- تام: العروض صحيحة أو حذّاء (فعِلن)؛ الضرب صحيح، مقطوع (متفاعلْ ب ب − −)، أحذّ (فعِلن)، أحذّ مضمر (فعْلن).
- مجزوء: متفاعلن متفاعلن؛ الضرب صحيح، مرفّل (متفاعلاتن)، مذيّل (متفاعلانْ)، مقطوع.
- Hashw: إضمار (متْفاعلن − − ب −) very common; وقص (مفاعلن) and خزل (متْفعلن) rare.
- Twin: when every foot is مضمر it equals الرجز; one ب ب − ب − settles الكامل.
- Feel: rich in moving letters; resonant, used for every theme.
- مفتاح: كمل الجمال من البحور الكاملُ — متفاعلن متفاعلن متفاعلُ

## الهزج — مفاعيلن مفاعيلن (×2، مجزوء وجوبًا)
- Arud: صحيحة (or مكفوفة). Darb: صحيح، محذوف (فعولن).
- Hashw: كفّ (مفاعيلُ ب − − ب) common, قبض rare.
- مفتاح: على الأهزاج تسهيلُ — مفاعيلن مفاعيلُ

## الرجز — مستفعلن مستفعلن مستفعلن (×2)
- تام، مجزوء، مشطور (one hemistich per line — الأرجوزة)، منهوك (two feet).
- Darb: صحيح، مقطوع (مستفعلْ − − − = مفعولن)، plus khabn forms.
- Hashw: very free — خبن (متفعلن)، طي (مستعلن)، خبل (متعلن) all appear.
- "حمار الشعراء": easy, used for didactic verse (الألفية) and rajaz chants.
- مفتاح: في أبحر الأرجاز بحرٌ يسهلُ — مستفعلن مستفعلن مستفعلُ

## الرمل — فاعلاتن فاعلاتن فاعلاتن (×2)
- تام: العروض محذوفة (فاعلن)؛ الضرب محذوف، مقصور (فاعلانْ)، or صحيح.
- مجزوء: فاعلاتن فاعلاتن؛ الضرب صحيح، مسبّغ (فاعلاتانْ)، محذوف، مقصور.
- Hashw: خبن (فعِلاتن ب ب − −) common; كفّ and شكل rare.
- Feel: gentle, musical; favoured in modern lyric.
- مفتاح: رمل الأبحر ترويه الثقاتُ — فاعلاتن فاعلاتن فاعلاتُ

## السريع — مستفعلن مستفعلن مفعولاتُ (×2)
- In use: مستفعلن مستفعلن فاعلن (العروض مطوية مكشوفة).
- Darb: فاعلن، فاعلانْ (موقوف)، فعْلن (أصلم).
- Hashw: like الرجز (خبن، طي).
- مفتاح: بحرٌ سريعٌ ماله ساحلُ — مستفعلن مستفعلن فاعلُ

## المنسرح — مستفعلن مفعولاتُ مستفعلن (×2)
- In use: مستفعلن مفعولاتُ مفتعلن — the middle foot almost always مطوي (فاعلاتُ − ب − ب).
- Arud/darb: مطوية (مفتعلن − ب ب −).
- مفتاح: منسرحٌ فيه يُضرب المثلُ — مستفعلن مفعولاتُ مفتعلُ

## الخفيف — فاعلاتن مستفعِ لن فاعلاتن (×2)
- تام: arud/darb صحيحة، محذوفة؛ darb مشعّث (فالاتن − − −) common.
- مجزوء: فاعلاتن مستفعِ لن؛ darb صحيح، مخبون مقصور (فعولن).
- Hashw: خبن everywhere (فعِلاتن، متفعِ لن).
- Feel: light, quick, elegiac and lyrical.
- مفتاح: يا خفيفًا خفّت به الحركاتُ — فاعلاتن مستفع لن فاعلاتُ

## المضارع — مفاعيلُ فاعِ لاتن (مجزوء وجوبًا) — rare
- مفتاح: تُعدّ المضارعاتُ — مفاعيلُ فاعلاتُ

## المقتضب — مفعولاتُ مفتعلن (مجزوء وجوبًا) — rare
- First foot usually مطوي (فاعلاتُ − ب − ب).
- مفتاح: اقتضب كما سألوا — مفعولاتُ مفتعلُ

## المجتث — مستفعِ لن فاعلاتن (مجزوء وجوبًا)
- Darb: صحيح، مخبون، مشعّث.
- مفتاح: إن جُثّت الحركاتُ — مستفع لن فاعلاتُ

## المتقارب — فعولن فعولن فعولن فعولن (×2)
- تام: arud صحيحة/محذوفة؛ darb صحيح، مقصور (فعولْ)، محذوف (فعو)، أبتر (فعْ).
- مجزوء: three feet.
- Hashw: قبض (فعولُ) common.
- Feel: martial, marching.
- مفتاح: عن المتقارب قال الخليلُ — فعولن فعولن فعولن فعولُ

## المتدارك / الخبب — implementation's shared-family label
- The engine groups فاعلن and supported فعِلن/فعْلن patterns under one family. This does not settle theoretical distinctions between المتدارك and الخبب or authorize every combination in every convention.
- Darb may be مذيّل (فاعلانْ) or مرفّل (فاعلاتن).
- Feel: galloping, very common in modern and song poetry.
- مفتاح: حركات المحدث تنتقلُ — فعِلن فعِلن فعِلن فعِلُ

---

## Quick identification hints (hypotheses to check)

These shortcuts do not establish a meter. Scan the complete supplied sequence and verify pronunciation and licensed forms; use manual, provisional analysis if execution is unavailable.

- Count letters: a tawil verse is long (≈ 46–48 arudi letters); مجزوء forms are short.
- Starting ب − (watad) → الطويل، الوافر، الهزج، المتقارب، المضارع.
- Starting with ب ب ب (three moving letters) → almost certainly الكامل (or خبن/خبل in other meters).
- Sadr ending in فعِلن ب ب − with مستفعلن فاعلن inside → البسيط.
- All feet of one kind repeated → الكامل/الرجز/الرمل/الهزج/المتقارب/المتدارك/الوافر families.

# Arabic poetry skill: source findings

Read 2026-10-14. These findings support writing, revising, and identifying Arabic poetry. Source claims and proposed agent behavior are distinguished below. This is a maintainer research note, not an exhaustive prosody manual.

The deeper follow-up includes [five authored craft works and two contemporary studies](arabic-poetry-craft-2026-10-14.md), [five distinct existing skill designs](arabic-poetry-similar-skills-2026-10-14.md), [computational evaluation and analyzer research](arabic-poetry-computational-2026-10-14.md), and a [validation record](arabic-poetry-validation-2026-10-14.md). Their useful findings are incorporated into the served skill's references; these maintainer notes are not needed to install it.

## 1. Scan pronunciation before identifying the meter

Primary teaching source: Imam Muhammad ibn Saud Islamic University, Dr Badr Muhammad al-Rashid, [مقدمة في العروض: علم أوزان الشعر وقافيته](https://units.imamu.edu.sa/deanships/admission/activities/Pages/news10.aspx), sections **القاعدة العامة في الكتابة العروضية**, **القواعد التفصيلية**, **الرموز**, and **تقطيع الشعر**.

The page teaches a pronunciation-based sequence: write the pronounced form, mark moving/static letters, then match feet and candidate meters. It explains splitting shadda, converting pronounced tanwin into a static nun, restoring spoken unwritten long vowels, dropping hamzat al-wasl in connected speech, solar-lam assimilation, and removing unpronounced spelling letters. A pronoun ha is lengthened only if pronounced that way. It describes lengthening the moving final rhyme letter into a matching long vowel.

Agent implications: preserve the original spelling, display assumed vocalization separately, then show **الكتابة العروضية → الرموز → التفعيلات**. Explain symbols before using them: the source uses `/` for a moving letter and `0` for a static letter; the skill uses `1` and `0` respectively. Do not silently mix character and syllable notation. Start/connected-speech rules differ. Do not automatically lengthen every pronoun ha or mechanically freeze every final vowel: identify the intended reading and rhyme ending first. Unknown vocalization should yield alternatives or a narrowly targeted question, not an invented confident result.

## 2. Legal variations depend on meter and position

Primary authored book: Ahmad al-Hashimi, [ميزان الذهب: مقدمات علم العروض](https://www.safahat.org/books/50259706/1.1/), **المقدمة الثانية: التفاعيل العشرة**, **المقدمة الثالثة: الزحاف والعلل**, **المقدمة الرابعة: الزحاف المفرد**, **المقدمة السادسة والسابعة: العلل**, and final footnote on **كيفية التقطيع**. [Book landing page](https://www.safahat.org/books/50259706/) explicitly identifies the text as public domain and legally available from Hindawi.

The book distinguishes causes and pegs inside feet, including the differently structured `مستفعلن`/`مستفع لن` and `فاعلاتن`/`فاع لاتن`. It defines non-obligatory zihaf, with examples such as khabn (`فاعلن → فَعِلُنْ`), idmar (`متفاعلن → مُتْفاعلن`), and qabd (`فعولن → فعولُ`; its table also gives `مفاعيلن → مفاعلن`). The cutting procedure compares pronounced moving/static letters against the balance foot by foot.

Agent implications: a changed foot is not automatically a broken meter. Name the permitted variation and its location. Conversely, arbitrary changes cannot be excused by merely saying “زحاف”. Use the specific meter chapter when validating a candidate; separate **الحشو / العروض / الضرب** and check both hemistichs.

Edition caution: some general summaries are inconsistent with tables/later chapters. For example, the introduction's list of meters admitting qabd omits الطويل, while its الطويل chapter allows it. Do not treat a single broad list as a universal rule or copy all tabulations without cross-checking.

## 3. Check the actual meter form, not only a mnemonic

Primary source: al-Hashimi, [دروس علم العروض البحور](https://www.safahat.org/books/50259706/1.2/), **البحر الأول: الطويل**, **خلاصة بحر الطويل**, **البحر السادس: الهزج**, and footnotes **١٣** and **١٧**.

The الطويل chapter distinguishes its underlying pattern from the accepted `مفاعلن` عروض, its three ضرب forms, and the exception for تصريع. Footnote ١٣ describes حذف in the first متقارب عروض as non-obligatory; footnote ١٧ permits قطع in the متدارك حشو. Thus blanket “every علة is obligatory and only at endings” is unsafe. Check the chapter-specific forms and exceptions.

Verified public-domain teaching example, supplied without a named poet in the الهزج chapter:

> هَزَجْنَا فِي أَغَانِيكُمْ ** وَشَاقَتْنَا مَعَانِيكُمْ

| Part | Pronounced grouping | Letters | Feet |
| --- | --- | --- | --- |
| الصدر | هَزَجْنَا فِي / أَغَانِيكُمْ | `1101010 | 1101010` | مفاعيلن مفاعيلن |
| العجز | وَشَاقَتْنَا / مَعَانِيكُمْ | `1101010 | 1101010` | مفاعيلن مفاعيلن |

Result: الهزج, two feet per hemistich. Here `1` marks a moving letter, `0` a static letter, and ` | ` separates feet; read the symbol string from left to right.

Additional verified example: Al Jazeera Learning, [قفا نبك](https://learning.aljazeera.net/en/languageofmedia/%D9%82%D9%81%D8%A7-%D9%86%D8%A8%D9%83), has a full worked الطويل scansion. Both halves and the third-foot فعولُ in the عجز match the skill's transcription. The pronounced ending حَوْمَلِي has لام as روي and terminal ياء as وصل.

## 4. Distinguish rhyme from its anchor letter

Primary source: al-Hashimi, [في حروف القافية الستة](https://www.safahat.org/books/50259706/2.1/), sections **الروي**, **الوصل**, **الردف**, **التأسيس**, **الدخيل**, and **نظم المبحث الأول**.

The rhyme comprises more than its anchor letter: the book distinguishes روي, وصل, خروج, ردف, تأسيس, and دخيل. Its verse summary locates the rhyme from the final two static letters back to the preceding moving letter and allows it to occupy part of a word, a whole word, or more. The moving روي may generate a following long vowel as وصل. Thus the last written character is not necessarily the روي, and the final word is not automatically the entire قافية.

Agent implication: report **الروي** separately from the pronounced **القافية**; analyze supporting rhyme letters/movements only when relevant. A single line supports a local rhyme analysis, not proof that a whole poem consistently respects its rhyme obligations.

## 5. Modern forms need their own criteria

Primary terminology owner: Cairo Arabic Language Academy, [الشعر المرسل والتفعيلة](https://www.arabicacademy.gov.eg/ar/%D9%85%D8%AD%D8%B1%D9%83-%D8%A7%D9%84%D8%A8%D8%AD%D8%AB/%D9%85%D8%B9%D8%AC%D9%85/dic-383/%D8%A7%D9%84%D8%B4%D8%B9%D8%B1-%D8%A7%D9%84%D9%85%D8%B1%D8%B3%D9%84-%D9%88-%D8%A7%D9%84%D8%AA%D9%81%D8%B9%D9%8A%D9%84%D8%A9), entries **الشعر المرسل** and **التفعيلة**.

The Academy distinguishes metered unrhymed verse (مرسل) from تفعيلة: the latter uses Khalil's feet within a meter but varies their counts between lines; rhyme may vary or be omitted. Consequently, absence of a fixed rhyme does not establish prose poetry, and varying line lengths do not establish lack of meter.

Scholarly primary analysis: Dr Hamdi al-Jabali, **قصيدة النثر**, Hebron University, December 1996, [author's university-hosted PDF](https://staff.najah.edu/media/sites/default/files/_%D8%A7%D9%84%D9%86%D8%AB%D8%B1.pdf), printed p. **9** (PDF p.9) under **نظرية قصيدة النثر**, printed p. **12** (PDF p.12) on sentence and rhythm.

The paper documents prose-poem theory as removing obligatory meter/rhyme while shaping its own rhythm through sentence structure, parallelism, repetition, tone, and sounds. It discusses concentration and composition. The author's eventual rejection of the genre and the quoted proponents' claims of superiority are competing critical positions, not mechanical standards. Use the documented formal distinction without adopting either verdict.

Agent implications: give عمودي, تفعيلة, and قصيدة النثر equal creative standing. For prose poems, critique image, movement of thought, diction, compression, sentence rhythm, and sound; do not repair them by imposing a Khalilian meter. “شعر حر” is used ambiguously, so name the operational form or ask which meaning the user intends. Short fragments and accidental foot-like passages cannot conclusively classify the whole work.

Source identity caution: [Hindawi book 31462469, قضايا الشعر المعاصر](https://www.safahat.org/books/31462469/) is by **أحمد زكي أبو شادي**, not **نازك الملائكة**. A shared title is not evidence for the latter's theory. No direct Nazik edition was verified in this pass.

## 6. Dialectal poetry requires pronounced dialect and a tradition

Primary authored historical source: al-Hashimi, [في فنون الشعر الجارية على ألسنة العامة](https://www.safahat.org/books/50259706/3.3/), **الفن الأول: الزجل**.

The chapter discusses forms in vernacular language without classical case endings and both tune-led forms and vernacular compositions on classical meters. This supports retaining actual dialect pronunciation rather than adding classical case endings. It does not establish a complete correspondence between modern Nabati, zajal, and Khalilian meters.

Agent implication: preserve dialect. Identify region/tradition and request an intended reading or audio when written dialect is ambiguous. Avoid declaring a named Nabati meter merely by relabeling a superficially similar classical foot sequence. Exact dialectal taxonomies were not verified; this should be an explicit support boundary in the initial skill.

## Output contract to encode

For an identification request: **form → assumed reading → pronounced writing → symbol pattern → feet → candidate meter and licensed changes → rhyme/روي if requested → confidence and missing evidence**. For a repair: show original and minimal proposed revision, state the reason, then rescan changed metered lines. Literary suggestions should be identified as choices rather than formal errors. For composition: meet the user's chosen form; show verification honestly and do not claim a whole poem's meter is sound after checking only one example line.

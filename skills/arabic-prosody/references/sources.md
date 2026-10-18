# Sources and implemented coverage

Use pronunciation and the intended poetic convention to judge a scan. The implementation is a rule-based diagnostic tool; a low alignment cost does not prove that its inferred reading is intended or that every classical rule has been encoded.

## Primary references

- Ahmad al-Hashimi, [ميزان الذهب: مقدمات علم العروض](https://www.safahat.org/books/50259706/1.1/), sections on feet, cause/peg structure, and الزحاف والعلل. Check arithmetic and structural variants rather than importing changes solely from matching binary strings.
- Al-Hashimi, [دروس علم العروض البحور](https://www.safahat.org/books/50259706/1.2/), the relevant meter's chapter. The الطويل summary conditions تصريع on a first verse with matching ending weight and rhyme; المديد has paired عروض/ضرب forms. The full البسيط summary gives فعِلن for عروض outside تصريع and فعِلن/فعْلن for ضرب. Generic independent ending lists are insufficient for those cases. Further pair and position coverage remains limited to what the implementation actually encodes.
- Al-Hashimi, [حروف القافية](https://www.safahat.org/books/50259706/2.1/). Read the pronounced ending before deciding الروي، الوصل، الردف، التأسيس and named defects. The spelling-based audit remains provisional.
- Imam University, [مقدمة في العروض](https://units.imamu.edu.sa/deanships/admission/activities/Pages/news10.aspx), الكتابة العروضية and تقطيع الشعر. Preserve pronounced long vowels and tanwin. A foot continuing across a visual break does not authorize deleting a pronounced tanwin nun.
- Muslih Abdelfattah Najjar, [التدوير في شعر التفعيلة العربي: شعر معين بسيسو أنموذجًا](https://ojs.aiou.edu.pk/index.php/jar/article/download/1357/1227/3452), 2023, PDF pp.6–11. Distinguish semantic continuation, divided feet/words, and explicit الوصل/الوقف choices. Its terminology is a scholarly treatment, not an exhaustive universal classification.

These links are evidence for rule checks, not proof that all rules in each work are implemented. They supplement the initial contribution; the supplied fixture list is not a comprehensive source-verified poetry corpus.

## Validation limits

The supplied classical set contains 24 examples spanning the 16 named meters, plus a taf‘ila sample and ending ambiguity. They are a regression set, not a measured accuracy rate for unseen poems. Cross-runtime parity checks selected forms, sound patterns, errors, and feet; two implementations agreeing does not establish linguistic correctness.

The integration audit adds negative cases for phonetic preservation, forced meter handling, context-dependent ending rules, test failure exits, stale asynchronous saves, isolated conversations, and added-tashkeel-only updates. Real host database and model capabilities still require testing in their supported environment.

Treat المتدارك/الخبب as this implementation's shared-family convention. Do not present it as settling disputed theory, or call an unsupported dialect, mixed-foot poem, or prose poem broken merely because it does not match these tables.

## Rule map

Checked 2026-10-17/18. Each rule the scanner and the Diwan apply, the source that grounds it, and where it lives in the code. Where a rule is later practice, a licence, or an engineering choice rather than a classical table entry, the table says so.

Code locations: meter tables in `scripts/arud/meters.py` (exported to `assets/workbench/meters.json`); pronunciation in `scripts/arud/lattice.py` and `assets/workbench/engine.js` (`buildHemistich`); classical scanning and the poem-level vote in `scripts/arud/classical.py` (`scan_line`, `scan_pair`, `rank_poem`) and `engine.js` (`scanLine`, `scanPair`, `rankPoem`); free verse in `scripts/arud/freeverse.py` and `engine.js` (`analyzeFree`); rhyme in `scripts/arud/qafiya.py`; cross-foot warnings in `scripts/arud/report.py` (`verse_warnings`, `MUAQABA`) and `assets/workbench/page.html`.

### Source keys

| Key | Source | Used for |
| --- | --- | --- |
| H1 | Ahmad al-Hashimi, [ميزان الذهب في صناعة شعر العرب: مقدمات علم العروض](https://www.safahat.org/books/50259706/1.1/) | Feet (التفاعيل العشرة), الأسباب والأوتاد, الزحاف والعلل, تقطيع |
| H2 | Al-Hashimi, [ميزان الذهب: دروس علم العروض — البحور](https://www.safahat.org/books/50259706/1.2/) | Each meter's forms, أعاريض and أضرب, permitted زحافات per meter |
| H3 | Al-Hashimi, [ميزان الذهب: في حروف القافية الستة](https://www.safahat.org/books/50259706/2.1/) | الروي، الوصل، الخروج، الردف، التأسيس، الدخيل; القافية المطلقة والمقيدة; [عيوب القافية](https://www.safahat.org/books/50259706/2.5/) |
| D | Badr al-Din al-Damamini, العيون الغامزة على خبايا الرامزة (commentary on the خزرجية), Shamela book 5421: [المعاقبة والمراقبة والمكانفة](https://shamela.ws/book/5421/28), [علل الأجزاء: الخرم](https://shamela.ws/book/5421/39), meter chapters [p.51](https://shamela.ws/book/5421/51), [p.52](https://shamela.ws/book/5421/52), [p.55](https://shamela.ws/book/5421/55) | المعاقبة/المراقبة; الخرم and the five meters that take it; the forms of individual meters |
| T | Al-Khatib al-Tabrizi, الكافي في العروض والقوافي (standard classical tables) | Cross-check of أعاريض/أضرب counts per meter |
| R | Imam Muhammad ibn Saud Islamic University, Dr Badr al-Rashid, [مقدمة في العروض](https://units.imamu.edu.sa/deanships/admission/activities/Pages/news10.aspx) | الكتابة العروضية: what is written but not pronounced and vice versa, shadda, tanwin, connected reading |
| G | Muhammad Abu al-Futouh Ghoneim, [الضرورة الشعرية](https://diwanalarab.com/%D8%A7%D9%84%D8%B6%D8%B1%D9%88%D8%B1%D8%A9-%D8%A7%D9%84%D8%B4%D8%B9%D8%B1%D9%8A%D8%A9.html) (ديوان العرب) | قطع همزة الوصل and وصل همزة القطع listed among ضرورات التغيير |
| N | Nazik al-Malaika, قضايا الشعر المعاصر (1962), chapter on the meters of free verse | Free verse built on repeated feet; the "pure" meters (الكامل، الرمل، الهزج، الرجز، المتقارب، المتدارك) and the "mixed" ones (السريع، الوافر) |
| J | Muslih Abdelfattah Najjar, [التدوير في شعر التفعيلة العربي](https://ojs.aiou.edu.pk/index.php/jar/article/download/1357/1227/3452), 2023 | تدوير across lines in free verse; foot vs word division |
| W | [تفعيلات البحر الطويل](https://mawdoo3.com/%D8%AA%D9%81%D8%B9%D9%8A%D9%84%D8%A7%D8%AA_%D8%A7%D9%84%D8%A8%D8%AD%D8%B1_%D8%A7%D9%84%D8%B7%D9%88%D9%8A%D9%84) (Mawdoo3) | Secondary check of the الطويل forms and a worked example |

### Rule → source

#### Pronunciation (الكتابة العروضية)

| Rule | Source | Note |
| --- | --- | --- |
| Count what is pronounced: moving (/) and still (0) letters; shadda = two letters; tanwin = نْ | R, H1 | |
| همزة الوصل dropped mid-line, pronounced at the start of a hemistich; اللام الشمسية assimilated, القمرية kept | R, H1 | |
| التقاء الساكنين: a long vowel before a wasl is dropped (فِي الْ → فِلْ); a sakin or tanwin before it takes a vowel | R, H1 | |
| Words written differently from their sound (هذا، لكن، ذلك، أولئك، الله، الرحمن، عمرو، داود، مائة …) | R, H1 | List in `SPECIAL` (lattice.py / engine.js) |
| ألف التنوين، ألف الفارقة (كتبوا) silent | R | |
| إشباع at the end of a hemistich; هاء الضمير and ميم الجمع lengthened after a moving letter | R, H1 | Ishbaʿ of هاء الضمير after a sakin is offered only as a costly licence |
| قطع همزة الوصل mid-line | G | **Licence (ضرورة)**: used only when it saves the meter, and reported as such |
| Supplied vowel marks stay on their original letters, including a possible typo such as «فيِ» | — | **Input-preservation boundary**: ask about a doubtful reading rather than silently relocating a vowel |

#### Feet, زحافات and علل

| Rule | Source | Note |
| --- | --- | --- |
| The 16 meters + المتدارك, their feet, and their تام/مجزوء/مشطور/منهوك/مخلّع forms | H2, T | Table `FORMS` in meters.py |
| Permitted زحافات per position (قبض، كف، خبن، طي، خبل، إضمار، وقص، خزل، عصب، عقل، نقص، شكل، تشعيث) | H1, H2 | Rarer ones carry a higher cost; none is reported as a fault |
| علل only in العروض/الضرب (حذف، قطف، قطع، قصر، حذذ، صلم، كشف، وقف، بتر، تذييل، ترفيل، تسبيغ) | H1, H2 | التشعيث in الخبب حشو is accepted practice |
| Forms marked «عند المحدثين» (مذيّل/مرفّل in تام الخبب، مقطوع in مجزوء الرجز، مقصور in مجزوء الرمل، full forms in مجزوء المتقارب، مقصور in مخلّع البسيط، مذيّل in تام الكامل) | — | **Later practice**, not in the Khalilian tables of H2/T; accepted at a higher cost and labelled |
| الخرم on the opening foot of a verse in الطويل، الوافر، الهزج، المتقارب، المضارع (أثلم، أثرم، أعضب، أقصم، أجمّ، أعقص، أخرم، أخرب، أشتر) | D (p.39–41), H1 | Rare licence; opening foot only (`kharm` in meters.py) |
| المراقبة in المضارع and المقتضب (مفاعيلن / مفعولاتُ never left unchanged) | D (p.28), H2 | Built into the variant lists |
| المعاقبة in الرمل، المديد، الخفيف، المجتث (كفّ followed by خبن) | D (p.28), H1 | Reported as a ⚠ warning |
| التصريع: an عروض following the ضرب's form only in a مصرّع opening (first verse, matching rhyme) | H2, W | Enforced in `scan_pair` / `scanPair`; also a ⚠ warning if a reading still shows it later |
| Paired عروض/ضرب forms (e.g. المديد، البسيط) | H2 | `ending_pairs` in meters.py; applied to run-on (مدوّر) verses too |
| الاعتماد in الطويل (فعولُ before the محذوف ضرب) | H2 | Reported as a gentle ⚠ note; the strength of the rule varies by source |
| البيت المدوّر (a word shared by both halves) | H1 | Accepted, shown with ↔ |

#### Poem-level decisions

| Rule | Source | Note |
| --- | --- | --- |
| One meter and one ضرب form for the whole poem; وحدة الضرب | H2, H3 | The meter is chosen by vote across all lines; ambiguous endings re-read to agree with the dominant ضرب |
| Costs, penalties and thresholds (`LONE_PENALTY`, `TADWIR_PENALTY`, `DARB_MISMATCH`, the 40 % re-check) | — | **Engineering choices** for ranking readings; they never turn a permitted form into a fault |

#### Free verse (شعر التفعيلة)

| Rule | Source | Note |
| --- | --- | --- |
| Lines built from one repeated foot, any number per line | N | Families in `FAMILIES` |
| Families used: الكامل، الرجز، الرمل، المتقارب، المتدارك/الخبب، الهزج (pure); السريع، الوافر (mixed) | N | |
| Line-final variations (تذييل، ترفيل، قصر، حذف، تسبيغ …) at the end of a line only | H1, N | `endings` in meters.py, named in `_ENDING_NAMES` |
| تدوير: a foot may run on into the next line | J | Kept only when the crossing foot is sound (engineering safeguard) |
| «=» (an overlong syllable) only in pause, i.e. at a line end | H1, R | |

#### Rhyme (القافية)

| Rule | Source | Note |
| --- | --- | --- |
| الروي، المجرى، الردف، التأسيس، الوصل; القافية المطلقة والمقيدة | H3 | qafiya.py |
| عيوب القافية: الإيطاء، الإقواء، الإصراف، السناد، اختلاف الروي | H3 | The suggestion filter deliberately blocks repeated rhyme-word spellings. This is a stricter editing heuristic, not a complete definition of الإيطاء: the source distinguishes meaning and permits repetition after an interval. The scanner cannot resolve those semantic conditions. |
| In free verse the rhyme may change or be absent | N | Not reported as a fault |

### Limits of the rule map

- The safahat.org pages of ميزان الذهب are a modern transcription; page numbers of printed
  editions are not given. Shamela page numbers refer to that edition of العيون الغامزة.
- الكافي (T) and قضايا الشعر المعاصر (N) are cited from the standard printed works; no
  online copy was read for this file.
- An independent review of the meter tables against H2/T on 2026-10-17 found them
  consistent after the corrections listed in `docs/research/arabic-prosody-validation-2026-10-15.md`.
  Rules marked medium in that review (الاعتماد، some «عند المحدثين» forms) are reported as
  notes, not faults.

# Sources and implemented coverage

Use pronunciation and the intended poetic convention to judge a scan. The implementation is a rule-based diagnostic tool; a low alignment cost does not prove that its inferred reading is intended or that every classical rule has been encoded.

## Primary references

- Ahmad al-Hashimi, [ميزان الذهب: مقدمات علم العروض](https://www.safahat.org/books/50259706/1.1/), sections on feet, cause/peg structure, and الزحاف والعلل. Check arithmetic and structural variants rather than importing changes solely from matching syllable patterns.
- Al-Hashimi, [دروس علم العروض البحور](https://www.safahat.org/books/50259706/1.2/), the relevant meter's chapter. The الطويل summary conditions تصريع on a first verse with matching ending weight and rhyme; المديد has paired عروض/ضرب forms. The full البسيط summary gives فعِلن for عروض outside تصريع and فعِلن/فعْلن for ضرب. Generic independent ending lists are insufficient for those cases. Further pair and position coverage remains limited to what the implementation actually encodes.
- Al-Hashimi, [حروف القافية](https://www.safahat.org/books/50259706/2.1/). Read the pronounced ending before deciding الروي، الوصل، الردف، التأسيس and named defects. The spelling-based audit remains provisional.
- Imam University, [مقدمة في العروض](https://units.imamu.edu.sa/deanships/admission/activities/Pages/news10.aspx), الكتابة العروضية and تقطيع الشعر. Preserve pronounced long vowels and tanwin. A foot continuing across a visual break does not authorize deleting a pronounced tanwin nun.
- Muslih Abdelfattah Najjar, [التدوير في شعر التفعيلة العربي: شعر معين بسيسو أنموذجًا](https://ojs.aiou.edu.pk/index.php/jar/article/download/1357/1227/3452), 2023, PDF pp.6–11. Distinguish semantic continuation, divided feet/words, and explicit الوصل/الوقف choices. Its terminology is a scholarly treatment, not an exhaustive universal classification.

These links are evidence for rule checks, not proof that all rules in each work are implemented. They supplement the initial contribution; the supplied fixture list is not a comprehensive source-verified poetry corpus.

## Validation limits

The supplied classical set contains 24 examples spanning the 16 named meters, plus a taf‘ila sample and ending ambiguity. They are a regression set, not a measured accuracy rate for unseen poems. Cross-runtime parity checks selected forms, sound patterns, errors, and feet; two implementations agreeing does not establish linguistic correctness.

The integration audit adds negative cases for phonetic preservation, forced meter handling, context-dependent ending rules, test failure exits, stale asynchronous saves, isolated conversations, and added-tashkeel-only updates. Real host database and model capabilities still require testing in their supported environment.

Treat المتدارك/الخبب as this implementation's shared-family convention. Do not present it as settling disputed theory, or call an unsupported dialect, mixed-foot poem, or prose poem broken merely because it does not match these tables.

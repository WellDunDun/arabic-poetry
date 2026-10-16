# Arabic prosody contribution audit

Reviewed on 2026-10-15 for integration into `WellDunDun/arabic-poetry`.

## Provenance and scope

Contributor: [Firas F. Khabour (@firaskhabour)](https://github.com/firaskhabour), using the name supplied in his README. Source: [add-arabic-prosody](https://github.com/firaskhabour/arabic-poetry/tree/466da42833b2a575543c2a68658dcfbcd01352d2).

Original commits retained in the integration branch:

- [`ffd4dbf`](https://github.com/firaskhabour/arabic-poetry/commit/ffd4dbf1a4ae495fc6bb5645a94152ab8c3cdf2f): Arabic prosody skill, scanner, Diwan workbench, exporters, references and fixtures.
- [`466da42`](https://github.com/firaskhabour/arabic-poetry/commit/466da42833b2a575543c2a68658dcfbcd01352d2): plugin manifest update.

Compared against upstream `b2349117a6eec0e51f0aaabdba968a0f48a2e164`. The contribution adds a second skill alongside the existing composition and interpretation skill. The review used the original user brief, repository authoring rules, and the contribution's declared behavior; no separate product specification was supplied.

Separate standards and behavior reviews inspected the Python scanner, browser engine, asynchronous workbench state and tests. Repairs are a separate maintainer commit so the contribution's original authorship remains visible.

## Standards findings

| Priority | Finding | Repair and evidence |
| --- | --- | --- |
| P1 | An older asynchronous save could clear the dirty flag for a newer draft, allowing a database snapshot to overwrite that draft. | Track edit revisions, copy save payloads, and acknowledge only the saved revision. Deterministic delayed-save and snapshot regressions exercise production functions. |
| P2 | Model conversations, pending tools and alternatives could survive a poem switch or target a changed draft. | Scope requests and responses to poem, text, mode, meter, revision and selection session; reset conversations on selection changes and reject stale tool execution/results. |
| P2 | A diacritization response could replace wording, remove existing marks, or overwrite edits made during the request. | Accept added tashkeel only, preserving base text, existing marks and line structure; reject stale responses. Positive and negative production-function regressions cover these cases. |
| P2 | The Python fixture runner printed failures but exited successfully; the browser test did not actually compare Python output. | Make failures exit nonzero and compare expected fixtures plus Python/JavaScript patterns, errors and feet. Deliberately wrong fixture expectations produce exit status 1 in both runners. |

## Behavior findings

| Priority | Finding | Repair and evidence |
| --- | --- | --- |
| P1 | Enjambment could delete the pronounced nun of tanwin, falsely accepting `يَدٌ\nتَاهَتْ` as sound Kamil. | Preserve tanwin in both engines; test that this reading has errors in Kamil and remains sound under the supported Hazaj reading. |
| P1 | Alif before a paused final consonant was deleted: `كِتَابْ` became `كتب`, changing the ending classification. | Preserve `كتاب` / `1100`; assert the مقصور ending in Python and JavaScript. |
| P1 | Conditional تصريع endings were accepted without first-verse, matching-weight and rhyme context. | Add contextual paired-half scanning; reject inappropriate standalone and later-verse use. Include matching/mismatching and historical opening-verse regressions. |
| P1 | Independently enumerated مديد endings admitted incompatible عروض/ضرب combinations. | Encode and enforce supported ending pairs in both engines and exported meter tables; add accepted and rejected pair regressions. |
| P2 | Full البسيط accepted `فاعلن` endings outside the forms stated in the checked source. | Remove those two unsupported entries; test both halves and the browser verifier. |
| P2 | Forcing a free-verse family outside the top three candidates crashed with `KeyError: 'lines'`. | Filter before summarizing; check both text and JSON command output. |
| P1 | The standalone HTML lacked a UTF-8 declaration. Plain HTTP delivery garbled Arabic and caused script parse failures. | Declare UTF-8 and rebuild the bundled page; a browser reload reports UTF-8, correct Arabic, retained content, a meter result and no page errors. |

The meter-rule repairs were checked against the primary references linked in [the installed skill's sources](../../skills/arabic-poetry/references/SCANNER-SOURCES.md), especially al-Hashimi's الطويل, المديد and البسيط chapters. The implemented coverage remains narrower than the complete classical tradition. The تصريع rhyme guard now considers candidate ردف and تأسيس as well as روي and known مجرى; unknown vocalization remains provisional. A single-form regression also checks the absence of صدر without imposing a paired-ending constraint.

## Validation

- Existing poetry checker: eight unit tests pass.
- Prosody fixtures: 24 classical examples, a taf‘ila sample and ending ambiguity pass.
- Ten added scanner regression methods and workbench-state regressions pass.
- Python/browser parity now asserts meter, form, exact matches, sound patterns and feet for the fixture set.
- Both skill packages pass `skills-ref` validation; plugin JSON, relative Markdown links and whitespace checks pass.
- Rebuilt browser bundle from sources and exported meter tables.
- Real browser: create an Arabic poem, identify الطويل, inspect scansion, reload and retain the poem in local storage. No page errors on the final reload.
- CLI Word/text export: generated files, parsed all DOCX XML parts, and checked Arabic content and RTL paragraph markup.

## Remaining limits

This is regression evidence, not an unseen-poem accuracy benchmark or an exhaustive audit of every meter variant. Ranking and confidence are heuristic; rhyme analysis starts from spelling and requires pronunciation review. Agreement between two implementations does not establish linguistic correctness.

Actual Claude host sampling, database synchronization and host downloads were not exercised end to end. Their state transitions have local regressions. In an ordinary browser, manual editing and local storage worked; Word download displayed the unavailable-host fallback. CLI Word export worked. Optional PDF export was not tested. README and skill instructions now describe these host and runtime requirements, CDN dependencies and coverage limits.

Merge policy: keep the contributor's original commits and linked README credit; merge only the reviewed integration head after local validation. Do not modify the contributor's fork or its branch.

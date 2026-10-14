# Arabic poetry: computational evidence and tool audit

Read 2026-10-14. Papers were inspected beyond their abstracts. These findings inform a portable agent workflow, not a requirement to install or train their models. No external analyzer was executed in this research pass.

## Instruction-guided generation and evaluation

Sadallah et al., [Instruction-Guided Poetry Generation in Arabic and Its Dialects](https://arxiv.org/abs/2604.27766), v1, 30 April 2026. Read [PDF](https://arxiv.org/pdf/2604.27766), §4.2, §5.1, Limitations, Appendix F; [authors' code](https://github.com/mbzuai-nlp/instructpoet-ar).

The study separates generation, continuation, revision, and analysis. It assesses compliance, fluency, coherence, and poetic quality separately. Its generation evaluation uses 100 prompts, four model outputs per prompt, and two Arabic-speaking evaluators with shuffled, anonymous model identities. Revision is harder in its evaluated setting because it must retain meaning while recovering formal constraints. Important limit: dialectal instructions do not imply natively dialectal poetic content; the authors say the corpus is predominantly historical MSA. Automated semantic overlap and rhyme metrics do not establish a complete metrical or literary verdict.

Practical adoption: track the user's independent constraints, distinguish continuation from rewriting, and assess technical correctness separately from literary effect. Do not advertise model scores as this skill's validation or assume modern/dialect coverage from the paper's title.

## Interpretation has several independent dimensions

Al Ghallabi et al., [Fann or Flop](https://aclanthology.org/2025.emnlp-main.1023/), 2025; read [full text §3](https://arxiv.org/html/2505.18152v2), particularly evaluation criteria and metric limitations. [Evaluation code](https://github.com/mbzuai-oryx/FannOrFlop).

The authors distinguish literal comprehension, thematic/emotional depth, cultural/historical appropriateness, stylistic sensitivity, and explanatory coherence. They discuss the limits of surface overlap for legitimate interpretive variation. Version/metadata caution: anthology abstract says 21 genres while the inspected v2/full-paper abstract says 14; do not adopt a taxonomy from those inconsistent counts.

Practical adoption: build an evidenced literal reading before an interpretation, anchor rhetorical claims in actual words and syntax, separate external historical facts from hypotheses, and allow plausible alternatives. This benchmark concerns understanding, not proof of generated poems' metrical validity or originality. Agent self-review is not human expert evaluation.

## Repair a bounded phrase in context

Elzohbi and Zhao, [Tahḏīb: A Rhythm-Aware Phrase Insertion for Classical Arabic Poetry Composition](https://aclanthology.org/2025.arabicnlp-main.15/), 2025; read [PDF](https://aclanthology.org/2025.arabicnlp-main.15.pdf), introduction and §§3.1–3.2.

The task reconstructs or inserts words under a target rhythmic pattern while using surrounding verse as context. The authors frame it as co-creative assistance, retaining the author in the process. Their fully vocalized grapheme transformation makes the input-to-rhythm relation explicit. This model study does not establish universal poetic license rules or guarantee arbitrary local repairs preserve meaning.

Practical adoption: identify the faulty span, keep sound surrounding material where possible, compare a small number of meaningful repairs, and rescan the whole affected line. Foot boundaries may cross words, so choose a grammatical repair span rather than deleting letters at a foot boundary.

## Existing analyzers are useful evidence layers

| Primary source inspected | Direct observation | Workflow implication |
| --- | --- | --- |
| [Aruudy README](https://github.com/linuxscout/aruudy), [prosody.py](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/prosody.py), [meter.py](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/meter.py), `normalize`, `BahrForm.validate`, `search_bahr` | README recommends full vocalization. Normalizer inserts inferred marks. Search returns the first successful meter; the inspected form method consumes each configured foot then returns parts without an explicit leftover check. | Preserve supplied and tool-normalized text separately. Verify whole-input consumption and competing candidates. Static code inspection is not a runtime defect reproduction or exhaustive audit. |
| [Qawafi repository](https://github.com/ARBML/qawafi), Testing example | Exposes diacritized text, symbol pattern, nearest patterns, meter, rhyme, era, and theme; the example opts into `override_tashkeel=True`. | Inspect each layer; do not silently overwrite user vocalization or equate nearest patterns and predicted eras with verified exact fits and provenance. This is a library/platform, not an agent skill. |
| [Ashaar paper](https://arxiv.org/abs/2307.06218), 2023, abstract and framework overview | Separates meter/theme/era classification, diacritization, عروض prediction, and conditional generation. | Use a staged analysis record instead of one opaque verdict. The existence of a research model does not supply an installed dependency or current accuracy guarantee. |

## Concrete change rationale

- Add literary close reading, separate technical/literary review, and preserve intent during continuation.
- Strengthen pronunciation and tool-normalization records, candidate ambiguity, exact sequence coverage, and mismatch localization.
- Add a small standard-library checker for a declared, fully expanded عروض transcription and its annotated foot strings. It checks arithmetic and coverage only; it does not infer vocalization, validate meters, or certify poetic quality.
- Include negative cases for dropped trailing sounds, false foot patterns, ambiguous fragments, and prose-poem requests. A useful local trial tests these failure modes rather than merely checking headings or frontmatter.

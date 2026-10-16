# Consolidation comparison, 2026-10-16

The combined package retained the behaviors covered by this small trial and answered the preliminary-analysis request without the approval interruption observed with both old skills installed. This is regression evidence for consolidation, not evidence of generally better poetry or improved scanner accuracy.

## Setup

- Base: `3286f489881b9fbc5bb2fc2bca7dd064835b1a4c`.
- Requests and semantic criteria were frozen in commit `e1f91bf` before editing the skills. See [requests](../../prompts.json) and [rubric](../../rubric.json).
- Four fresh execution agents used the inherited parent model/configuration, without model overrides. Exact backend identity and reasoning level were not exposed in the record. Each ran eight sequential requests sharing its own context; it could not see the other conditions, rubric, proposed changes or prior findings.
- Conditions: original poetry only, prosody only, both current packages, and combined poetry. Packages were isolated and their source content hashes preserved. Execution was restricted to local filesystem, Python and Node, with no browser, network, hosted APIs, publishing, installs or global font changes.
- The lead reviewed actual responses, commands and artifacts against the frozen criteria. The semantic grader knew the condition names; this was not blinded grading. [Grades](grades.json) contain criterion-level reasons, and [run metadata](runs.json) binds the corpus, package hashes and response records.

After PR review restored links to the retained transcription/rhyme references, a fifth fresh execution agent reran the combined condition on the revised package using the same eight requests and tool limits. The combined records below are that latest run, re-reviewed against the original criteria. The initial combined run is retained in Git at `29f136c9ec7fb4f6272e5afd1a012aafd075cfb0`; the three baseline records are unchanged. Both combined runs met all eight cases. This follow-up was required by the package-content check, not an attempt to resample a failing result.

## Results

Pass means all applicable frozen behavior criteria passed. It does not imply identical capabilities or a successful unavailable integration.

| Request | Original only | Prosody only | Both current | Combined |
| --- | --- | --- | --- | --- |
| Five-line prose composition | Pass | Pass | Pass | Pass |
| Grounded close reading without inferred death | Pass | Pass | Pass | Pass |
| Classical scansion, English answer, rhyme distinction | Pass | Pass | Pass | Pass |
| Brief provisional reading of an unvocalized fragment | Pass | Pass | **Fail** | Pass |
| Review tashkeel and stop before meter analysis | Pass | Pass | Pass | Pass |
| Minimal repair with semantic tradeoff and before/after evidence | Pass | Pass | Pass | Pass |
| Preserve tanwin across a taf‘ila boundary | Pass | Pass | Pass | Pass |
| Honest local editor/export fallback | Pass with editor gap | Pass | Pass | Pass |
| **Cases passing the frozen criteria** | **8/8** | **8/8** | **7/8** | **8/8** |

The both-current response to `provisional-reading` asked "هل تعتمد هذا التشكيل لأفحص البحر؟" and supplied no preliminary meter reasoning. The combined response disclosed a وقف/vocalization assumption, gave a supported السريع candidate and limited the conclusion to the fragment. It still paused for the separate explicit review-first request.

Prosody-only also answered the preliminary request, despite its entrypoint's blanket approval instruction. This variation is a reason to reconcile the written policy, not proof that one sample predicts future behavior.

Original-only used its arithmetic checker plus manual analysis for metrical cases. It manually created a Word file and accurately stated that no Diwan editor was installed. The other three used their bundled scanner/exporter and produced local HTML. Thus equal case scores do not mean the original package had the new engine or editor. No condition opened a browser, synchronized a hosted database or demonstrated future-chat persistence.

Raw response and command evidence:

- [Original only](original-only.responses.json), [package hashes](original-only.package-hashes.json).
- [Prosody only](prosody-only.responses.json), [package hashes](prosody-only.package-hashes.json).
- [Both current](current-both.responses.json), [package hashes](current-both.package-hashes.json).
- [Combined](combined.responses.json), [package hashes](combined.package-hashes.json).

[Artifact hashes](artifacts.json) record the actual temporary outputs inspected during grading. Generated HTML/DOCX files are intentionally outside the repository. All listed artifacts existed. Every condition's DOCX passed ZIP integrity, XML parsing, exact Arabic title/verse-content checks and RTL paragraph checks. Visual Word rendering was not tested. The review-only responses differ in the connected-reading vocalization of «أبع»; the frozen criteria cover preservation and review behavior, not expert validation of every added vowel.

## Software and relocation checks

- [Before](software-before.json) and [after](software-after.json): eight original arithmetic-checker tests, ten scanner regression methods, 24 classical fixtures plus taf‘ila/ending checks, Python/JavaScript parity and workbench-state regressions all pass.
- [21 scanner/exporter/browser/font implementation files](unchanged-implementation.json) are byte-identical after relocation. This change does not revise the scanner algorithm. Its historical regression and accuracy limits still apply.
- Building at the new package path reproduces the original `diwan.html` and `meters.json` hashes.
- Skill reference and skill-creator validators, plugin JSON, relative Markdown links and whitespace checks pass. The shared entrypoint is 66 lines.
- `python3 evals/check_results.py` checks 32 current response records, corpus bytes and baseline manifests against pinned Git history, criterion/case status consistency, artifact-inventory correspondence/checksum and current combined-package identity. It does not grade meaning or poetry or recreate missing artifacts.
- Fifteen evidence acceptance/mutation regressions pass. Thirteen of those tests reproduced checker failures on the originally reviewed implementation. They now reject coordinated edits to corpus/baseline metadata, contradictory case grades and missing or inconsistent artifact inventories while accepting valid records and applicable `not_applicable` judgments. The [review dispositions](../../../docs/research/pr-2-review-2026-10-16.md) explain each finding and correction.
- [Review follow-up check outputs](review-checks.json) record the final checker tests, existing software suites and package validators after the fixes.

Execution caveat: early both-current Python calls wrote bytecode caches and the exporter used its default transient temporary directory; the exporter was rerun with temporary files under the assigned output directory. Hash checks confirm all original package source files remained unchanged. Later combined runs disabled bytecode and used an output-local temporary directory.

## What this does not establish

There is one sample per case/condition, shared context inside each batch, no independently recorded sampling seed, no exact backend identifier and no expert literary-quality assessment. Some metrical inputs overlap worked examples or existing regressions. Providing installed package paths also bypasses a real host's automatic skill-discovery mechanism. Do not report an accuracy percentage, statistical improvement or a routing benchmark from these results.

Before stronger claims, use fresh per-case sessions, multiple samples, held-out poetry, dialectal and stanza traditions, metered composition/continuation and expert Arabic review. Actual host sampling/storage/download integrations, browser UI behavior at the new path and PDF conversion remain untested in this trial. The executable browser assets are unchanged; that is relocation evidence, not a new live integration test.

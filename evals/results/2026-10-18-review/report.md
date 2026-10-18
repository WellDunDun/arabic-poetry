# CodeRabbit follow-up trial

The updated combined package is `2049f56a5b2e99f8523be71826657e9b6010af4d` (combined-pr2). Only `skills/arabic-poetry/references/PROSODY.md` differs from the previous evaluated package: it identifies the integrated scanner rather than a separately installed companion. A new independent worker completed all eight unchanged frozen requests on these exact bytes. Requests, criteria and baseline Git pins are unchanged.

| Condition | Cases meeting all frozen criteria | Execution |
| --- | --- | --- |
| Original-only | 8/8 | Reused from earlier 2026-10-18 trial |
| Prosody-only | 8/8 | Reused from earlier 2026-10-18 trial |
| Both frozen baseline skills | 8/8 | Reused from earlier 2026-10-18 trial |
| Updated combined package | 8/8 | New follow-up execution |

Combined failures: none under the frozen criteria.

Workbench-export evidence is specific to each condition. Original-only verifies local TXT and reports its missing editor/exporter; the other conditions describe their actual local editor and Word files. Evidence prose was corrected in the earlier grade metadata as requested by CodeRabbit, with no changes to raw responses, criteria or verdicts. This follow-up does not relabel those older executions.

The new worker received only the assigned package and requests. Cases share one context, exact backend/model settings were not independently exposed, and lead semantic grading was not blind. These small trials do not establish general accuracy, literary quality or a measured improvement. Raw responses and actual command receipts, including failures if any, remain available. Package hashes match the current branch, and artifact hashes/sizes were verified while recording; temporary paths are provenance rather than durable downloads.

No browser opening, live host connection, shared storage, PDF conversion or visual Word-layout test was performed. Actual local HTML/DOCX files are inspected separately for script syntax and ZIP/XML/title/text. The frozen evidence validator and its mutation tests verify record consistency, not semantic correctness. See [the CodeRabbit disposition](../../../docs/research/pr-2-3-coderabbit-2026-10-18.md) and software/artifact check receipts in this directory. Both PRs remain unmerged.

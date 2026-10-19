# Poetry skill evaluations

This frozen request set compares instruction behavior while consolidating the two skills. It supplements the scanner/checker/workbench software tests; it is not a corpus accuracy benchmark or a human literary-quality study.

## Conditions

Use the same model, reasoning setting, requests and capability limits for:

1. `original-only`: `arabic-poetry` at the frozen base commit.
2. `prosody-only`: `arabic-prosody` at that commit, with no sibling skill installed.
3. `current-both`: both original packages at that commit.
4. `combined`: the proposed single package.

The base commit is pinned in `rubric.json`. Reconstruct baseline packages with `git archive` or a detached checkout, outside the candidate tree. Do not update baseline instructions to make an evaluation pass. Use isolated output directories and keep packages read-only. Do not give the execution agent the rubric, expected answers, other conditions' outputs, proposed changes, or prior review findings.

## Execution

Give an independent agent the installed package path(s), `prompts.json`, an empty output directory, and these capability limits: local filesystem, Python and Node only; no network, browser, host Artifact/database/model/download API, external publishing, package installation or global font installation. Existing local HTML can be copied and DOCX exported. Preserve the actual commands, exit status, outputs and generated artifact paths alongside each Arabic/English response. Do not claim an unexecuted command passed.

Run every case as a separate request. For economical batch trials, record that cases share an agent context and that this may influence later cases. Repeat with fresh per-case sessions and multiple samples before making a statistical or production-quality claim. The initial consolidation trial is a single batch per condition, with no access to other batches.

Grade actual responses and artifacts against the already frozen criteria in `rubric.json`; record evidence and missing capabilities. Keep exact prompt IDs and the same grading criteria across conditions. Report individual failures and execution gaps rather than only an aggregate score. Semantic grading is a reviewer judgment; string matching does not establish meaning preservation, correct scansion or poetic quality.

Commit selected raw response/command records and the comparison report under `evals/results/`. Keep generated HTML, DOCX, screenshots and temporary inputs outside the repository. Record tool/model versions when available, conditions, commit identities and content hashes so a later reviewer can distinguish a new trial from the original evidence.

Run the deterministic corpus/evidence integrity check with `python3 evals/check_results.py` once results have been recorded. It checks IDs, provenance and evidence completeness, not response quality. Maintainer validation commands and software checks live in `AGENTS.md`.

The checker reads the full corpus and baseline commit IDs pinned in its source. It compares current requests/criteria with the corpus Git objects and derives the three baseline file inventories from the baseline Git tree. Run it in a Git checkout with those commits available; shallow checkouts must fetch that history first. Validation itself performs no network fetch. Record the full corpus commit and the SHA-256 of `artifacts.json` in `runs.json`; each inventory row must match a response's case/path and have a valid digest and byte count. Temporary output files need not survive for this internal-consistency check, which cannot recreate or certify missing artifacts.

Case summaries must agree with their criterion judgments: any applicable failure makes the case fail, while `not_applicable` judgments do not turn passing applicable criteria into failures. Semantic grades still require reviewer judgment. Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals -p 'test_*.py'` for acceptance and mutation regressions, including coordinated data/checksum changes. Pinning history and cross-checking records does not make the checker tamper-proof against changes to its own reviewed code or establish poetry quality.

The [manual draft-review trial](results/2026-10-18-draft-review/report.md) and [CodeRabbit follow-up trial](results/2026-10-18-review/report.md) record earlier packages. The [earlier 2026-10-18 trial](results/2026-10-18/report.md) remains available. Earlier results remain historical; the three baseline packages and the requests/criteria stay pinned to the original Git snapshots.

The [latest workflow regression trial](results/2026-10-19-preservation/report.md) retains original baseline executions, adds final-package follow-up batches, and discloses the workers' earlier same-condition context.

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

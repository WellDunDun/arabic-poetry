# Poetry skill evaluations

## Client/session review fixes

The [current client/session trial](results/2026-10-20-review-fixes-pr11/report.md) records the fixed parent package: 73 skill tests and 31 fresh agent cases, with case-specific grades, actual commands and resulting artifacts/state. The documented examples run without optional clients. Earlier trial records remain historical.

## Automatic word suggestions

The [diwan-automatic-suggestions.json](diwan-automatic-suggestions.json) scenarios cover real browser word requests through both installed clients, no handoff dialog, acceptance-only saves, agent/browser synchronization and reload persistence. These live model calls require the user's authorization and normal client login. Use the disposable poem and frozen steps, capture the rendered menu and canonical revisions, and record failed attempts as well as the final run. `test_diwan_agent.py`, `workbench_host.js` and `workbench_state.js` provide repeatable fixture-based regressions without live calls. Native host sampling is verified separately from the CLI adapters; passing one does not establish the other. Reports must distinguish current package proof from historical runs and must not claim broad poetic accuracy.

The [earlier automatic-suggestions trial](results/2026-10-20-automatic-suggestions/report.md) includes both real client/browser flows and fresh executions of all 31 existing agent cases. Earlier trials remain unchanged.

## Shared-file CLI

The frozen [diwan-cli.json](diwan-cli.json) suite covers discovery, exact import, accepted conditional editing, stale saves, idempotent retry and restoring history as a new revision. Run `python3 evals/run_diwan_cli.py --skill /absolute/path/to/skill --output /absolute/new/temp/directory`. It uses fresh Codex sessions and disposable local files, with no browser, installs or publication. Inspect recorded commands and actual initial/final documents and history, then grade each frozen criterion. Software concurrency/crash tests and real browser checks are separate from these agent cases.

The [shared-file trial](results/2026-10-19-shared-cli/report.md) records an earlier candidate: six CLI cases, nine automatic-routing cases, four explicit-launch cases and eight unchanged poetry cases. It retains one failed pronoun-choice disclosure criterion in the poetry run. Original historical baselines are reused by reference, not rerun. Additional CLI/routing grades are recorded separately and remain reviewer judgments.

## Editor review fixes

The [editor/queue review-fix trial](results/2026-10-20-editor-fixes/report.md) records the preceding candidate. It records failing-before/passing-after regressions for deferred agent updates after cancel/close, literal and unchanged bulk saves, and actionable queue-response errors. All 31 frozen agent requests were rerun against that package. The production page/transport integration runs with `node skills/arabic-poetry/tests/workbench_shared.js`; the queue cases run through normal skill unittest discovery.

The [merge-readiness trial](results/2026-10-20-merge-readiness/report.md) records the earlier fixes for renamed server sessions and copied-document create replay. It preserves failing-before/passing-after regressions and reruns all 31 frozen agent cases, software checks and isolated installation/update checks.

The [session lifecycle trial](results/2026-10-20-session-lifecycle/report.md) records the preceding package: identity/history survive reuse of a renamed poem's old filename, server replacement and stop are serialized, fixed-port reopening waits for socket closure, and stale tokens recover without discarding uncertain live sessions. All 31 frozen agent cases, software checks and isolated install/update checks were rerun against that package; other suites retain separate frozen criteria and grades. Earlier real-browser evidence is identified separately because the browser source is unchanged.

## Pronoun-reading follow-up

The frozen [pronoun-reading.json](pronoun-reading.json) suite tests ambiguous address in Arabic and English, a supplied feminine vowel and a feminine referent fixed by context. Use the same isolated runner with `--suite evals/pronoun-reading.json`. Grade the actual reading and explanation: ambiguous readings need explicit disclosure, while supplied or context-fixed readings must remain intact without an invented question. Preserve all original words, spaces and marks, and respect line-only/review-first scope.

The [pronoun-reading trial](results/2026-10-19-pronoun-reading/report.md) records an earlier candidate. It reruns the unchanged eight poetry cases, all CLI/routing/explicit-launch cases and the four new cases. The original review-only case passes; the earlier failed execution remains in the shared-file trial. Other suites retain their separate frozen criteria and recorded semantic grades.

## Automatic drafting triggers

The frozen [diwan-auto-open.json](diwan-auto-open.json) suite tests English/Arabic composition and revision without an explicit editor request, quick interpretation and meter analysis, composition/revision chat-only overrides, and revision with no local viewer. Its baseline is PR #9 at `8fbdef835a02773d7153ba4c523b2e1de7e6663a`. Requests and criteria are independent of the older suites and were fixed before the comparison runs.

Run the same isolated runner below with `--suite evals/diwan-auto-open.json`, first against the baseline package and then against the candidate. Cases can inherit the suite's synthetic current poem, override it with their own `context`, or set `context: null` for a new poem with no existing text. The HTML evidence records the actual embedded title, text and status so generated and revised drafts can be checked separately from the original input. `initial_text_matches` compares only against that original input; it should be false for an intentional revision. Grade the complete revised/generated text against the request instead. The offline `test_diwan_launch.py` regression verifies this isolation and the resulting display receipts without calling a model.

## First-request Diwan launch

The independent suite [diwan-launch.json](diwan-launch.json) freezes English and Arabic editor requests, an unavailable-viewer case, an explicit chat-only case and software invariants. It uses a synthetic poem, not a private user transcript. Its baseline is main at `50938ba72240d810079d9d360397df256f83e4c9`. Keep this suite separate from the historical consolidation corpus below.

Run `python3 evals/run_diwan_launch.py --skill /absolute/path/to/skill --output /absolute/new/temp/directory --condition before` against the unmodified baseline, then repeat with the candidate and `--condition after`. Use the same client/model settings and frozen requests. Each case gets a fresh Codex session and a read-only copy of the package. This runs the installed Codex model and requires its normal authentication. It creates only isolated local fixtures, never a marketplace installation or hosted publication. Inspect every raw `events.jsonl`, final response and HTML artifact before grading the frozen criteria. `runs.json` retains package/corpus hashes, exit status and opener receipts. The fixture opener records a local display request; it does not render HTML. Keep these model runs distinct from real browser checks and report failures honestly.

The production software regressions run with `test_prepare_diwan.py`, `test_serve_diwan.py`, `workbench_state.js` and `workbench_host.js` as part of the maintainer checks. In a real browser, prepare two poems into one writable workspace, open each, edit one and reopen it. Check the title, exact text and marks, selection, saved-edit warning and original review status. Repeat with storage unavailable and confirm the supplied poem remains visible with a persistence warning. Browser evidence must identify the tested host. A passing local browser run does not prove Claude's sandboxed HTML preview, a ChatGPT extension, or connected AI buttons work.

## Historical consolidation corpus

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

The [earlier workflow regression trial](results/2026-10-19-preservation/report.md) retains original baseline executions, adds final-package follow-up batches, and discloses the workers' earlier same-condition context.

The earlier source-reference package is checked by [the source-cleanup trial](results/2026-10-19-source-cleanup/report.md). It references the existing frozen baseline execution files directly rather than copying them again. The test fixture materializes those references only in its temporary mutation workspace.

The [plugin lifecycle receipts](results/2026-10-19-plugin-lifecycle/receipts.json) cover real Claude Code and Codex Git marketplace installs, fixture-only patch updates, repeated updates, Codex runtime skill discovery, Claude plugin inventory and installed-file hashes. Reproduce them with `tests/plugin_lifecycle.py` as documented in `AGENTS.md`. These are distribution tests, with no model requests or poetry grading. They do not verify browser account/workspace sync or automatic update timers; temporary paths in the receipts are execution provenance.

The [GitHub install receipts](results/2026-10-19-plugin-lifecycle/github-install.json) additionally record installation from the actual review branch, including its Git commit, Codex runtime discovery, Claude plugin inventory and installed files. The recorded `source_commit` identifies the exact snapshot tested; later documentation or evidence commits may change files outside the skill directory.

The [optimization-guard lifecycle run](results/2026-10-19-plugin-lifecycle/receipts-optimization-fixed.json) records the rerun after adding a fail-fast guard against optimized Python, which disables assertions. The regression test also checks that optimized execution writes a failed receipt before launching client commands.

The [Diwan launch trial](results/2026-10-19-diwan-launch/report.md) records the earlier candidate: fresh before/after launch requests, real-browser checks and a rerun of the unchanged eight-case poetry corpus. It retains a failed sound-to-foot response criterion rather than treating passing software checks as passing poetry behavior.

The [scansion explanation follow-up](results/2026-10-19-scansion-explanation/report.md) records the earlier package against the same eight poetry requests and four launch requests. It preserves the earlier failed response and references historical baseline/browser evidence separately from the fresh candidate executions.

The [automatic-opening trial](results/2026-10-19-auto-open/report.md) records the preceding package: a fresh nine-case before/after routing comparison, all eight frozen poetry cases, and all four original launch cases. It retains source-preservation diagnostic failures separately from the final execution and keeps the earlier suites unchanged.

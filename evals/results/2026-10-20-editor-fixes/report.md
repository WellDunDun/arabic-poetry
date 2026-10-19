# Editor and queue review fixes

The candidate fixes three issues found during PR #10's readiness review: deferred agent updates now reach a clean editor after cancel/close, shared-file bulk saves preserve whitespace and make no revision for unchanged text, and queue failures use actionable CLI error codes.

Evaluated implementation: `5a36240` on `codex/diwan-cli`, following `30f377a`. [The package inventory](combined.package-hashes.json) pins the exact skill bytes. The unreleased plugin capability version remains 0.2.0. Later evidence-only commits do not change this payload.

## Failing-before and passing-after regressions

[Regression receipts](regressions.json) execute identical new tests against the pinned pre-fix production files and the final candidate. The before fixture copies the current skill/tests, then restores `page.html`, `file.js`, `diwan.py` and `serve_diwan.py` from `30f377a`. All fixtures and generated files remain outside Git.

- `workbench_shared.js` integrates the production page snapshot callback, edit actions and actual file transport using the existing DOM/scansion/fetch fixtures. Its six affected scenarios fail before the fixes; all seven pass afterward. They cover bulk/line/word close, no menu redraw while deferring, zero save requests or queued dirty state on cancel/no-op, unchanged LF/CRLF text, literal changed whitespace, and continued protection of a dirty draft against an agent update.
- The actual subprocess CLI regression fails all six response-error subcases before and passes afterward: missing/expired requests exit 4, answered/cancelled requests exit 5, and invalid ids/values exit 2. It verifies no new response is written, an existing answer remains intact and the poem version does not change.
- `RequestError` remains a `ValueError` for the existing bridge helper. Exclusive response writes and genuine I/O-error handling remain intact.

## Fresh agent results

| Suite | Result | Evidence |
|---|---|---|
| Unchanged poetry corpus | 8/8 pass | [Responses/commands](combined.responses.json), [grades](grades.json) |
| Pronoun-reading coverage | 4/4 pass | [Responses/commands](pronouns-after.json), [grades](pronouns-grades.json) |
| Shared-file CLI | 6/6 pass | [Execution/state/history](cli-after.json), [grades](cli-grades.json) |
| Automatic drafting routes | 9/9 pass | [Execution/artifacts](auto-open-after.json), [grades](auto-open-grades.json) |
| Explicit editor launch | 4/4 pass | [Execution/artifacts](launch-after.json), [grades](launch-grades.json) |

All 31 candidate cases run in fresh Codex CLI 0.155.1 sessions with read-only package copies and the same frozen requests/criteria. Execution sessions see no rubric, prior answer or expected result. The CLI default model is used without an override; the exact backend identifier is not emitted. Grading is the lead agent's semantic judgment with condition known. These are diagnostic samples, not a general accuracy or literary-quality claim. Some CLI cases initially try an unavailable `python` command, then recover with `python3`; the failed lookups remain in the command records. Historical baselines are reused by reference, not rerun. The [preceding pronoun trial](../2026-10-19-pronoun-reading/report.md) and its earlier failed poetry execution remain unchanged.

## Software, browser and distribution checks

[Software receipts](software-checks.json) include 52 skill tests, four root tests and 16 evaluation tests, all passing. All 24 scanner gold fixtures, Python/JavaScript parity, state/host/file-transport suites and seven page/transport scenarios pass. Skill validation, manifests, version consistency, local links and evaluation evidence integrity also pass. A separate ZIP/XML inspection checks the newly generated Word file's exact requested title and canonical poem text.

[Real browser checks](browser-checks.json) verify the final build through accessible UI controls and independent CLI reads: exact initial poem, an unchanged bulk Save preserving CRLF/whitespace/revision 1, an agent save deferred while the textarea stays intact, cancel adopting revision 2, and a changed literal-whitespace save reaching revision 3. The diagnostic `d8469bf` browser run additionally checked stale-save draft recovery; final-source production integration tests cover that protection. The display-request fixture cannot render HTML, so launch receipts remain distinct from the real browser checks.

[Native lifecycle receipts](lifecycle.json) cover fresh isolated Claude/Codex Git installation, update, repeated update, discovery and exact payload checks. They do not modify user plugin settings or prove browser-account sync.

Claude performed a read-only review of the focused fixes, followed by review of the final snapshot after its test-strengthening/menu suggestions were applied. Both found no merge-blocking issue in these fixes. Claude inspected code and tests; it did not execute them. Private prompts, audit text and review output remain outside Git. The executable regressions, browser checks and evals above were run separately by the lead agent.

Firas F. Khabour's credit and the core scanner, meter data, export engine and fonts remain unchanged. Safe shared writes still require cooperating macOS/Linux clients and a browser reaching the same local loopback server. HTML snapshots do not synchronize files; this change adds no cloud bridge, automatic agent wake-up or ChatGPT extension. Generated HTML/Word files and screenshots remain outside Git; temporary paths record provenance rather than permanent downloads.

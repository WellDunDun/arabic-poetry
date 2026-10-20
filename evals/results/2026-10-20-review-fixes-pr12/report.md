# Supervised runtime review fixes

Unreleased 0.3.1 combined candidate. Runtime source `471033720c3ade691ddd9e260be18c06e937efa7`. All skill digests match the evaluated package in [combined.package-hashes.json](combined.package-hashes.json). The fixed parent has its own [73-test/31-case record](../2026-10-20-review-fixes-pr11/report.md).

## Result

The parent fixes healthy reuse before client resolution, requested mode preservation and client-independent command examples. This branch adds generation-specific stop requests and supervisor shutdown receipts, protected by an owned file lease. Stop remains reachable while a replacement has no listening socket; success follows owned-worker teardown. Foreign open/serve calls cannot create a second runtime in that gap. Explicit replacements wait for shutdown acknowledgement. Initial readiness and stop deadlines cover bounded forced teardown. Crashed supervisors, orphan workers, unreadable control records and inactive old control files have regression coverage. Protocol 2 gates the changed launcher handshake.

## Verification

- 100 skill, 4 root package/version and 16 evidence/launch tests pass, 120 Python tests total. [Software receipts](software-checks.json) include exact commands/output. The initial evidence test correctly rejected the old package snapshot; after recording the fresh trial, all 16 pass.
- 24 scanner fixtures, Python/JavaScript parity, all workbench suites, skills reference validation, Claude plugin validation and synchronized JSON manifests pass.
- [Failing-before regression receipts](regressions.json) preserve the original and intermediate failures. The current full test output records their passing-after state.
- Real isolated Claude and Codex Git install, update, repeat update, discovery/inventory and exact skill-byte checks pass; see [lifecycle.json](lifecycle.json). These test explicit commands, not background download timers.
- All 31 fresh agent cases pass lead semantic review against unchanged requests and criteria: 8 poetry, 9 routing, 4 explicit launches, 4 pronoun readings and 6 CLI workflows. Actual [poetry responses/commands](combined.responses.json), [workflow responses/commands/state](agent-workflows.json), [poetry grades](grades.json) and [case-specific workflow grades](agent-workflow-grades.json) are retained. Both PR packages were run independently, 62 agent cases total.
- In the [current real-browser fixture](live-browser.json), the update remained pending with an unsaved draft and canonical revision 1. Saving retained the exact draft at revision 2, then updated at the same address and supervisor identity. Stop closed the fixture without changing the saved poem.
- Claude reviewed the corrections. Its accepted findings were reproduced and fixed; its final targeted confirmation reported no remaining finding for the last timing correction. Review transcripts remain outside Git.

## Interpretation and limits

All proposed meter claims that cite execution have actual scanner commands. The complete tawil hemistich connects pronounced groups, syllables and feet; lam as rawi is distinct from the final lengthened kasra. The ambiguous fragment remains provisional. The Kamil boundary case retains pronounced tanwin nun. Requested masculine/feminine disclosures and review/chat-only routing are preserved. Word ZIP/XML, canonical data and preloaded HTML retain the exact supplied title, text and marks in the export case.

The bounded-repair response and its actual scans meet the frozen minimal-repair criteria, but two optional text copies contain a literal backslash-n suffix instead of a newline. Those artifacts remain unchanged in the evidence. They are not asserted to be byte-exact copies of the displayed poem. The chat-only revision uses Markdown hard-break spacing and changes no files. Unavailable `python` attempts, where present, are retained with recovery through `python3`.

The English review-only request says to explain the reading then stop; its response does so without scanning or opening an editor. It does not require inventing a confirmation question. This interpretation is stated in that criterion's evidence. No criteria were changed after the run.

These are diagnostic samples with lead grading and condition known, not literary-quality or general accuracy benchmarks. The three original baseline conditions are reused unchanged. Display-opener receipts are not browser rendering; the separately recorded browser fixture is local, not account sync, public directory acceptance or a ChatGPT extension. The current browser uses manual suggestions and does not re-prove live model responses.

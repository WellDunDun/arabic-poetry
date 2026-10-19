# Final merge-readiness evaluation

PR #9 is merged. This candidate for PR #10 targets `main` and adds two fixes from its GitHub review: reopening a poem renamed within its directory shuts down its previously owned server before replacing the session receipt, and an exact create replay checks document binding before reporting success. A copied document cannot use its shared ID to open or stop the original's server.

Evaluated implementation: `f8207dd`. [Package hashes](combined.package-hashes.json) pin the exact skill, including tests. Later evidence-only commits retain that payload. The package version remains 0.2.0. Firas F. Khabour's credit, scanner, core engine, meter data, exporter and fonts are preserved.

## Regression and software evidence

[Regression receipts](regressions.json) run identical focused CLI tests on the final candidate and on a disposable skill copy with the three production Python files restored from `7db883c`. Both tests fail before and pass after: the copied create incorrectly succeeds before the fix, and the renamed poem leaves the old loopback server reachable. Cleanup uses authenticated owned-session URLs. The copied-file regression also checks dry-run rejection without file writes.

[Software receipts](software-checks.json) record 54 skill tests and four root tests passing, all 24 scanner fixtures, Python/JavaScript parity, editor state/host/file checks and seven production page/transport scenarios. The 16 evaluation/evidence tests and default evidence checker are run after recording this trial. Skill, manifest and version validation pass. A separate ZIP/XML inspection verifies the new Word artifact's exact title and vocalized poem text.

[Native lifecycle receipts](lifecycle.json) verify fresh isolated Claude/Codex Git installation, update, repeated update, discovery and matching installed payloads. Fixture version 0.2.1 is local test data, not a published release. No user plugin settings are changed.

## Fresh agent results

| Suite | Result | Evidence |
|---|---|---|
| Unchanged poetry corpus | 8/8 pass | [Responses and commands](combined.responses.json), [grades](grades.json) |
| Pronoun readings | 4/4 pass | [Responses and commands](pronouns-after.json), [grades](pronouns-grades.json) |
| Shared-file CLI | 6/6 pass | [State, history and commands](cli-after.json), [grades](cli-grades.json) |
| Automatic drafting routes | 9/9 pass | [Artifacts and commands](auto-open-after.json), [grades](auto-open-grades.json) |
| Explicit editor launch | 4/4 pass | [Artifacts and commands](launch-after.json), [grades](launch-grades.json) |

These 31 executions use fresh Codex CLI 0.155.1 sessions with read-only skill copies, unchanged requests and unchanged criteria. The default model is used; its backend identifier is not emitted. Grading is the lead agent's semantic judgment with condition known. Historical baselines and earlier failed responses remain unchanged. This is a diagnostic sample, not a general accuracy or literary-quality claim. Raw command failures remain in the receipts; the export case's initial file search returned 1 because no matching files existed, then real creation/export checks succeeded.

The [preceding real-browser checks](../2026-10-20-editor-fixes/browser-checks.json) are reused explicitly: browser sources and generated HTML are byte-identical to that tested candidate. The new server-lifecycle regressions use real loopback servers and independently check that the old server stops responding. The launch fixture records display requests without rendering HTML. No fresh browser rendering is claimed for this Python-only fix.

Safe shared writes still require cooperating macOS/Linux clients and a browser reaching the same local server. HTML snapshots do not synchronize edits. This does not prove ChatGPT browser-account sync, automatic update timers, public directory acceptance or automatic agent wake-up. Private review output and generated artifacts remain outside Git.

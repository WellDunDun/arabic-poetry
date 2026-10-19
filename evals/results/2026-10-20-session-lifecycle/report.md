# Session identity and lifecycle evaluation

PR #9 is merged. This PR #10 candidate preserves poem identity/history when a renamed poem's old filename is reused. It rejects copied identities in create/open/update previews, prevents an old server from serving the replacement poem, serializes owned-session teardown, waits for socket closure before fixed-port reuse, and retains receipts on network uncertainty. A complete response to a stale token permits recovery without stopping another poem's server. Moving to another directory requires stopping the session first.

Evaluated implementation: `20d6ab6`. [Package hashes](combined.package-hashes.json) pin the complete skill. Later evidence-only commits retain that payload. The package version is 0.2.0. Firas F. Khabour's credit and the scanner, core engine, meter data, exporter and fonts remain unchanged.

## Regression evidence

- [Identity regressions](identity-regressions.json) run identical tests on production files from `586cb0c` and the corrected implementation. Copied open/update previews, a replacement poem occupying the old filename, and inaccurate stop-after-rename results fail before and pass after.
- [Shutdown regressions](shutdown-regressions.json) fail on `2317505` and pass after: a renamed poem can reuse its fixed port, a health timeout preserves its receipt, and uncertain teardown is reported before any replacement process starts.
- [Stale-token regression](regressions.json) fails on `557b775` and passes after. Two real poem servers reuse a port in sequence; the first poem can stop/reopen while the second remains available.
- The [preceding regression record](../2026-10-20-merge-readiness/regressions.json) retains the original copied-create and leaked-server failures. The final suite also exercises concurrent reopening, unchanged poem versions, history retention and copied-file rejection without writes.

## Fresh agent results

| Suite | Result | Evidence |
|---|---|---|
| Unchanged poetry corpus | 8/8 pass | [Responses and commands](combined.responses.json), [grades](grades.json) |
| Pronoun readings | 4/4 pass | [Responses and commands](pronouns-after.json), [grades](pronouns-grades.json) |
| Shared-file CLI | 6/6 pass | [Documents, history and commands](cli-after.json), [grades](cli-grades.json) |
| Automatic drafting routes | 9/9 pass | [Artifacts and commands](auto-open-after.json), [grades](auto-open-grades.json) |
| Explicit editor launch | 4/4 pass | [Artifacts and commands](launch-after.json), [grades](launch-grades.json) |

All 31 executions use fresh Codex CLI 0.155.1 sessions, read-only package copies and unchanged requests/criteria, without expected answers or prior responses. The default model is used; its backend identifier is not emitted. Grading is the lead agent's semantic judgment with condition known. Historical baseline executions and earlier failed responses remain unchanged. This diagnostic sample is not a general accuracy or literary-quality claim. Command-level failures remain recorded rather than being hidden by the case result.

## Software and distribution

[Software receipts](software-checks.json) record 61 skill tests and four root tests, all 24 scanner fixtures, Python/JavaScript parity, state/host/file transport checks, seven production page/transport scenarios, skill validation, manifest parsing and version consistency. The 16 evaluation/evidence tests and default evidence checker pass after recording this trial: 81 Python tests total. A separate Word ZIP/XML inspection verifies the actual newly generated artifact's requested title and vocalized poem text.

[Native lifecycle receipts](lifecycle.json) verify fresh isolated Claude/Codex Git installation, update, repeated update, discovery and exact installed payloads. Fixture version 0.2.1 is local test data. These checks change no user plugin settings and publish nothing.

The [earlier real-browser receipts](../2026-10-20-editor-fixes/browser-checks.json) remain separate. Browser sources and generated HTML are byte-identical to that tested candidate; no new visual run is claimed for these Python lifecycle fixes. New server regressions use real loopback servers. The launch fixture records display requests without rendering HTML.

Claude inspected the staged lifecycle fixes read-only. Its final focused review found no remaining merge blocker. It did not execute tests; the execution evidence above was collected separately. Private review output and generated artifacts remain outside Git.

Safe writes require cooperating macOS/Linux clients and a browser reaching the same local server. HTML snapshots do not synchronize edits. This does not establish ChatGPT browser-account sync, automatic update timers, public directory acceptance or automatic agent wake-up.

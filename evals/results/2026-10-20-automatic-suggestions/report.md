# Automatic Diwan suggestions

The candidate is implementation commit `9e9e90e`, version 0.3.0. Its package hashes match all fresh trial copies. The previous historical baselines and failed executions remain unchanged; the three original consolidation baseline conditions are reused by reference, not rerun.

## Automatic word requests

The production host-adapter regression [fails against main and passes after the fix](regressions.json): preloading a poem previously hid the native host's model connection. The corrected adapter preserves host sampling independently of local shared-file storage. Host compatibility is exercised through production adapter fixtures, not a live hosted Claude preview.

[Live browser receipts](live-browser.json) follow the [two-client scenarios](../../diwan-automatic-suggestions.json) using a synthetic poem. Both installed clients answered a real word-menu request without a handoff modal, chat message or pasted response. The final Claude request took 31.11 seconds; Codex took 18.99 seconds. This single sample is not a latency benchmark. Each poem remained exactly unchanged at revision 1 until selection; selecting «سِفْرِي» created revision 2 and changed only the intended word. A conditional agent edit created revision 3 while retaining that replacement. Both edits appeared in the browser without a manual refresh and survived reload. Screenshots and original prompts/responses remain in the disposable local workspace; their paths and hashes are recorded. No private user poem or credential is included.

An earlier Claude attempt with default effort timed out after 120 seconds. It displayed an inline failure and retry choice. The final bounded interactive configuration uses low reasoning effort and completed with both clients. No automatic retry or provider switching occurred.

The added software regressions cover both client subprocess protocols, no-tool invocation flags, explicit manual mode, native host precedence, duplicate in-flight requests, timeout/cancellation cleanup, SIGTERM cleanup, malformed and fenced JSON, unexpected worker failures, retry after failure, preserving a running session on implicit reopen, and keeping its port on an explicit provider change. Software fixtures make no live model calls.

## Poetry and shared-file behavior

All 31 current agent executions use fresh default-model Codex sessions and read-only package copies, with the existing requests and criteria unchanged:

| Suite | Fresh cases | Result |
|---|---:|---|
| [Poetry consolidation](combined.responses.json), [grades](grades.json) | 8 | 8 pass |
| [Automatic drafting routes](auto-open-after.json), [grades](auto-open-grades.json) | 9 | 9 pass |
| [Explicit editor requests](launch-after.json), [grades](launch-grades.json) | 4 | 4 pass |
| [Pronoun readings](pronouns-after.json), [grades](pronouns-grades.json) | 4 | 4 pass |
| [Shared-file CLI](cli-after.json), [grades](cli-grades.json) | 6 | 6 pass |

The lead reviewed responses, raw command events, embedded poem data, source/package integrity and final documents/history against the frozen criteria with condition known. This is a diagnostic sample, not a statistical accuracy or literary-quality claim. Opener fixtures record display requests and do not render HTML; the real browser checks above are separate. Repeated bundled documentation output is hashed rather than duplicated in the public command receipts. Full raw events remain at the recorded local paths.

Firas F. Khabour's scanner, meter tables, engine, exporter and font assets are unchanged. The original word-replacement prompt and replacement logic are retained; the change restores automatic request delivery and repairs failure handling.

## Installation and review

[Native client lifecycle checks](lifecycle.json) verify isolated Git-backed installation, update, repeat update, discovery and exact installed skill bytes in Claude and Codex. Fixture 0.3.1 is local test data, not a published release. User plugin settings were not changed by these checks. The working browser preview uses the PR candidate; the user's account plugin updates after a reviewed merge.

Claude reviewed the integration read-only. Valid issues were corrected with regressions for malformed output, process cleanup, session reuse and retry. Its private review remains outside Git. [Software check receipts](software-checks.json) record 90 passing Python tests, all 24 scanner fixtures, Python/JavaScript parity, workbench transport/state checks, skill validation, manifest/version consistency and evidence integrity. No tag, public-directory submission or publication was performed.

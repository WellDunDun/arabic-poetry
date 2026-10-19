# Pronoun-reading follow-up

The original review-only response now explicitly identifies its assumed masculine addressee in «وجهكَ», offers «وجهكِ» as the feminine alternative, and waits for approval without scanning. The instruction correction requires naming a meaningful pronoun reading, while preserving any reading already fixed by supplied marks or context. The scanner review reference also names pronoun choices among consequential vocalization decisions.

Evaluated implementation: `9ad0f76` on `codex/diwan-cli`, following the prior candidate at `0927618`. [The exact skill inventory](combined.package-hashes.json) identifies the evaluated bytes. Only `SKILL.md` and `references/SCANNER.md` change in the shipped skill; scripts, browser assets and software tests are unchanged. The unreleased plugin capability version remains 0.2.0. Evidence-only commits do not change the evaluated payload.

## Fresh candidate results

| Suite | Result | Evidence |
|---|---|---|
| Unchanged poetry corpus | 8/8 pass | [Responses and commands](combined.responses.json), [grades](grades.json) |
| New pronoun-reading cases | 4/4 pass | [Responses and commands](pronouns-after.json), [grades](pronouns-grades.json) |
| Shared-file CLI | 6/6 pass | [Execution/state/history](cli-after.json), [grades](cli-grades.json) |
| Automatic drafting routes | 9/9 pass | [Execution and artifacts](auto-open-after.json), [grades](auto-open-grades.json) |
| Explicit editor launch | 4/4 pass | [Execution and artifacts](launch-after.json), [grades](launch-grades.json) |

The [preceding shared-file trial](../2026-10-19-shared-cli/report.md) remains unchanged at 7/8 for the poetry corpus, retaining the failed response and criterion. The original requests and rubric were not changed. The four new pronoun requests and criteria were committed before execution; they are additional coverage, not a replacement for the original regression.

Both ambiguous-address cases explicitly identify masculine address and the feminine alternative. The supplied-feminine case preserves the poet's kasra, and the mother-context case chooses feminine address. Both fixed-reading cases return only the requested vocalized line, with no unnecessary question. Their recorded commands only read the entrypoint; none scans, opens an editor or rewrites a source file. Base letters and spacing were also checked against the frozen inputs.

All 31 candidate requests use fresh Codex CLI 0.155.1 sessions with read-only package copies. They receive no rubric, expected response or previous answers. The normal configured model is used; its exact backend identifier is not emitted. The lead agent grades the actual responses, command evidence and artifacts with condition known. These are single diagnostic samples, not a general accuracy or literary-quality claim. CLI discovery and restore each first try an unavailable `python` command, then recover with `python3`; those failed lookups remain in the command records. The stale-save case directly receives the expected conflict exit 5 and preserves the newer version.

The three historical original poetry baseline conditions are reused by reference, not rerun. Earlier automatic-routing and explicit-launch baselines likewise remain historical. The new pronoun suite has fresh candidate executions; no separate baseline run is claimed for those four new cases.

## Software and distribution verification

[Software receipts](software-checks.json) record passing skill validation, manifest parsing/version consistency, 51 skill tests (including 18 CLI cases), four root tests, 24 scanner gold fixtures, Python/JavaScript parity, editor state/host/file-adapter tests, evaluation regressions and evidence integrity. A separate ZIP/XML check verifies the newly generated Word file contains the exact requested title and canonical poem text.

[Native lifecycle receipts](lifecycle.json) record a fresh isolated Claude/Codex Git install, update, repeated update, discovery and payload verification. These tests do not modify the user's plugin settings or establish browser-account synchronization.

[Browser evidence](browser-checks.json) is explicitly reused from the preceding shared-file implementation; its source commit and provenance are retained. Browser code did not change, so no new live browser run is claimed here. The launch fixture only records display requests and cannot render HTML. Generated HTML, Word files and screenshots stay outside Git; temporary paths identify execution provenance rather than permanent downloads. Private review/audit documents remain outside Git.

Firas F. Khabour's attribution and core scanner/editor/exporter remain unchanged. The CLI's existing macOS/Linux advisory-lock and local-loopback requirements continue to apply. This follow-up adds no cloud bridge, model-service connection or ChatGPT extension integration.

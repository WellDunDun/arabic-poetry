# Client/session review fixes

Unreleased 0.3.0 parent candidate. Source `58e59a9b5a3069cd238d9b004de00dba6dd51db3`.

A healthy implicit session is reused before resolving a client from the new shell. Session receipts preserve the requested auto/manual/explicit client mode independently of the resolved client, including older receipts and rename/reopen. Switching between auto and an explicit client is retained even when both resolve to the same executable. The documented serve example uses manual mode; its execution test removes optional clients from PATH.

## Verification

- The new regressions fail against the original behavior: AGENT_NOT_FOUND before healthy reuse, lost auto/requested modes, and the optional-client-dependent example. See [regressions.json](regressions.json).
- All 73 skill tests pass on this exact parent package.
- Real isolated Claude and Codex Git installation, update, repeated update, discovery/inventory and exact installed skill-byte checks pass. See [lifecycle.json](lifecycle.json). No production installation was changed.
- All 31 fresh agent cases pass lead semantic review: 8 poetry, 9 routing, 4 explicit opening, 4 pronoun and 6 CLI workflows. No requests or criteria changed. Actual responses and command output are recorded in [combined.responses.json](combined.responses.json) and [agent-workflows.json](agent-workflows.json), with case-specific [poetry grades](grades.json) and [workflow grades](agent-workflow-grades.json).
- Word ZIP/XML and local HTML/canonical poem data were inspected. Exact title, text and marks are retained. Display receipts are fixture acknowledgements, not real rendering.
- Two CLI cases initially tried unavailable `python`, then recovered through `python3`. Their failed commands remain in the evidence. The stale save actually exits 5 without a fresh-precondition retry; idempotent retry advances once; restore creates revision 3 and keeps all three history entries.

The English review-only request says to explain the reading then stop. Its response stops after the masculine/feminine alternatives, without a scan/editor; an additional confirmation question is not required by that request. This is recorded in the specific criterion evidence.

The three historical poetry baseline conditions are reused unchanged. This is a diagnostic sample with lead grading and condition known, not a literary-quality or general accuracy benchmark. Automatic-client/model behavior and shared-file browser rendering have separate earlier evidence; this trial does not establish account sync or directory publication. Internal review notes remain outside Git.

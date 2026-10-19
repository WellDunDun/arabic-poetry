# Automatic Diwan drafting trial

Date: 2026-10-19, Asia/Amman. Final evaluated skill bytes match source commit `a570853`. The automatic-opening baseline is PR #9 at `8fbdef835a02773d7153ba4c523b2e1de7e6663a`.

## Behavior and method

Creating, continuing or revising a poem now routes to Diwan in the same turn, with the complete generated or revised draft preloaded. The agent uses an available local viewer without an extra editor offer, permission question, publication or paste step. It reuses an existing Diwan tab. Quick analysis, interpretation, critique without rewriting, requested review-first pauses and explicit chat-only delivery stay in chat. Missing local display capability yields a prepared file and an honest handoff.

Proposed revisions use separate draft files. A poem's input path identifies the source and does not itself ask the agent to overwrite it. Acceptance or an explicit save-back instruction permits updating the working copy. The editor's review status and preserved browser drafts remain unchanged.

The new `diwan-auto-open-v1` requests and criteria were frozen before the before/after executions. Its nine cases cover English/Arabic creation and revision, quick imagery and meter analysis, creation/revision chat-only overrides, and revision without a viewer. Each case ran in a fresh Codex CLI session with a read-only skill copy. The same enhanced runner supplied inherited, overridden or absent poem context to both conditions and recorded actual embedded draft text. Execution sessions received no rubric, expected answers or review findings.

Both conditions used `codex-cli 0.155.1` with default model settings and no override. JSONL events did not identify an exact backend model. Capabilities were local files, Python and Node, with a fixture opener only where declared. No network, publishing, installs, hosted storage or model-service connections were available to the execution sessions.

## Results

| Frozen suite | Prior PR #9 | Final candidate |
| --- | --- | --- |
| Automatic drafting, nine cases | 4/9 pass | 9/9 pass |
| Original poetry corpus, eight cases | Historical 8/8 | Fresh 8/8 pass |
| Original explicit-launch suite, four cases | Historical 4/4 | Fresh 4/4 pass |

Only the new nine-case suite has fresh executions of both conditions here. Historical counts refer to the unchanged [scansion explanation trial](../2026-10-19-scansion-explanation/report.md). The original consolidation baseline conditions remain referenced from their earlier records rather than rerun.

The old package composes and revises in chat without preparing or opening Diwan. Its quick-analysis and explicit chat-only cases pass the new criteria. Its ordinary revisions also overwrite the supplied input. The final package preloads the actual generated poems with their requested titles and four lines, and preloads each exact requested revision with all other marks and line breaks preserved. The original inputs remain unchanged. All four default-opening cases invoke the available opener during the same session. The two quick-analysis and two chat-only cases create no editor; chat-only cases also create no poem files. The unavailable-viewer revision prepares the exact draft, retains the original and links the file without claiming it opened.

Selected earlier revision diagnostics are retained in `revision-diagnostics.json`. They opened the correct draft but did not consistently preserve the source file. These failures prompted the source-path/save-back clarification. They are not relabeled as final passes or represented as another complete comparison. Other raw diagnostic logs remain outside Git.

`auto-open-before.json`, `auto-open-after.json` and `auto-open-grades.json` contain complete final responses, commands, package hashes, embedded drafts, display receipts and criterion judgments. `combined.responses.json`, `grades.json`, `artifacts.json` and `combined.execution-notes.json` retain the fresh original-corpus evidence. `launch-after.json` and `launch-grades.json` record the four original launch cases.

## Software and distribution

All required software checks pass: 33 scanner/launch/bridge tests, four root helper tests, 16 evaluation tests, 24 classical fixtures, Python/browser parity, editor state/host regressions, skill and manifest/version validation. The new offline runner regression checks per-case context isolation, generated-draft capture and actual fixture receipts without calling a model. The final skill entrypoint has 67 lines, and changed local Markdown links resolve. The newly exported Word file was independently checked as a valid DOCX with the exact Arabic title and marked poem. See `software-checks.json`.

Native Claude/Codex Git install, update, repeated-update, skill-discovery and installed-payload checks passed again against the final committed instructions using isolated client state and a local Git mirror. See `lifecycle.json`. Version `0.1.2` remains unreleased. Nothing was merged, tagged or published.

Firas F. Khabour's scanner, meter tables, export engine, font assets and attribution remain preserved. This follow-up changes instructions, public documentation and evaluations; it changes no editor/runtime implementation. Earlier [real-browser checks](../2026-10-19-diwan-launch/browser-checks.json) remain historical evidence for that unchanged implementation and were not rerun for these instruction changes.

## Limits

The opener records delivery requests without rendering HTML, so these agent runs do not prove that a user saw the editor. Grades are lead semantic judgments with the condition known. Single runs and diagnostic iteration do not establish a general success rate or literary accuracy. The nine-case suite samples creation and revision, not every continuation or extended editing session.

Final-response file-link rendering is also not certified by the frozen criteria: the bounded-repair response contains a stray mark before its fallback link, and the export response uses relative links. The actual files and absolute artifact paths are recorded and valid. These output-format limitations are separate from the passing routing/scansion criteria.

No Claude sandboxed-preview integration, ChatGPT extension, automatic AI-button connection, account sync, directory acceptance or background update timer was verified. Generated HTML/documents, screenshots, private audits and model review logs stay outside Git. PR #9 remains unmerged for review.

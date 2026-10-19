# Shared-file Diwan CLI trial

The candidate adds one canonical `.diwan.json` document shared by the local editor and the agent. Both save through version preconditions, a directory-wide advisory lock, atomic replacement and stable request identities. History retains complete snapshots; restoring creates a new revision. Conflicts preserve the newer file and the browser draft. Import files and HTML-only snapshots are explicitly separate from the live document.

Implementation evaluated: `f37a979` on `codex/diwan-cli`, based on PR #9 at `fd203d4ab119ce33f0539398ff0bbbfe2dadcf3f`. The exact evaluated skill bytes are in [the package inventory](combined.package-hashes.json). Later evidence-only commits do not change that payload.

## Results and remaining behavior gap

| Evidence | Result | Scope |
|---|---|---|
| [New CLI requests](cli-after.json), [grades](cli-grades.json) | 6/6 pass | Fresh agent sessions: discovery, import, accepted edit, stale conflict, identical retry, restore |
| [Automatic routing](auto-open-after.json), [grades](auto-open-grades.json) | 9/9 pass | Creation/revision launch, quick chat, chat-only overrides, unavailable viewer |
| [Explicit launch](launch-after.json), [grades](launch-grades.json) | 4/4 pass | English/Arabic opening, unavailable viewer, chat-only |
| [Unchanged poetry requests](combined.responses.json), [grades](grades.json) | 7/8 pass | Review-only response does not explicitly disclose masculine address in وجهكَ |
| [Software checks](software-checks.json) | Pass | 51 skill tests including 18 CLI tests, 4 root tests, 24 gold fixtures, runtime parity and editor state/host/file tests |
| [Browser checks](browser-checks.json) | Pass | Real in-app browser: exact load, title/empty-text validation, browser-to-file save, stale conflict, explicit reload, CLI restore and clean refresh |
| [Plugin lifecycle](lifecycle.json) | Pass | Isolated native Claude/Codex Git install, update, repeated update, discovery and payload checks |

The failed poetry response preserves the text and stops for approval, but silently chooses masculine address. The skill already requires disclosure of consequential reading choices; this execution did not fully follow that instruction. The failure is retained rather than changing the rubric or replacing the response with another sample. It needs review before a merge decision. Passing software does not establish reliable literary behavior.

All 27 candidate cases use fresh Codex CLI 0.155.1 sessions and read-only package copies. Execution sessions receive the request and capability limits, not the rubric or previous answers. The normal configured model is used; the exact backend identifier is not emitted by this runner. Grading is the lead agent's semantic judgment with condition known. This is a small diagnostic trial, not an accuracy estimate. A failed `python` lookup in the restore case is retained; the agent recovers using `python3`. The stale-save wrapper's outer process succeeds while explicitly recording the real inner CLI conflict exit 5.

The three original poetry baseline conditions reuse the pinned executions from the preservation trial. Automatic-routing and explicit-launch baseline results are referenced from their earlier trials. Those baselines were not rerun for this CLI change. The launch fixture records display requests and cannot render HTML; actual shared-file behavior is verified separately in the real browser. Browser screenshots and generated poem/Word files remain outside Git. Temporary paths in execution records identify actual evidence; they are not permanent artifact downloads. The Word artifact also passed an independent ZIP/XML check for the exact canonical title and text. Browser Word export displayed a preparation-success toast; its downloaded contents were not separately inspected.

## Applying the CLI design skill

Used [design-agent-native-cli](https://github.com/WellDunDun/skills/tree/main/skills/design-agent-native-cli), reading its complete entrypoint and both references. These are the concrete contracts and observed evidence:

| Principle | Implementation / evidence |
|---|---|
| Automation first | Noninteractive flags, file/stdin inputs, no setup prompts; discovery and CLI cases execute without interaction |
| Structured output | JSON stdout, structured stderr errors, stable exit codes; get/update/history fixtures and HTTP tests |
| Actionable errors | Missing-file, invalid UTF-8, stale-version, duplicate-id and delivery errors include recovery guidance; browser validation offers draft recovery |
| Safe mutations | Mandatory save version/request id, dry-run, no delete; real two-process races, interrupted writes and replay tests |
| Bounded output | History pagination and bounded pending results; pagination tests |
| Consistent grammar | One command vocabulary; the metadata is derived from the same argparse definitions |
| Progressive discovery | Offline root/subcommand help, machine summary/detail, workflow reference; every documented command example executes in disposable fixtures |
| Lifecycle | Owned local server start/reuse/stop; local session tests. Remote async jobs are not applicable |
| Configuration | Explicit document paths and no credentials; profiles are not applicable to this local workflow |
| Artifact delivery | Atomic text/Markdown/Word exports with path/hash/bytes/source version. No upstream feedback endpoint is configured |

## Safety and platform coverage

The software tests exercise concurrent writers, stale browser edits, lost acknowledgements, writes interrupted before/after replacement, and request-id collisions. Review fixes cover macOS case/Unicode filename aliases sharing a lock/history, export protection for the entire private `.diwan` directory, duplicate-id queue isolation, recoverable creation staging links, field-validation errors and a verified integrity hash on the existing JSZip CDN asset. Private review/audit text is kept outside the repository.

Safe writes currently require macOS/Linux (`fcntl`); execution here was on macOS. Arbitrary tools directly overwriting JSON ignore the advisory lock and are unsupported. There is no automatic merge. Keep the document and hidden `.diwan` history together when moving a workspace. A recognized interrupted exclusive creation is recoverable by retrying `create` with the same input; dry-run leaves staging files untouched and unrelated hard links are rejected. Export cannot replace the current poem, lock or another poem's private history.

Shared-file editing needs the browser and agent to reach the same local loopback server. A sandboxed HTML preview can instead use the disclosed snapshot fallback; its edits do not synchronize to the document. No cloud bridge, automatic agent wake-up, ChatGPT extension integration, Windows safe-write support or browser-account sync is established by this trial.

Firas F. Khabour's attribution remains. The scanner, scanner data, core workbench engine, meter data, export engine and fonts are byte-identical to main at `50938ba`; only their integration with the new document workflow changes. The browser save path does not send a model request.

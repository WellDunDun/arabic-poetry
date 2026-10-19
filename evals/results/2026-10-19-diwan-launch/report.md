# First-request Diwan trial

Date: 2026-10-19, Asia/Amman. The candidate package bytes match source commit `00fc740`. The launch baseline is main at `50938ba72240d810079d9d360397df256f83e4c9`.

## Launch behavior

The frozen `diwan-first-request-v1` suite ran four requests against each package, with a fresh Codex CLI session per case and the same default client settings. No model override was supplied; the client did not emit an exact backend model identifier. The requests cover English and Arabic opening, a missing local viewer, and explicit chat-only scope. Inputs are synthetic. The worker receives the installed skill and capability limits, not the rubric or expected answers.

| Condition | Passing cases | Interpretation |
| --- | --- | --- |
| Main before the fix | 4/4 | With an explicit fixture opener, the agent constructed a custom preloaded HTML copy. |
| Candidate | 4/4 | The agent used the shipped helper, preserved the exact supplied text, and requested local display in the first turn. |

Both conditions succeeded in this small controlled sample. It does not establish a success-rate improvement. The candidate makes preloading a supported operation and adds tested identity, revision and storage handling instead of relying on custom page edits.

See `launch-before.json`, `launch-after.json` and `launch-grades.json`. The records include complete final responses, executed commands, package and input integrity checks, HTML hashes and matching opener receipts. The fixture opener records delivery requests without rendering HTML. It cannot prove that a user saw an editor. Timeout handling records `timed_out` and terminates the client process group; no final trial case timed out.

## Real browser and software checks

The separate Brave browser run on the same Mac rendered the preloaded HTML over loopback HTTP. It checked exact text and marks on first opening, preservation of a browser edit, opening a different supplied chat revision without deleting that edit, and a storage-denied page that still displays the poem with a warning. The actual English HTML artifacts produced by both agent conditions were also opened and their textarea values read back exactly. All six recorded checks passed. See `browser-checks.json`.

The software checks include 33 scanner/launch/bridge tests, four root distribution-helper tests, 15 evidence-integrity tests, 24 classical fixtures, Python/browser parity, production editor state/host regressions and manifest/skill validation. Native Claude and Codex Git installation, update, repeated update and installed payload verification passed in isolated client state. See `software-checks.json` and `lifecycle.json`. Firas's scanner, meter tables, export engine and font assets remain unchanged.

## Existing poetry corpus

All eight candidate requests in the original frozen corpus were rerun, one fresh session per request. The three historical baseline conditions and judgments remain referenced from their earlier records, not rerun or represented as a fresh same-model comparison. The corpus requests and criteria remain unchanged. Command execution, final responses and artifact inventories are in `combined.responses.json`, `artifacts.json` and `combined.execution-notes.json`.

Seven candidate cases meet all criteria. `classical-scan` fails its compact sound-to-foot account criterion: the response names the correct meter and gives the full feet, but does not map the actual words/sounds onto them. Its real scanner run is recorded and successful. This final-answer coverage shortfall is retained in `grades.json`; a valid scanner alignment does not make the response fully compliant. The local workbench case created preloaded HTML and a valid Word file while accurately stating that no viewer was available.

## Limits

These are diagnostic samples and software checks, not a corpus accuracy estimate or Arabic literary-expert review. No Claude sandboxed HTML-preview integration, ChatGPT extension, automatic AI-button connection, account sync or public-directory installation was tested. Local storage does not synchronize concurrent tabs. The workflow reuses the existing Diwan tab; changing file/localhost origins requires carrying over the current edited text. Prepared files remain private local artifacts and were not published. Screenshots, generated documents, private session analysis and model review logs remain outside Git.

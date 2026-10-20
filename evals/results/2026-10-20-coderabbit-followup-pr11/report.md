# Automatic/manual documentation follow-up

Source `f25ae4c1248f3289a46fd4d26187a6d00c091fa6`. The exact served package is recorded in [combined.package-hashes.json](combined.package-hashes.json). This follow-up changes documentation and evaluation records; runtime code is unchanged from the [preceding functional trial](../2026-10-20-review-fixes-pr11/report.md).

The README and Diwan reference now distinguish automatic requests through an installed, signed-in Claude/Codex client from manual handoff to an existing chat. Automatic requests use the selected client's login and normal usage. They do not send a turn into the open conversation. Manual handoff does not start a separate agent run.

Historical automatic-suggestion metadata now names the correct preceding session-lifecycle trial. Its four pronoun grades cite their actual responses and command traces instead of nonexistent editor artifacts. The English request says to explain the consequential reading then stop. Its recorded answer does that, without scanning or opening an editor; no explicit confirmation question was requested. That interpretation is stated in its criterion evidence. Raw historical responses and frozen criteria were preserved.

## Verification

- 8 fresh frozen poetry cases: 8 pass and 0 fail under lead semantic review, condition known. Actual [responses and commands](combined.responses.json), [criterion-specific grades](grades.json), [artifact digests](artifacts.json) and [execution provenance](combined.execution-notes.json) are retained.
- 73 skill, 4 root and 16 evidence/launch tests, 93 Python tests total pass on this package. [Software receipts](software-checks.json) retain commands and output.
- All 24 scanner fixtures, Python/JavaScript parity, shared-file/host/state workbench checks, skill validation, Claude plugin validation and manifest/version checks pass.
- The export case creates a canonical poem document, preloaded HTML and a DOCX. The Word ZIP/XML and embedded title/text were inspected against the exact supplied poem. The response reports the missing local viewer and distinguishes local files from unavailable host/cross-chat storage.

The bounded-repair response meets the frozen criteria and has real before/after scanner execution. Its optional original/proposal text files contain the respective poem text followed by a normal newline; their exact bytes are retained in the artifact inventory.

## Limits

One fresh sample per case is diagnostic evidence, not a statistical or literary-quality benchmark. The three baseline conditions are reused unchanged from the frozen historical trial. The preceding 31-case workflow executions, live suggestions, browser checks, Claude reviews and installation lifecycle remain tied to their own recorded sources. They were not rerun for this documentation correction. No account sync, background update timer or public directory acceptance was tested. Internal review notes remain outside Git.

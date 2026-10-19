# Scansion explanation follow-up

Date: 2026-10-19, Asia/Amman. The evaluated skill bytes match source commit `9ae1c39`. The previous [Diwan launch trial](../2026-10-19-diwan-launch/report.md) remains unchanged, including its failed scansion explanation criterion.

## Correction and frozen requests

The earlier response named al-Tawil and listed its feet, but did not connect the actual sounds to those feet. The skill now asks for a complete hemistich's pronounced groups, observed syllable patterns and fitted feet in a compact metrical explanation. For a shorter fragment it covers the whole fragment. The scanner reference explains how to derive this from the inspected reading and alignment, with word boundaries allowed inside feet. The scanner implementation and metrical rules were not changed.

All eight original poetry requests and all four Diwan launch requests were rerun through `evals/run_diwan_launch.py`. Each request received a fresh Codex CLI session, a read-only package copy and the same capability limits as the earlier trial. The client was `codex-cli 0.155.1`, using its default model settings without an override. The JSONL events did not identify an exact backend model. Execution sessions received no rubric, prior answers or review findings. Both suites and their criteria remain frozen.

## Results

| Suite | Earlier candidate | This candidate |
| --- | --- | --- |
| Eight-case poetry corpus | 7/8 cases pass | 8/8 cases pass |
| Four-case Diwan launch suite | 4/4 cases pass | 4/4 cases pass |

Earlier counts refer to the previous trial, not new baseline runs. The three original consolidation baseline conditions are referenced from their historical records. The launch baseline remains at main commit `50938ba72240d810079d9d360397df256f83e4c9`; its execution and grades are referenced by `launch-grades.json`.

The fresh `classical-scan` response maps the first hemistich in four complete rows, with each pronounced group, syllables and foot. Its groups match the actual captured scanner output. It distinguishes lam as rawi from the lengthened final vowel, answers in English and respects chat-only scope. All four frozen criteria pass. The other seven cases preserve direct prose composition, grounded interpretation, preliminary uncertainty, review-first scope, minimal repair, pronounced tanwin and truthful local export behavior.

The launch cases prepare the exact current poem and use the available fixture opener in the first turn for both English and Arabic. The unavailable-viewer case prepares the file and states the limitation. The chat-only case creates no editor. Package/input/opener integrity and receipt-to-file hashes pass in every case. The fixture records display requests without rendering HTML; it does not prove a user saw the editor.

See `combined.responses.json` for complete final responses and executed commands, `grades.json` for semantic judgments, and `combined.execution-notes.json` for execution status and raw-event digests. `launch-after.json` and `launch-grades.json` retain the new launch responses, commands, integrity checks and criterion-level judgments. Artifact inventories identify bytes created outside Git. Command streams are aggregated by the client, so stderr is not independently separated.

## Software and distribution

All required checks pass: 33 scanner/launch/bridge tests, four root helper tests, 15 evidence-integrity tests, 24 classical fixtures, Python/browser parity, editor state/host regressions, skill validation and manifest/version checks. The generated Word file was separately checked as a valid DOCX containing the requested Arabic title and exact marked poem. Local Markdown links and the 66-line skill entrypoint were checked. See `software-checks.json`.

Native Claude and Codex Git install, update, repeated-update, skill-discovery and installed-payload checks passed again using temporary client state and a local mirror. See `lifecycle.json`. No release tag or publication was made.

Firas F. Khabour's scanner, meter tables, export engine and font assets remain byte-for-byte unchanged from main. This follow-up changes two instruction files and the unreleased changelog entry. The earlier six [real-browser checks](../2026-10-19-diwan-launch/browser-checks.json) are historical evidence for the unchanged editor implementation; they were not rerun for this instruction-only correction.

## Limits

Grades are lead semantic judgments with the condition known. A single fresh session per case is a diagnostic sample, not an accuracy estimate, statistical improvement claim or Arabic literary-expert review. These tests do not establish Claude sandboxed-preview integration, ChatGPT extension behavior, automatic AI-button connections, account sync, directory acceptance or background update timers. Prepared files remain local. Generated HTML/documents, screenshots, private audits and review logs stay outside Git. PR #9 remains unmerged for review.

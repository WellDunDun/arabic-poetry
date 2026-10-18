# Manual CodeRabbit review of draft PR #3

The user authorized a manual draft review. [The request](https://github.com/WellDunDun/arabic-poetry/pull/3#issuecomment-6254250729) was accepted, and CodeRabbit completed its review of `03d806744745946c521bbebf11fce76bf722cb2e` on 2026-10-18. PR #2 had no newer CodeRabbit findings; its two previous findings were fixed. Two older Codex evidence-validator threads were also resolved after all 15 acceptance/mutation regressions passed.

## Valid findings and fixes

- [Database wording](https://github.com/WellDunDun/arabic-poetry/pull/3#discussion_r4308457204): README now says a host database must be connected. An available service alone does not receive poem data.
- [Orphaned pending requests](https://github.com/WellDunDun/arabic-poetry/pull/3#discussion_r4308457211): pending lists live requests oldest first and excludes work older than the ten-minute browser deadline. Direct responses to expired IDs are rejected. A newly bound server session cancels all open earlier requests, including already expired requests. A failed attempt to bind an occupied port leaves the active session’s requests intact. Completed answers remain untouched.
- Queue privacy nit: `.diwan/.gitignore` is created with `*` when absent, preserving an existing ignore file. This reduces accidental addition of untracked queue data; it does not untrack existing files or block force-add.
- Docstring coverage warning: all functions in the bridge and its Python regression module now have concise docstrings. This is local AST evidence, not a claim about a subsequent CodeRabbit check.

The lead also reproduced a duplicate-answer race: two simultaneous responders both passed the precheck and one replaced the other’s answer. Response publication now atomically links a completed temporary file into place without overwriting an existing answer. Exactly one responder succeeds, and temporary files are cleaned up. Other queue JSON publication remains atomic.

## Evaluation wording notes

CodeRabbit suggested rewriting two saved agent responses. The repository requires preserving raw responses. Clarifications were therefore added to their reports, without modifying response bytes, commands or recorded verdicts:

- The earlier السريع match depends on the explicitly assumed paused ending. The regular connected reading instead ranks الرجز first with one alignment error. The later provisional الرجز response uses that different reading.
- In the follow-up workbench response, “saved” means the listed local JSON/TXT/DOCX files. The editor is a separate unchanged HTML copy; the response explicitly says the poem was not loaded into editor storage.

## Evidence and limits

Four regression targets fail on the previous bridge: concurrent duplicate replies, pending order/expiry, startup cancellation and missing ignore file. All ten bridge tests pass after the changes, including failed-restart preservation and existing-ignore preservation. Scanner, workbench, adapter, package and evidence checks are recorded separately. A fresh independent eight-request trial of the final package is recorded in `evals/results/2026-10-18-draft-review/`, using the unchanged frozen requests/criteria and explicitly reusing the earlier baseline trials. The old raw execution records remain unchanged.

No live provider, browser session, shared host database, PDF or visual Word-layout test is claimed here. CodeRabbit’s completed review covers the pre-fix head above; subsequent commits are not called approved. Both PRs remain open and unmerged, and PR #3 remains a draft with automatic merging disabled.

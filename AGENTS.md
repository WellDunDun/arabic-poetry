# AGENTS.md

## Purpose and public documentation

This is a collaborative Arabic poetry Agent Skill. Keep README.md user-facing: purpose, installation, capabilities, sources, credits, and license. Keep maintenance and validation instructions here. Preserve attribution to the original idea and to contributors; do not invent a collaborator's name or claim sole origin.

## Layout

Keep the served skill at `skills/arabic-poetry/`, with `SKILL.md`, one-level `references/`, and deterministic helpers in `scripts/`. Its frontmatter name must match its directory. Keep the entrypoint under 100 lines when practical. Use relative reference links and do not require maintainer research notes to install the skill.

There is one served skill. Its `scripts/` include the scanner (`scan.py`, pure Python). `assets/workbench/` holds the Diwan page sources (`page.html`, `engine.js`, `export.js`, `host.js`, `meters.json`) and built `diwan.html`; `assets/fonts/` holds Amiri and its license. `scripts/arud/meters.py` is the meter-table source: after changing tables or browser code, run `python3 skills/arabic-poetry/scripts/build_workbench.py` and keep parity passing. Put scanner and workbench procedures in their references rather than expanding the shared entrypoint.

Keep maintained sources, rule mappings and coverage limits in the served skill's `references/`. Keep internal audits, PR review dispositions, planning notes and dated research work logs outside the Git checkout. Commit reusable tests, evaluation methodology and necessary execution evidence under `evals/`, distinguishing source findings from agent behavior and software checks. Do not add unrelated artifacts, screenshots, or app prototypes to the root. Preserve unrelated changes.

## Editing the skill

Support classical and modern forms equally. Ground technical assertions in pronunciation, actual sound sequences, and appropriate Arabic sources. Preserve the user's meaning, dialect, authorship, and editing scope. Keep ambiguity and source limitations visible. Do not import an analyzer's marketing claims or faulty patterns as authority.

The scanner compares supported vocalized readings with implemented metrical forms. Its spelling-based rhyme-repeat filter is an editing heuristic; neither a matching scan nor a repeated spelling certifies full metrical legality, a semantic rhyme fault, originality or literary quality. Keep these limits explicit in documentation and outputs.

The portable root `plugin.json` discovers skills under `skills/`. `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` serve the same root package to OpenAI and Claude clients under `arabic-poetry-plugins`. The relative entry paths are resolved inside the Git-cloned marketplace; default installation must register the repository URL, not a developer's local checkout. Keep the Claude-compatible `.claude-plugin/plugin.json`, both catalogs and README.md consistent. There is one skill package, not a separate copy per host. The published installation slug is `WellDunDun/arabic-poetry`. Public directory publication and browser-account sync require separate verification.

## Plugin releases

- Keep plugin and marketplace names stable. `plugin.json` holds the canonical release version; `.claude-plugin/plugin.json` and its marketplace entry must match it. Run `python3 scripts/plugin_version.py` to check all three. Advance them together with `python3 scripts/plugin_version.py MAJOR.MINOR.PATCH`. The helper validates first, refuses a decrease, and is repeatable for the same version.
- Merging to `main` distributes the version, even without a release tag. After the initial 0.1.0 package reaches `main`, bump the version for every change to shipped instructions, references, scripts, assets or plugin behavior. Use patch for compatible corrections, minor for compatible capabilities and major for breaking changes. Update CHANGELOG.md with concrete user-visible changes. Fixture-only version bumps in lifecycle tests are not published releases.
- Release through a reviewed PR to `main`. Run the checks below and the lifecycle test before merge. When publishing an authorized release, tag its reviewed merge commit `vMAJOR.MINOR.PATCH`; do not move a published tag. Tagging/publishing requires release authorization separate from merging package changes. The default marketplace follows `main`; tags and commits are reproducible opt-outs from subsequent releases.
- For a rollback, revert the payload in a new PR and assign a higher patch version. Do not lower the manifest version or ask users to edit their plugin cache.
- CLI installation/update tests do not prove background timers, Claude account sync, ChatGPT workspace import, browser skill invocation or public directory acceptance. Preserve these distinctions in instructions and review evidence. Never change a shared workspace just to test without identifying and authorizing the test destination.

## Validation

Run from the repository root. Bridge tests bind temporary loopback sockets, so the test environment must permit localhost networking:

```sh
skills-ref validate skills/arabic-poetry
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 scripts/plugin_version.py
claude plugin validate .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 skills/arabic-poetry/tests/run_gold.py
node skills/arabic-poetry/tests/parity.js
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/arabic-poetry/tests -p 'test_*.py'
node skills/arabic-poetry/tests/workbench_state.js
node skills/arabic-poetry/tests/workbench_host.js
node skills/arabic-poetry/tests/workbench_file.js
node skills/arabic-poetry/tests/workbench_shared.js
node skills/arabic-poetry/tests/workbench_updates.js
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals -p 'test_*.py'
python3 evals/check_results.py
git diff --check
```

For distribution changes, run `PYTHONDONTWRITEBYTECODE=1 python3 tests/plugin_lifecycle.py --output /absolute/temp/path/plugin-lifecycle.json`. It requires installed `git`, `python3`, `claude` and `codex` executables. It creates a temporary Git mirror, redirects the fixture's Git reads to that mirror, and gives child clients temporary settings/cache directories. It never calls a model or publishes tags. It verifies real installs, patch updates, repeated updates, Codex runtime skill discovery, Claude plugin inventory, scanner startup and exact installed skill bytes. Keep necessary execution receipts under `evals/`; keep internal audits outside Git.

Check local Markdown reference links, entrypoint length, and whitespace in new untracked files. A structural validator is not a behavioral poetry test. Run meaningful examples when workflow changes warrant them, and report exact evidence and remaining limits.

For instruction changes, use the frozen requests and semantic criteria in `evals/` for comparable before/after trials. Preserve raw responses and executed evidence, record package hashes and capability limits, and distinguish software regressions, agent behavior and human literary review. Do not tune criteria after seeing outputs or describe a small single-run trial as a general accuracy benchmark. Historical evaluation records may retain earlier skill paths; keep active documentation links working.

Final responses for edits should report changed files, checks performed, and any unverified behavior. Do not commit unrelated work or present generated lines as a historical poet's words.

## Shared-file CLI

`skills/arabic-poetry/scripts/diwan.py` is the bundled CLI; `diwan_store.py` owns document validation, lock/CAS saves, history and operation receipts. `assets/workbench/file.js` adapts the existing editor to the local file API. Keep it embedded through `build_workbench.py`, and retain the scanner/exporter core and attribution. Shared JSON documents, history, server logs and session receipts belong in a writable poem workspace outside the installed package.

Run `test_diwan_cli.py` through the skill unittest discovery above and `workbench_file.js` for transport regressions. Exercise real browser-to-file saving, agent-to-browser refresh, stale browser conflict preservation, explicit reload and history restore in a disposable workspace. Stop owned test servers through `diwan.py stop FILE`; never kill an unverified PID. CLI help and `agent-context` must work offline before file setup. Record applicable CLI-design principles and conditional capabilities in the evaluation report. Safe writes rely on cooperating macOS/Linux writers using this API; direct file edits bypass advisory locks.

`scripts/diwan_agent.py` dispatches automatic AI requests to the selected installed Claude/Codex client. Software tests use fixture executables and make no live model calls. For a user-authorized live trial, verify both providers through real browser word-menu actions, no handoff modal, displayed suggestions, accepted replacement saved to the canonical file, and unchanged text before selection. Keep prompts in a disposable poem workspace. Preserve native host sampling independently of local poem storage; do not replace it with a manual queue. Manual mode remains explicit and must not call a model.

`scripts/diwan_updates.py` supervises shared-file workers and follows compatible, newer versions already installed in the same versioned plugin cache. Keep the loopback address, document identity, agent selection and CAS/history protocol stable across a handoff. The page must defer reload while a draft, editor, save, conflict or AI request is active. Never install packages from the editor, accept an executable path from HTTP input, force a draft save, or reload a dirty page. A failed successor returns to the last working package without retrying that target in a loop. `assets/workbench/runtime.json` declares the handoff protocol; change its number for incompatible runtime/document APIs.

The session's supervising launcher stays alive while workers update. A release that requires different running launcher behavior must advance the handoff protocol and require a safe reopen. Protocol compatibility covers document/history formats as well as HTTP and worker-launch behavior.

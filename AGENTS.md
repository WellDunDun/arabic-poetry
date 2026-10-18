# AGENTS.md

## Purpose and public documentation

This is a collaborative Arabic poetry Agent Skill. Keep README.md user-facing: purpose, installation, capabilities, sources, credits, and license. Keep maintenance and validation instructions here. Preserve attribution to the original idea and to contributors; do not invent a collaborator's name or claim sole origin.

## Layout

Keep the served skill at `skills/arabic-poetry/`, with `SKILL.md`, one-level `references/`, and deterministic helpers in `scripts/`. Its frontmatter name must match its directory. Keep the entrypoint under 100 lines when practical. Use relative reference links and do not require maintainer research notes to install the skill.

There is one served skill. Its `scripts/` include the scanner (`scan.py`, pure Python). `assets/workbench/` holds the Diwan page sources (`page.html`, `engine.js`, `export.js`, `host.js`, `meters.json`) and built `diwan.html`; `assets/fonts/` holds Amiri and its license. `scripts/arud/meters.py` is the meter-table source: after changing tables or browser code, run `python3 skills/arabic-poetry/scripts/build_workbench.py` and keep parity passing. Put scanner and workbench procedures in their references rather than expanding the shared entrypoint.

Keep research in `docs/research/`; distinguish source findings, proposed workflow, and validation evidence. Do not add unrelated artifacts, screenshots, or app prototypes to the root. Preserve unrelated changes.

## Editing the skill

Support classical and modern forms equally. Ground technical assertions in pronunciation, actual sound sequences, and appropriate Arabic sources. Preserve the user's meaning, dialect, authorship, and editing scope. Keep ambiguity and source limitations visible. Do not import an analyzer's marketing claims or faulty patterns as authority.

The scanner compares supported vocalized readings with implemented forms and displays them in ب − = notation. It does not certify intended pronunciation, complete meter legality, originality or literary quality. Preserve the distinction and the scanner/Diwan contributor credit.

Update `.claude-plugin/plugin.json` and README.md when changing the served layout. The published installation slug is `WellDunDun/arabic-poetry`.

## Validation

Run from the repository root. Bridge tests bind temporary loopback sockets, so the test environment must permit localhost networking:

```sh
skills-ref validate skills/arabic-poetry
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/arabic-poetry/scripts -p 'test_*.py'
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 skills/arabic-poetry/tests/run_gold.py
node skills/arabic-poetry/tests/parity.js
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/arabic-poetry/tests -p 'test_*.py'
node skills/arabic-poetry/tests/workbench_state.js
node skills/arabic-poetry/tests/workbench_host.js
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals -p 'test_*.py'
python3 evals/check_results.py
git diff --check
```

Check local Markdown reference links, entrypoint length, and whitespace in new untracked files. A structural validator is not a behavioral poetry test. Run meaningful examples when workflow changes warrant them, and report exact evidence and remaining limits.

For instruction changes, use the frozen requests and semantic criteria in `evals/` for comparable before/after trials. Preserve raw responses and executed evidence, record package hashes and capability limits, and distinguish software regressions, agent behavior and human literary review. Do not tune criteria after seeing outputs or describe a small single-run trial as a general accuracy benchmark. Research records may retain historical skill paths; keep their live relative links working.

Final responses for edits should report changed files, checks performed, and any unverified behavior. Do not commit unrelated work or present generated lines as a historical poet's words.

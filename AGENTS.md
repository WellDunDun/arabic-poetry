# AGENTS.md

## Purpose and public documentation

This is a collaborative Arabic poetry Agent Skill. Keep README.md user-facing: purpose, installation, capabilities, sources, credits, and license. Keep maintenance and validation instructions here. Preserve attribution to the original idea and to contributors; do not invent a collaborator's name or claim sole origin.

## Layout

Keep the served skill at `skills/arabic-poetry/`, with `SKILL.md`, one-level `references/`, and deterministic helpers in `scripts/`. Its frontmatter name must match its directory. Keep the entrypoint under 100 lines when practical. Use relative reference links and do not require maintainer research notes to install the skill.

`skills/arabic-prosody/` follows the same rules. Its `scripts/` hold the scanner (`scan.py`, pure Python); `assets/workbench/` holds the Diwan page sources (`page.html`, `engine.js`, `export.js`, `meters.json`) and the built single file `diwan.html`; `assets/fonts/` holds the Amiri font for PDF export. `scripts/arud/meters.py` is the single source of the meter tables: after changing it or the browser engine, run `python3 skills/arabic-prosody/scripts/build_workbench.py` and keep the parity test passing. Its entrypoint is longer than 100 lines because it also documents the Diwan workflow.

Keep research in `docs/research/`; distinguish source findings, proposed workflow, and validation evidence. Do not add unrelated artifacts, screenshots, or app prototypes to the root. Preserve unrelated changes.

## Editing the skill

Support classical and modern forms equally. Ground technical assertions in pronunciation, actual sound sequences, and appropriate Arabic sources. Preserve the user's meaning, dialect, authorship, and editing scope. Keep ambiguity and source limitations visible. Do not import an analyzer's marketing claims or faulty patterns as authority.

The bundled checker verifies declared transcription arithmetic and exact foot coverage. It does not infer vocalization or certify meter legality, originality, or literary quality. Keep these limits explicit in documentation and outputs.

Update `.claude-plugin/plugin.json` and README.md when changing the served layout. The published installation slug is `WellDunDun/arabic-poetry`.

## Validation

Run from the repository root:

```sh
skills-ref validate skills/arabic-poetry
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/arabic-poetry/scripts -p 'test_*.py'
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
skills-ref validate skills/arabic-prosody
PYTHONDONTWRITEBYTECODE=1 python3 skills/arabic-prosody/tests/run_gold.py
node skills/arabic-prosody/tests/parity.js
git diff --check
```

Check local Markdown reference links, entrypoint length, and whitespace in new untracked files. A structural validator is not a behavioral poetry test. Run meaningful examples when workflow changes warrant them, and report exact evidence and remaining limits.

Final responses for edits should report changed files, checks performed, and any unverified behavior. Do not commit unrelated work or present generated lines as a historical poet's words.

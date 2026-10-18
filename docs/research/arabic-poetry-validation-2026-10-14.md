# Arabic poetry: validation record

Checked 2026-10-14. This concerns the skill package, optional arithmetic helper, and a small independent agent trial. It is not a corpus benchmark, an analyzer accuracy claim, or human assessment of literary quality.

## Package checks

- Agent Skills reference validator: `Valid skill: skills/arabic-poetry`.
- Skill-creator validator: `Skill is valid!`.
- Entrypoint remains below 100 lines.
- Relative references resolve; plugin manifest and both catalogs retain the skill.
- Plugin JSON and whitespace pass, including new untracked Markdown files.

The validators check package structure, not poetry or analytical accuracy.

## Local checker behavior

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/arabic-poetry/scripts -p 'test_*.py' -v`.

Eight tests passed, with multiple cases where relevant:

- Source-backed الطويل and الهزج transcription patterns.
- Explicit tanwin readings in وصل and وقف; unexpanded input rejected.
- Missing vocalization, shadda/madda, unsuitable unexpanded spelling, punctuation, and empty transcription rejected.
- Fully aligned scan accepted.
- Dropped trailing sounds, duplication, and reversed text coverage rejected.
- Incorrect الخبن foot pattern rejected.
- Malformed CLI input returns failure JSON and exit `1`.
- File and stdin inputs return identical success JSON and exit `0`.

The helper checks a supplied, explicitly expanded عروض transcription. It does not choose pronunciation, identify meter, validate labels or licensed variations, or check originality.

## Independent forward trial

An independently prompted agent read the skill, produced actual Arabic responses, and ran the helper without installation. Prompts supplied no intended answer or suggested fix. Raw responses and checker evidence were inspected from `/private/tmp/arabic-poetry-forward-20261014.md`.

| Request | Observed response and executed evidence | Limit |
| --- | --- | --- |
| Explain an empty chair facing a door; ask whether death follows | Linked wording to absence/expectation; declined to infer death or author biography. | Supported interpretation, not proof of intent. |
| Identify «أنادي بلادي / وأمشي وحيدا» | Stated vocalization and وقف, scanned four فعولن, retained whole-form uncertainty. Checker exit `0`, sequence ب − − ⁞ ب − − ⁞ ب − − ⁞ ب − −. | Overlaps the worked exercise; limited generalization evidence. |
| Repair «أُنَادِي بِلَادِي وَأَمْشِي هُنَا وَحِيدًا» to four unmodified فعولن | Deleted هنا, disclosed loss of location reference, rescanned the line. Original sequence ب − − ⁞ ب − − ⁞ ب − − ⁞ ب − ب − −, mismatch exit `1`; repaired sequence ب − − ⁞ ب − − ⁞ ب − − ⁞ ب − −, exit `0`. (The checker has since been removed in favour of the arabic-prosody scanner.) | One viable one-word repair, not exhaustive search or pronunciation proof. |

No execution difficulty was reported. No external integration was tested. Broader unseen examples, representative poets, dialectal traditions, and human literary review remain outside this trial.

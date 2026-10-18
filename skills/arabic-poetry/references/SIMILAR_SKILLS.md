# Similar skills inspected

Source inspection on 2026-10-14 covered five distinct designs. Links below pin the inspected Git commits. These are comparison references, not dependencies or recommendations to install them. No candidate was installed or executed. The findings concern instructions and source, not measured output quality or adoption.

| Primary skill source | Useful idea adapted | Important limit |
| --- | --- | --- |
| [cnemri/arud-skill](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/SKILL.md) | Per-foot diagnostics, separate rhyme analysis, and poem-wide consistency | Classical/tool emphasis. Its accuracy and coverage assertions are author claims; independently verify actual readings and rules. |
| [Moshe-ship/hurmoz arabic-poetry](https://github.com/Moshe-ship/hurmoz/blob/e053ba8a324984b326710769151d4ae155e40041/arabic-poetry/SKILL.md) | Accessible intake and explanation of meaning/rhetoric | Partial meter table, no worked scan or uncertainty workflow. An occasion or بحر must remain unknown when evidence is missing. |
| [Tibsfox poetry-form](https://github.com/Tibsfox/gsd-skill-creator/blob/e179dfe911f3b3c2ff8bcd90ecd6ee4738648d17/examples/skills/writing/poetry-form/SKILL.md) | Examine imagery, pauses, enjambment, and the effect of line placement | English stress-based meter and universal craft preferences do not transfer directly to Arabic عروض or شعر حر. |
| [Tibsfox revision-editing](https://github.com/Tibsfox/gsd-skill-creator/blob/e179dfe911f3b3c2ff8bcd90ecd6ee4738648d17/examples/skills/writing/revision-editing/SKILL.md) | Distinguish whole-piece revision from local edits; try a cut and compare | Expository thesis/topic-sentence conventions can flatten poetry. Respect local repair scope and purposeful ambiguity. |
| [Community textual-evidence-and-close-reading](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/932eb23331721b16e967c59f093781be1928b498/PMLA-Skills/skills/pmla-textual-evidence-and-close-reading/SKILL.md) | Exact phrase, observable feature, explicit interpretive inference; consider resisting details | Community-authored source. Its name does not establish journal endorsement; do not import unverified official submission rules. |

The Hurmoz design also appears in [Mkhlab's Hermes copy](https://github.com/Moshe-ship/mkhlab/blob/5e64b235a11dee43c78b2c912e066fc68c432560/hermes-skills/arabic-poetry/SKILL.md), which is byte-identical at the inspected commits, and a related OpenClaw copy. These are not independent creative approaches.

## Technical material checked rather than inherited

In arud-skill's [variation reference](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/references/zihafs_ilal_reference.md), الخبن deletes the second still letter, so فاعلن − ب − becomes فعِلن ب ب − and فاعلاتن − ب − − becomes فعِلاتن ب ب − −. The inspected الخبن examples instead give the patterns of فعولن ب − − and مفاعيلن ب − − −. These are internally inconsistent transformations; they are not runtime findings about every output of PyArud. Its [meter reference](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/references/buhur_reference.md) claims guaranteed meter separation through costs without an independently verified benchmark here.

Our response is to preserve the sound-to-pattern evidence, check exact coverage, and validate the interpretation against Arabic prosody sources. In this repository the [integrated scanner](../SKILL.md) does the counting in ب − notation.

## How these comparisons changed this skill

- Add a close-reading path without mandatory biographical speculation or meter labels.
- Use line-break and cut-and-restore experiments as local editorial choices, not universal quality tests.
- Keep user wording, assumed vocalization, tool normalization, and analyzer outputs distinguishable.
- Preserve the poet's voice while checking technical correctness and literary effect separately.

This was a dated search sample across public repositories and catalogs, not an exhaustive inventory. Software analyzers, paid listings without readable source, and unrelated scientific-literature skills were excluded from the five-design count.

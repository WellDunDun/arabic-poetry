# Arabic poetry: comparison with existing agent skills

Researched on 2026-10-14. This is a source inspection, not an installation test or a benchmark of generated poems.

## Scope and method

Searches covered public GitHub repositories and the SkillsMP, skills.sh, MDSkill, Skills Directory, SkillMD, SkillsCat, and Agensi catalogs. Queries included `"SKILL.md" "Arabic poetry"`, `"SKILL.md" "poetry" writing revision`, `"skills" "prosody" "github" Arabic`, `"SKILL.md" "close reading"`, and the names of discovered candidates. Catalogs supplied leads. The substantive comparisons below use the owners' actual source files, read at fixed Git commits through public GitHub metadata and raw-source endpoints.

Five distinct skill designs were inspected. The Arabic poetry design appears in three inspected files across two related repositories; those copies do not constitute three independent approaches. No candidate was installed, and no candidate script was executed. Commit dates describe the inspected repository heads, not proof of release, quality, or adoption. This search is a dated sample, not proof that no other Arabic poetry skills exist.

## Source inventory

| Design | Owner and inspected path | Repository revision | Classification |
|---|---|---|---|
| arud-skill | `cnemri/arud-skill`, `SKILL.md`; three prosody references and `scripts/arud_cli.py` | `ed0fbe77429a60729aeb2595178a78d001feb4ba`, 2026-08-21 | Actual agent skill with a Python analyzer wrapper |
| arabic-poetry | `Moshe-ship/hurmoz`, `arabic-poetry/SKILL.md` | `e053ba8a324984b326710769151d4ae155e40041`, 2026-05-30; frontmatter version `1.0.0` | Actual Hermes skill |
| arabic-poetry copies | `Moshe-ship/mkhlab`, `hermes-skills/arabic-poetry/SKILL.md` and `skills/arabic-poetry/SKILL.md` | `5e64b235a11dee43c78b2c912e066fc68c432560`, 2026-05-31; Hermes version `1.0.0` | Related Hermes/OpenClaw packaging of the same workflow |
| poetry-form | `Tibsfox/gsd-skill-creator`, `examples/skills/writing/poetry-form/SKILL.md` | `e179dfe911f3b3c2ff8bcd90ecd6ee4738648d17`, 2026-07-19 | Actual example skill, chiefly English-language craft |
| revision-editing | Same owner, `examples/skills/writing/revision-editing/SKILL.md` | Same fixed revision | Actual example skill for general writing revision |
| pmla-textual-evidence-and-close-reading | `brycewang-stanford/Awesome-Journal-Skills`, `PMLA-Skills/skills/pmla-textual-evidence-and-close-reading/SKILL.md` | `932eb23331721b16e967c59f093781be1928b498`, 2026-09-27 | Actual community skill for literary scholarship; its name does not establish PMLA endorsement |

The two Hermes Arabic poetry files are byte-identical at these commits. Their SHA-256 is `adf1ec7a6cea0bcc02242801edcaab564550bdfd0e9daf29f3054ef5d353b517`. The OpenClaw copy adjusts metadata and presentation while retaining the same core workflow. [Hurmoz source](https://github.com/Moshe-ship/hurmoz/blob/e053ba8a324984b326710769151d4ae155e40041/arabic-poetry/SKILL.md), [Mkhlab Hermes source](https://github.com/Moshe-ship/mkhlab/blob/5e64b235a11dee43c78b2c912e066fc68c432560/hermes-skills/arabic-poetry/SKILL.md), [Mkhlab OpenClaw source](https://github.com/Moshe-ship/mkhlab/blob/5e64b235a11dee43c78b2c912e066fc68c432560/skills/arabic-poetry/SKILL.md).

## What each design contributes

### arud-skill

This is the strongest directly relevant technical baseline in the inspected sample. It separates verse scanning, phonetic transcription, rhyme extraction, defect diagnosis, and poem-wide consistency. Its examples expose actual foot segments, variation names, counts of valid verses, and the dominant rhyme. It links specialized references. Those are useful output and navigation patterns. The entry point concentrates on classical analysis and developer integration; it does not supply a developed creative-revision or prose-poetry workflow. Its claims of deterministic accuracy and comprehensive coverage are the author's claims, not findings from this inspection. [Skill source](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/SKILL.md).

The wrapper requires Python 3.12 or later, declares `pyarud>=1.0.0`, and includes developer-local import search paths. An unbounded lower dependency requirement is not a reproducible analyzer version. The script was read, not run. For any optional integration, record the installed package version and exact input and avoid copying those local paths. [Wrapper source](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/scripts/arud_cli.py).

Its reference tables need independent checking. For example, the stated operation for الخبن is deleting the second silent position, yet فاعلن (− ب −) is shown changing to the pattern of فعولن (ب − −). Applying that deletion yields فعِلن (ب ب −). Likewise, the deletion turns فاعلاتن (− ب − −) into فعِلاتن (ب ب − −), not the table's مفاعيلن pattern (ب − − −). Patterns are given here in the shared ب − syllable notation. These are internal transformation inconsistencies, established without executing the analyzer. The numeric variation-cost table also claims to guarantee separation of similar meters; this inspection provides no benchmark supporting that guarantee. Do not inherit either the faulty patterns or the guarantee. [Variation reference](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/references/zihafs_ilal_reference.md), [Meter reference](https://github.com/cnemri/arud-skill/blob/ed0fbe77429a60729aeb2595178a78d001feb4ba/references/buhur_reference.md).

### Hurmoz and Mkhlab arabic-poetry

The shared design offers a compact intake covering subject, form, and length, then an explanation template covering poet, poem, meaning, rhetoric, occasion, and meter. It warns against uncertain attribution and distinguishes popular/Nabati poetry from formal Arabic. Its limitations are concrete. A heading promises sixteen meters but lists eight, with abbreviated patterns. It instructs the agent to name a meter for every analyzed verse without a pronunciation or uncertainty procedure. It supplies no worked scan or revision-and-rescan loop. Its search example fetches an AlDiwan webpage and labels it an API; the file does not establish a documented structured API. [Primary skill source](https://github.com/Moshe-ship/hurmoz/blob/e053ba8a324984b326710769151d4ae155e40041/arabic-poetry/SKILL.md).

Use the accessible explanation structure, but allow unknown attribution and unestablished meter. Separate source-backed occasion from interpretation. Do not copy the incomplete meter table, famous-phrase shortcut, or mandatory question sequence. Our skill already has stronger scansion and editing procedures. The main opportunity is a fuller explanation workflow that earns interpretive claims through the supplied text.

### poetry-form

The source discusses imagery, sound, enjambment, pauses, and line placement as meaning-making choices. It suggests comparing a lineated poem with a prose rendering to notice what the breaks contribute. Its breadth helps modern-poetry critique. However, its metrical framework is mostly English stress-based prosody, and its definition of free verse should not be translated wholesale into the context-dependent Arabic label شعر حر. Several craft preferences are phrased as universal judgments. [Primary skill source](https://github.com/Tibsfox/gsd-skill-creator/blob/e179dfe911f3b3c2ff8bcd90ecd6ee4738648d17/examples/skills/writing/poetry-form/SKILL.md).

Adapt the comparison as a diagnostic experiment: identify how a particular Arabic line break changes emphasis, suspension, or pace. Treat the result as evidence about that poem, not a categorical test of poetic legitimacy. For Arabic verse, retain phonological scansion and the intended form's conventions. Do not transfer English foot definitions or claim that prose poetry must always use paragraph typography.

### revision-editing

The source separates whole-piece revision from sentence edits and proofreading. Its cut-and-restore experiment and workshop feedback protocol make revision actionable. It also encourages reading aloud. These are transferable editorial methods. Its thesis, topic-sentence, coherence, passive-voice, and mandatory large-to-small rules primarily serve expository prose. Applying them indiscriminately would flatten purposeful poetic fragments, delay, or ambiguity, and would overrun a request to fix one foot. [Primary skill source](https://github.com/Tibsfox/gsd-skill-creator/blob/e179dfe911f3b3c2ff8bcd90ecd6ee4738648d17/examples/skills/writing/revision-editing/SKILL.md).

Adapt the scope hierarchy to the actual request. For a full poem, inspect image movement and the ending before polishing diction. For a local repair, keep the intervention local. A cut should survive both a meaning comparison and a rhythm check. A workshop response can name a successful passage, a concrete problem, and one revision experiment without automatic praise or a compulsory questionnaire.

### pmla-textual-evidence-and-close-reading

The source ties claims to exact wording, formal features, and an explicit inference. It asks readers to consider passages that resist their interpretation and to record edition and translation choices. Its example turns a generic grief claim into a claim about syntax that the reader can check. This is useful for Arabic explanation and critique, especially where a summary of the theme misses the poem's actual language. The skill belongs to a community repository. Its statements about official journal requirements require separate journal-source verification and need not enter our poetry skill. [Primary skill source](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/932eb23331721b16e967c59f093781be1928b498/PMLA-Skills/skills/pmla-textual-evidence-and-close-reading/SKILL.md).

Adapt the evidence chain as `quoted phrase → linguistic or sonic feature → supported effect or reading`. Distinguish the poem's speaker from the historical author. Offer a rival reading only when the wording supports it. Preserve wording and meaningful variants; avoid adding a poet's biography or an occasion to fill a template.

## Other leads and exclusions

- [Agensi's poetry-workshop-persona](https://www.agensi.io/skills/poetry-workshop-persona) is a paid catalog listing with an example and advertised capabilities. The full source package was not inspected. It is not counted as a verified technical baseline, and its security or compatibility claims were not adopted.
- [SkillMD's poetry-prose-expert listing](https://skillmd.com/skills/tomjiu/poetry-prose-expert) shows Chinese poetry/prose content, but the original owner/path was not independently resolved here. It remains a discovery lead rather than a primary-source comparison.
- A [ClawHub submission issue for AppKeys](https://github.com/openclaw/clawhub/issues/173) mentions an Arabic-poetry capability in a general API marketplace. That is not evidence of a dedicated Arabic prosody skill or a validated scanner.
- [pyarud](https://github.com/cnemri/pyarud) and [Aruudy](https://github.com/kariminf/aruudy) are software analyzers, not interchangeable with installable poetry skills. Tool evaluation belongs to a separate comparison. A repository merely mentioning poetry was excluded.
- Search hits named "literature close reading" often concerned scientific papers. They were excluded from the literary comparison unless actual source content dealt with poetry or literary language.

## Improvements supported by this comparison

These are proposed adaptations, not copied code or claims of measured improvement.

| Opportunity | Change to our skill | Reason and source |
|---|---|---|
| Explanation is less developed than identification | Add a compact explanation path covering difficult wording, speaker/situation, one supported interpretive claim, and relevant sound/form | Hurmoz's accessible explanation template plus the close-reading source's evidence chain |
| Technical output can hide input assumptions | For tool-assisted scanning, keep exact supplied text, vocalized reading, normalized tool input, package/version, candidate output, and independent check distinguishable | arud-skill wrapper and explicit per-foot outputs |
| Analyzer match can overstate validity | Describe a score as that analyzer's score; check hemistich boundaries, allowed end forms, and each change independently; preserve unresolved candidates | arud-skill's claims and internally inconsistent reference transformations |
| Modern critique can become a theme summary | Check specific effects of sound, syntax, image progression, breaks, and ending; quote the detail supporting each major judgment | poetry-form and literary close-reading source |
| Revision can erase purposeful ambiguity | Treat compression and cuts as optional experiments, compare meaning and rhythm, and respect the requested edit scope | revision-editing's experiments adapted to poetry |
| Quality needs separate dimensions | Judge instruction adherence, metrical/rhyme validity where applicable, imagery and development, and preserved authorial voice separately | Combined design gap across the inspected skills; this is our synthesis |

Keep existing safeguards for unvocalized readings, incomplete fragments, dialectal traditions, prose poetry, and authorial voice. The inspected skills do not replace Arabic scholarly sources for rules of عروض, قافية, or the contested history and terminology of modern forms.

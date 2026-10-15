# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

```sh
npx skills@latest add WellDunDun/arabic-poetry
```

The repository serves two skills; install either or both:

- `arabic-poetry`: writing, revising, continuing and reading Arabic poetry.
- `arabic-prosody`: a deterministic meter and rhyme scanner with the **Diwan** workbench for checking, fixing and exporting your poems.

Select `arabic-poetry` in your agent. Try requests such as:

- "اكتب قصيدة تفعيلة قصيرة عن العودة إلى البيت."
- "أصلح وزن هذه الأبيات بأقل تغيير، وحافظ على المعنى والقافية."
- "ما نوع هذا الشعر وبحره؟ بيّن التقطيع وما لا يمكن الجزم به."
- "اشرح الصورة والمعنى في هذه القصيدة النثرية من غير افتراض سيرة للشاعر."

## Why it exists

Arabic poetry needs more than fluent phrasing or a guessed meter. This skill connects pronunciation and scansion with meaning, syntax, imagery, and the intended poetic form. It gives classical and modern forms equal standing and distinguishes technical findings from literary preferences.

## Skill

[arabic-poetry](skills/arabic-poetry/SKILL.md) supports composition, continuation, revision, close reading, and form, meter, and rhyme identification. It includes worked examples and an optional local checker for declared sound-pattern arithmetic. The checker does not establish pronunciation or metrical legality by itself.

[arabic-prosody](skills/arabic-prosody/SKILL.md) scans poems with a rule-based engine. It reads the text as it is pronounced, tries the plausible readings (sung or stopped endings, optional lengthenings), matches every half-verse against the 16 meters and their permitted variations, and decides the meter across the whole poem. It reports broken feet in the classical ب − notation, checks the rhyme letter at the end of each verse, and verifies every suggested repair before showing it.

Its **Diwan** page keeps a poet's poems between conversations: confirm the proposed tashkeel word by word, see the scansion update live, ask Claude about any line, and export a poem or the whole collection to Word (PDF on request). Try:

- "check my poem", with a poem pasted with or without tashkeel.
- "ما بحر هذه الأبيات؟" for a poem you admire.
- "صدّر الديوان PDF مع ملحق التقطيع."

The [source references](skills/arabic-poetry/references/SOURCES.md) and [research notes](docs/research/arabic-poetry.md) document the evidence, similar skills, and limitations.

## Collaboration

This project is maintained separately from the [personal skills collection](https://github.com/WellDunDun/skills).

Contributions to poetic examples, Arabic terminology, research, and technical checks are welcome. Preserve the original poet's authorship and acknowledge contributions in the relevant work.

## Credits

- `arabic-poetry` and this repository: Daniel Petro ([@WellDunDun](https://github.com/WellDunDun)).
- `arabic-prosody` and the Diwan workbench: Firas F. Khabour.
- The Amiri typeface bundled for PDF export is by Khaled Hosny, under the SIL Open Font License ([OFL.txt](skills/arabic-prosody/assets/fonts/OFL.txt)).

## License

MIT. See [LICENSE](LICENSE). Linked works remain subject to their own terms; references do not relicense third-party texts.

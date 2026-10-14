# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

```sh
npx skills@latest add WellDunDun/arabic-poetry
```

Select `arabic-poetry` in your agent. Try requests such as:

- "اكتب قصيدة تفعيلة قصيرة عن العودة إلى البيت."
- "أصلح وزن هذه الأبيات بأقل تغيير، وحافظ على المعنى والقافية."
- "ما نوع هذا الشعر وبحره؟ بيّن التقطيع وما لا يمكن الجزم به."
- "اشرح الصورة والمعنى في هذه القصيدة النثرية من غير افتراض سيرة للشاعر."

## Why it exists

Arabic poetry needs more than fluent phrasing or a guessed meter. This skill connects pronunciation and scansion with meaning, syntax, imagery, and the intended poetic form. It gives classical and modern forms equal standing and distinguishes technical findings from literary preferences.

## Skill

[arabic-poetry](skills/arabic-poetry/SKILL.md) supports composition, continuation, revision, close reading, and form, meter, and rhyme identification. It includes worked examples and an optional local checker for declared sound-pattern arithmetic. The checker does not establish pronunciation or metrical legality by itself.

The [source references](skills/arabic-poetry/references/SOURCES.md) and [research notes](docs/research/arabic-poetry.md) document the evidence, similar skills, and limitations.

## Collaboration

This project is maintained separately from the [personal skills collection](https://github.com/WellDunDun/skills).

Contributions to poetic examples, Arabic terminology, research, and technical checks are welcome. Preserve the original poet's authorship and acknowledge contributions in the relevant work.

## License

MIT. See [LICENSE](LICENSE). Linked works remain subject to their own terms; references do not relicense third-party texts.

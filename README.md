# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

### Let your agent install it

Copy one of these prompts into your agent's chat.

انسخ أحد النصين والصقه في محادثتك مع وكيلك.

#### English

```text
Install Arabic Poetry for this agent by following the instructions at https://raw.githubusercontent.com/WellDunDun/arabic-poetry/refs/heads/main/INSTALL.md
```

#### العربية

```text
ثبّت لي مهارات الشعر العربي لهذا الوكيل باتباع التعليمات في https://raw.githubusercontent.com/WellDunDun/arabic-poetry/refs/heads/main/INSTALL.md
```

Your agent handles setup using the [installation guide](INSTALL.md). This requires an agent that can install skills; a chat that can only generate text cannot perform the installation.

يتولى وكيلك الإعداد باتباع [دليل التثبيت](INSTALL.md). يلزم وكيل يستطيع تثبيت المهارات؛ فالمحادثة التي تقتصر على توليد النص لا تستطيع تنفيذ التثبيت.

### Install with a command

```sh
npx skills@latest add WellDunDun/arabic-poetry
```

The repository serves one skill, `arabic-poetry`, with writing and interpretation guidance, a local meter scanner, and the optional **Diwan** editing workbench.

Select `arabic-poetry` in your agent. Try requests such as:

- "اكتب قصيدة تفعيلة قصيرة عن العودة إلى البيت."
- "أصلح وزن هذه الأبيات بأقل تغيير، وحافظ على المعنى والقافية."
- "ما نوع هذا الشعر وبحره؟ بيّن التقطيع وما لا يمكن الجزم به."
- "اشرح الصورة والمعنى في هذه القصيدة النثرية من غير افتراض سيرة للشاعر."

## Why it exists

Arabic poetry needs more than fluent phrasing or a guessed meter. This skill connects pronunciation and scansion with meaning, syntax, imagery, and the intended poetic form. It gives classical and modern forms equal standing and distinguishes technical findings from literary preferences.

## Skill

[arabic-poetry](skills/arabic-poetry/SKILL.md) supports composition, continuation, revision, close reading, and form, meter, and rhyme identification. The agent uses the relevant writing, analysis or editing workflow for the request. Quick questions stay in chat; the editor is optional.

Its local Python scanner compares vocalized text against implemented forms of the 16 meters and their configured variations. It reports feet, candidate meters, mismatches and rhyme candidates. Ranking is heuristic, rhyme analysis starts from spelling, and a zero-error alignment still needs a plausible pronunciation and an independent rule check. A separate arithmetic checker checks a declared transcription; it cannot identify meter by itself.

The skill preserves your wording and tashkeel. Preliminary analysis can state reading assumptions; if you ask to approve a proposed vocalization before analysis, it pauses for your review. Repairs must preserve the intended meaning and explain any tradeoff.

Its **Diwan** page lets you review tashkeel word by word, see scansion update live, work with your agent on a line, and export a poem or collection to Word. A local bridge lets Codex or another agent in your existing chat read requests and return answers to the editor. Click an AI button, then ask your chat to handle the pending Diwan request. The editor does not wake the chat automatically. A copy/paste fallback also works in an ordinary browser; the original Claude integration remains optional. Poems use browser storage unless a host database is available. Word downloads work in a normal browser. The page loads fonts and its browser Word-export library from CDNs. CLI Word export needs Node.js; optional PDF export also needs LibreOffice and font support. See the [editor workflow](skills/arabic-poetry/references/DIWAN.md). Try:

- "check my poem", with a poem pasted with or without tashkeel.
- "ما بحر هذه الأبيات؟" for a poem you admire.
- "صدّر الديوان PDF مع ملحق التقطيع."

The [source references](skills/arabic-poetry/references/SOURCES.md), [scanner coverage notes](skills/arabic-poetry/references/SCANNER-SOURCES.md) and [research notes](docs/research/arabic-poetry.md) document evidence, similar skills, and limitations.

If you previously installed `arabic-prosody`, replace that installation with `arabic-poetry` from this repository. Its scanner, workbench and exporters are now included in the single package.

## Collaboration

This project is maintained separately from the [personal skills collection](https://github.com/WellDunDun/skills).

Contributions to poetic examples, Arabic terminology, research, and technical checks are welcome. Preserve the original poet's authorship and acknowledge contributions in the relevant work.

## Credits

- Original poetry skill, research and repository: Daniel Petro ([@WellDunDun](https://github.com/WellDunDun)).
- Meter/rhyme scanner, Diwan workbench and exporters, originally contributed as `arabic-prosody`: Firas F. Khabour ([@firaskhabour](https://github.com/firaskhabour)). His contribution is retained in the combined skill and Git history.
- The Amiri typeface bundled for PDF export is by Khaled Hosny, under the SIL Open Font License ([OFL.txt](skills/arabic-poetry/assets/fonts/OFL.txt)).

## License

MIT. See [LICENSE](LICENSE). Linked works remain subject to their own terms; references do not relicense third-party texts.

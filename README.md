# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

### ChatGPT and Codex plugin preview

This repository includes a plugin package for ChatGPT and Codex, using the same `arabic-poetry` skill. It is not yet listed in the public Plugins Directory. For a local desktop installation, copy this request into an agent that can access local files and run the supported installer:

```text
Install the Arabic Poetry plugin from https://github.com/WellDunDun/arabic-poetry for this ChatGPT desktop or Codex environment. Use the repository's plugin manifest and marketplace, preserve my existing setup, and verify that its arabic-poetry skill is available in a new chat. Then help me try a poem. If this environment cannot install local plugins, explain the supported alternative.
```

تتضمن هذه النسخة إضافة لـChatGPT وCodex تستخدم مهارة `arabic-poetry` نفسها. لم تُنشر بعد في دليل الإضافات العام. للتثبيت المحلي على سطح المكتب، انسخ الطلب التالي إلى وكيل يستطيع الوصول إلى الملفات وتنفيذ أداة التثبيت المدعومة:

```text
ثبّت إضافة الشعر العربي من https://github.com/WellDunDun/arabic-poetry لبيئة ChatGPT لسطح المكتب أو Codex التي أستخدمها الآن. استخدم ملف تعريف الإضافة ودليل الإضافات في المستودع، وحافظ على إعداداتي الحالية، وتحقق من ظهور مهارة arabic-poetry في محادثة جديدة. ثم ساعدني على تجربة قصيدة. إن كانت هذه البيئة لا تدعم تثبيت إضافات محلية، فوضّح البديل المدعوم.
```

After installation, choose the skill with `@` in ChatGPT or `$arabic-poetry` in Codex. Scanner scripts need command execution; the plugin does not add a hosted Diwan connection. See the [installation guide](INSTALL.md#chatgpt-and-codex-plugin-preview).

بعد التثبيت، اختر المهارة باستخدام `@` في ChatGPT أو `$arabic-poetry` في Codex. تحتاج برامج التقطيع إلى تنفيذ الأوامر؛ ولا تضيف هذه الحزمة اتصالًا سحابيًا بمحرر ديوان. راجع [دليل التثبيت](INSTALL.md#chatgpt-and-codex-plugin-preview).

### Use it in your current chat

Copy one of these prompts into your agent's chat.

انسخ أحد النصين والصقه في محادثتك مع وكيلك.

#### English

```text
Run `npx skills use "https://github.com/WellDunDun/arabic-poetry" --skill "arabic-poetry"` and follow the generated skill instructions now. Read its complete output, redirecting it to a temporary file first if necessary. Resolve relative paths from the supporting-files directory it provides.
```

#### العربية

```text
شغّل `npx skills use "https://github.com/WellDunDun/arabic-poetry" --skill "arabic-poetry"` واتّبع تعليمات المهارة الناتجة الآن. اقرأ المخرجات كاملة، واحفظها أولًا في ملف مؤقت إذا لزم الأمر. اعتبر مجلد الملفات المساندة الذي يحدده الأمر أساسًا لأي مسارات نسبية.
```

This loads the skill for the current conversation without permanently installing it. Your agent needs command execution. For persistent installation, use the command below or the [installation guide](INSTALL.md).

يحمّل هذا المهارة للمحادثة الحالية دون تثبيتها بشكل دائم. يلزم وكيل يستطيع تنفيذ الأوامر. للتثبيت الدائم، استخدم الأمر أدناه أو [دليل التثبيت](INSTALL.md).

### Install permanently

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

Its local Python scanner compares vocalized text against implemented forms of the 16 meters and their configured variations. It reports feet, candidate meters, mismatches and rhyme candidates. Ranking is heuristic, rhyme analysis starts from spelling, and a zero-error alignment still needs a plausible pronunciation and an independent rule check. Scans use ب for short, − for long and = for overlong syllables in pause.

The skill preserves your wording and tashkeel. Preliminary analysis can state reading assumptions; if you ask to approve a proposed vocalization before analysis, it pauses for your review. Repairs must preserve the intended meaning and explain any tradeoff.

Its **Diwan** page lets you review tashkeel word by word, see scansion update live, work with your agent on a line, and export a poem or collection to Word. A local bridge lets Codex or another agent in your existing chat read requests and return answers to the editor. Click an AI button, then ask your chat to handle the pending Diwan request. The editor does not wake the chat automatically. A copy/paste fallback also works in an ordinary browser; the original Claude integration remains optional. Poems use browser storage unless a host database is connected. Word downloads work in a normal browser. The page loads fonts and its browser Word-export library from CDNs. CLI Word export needs Node.js; optional PDF export also needs LibreOffice and font support. See the [editor workflow](skills/arabic-poetry/references/DIWAN.md). Try:

- "check my poem", with a poem pasted with or without tashkeel.
- "ما بحر هذه الأبيات؟" for a poem you admire.
- "صدّر الديوان PDF مع ملحق التقطيع."

The [source references](skills/arabic-poetry/references/SOURCES.md), [scanner coverage notes](skills/arabic-poetry/references/SCANNER-SOURCES.md) and [similar-skill comparisons](skills/arabic-poetry/references/SIMILAR_SKILLS.md) document evidence, similar skills, and limitations.

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

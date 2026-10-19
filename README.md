# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

Choose one installation method. Both include the same poetry skill, scanner and optional Diwan editor.

اختر إحدى طريقتي التثبيت. تتضمن كلتاهما مهارة الشعر نفسها وبرنامج التقطيع ومحرر ديوان الاختياري.

| Installation · التثبيت | Updates · التحديثات |
| --- | --- |
| [Plugin · إضافة](#option-1-install-the-plugin) for supported Claude, Codex and ChatGPT workspaces | Through your host's plugin manager. Automatic updates depend on its settings. · عبر مدير الإضافات في بيئتك، ويعتمد التحديث التلقائي على إعداداته. |
| [Standalone skill with Skills CLI · مهارة مستقلة بأداة Skills CLI](#option-2-install-with-skills-cli) for agents that can run commands | Update manually with Skills CLI. · حدّثها يدويًا بأداة Skills CLI. |

### Option 1: install the plugin

**الخيار الأول: تثبيت الإضافة**

Use the repository marketplace in a supported Claude or Codex host, or a ChatGPT workspace with admin Git import. Copy the English or Arabic prompt into your agent.

استخدم دليل الإضافات المرتبط بالمستودع في بيئة Claude أو Codex تدعمه، أو في مساحة عمل ChatGPT تتيح استيراد Git للمسؤول. انسخ النص الإنجليزي أو العربي إلى وكيلك.

#### English plugin prompt

```text
Install Arabic Poetry from the Git-backed plugin marketplace at https://github.com/WellDunDun/arabic-poetry for the agent I am using. Follow the repository's INSTALL.md for this host and preserve my existing setup. Explain whether updates are automatic, require an opt-in, or need a manual command. Verify the installed version and arabic-poetry skill, then help me try a poem. If this account cannot import the marketplace, explain the limitation and point me to the standalone skill option.
```

#### نص تثبيت الإضافة بالعربية

```text
ثبّت إضافة الشعر العربي من دليل الإضافات المرتبط بمستودع Git على https://github.com/WellDunDun/arabic-poetry للوكيل الذي أستخدمه الآن. اتّبع دليل INSTALL.md الخاص بهذه البيئة وحافظ على إعداداتي الحالية. وضّح هل التحديث تلقائي، أم يحتاج إلى تفعيل خيار، أم يتطلب أمرًا يدويًا. تحقّق من النسخة المثبّتة وظهور مهارة arabic-poetry، ثم ساعدني على تجربة قصيدة. إذا كان حسابي لا يتيح استيراد الدليل، فوضّح القيد وأرشدني إلى خيار المهارة المستقلة.
```

#### Plugin updates · تحديث الإضافة

Updates come through the host's plugin manager. Claude Code requires auto-update to be enabled for this third-party marketplace. ChatGPT workspace Git imports use workspace sync. For Codex and manual refreshes, follow the [installation and update guide](INSTALL.md). Verify the installed version after updating and reload or start a new chat as your host requires.

تصل التحديثات عبر مدير الإضافات في بيئتك. يتطلب Claude Code تفعيل التحديث التلقائي لهذا الدليل الخارجي. ويستخدم استيراد Git في مساحات عمل ChatGPT مزامنة مساحة العمل. لتحديث Codex أو التحديث اليدوي، اتّبع [دليل التثبيت والتحديث](INSTALL.md). تحقّق من النسخة المثبّتة بعد التحديث، وأعد التحميل أو ابدأ محادثة جديدة حسب متطلبات البيئة.

The plugin is not listed in either public plugin directory yet. The public ChatGPT directory package is being prepared for review. Personal ChatGPT accounts cannot use workspace-admin Git import. After approval and publication, directory users receive published package versions. Maintainers must upload and publish each update. GitHub commits alone do not update the public listing, and a manually uploaded ZIP does not follow GitHub updates.

لم تُنشر الإضافة في دليلي الإضافات العامين بعد. يجري إعداد حزمة دليل ChatGPT العام للمراجعة. لا تستطيع حسابات ChatGPT الشخصية استخدام استيراد Git المخصص لمسؤولي مساحات العمل. بعد الاعتماد والنشر، يحصل مستخدمو الدليل على نسخ الحزمة المنشورة. ويجب على القائمين على الإضافة رفع كل تحديث ونشره. لا تُحدّث تغييرات GitHub وحدها القائمة العامة، ولا يتبع ملف ZIP المرفوع يدويًا تحديثات GitHub.

### Option 2: install with Skills CLI

**الخيار الثاني: تثبيت المهارة بأداة Skills CLI**

Install the complete standalone skill with [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill). Your agent needs command execution and Node.js/npm. This route works independently of plugin marketplace support. Copy one of these prompts into your agent.

ثبّت المهارة المستقلة كاملة بأداة [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill). يحتاج وكيلك إلى تنفيذ الأوامر وتوفّر Node.js/npm. تعمل هذه الطريقة دون الحاجة إلى دعم أدلة الإضافات. انسخ أحد النصين إلى وكيلك.

#### English skill prompt

```text
Install the arabic-poetry skill from https://github.com/WellDunDun/arabic-poetry using `npx skills@latest add WellDunDun/arabic-poetry --skill arabic-poetry --global`. Add the appropriate --agent flag to target only the agent I am using. Preserve my existing skills and local changes. Verify that this agent can discover the complete installed skill and its supporting files. Explain how to update it manually with Skills CLI, then help me try a poem. If command execution or Node.js/npm is unavailable, explain what is missing.
```

#### نص تثبيت المهارة بالعربية

```text
ثبّت مهارة arabic-poetry من https://github.com/WellDunDun/arabic-poetry باستخدام `npx skills@latest add WellDunDun/arabic-poetry --skill arabic-poetry --global`. أضف خيار --agent بالقيمة المناسبة لاستهداف الوكيل الذي أستخدمه فقط. حافظ على مهاراتي الحالية وتعديلاتي المحلية. تحقّق من أن الوكيل يستطيع العثور على المهارة المثبّتة كاملة وملفاتها المساندة. وضّح كيفية تحديثها يدويًا بأداة Skills CLI، ثم ساعدني على تجربة قصيدة. إذا تعذّر تنفيذ الأوامر أو لم يتوفّر Node.js/npm، فوضّح ما ينقص.
```

If you prefer running the installation yourself, this command lets you select the agent:

إذا أردت تنفيذ التثبيت بنفسك، يتيح لك هذا الأمر اختيار الوكيل:

```sh
npx skills@latest add WellDunDun/arabic-poetry --skill arabic-poetry --global
```

#### Standalone skill updates · تحديث المهارة المستقلة

The installed skill stays at its current revision until you update it. Skills CLI does not enable background plugin updates. To update only this skill in the user-wide installation above, ask your agent to preserve local changes, run the command below, and verify the result. For a project-only installation, use `--project` instead of `--global` from that project. See [Skills CLI update options](https://github.com/vercel-labs/skills#skills-update).

تبقى المهارة المثبّتة على نسختها الحالية حتى تحدّثها. لا تفعّل أداة Skills CLI تحديثات الإضافات في الخلفية. لتحديث هذه المهارة وحدها في التثبيت على مستوى المستخدم أعلاه، اطلب من وكيلك الحفاظ على التعديلات المحلية، وتنفيذ الأمر أدناه، والتحقّق من النتيجة. للتثبيت داخل مشروع فقط، استخدم `--project` بدلًا من `--global` من داخل المشروع. راجع [خيارات التحديث](https://github.com/vercel-labs/skills#skills-update).

```sh
npx skills@latest update arabic-poetry --global
```

### Try in this chat without installing

**جرّب المهارة في هذه المحادثة دون تثبيت**

For temporary use, copy one of these prompts into an agent that can run commands. This downloads supporting files to a temporary directory. Run the prompt again when you want to load the latest repository version. An existing chat does not reload it automatically.

للاستخدام المؤقت، انسخ أحد النصين إلى وكيل يستطيع تنفيذ الأوامر. يحمّل الأمر الملفات المساندة إلى مجلد مؤقت. أعد تنفيذ النص عندما تريد تحميل أحدث نسخة من المستودع. لا تُحدّث المحادثة الحالية تعليمات المهارة تلقائيًا.

#### English current-chat prompt

```text
Run `npx skills use "https://github.com/WellDunDun/arabic-poetry" --skill "arabic-poetry"` and follow the generated skill instructions now. Read its complete output, redirecting it to a temporary file first if necessary. Resolve relative paths from the supporting-files directory it provides.
```

#### نص الاستخدام في المحادثة بالعربية

```text
شغّل `npx skills use "https://github.com/WellDunDun/arabic-poetry" --skill "arabic-poetry"` واتّبع تعليمات المهارة الناتجة الآن. اقرأ المخرجات كاملة، واحفظها أولًا في ملف مؤقت إذا لزم الأمر. اعتبر مجلد الملفات المساندة الذي يحدده الأمر أساسًا لأي مسارات نسبية.
```

Scanner scripts need execution capability. Diwan runs in a browser; its local agent bridge needs shared local file access. Browser-only chats can use its copy/paste exchange. Neither installation method adds a cloud Diwan connection.

تحتاج برامج التقطيع إلى إمكانية تنفيذ الأوامر. يعمل ديوان في المتصفح، ويحتاج اتصاله المحلي بالوكيل إلى الوصول إلى ملفات مساحة العمل نفسها. ويمكن لمحادثات المتصفح استخدام تبادل الطلب والإجابة بالنسخ واللصق. لا تضيف أي من طريقتي التثبيت اتصالًا سحابيًا بديوان.

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

[Support](SUPPORT.md) · [Privacy](PRIVACY.md)

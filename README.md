# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

### Install the plugin, recommended

Install from the repository-backed **Arabic Poetry** marketplace to keep receiving reviewed updates. Claude and ChatGPT/Codex use the same poetry skill inside their plugin packages. The plugin is not listed in either public plugin directory.

Copy this into your agent:

```text
Install Arabic Poetry from the Git-backed plugin marketplace at https://github.com/WellDunDun/arabic-poetry for the agent I am using. Keep the installation connected to the repository for future updates, explain any update opt-in, and preserve my existing setup. Verify that the installed plugin exposes its arabic-poetry skill, then help me try a poem. If this browser account requires a workspace admin to import the marketplace, explain that limitation and the supported alternative. Do not replace this with a one-time skill copy unless plugin installation is unavailable.
```

للتثبيت مع تلقّي التحديثات، استخدم إضافة **الشعر العربي** من دليل الإضافات المرتبط بالمستودع. تستخدم Claude وChatGPT/Codex المهارة نفسها داخل الإضافة. لم تُنشر الإضافة في دليلي الإضافات العامين.

```text
ثبّت إضافة الشعر العربي من دليل الإضافات المرتبط بمستودع Git على https://github.com/WellDunDun/arabic-poetry للوكيل الذي أستخدمه الآن. أبقِ التثبيت مرتبطًا بالمستودع لتلقّي التحديثات، ووضّح أي خيار يلزم تفعيله للتحديث، وحافظ على إعداداتي الحالية. تحقّق من ظهور مهارة arabic-poetry ضمن الإضافة المثبّتة، ثم ساعدني على تجربة قصيدة. إذا كان استيراد الدليل في حساب المتصفح يحتاج إلى مسؤول مساحة عمل، فوضّح ذلك والبديل المدعوم. لا تستبدل الإضافة بنسخة مستقلة من المهارة إلا إذا تعذّر تثبيت الإضافات.
```

[Installation and update instructions](INSTALL.md) cover Claude web/Desktop/Code, ChatGPT workspace import, and Codex. Automatic updates depend on the host and its settings. Claude Code third-party marketplaces need auto-update enabled; ZIP uploads and standalone skill copies do not follow this repository automatically.

يتضمن [دليل التثبيت والتحديث](INSTALL.md) طرق Claude في المتصفح وسطح المكتب وCode، واستيراد الدليل في مساحات عمل ChatGPT، وCodex. يعتمد التحديث التلقائي على البيئة وإعداداتها؛ ويلزم تفعيله للأدلة الخارجية في Claude Code. ملفات ZIP والنسخ المستقلة من المهارة لا تتبع تحديثات هذا المستودع تلقائيًا.

Scanner scripts need execution capability. Diwan runs in a browser; its local agent bridge needs shared local file access. Browser-only chats can use its copy/paste exchange. This package does not add a cloud Diwan connection.

تحتاج برامج التقطيع إلى إمكانية تنفيذ الأوامر. يعمل ديوان في المتصفح، ويحتاج اتصاله المحلي بالوكيل إلى الوصول إلى ملفات مساحة العمل نفسها. ويمكن لمحادثات المتصفح استخدام تبادل الطلب والإجابة بالنسخ واللصق. لا تضيف الحزمة اتصالًا سحابيًا بديوان.

### Fallback: use the skill in your current chat

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

### Fallback: install a standalone skill

```sh
npx skills@latest add WellDunDun/arabic-poetry
```

The repository serves one skill, `arabic-poetry`, with writing and interpretation guidance, a local meter scanner, and the **Diwan** drafting and editing workbench.

Select `arabic-poetry` in your agent. Try requests such as:

- "اكتب قصيدة تفعيلة قصيرة عن العودة إلى البيت."
- "أصلح وزن هذه الأبيات بأقل تغيير، وحافظ على المعنى والقافية."
- "ما نوع هذا الشعر وبحره؟ بيّن التقطيع وما لا يمكن الجزم به."
- "اشرح الصورة والمعنى في هذه القصيدة النثرية من غير افتراض سيرة للشاعر."

## Why it exists

Arabic poetry needs more than fluent phrasing or a guessed meter. This skill connects pronunciation and scansion with meaning, syntax, imagery, and the intended poetic form. It gives classical and modern forms equal standing and distinguishes technical findings from literary preferences.

## Skill

[arabic-poetry](skills/arabic-poetry/SKILL.md) supports composition, continuation, revision, close reading, and form, meter, and rhyme identification. Creating, continuing or revising a poem opens Diwan automatically with the complete draft when a local viewer is available. Quick questions and explicit chat-only requests stay in chat.

Its local Python scanner compares vocalized text against implemented forms of the 16 meters and their configured variations. It reports feet, candidate meters, mismatches and rhyme candidates. Ranking is heuristic, rhyme analysis starts from spelling, and a zero-error alignment still needs a plausible pronunciation and an independent rule check. Scans use ب for short, − for long and = for overlong syllables in pause.

The skill preserves your wording and tashkeel. Preliminary analysis can state reading assumptions; if you ask to approve a proposed vocalization before analysis, it pauses for your review. Repairs must preserve the intended meaning and explain any tradeoff.

Its **Diwan** page lets you review tashkeel word by word, see scansion update live, work with your agent on a line, and export a poem or collection to Word. A local bridge connects automatic suggestions to an installed, signed-in Claude or Codex client. In manual mode, ask your existing chat to handle the pending Diwan request and return its answer to the editor. These separate requests do not wake the chat automatically. A copy/paste fallback also works in an ordinary browser; the original Claude integration remains optional. The shared-file CLI saves to your poem document; standalone snapshot pages use browser storage. Word downloads work in a normal browser. The page loads fonts and its browser Word-export library from CDNs. CLI Word export needs Node.js; optional PDF export also needs LibreOffice and font support. See the [editor workflow](skills/arabic-poetry/references/DIWAN.md). Try:

- "check my poem", with a poem pasted with or without tashkeel.
- "ما بحر هذه الأبيات؟" for a poem you admire.
- "صدّر الديوان PDF مع ملحق التقطيع."

The [source references](skills/arabic-poetry/references/SOURCES.md), [scanner coverage notes](skills/arabic-poetry/references/SCANNER-SOURCES.md) and [similar-skill comparisons](skills/arabic-poetry/references/SIMILAR_SKILLS.md) document evidence, similar skills, and limitations.

Creating, continuing or revising a poem opens a private Diwan copy with the complete new or revised draft already loaded, without an extra request or paste step. You can also ask "Open Diwan with this poem". Say "keep this in chat" to opt out; quick analysis and explanation stay in chat. The agent uses a local HTML viewer or browser when available and reuses the existing Diwan tab. Reopening preserves saved browser edits. If the host cannot display local HTML, it provides the preloaded file and explains that remaining step. This does not publish the poem or automatically connect the editor's AI buttons to the chat.

عند كتابة قصيدة أو إكمالها أو تعديلها، يفتح الوكيل ديوان تلقائيًا بنسخة خاصة تتضمن المسودة الجديدة أو المعدّلة كاملة، دون طلب إضافي أو نسخ ولصق. ويمكنك أيضًا أن تقول «افتح ديوان بهذه القصيدة». قل «أريد الرد هنا في المحادثة فقط» إذا لم ترد فتح المحرر؛ وتبقى أسئلة التحليل والشرح السريعة في المحادثة. يستخدم الوكيل عارض HTML محليًا أو متصفحًا متاحًا، ويعيد استخدام تبويب ديوان المفتوح ويحافظ على تعديلات المتصفح المحفوظة. إذا تعذّر العرض المحلي، يقدّم الملف المحمّل بالقصيدة ويوضّح الخطوة المتبقية. لا ينشر هذا القصيدة ولا يربط أزرار الذكاء بالمحادثة تلقائيًا.

If you previously installed `arabic-prosody`, replace that installation with `arabic-poetry` from this repository. Its scanner, workbench and exporters are now included in the single package.

The bundled [Diwan CLI](skills/arabic-poetry/references/CLI.md) lets your agent and editor share one `.diwan.json` poem file containing the text, title and review state. Editor saves update that file, and agent saves appear in the editor. Version checks reject stale changes; earlier revisions can be restored without deleting newer history. Ask your agent: "Open this poem as a shared Diwan document. Read the latest version before saving, and keep a draft if there is a conflict." Plain text/Markdown can be imported; they are treated as literal poem text. Shared saving currently requires macOS/Linux and a browser that can reach the agent's local server.

يتيح [سطر أوامر ديوان](skills/arabic-poetry/references/CLI.md) للوكيل والمحرر العمل على ملف قصيدة واحد بصيغة `.diwan.json`، يتضمن النص والعنوان وحالة المراجعة. يحفظ المحرر تعديلاته في الملف نفسه، وتظهر تعديلات الوكيل في المحرر. تُرفض التعديلات المبنية على نسخة قديمة، ويمكن استعادة مراجعة سابقة دون حذف السجل الأحدث. قل لوكيلك: «افتح هذه القصيدة كمستند ديوان مشترك، واقرأ أحدث نسخة قبل الحفظ، واحتفظ بمسودتي عند التعارض». يمكن استيراد النص العادي وMarkdown بوصفهما نص القصيدة حرفيًا. يتطلب الحفظ المشترك حاليًا macOS أو Linux ومتصفحًا يصل إلى الخادم المحلي للوكيل.

**Word replacements:** right-click a word, or two-finger click on a Mac trackpad. Choose **بالمعنى نفسه** for synonyms, **بالتقطيع نفسه** for the same rhythm, or **تؤدّي المعنى وتقيم الوزن** to preserve meaning and repair meter. A normal click edits spelling/vowels. With a connected host or an installed, signed-in Claude/Codex client, suggestions arrive automatically. Select a suggestion to apply it. Local AI actions make separate requests using that client's login and usage allowance; they do not send a turn into your open chat. Ask your agent to open Diwan with Claude, Codex, or manual chat mode. The manual dialog remains available when automatic AI is unavailable.

**بدائل الكلمات:** انقر على الكلمة بزر الفأرة الأيمن، أو بإصبعين على لوحة تتبّع Mac. اختر «بالمعنى نفسه» للمرادفات، أو «بالتقطيع نفسه» للحفاظ على الإيقاع، أو «تؤدّي المعنى وتقيم الوزن» لإصلاح الوزن مع حفظ المعنى. النقر العادي يفتح تعديل الكلمة وتشكيلها. تصل الاقتراحات تلقائيًا إذا كان المضيف متصلًا بنموذج، أو كان Claude/Codex مثبتًا ومسجّل الدخول محليًا. اختر اقتراحًا لتطبيقه. تستخدم طلبات الذكاء المحلية تسجيل الدخول وحصة الاستخدام للعميل المحدد بطلبات مستقلة عن محادثتك المفتوحة. اطلب من وكيلك فتح ديوان مع Claude أو Codex أو وضع المحادثة اليدوي. يبقى مربع الطلب اليدوي بديلًا عند تعذّر الاتصال التلقائي.

An open shared-file Diwan can pick up compatible updates after your plugin manager installs them. It waits until your edits are saved and you finish editing, then reconnects automatically with the same poem and history. Unsaved edits or a save conflict keep the update pending. This requires a session opened with 0.3.1 or later and a supported versioned plugin cache; see [updates](INSTALL.md#versions-and-releases).

يمكن لديوان المشترك المفتوح التقاط تحديث متوافق بعد أن يثبّته مدير الإضافات. ينتظر حفظ تعديلاتك وانتهاء التحرير، ثم يعيد الاتصال تلقائيًا بالقصيدة وسجلها نفسيهما. تبقى المسودات غير المحفوظة أو تعارضات الحفظ سببًا لتعليق التحديث. يلزم فتح الجلسة بالإصدار 0.3.1 أو أحدث واستخدام ذاكرة إضافات ذات إصدارات مدعومة؛ راجع [التحديثات](INSTALL.md#versions-and-releases).

## Collaboration

This project is maintained separately from the [personal skills collection](https://github.com/WellDunDun/skills).

Contributions to poetic examples, Arabic terminology, research, and technical checks are welcome. Preserve the original poet's authorship and acknowledge contributions in the relevant work.

## Credits

- Original poetry skill, research and repository: Daniel Petro ([@WellDunDun](https://github.com/WellDunDun)).
- Meter/rhyme scanner, Diwan workbench and exporters, originally contributed as `arabic-prosody`: Firas F. Khabour ([@firaskhabour](https://github.com/firaskhabour)). His contribution is retained in the combined skill and Git history.
- The Amiri typeface bundled for PDF export is by Khaled Hosny, under the SIL Open Font License ([OFL.txt](skills/arabic-poetry/assets/fonts/OFL.txt)).

## License

MIT. See [LICENSE](LICENSE). Linked works remain subject to their own terms; references do not relicense third-party texts.

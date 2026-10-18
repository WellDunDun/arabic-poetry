# Arabic poetry

A collaborative Agent Skill for writing, revising, continuing, and understanding classical and modern Arabic poetry.

Use it for عمودي، تفعيلة، قصيدة نثر, evidence-led meter and rhyme analysis, and revisions that preserve the poet's meaning and voice.

## Quickstart

### Let your agent install it

Copy either prompt below and paste it into your agent's chat. The agent will check which installation method your app supports and handle the setup where possible.

انسخ أحد النصين أدناه والصقه في محادثتك مع الوكيل. سيتحقق الوكيل من طريقة التثبيت التي يدعمها تطبيقك، ويتولى الإعداد إن كانت أدواته تسمح بذلك.

#### English

```text
Please install Arabic Poetry for me:
https://github.com/WellDunDun/arabic-poetry

I'm not technical. Handle the installation and setup yourself using the tools available in this app, rather than giving me terminal commands.

Identify which agent app I'm using, read the repository's current installation instructions, and use its supported installation method. Install it as a plugin where supported; otherwise install its bundled skills. Include the complete published package, with its references, scanner, and editor assets.

Use the published default branch. Preserve my existing skills, settings, and files. If it is already installed, check its version before making changes.

Verify that the installed skills are discoverable. Check that the local poetry scanner works if this environment supports running it. Clearly distinguish successful installation from features that are unavailable or still need activation.

Use my existing agent and conversation. Don't create another agent session, require a separate AI subscription, or configure paid services.

Ask me only for permissions or actions that genuinely require my involvement. If installation is unsupported here, explain that plainly and give me the simplest supported alternative.

When finished, tell me in plain language:
- What is ready to use.
- Whether I need to reload the app or start a new chat.
- How to begin by pasting a poem or asking you to write one.
```

#### العربية

```text
ثبّت لي إضافة Arabic Poetry للشعر العربي من هذا المستودع:
https://github.com/WellDunDun/arabic-poetry

لست متخصصًا تقنيًا. تولَّ التثبيت والإعداد بنفسك باستخدام الأدوات المتاحة في هذا التطبيق، بدلًا من إعطائي أوامر لأشغّلها في الطرفية.

تعرّف على تطبيق الوكيل الذي أستخدمه، واقرأ تعليمات التثبيت الحالية في المستودع، واتبع الطريقة التي يدعمها التطبيق. ثبّت الحزمة كإضافة إذا كان ذلك مدعومًا، وإلا فثبّت المهارات المضمّنة فيها. ضمّن الحزمة المنشورة كاملة، بما فيها المراجع وأداة فحص الوزن وملفات المحرر.

استخدم الفرع الافتراضي المنشور في المستودع. حافظ على مهاراتي وإعداداتي وملفاتي الحالية. إذا كانت الإضافة مثبتة بالفعل، فتحقق من نسختها قبل إجراء أي تغيير.

تحقق من أن الوكيل يستطيع العثور على المهارات المثبتة. جرّب أداة فحص الوزن المحلية إذا كانت هذه البيئة تسمح بتشغيلها. وضّح الفرق بين نجاح التثبيت وبين الميزات غير المتاحة أو التي ما زالت تحتاج إلى تفعيل.

استخدم وكيلي ومحادثتي الحاليين. لا تنشئ جلسة وكيل أخرى، ولا تطلب اشتراكًا منفصلًا في خدمة ذكاء اصطناعي، ولا تُعِدّ خدمات مدفوعة.

لا تطلب تدخّلي إلا لمنح صلاحية أو تنفيذ خطوة لا يمكنك إتمامها بدوني. إذا كانت هذه البيئة لا تدعم التثبيت، فاشرح ذلك بوضوح وقدّم أبسط بديل مدعوم.

عند الانتهاء، أخبرني بلغة بسيطة:
- ما الذي أصبح جاهزًا للاستخدام.
- هل أحتاج إلى إعادة تحميل التطبيق أو بدء محادثة جديدة.
- كيف أبدأ بلصق قصيدة أو بطلب كتابة قصيدة منك.
```

These prompts install the published version. Unmerged changes are not included.

يثبّت هذان النصان النسخة المنشورة. ولا يشمل التثبيت التغييرات التي لم تُدمج بعد.

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

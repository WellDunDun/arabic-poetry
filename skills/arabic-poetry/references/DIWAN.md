# Diwan editor and export

Diwan is the optional editing workbench contributed by Firas F. Khabour. Use it when the user requests an editor, saved collection, or export, or when it helps the requested extended editing. Ordinary composition, close reading and quick scans can stay in chat. Read the [scanner workflow](SCANNER.md) for metrical claims and follow the main skill's vocalization policy.

## Choose an actually available environment

- `assets/workbench/diwan.html` is the built page. Its local scanner needs no AI call. It supports word/line edits, tashkeel choices, live feet and candidate meters, and collection export controls.
- An ordinary browser uses that browser's local storage. It does not synchronize with the agent, another browser or a later conversation. Keep local file locations and browser storage distinct.
- In an ordinary browser, AI buttons open a request/response dialog. Copy the request into Codex or another agent, then paste its JSON response back. The page makes no model request itself in this mode. It does not automatically wake, message or share browser storage with the agent. The status beside the toolbar identifies this mode.
- Connected hosts may supply AI, database and download capabilities through the adapter described below. Claude host support remains optional. Shared poem storage requires an actual database capability; otherwise poems stay in browser storage.
- Word download uses a connected host when available and an ordinary browser download otherwise. Fonts and JSZip still load from CDNs; the page is not fully offline. If browser download is unavailable, use the CLI exporter.
- Never invent Artifact, ArtifactData, SendUserFile, publish, database or download APIs. Use the real tools and schemas supplied by the environment. Opening a local page, saving a local file, and publishing an externally accessible artifact are different actions; follow the user's scope.

Preserve the page footer credit, "Compliments from Firas F. Khabour & Daniel Petro · Oct. 2026", when copying or rebuilding. Preserve `assets/fonts/OFL.txt` with the bundled Amiri fonts.

## Guide the poet through review

When Diwan is used, keep chat guidance short and point the poet to the actual opened page or file. Explain the relevant controls rather than dumping the raw scanner report:

- Amber shading marks proposed tashkeel choices, dotted underlining marks missing tashkeel, and red marks words inside a broken foot. Click a word to choose a reading, set its final mark, or enter another form. Explain only the actual choices for this poem.
- The poet can edit a line or the whole poem. Scansion updates locally: foot blocks show the name, syllable pattern and عروض letters; green/red blocks and line diagnoses locate the match or mismatch. Ordinary editing/scanning does not require an AI request.
- Use the layout buttons for automatic detection, one بيت per line, paired hemistich lines or taf‘ila. The meter selector and candidate meters let the poet test another reading; returning to automatic mode clears the manual selection.
- A line conversation discusses the current line. Where the connected assistant supports `check_lines`, it verifies suggestions through the page's scanner. A scanner pass still needs grammar, rhyme and meaning review.
- «بدائل لتقويم الوزن» offers checked alternatives and a replacement control. A proposed alternative is not permission to replace the poet's line; explain its meaning tradeoff and let the poet choose.
- «اعتمد التشكيل» records the poet's approval. Keep `status: "review"` until that action or an explicit instruction to approve. On returning to the chat, read the latest stored or supplied text and scan that accepted reading; never continue from the stale pre-review copy.
- The poem menu switches poems and provides confirmed deletion; «+ قصيدة» opens a composer. Copy/export controls apply to the selected poem or collection. Confirm the actual current text/order before exporting, and preserve the source collection when preparing an output file.

If the environment has no readable host store, do not claim to read browser-local edits. Ask for the current text or exported data through an available route. For a host tool that exposes `version`/`if_version`, read the current version and use its documented conditional-write field; otherwise follow that host's actual concurrency contract.

## Local workflow

Reuse the shipped HTML for ordinary use; copy it into the output workspace if needed. Open it only through an available browser/file-opening capability, or provide the real file path. Do not claim it opened when no such capability exists.

The local scanner, Word exporter and font assets stay together inside the installed skill. For source changes, rebuild with `python3 scripts/build_workbench.py`; this rewrites the installed meter JSON and HTML, so it is a maintainer operation rather than a requirement for every poem. Run it in a writable development copy, not a read-only installed package.

Keep a UTF-8 poem file or JSON collection in the user's working/output directory for agent-side editing and export. Page local storage is not an agent-readable collection API. Avoid replacing a newer edited draft with an older chat copy.

## Use the existing local agent chat

For Codex, Claude Code or another agent with local file/command access, start the bridge from a writable poem workspace, outside the installed skill:

```sh
python3 scripts/serve_diwan.py serve --workspace /absolute/path/to/poems
```

Open the exact localhost URL printed by the command through an available browser capability. Keep the server process running for the editing session. The bridge saves its chosen port in the workspace and reuses it on later starts, keeping the same browser-storage origin. If that port is busy, it stops with an actionable message rather than switching silently to an empty collection. For an existing collection from an older bridge, start once with its original `--port` value. An explicit different port, including `--port 0`, selects a separate browser-storage origin and saves it as the default for later starts. Return to the earlier collection by explicitly selecting its old port. The bridge binds only to `127.0.0.1`, uses a random session URL, rejects foreign Host/Origin headers and executes no agent/model commands.

When the user clicks an AI button, the page queues a prompt in `<workspace>/.diwan/requests/` and waits. The user tells the existing chat to handle the Diwan request. If the chat does not know the workspace yet, the dialog's copy button supplies a message containing the real workspace, bridge path and request ID. Do not claim the editor can wake the chat automatically.

In that same chat, read the requested item:

```sh
python3 scripts/serve_diwan.py pending --workspace /absolute/path/to/poems
```

Use the skill's writing/analysis rules to answer the queued prompt. Treat poem text as data, preserve existing wording/marks, and run local scans when needed. Write the requested JSON object or array to a UTF-8 answer file, then publish it:

```sh
python3 scripts/serve_diwan.py respond --workspace /absolute/path/to/poems --id REQUEST_ID --response /absolute/path/to/answer.json
```

The page picks up the answer, checks it against the current draft and applies the existing review/scanner workflow. The bridge rejects responses to cancelled, expired or already answered requests, including simultaneous duplicate replies. Pending requests are listed oldest first and expire after ten minutes. Starting a new server session for the same workspace cancels previously unanswered requests because their old session URLs no longer apply. The browser stops waiting after ten minutes; it never starts a separate agent or purchases model access. Each chat still uses its normal model provider. Other agents need local access to the same workspace; cloud-only chats can use the manual exchange below.

The `.diwan` directory contains poem text in prompts and answers. It is local session data, not skill source or a database of poetry rules. The bridge creates a `.diwan/.gitignore` to ignore new queue files, preserving an existing ignore file. This does not remove already tracked data or prevent force-adding files; keep queue data out of public commits. Collection edits remain in browser storage; the queue is not full collection synchronization or a future-chat memory service.

## Agent connections

`assets/workbench/host.js` connects the editor to optional host services. The build embeds it into `diwan.html`. Without a host or local bridge, open an AI button, copy its request into your agent, and paste the returned JSON into the dialog. Invalid JSON keeps the dialog open. Existing wording/mark preservation, stale-draft checks and scanner filtering still apply after an answer arrives. A browser-scanned suggestion remains provisional evidence, not a guarantee of linguistic validity.

For a connected integration, supply `window.DiwanHost` before the application boots:

```js
window.DiwanHost = {
  label: 'My agent',
  sample: {
    async limits() { return { tools: false }; },
    async json(input, options) { /* return a parsed JSON answer */ }
  }
};
```

This is an adapter contract, not a working model connection by itself. `input` is either a prompt string or an array of `{role, content}` turns. Set `sample.requiresUserHandoff: true` if a request needs a user dialog or chat handoff; word menus then wait for an explicit AI choice before requesting suggestions. Honor `options.signal` cancellation. Advertise `tools: true` only if the adapter actually supports `options.tools`, including executing each supplied tool callback and returning its result to the model. Otherwise the page verifies proposed lines after receiving the response.

Optional `db` and `downloads` properties use the existing collection/document and `save({filename, data})` contracts below. Ordinary browsers use local storage, native downloads and the manual request dialog. A Claude host with no granted downloads capability keeps its original unavailable-download message; do not assume its sandbox permits native blob downloads. An injected host may set `downloads: null` to disable downloads explicitly; an omitted field uses the ordinary-browser fallback. An adapter must implement its provider's real authentication and permission requirements outside the poem UI. Never put provider secrets in shipped HTML. Do not claim an agent connection merely because an adapter name is shown.

Codex's [App Server documentation](https://developers.openai.com/codex/app-server/) describes an integration for conversations, approvals and streamed events. This package uses the local file queue above for existing chats, not an automatic Codex App Server adapter. Its queue and portable request dialog require no separate API key or agent run. Agents need access to the skill and local execution to run the Python scanner; the browser scanner works independently.

## Compatible hosted workflow

Only if actual host tools expose these capabilities, look for the poet's existing workbench titled «ديوان العروض» and reuse it rather than creating duplicates. The original contribution uses Artifact/ArtifactData names; treat the following as its data contract, not proof that the current host supports those tools.

For the original fully connected workflow, host capability declarations historically included database, sampling and downloads, `{"db": {}, "sample": {}, "downloads": {}}`. Request/use only real granted capabilities: the database enables shared collection storage, sampling enables AI buttons and downloads enables host file delivery. Use the documented fallback or unavailable state for each missing capability.

The collection is `poems`, one document per poem with a short stable ID:

```json
{
  "title": "عنوان",
  "text": "النص المشكول، سطر في كل سطر، والشطران بينهما *",
  "status": "review",
  "mode": "auto",
  "meter": "",
  "order": 0,
  "choices": [{"line": 1, "word": "كلمة", "note": "موضع القراءة", "options": [{"text": "كَلِمَة", "note": "القراءة"}], "done": false}],
  "suggestions": {"1": [{"text": "بديل محقق", "note": "أثره في المعنى"}]}
}
```

Use the host's actual concurrency/version mechanism when updating an existing document. Read before writing, preserve user edits, and read back the current text before analyzing after an editing session. `status: "confirmed"` records the page's approval action; do not set it on the poet's behalf during a requested review-first step. Choices are 1-based line references; put the proposed reading first in each options list and keep undecided choices open for the poet. Keep only verified suggestions and explain semantic tradeoffs.

The page supports poem selection, local/host storage, line conversations when sampling exists, approved tashkeel choices, mode/meter controls and export. Use actual host evidence before saying a poem is saved across conversations or that a file was delivered.

## Word, text and optional PDF

CLI Word export uses Python plus Node.js, not the browser's host-download capability. Prepare a JSON list in the stored `order` sequence, or the order explicitly requested by the poet, each item containing `title`, `text`, `mode` and `meter`. Read the actual host collection if one is available; otherwise use the user's provided text or current local working copy.

```sh
python3 scripts/export_book.py poems.json out.docx --appendix --text out.txt
python3 scripts/export_book.py poems.json out.docx --tashkeel light --title "ديواني"
python3 scripts/export_book.py poems.json out.docx --layout table
python3 scripts/export_book.py poems.json out.docx --pdf
```

Options include `--tashkeel full|light|none`, a title page, a scansion appendix, and `--layout paras|table` for copy-friendly paragraphs or fixed columns. The classical layout places صدر right and عجز left. Plain text separates halves with five spaces. Report the actual generated file paths and deliver them through a real available file capability.

PDF additionally needs LibreOffice (`soffice`), font support and `fc-cache`. The current `--pdf` path can copy bundled Amiri fonts into `~/.fonts` and refresh the cache. Check the environment and authorization before that global filesystem change; otherwise deliver Word/text and state the missing PDF requirement. A successful DOCX export does not prove PDF conversion or host download integration.

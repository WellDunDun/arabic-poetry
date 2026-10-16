# Diwan editor and export

Diwan is the optional editing workbench contributed by Firas F. Khabour. Use it when the user requests an editor, saved collection, or export, or when it helps the requested extended editing. Ordinary composition, close reading and quick scans can stay in chat. Read the [scanner workflow](SCANNER.md) for metrical claims and follow the main skill's vocalization policy.

## Choose an actually available environment

- `assets/workbench/diwan.html` is the built page. Its local scanner needs no AI call. It supports word/line edits, tashkeel choices, live feet and candidate meters, and collection export controls.
- An ordinary browser uses that browser's local storage. It does not synchronize with the agent, another browser or a later conversation. Keep local file locations and browser storage distinct.
- AI buttons require a compatible host's Claude sampling capability. Shared poem storage requires its database capability. Browser Word download additionally requires host downloads. Do not claim these integrations exist merely because the HTML is open.
- Fonts and JSZip load from CDNs; the page is not fully offline. In a host without sampling/database/download support, use manual editing and local files plus the CLI exporter.
- Never invent Artifact, ArtifactData, SendUserFile, publish, database or download APIs. Use the real tools and schemas supplied by the environment. Opening a local page, saving a local file, and publishing an externally accessible artifact are different actions; follow the user's scope.

Preserve the page footer credit, "Compliments from Firas F. Khabour & Daniel Petro · Oct. 2026", when copying or rebuilding. Preserve `assets/fonts/OFL.txt` with the bundled Amiri fonts.

## Local workflow

Reuse the shipped HTML for ordinary use; copy it into the output workspace if needed. Open it only through an available browser/file-opening capability, or provide the real file path. Do not claim it opened when no such capability exists.

The local scanner, Word exporter and font assets stay together inside the installed skill. For source changes, rebuild with `python3 scripts/build_workbench.py`; this rewrites the installed meter JSON and HTML, so it is a maintainer operation rather than a requirement for every poem. Run it in a writable development copy, not a read-only installed package.

Keep a UTF-8 poem file or JSON collection in the user's working/output directory for agent-side editing and export. Page local storage is not an agent-readable collection API. Avoid replacing a newer edited draft with an older chat copy.

## Compatible hosted workflow

Only if actual host tools expose these capabilities, reuse an existing Diwan rather than creating duplicates. The original contribution uses Artifact/ArtifactData names; treat the following as its data contract, not proof that the current host supports those tools.

If host creation supports capability declarations, the page requires database, sampling and downloads, historically `{"db": {}, "sample": {}, "downloads": {}}`. Request/use only real granted capabilities. If unavailable, keep the local/chat workflow.

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

Use the host's actual concurrency/version mechanism when updating an existing document. Read before writing, preserve user edits, and read back the current text before analyzing after an editing session. `status: "confirmed"` records the page's approval action; do not set it on the poet's behalf during a requested review-first step. Choices are 1-based line references. Keep only verified suggestions and explain semantic tradeoffs.

The page supports poem selection, local/host storage, line conversations when sampling exists, approved tashkeel choices, mode/meter controls and export. Use actual host evidence before saying a poem is saved across conversations or that a file was delivered.

## Word, text and optional PDF

CLI Word export uses Python plus Node.js, not the browser's host-download capability. Prepare a JSON list in the desired order, each item containing `title`, `text`, `mode` and `meter`. Read the actual host collection if one is available; otherwise use the user's provided text or current local working copy.

```sh
python3 scripts/export_book.py poems.json out.docx --appendix --text out.txt
python3 scripts/export_book.py poems.json out.docx --tashkeel light --title "ديواني"
python3 scripts/export_book.py poems.json out.docx --pdf
```

Options include `--tashkeel full|light|none`, a title page, and a scansion appendix. The classical layout places صدر right and عجز left. Plain text separates halves with five spaces. Report the actual generated file paths and deliver them through a real available file capability.

PDF additionally needs LibreOffice (`soffice`), font support and `fc-cache`. The current `--pdf` path can copy bundled Amiri fonts into `~/.fonts` and refresh the cache. Check the environment and authorization before that global filesystem change; otherwise deliver Word/text and state the missing PDF requirement. A successful DOCX export does not prove PDF conversion or host download integration.

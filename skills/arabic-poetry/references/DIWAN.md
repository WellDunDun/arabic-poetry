# Diwan editor and export

Diwan is the optional editing workbench contributed by Firas F. Khabour. Use it when the user requests an editor, saved collection, or export, or when it helps the requested extended editing. Ordinary composition, close reading and quick scans can stay in chat. Read the [scanner workflow](SCANNER.md) for metrical claims and follow the main skill's vocalization policy.

## Choose an actually available environment

- `assets/workbench/diwan.html` is the built page. Its local scanner needs no AI call. It supports word/line edits, tashkeel choices, live feet and candidate meters, and collection export controls.
- An ordinary browser uses that browser's local storage. It does not synchronize with the agent, another browser or a later conversation. Keep local file locations and browser storage distinct.
- AI buttons require a compatible host's Claude sampling capability. Shared poem storage requires its database capability. Browser Word download additionally requires host downloads. Do not claim these integrations exist merely because the HTML is open.
- Fonts and JSZip load from CDNs; the page is not fully offline. In a host without sampling/database/download support, use manual editing and local files plus the CLI exporter.
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

## Compatible hosted workflow

Only if actual host tools expose these capabilities, look for the poet's existing workbench titled «ديوان العروض» and reuse it rather than creating duplicates. The original contribution uses Artifact/ArtifactData names; treat the following as its data contract, not proof that the current host supports those tools.

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

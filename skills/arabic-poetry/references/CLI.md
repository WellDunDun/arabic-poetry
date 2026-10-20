# Shared-file Diwan CLI

Use the bundled `scripts/diwan.py` when the editor and agent can reach the same local computer. It uses Python's standard library; safe writes currently require macOS/Linux. Opening, saving and scanning need no model request or cloud publication. AI suggestions use the selected installed Claude/Codex client's existing login and usage allowance; no separate API key is required. Commands never prompt. Help is offline and has no setup side effects.

## One authoritative poem

The canonical `.diwan.json` file contains the title, exact UTF-8 poem text, review choices, suggestions, status, layout, meter, stable id, increasing revision and save identity. Both CLI and editor read/write this document. Browser storage is not the poem store in this mode. Hidden `.diwan/shared/` files contain immutable history, save receipts and local session state, not a competing current poem.

Import `.txt` or `.md` with `create --text-file`. Their complete contents are literal poem text; Markdown headings/frontmatter are not parsed or stripped. The original import file remains unchanged and is no longer the live draft. Export `txt`/`md` to obtain plain poem text again. Do not treat an old import/export as the latest shared document.

Run from the installed skill directory, or replace the script path with its absolute installed location:

```sh
python3 scripts/diwan.py --help
python3 scripts/diwan.py agent-context --command update --json
python3 scripts/diwan.py create /absolute/poems/window.diwan.json --title نافذة --text-file /absolute/poems/draft.txt --json
python3 scripts/diwan.py open /absolute/poems/window.diwan.json --agent auto --no-browser --json
python3 scripts/diwan.py get /absolute/poems/window.diwan.json --json
```

Create the parent poem directory first. Use the current complete new/revised draft as input. Repeating create at the same path with the same initial fields returns the existing document; different content is a conflict, not permission to overwrite it. Preserve unrelated originals and use a separate canonical proposal when the poet has not accepted a revision.

`open` starts or reuses an owned loopback server and returns its exact URL. With `--no-browser`, open that URL through the agent's real browser capability and verify the visible poem. Without it, the CLI asks the operating system to open the browser; `browser_open_requested` is a request, not proof of rendered display. A display failure can leave a working server: use its returned URL rather than recreating the poem. `serve` runs in the foreground; `stop FILE` stops the owned server without changing the poem. Reopening reuses a healthy session. The editor is for one shared document; create/open another file for another poem.

If the current host cannot reach the same loopback server, state that limitation. A [preloaded snapshot](DIWAN.md#open-with-the-current-poem) remains available for local HTML viewers, but its browser edits do not synchronize to the canonical file. Do not promise shared-file behavior for that fallback.

## Updates in an open editor

Shared-file sessions opened with version 0.3.1 or later can follow compatible updates already installed by the plugin manager. The local runtime checks the same plugin's versioned cache, including user-scope Claude Code installations and Codex installations. It does not fetch Git commits or install packages. Keep the host's update settings enabled, or use its normal update command. Pinned installations remain pinned. Account-only/ZIP installations, standalone copies and development checkouts require reopening with the updated package.

An idle editor reconnects and reloads automatically, keeping its address, canonical poem, revision history and selected AI client. An update waits while a text/word/line editor, title input, unsent question, save, conflict, export or AI request is active. It never saves or discards a draft to make an update proceed. Complete the edit and wait for a successful save, or cancel it explicitly. A failed/conflicting save keeps the draft and existing recovery controls; a compatible server handoff triggered by another tab must also leave that draft visible. If the new worker cannot start, Diwan returns to the last working version and shows a notice.

Older running sessions need one safe reopen to acquire this mechanism. Check that there are no unsaved edits before stopping/reopening such a session; never overwrite the poem or refresh an active draft. Native hosted/snapshot pages do not use this local runtime handoff.

## Conditional saving and recovery

Read `get --json` immediately before preparing an accepted save. Its `version` is an opaque content hash; `poem.revision` is the human-readable revision number. Write a JSON patch containing only intended editable fields, or use `--text-file` for an exact text-only update. `--input -` and `--text-file -` read stdin; empty input fails promptly.

```sh
python3 scripts/diwan.py update /absolute/poems/window.diwan.json --input /absolute/poems/change.json --if-version CURRENT_VERSION --request-id edit-window-1 --json
python3 scripts/diwan.py history /absolute/poems/window.diwan.json --limit 20 --json
python3 scripts/diwan.py restore /absolute/poems/window.diwan.json --revision OLD_VERSION --if-version CURRENT_VERSION --request-id restore-window-1 --json
```

Replace version placeholders with actual `get`/`history` results. Reuse the same request id, patch and expected version when retrying the same uncertain save. Reusing an id with different input fails. Receipts recover a write interrupted after the canonical file changed. A replay reports both the originally applied version and the current document; it does not roll back later edits. A restore creates a new revision and retains intervening history. History defaults to 20 entries, supports `--before NEXT_CURSOR`, and never silently deletes older versions.

On `CONFLICT`, preserve the newer file and your proposed draft. Reread, compare and reassess; never silently substitute a fresh version for the stale patch. The editor keeps a conflicting draft visible, offers a download, and requires an explicit discard/reload to take the saved version. It warns before leaving with unsaved edits. It does not automatically merge simultaneous changes.

All supported writers use the same advisory file lock and conditional check, followed by an atomic complete-file replacement. Version history is durable before replacement. This prevents stale CLI/browser writes and torn saves between cooperating clients. A tool directly overwriting JSON outside this API ignores that lock and is unsupported; agents must use `update`, not a raw file write. Directory/file I/O failures can leave a committed save with an incomplete receipt: inspect `get` and retry the same operation identity, not a new create.

Create, update, restore, open and export accept `--dry-run`. A preview validates inputs without changing files, reserving a version or starting a browser/server. No delete command is provided. History and receipts are keyed by the stable poem id, while a directory-wide lock also covers case and Unicode filename aliases on macOS. Different files with a copied id in one workspace are rejected; import a new document instead. Renaming within the same directory retains history; `open` shuts down the old session and starts one at the new path, and `stop` can stop it directly. Stop the session before moving a poem to another directory or moving its workspace. Keep the canonical file and its .diwan history together when moving a workspace. Moving only the poem retains current content, not history in its former directory. There is no dedicated migration command. If shutdown cannot be confirmed, keep the session receipt and retry `stop` or `open`.

## Scan, export and existing chat

```sh
python3 scripts/diwan.py scan /absolute/poems/window.diwan.json --json
python3 scripts/diwan.py export /absolute/poems/window.diwan.json --format docx --output /absolute/poems/window.docx --json
python3 scripts/diwan.py pending /absolute/poems/window.diwan.json --limit 20 --json
python3 scripts/diwan.py respond /absolute/poems/window.diwan.json --id REQUEST_ID --input /absolute/poems/answer.json --json
```

Scanning uses Firas F. Khabour's existing local engine; interpret pronunciation/rules through [SCANNER.md](SCANNER.md). Export supports `txt`, literal `md`, and `docx`; Word uses the existing Node exporter. Existing identical output is reused. Different output needs another filename or explicit `--overwrite`. Generation happens in a temporary directory; final delivery is atomic and returns path/hash/bytes/source version. No PDF capability is added here.

Right-click a poem word, or use a two-finger click on a Mac trackpad, to open its replacement menu. A normal click edits spelling and vowels. Opening the replacement menu requests suggestions automatically when AI is connected; selecting a suggested replacement saves through the shared-file version guard. Failed requests show an error and a retry choice rather than leaving a spinner running.

New `open` and `serve` sessions detect a client automatically: prefer Claude when launched inside Claude Code, otherwise Codex if installed, then Claude. Reopening a running session preserves its current client unless `--agent` is explicit. Choose `--agent claude` or `--agent codex` when selecting that agent; the returned receipt names the actual client. An explicit change replaces the owned server at its existing port without changing the poem. Each AI action is a separate bounded model request through that client's saved login, not a turn in the existing conversation. It receives the bundled skill guidance and current poem/diagnostics, runs without shell/MCP access, and cannot save the poem. Calls use isolated client settings and low reasoning effort for interactive suggestions, keep no persistent chat session, time out after two minutes, and never retry or switch providers silently. The browser still checks suggested text against the current draft and scanner before applying it. A supplied host AI connection takes precedence without moving shared-file storage to a hosted database.

Use `--agent manual` to require the existing conversation instead. If neither client is installed, `auto` selects this fallback. Its dialog asks the poet to tell their chat to handle the request. Read bounded `pending` results, use the poetry skill, and `respond` with the required JSON. Cancellation stops an automatic client process; manual cancelled/expired requests cannot accept a response. A queued answer alone does not save a poem.

Results are JSON on stdout; errors are JSON on stderr. Exit codes: 0 success, 2 invalid input, 4 missing file/version, 5 conflict, 6 I/O, unsupported platform or delivery uncertainty. A nonzero exit does not prove that a preceding save or server launch was rolled back. Structured discovery describes the current flags, mutual exclusions and conditional capabilities. Profiles and remote-job controls are not applicable to this local, explicitly addressed workflow.

# Changelog

## 0.3.1, safe updates in an open Diwan, unreleased

- Let an explicit stop cancel an update, including the brief interval when the local server is offline. Confirm supervisor shutdown before reporting success.
[Customer release notes in English and Arabic](docs/releases/0.3.1.md) include automatic word suggestions from the pending 0.3.0 changes, safe editor updates and the one-time upgrade steps. This candidate is not yet released.

- Follow compatible plugin versions already installed in the same Claude Code user-scope or Codex versioned cache. Keep the open editor's address, poem identity, saved text, revision history and selected AI client through a supervised restart.
- Wait for saved, idle editors before reloading. Preserve unsaved bulk/line/word/title edits, unsent questions, in-flight saves, conflicts and AI requests, including when another tab initiates the update.
- Return to the working package if an updated worker fails to start. Keep plugin installation under the host's existing update settings; older sessions require one safe reopen.

## 0.3.0, automatic Diwan suggestions, unreleased

- Preserve automatic/manual client selection when reopening a poem, including older sessions. Reuse a healthy session when its client is absent from a new shell's PATH.
- Restore automatic word suggestions through native host AI, including shared-file and preloaded poems, without changing their storage.
- Add automatic requests through an installed, signed-in Claude or Codex client. Opening a word replacement menu requests suggestions without a modal or chat handoff; selecting a replacement saves through the existing version guard.
- Add explicit client selection, bounded tool-free requests, timeout/cancellation handling and visible errors with retry. Keep manual chat mode as a fallback.
- Explain right-click word controls and automatic-client usage in English and Arabic.

## 0.2.0, shared-file Diwan CLI, unreleased

- Shut down an owned server before replacing its session after a rename within its directory. Preserve the renamed poem's identity/history when a new poem reuses its old filename; an old server cannot read or modify that replacement poem. Serialize server replacement and shutdown, report actual stop results, and retain receipts on uncertain shutdown. Stop sessions before moving to another directory.
- Reject copied document identities before reporting successful create replay, open or update previews.

- Refresh a clean editor after closing or cancelling an edit that deferred an agent save. Preserve literal bulk-edit whitespace and avoid a revision for unchanged text. Report missing, conflicting and invalid queue responses with their documented CLI error codes.

- Explicitly disclose consequential pronoun readings introduced by tashkeel, while preserving readings fixed by supplied marks or context.

- Add a bundled CLI for discovery, import/create, reading, conditional updates, history, restore, local opening, scanning, export and existing-agent requests.
- Share one `.diwan.json` poem document between editor and agent. Preserve exact imported text and keep title/review state with it. Browser edits save to that file; clean editors refresh when another writer saves.
- Reject stale saves, retain conflicting browser drafts, and provide recovery controls. Add atomic file replacement, immutable revision snapshots and save identities that recover interrupted acknowledgements without duplicating a save.
- Keep the preloaded HTML workflow as a clearly labeled snapshot fallback. It does not synchronize source files. Safe shared writes currently require macOS/Linux and a browser that reaches the same local server.

## 0.1.2, preloaded local Diwan, unreleased

- Open Diwan automatically with the complete draft when creating, continuing or revising a poem, as well as on explicit editor requests. Keep quick analysis, review-first pauses and explicit chat-only requests in chat. Use a supported local viewer with no hosted publication or paste step.
- Add `prepare_diwan.py` to create private, preloaded copies of Firas F. Khabour's Diwan. Preserve text, tashkeel, review status and saved browser edits. Keep the poem visible with a warning when storage is unavailable.
- Let the local bridge serve a prepared page. Keep its existing agent request/response workflow.
- Make builder help safe and add launch, storage, host and first-request evaluation coverage. This release does not implement a ChatGPT extension or automatic AI-button connection.
- Require compact metrical explanations to connect a complete hemistich's actual pronounced groups to syllables and feet, rather than listing only the meter's foot names.

## 0.1.0, repository distribution

- Package the shared Arabic poetry skill for Claude and ChatGPT/Codex.
- Add repository-backed marketplaces, installation prompts and update instructions.
- Preserve Firas F. Khabour's scanner, Diwan workbench, exporters and credit.

This version is distributed from `main` without a release tag. See [installation and updates](INSTALL.md) for supported routes.

# Safe updates in an open Diwan

Candidate version: 0.3.1, unreleased. Runtime source: `30cd2962f497a3bc54e81a8cc7dc793d9156ff28`. All 66 skill-file digests match the final evaluated package in [combined.package-hashes.json](combined.package-hashes.json).

The shared-file editor follows compatible versions already installed by its plugin manager. A supervised worker handoff preserves the loopback address, document identity, revision history and selected client. The browser reloads only after editing ends and the latest save is acknowledged. A draft, save failure or conflict keeps the update pending; the updater never saves or discards a draft to proceed.

## Runtime checks

The frozen [runtime scenarios](../../diwan-runtime-updates.json) are covered by 15 Python runtime tests and the production-page/transport JavaScript tests. Cases include installed-only detection, incompatible protocols, foreign package paths, standalone skill use, Claude/Codex/manual selections, pending model requests, replaced documents, partial startup output, incomplete packages, failed startup, crashes after readiness, rollback followed by success, registry changes during handoff, cumulative failed-version blocking, shutdown during startup, and overlapping document saves.

The server waits for active document writes before accepting a handoff and rejects later writes while restarting. The browser retains those drafts and their recovery controls. A replacement that fails falls back to the working package; each failed root remains blocked for the supervisor session.

## Real browser

[live-browser.json](live-browser.json) records a disposable shared poem in the Codex in-app browser. All 49 production files in both the original supervisor and the replacement workers match the accepted source. The version numbers 0.3.2 and 0.3.3 are fixture-only installation declarations, not published releases.

1. Typed an unsaved bulk draft and advanced the fixture installation to 0.3.2. The pending-update notice appeared while the exact textarea text remained visible and the saved poem stayed at revision 1.
2. Saved the draft. The editor updated and reloaded automatically at the same address, retaining its exact text at revision 2. No extra poem revision was created by the update.
3. Opened a clean second tab, started a different unsaved draft in the first tab, and made a conditional agent save creating revision 3. Installed fixture 0.3.3. The clean tab updated, while the first tab retained its unsaved text.
4. Tried saving the stale draft. The visible conflict retained the browser draft and download/recovery controls; the canonical file still contained the agent's revision 3.

Screenshots and raw browser state stay outside Git; their execution paths and hashes are recorded. Session tokens are not published. The runtime browser fixtures use manual mode and make no model requests. Provider selection is exercised separately through fixture executables and real plugin-manager installation tests.

## Package and behavior verification

- 105 Python unit tests pass: 85 skill tests, 4 root package/version tests and 16 evidence/launch tests.
- 24 scanner fixtures and Python/JavaScript parity pass. Workbench state, host, file, shared-page and update suites pass.
- Skills reference validation, Claude plugin validation, all four JSON manifests, synchronized version declarations and whitespace checks pass.
- Real isolated Claude and Codex Git installation, update, repeated update, discovery/inventory and exact skill-byte checks pass. Both clients' installed updates are detected by the runtime resolver. See [lifecycle.json](lifecycle.json).
- All 31 fresh agent cases pass semantic review against unchanged criteria: 8 poetry, 9 opening triggers, 4 explicit launches, 4 pronoun readings and 6 conditional CLI workflows. Actual responses, commands, states and artifact evidence are recorded. The discovery case's initial unavailable `python` command is retained; the agent recovered with `python3` and inspected the real help/contract.
- `check_results.py` validates the current package and all 32 response records across the four historical/current poetry conditions. The three historical baseline conditions are reused unchanged, not rerun.

The poetry entrypoint, craft/prosody rules, scanner, meter tables, exporter core, fonts and Firas F. Khabour's attribution are preserved. The update change does not alter the poetry criteria. Internal code-review notes remain outside the repository; accepted review findings have regression tests.

## Limits

These are diagnostic samples with lead semantic grading and the condition known, not a literary-quality or general reliability benchmark. Browser evidence covers a local shared-file editor, not hosted account synchronization or a ChatGPT extension. Native client tests cover explicit installation/update commands, not background download timers.

Automatic handoff requires compatible updates in the same supported versioned cache, including user-scope Claude Code and Codex installations. The editor does not fetch Git commits or install releases. Older running sessions need one safe reopen after installing this mechanism. Standalone/account-only/ZIP installs and incompatible runtime, launcher or document protocols require reopening. The supervisor stays alive for the session; a release that needs different running launcher behavior must use a new protocol.

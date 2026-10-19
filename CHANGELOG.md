# Changelog

## 0.1.2, preloaded local Diwan, unreleased

- Open an explicitly requested editor with the current poem in the first turn, using a supported local viewer and no hosted publication.
- Add `prepare_diwan.py` to create private, preloaded copies of Firas F. Khabour's Diwan. Preserve text, tashkeel, review status and saved browser edits. Keep the poem visible with a warning when storage is unavailable.
- Let the local bridge serve a prepared page. Keep its existing agent request/response workflow.
- Make builder help safe and add launch, storage, host and first-request evaluation coverage. This release does not implement a ChatGPT extension or automatic AI-button connection.
- Require compact metrical explanations to connect a complete hemistich's actual pronounced groups to syllables and feet, rather than listing only the meter's foot names.

## 0.1.0, repository distribution

- Package the shared Arabic poetry skill for Claude and ChatGPT/Codex.
- Add repository-backed marketplaces, installation prompts and update instructions.
- Preserve Firas F. Khabour's scanner, Diwan workbench, exporters and credit.

This version is distributed from `main` without a release tag. See [installation and updates](INSTALL.md) for supported routes.

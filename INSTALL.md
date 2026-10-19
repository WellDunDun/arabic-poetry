# Install Arabic Poetry

For an agent handling a persistent installation request. Install the skills for the app the user is using, then help them try a poem. To use the skill in the current conversation without installing it, follow the [README quickstart](README.md#quickstart). The [Skills CLI `use` command](https://github.com/vercel-labs/skills#use-a-skill-without-installing) provides temporary supporting files and instructions for the current agent; permanent installation is separate.

Source: https://github.com/WellDunDun/arabic-poetry

## ChatGPT and Codex plugin preview

The root `plugin.json` packages the existing skill for compatible ChatGPT and Codex plugin hosts. `.agents/plugins/marketplace.json` provides a local marketplace pointing at this checkout. The Claude manifest remains available for compatible hosts. There is one skill directory, with the same scanner, references and Firas's Diwan assets in every route.

This is a local plugin preview, not a listing in the public Plugins Directory. Do not claim installation or ChatGPT support from downloaded files alone. Verify the installed skill in the actual host and start a new chat if required.

In a supported ChatGPT desktop environment, open or select this repository and install **Arabic Poetry** from its local marketplace in **Plugins**. If the repository source does not appear, ask the local agent to register this checkout through the host's supported marketplace installer. Web and mobile users should not be instructed to run local shell commands; public directory distribution is separate.

With a Codex CLI that supports `codex plugin`, register a checkout containing the root manifest and marketplace, then install:

```sh
codex plugin marketplace add /absolute/path/to/arabic-poetry
codex plugin add arabic-poetry@arabic-poetry-local
```

Reuse an existing working installation and preserve unrelated marketplace entries. After installation, start a new chat, select the skill with `@` in ChatGPT or `$arabic-poetry` in Codex, and try a supplied poem. Check Python execution before claiming a scanner run. If no execution capability is available, use the skill's documented manual-analysis limits. Diwan uses the local bridge where the agent shares the poem workspace, or the manual JSON exchange elsewhere. This package includes no remote MCP server or embedded ChatGPT Diwan adapter.

Packaging and distribution follow [OpenAI's plugin guide](https://developers.openai.com/plugins/build/plugins); see [supported plugin surfaces](https://learn.chatgpt.com/docs/plugins) and [skill invocation](https://learn.chatgpt.com/docs/skills-and-plugins). Native ChatGPT installation and UI behavior still require validation in the user's target environment.

## Install for the current agent

1. Read the source repository's default branch. The skill directories served by that version are listed in [the package manifest](.claude-plugin/plugin.json). Install each listed directory in full, including references, scripts and assets. An older published version may list two skills; the combined version lists one.
2. Check whether those skills are already installed in this agent. Reuse a working installation; preserve local modifications rather than replacing them silently.
3. Use the agent's supported installer. In Codex, use the built-in `$skill-installer` when available, specifying `WellDunDun/arabic-poetry` and the skill paths from the manifest. [OpenAI's instructions](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) support installation from other repositories.
4. If no suitable native installer is available and Node.js/npm is installed, use the [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill). Target this agent and user-level installation. For Codex, the command is:

   ```sh
   npx --yes skills@latest add WellDunDun/arabic-poetry --global --agent codex --skill '*' --yes
   ```

   For another supported agent, replace `codex` with its documented CLI identifier, such as `claude-code`. Keep `--skill '*'` quoted. Do not use `--all`, which also targets other agents. If the user explicitly requested project-only installation, omit `--global` and run from that project.

These routes install Agent Skills separately from the native plugin preview above. Supported local hosts can use this repository's marketplace; the package is not listed in the universal public directory. If the current app cannot install local skills or plugins, explain the blocker and its supported alternative instead of claiming success.

## Confirm and start

- Verify the installed folders and the current agent's skill discovery. If the app needs a reload or a new chat, give that one next step. Downloaded files alone do not establish activation.
- If Python is available, run the installed scanner's `--help` to confirm it starts. Do not require editor, Word/PDF or hosted-service setup to begin writing or discussing poetry. Consult the installed workflow references when those features are requested.
- Tell the user what is ready, then ask them to paste a poem or describe one they would like to write. Keep the explanation in their language.

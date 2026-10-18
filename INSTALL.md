# Install Arabic Poetry

For the agent receiving the README's installation request. Install the skills for the app the user is using, then help them try a poem.

Source: https://github.com/WellDunDun/arabic-poetry

## Install for the current agent

1. Read the source repository's default branch. The skill directories served by that version are listed in [the package manifest](.claude-plugin/plugin.json). Install each listed directory in full, including references, scripts and assets. An older published version may list two skills; the combined version lists one.
2. Check whether those skills are already installed in this agent. Reuse a working installation; preserve local modifications rather than replacing them silently.
3. Use the agent's supported installer. In Codex, use the built-in `$skill-installer` when available, specifying `WellDunDun/arabic-poetry` and the skill paths from the manifest. [OpenAI's instructions](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) support installation from other repositories.
4. If no suitable native installer is available and Node.js/npm is installed, use the [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill). Target this agent and user-level installation. For Codex, the command is:

   ```sh
   npx --yes skills@latest add WellDunDun/arabic-poetry --global --agent codex --skill '*' --yes
   ```

   For another supported agent, replace `codex` with its documented CLI identifier, such as `claude-code`. Keep `--skill '*'` quoted. Do not use `--all`, which also targets other agents. If the user explicitly requested project-only installation, omit `--global` and run from that project.

These routes install Agent Skills. The Claude-style manifest does not establish a native plugin installation route for every app, and this repository is not claimed to be listed in a plugin marketplace. If the current app cannot install local skills, explain the blocker and its supported alternative instead of claiming success.

## Confirm and start

- Verify the installed folders and the current agent's skill discovery. If the app needs a reload or a new chat, give that one next step. Downloaded files alone do not establish activation.
- If Python is available, run the installed scanner's `--help` to confirm it starts. Do not require editor, Word/PDF or hosted-service setup to begin writing or discussing poetry. Consult the installed workflow references when those features are requested.
- Tell the user what is ready, then ask them to paste a poem or describe one they would like to write. Keep the explanation in their language.

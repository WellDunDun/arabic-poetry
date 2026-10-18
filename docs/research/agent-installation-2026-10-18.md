# Agent-assisted use and installation prompts

Researched 2026-10-18. Primary-source documentation and package inspection; no user-level installations were performed.

## Published patterns

| Source | What it publishes | What we adopt |
| --- | --- | --- |
| [Superpowers installation](https://github.com/obra/superpowers#installation) | An OpenCode prompt beginning "Fetch and follow instructions from" and linking to its raw installation document. Other hosts get their own installation routes. | Keep the persistent installation route in a maintained guide. |
| [Dailybot installation](https://www.dailybot.com/skills/agent-skill/) | A short natural-language instruction to install a linked skill and perform a first task, alongside manual CLI setup. | Keep installation approachable and end with a useful first action. |
| [OpenAI skill installation](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) | Codex's built-in `$skill-installer` can download skills from other repositories. It also documents discovery/restart behavior. | Use Codex's installer when available; verify discovery separately from downloading. |
| [Vercel Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) | Compact commands with explicit agent, scope and skill options. `--global` selects user scope, `--agent` chooses agents, `--skill '*'` selects all skills and `--yes` skips interactive prompts. `--all` targets every agent as well as every skill. | Keep permanent installation scoped to the current agent; use the separate `use` command for the current conversation. |
| [Anthropic Skills](https://github.com/anthropics/skills#try-in-claude-code-claudeai-and-the-api) | Separate Claude Code marketplace installation, Claude.ai guidance and API guidance. | Do not describe one host's plugin metadata as universal plugin support. |
| [AGY agent plugins](https://github.com/iicmaster/antigravity-plugins#ai-assisted-installation) | Different assisted-installation prompts for Claude and Codex, with host-specific flows and verification. | Put platform differences in the installation document. |
| [Remy installation](https://github.com/dirkpaessler/Remy#1-install-remy) | Tells users where to paste a short setup request in Claude Code and gives human restart steps separately. | Say which capabilities an installing agent needs; do not promise installation in text-only chat. |

## Decision for Arabic Poetry

The README now follows the user's supplied `grill-me` example. Both language versions ask the existing agent to run `npx skills use "https://github.com/WellDunDun/arabic-poetry" --skill "arabic-poetry"`, read its complete output, follow the generated instructions and resolve relative paths from the supplied supporting-files directory.

The [Skills CLI's use documentation](https://github.com/vercel-labs/skills#use-a-skill-without-installing) describes this as use without installation: it downloads the selected package into a temporary directory and prints a generated prompt. We omit `--agent`, which would start a separate supported agent. The README labels this as current-conversation use and keeps permanent installation as a separate option through `skills add` and `INSTALL.md`. This implements the user's requested wording; it is not a measured prompt-success claim.

The guide specifies:

- Install all complete skill folders declared by the published package. This covers the current two-skill release and the proposed combined release without hardcoding a stale layout in the user prompt.
- Prefer the current agent's supported installer; Codex may expose `$skill-installer`.
- Use the documented Skills CLI fallback only when Node.js/npm exists, targeting one agent and user scope. Do not substitute `--all`.
- Check files, skill discovery and, when Python exists, scanner startup. Keep optional editor/export setup out of basic installation.
- Finish by helping the user start with a poem in their language.

The repository's `.claude-plugin/plugin.json` lists served skill directories. It does not establish a native Codex plugin or a listing in any marketplace. The documented fallback installs Agent Skills, not every possible native plugin feature.

## Verification and release boundary

The actual remote command was tested with Skills CLI 1.7.2, using a temporary npm cache and redirecting stdout to a temporary file before reading it in full. It exited successfully, selected `arabic-poetry`, emitted the complete `SKILL.md` and supplied a temporary supporting-files directory. The directory contained `SKILL.md` and `references/CRAFT.md`, confirming the relative-reference instruction against an actual result. No `--agent` launch or persistent skill installation was performed.

Documentation checks verify equivalent command tokens in both language prompts, local Markdown links and whitespace. The existing frozen evaluation-integrity check still matches the skill package because only root documentation changed; no poetry trial was relabelled or rerun for this documentation edit.

The public command resolves the repository's default branch. It works with the published `arabic-poetry` skill without depending on the unmerged `INSTALL.md` URL. It does not load unmerged consolidation or portable-editor work; those remain in PRs #2 and #3 until reviewed and merged.

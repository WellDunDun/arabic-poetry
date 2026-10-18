# Agent-assisted installation prompts

Researched 2026-10-18. Primary-source documentation and package inspection; no user-level installations were performed.

## Published patterns

| Source | What it publishes | What we adopt |
| --- | --- | --- |
| [Superpowers installation](https://github.com/obra/superpowers#installation) | An OpenCode prompt beginning "Fetch and follow instructions from" and linking to its raw installation document. Other hosts get their own installation routes. | A one-sentence user prompt pointing at maintained instructions. |
| [Dailybot installation](https://www.dailybot.com/skills/agent-skill/) | A short natural-language instruction to install a linked skill and perform a first task, alongside manual CLI setup. | Keep installation approachable and end with a useful first action. |
| [OpenAI skill installation](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use) | Codex's built-in `$skill-installer` can download skills from other repositories. It also documents discovery/restart behavior. | Use Codex's installer when available; verify discovery separately from downloading. |
| [Vercel Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) | Compact commands with explicit agent, scope and skill options. `--global` selects user scope, `--agent` chooses agents, `--skill '*'` selects all skills and `--yes` skips interactive prompts. `--all` targets every agent as well as every skill. | Document a concrete fallback that installs only for the current agent. |
| [Anthropic Skills](https://github.com/anthropics/skills#try-in-claude-code-claudeai-and-the-api) | Separate Claude Code marketplace installation, Claude.ai guidance and API guidance. | Do not describe one host's plugin metadata as universal plugin support. |
| [AGY agent plugins](https://github.com/iicmaster/antigravity-plugins#ai-assisted-installation) | Different assisted-installation prompts for Claude and Codex, with host-specific flows and verification. | Put platform differences in the installation document. |
| [Remy installation](https://github.com/dirkpaessler/Remy#1-install-remy) | Tells users where to paste a short setup request in Claude Code and gives human restart steps separately. | Say which capabilities an installing agent needs; do not promise installation in text-only chat. |

## Decision for Arabic Poetry

The previous prompts repeated installation policy, environment detection, preservation, verification and reporting instructions in both languages. That made the copyable text long while still leaving the agent to infer installation mechanics.

The README now uses one equivalent sentence in each language. Both link to `INSTALL.md`, which owns the actionable setup routes. This is an inference from the examples above, not evidence that one wording has a measured success rate.

The guide specifies:

- Install all complete skill folders declared by the published package. This covers the current two-skill release and the proposed combined release without hardcoding a stale layout in the user prompt.
- Prefer the current agent's supported installer; Codex may expose `$skill-installer`.
- Use the documented Skills CLI fallback only when Node.js/npm exists, targeting one agent and user scope. Do not substitute `--all`.
- Check files, skill discovery and, when Python exists, scanner startup. Keep optional editor/export setup out of basic installation.
- Finish by helping the user start with a poem in their language.

The repository's `.claude-plugin/plugin.json` lists served skill directories. It does not establish a native Codex plugin or a listing in any marketplace. The documented fallback installs Agent Skills, not every possible native plugin feature.

## Verification and release boundary

Documentation checks cover equivalent short prompts, the target repository/file path, local Markdown links, the manifest's declared skill folders, supported CLI options against first-party documentation, and whitespace. No automatic installation was run against a user's global skill directory, and no cross-agent activation test is claimed.

The public prompt targets `main/INSTALL.md`. That file is introduced by this unmerged PR, so the prompt is the intended published onboarding and will only work at that URL after merge. A reviewer can inspect [the installation guide on the review branch](https://github.com/WellDunDun/arabic-poetry/blob/codex/portable-diwan/INSTALL.md). Installing from the current default branch still installs only that branch's published skills; it does not include unmerged editor changes.

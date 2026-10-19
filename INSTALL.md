# Install and update Arabic Poetry

Prefer a repository-backed plugin. It keeps the installed package connected to future releases. Use a standalone skill or ZIP only when the current host cannot install from a repository marketplace. The source is [WellDunDun/arabic-poetry](https://github.com/WellDunDun/arabic-poetry), and the marketplace is `arabic-poetry-plugins`.

The default commands below follow the reviewed `main` branch. The plugin is available from this repository and has not been listed in either public plugin directory.

## Claude web and Desktop

1. Open **Customize > Plugins > Add > Add marketplace** and choose the repository option.
2. Enter `https://github.com/WellDunDun/arabic-poetry.git`, then add **Arabic Poetry** from that marketplace. Use a branch that receives future releases rather than a fixed commit if you want updates.
3. Verify that the plugin is enabled and exposes `arabic-poetry` in the skills menu. Try a supplied poem. A downloaded repository alone does not establish activation.
4. Check the marketplace's available refresh/update controls. For organization-managed distribution, use GitHub/GitLab sync with **Sync automatically** enabled, rather than manually uploading ZIPs. Claude's organization sync has repository-visibility and admin-access requirements; follow the [organization guide](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization) for an approved private/internal mirror when required.

Plugins are available in Claude web chat and Desktop on supported paid plans. Account and organization policies can restrict installation. See [Claude's plugin instructions](https://support.claude.com/en/articles/13837440-use-plugins-in-claude). Browser/account sync has not been verified by the local CLI lifecycle test.

## Claude Code

Register the Git source once, then install the plugin:

```sh
claude plugin marketplace add https://github.com/WellDunDun/arabic-poetry.git
claude plugin install arabic-poetry@arabic-poetry-plugins
claude plugin list
claude plugin details arabic-poetry
```

Avoid a local filesystem path for the default install; that tracks a local copy rather than fetching future Git releases.

In a Claude Code session, open `/plugin`, choose **Marketplaces > arabic-poetry-plugins > Enable auto-update**. Third-party marketplaces have auto-update off by default. Updates apply at the next session; use `/reload-plugins` when the host offers it. Select the skill as `/arabic-poetry:arabic-poetry`.

To update explicitly:

```sh
claude plugin marketplace update arabic-poetry-plugins
claude plugin update arabic-poetry@arabic-poetry-plugins
claude plugin list
```

Confirm the installed version changed, then start a new session. Refreshing a marketplace listing alone is not proof that the installed plugin updated. See [Claude Code updates](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated).

## ChatGPT in the browser or desktop app

For a workspace with GitHub marketplace import, a workspace admin can connect the repository:

1. Open **Admin > Plugins > Add > Import marketplace**.
2. Set **Source** to `https://github.com/WellDunDun/arabic-poetry`, leave **Path** empty, and select `main` to follow reviewed releases. A fixed commit does not follow later releases.
3. Complete the host's normal GitHub authorization, inspect the import result, and make **Arabic Poetry** available to the intended users.
4. Install it from the workspace's **Plugins** list, start a new chat, and choose its poetry skill with `@`. Verify discovery and try a poem in that environment.

New Git-backed workspace marketplaces have daily sync enabled. For an immediate refresh, use **Admin > Plugins > Marketplaces > Sync now**, inspect the sync report, then verify the installed skill in a new chat. This is the [workspace import and update route](https://learn.chatgpt.com/docs/enterprise/plugin-management); it is not a promise that every personal account can import a repository. If the account lacks these admin controls, explain the limitation. Do not ask a user to send passwords or turn a workspace-wide import into an unannounced personal install.

Public directory publication is separate and has not been done. The package contains no MCP server or desktop-only hooks. Local scanner/export scripts still require an execution environment; an enabled skill does not grant arbitrary local file access to browser chat. See [supported plugin environments](https://learn.chatgpt.com/docs/plugins).

## Codex with a Git marketplace

```sh
codex plugin marketplace add https://github.com/WellDunDun/arabic-poetry.git --ref main
codex plugin add arabic-poetry@arabic-poetry-plugins
codex plugin list --json
```

In compatible desktop hosts, use the registered repository marketplace in **Plugins**. Select the installed skill from the skill picker. Native plugins may namespace it as `$arabic-poetry:arabic-poetry`; use the exact name shown by the host.

To refresh and install the current version explicitly:

```sh
codex plugin marketplace upgrade arabic-poetry-plugins
codex plugin add arabic-poetry@arabic-poetry-plugins
codex plugin list --json
```

Start a new chat and verify the plugin's skill path/version. Do not infer updated installed files from catalog metadata alone. The local CLI test covers these explicit commands, not a background update timer. Git marketplace refresh and ChatGPT workspace daily sync are different mechanisms. See [OpenAI's marketplace packaging guide](https://developers.openai.com/plugins/build/plugins#marketplace-metadata).

## Versions and releases

The plugin uses `MAJOR.MINOR.PATCH` versions. Read [CHANGELOG.md](CHANGELOG.md) for changes; the installed version is shown by each host's plugin manager or the list commands above. A versioned release identifies the instructions, references, scanner, editor and exporters that travel together.

The default Git source follows reviewed `main` commits. Released versions receive a `vMAJOR.MINOR.PATCH` tag for reproducibility. Selecting a fixed release tag or commit is an opt-out from newer releases, not the default update route. Maintainer release checks and the synchronized version command are in [AGENTS.md](AGENTS.md#plugin-releases).

Prefer an update over uninstall/reinstall. Preserve user-authored local modifications and poem workspaces. An accepted update does not synchronize browser-stored poems with an agent or another browser. Diwan still uses its local bridge or manual JSON exchange as described in [DIWAN.md](skills/arabic-poetry/references/DIWAN.md).

## Fallback for other agents

If plugin installation is unavailable, explain the missing capability first, then install the complete `skills/arabic-poetry` directory using the agent's supported skill installer. Preserve existing modifications. In Codex, `$skill-installer` is one standalone route. If an appropriate native installer is absent, the [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) can target the current agent only:

```sh
npx --yes skills@latest add WellDunDun/arabic-poetry --global --agent codex --skill arabic-poetry --yes
```

Replace `codex` with the current supported agent's identifier when appropriate. Omit `--global` only for a requested project-only install. This installs a standalone skill and is not subscribed to our plugin marketplace updates. The [README's current-chat prompt](README.md#fallback-use-the-skill-in-your-current-chat) is temporary use, not a persistent plugin installation.

## Confirm and try a poem

- Verify the installed plugin's version and skill discovery. If required, give the user one reload/new-chat step. Files on disk alone do not prove activation.
- When execution is available, run the installed scanner's `--help` and then analyze a supplied line. Otherwise follow the skill's explicit manual-analysis limits. Do not invent a scanner run.
- Keep ordinary writing and interpretation in chat. Editor, Word/PDF and hosted services are optional. Tell the user which capabilities are ready and ask them to paste a poem or describe one they want to write.

راجع [بداية الاستخدام بالعربية](README.md#install-the-plugin-recommended) لنسخ طلب التثبيت. الإضافات المرتبطة بالمستودع هي المسار المفضّل؛ ويعتمد وصول التحديث على إعدادات البيئة. يغطّي اختبار العميل المحلي التثبيت والتحديث بأوامر Claude Code وCodex، ولا يثبت وحده نجاح مزامنة حساب Claude أو مساحة عمل ChatGPT في المتصفح.

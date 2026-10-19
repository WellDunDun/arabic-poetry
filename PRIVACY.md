# Privacy

Last updated: 19 October 2026.

Arabic Poetry is a package of agent instructions, reference files, and optional local tools. Daniel Petro created the original skill and repository; Firas F. Khabour contributed the scanner, Diwan and exporters. The package does not include a maintainer-operated server, account system, analytics service, advertising, or telemetry. It does not request passwords or API keys.

## Poems and conversations

The agent receives the poems, edits, vocalization choices, and other text you put in its conversation. The agent platform processes and retains that conversation under its own settings and policies. Installing this package does not give its maintainers access to your conversations. We do not operate a separate store of your poems and cannot delete copies held by your agent platform. Use that platform's conversation and data controls.

The Python meter scanner processes text in its execution environment without sending it to an external analyzer. Input files, reports, and exports remain wherever you or your agent save them. In a cloud chat, that location may be the platform's execution environment rather than your computer.

## Optional Diwan editor

In an ordinary browser, Diwan stores poems and review choices in that browser's local storage until you delete them or clear site data. This does not synchronize poems with another browser or conversation. Export work you want to keep before clearing storage.

Opening Diwan loads fonts from Google Fonts and the JSZip library from Cloudflare's CDN. Those providers receive normal web request information, such as an IP address and browser headers. The ordinary editor does not send poem text in these resource requests. Choosing a link to the external Kalimmat rhyme site sends the selected rhyme ending in that site's URL; use such links only when you want to visit that service.

Without a connected host, AI buttons use a manual copy/paste exchange. You choose what text to send to your agent. An optional host adapter may send a request to its configured model or save poems to its configured database. That host's permissions, privacy rules, and retention apply. The package does not configure a cloud model connection or database for you.

The optional local bridge writes poem excerpts, prompts, and answers under `.diwan/` in the workspace you select. Expiration or cancellation stops request processing; it does not erase those files. Delete them when no longer needed and keep them out of public repositories. The bridge binds to localhost and does not run a model itself.

## Support, retention, and control

If you open a public GitHub issue, the maintainers and other visitors can read it. GitHub controls storage and visibility under its own policies. Do not post unpublished poems, private files, credentials, or personal information. Use a short example you are comfortable making public. Public issues are not confidential support messages.

The package has no maintainer-operated data store or retention schedule. Browser data, local files, host storage, conversations, and GitHub issues have separate lifetimes and deletion controls described above. The maintainers can respond about repository content but cannot remove data held by your platform, browser, host provider, or other third-party service.

For privacy questions, use the [support instructions](SUPPORT.md) without including private material. We will update this notice when the package's data practices change.

# Single Arabic poetry skill

Proposal against `3286f489881b9fbc5bb2fc2bca7dd064835b1a4c`. Review through a pull request before merging.

## Resulting package

Serve one `arabic-poetry` skill. Retain literary workflows, Firas F. Khabour's scanner and Diwan workbench, both checker types, all existing test fixtures, export code and font licenses in that package. Git history retains the original contribution commits; README and workbench credits remain explicit.

The entrypoint routes writing/critique to `CRAFT.md`, interpretation to `READING.md`, metrical work to `PROSODY.md` plus `SCANNER.md`, and optional editing/export to `DIWAN.md`. Conditional details no longer require loading a second skill's long entrypoint. The original arithmetic checker remains distinct from meter detection.

Move the former `skills/arabic-prosody/` implementation, assets, references and tests under `skills/arabic-poetry/`. Rename its lowercase `sources.md` to `SCANNER-SOURCES.md` to avoid a collision with the existing `SOURCES.md` on case-insensitive filesystems. Remove its served manifest entry and describe the installation migration in README. Historical research remains, with its live relative source link repaired.

## Reconciled behavior

| Concern | Prior instruction overlap | Combined policy |
| --- | --- | --- |
| Tashkeel | General inferred-reading analysis versus mandatory approval before scanning | Preliminary analysis can disclose assumptions. Pause for an explicitly requested review or a consequential unresolved ambiguity; preserve supplied marks and intended meaning. |
| Already confirmed/generated text | Broad approval rule could add a routine turn | Verify confirmed or newly composed readings without asking for routine vowel approval. |
| Tool evidence | Optional arithmetic checker versus mandatory scanner verdicts | Run the bundled scanner for supported metrical claims when execution is available. Inspect pronunciation and licensed forms; manual fallback is disclosed and unresolved claims remain provisional. |
| Editor | Chat-first workflows versus mandatory workbench for editing | Diwan is optional and used when requested or helpful to the task. Chat-only requests stay in chat. |
| Hosted capabilities | Artifact/database/sampling/download assumptions | Use only actual exposed capabilities. A local HTML file or browser store does not establish host synchronization or future-chat access. |
| Form classification | General prose-poetry coverage versus an older supporting reference suggesting prose from failed detection | Respect intended form; unsupported or failed meter matches do not establish prose poetry. |
| Validity | A permissible local foot change versus a whole-line verdict | Verify whole sequences, position-specific rules and endings, then grammar, rhyme and meaning. Alignment is evidence, not comprehensive certification. |

Keep the two source traditions visible through craft sources and scanner-specific coverage references. This packaging change does not establish exhaustive correctness of the rule tables, improve the engine's measured accuracy, or prove literary quality.

## Before/after evidence

Freeze requests and semantic criteria before modifying the skills. Compare original-only, prosody-only, both-current and combined installations under the same restricted local tool capabilities, with independent execution agents and recorded responses/commands. Preserve the original packages and hashes outside the candidate tree.

The comparison and its limitations live in [the evaluation report](../../evals/results/2026-10-16/report.md). Raw response records, package hashes, command outputs, reviewer criterion judgments and software checks accompany it. The integrity checker validates completeness/provenance, not semantic quality. It is a small single-run comparison with shared context inside each condition; repeat with isolated per-case sessions, more cases and expert Arabic review before making general claims.

Scanner/exporter implementation and shipped browser/font assets are compared byte-for-byte against the base, then the existing tests run at their relocated paths. Rebuilding the workbench must reproduce the original bundle. CLI Word output is checked structurally for ZIP/XML integrity, Arabic content and RTL markup. Host integrations and PDF remain outside this consolidation trial.

# Scanner and optional tools

Tools help check a proposed reading; they do not determine literary value. None of the external tools or models below is required by this skill. Do not install a stack or submit a user's unpublished poem to a service simply because it is linked here.

## Use the bundled scanner for supported analysis

The local [scan.py](../scripts/scan.py) takes vocalized verse, derives implemented pronunciation alternatives and ranks metrical forms. It supplies reproducible alignment evidence for identification and repair. Read [SCANNER.md](SCANNER.md) for input, commands, confirmation policy and interpretation, and [SCANNER-SOURCES.md](SCANNER-SOURCES.md) for coverage limits. It is the integrated scanner contributed by Firas F. Khabour; it is not an external service or another skill to install.

Use it when making supported metrical claims and execution is available. Inspect its pronunciation, whole-input coverage and rule permissions. It does not replace literary judgment or makes a failed scan proof of prose poetry. Optional [Diwan editing/export](DIWAN.md) uses the same engine family.

## Audit analyzer evidence

Keep the original, inferred vocalization, tool-normalized text, عروض transcription, syllable pattern, and aligned feet distinct. Inspect what a tool changed, which metrical variants it covers, and whether it consumes the whole input. A classifier's highest-scoring meter is a hypothesis; a nearest-pattern score is not an exact licensed fit.

- [Aruudy](https://github.com/linuxscout/aruudy) returns normalized text, عروض writing, sound patterns, and feet. Its README requires full vocalization and describes some inferred missing marks. The inspected [normalizer](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/prosody.py) inserts inferred marks; the inspected [matcher](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/meter.py) returns the first successful candidate, and `BahrForm.validate` returns parts without an explicit remaining-sequence check. This is a static source finding, not a reproduced runtime benchmark. Check ambiguity and full coverage yourself.
- [Qawafi](https://github.com/ARBML/qawafi) exposes diacritization, meter classification, nearest patterns, rhyme, theme, and era. Its example uses `override_tashkeel=True`. Preserve supplied vocalization unless replacement is intended; label era/theme predictions as model outputs rather than verified attribution.
- [PyArud](https://github.com/cnemri/pyarud) and [arud-skill](https://github.com/cnemri/arud-skill) offer an Arabic-specific tool workflow. Inspect the actual version and output before relying on it. Source inspection found inconsistent pattern examples in arud-skill's reference material; its confidence or deterministic implementation claim does not certify those examples or its full analysis.

External tools use their own symbols for moving and still letters or syllables. Convert any such pattern to ب − = before comparing it with the scanner, and say that you converted it. Investigate conflicting readings instead of averaging conflicting meter names.

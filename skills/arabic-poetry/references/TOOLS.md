# Optional tools and arithmetic checks

Tools help check a proposed reading; they do not determine literary value. None of the external tools or models below is required by this skill. Do not install a stack or submit a user's unpublished poem to a service simply because it is linked here.

## Audit analyzer evidence

Keep the original, inferred vocalization, tool-normalized text, عروض transcription, symbol string, and aligned feet distinct. Inspect what a tool changed, which metrical variants it covers, and whether it consumes the whole input. A classifier's highest-scoring meter is a hypothesis; a nearest-pattern score is not an exact licensed fit.

- [Aruudy](https://github.com/linuxscout/aruudy) returns normalized text, عروض writing, sound patterns, and feet. Its README requires full vocalization and describes some inferred missing marks. The inspected [normalizer](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/prosody.py) inserts inferred marks; the inspected [matcher](https://github.com/linuxscout/aruudy/blob/master/aruudy/poetry/meter.py) returns the first successful candidate, and `BahrForm.validate` returns parts without an explicit remaining-sequence check. This is a static source finding, not a reproduced runtime benchmark. Check ambiguity and full coverage yourself.
- [Qawafi](https://github.com/ARBML/qawafi) exposes diacritization, meter classification, nearest patterns, rhyme, theme, and era. Its example uses `override_tashkeel=True`. Preserve supplied vocalization unless replacement is intended; label era/theme predictions as model outputs rather than verified attribution.
- [PyArud](https://github.com/cnemri/pyarud) and [arud-skill](https://github.com/cnemri/arud-skill) offer an Arabic-specific tool workflow. Inspect the actual version and output before relying on it. Source inspection found inconsistent binary examples in arud-skill's reference material; its confidence or deterministic implementation claim does not certify those examples or its full analysis.

Do not read `v/c`, `w/s`, syllable `u/-`, and `1/0` interchangeably. Name and convert the tool's notation before comparison. Investigate conflicting readings instead of averaging conflicting meter names.

## Check a displayed scan locally

The bundled [check_scansion.py](../scripts/check_scansion.py) uses Python's standard library. It checks two concrete invariants: the annotated foot texts cover the supplied عروض transcription exactly, and their claimed binary patterns match its moving/still letters. It does **not** derive pronunciation from ordinary spelling, detect a بحر, validate زحافات, or prove that the foot labels are correct.

Supply expanded عروض writing. Mark every consonant with a short vowel or sukun; a bare long vowel is accepted after its corresponding short vowel. Expand shadda, tanwin, madda and unwritten sounds first. Choose الوصل/الوقف and إشباع explicitly. Unsupported or missing marks produce an error rather than a guessed sound.

```json
{
  "arudi": "هَزَجْنَا فِي أَغَانِيكُمْ",
  "feet": [
    {"text": "هَزَجْنَا فِي", "pattern": "1101010", "label": "مفاعيلن"},
    {"text": "أَغَانِيكُمْ", "pattern": "1101010", "label": "مفاعيلن"}
  ]
}
```

```sh
python3 scripts/check_scansion.py /path/to/scan.json
```

Run from the skill directory, or use its absolute script path. Omit the file argument or use `-` to read JSON from stdin. Output is JSON; exit `0` means arithmetic checks passed, exit `1` means an input error or mismatch. Review the `actual`, per-foot rows, and `problems`. Correct the transcription only when the pronunciation justifies it, then rerun after any repair.

Even a passing result can describe the wrong reading or an illegal metrical form. Verify the original-to-transcription step and the meter-specific interpretation separately.

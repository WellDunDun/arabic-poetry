# Prosody and rhyme

Use this procedure for identifying a meter, composing metrical poetry, or repairing a suspected break. Consult the [sources](SOURCES.md) for unfamiliar rules and specific ending forms.

## Keep four layers separate

1. The text as supplied, including diacritics and line breaks.
2. A grammatically and semantically plausible pronunciation. Mark added vocalization as inferred when the user did not supply it.
3. A phonetic عروض transcription and its sound sequence.
4. The proposed feet, their variants, and the verdict.

If a layer changes, recompute the layers that follow. Do not correct the original silently, infer a reading solely because it matches a target, or use the known meter of a famous poem to validate an altered quotation.

When using an analyzer, retain its normalized input and version alongside these layers. Inspect inserted vowels and spelling changes before accepting the scan. Use the integrated [scanner workflow](SCANNER.md) for supported metrical claims when execution is available. The [tool guide](TOOLS.md) distinguishes that scanner, optional external analyzers and the local transcription arithmetic checker.

## Establish the pronounced sequence

الكتابة العروضية represents what is pronounced. It is an analysis notation, not a corrected spelling of the poem.

- Expand a pronounced شدة into a ساكن followed by a متحرك. Represent pronounced تنوين with a final ساكن نون when reading in وصل.
- Account for pronounced long vowels, including letters not shown in ordinary spelling. Omit silent written letters, such as the distinguishing alif in كتبوا.
- Handle همزة الوصل according to position and connected pronunciation. Keep همزة القطع. Account for assimilation in the solar article and pronunciation of the lunar article.
- Apply the actual الوصل or الوقف reading, including case endings, tanwin, and word-final ة. Do not stop after every printed word when scanning a connected phrase.
- Explain any terminal إشباع, هاء الضمير treatment, or poetic license needed for a reading. Do not lengthen arbitrary vowels to fit a template. Use a rule appropriate to this position and tradition.
- For dialectal poetry, establish the spoken wording first. Standard Arabic case endings and spelling normalization can change its rhythm.

Use one notation consistently. A simple character notation is `1` for a متحرك and `0` for a ساكن; these symbols do not mean stressed and unstressed syllables. Long-vowel letters count as ساكن in this notation. Alternatively use explained syllable notation, but never mix the two without converting explicitly.

Keep symbols in code blocks or short code spans so Arabic display order does not reverse the sequence. State that the symbol sequence is read from left to right and the Arabic verse in its normal reading order.

## Match a meter

- Segment the sound sequence into feet. Foot boundaries need not coincide with word boundaries. Preserve the whole sequence with no deleted, inserted, or duplicated sounds.
- Recompute the claimed binary pattern from the displayed transcription and verify that foot texts cover it in order, including trailing sounds. The local checker automates only this arithmetic. A passing string does not establish correct pronunciation, labels, or licensed variants.
- Compare the actual sequence with the applicable metrical form, including its عروض and ضرب. A textbook's theoretical base pattern is a starting point, not a rule that every foot must appear unchanged.
- Distinguish حشو, عروض, and ضرب. Verify each زحاف or علة in that meter and position. A change allowed in one foot or ending does not authorize it everywhere.
- Consider complete and shortened forms where applicable, such as مجزوء، مشطور، منهوك. Do not diagnose a shortened form as broken merely for having fewer feet.
- Check both halves of a supplied بيت and multiple lines of a supplied poem. If a passage fits only partially, identify where the match stops rather than assigning a certain بحر.
- Locate a mismatch in a pronounced phrase and state the assumed target form. A nearest-pattern distance can suggest where to inspect, but cannot distinguish a typo, a different reading, a permitted change, and a genuine break by itself. Recheck the whole line after proposing a phrase repair.
- For تفعيلة, check the recurring rhythmic basis and variants over the actual sequence. Examine connected reading where a line break participates in تدوير. State the analytic convention when the treatment is disputed.
- Distinguish a continuing thought from a foot or word divided by the printed break. State the boundary and chosen الوصل/الوقف treatment; do not apply a blanket incompatibility between تدوير and rhyme. The contemporary [Najjar study](SOURCES.md) offers applications without making every classification universal.

The common sixteen-meter inventory is الطويل، المديد، البسيط، الوافر، الكامل، الهزج، الرجز، الرمل، السريع، المنسرح، الخفيف، المضارع، المقتضب، المجتث، المتقارب، المتدارك. Use a source for the applicable form and variants rather than treating this list as a detector. Do not equate الخبب with every occurrence of المتدارك without explaining the convention used.

For quick checks, these feet have the following moving/still sequences. They are reusable building blocks, not complete meter definitions or universal variant permissions.

| Foot | Sequence, read left to right |
| --- | --- |
| فَعُولُنْ | `11010` |
| مَفَاعِيلُنْ | `1101010` |
| فَاعِلُنْ | `10110` |
| فَاعِلَاتُنْ | `1011010` |
| مُسْتَفْعِلُنْ | `1010110` |
| مُتَفَاعِلُنْ | `1110110` |
| مُفَاعَلَتُنْ | `1101110` |
| مَفْعُولَاتُ | `1010101` |

Identical moving/still strings can conceal different سبب and وتد structures, such as مستفعلن and مستفع لن. Preserve the structural interpretation required by the meter when deciding which alterations are permitted.

## Judge uncertainty

| Evidence | Appropriate conclusion |
| --- | --- |
| All supplied sounds fit a documented form with a plausible reading | Name the meter and show the supporting scan |
| Different plausible vocalizations or short fragments fit different meters | Give candidates and the reading or extra context that distinguishes them |
| Surrounding lines establish a meter but one passage fails | Show the mismatch and assess whether it is a transcription issue, reading issue, or metrical fault |
| No supported fit and little context | Say that the meter is not established; request vocalization or more lines only if needed |

Use qualitative confidence tied to evidence, not invented percentages. Distinguish "this fragment fits" from "the whole poem is regular". A failed scan does not prove قصيدة نثر, and a fitting fragment does not prove that the whole text is a classical poem.

## Rhyme

- Analyze the pronounced ending and compare endings across the poem. Separate **الروي**, the rhyme's anchoring letter, from **القافية**, the fuller ending pattern.
- Under the common Khalilian definition, find the final ساكن and the preceding ساكن and include the متحرك before the latter. Use the applicable pronounced ending, including justified إشباع, when delimiting this span.
- Identify الوصل، الخروج، الردف، التأسيس، الدخيل and relevant movements when present and useful. These terms describe different positions; avoid guessing all of them from a last written character.
- Distinguish قافية مطلقة from مقيدة through the movement or stillness of the الروي. A terminal long vowel may be وصل rather than روي; terminal هاء or ة requires attention to its role and pronunciation.
- Diagnose a named defect, such as إقواء or سناد, only after establishing the rhyme scheme and the exact inconsistent component. For modern forms, changing rhyme may be an intentional design choice.

See the [worked example](EXAMPLES.md) for a complete sound-to-foot alignment and the difference between الروي and terminal إشباع.

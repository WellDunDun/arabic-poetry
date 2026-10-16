# الكتابة العروضية — what is counted

Prosody counts what is **pronounced**, not what is written.

## Written but not pronounced (dropped)
- **همزة الوصل** in mid-line: «وَاسْمَعْ» → وسمع، «فِي الدَّارِ» → فِدْدار. At the start of a hemistich it is pronounced (أَلْ...).
- **لام الشمسية**: «الشَّمْس» → ششمس (the lam disappears, the next letter doubles).
- **الألف الفارقة** after واو الجماعة: «كَتَبُوا» → كتبو.
- **ألف التنوين المنصوب**: «حَبِيبًا» → حبيبن.
- **واو عمرو**، واو «أولئك/أولو/أولي/أولات».
- **حرف المد before a sakin** (التقاء الساكنين): «فِي الْبَيْتِ» → فِلْبيت، «عَلَى الْأَرْضِ» → علَلْأرض.

## Pronounced but not written (added)
- **التنوين** → نون ساكنة: «حَبِيبٌ» → حبيبن.
- **الشدة** → letter twice, first sakin: «أُقَصِّرُ» → أقصْصِر.
- **الألف المحذوفة رسمًا**: هٰذا → هاذا، ذٰلك → ذالك، لٰكن → لاكن، الله → اللاه، الرحمٰن → الرحمان، طٰه.
- **إشباع آخر الشطر** (الإطلاق): a final vowel is lengthened — «منزلِ» → منزلي، «العزائمُ» → العزائمو، «الهوى» stays.
- **إشباع هاء الضمير** after a moving letter: «لَهُ» → لهو، «بِهِ» → بهي (not after a sakin: «مِنْهُ»، «فِيهِ»).
- **إشباع ميم الجمع** optionally: «لَهُمْ» or «لَهُمُو».

## Moving vs still
- حرف عليه حركة أو تنوين (أوله) = متحرك `/`.
- حرف ساكن، حرف مد (ا، و بعد ضم، ي بعد كسر)، نون التنوين، أول المشدد = ساكن `0`.
- The last letter of every hemistich is counted ساكن (sukun or the ishba' letter).
- Two sakins never meet inside a line; if they seem to, re-check the reading (wasl, madd before sakin, etc.).

## Common reading choices that change the weight
| choice | effect |
|---|---|
| قطع همزة الوصل للضرورة | adds a moving letter |
| تسهيل/حذف الهمزة («شيءٍ» → «شيٍ» rare) | removes a letter |
| صرف الممنوع من الصرف للضرورة | adds tanwin (نون ساكنة) |
| إسكان المتحرك للضرورة | changes / to 0 |
| «أنا» بإثبات الألف أو حذفها لفظًا | 0 or nothing |
| الإشباع / عدمه في هاء الضمير وميم الجمع | adds or removes a sakin |

The scanner tries the optional ones automatically (and reports which it
used); forced ones (ضرورات) are for you to propose when fixing, see `fixing.md`.

# Repairing a broken line (تقويم الوزن)

Goal: restore the meter with the **smallest change to the poet's meaning, words
and music**. Always verify candidates with `scan.py verify`.

## 1. Locate
From the report: which foot is ✗, what was found vs what is allowed there, and
whether the hemistich is too long or too short overall. A 💡 line means one word
is surplus — often a filler conjunction or particle.

## 2. Choose a technique (least invasive first)

| problem | techniques |
|---|---|
| one extra moving letter | drop a و/ف/ثم; a shorter synonym (يَقُولُ ب − ب → قَالَ − ب); «لكنَّ» → «لكنْ» |
| one extra sakin | put an indefinite word in إضافة (drops its tanwin)، حذف ألف «أنا» لفظًا، a synonym without a long vowel |
| one missing moving letter | add و/ف/لـ/بـ or vocative يا; a longer synonym |
| one missing sakin | make a word indefinite (adds tanwin), lengthen هاء الضمير after a moving letter (لَهُ → لَهُو)، a form with a long vowel (كَتَبَ → كاتِب) |
| moving where sakin needed (or reverse) | reorder words; a synonym of another pattern (فَعَلٌ ↔ فَعْلٌ); a different case/mood if grammar allows |
| wrong darb form | rework the last word; match the poem's dominant darb |
| broken rhyme | find a rhyme word with the same rawi and majra; check ridf/ta'sis match |

## 3. Use the weight tool
`scan.py weigh "كلمة"` gives a word's pattern; build a phrase whose pattern
fills exactly the gap (e.g. the foot needs ب − − and you have ب −: add a
word weighing − or swap for a ب − − synonym).

## 4. الضرورات الشعرية (licences — use sparingly, and name them to the poet)
- صرف الممنوع من الصرف (يُنوَّن): «مساجدٍ».
- قطع همزة الوصل أو وصل همزة القطع.
- قصر الممدود (السماءُ → السما) أو مدّ المقصور (أقلّ قبولًا).
- تسكين المتحرك أو تحريك الساكن في مواضع محدودة.
- إشباع الحركة لتوليد حرف مد (خاصة في القافية).
- تخفيف المشدد: «رُبَّ → رُبَ».
Modern editors frown on heavy use; prefer lexical fixes first.

## 5. Present
For each broken line: original, then 2–3 verified alternatives, each with what
changed, why it scans now (the foot before/after), and any shift in meaning.
Let the poet choose; never overwrite the original silently.

# شعر التفعيلة والشعر الحر

## Definitions
- **شعر التفعيلة** (often called الشعر الحر in Arabic criticism since نازك الملائكة
  and بدر شاكر السياب, late 1940s): the line (السطر) is built from **one repeated
  taf'ila**, but the number of feet per line is free and lines need not rhyme
  regularly.
- **قصيدة النثر**: no meter at all. If the scanner finds no taf'ila that fits
  most lines, the text may be a prose poem — say so respectfully; it is a form,
  not a failure.
- Some poets mix taf'ilas from one "circle" (e.g. مستفعلن with فاعلن as in
  البسيط) — the scanner handles one family at a time; mention mixed usage when
  two families each fit different stretches.

## Taf'ila families (the "صافية" meters used in free verse)
| التفعيلة | البحر | صور الحشو | نهايات السطر الشائعة |
|---|---|---|---|
| متفاعلن | الكامل | متَفاعلن ب ب − ب −، متْفاعلن − − ب − | متفاعلْ، متفاعلانْ، متفاعلاتن، فعِلن |
| مستفعلن | الرجز | مستفعلن، متفعلن، مستعلن | مستفعلْ، متفعلْ، مستفعلانْ |
| فاعلاتن | الرمل | فاعلاتن، فعِلاتن | فاعلانْ، فاعلن، فعِلن، فاعلاتانْ |
| فعولن | المتقارب | فعولن، فعولُ | فعولْ، فعو، فعْ |
| فاعلن | المتدارك/الخبب | فاعلن، فعِلن، فعْلن | فاعلانْ، فاعلاتن |
| مفاعيلن | الهزج | مفاعيلن، مفاعيلُ | فعولن |
| مفاعلتن | الوافر | مفاعلتن، مفاعلْتن | فعولن |

## Rules the scanner applies
- Each line is a sequence of whole feet; the **last foot of a line** may take an
  ending form (علة) from the table.
- **التدوير**: a foot may run across a line break — the line's last word is then
  read in wasl (its final vowel not lengthened) and the foot completes in the
  next line. Marked ↵ in the report; it is legitimate, though some poets avoid it.
- Line length is free; a one-foot line is fine.
- Rhyme is free; recurring end-sounds may still be pointed out as a strength.

## Checking a single line while composing
`python3 scripts/scan.py verify --meter kamil --free "السطر"`

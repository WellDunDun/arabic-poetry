# -*- coding: utf-8 -*-
"""Rhyme (القافية) audit for classical poems: rawi, majra, ridf, ta'sis, qafiya type, common faults."""
from collections import Counter
from .lattice import parse_word, rewrite_special, clean

MADD = {'ا', 'ى', 'و', 'ي'}
VOWEL_AR = {'a': 'فتحة', 'u': 'ضمة', 'i': 'كسرة', None: 'غير مشكول', 'o': 'سكون', 'm': 'حركة غير مشكولة'}


def _last_word_units(text):
    words = clean(text).split(' ')
    return rewrite_special(parse_word(words[-1])), words[-1]


def line_rhyme(text):
    units, word = _last_word_units(text)
    units = list(units)
    # drop alef fariqa and trailing silent letters
    while len(units) > 1 and units[-1].letter == 'ا' and units[-2].letter == 'و' and not units[-2].vowel:
        units.pop()
    wasl = None
    idx = len(units) - 1
    # final madd letter after a moving letter = wasl (ishba' letter)
    if idx > 0 and units[idx].letter in MADD and not units[idx].vowel and not units[idx].shadda and not units[idx].tanwin:
        wasl = units[idx].letter
        idx -= 1
    rawi = units[idx]
    ha_wasl_candidate = None
    if rawi.letter in ('ه', 'ة') and idx > 0 and units[idx - 1].letter not in MADD:
        ha_wasl_candidate = idx - 1
    def info(i, wasl_letter):
        r = units[i]
        maj = r.vowel or r.tanwin or ('o' if r.sukun else None)
        if wasl_letter and maj is None:
            maj = {'ا': 'a', 'ى': 'a', 'و': 'u', 'ي': 'i'}.get(wasl_letter)
        ridf = None
        if i >= 1 and units[i - 1].letter in MADD and not units[i - 1].vowel and not units[i - 1].shadda:
            ridf = 'ا' if units[i - 1].letter in 'اى' else 'وي'
        tasis = i >= 2 and units[i - 2].letter == 'ا' and not units[i - 2].vowel and ridf is None
        return {'rawi': r.letter.replace('ة', 'ت'), 'majra': maj, 'ridf': ridf, 'tasis': tasis}
    base = info(idx, wasl)
    alt = info(ha_wasl_candidate, 'ه') if ha_wasl_candidate is not None else None
    return {'word': word, 'base': base, 'alt': alt}


def qafiya_type(pattern):
    """Classify by the number of moving letters between the last two still letters."""
    if not pattern or not pattern.endswith('0'):
        return None
    body = pattern[:-1]
    k = body.rfind('0')
    if k < 0:
        return None
    n = len(body) - k - 1
    return {0: 'مترادف (ساكنان متتاليان)', 1: 'متواتر', 2: 'متدارك', 3: 'متراكب', 4: 'متكاوس'}.get(n)


def audit(sadrs, ajuzs, ajuz_patterns=None, endings=None):
    rows = [line_rhyme(a) for a in ajuzs]
    # unmarked final letters: use what the meter scan chose (إطلاق = moving rawi, تقييد = sakin)
    for i, r in enumerate(rows):
        e = endings[i] if endings and i < len(endings) else None
        for key in ('base', 'alt'):
            c = r[key]
            if c and c['majra'] is None and e:
                c['majra'] = 'o' if e == 'sakin' else 'm'
    # each line votes for its possible rawi letters (with/without a ha of wasl)
    votes = Counter()
    for r in rows:
        cands = {r['base']['rawi']} | ({r['alt']['rawi']} if r['alt'] else set())
        votes.update(cands)
    rawi = votes.most_common(1)[0][0]
    chosen, ha_lines = [], []
    for i, r in enumerate(rows):
        if r['base']['rawi'] == rawi or not r['alt']:
            chosen.append(r['base'])
        elif r['alt']['rawi'] == rawi:
            chosen.append(r['alt']); ha_lines.append(i)
        else:
            chosen.append(r['base'])
    use_alt = len(ha_lines) > 0.5 * len(rows)
    issues = []
    if ha_lines and not use_alt:
        for i in ha_lines:
            issues.append((i, 'القافية هنا بهاء وصل («ـهْ/ـةْ») والرويّ متحرك قبلها، بخلاف بقية الأبيات'))
    for i, c in enumerate(chosen):
        if c['rawi'] != rawi:
            issues.append((i, f'الرويّ «{c["rawi"]}» يخالف رويّ القصيدة «{rawi}» (إكفاء/إجازة إن تقارب المخرج)'))
    majras = Counter(c['majra'] for c in chosen if c['majra'] and c['majra'] != 'm')
    if not majras:
        majras = Counter(c['majra'] for c in chosen if c['majra'])
    main_majra = majras.most_common(1)[0][0] if majras else None
    for i, c in enumerate(chosen):
        m = c['majra']
        if m is None or main_majra is None or m == main_majra:
            continue
        if m == 'm' and main_majra in ('a', 'u', 'i') or main_majra == 'm' and m in ('a', 'u', 'i'):
            continue
        pair = {m, main_majra}
        if pair == {'u', 'i'}:
            name = 'إقواء'
        elif 'a' in pair and 'o' not in pair:
            name = 'إصراف'
        else:
            name = 'خلط بين قافية مطلقة ومقيّدة'
        issues.append((i, f'{name}: حركة الرويّ {VOWEL_AR.get(m, m)} والغالب {VOWEL_AR.get(main_majra, main_majra)}'))
    unk = [i for i, c in enumerate(chosen) if c['majra'] == 'm']
    if unk and main_majra in ('a', 'u', 'i'):
        issues.append((unk[0], 'حركة الرويّ غير مشكولة في الأبيات ' + '، '.join(str(i + 1) for i in unk)
                       + f'؛ يجب أن تكون {VOWEL_AR[main_majra]} كبقية القصيدة — شكّلها للتحقق من الإقواء/الإصراف'))
    ridfs = Counter(c['ridf'] for c in chosen)
    main_ridf = ridfs.most_common(1)[0][0]
    for i, c in enumerate(chosen):
        if c['ridf'] != main_ridf:
            issues.append((i, f'سناد الردف: الردف هنا «{c["ridf"] or "لا ردف"}» والغالب «{main_ridf or "لا ردف"}»'))
    tas = Counter(c['tasis'] for c in chosen)
    main_tas = tas.most_common(1)[0][0]
    for i, c in enumerate(chosen):
        if c['tasis'] != main_tas:
            issues.append((i, 'سناد التأسيس: ' + ('تأسيس في بيت غير مؤسَّس القافية' if c['tasis'] else 'غياب ألف التأسيس')))
    seen = {}
    for i, r in enumerate(rows):
        w = clean(r['word'])
        w = ''.join(ch for ch in w if 'ء' <= ch <= 'ي')
        if w in seen and i - seen[w] < 7:
            issues.append((i, f'إيطاء محتمل: كلمة القافية «{r["word"]}» تكررت بعد البيت {seen[w] + 1} (لا عيب إن اختلف المعنى)'))
        seen[w] = i
    tasree = None
    if sadrs and sadrs[0]:
        s0 = line_rhyme(sadrs[0])
        sc = s0['alt'] if (s0['alt'] and s0['base']['rawi'] != rawi and s0['alt']['rawi'] == rawi) else s0['base']
        tasree = sc['rawi'] == rawi and (sc['majra'] in (main_majra, None, 'm') or main_majra == 'm')
    qtype = None
    if ajuz_patterns:
        types = Counter(qafiya_type(p) for p in ajuz_patterns if p)
        if types:
            qtype = types.most_common(1)[0][0]
    return {
        'rawi': rawi, 'ha_wasl': use_alt, 'majra': main_majra, 'majra_ar': VOWEL_AR.get(main_majra, main_majra),
        'mutlaqa': main_majra not in (None, 'o'), 'ridf': main_ridf, 'tasis': main_tas,
        'type': qtype, 'tasree': tasree, 'issues': sorted(issues),
    }

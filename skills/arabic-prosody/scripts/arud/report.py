# -*- coding: utf-8 -*-
"""Human-readable (Markdown) reports. Patterns are shown with / (moving) and 0 (still)."""
from .meters import METER_INFO, FORMS_BY_KEY, darb_group
from .classical import to_marks, discriminating_lines, template, rescan


def meter_title(form):
    ar, en, _ = METER_INFO[form.meter]
    return f'{ar} ({en}) — {form.name}'


def diagnose(foot, variants):
    exp, got = foot.expected, foot.got
    if len(got) > len(exp):
        kind = f'زيادة {len(got) - len(exp)} حرف/حروف'
    elif len(got) < len(exp):
        kind = f'نقص {len(exp) - len(got)} حرف/حروف'
    else:
        kind = 'حركة في موضع سكون أو العكس'
    allowed = '، '.join(f'{v[1]} {to_marks(v[0])}' for v in variants)
    return f'{kind} — وُجد {to_marks(got) or "∅"} والمسموح هنا: {allowed}'


def confidence(cands, n):
    if not cands:
        return 'لا يوجد'
    a = cands[0]
    b = cands[1] if len(cands) > 1 else None
    margin = (b['total'] - a['total']) if b else 9
    if a['exact'] == 0:
        return 'منخفضة'
    if margin >= max(1.0, 0.5 * n) and a['exact'] >= 0.5 * n:
        return 'عالية'
    if margin >= 0.5:
        return 'متوسطة'
    return 'منخفضة'


def word_fixes(text, form, part):
    """Which single word, if removed, makes the hemistich scan? (locates an extra word)"""
    from .classical import scan_hemistich
    from .lattice import clean
    words = clean(text).split(' ')
    hits = []
    if len(words) < 3:
        return hits
    for i in range(len(words)):
        t = ' '.join(words[:i] + words[i + 1:])
        r = scan_hemistich(t, form, part, cap=2)
        if r is not None and r.errors == 0:
            hits.append(words[i])
    return hits


MUAQABA = ('ramal', 'madid', 'khafif', 'mujtath')


def verse_warnings(idx, r, form):
    """Rules that span a whole verse: the تصريع forms of the عروض, and الاعتماد in الطويل."""
    out = []
    sadr, ajuz = r[1], r[2]
    if sadr is not None and sadr.errors == 0 and 'تصريع' in (sadr.ending_label or ''):
        same = ajuz is not None and sadr.feet[-1].got == ajuz.feet[-1].got
        if idx > 0 or not same:
            out.append(f'التصريع: «{sadr.ending_label}» لا تأتي إلا في مطلعٍ مصرَّع (العروض فيه على صورة الضرب)')
    if form.meter == 'tawil' and ajuz is not None and ajuz.errors == 0 and 'محذوف' in (ajuz.ending_label or '') \
            and len(ajuz.feet) >= 2 and ajuz.feet[-2].name == 'فعولن':
        out.append('الاعتماد: قبل الضرب المحذوف تُقبض «فعولن» عادةً (فعولُ فعولن)')
    return out


def render_hemi(h, part_name, form, show_ok=True, text=None):
    T = template(form, h.part if part_name == 'شطر منفرد' else ('ajuz' if (part_name in ('العجز', 'الشطر') or form.single) else 'sadr'))
    lines = []
    status = 'سليم' if h.errors == 0 else f'مكسور ({h.errors} خطأ)'
    lines.append(f'  - **{part_name}** [{status}]  الكتابة العروضية: `{h.arudi}`'
                 + ('  (ـ = حرف إشباع)' if 'ـ' in h.arudi else ''))
    feet_str = ' | '.join((f'{f.name} {to_marks(f.got)}' if not f.errors
                           else f'؟ {to_marks(f.got)} ✗ (المتوقع {f.name})') for f in h.feet)
    lines.append(f'    التفاعيل: {feet_str}')
    for a_, b_ in zip(h.feet, h.feet[1:]):
        if form.meter in MUAQABA and a_.name.endswith('ُ') and (b_.name.startswith('فعِ') or b_.name.startswith('متفع')):
            lines.append(f'    ⚠ معاقبة: لا يجتمع الكفّ في «{a_.name}» والخبن في «{b_.name}» بعدها (يسقط ساكنا السببين المتجاورين معًا)')
    if getattr(h, 'tadwir', None) and part_name == 'الصدر' and h.errors == 0:
        lines.append(f'    ↔ بيت مدوّر: كلمة «{h.tadwir}» مشتركة بين الشطرين، تبدأ تفعيلتها في الصدر وتكتمل في العجز')
    for f in h.feet:
        if f.errors:
            lines.append(f'    ✗ التفعيلة {f.pos + 1} («{f.letters}»): ' + diagnose(f, T.positions[f.pos]))
    if h.errors:
        diff = len(h.pattern) - min(len(v[0]) for v in T.positions[-1]) - sum(min(len(v[0]) for v in p) for p in T.positions[:-1])
        if text:
            hits = word_fixes(text, form, 'ajuz' if (part_name in ('العجز', 'الشطر') or form.single) else 'sadr')
            if hits:
                lines.append('    💡 دليل على موضع الزيادة (لا إصلاح جاهز): حذف كلمة واحدة من '
                             + '، '.join(f'«{w}»' for w in hits) + ' يعيد الوزن؛ الزيادة في هذه المنطقة')
    if h.readings:
        lines.append('    قراءات مفترضة: ' + '؛ '.join(dict.fromkeys(h.readings)))
    if h.n_unmarked:
        lines.append(f'    ⚠ {h.n_unmarked} حرفًا بلا تشكيل؛ السكون المفترض: `{h.sukun_hint}`')
    return lines


def render_classical(scans, ranking, cands, qaf=None, top_n=4):
    n = len(scans)
    out = []
    best = cands[0]
    form = best['form']
    out.append(f'## البحر: {meter_title(form)}')
    out.append(f'الثقة: **{confidence(cands, n)}** — أبيات سليمة {best["exact"]}/{n}'
               + (f'، الضرب الغالب: {best["dominant_darb"]}' if best['dominant_darb'] else ''))
    out.append(f'مفتاح البحر: {METER_INFO[form.meter][2]}')
    out.append('')
    out.append('### المرشّحون (الأقل تكلفة أرجح)')
    out.append('| البحر/الصيغة | التكلفة | أبيات سليمة | أشطر سليمة |')
    out.append('|---|---|---|---|')
    for c in cands[:top_n]:
        halves = n if c['form'].single else 2 * n
        out.append(f'| {meter_title(c["form"])} | {c["total"]:.2f} | {c["exact"]}/{n} | {c.get("exact_h", 0)}/{halves} |')
    if len(cands) > 1:
        a, b = cands[0], cands[1]
        ev = discriminating_lines(a, b)
        rev = discriminating_lines(b, a)
        out.append('')
        if ev:
            out.append(f'الأبيات التي تحسم لصالح {METER_INFO[a["form"].meter][0]} على {METER_INFO[b["form"].meter][0]}: '
                       + '، '.join(str(i + 1) for i in ev))
        elif b['total'] - a['total'] < 0.5:
            out.append(f'⚠ التباس بين {METER_INFO[a["form"].meter][0]} و{METER_INFO[b["form"].meter][0]}: '
                       'كل الأبيات تصلح للبحرين بالقراءة الحالية؛ أضف أبياتًا أو راجع التشكيل.')
        if rev:
            out.append(f'أبيات تميل إلى {METER_INFO[b["form"].meter][0]}: ' + '، '.join(str(i + 1) for i in rev))
    broken = sum(1 for c, r in best['per_line'] if not (r is not None and (r[1] is None or r[1].errors == 0) and r[2].errors == 0))
    if n >= 2 and broken / n >= 0.4:
        out.append('')
        out.append(f'⚠ **إعادة فحص:** الخلل في {broken} من {n} أبيات. قبل اقتراح أي تصحيح: راجع التشكيل، وجرّب البحور التالية '
                   '(`--meter`)، وجرّب `--mode free` إن لم تكن القصيدة عمودية: '
                   + '، '.join(f'{METER_INFO[c["form"].meter][0]} ({c["exact"]}/{n})' for c in cands[1:4]))
    if best['darb_mismatch']:
        out.append('')
        out.append('⚠ اختلاف الضرب عن الغالب في الأبيات: ' + '، '.join(str(i + 1) for i in best['darb_mismatch'])
                   + ' (الضرب يجب أن يلتزم صورة واحدة في القصيدة)')
    out.append('')
    out.append('### تقطيع الأبيات')
    for idx, (c, r) in enumerate(best['per_line']):
        ls = scans[idx]
        out.append(f'**{idx + 1}.** {ls.text.strip()}')
        if r is None:
            r = rescan(ls, form)
            if r is None:
                out.append('  - لم يمكن مطابقة البيت مع هذا البحر (خلل كبير أو طول غير مناسب).')
                continue
            out.append('  - ⚠ خلل كبير في هذا البيت:')
        if r[3] is not None and ls.sadr is None:
            out.append(f'  - (قُسّم البيت آليًّا: «{r[3][0]}» * «{r[3][1]}»)')
        sad_t, aj_t = (r[3] if r[3] else (None, ls.text))
        if r[1] is not None:
            out.extend(render_hemi(r[1], 'الصدر', form, text=sad_t))
        out.extend(render_hemi(r[2], 'العجز' if r[1] is not None else ('شطر منفرد' if getattr(r[2], 'lone', False) else 'الشطر'), form, text=aj_t))
        for w in verse_warnings(idx, r, form):
            out.append('    ⚠ ' + w)
        if r[1] is not None and r[1].errors == 0 and r[2].errors == 0 and best['dominant_darb'] and not getattr(r[2], 'lone', False) \
                and darb_group(r[2].ending_label) != best['dominant_darb']:
            out.append(f'    ⚠ الضرب هنا «{r[2].ending_label}» بخلاف الغالب «{best["dominant_darb"]}»')
    if qaf:
        out.append('')
        out.append('### القافية')
        typ = f'، نوعها: {qaf["type"]}' if qaf.get('type') else ''
        out.append(f'الرويّ: **{qaf["rawi"]}**' + (' (والهاء بعده وصل)' if qaf['ha_wasl'] else '')
                   + f'، حركته (المجرى): {qaf["majra_ar"]} — قافية {"مطلقة" if qaf["mutlaqa"] else "مقيّدة"}'
                   + (f'، الردف: {qaf["ridf"]}' if qaf['ridf'] else '') + ('، مؤسّسة' if qaf['tasis'] else '') + typ)
        if qaf.get('tasree') is not None:
            out.append('المطلع مصرَّع.' if qaf['tasree'] else 'المطلع غير مصرَّع.')
        if qaf['issues']:
            for i, msg in qaf['issues']:
                out.append(f'- البيت {i + 1}: {msg}')
        else:
            out.append('لا عيوب ظاهرة في القافية.')
    return '\n'.join(out)


def render_free(results, lines, top_n=3):
    out = []
    if not results:
        return 'تعذّر التقطيع.'
    best = results[0]
    fam = best['family']
    ar, en, _ = METER_INFO[fam.meter]
    bits = max(best['nbits'], 1)
    rate = best['errors'] / bits
    out.append(f'## شعر التفعيلة — التفعيلة: {fam.foot} (من {ar} / {en})')
    verdict = 'موزون' if rate < 0.03 else ('موزون مع مواضع خلل' if rate < 0.1 else 'لا يتّسق على تفعيلة واحدة — ربما قصيدة نثر أو مزج تفاعيل')
    out.append(f'الحكم: **{verdict}** — أخطاء {best["errors"]} في {bits} حرفًا عروضيًّا')
    nbroken = sum(1 for fl in best['lines'] if fl.errors)
    if len(best['lines']) >= 2 and nbroken / len(best['lines']) >= 0.4:
        out.append(f'⚠ **إعادة فحص:** الخلل في {nbroken} من {len(best["lines"])} أسطر. راجع التشكيل، وجرّب التفعيلات الأخرى (`--meter`) أو `--mode classical`.')
    out.append('')
    out.append('| التفعيلة | التكلفة | الأخطاء |')
    out.append('|---|---|---|')
    for r in results[:top_n + 2]:
        out.append(f'| {r["family"].foot} ({METER_INFO[r["family"].meter][0]}) | {r["total"]:.2f} | {r["errors"]} |')
    out.append('')
    from .lattice import build_hemistich, describe
    lens = [len(describe(build_hemistich(fl.text))[1]) for fl in best['lines']]
    if len(lens) >= 2 and len(lens) % 2 == 0 and max(lens) <= 1.25 * min(lens):
        out.append('💡 الأسطر متقاربة الطول: قد تكون عمودية، كل سطر شطر وكل سطرين بيت. جرّب `--mode pairs`.')
        out.append('')
    out.append('### تقطيع الأسطر')
    for fl in best['lines']:
        parts = []
        for (name, let, b, err, crosses) in fl.feet:
            if name.startswith('↩'):
                parts.append('(تكملة تفعيلة من السطر السابق)')
                continue
            parts.append(f'{name} {to_marks(b)}' + (' ✗' if err else '') + (' ↵' if crosses else ''))
        out.append(f'**{fl.index + 1}.** {fl.text.strip()}')
        nfeet = len([p for p in fl.feet if not p[0].startswith('↩')])
        out.append('   ' + ' | '.join(parts) + f'   — عدد التفعيلات: {nfeet}')
        for (name, let, b, err, crosses) in fl.feet:
            if err:
                out.append(f'   ✗ «{let}» = {to_marks(b)} لا يطابق صور {fam.foot} المسموحة: '
                           + '، '.join(f'{v[1]} {to_marks(v[0])}' for v in fam.hashw))
    notes = [f'سطر {li + 1}: {n}' for li, n in best['readings']]
    if notes:
        out.append('')
        out.append('قراءات مفترضة: ' + '؛ '.join(dict.fromkeys(notes)))
    out.append('')
    out.append('↵ = تفعيلة مدوَّرة تمتد إلى السطر التالي · ب مقطع قصير، − طويل، = زائد الطول')
    return '\n'.join(out)

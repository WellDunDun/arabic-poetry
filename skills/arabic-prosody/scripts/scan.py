#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic prosody (العروض) command-line tool.

  python3 scan.py analyze poem.txt [--mode auto|classical|free] [--meter KEY] [--json]
  python3 scan.py weigh "كلمات أو شطر"
  python3 scan.py verify --meter tawil [--form تام] [--part sadr|ajuz|verse] "بديل 1" "بديل 2" ...
  python3 scan.py meters

Input: one verse per line. Separate the two hemistichs with  *  or a tab or 3+ spaces
(or | ). Lines with no separator are auto-split, or treated as free verse.
Full diacritics (تشكيل) give the most reliable result.
"""
import argparse
import signal
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arud.lattice import build_hemistich, clean, describe   # noqa: E402
from arud.classical import (scan_line, rank_poem, best_per_meter, split_line, scan_hemistich, scan_mudawwar, TADWIR_PENALTY,  # noqa: E402
                            to_marks, template, scan_pair)
from arud.meters import FORMS, FORMS_BY_KEY, METER_INFO, FAMILIES   # noqa: E402
from arud import freeverse, qafiya, report   # noqa: E402


def read_input(path):
    if path in (None, '-'):
        text = sys.stdin.read()
    elif os.path.exists(path):
        text = open(path, encoding='utf-8').read()
    else:
        text = path
    return [l for l in text.splitlines() if clean(l)]


def forms_for(meter):
    if not meter:
        return FORMS
    fs = [f for f in FORMS if f.meter == meter or f.key == meter]
    if not fs:
        sys.exit(f'unknown meter {meter}; run: scan.py meters')
    return fs


def classical(lines, meter=None):
    forms = forms_for(meter)
    scans = [scan_line(i, l, forms) for i, l in enumerate(lines)]
    ranking = rank_poem(scans, forms)
    cands = best_per_meter(ranking)
    return scans, ranking, cands


def classical_qafiya(scans, best):
    sadrs, ajuzs, pats, ends = [], [], [], []
    for idx, (c, r) in enumerate(best['per_line']):
        ls = scans[idx]
        if ls.ajuz:
            sadrs.append(ls.sadr); ajuzs.append(ls.ajuz)
        elif r is not None and r[3] is not None:
            sadrs.append(r[3][0]); ajuzs.append(r[3][1])
        elif best['form'].single:
            sadrs.append(None); ajuzs.append(ls.text)
        else:
            continue
        pats.append(r[2].pattern if (r is not None and r[2].errors == 0) else None)
        e = None
        if r is not None:
            rd = ' '.join(r[2].readings)
            e = 'sakin' if 'آخر الشطر: سكون' in rd else ('moving' if 'إطلاق' in rd else None)
        ends.append(e)
    if not ajuzs:
        return None
    return qafiya.audit(sadrs, ajuzs, pats, ends)


def cmd_analyze(a):
    lines = read_input(a.input)
    if not lines:
        sys.exit('no text')
    has_sep = sum(1 for l in lines if split_line(l)) / len(lines)
    mode = a.mode
    free_res = None
    if mode == 'pairs':
        if len(lines) % 2 or has_sep:
            sys.exit('--mode pairs needs an even number of lines without * separators')
        lines = [lines[i] + ' * ' + lines[i + 1] for i in range(0, len(lines), 2)]
        mode = 'classical'
    if mode == 'auto':
        if has_sep >= 0.5:
            mode = 'classical'
        else:
            lens = [len(describe(build_hemistich(l))[1]) for l in lines]
            spread = (statistics.pstdev(lens) / statistics.mean(lens)) if len(lens) > 1 else 0
            scans, ranking, cands = classical(lines, a.meter)
            free_res, flines = freeverse.analyze(lines, meter=a.meter)
            c_err = cands[0]['total'] / len(lines) if cands else 99
            f_err = (free_res[0]['total'] / len(lines)) if free_res else 99
            if spread > 0.2:
                c_err += 0.5
            elif spread < 0.12:
                c_err -= 0.3     # equal-length lines: favour classical (مشطور / أرجوزة)
            mode = 'classical' if c_err <= f_err else 'free'
    if mode == 'free':
        res, flines = free_res and (free_res, lines) or freeverse.analyze(lines, meter=a.meter)
        if a.json:
            print(json.dumps([{'meter': r['family'].meter, 'foot': r['family'].foot, 'total': r['total'],
                               'errors': r['errors'],
                               'lines': [{'line': fl.index + 1, 'feet': [{'name': f[0], 'letters': f[1], 'pattern': f[2],
                                                                          'errors': f[3], 'tadwir': f[4]} for f in fl.feet]}
                                         for fl in r.get('lines', [])]} for r in res[:3]], ensure_ascii=False, indent=1))
        else:
            print(report.render_free(res, lines))
        return
    scans, ranking, cands = classical(lines, a.meter)
    qaf = classical_qafiya(scans, cands[0]) if cands else None
    if a.json:
        best = cands[0]
        def hj(h):
            if h is None:
                return None
            return {'arudi': h.arudi, 'pattern': to_marks(h.pattern), 'errors': h.errors, 'ending': h.ending_label,
                    'readings': h.readings, 'unmarked': h.n_unmarked,
                    'feet': [{'name': f.name, 'expected': to_marks(f.expected), 'got': to_marks(f.got),
                              'letters': f.letters, 'errors': f.errors} for f in h.feet]}
        print(json.dumps({
            'meter': best['form'].meter, 'meter_ar': METER_INFO[best['form'].meter][0], 'form': best['form'].name,
            'confidence': report.confidence(cands, len(lines)),
            'candidates': [{'form': c['form'].key, 'total': round(c['total'], 3), 'exact': c['exact']} for c in cands[:5]],
            'dominant_darb': best['dominant_darb'], 'darb_mismatch_lines': [i + 1 for i in best['darb_mismatch']],
            'verses': [{'n': i + 1, 'text': scans[i].text, 'sadr': hj(r[1]) if r else None, 'ajuz': hj(r[2]) if r else None}
                       for i, (c, r) in enumerate(best['per_line'])],
            'qafiya': qaf,
        }, ensure_ascii=False, indent=1))
    else:
        print(report.render_classical(scans, ranking, cands, qaf))


def cmd_weigh(a):
    text = ' '.join(a.text)
    words = clean(text).split(' ')
    slots = build_hemistich(text)
    print(f'النص: {text}')
    arudi, bits = describe(slots)
    print(f'الكتابة العروضية: {arudi}')
    print(f'الوزن: {to_marks(bits)}   ({len(bits)} حرفًا عروضيًّا: {bits.count("1")} متحرك، {bits.count("0")} ساكن)')
    print('الكلمات (قراءة افتراضية؛ آخر كلمة تُعامل كآخر شطر):')
    for wi, w in enumerate(words):
        ws = [s for s in slots if s.w == wi]
        b = ''.join(min(s.opts, key=lambda o: o.cost).bits for s in ws)
        alts = [s for s in ws if len(s.opts) > 1]
        alt_txt = ''
        if alts:
            alt_txt = '  بدائل: ' + '؛ '.join(f'{o.note or o.bits}={to_marks(o.bits)}' for s in alts for o in s.opts)
        print(f'  {w}: {to_marks(b)}{alt_txt}')


def rhyme_key(w):
    import re as _re
    x = _re.sub('[\u064B-\u0652\u0670\u0640]', '', clean(w))
    x = _re.sub('[أإآٱ]', 'ا', x).replace('ة', 'ه').replace('ى', 'ي')
    x = _re.sub('[^\u0621-\u064A]', '', x)
    return _re.sub('^(وال|فال|بال|كال|لل|ال)(?=..)', '', x)


def cmd_verify(a):
    if a.free:
        fams = [f for f in FAMILIES if f.meter == a.meter]
        if not fams:
            sys.exit('no taf\'ila family for this meter; run: scan.py meters')
        for text in a.texts:
            L, line_end = freeverse.build_stream([text])
            r = freeverse.scan_family(L, line_end, fams[0])
            print(f'— «{text}»')
            if r is None:
                print('  ✗ بعيد جدًّا عن الوزن'); continue
            total, steps, T = r
            fl, rd = freeverse.summarize(L, steps, T, [text])
            err = sum(f[3] for f in fl[0].feet)
            print(f'  {"✓ موزون" if err == 0 else "✗ مكسور"} على تفعيلة {fams[0].foot}: '
                  + ' | '.join(f'{f[0]} {to_marks(f[2])}' + (' ✗' if f[3] else '') for f in fl[0].feet))
        return
    forms = [f for f in FORMS if f.meter == a.meter and (not a.form or a.form in f.name)]
    if not forms:
        sys.exit('unknown meter/form; run: scan.py meters')
    used = []
    if a.poem:
        with open(a.poem, encoding='utf-8') as fh:
            plines = [l for l in fh.read().split('\n') if clean(l)]
        used = [(i + 1, clean(l).split(' ')[-1]) for i, l in enumerate(plines) if i + 1 != a.line]
    def repeat_of(text):
        ws = clean(text).split(' ')
        if not used or not ws:
            return None
        k = rhyme_key(ws[-1])
        return next((u for u in used if rhyme_key(u[1]) == k), None)
    for text in a.texts:
        sp = split_line(text)
        best = None
        for form in forms:
            if a.part == 'verse' or (a.part is None and sp):
                if form.single or not sp:
                    continue
                pair = scan_pair(sp[0], sp[1], form, first=True, cap=8)
                if pair and (best is None or pair[0] < best[0]):
                    best = (pair[0], form, [('الصدر', pair[1]), ('العجز', pair[2])])
                m = scan_mudawwar(sp[0], sp[1], form, cap=8)
                if m and (best is None or m[0] + TADWIR_PENALTY < best[0]):
                    best = (m[0] + TADWIR_PENALTY, form, [('الصدر', m[1]), ('العجز', m[2])])
            else:
                part = a.part or 'ajuz'
                if form.single and part == 'sadr':
                    continue
                r = scan_hemistich(text, form, part, cap=8)
                if r and (best is None or r.cost < best[0]):
                    best = (r.cost, form, [('الصدر' if part == 'sadr' else 'العجز', r)])
        if best is None:
            print(f'✗ «{text}» — بعيد جدًّا عن الوزن' if a.brief else f'— «{text}»\n  ✗ بعيد جدًّا عن الوزن')
            continue
        ok = all(h.errors == 0 for _, h in best[2])
        rp = repeat_of(text)
        if rp:
            ok = False
            print(f'  ⚠ إيطاء: «{rp[1]}» قافية السطر {rp[0]} — اختر كلمة قافية أخرى' if not a.brief else '', end='' if a.brief else '\n')
        if a.brief:
            feet = ' — '.join(' | '.join(f.name + ('✗' if f.errors else '') for f in h.feet) for _, h in best[2])
            tw = getattr(best[2][0][1], 'tadwir', None)
            print(f'{"✓" if ok else "✗"} «{text}»  [{feet}]' + (f'  (مدوّر: «{tw}» بين الشطرين)' if tw else '')
                  + (f'  ⚠ إيطاء: «{rp[1]}» قافية السطر {rp[0]}' if rp else ''))
            continue
        print(f'— «{text}»')
        print(f'  {"✓ موزون" if ok else "✗ مكسور"} على {report.meter_title(best[1])}')
        for name, h in best[2]:
            for l in report.render_hemi(h, name, best[1]):
                print('  ' + l)


def tashkeel_coverage(line):
    """Share of letters that carry the marks a scan needs (bare madd letters and alefs need none)."""
    from arud.lattice import parse_word, ALEFS
    need = have = 0
    for w in clean(line).split(' '):
        units = parse_word(w)
        for k, u in enumerate(units):
            if u.letter in ALEFS or u.letter in ('ى', 'آ'):
                continue
            prev = units[k - 1] if k else None
            if u.letter in 'وي' and not u.marked and prev is not None and prev.vowel in ('u', 'i'):
                continue   # madd letter
            need += 1
            have += u.marked
    return have, need


def cmd_coverage(a):
    lines = read_input(a.input)
    tot_h = tot_n = 0
    rows = []
    for i, l in enumerate(lines):
        h, n = tashkeel_coverage(l)
        tot_h += h; tot_n += n
        rows.append((i + 1, h, n))
    pct = 100 * tot_h / max(tot_n, 1)
    level = 'full' if pct >= 90 else ('partial' if pct >= 30 else 'none')
    print(f'tashkeel coverage: {pct:.0f}% ({level})')
    for i, h, n in rows:
        p = 100 * h / max(n, 1)
        if p < 90:
            print(f'  line {i}: {p:.0f}%')
    print({'full': 'OK to scan directly (confirm only real ambiguities).',
           'partial': 'Complete the tashkeel and ask the poet to confirm before scanning.',
           'none': 'Diacritize the whole poem and ask the poet to confirm before scanning.'}[level])


def cmd_meters(a):
    for f in FORMS:
        ar, en, key_line = METER_INFO[f.meter]
        hem = ' '.join(vs[0][1] for vs in f.hashw)
        arud = '/'.join(dict.fromkeys(v[1] for v in f.arud)) if f.arud else '—'
        darb = '/'.join(dict.fromkeys(v[1] for v in f.darb))
        print(f'{f.meter:10s} {ar} — {f.name}: {hem} [{arud}] || {hem} [{darb}]')
    print('\nشعر التفعيلة:')
    for fam in FAMILIES:
        print(f'  {fam.meter:10s} {fam.foot}  صور الحشو: ' + '، '.join(v[1] for v in fam.hashw)
              + '  | نهايات: ' + '، '.join(v[1] for v in fam.endings))


def main():
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    an = sub.add_parser('analyze'); an.add_argument('input', nargs='?')
    an.add_argument('--mode', default='auto', choices=['auto', 'classical', 'free', 'pairs'],
                    help='pairs = one hemistich per line, two lines make a verse')
    an.add_argument('--meter'); an.add_argument('--json', action='store_true')
    an.set_defaults(fn=cmd_analyze)
    w = sub.add_parser('weigh'); w.add_argument('text', nargs='+'); w.set_defaults(fn=cmd_weigh)
    v = sub.add_parser('verify'); v.add_argument('--meter', required=True); v.add_argument('--form')
    v.add_argument('--part', choices=['sadr', 'ajuz', 'verse'])
    v.add_argument('--free', action='store_true', help='check as a taf\'ila (free verse) line')
    v.add_argument('--brief', action='store_true', help='one line per candidate')
    v.add_argument('--poem', help='poem file: flag candidates whose rhyme word already ends another verse (إيطاء)')
    v.add_argument('--line', type=int, help='with --poem: 1-based number of the line being replaced')
    v.add_argument('texts', nargs='+')
    v.set_defaults(fn=cmd_verify)
    m = sub.add_parser('meters'); m.set_defaults(fn=cmd_meters)
    c = sub.add_parser('coverage'); c.add_argument('input', nargs='?'); c.set_defaults(fn=cmd_coverage)
    a = p.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()

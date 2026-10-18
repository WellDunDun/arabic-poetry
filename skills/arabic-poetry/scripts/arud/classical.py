# -*- coding: utf-8 -*-
"""Scansion of classical (عمودي) verse: per-hemistich alignment against every meter form,
then a poem-level vote that weighs all lines together."""
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

from .lattice import build_hemistich, clean
from .aligner import LatticeGraph, TemplateGraph, align
from .meters import FORMS, METER_INFO, darb_group

LINE_CAP = 6.0          # a hopeless line can't contribute more than this to a meter's total
DARB_MISMATCH = 0.75    # penalty when a line's darb differs from the poem's dominant darb

_TEMPLATE_CACHE = {}


def template(form, part, ending_patterns=None, tasri_pattern=None):
    key = (form.key, part, tuple(ending_patterns or ()), tasri_pattern)
    if key not in _TEMPLATE_CACHE:
        last = form.darb if (part == 'ajuz' or form.single) else [
            v for v in form.arud if 'تصريع' not in v[3] or v[0] == tasri_pattern]
        if ending_patterns is not None:
            last = [v for v in last if v[0] in ending_patterns]
        _TEMPLATE_CACHE[key] = TemplateGraph(form.hashw + [last]) if last else None
    return _TEMPLATE_CACHE[key]


def restricted_template(form, group):
    key = (form.key, 'ajuz', group)
    if key not in _TEMPLATE_CACHE:
        darb = [v for v in form.darb if darb_group(v[3]) == group]
        if not darb:
            return None
        _TEMPLATE_CACHE[key] = TemplateGraph(form.hashw + [darb])
    return _TEMPLATE_CACHE[key]


def scan_restricted(text, form, group, cap=4.0):
    T = restricted_template(form, group)
    if T is None:
        return None
    scan_hemistich(text, form, 'ajuz', cap)          # fills the lattice cache
    from .classical import scan_hemistich as _s      # noqa
    L, words = _LATTICE_CACHE[text]
    r = align(L, T, cap)
    if r is None:
        return None
    return summarize(L, T, r[0], r[1], form, 'ajuz', words)


def to_marks(bits):
    """Classical syllable notation, read right to left: ب short (moving letter alone), − long (moving + still), = overlong (moving + two still)."""
    t = []
    i = 0
    while i < len(bits):
        if bits[i] == '1':
            if i + 1 < len(bits) and bits[i + 1] == '0':
                t.append('−'); i += 2; continue
            t.append('ب')
        else:
            if t and t[-1] == '−':
                t[-1] = '='
            else:
                t.append('◌ْ')  # a stray still letter (only in broken feet)
        i += 1
    return ' '.join(t)


@dataclass
class Foot:
    pos: int
    expected: str
    name: str
    label: str
    got: str
    letters: str
    errors: int
    words: List[int]


@dataclass
class HemiResult:
    form_key: str
    part: str
    cost: float
    errors: int
    feet: List[Foot]
    readings: List[str]
    ending_label: str
    arudi: str
    pattern: str
    sukun_hint: Optional[str] = None   # undiacritized letters the scan assumed sakin
    n_unmarked: int = 0


def summarize(L, T, cost, steps, form, part, words) -> HemiResult:
    positions = T.positions
    per = defaultdict(lambda: {'v': None, 'got': '', 'let': '', 'err': 0, 'words': set()})
    cur = 0
    readings = []
    seen = set()
    sukun_at = set()
    for st in steps:
        if st.pinfo is not None:
            cur = st.pinfo[0]
            if per[cur]['v'] is None:
                per[cur]['v'] = st.pinfo[1]
        if st.tinfo is not None:
            k, j, c = st.tinfo
            o = L.slots[k].opts[j]
            if (k, j) not in seen:
                seen.add((k, j))
                sl = L.slots[k]
                if len(sl.opts) > 1 and sl.kind in ('unk', 'unk_end') and o.bits == '0':
                    sukun_at.add(k)
                if o.note and len(sl.opts) > 1 and sl.kind not in ('unk',) and not (sl.kind == 'unk_end' and o.bits in ('0', '1')):
                    readings.append(f'«{words[sl.w]}»: {o.note}')
            if c >= 0:
                per[cur]['got'] += st.bit
                per[cur]['let'] += o.disp[c] if c < len(o.disp) else ''
                per[cur]['words'].add(L.slots[k].w)
        if st.op in ('sub', 'del', 'ins'):
            per[cur]['err'] += 1
    feet = []
    for p, variants in enumerate(positions):
        d = per[p]
        vi = d['v'] if d['v'] is not None else 0
        var = variants[vi]
        feet.append(Foot(p, var[0], var[1], var[3], d['got'], d['let'], d['err'], sorted(d['words'])))
    errors = sum(1 for st in steps if st.op in ('sub', 'del', 'ins'))
    arudi = ' '.join(f.letters for f in feet)
    pattern = ''.join(st.bit for st in steps if st.bit is not None)
    hint = None
    n_unk = sum(1 for s in L.slots if s.kind in ('unk', 'unk_end'))
    if n_unk:
        out_words = {}
        for k, s in enumerate(L.slots):
            out_words.setdefault(s.w, '')
            out_words[s.w] += s.letter + ('\u0652' if k in sukun_at else '')
        hint = ' '.join(out_words[w] for w in sorted(out_words))
    return HemiResult(form.key, part, cost, errors, feet, readings, feet[-1].label, arudi, pattern, hint, n_unk)


_LATTICE_CACHE = {}


def scan_hemistich(text, form, part, cap=4.0, _cache=_LATTICE_CACHE,
                    ending_patterns=None, tasri_pattern=None):
    key = text
    if key not in _cache:
        slots = build_hemistich(text)
        _cache[key] = (LatticeGraph(slots), clean(text).split(' '))
    L, words = _cache[key]
    T = template(form, part, ending_patterns, tasri_pattern)
    if T is None:
        return None
    r = align(L, T, cap)
    if r is None:
        return None
    cost, steps = r
    return summarize(L, T, cost, steps, form, part, words)


def same_rhyme(a, b):
    """Compare available rhyme candidates; unknown vowels remain provisional."""
    from .qafiya import line_rhyme
    ra, rb = line_rhyme(a), line_rhyme(b)
    return any(x['rawi'] == y['rawi'] and x['ridf'] == y['ridf'] and x['tasis'] == y['tasis'] and
               (x['majra'] is None or y['majra'] is None or x['majra'] == y['majra'])
               for x in (ra['base'], ra['alt']) if x
               for y in (rb['base'], rb['alt']) if y)


def compatible_endings(ra, rb, form, first=False):
    if ra is None:
        return form.single
    arud, darb = ra.feet[-1], rb.feet[-1]
    if form.ending_pairs and darb.expected not in form.ending_pairs.get(arud.expected, []):
        return False
    return 'تصريع' not in arud.label or (first and arud.expected == darb.expected)


def scan_pair(a, b, form, first=False, cap=4.0):
    """Enforce declared ending pairs and contextual first-verse tasri'."""
    endings = list(dict.fromkeys(v[0] for v in form.darb)) if form.ending_pairs else [None]
    best = None
    for ending in endings:
        rb = scan_hemistich(b, form, 'ajuz', cap,
                             ending_patterns=[ending] if ending else None)
        if rb is None:
            continue
        allowed = [arud for arud, darbs in form.ending_pairs.items()
                   if rb.feet[-1].expected in darbs] if form.ending_pairs else None
        if allowed == []:
            continue
        tasri = rb.feet[-1].expected if first and rb.errors == 0 and same_rhyme(a, b) else None
        ra = scan_hemistich(a, form, 'sadr', cap, ending_patterns=allowed, tasri_pattern=tasri)
        if ra and (best is None or ra.cost + rb.cost < best[0]):
            best = (ra.cost + rb.cost, ra, rb, (a, b))
    return best


SEPARATORS = re.compile(r'\s*(?:\t+|\*+|\|+|…+|\.\.\.+|٭+|⁂|\s{3,}|//+|-{2,}|—+|،\s{2,})\s*')


def split_line(line):
    parts = [p for p in SEPARATORS.split(line.strip()) if p.strip()]
    if len(parts) == 2:
        return parts[0], parts[1]
    return None


def auto_splits(line):
    words = clean(line).split(' ')
    n = len(words)
    total = sum(len(w) for w in words)
    out = []
    acc = 0
    for i in range(1, n):
        acc += len(words[i - 1])
        if 0.33 <= acc / total <= 0.67:
            out.append((' '.join(words[:i]), ' '.join(words[i:])))
    return out


@dataclass
class LineScan:
    index: int
    text: str
    sadr: Optional[str]
    ajuz: Optional[str]
    results: dict = field(default_factory=dict)   # form_key -> (cost, sadrRes, ajuzRes)


def scan_line(i, line, forms=FORMS, auto_split=True):
    ls = LineScan(i, line, None, None)
    sp = split_line(line)
    candidates = [sp] if sp else (auto_splits(line) if auto_split else [])
    for form in forms:
        best = None
        if form.single:
            text = line if not sp else None
            if text is None:
                continue
            r = scan_hemistich(text, form, 'ajuz')
            if r is not None:
                best = (r.cost + form.rare, None, r, None)
        else:
            for (a, b) in candidates:
                pair = scan_pair(a, b, form, first=i == 0)
                if pair is None:
                    continue
                _, ra, rb, _ = pair
                c = pair[0] + form.rare
                if best is None or c < best[0]:
                    best = (c, ra, rb, (a, b))
        if best is not None:
            ls.results[form.key] = best
    if sp:
        ls.sadr, ls.ajuz = sp
    return ls


def rank_poem(lines: List[LineScan], forms=FORMS):
    """Score every meter form across all lines; returns ranked list of dicts."""
    ranking = []
    for form in forms:
        per_line = []
        darbs = Counter()
        for ls in lines:
            r = ls.results.get(form.key)
            if r is None:
                per_line.append((LINE_CAP, None))
                continue
            per_line.append((min(r[0], LINE_CAP), r))
            if r[2] is not None and r[2].errors == 0:
                darbs[darb_group(r[2].ending_label)] += 1
        dominant = darbs.most_common(1)[0][0] if darbs else None
        # second pass: lines whose ending is ambiguous are re-read to agree with the poem's darb
        if dominant and not form.single:
            for idx, (c, r) in enumerate(per_line):
                if r is None or r[2].errors or (r[1] is not None and r[1].errors):
                    continue
                if darb_group(r[2].ending_label) == dominant:
                    continue
                aj_text = r[3][1] if r[3] else lines[idx].ajuz
                if not aj_text:
                    continue
                rr = scan_restricted(aj_text, form, dominant)
                if rr is not None and rr.errors == 0 and compatible_endings(r[1], rr, form, idx == 0):
                    nc = (r[1].cost if r[1] else 0) + rr.cost + form.rare
                    per_line[idx] = (min(nc, LINE_CAP), (nc, r[1], rr, r[3]))
        total = 0.0
        exact = 0
        mismatched_darb = []
        for idx, (c, r) in enumerate(per_line):
            total += c
            if r is not None and (r[1] is None or r[1].errors == 0) and r[2].errors == 0:
                exact += 1
                if dominant and darb_group(r[2].ending_label) != dominant:
                    total += DARB_MISMATCH
                    mismatched_darb.append(idx)
        exact_h = sum(((r[1] is not None and r[1].errors == 0) + (r[2].errors == 0)) for c, r in per_line if r is not None)
        ranking.append({'form': form, 'total': total, 'exact': exact, 'exact_h': exact_h, 'n': len(lines),
                        'dominant_darb': dominant, 'darb_mismatch': mismatched_darb, 'per_line': per_line})
    score = lambda d: (d['total'] - 0.25 * d['exact_h'], -d['exact'])
    ranking.sort(key=score)
    # lines too broken for the fast pass still count their sound half (top candidates only)
    for d in ranking[:6]:
        for idx, (c, r) in enumerate(d['per_line']):
            if r is None:
                rr = rescan(lines[idx], d['form'])
                if rr is not None:
                    d['exact_h'] += (rr[1] is not None and rr[1].errors == 0) + (rr[2].errors == 0)
    ranking.sort(key=score)
    return ranking


def best_per_meter(ranking):
    seen, out = set(), []
    for r in ranking:
        m = r['form'].meter
        if m in seen:
            continue
        seen.add(m)
        out.append(r)
    return out


def discriminating_lines(a, b):
    """Lines that fit candidate a exactly but not b (evidence for a over b)."""
    out = []
    for idx, ((ca, ra), (cb, rb)) in enumerate(zip(a['per_line'], b['per_line'])):
        ea = ra is not None and (ra[1] is None or ra[1].errors == 0) and ra[2].errors == 0
        eb = rb is not None and (rb[1] is None or rb[1].errors == 0) and rb[2].errors == 0
        if ea and not eb:
            out.append(idx)
    return out


def rescan(ls, form, cap=20.0):
    """Re-scan one line against one form with a loose cap (for reporting badly broken lines)."""
    sp = split_line(ls.text)
    candidates = [sp] if sp else auto_splits(ls.text)
    best = None
    if form.single:
        r = scan_hemistich(ls.text, form, 'ajuz', cap)
        return (r.cost, None, r, None) if r else None
    for (a, b) in candidates:
        pair = scan_pair(a, b, form, first=ls.index == 0, cap=cap)
        if pair and (best is None or pair[0] < best[0]):
            best = pair
    return best

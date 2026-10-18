# -*- coding: utf-8 -*-
"""
Scansion of taf'ila / free verse (شعر التفعيلة): lines of unequal length built on
one repeated foot. The whole poem is scanned as one stream so a foot may run on
from one line into the next (تدوير). Every family is tried and ranked.
"""
from dataclasses import dataclass, field
from typing import List

from .lattice import build_hemistich, clean, Opt
from .aligner import LatticeGraph, INS, DEL, SUB, INF
from .meters import FAMILIES, METER_INFO

CROSS = 0.15     # a foot continues across a line break (tadwir)
BEAM = 5.0


class LoopTemplate:
    def __init__(self, family):
        self.family = family
        self.variants = [(v, False) for v in family.hashw] + [(v, True) for v in family.endings]
        self.out = [[]]                 # state 0 = START (foot boundary)
        for vi, (var, is_end) in enumerate(self.variants):
            bits = var[0]
            prev = 0
            for c, b in enumerate(bits):
                last = c == len(bits) - 1
                if last:
                    to = 0
                else:
                    self.out.append([])
                    to = len(self.out) - 1
                self.out[prev].append((to, b, var[2] if c == 0 else 0.0, (vi, c), is_end and last))
                prev = to
        self.n = len(self.out)


def _add_tadwir(slots):
    for k in range(len(slots) - 1, -1, -1):
        s = slots[k]
        if s.kind == 'silent':
            continue
        extra = []
        for o in s.opts:
            if len(o.bits) >= 2 and o.bits.endswith('0') and s.kind in ('end_v', 'end_amb', 'ha', 'shadda'):
                extra.append(Opt(o.bits[:-1], o.disp[:-1], o.cost + 0.3, 'تدوير: آخر السطر موصول بما بعده'))
        s.opts.extend(extra)
        return


@dataclass
class FVLine:
    index: int
    text: str
    feet: list = field(default_factory=list)     # (name, letters, bits, errors, crosses_line)
    errors: int = 0


def build_stream(lines):
    slots, owner = [], []
    for li, line in enumerate(lines):
        sl = build_hemistich(line)
        if li + 1 < len(lines):
            _add_tadwir(sl)
        for s in sl:
            s.line = li
        slots.extend(sl)
    L = LatticeGraph(slots)
    line_end = set()
    L.end_line = {}          # line-end node -> the line it closes
    for k in range(1, len(slots)):
        if slots[k].line != slots[k - 1].line:
            line_end.add(L.slot_start[k]); L.end_line[L.slot_start[k]] = slots[k - 1].line
    line_end.add(L.final)
    # nodes followed only by silent (epsilon) edges into a line end are line ends too
    changed = True
    while changed:
        changed = False
        for u in range(L.n):
            if u in line_end or not L.out[u]:
                continue
            if all(b is None and w in line_end for (w, b, _, _) in L.out[u]):
                line_end.add(u); changed = True
                tgt = [L.end_line[w] for (w, _, _, _) in L.out[u] if w in L.end_line]
                if tgt:
                    L.end_line[u] = tgt[0]
    return L, line_end


def scan_family(L, line_end, family, no_cross=frozenset()):
    T = LoopTemplate(family)
    cost = [dict() for _ in range(L.n)]
    back = [dict() for _ in range(L.n)]
    cost[0][0] = 0.0
    for u in range(L.n):
        cu = cost[u]
        if not cu:
            continue
        best = min(cu.values())
        bu = back[u]
        for s in range(T.n):
            c = cu.get(s)
            if c is None or c > best + BEAM:
                continue
            for (t, ch, ec, pin, end_only) in T.out[s]:
                if end_only and u not in line_end:
                    continue
                nc = c + INS + ec
                if t > s and nc < cu.get(t, INF):
                    cu[t] = nc; bu[t] = (u, s, 'ins', None, None, pin, ch)
            for (w, bit, lc, tin) in L.out[u]:
                cw, bw = cost[w], back[w]
                cross = ((INF if getattr(L, 'end_line', {}).get(w) in no_cross else CROSS)
                         if (w in line_end and w != L.final) else 0.0)
                if bit is None:
                    nc = c + lc + (cross if s != 0 else 0)
                    if nc < cw.get(s, INF):
                        cw[s] = nc; bw[s] = (u, s, 'eps', tin, None, None, None)
                    continue
                nc = c + lc + DEL + (cross if s != 0 else 0)
                if nc < cw.get(s, INF):
                    cw[s] = nc; bw[s] = (u, s, 'del', tin, bit, None, None)
                for (t, ch, ec, pin, end_only) in T.out[s]:
                    if end_only and w not in line_end:
                        continue
                    nc = c + lc + ec + (0.0 if ch == bit else SUB) + (cross if t != 0 else 0)
                    if nc < cw.get(t, INF):
                        cw[t] = nc; bw[t] = (u, s, 'match' if ch == bit else 'sub', tin, bit, pin, ch)
    fin = cost[L.final]
    if not fin:
        return None
    # prefer ending on a foot boundary; otherwise pay for the missing part
    end_state = 0 if 0 in fin else min(fin, key=fin.get)
    total = fin[end_state] + (0 if end_state == 0 else 2.0)
    steps = []
    u, s = L.final, end_state
    while (u, s) != (0, 0):
        pu, ps, op, tin, bit, pin, ch = back[u][s]
        steps.append((op, tin, bit, pin, ch))
        u, s = pu, ps
    steps.reverse()
    return total, steps, T


def summarize(L, steps, T, lines):
    out = [FVLine(i, t) for i, t in enumerate(lines)]
    cur = None   # current foot accumulator
    readings = []

    def flush(foot):
        if foot is None:
            return
        li = foot['lines'][0] if foot['lines'] else 0
        crosses = len(set(foot['lines'])) > 1
        out[li].feet.append((foot['name'], foot['let'], foot['bits'], foot['err'], crosses))
        out[li].errors += foot['err']
        for extra in set(foot['lines'][1:]):
            if extra != li:
                out[extra].feet.append(('↩ ' + foot['name'], '', '', 0, True))

    pend = None   # extra syllables at a line's start belong to that line's first foot
    for (op, tin, bit, pin, ch) in steps:
        if pin is not None and pin[1] == 0:
            flush(cur)
            var = T.variants[pin[0]][0]
            cur = {'name': var[1], 'let': '', 'bits': '', 'err': 0, 'lines': []}
            if pend:
                cur.update(pend); pend = None
        if cur is None:
            cur = {'name': '؟', 'let': '', 'bits': '', 'err': 0, 'lines': []}
        if op == 'del' and tin is not None and cur['lines'] and L.slots[tin[0]].line > max(cur['lines']):
            k, j, c = tin
            o = L.slots[k].opts[j]
            pend = pend or {'let': '', 'bits': '', 'err': 0, 'lines': []}
            if c >= 0:
                pend['bits'] += bit
                pend['let'] += o.disp[c] if c < len(o.disp) else ''
                pend['lines'].append(L.slots[k].line)
            pend['err'] += 1
            continue
        if pend and tin is not None and pend['lines'] and L.slots[tin[0]].line == pend['lines'][0]:
            for key in ('let', 'bits'):
                cur[key] += pend[key]
            cur['err'] += pend['err']; cur['lines'] += pend['lines']; pend = None
        if tin is not None:
            k, j, c = tin
            o = L.slots[k].opts[j]
            if c >= 0:
                cur['bits'] += bit
                cur['let'] += o.disp[c] if c < len(o.disp) else ''
                cur['lines'].append(L.slots[k].line)
            if o.note and len(L.slots[k].opts) > 1 and L.slots[k].kind not in ('unk',) and c <= 0:
                readings.append((L.slots[k].line, o.note))
        if op in ('sub', 'del', 'ins'):
            cur['err'] += 1
    flush(cur)
    if pend:
        flush(dict(pend, name='؟'))
    return out, readings


def bad_crossings(L, steps):
    """Lines whose closing foot runs into the next line and still has errors: there the run-on
    (تدوير) only shifts a fault instead of completing a foot."""
    out, lines, err = set(), [], 0
    def close():
        ls = sorted(set(lines))
        if len(ls) > 1 and err > 0:
            out.update(range(ls[0], ls[-1]))
    for (op, tin, bit, pin, ch) in steps:
        if pin is not None and pin[1] == 0:
            close(); lines, err = [], 0
        if op == 'del' and tin is not None and lines and L.slots[tin[0]].line > max(lines):
            continue
        if tin is not None and tin[2] >= 0:
            lines.append(L.slots[tin[0]].line)
        if op in ('sub', 'del', 'ins'):
            err += 1
    close()
    return out


def scan_family_best(L, line_end, fam):
    """A line may run on into the next only through a sound foot; where a crossing foot is broken,
    that line is made to close on its own and the poem is rescanned."""
    banned = set()
    r = scan_family(L, line_end, fam)
    for _ in range(6):
        if r is None:
            return None
        bad = bad_crossings(L, r[1]) - banned
        if not bad:
            return r
        banned |= bad
        r2 = scan_family(L, line_end, fam, frozenset(banned))
        if r2 is None:
            return r
        r = r2
    return r


def analyze(lines, meter=None):
    lines = [l for l in lines if clean(l)]
    L, line_end = build_stream(lines)
    results = []
    for fam in FAMILIES:
        if meter and fam.meter != meter:
            continue
        r = scan_family_best(L, line_end, fam)
        if r is None:
            continue
        total, steps, T = r
        errors = sum(1 for s in steps if s[0] in ('sub', 'del', 'ins'))
        nbits = sum(1 for s in steps if s[2] is not None)
        results.append({'family': fam, 'total': total, 'errors': errors, 'nbits': nbits,
                        'steps': steps, 'T': T})
    results.sort(key=lambda d: d['total'])
    for r in results[:3]:
        r['lines'], r['readings'] = summarize(L, r['steps'], r['T'], lines)
    return results, lines

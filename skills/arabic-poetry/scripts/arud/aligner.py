# -*- coding: utf-8 -*-
"""
Weighted alignment between a reading lattice (all plausible pronunciations of a
hemistich) and a meter template (all permitted feet at each position).

Edit operations let us scan *broken* lines too: the best alignment shows which
foot breaks and by how much (a missing / extra / wrong letter).
"""
from dataclasses import dataclass
from typing import List, Optional

INS = 1.0   # template expects a letter the text does not have  (line too short here)
DEL = 1.0   # text has a letter the template does not expect     (line too long here)
SUB = 1.0   # moving where still is expected, or the reverse
INF = float('inf')


class LatticeGraph:
    """DAG built from lattice slots. Nodes are numbered in topological order."""

    def __init__(self, slots):
        self.slots = slots
        self.out = [[]]           # node -> list of (to, bit|None, cost, info)
        self.slot_start = []
        node = 0
        for k, s in enumerate(slots):
            self.slot_start.append(node)
            pending = []          # (from_node, bits, cost, opt_idx)
            ends = []
            for j, o in enumerate(s.opts):
                pending.append((j, o))
            # allocate intermediate nodes
            chains = []
            for j, o in pending:
                inter = []
                for _ in range(max(len(o.bits) - 1, 0)):
                    self.out.append([])
                    inter.append(len(self.out) - 1)
                chains.append((j, o, inter))
            self.out.append([])
            nxt = len(self.out) - 1
            for j, o, inter in chains:
                if not o.bits:
                    self.out[node].append((nxt, None, o.cost, (k, j, -1)))
                    continue
                seq = [node] + inter + [nxt]
                for c, b in enumerate(o.bits):
                    self.out[seq[c]].append((seq[c + 1], b, o.cost if c == 0 else 0.0, (k, j, c)))
            node = nxt
        self.final = node
        self.n = len(self.out)
        # length bounds for quick pruning
        lo = [INF] * self.n
        hi = [-INF] * self.n
        lo[0] = hi[0] = 0
        for u in range(self.n):
            if lo[u] == INF:
                continue
            for (w, b, _, _) in self.out[u]:
                d = 0 if b is None else 1
                lo[w] = min(lo[w], lo[u] + d)
                hi[w] = max(hi[w], hi[u] + d)
        self.min_len, self.max_len = lo[self.final], hi[self.final]


class TemplateGraph:
    """DAG for one hemistich template: a list of positions, each a list of variants."""

    def __init__(self, positions):
        self.positions = positions
        self.out = [[]]
        self.boundary = [0]
        node = 0
        for p, variants in enumerate(positions):
            chains = []
            for vi, var in enumerate(variants):
                inter = []
                for _ in range(len(var[0]) - 1):
                    self.out.append([])
                    inter.append(len(self.out) - 1)
                chains.append((vi, var, inter))
            self.out.append([])
            nxt = len(self.out) - 1
            for vi, var, inter in chains:
                seq = [node] + inter + [nxt]
                for c, b in enumerate(var[0]):
                    self.out[seq[c]].append((seq[c + 1], b, var[2] if c == 0 else 0.0, (p, vi, c)))
            node = nxt
            self.boundary.append(node)
        self.final = node
        self.n = len(self.out)
        self.min_len = sum(min(len(v[0]) for v in vs) for vs in positions)
        self.max_len = sum(max(len(v[0]) for v in vs) for vs in positions)


@dataclass
class Step:
    op: str                    # match / sub / del / ins / eps
    tinfo: Optional[tuple]     # lattice (slot, opt, char)
    bit: Optional[str]
    pinfo: Optional[tuple]     # template (pos, variant, char)
    expected: Optional[str]


def align(L: LatticeGraph, T: TemplateGraph, cap: float = 4.0):
    if L.min_len - T.max_len > cap or T.min_len - L.max_len > cap:
        return None
    cost = [dict() for _ in range(L.n)]
    back = [dict() for _ in range(L.n)]
    cost[0][0] = 0.0
    Tout = T.out
    for u in range(L.n):
        cu = cost[u]
        if not cu:
            continue
        bu = back[u]
        lout = L.out[u]
        # template states are numbered topologically, so insertions (s -> t > s)
        # are always relaxed before t is visited in this loop
        for s in range(T.n):
            c = cu.get(s)
            if c is None or c > cap:
                continue
            for (t, ch, ec, pin) in Tout[s]:
                nc = c + INS + ec
                if nc < cu.get(t, INF):
                    cu[t] = nc
                    bu[t] = (u, s, 'ins', None, None, pin, ch)
            for (w, bit, lc, tin) in lout:
                cw, bw = cost[w], back[w]
                if bit is None:
                    nc = c + lc
                    if nc < cw.get(s, INF):
                        cw[s] = nc; bw[s] = (u, s, 'eps', tin, None, None, None)
                    continue
                nc = c + lc + DEL
                if nc < cw.get(s, INF):
                    cw[s] = nc; bw[s] = (u, s, 'del', tin, bit, None, None)
                for (t, ch, ec, pin) in Tout[s]:
                    nc = c + lc + ec + (0.0 if ch == bit else SUB)
                    if nc < cw.get(t, INF):
                        cw[t] = nc; bw[t] = (u, s, 'match' if ch == bit else 'sub', tin, bit, pin, ch)
    final_cost = cost[L.final].get(T.final)
    if final_cost is None:
        return None
    steps: List[Step] = []
    u, s = L.final, T.final
    while (u, s) != (0, 0):
        pu, ps, op, tin, bit, pin, ch = back[u][s]
        steps.append(Step(op, tin, bit, pin, ch))
        u, s = pu, ps
    steps.reverse()
    return final_cost, steps

# -*- coding: utf-8 -*-
"""
Arudi (prosodic) reading of Arabic text.

Turns a (preferably fully diacritized) hemistich into a *lattice*: a list of
slots, one per written letter, each holding one or more pronunciation options.
Each option is a short string of prosodic bits:
    '1' = mutaharrik (moving letter)      shown as  /
    '0' = sakin      (still letter)       shown as  0
Ambiguities are kept as alternatives instead of being resolved early, e.g.
  * the last letter of a hemistich written without a mark  -> "10" (ishba') or "0" (sukun)
  * a letter without any diacritic                          -> "1" or "0"
  * an undiacritized word ending                             -> "1", "0" or "10" (tanwin)
  * pronoun ha after a moving letter (lahu / lahū)            -> "10" or "1"
  * meem al-jam' (hum / humū)                                 -> "0" or "10"
The meter matcher later picks the reading that fits the meter best, and the
report tells the poet which readings were assumed.
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

FATHA, DAMMA, KASRA = 'َ', 'ُ', 'ِ'
SUKUN, SHADDA = 'ْ', 'ّ'
FATHATAN, DAMMATAN, KASRATAN = 'ً', 'ٌ', 'ٍ'
DAGGER, MADDA_MARK, HAMZA_ABOVE, HAMZA_BELOW = 'ٰ', 'ٓ', 'ٔ', 'ٕ'
TATWEEL, ALEF_WASLA = 'ـ', 'ٱ'
VOWEL_OF = {FATHA: 'a', DAMMA: 'u', KASRA: 'i'}
TANWIN_OF = {FATHATAN: 'a', DAMMATAN: 'u', KASRATAN: 'i'}
MADD_LETTER = {'a': 'ا', 'u': 'و', 'i': 'ي'}
LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءأإآؤئىة') | {ALEF_WASLA}
SUN_LETTERS = set('تثدذرزسشصضطظلن')
ALEFS = {'ا', ALEF_WASLA}
NORMALIZE = {'ک': 'ك', 'ی': 'ي', 'ۀ': 'ه', 'ہ': 'ه', 'ے': 'ي', 'ىٰ': 'ى'}


@dataclass
class Unit:
    letter: str
    vowel: Optional[str] = None      # a / u / i
    tanwin: Optional[str] = None     # a / u / i
    sukun: bool = False
    shadda: bool = False
    dagger: bool = False

    @property
    def marked(self):
        return bool(self.vowel or self.tanwin or self.sukun or self.shadda or self.dagger)


@dataclass
class Opt:
    bits: str
    disp: List[str]
    cost: float = 0.0
    note: Optional[str] = None


@dataclass
class Slot:
    w: int                 # word index in hemistich
    i: int                 # letter index in word
    letter: str
    kind: str              # cons_v, cons_tan, cons_o, shadda, madd, unk, unk_end, wasl, silent, hamza_madd, ha, meem
    opts: List[Opt] = field(default_factory=list)
    vowel: Optional[str] = None

    def fixed(self, bits, disp, note=None):
        self.opts = [Opt(bits, disp, 0.0, note)]


# ----------------------------------------------------------------------------
# parsing
# ----------------------------------------------------------------------------

def clean(text: str) -> str:
    for a, b in NORMALIZE.items():
        text = text.replace(a, b)
    text = text.replace(TATWEEL, '')
    text = re.sub(r'\s+([\u064b-\u0652\u0670\u0653-\u0655])', r'\1', text)   # a mark typed after a space belongs to the previous letter
    text = text.replace('آ', 'آ')
    out = []
    for ch in text:
        if ch in LETTERS or ch in VOWEL_OF or ch in TANWIN_OF or ch in (SUKUN, SHADDA, DAGGER, MADDA_MARK, HAMZA_ABOVE, HAMZA_BELOW):
            out.append(ch)
        elif ch.isspace():
            out.append(' ')
        else:
            out.append(' ')
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


def parse_word(word: str) -> List[Unit]:
    units: List[Unit] = []
    for ch in word:
        if ch in LETTERS:
            units.append(Unit(ch))
        elif not units:
            continue
        elif ch in VOWEL_OF:
            units[-1].vowel = VOWEL_OF[ch]
        elif ch in TANWIN_OF:
            units[-1].tanwin = TANWIN_OF[ch]
        elif ch == SUKUN:
            units[-1].sukun = True
        elif ch == SHADDA:
            units[-1].shadda = True
        elif ch == DAGGER:
            units[-1].dagger = True
        elif ch == MADDA_MARK and units[-1].letter == 'ا':
            units[-1].letter = 'آ'
        elif ch == HAMZA_ABOVE and units[-1].letter == 'ا':
            units[-1].letter = 'أ'
        elif ch == HAMZA_BELOW and units[-1].letter == 'ا':
            units[-1].letter = 'إ'
    # tanwin al-fath written on the alef: "كتابًا" sometimes typed as  ب ا ً
    for k in range(1, len(units)):
        u = units[k]
        if u.letter == 'ا' and u.tanwin and not units[k - 1].tanwin:
            units[k - 1].tanwin, u.tanwin = u.tanwin, None
    return units


def skeleton(units: List[Unit]) -> str:
    s = ''.join(u.letter for u in units)
    return s.replace('أ', 'ا').replace('إ', 'ا').replace(ALEF_WASLA, 'ا')


# Words whose written form differs from their pronunciation.
SPECIAL = {
    'هذا': 'هَاذَا', 'هذه': 'هَاذِهِ', 'هذي': 'هَاذِي', 'هذان': 'هَاذَانِ', 'هذين': 'هَاذَيْنِ',
    'هؤلاء': 'هَاؤُلَاءِ', 'هكذا': 'هَاكَذَا', 'ههنا': 'هَاهُنَا',
    'ذلك': 'ذَالِكَ', 'ذلكم': 'ذَالِكُمْ', 'ذلكما': 'ذَالِكُمَا',
    'لكن': 'لَاكِنْ', 'لكنما': 'لَاكِنَّمَا', 'لكنه': 'لَاكِنَّهُ', 'لكنها': 'لَاكِنَّهَا', 'لكني': 'لَاكِنَّنِي',
    'اولئك': 'أُلَائِكَ', 'اولو': 'أُلُو', 'اولي': 'أُلِي', 'اولات': 'أُلَاتُ',
    'الرحمن': 'الرَّحْمَانُ', 'رحمن': 'رَحْمَانُ', 'عمرو': 'عَمْرُ', 'داود': 'دَاوُودُ', 'طاوس': 'طَاوُوسُ',
    'السموات': 'السَّمَاوَاتُ', 'سموات': 'سَمَاوَاتُ',
    'مائة': 'مِئَة', 'مائتان': 'مِئَتَانِ', 'مائتين': 'مِئَتَيْنِ', 'ذلكن': 'ذَالِكُنَّ', 'اولاء': 'أُلَاءِ',
    'هاتان': 'هَاتَانِ', 'لكنك': 'لَاكِنَّكَ', 'لكنكم': 'لَاكِنَّكُمْ', 'لكننا': 'لَاكِنَّنَا', 'لكنهم': 'لَاكِنَّهُمْ',
}
PREFIX_LETTERS = set('وفبكل')


def rewrite_special(units: List[Unit]) -> List[Unit]:
    if not units or any(u.dagger for u in units):
        return units
    s = skeleton(units)
    for k in range(0, 3):
        if k and not all(c in PREFIX_LETTERS | {'ت'} for c in s[:k]):
            break
        rest = s[k:]
        last = units[-1]
        if rest in ('الله', 'اللهم'):
            if 'ت' in s[:k] and s[:k] != 'ت':
                break
            new = [Unit('ا'), Unit('ل', sukun=True), Unit('ل', vowel='a'), Unit('ا'),
                   Unit('ه', vowel=units[k + 3].vowel if len(units) > k + 3 else None,
                        sukun=units[k + 3].sukun if len(units) > k + 3 else False)]
            if rest == 'اللهم':
                new[-1].vowel = 'u'
                new.append(Unit('م', vowel=last.vowel, sukun=last.sukun, shadda=True))
            return units[:k] + new
        if rest == 'لله':
            hu = units[-1]
            new = [Unit('ل', vowel='i'), Unit('ل', sukun=True), Unit('ل', vowel='a'), Unit('ا'),
                   Unit('ه', vowel=hu.vowel, sukun=hu.sukun)]
            return units[:k] + new
        if 'ت' in s[:k]:
            continue
        if rest in SPECIAL:
            new = parse_word(SPECIAL[rest])
            if rest == 'لكن' and last.shadda:
                new = parse_word('لَاكِنَّ')
            if last.marked:  # keep the poet's case ending
                new[-1].vowel, new[-1].tanwin, new[-1].sukun = last.vowel, last.tanwin, last.sukun
                new[-1].shadda = new[-1].shadda or last.shadda
            return units[:k] + new
    return units


# ----------------------------------------------------------------------------
# lattice construction
# ----------------------------------------------------------------------------

def _is_article(units, k):
    """units[k] is the ل of the definite article?"""
    if units[k].letter != 'ل' or units[k].vowel or units[k].tanwin or units[k].shadda:
        return False
    if k + 1 >= len(units):
        return False
    if k == 1 and units[0].letter in ALEFS:
        return True
    if k == 2 and units[1].letter in ALEFS and units[0].letter in PREFIX_LETTERS:
        return True
    if k == 1 and units[0].letter == 'ل' and len(units) > 3:  # لِلْ / للشمس
        return True
    return False


def build_word_slots(units: List[Unit], wi: int, first_in_hemistich: bool):
    """Return (slots, starts_with_wasl_index or None)."""
    n = len(units)
    slots: List[Slot] = []
    wasl_slot = None
    force_double = set()
    has_article = any(_is_article(units, k) for k in range(n))
    for k, u in enumerate(units):
        L = u.letter
        prev = units[k - 1] if k else None
        nxt = units[k + 1] if k + 1 < n else None
        word_initial = k == 0
        s = Slot(wi, k, L, 'unk')
        s.vowel = u.vowel or u.tanwin

        # ---- article lam --------------------------------------------------
        if _is_article(units, k):
            if nxt.shadda:
                s.kind = 'silent'; s.fixed('', [], None)
            elif nxt.letter in SUN_LETTERS and not nxt.sukun:
                s.kind = 'silent'; s.fixed('', [], None)
                force_double.add(k + 1)
            else:
                s.kind = 'cons_o'; s.fixed('0', ['ل'])
            slots.append(s); continue

        # ---- alefs --------------------------------------------------------
        if L in ALEFS:
            nxt_sakin = nxt is not None and (nxt.sukun or _is_article(units, k + 1) or
                                             (nxt.letter == 'ل' and k + 2 < n and units[k + 2].shadda and not nxt.vowel) or
                                             (nxt.letter == 'ل' and nxt.shadda))   # الَّذِي / الَّتِي / اللَّهُ
            if k == 1 and units[0].letter in PREFIX_LETTERS and nxt_sakin:
                # وَالْ / فَاسْمَعْ : wasl alef after a prefix is never pronounced
                s.kind = 'silent'; s.fixed('', []); slots.append(s); continue
            if word_initial:
                if u.vowel and not nxt_sakin:
                    s.kind = 'cons_v'; s.fixed('1', ['أ'])
                elif nxt_sakin or (nxt is not None and _is_article(units, k + 1)):
                    s.kind = 'wasl'
                    wasl_slot = len(slots)
                    s.fixed('1', ['أ'], 'همزة وصل منطوقة في أول الشطر')
                else:
                    s.kind = 'cons_v'; s.fixed('1', ['أ'], 'ألف أول الكلمة عُدّت همزة قطع')
                slots.append(s); continue
            if prev is not None and prev.tanwin == 'a':
                s.kind = 'silent'; s.fixed('', []); slots.append(s); continue
            if k == n - 1 and prev is not None and prev.letter == 'و' and not prev.vowel and n >= 3:
                s.kind = 'silent'; s.fixed('', []); slots.append(s); continue  # alef fariqa (كتبوا)
            s.kind = 'madd'; s.fixed('0', ['ا']); slots.append(s); continue

        if L == 'آ':
            s.kind = 'hamza_madd'; s.fixed('10', ['ء', 'ا']); slots.append(s); continue

        if L == 'ى':
            if prev is not None and prev.tanwin:
                s.kind = 'silent'; s.fixed('', [])
            else:
                s.kind = 'madd'; s.fixed('0', ['ى'])
            slots.append(s); continue

        # ---- waw / ya -----------------------------------------------------
        if L in 'وي' and not u.vowel and not u.tanwin and not u.shadda:
            match = 'u' if L == 'و' else 'i'
            if prev is None:
                s.kind = 'cons_v'; s.fixed('1', [L])
            elif u.sukun:
                s.kind = 'madd' if prev.vowel == match else 'cons_o'
                s.fixed('0', [L])
            elif prev.vowel == match:
                s.kind = 'madd'; s.fixed('0', [L])
            elif prev.vowel == 'a' or prev.sukun:
                s.kind = 'unk'
                s.opts = [Opt('0', [L], 0.05, f'«{L}» ساكنة'), Opt('1', [L], 0.1, f'«{L}» متحركة')]
            else:
                s.kind = 'unk'
                s.opts = [Opt('0', [L], 0.0, None), Opt('1', [L], 0.3, f'«{L}» متحركة')]
            slots.append(s); continue

        # ---- general consonant (incl. hamzas, ة, و/ي with marks) -------------
        disp = 'ه' if (L == 'ة' and u.sukun) else ('ت' if L == 'ة' else L)
        pre_bits, pre_disp = '', []
        if u.shadda or k in force_double:
            pre_bits, pre_disp = '0', [disp]
        if u.dagger:
            s.kind = 'cons_v'; s.fixed(pre_bits + '10', pre_disp + [disp, 'ا'])
        elif u.tanwin:
            s.kind = 'cons_tan'; s.fixed(pre_bits + '10', pre_disp + [disp, 'ن'])
        elif u.vowel:
            s.kind = 'cons_v' if not pre_bits else 'shadda'
            s.fixed(pre_bits + '1', pre_disp + [disp])
        elif u.sukun:
            s.kind = 'cons_o'; s.fixed('0', [disp])
        elif u.shadda or k in force_double:
            s.kind = 'shadda'; s.fixed(pre_bits + '1', pre_disp + [disp])
        elif word_initial or (L in 'إ'):
            s.kind = 'cons_v'; s.fixed('1', [disp])
        elif k == n - 1:
            s.kind = 'unk_end'
            s.opts = [Opt('1', [disp], 0.05, 'حركة إعراب مقدّرة'),
                      Opt('0', [disp], 0.05, 'سكون آخر الكلمة')]
            if not has_article:
                s.opts.append(Opt('10', [disp, 'ن'], 0.15, 'تنوين مقدّر'))
        else:
            s.kind = 'unk'
            s.opts = [Opt('1', [disp], 0.05, f'«{disp}» متحركة'), Opt('0', [disp], 0.05, f'«{disp}» ساكنة')]
        slots.append(s)

    # ---- pronoun ha / meem al-jam' / أنا -----------------------------------
    if n >= 2:
        last, before = units[-1], units[-2]
        sl = slots[-1]
        before_slot = slots[-2]
        before_moving = before_slot.kind in ('cons_v', 'shadda') or (before.vowel is not None)
        if last.letter == 'ه' and last.vowel in ('u', 'i') and not last.tanwin and not last.shadda:
            if skeleton(units)[-3:] != 'لله' and not skeleton(units).endswith('الله'):
                v = last.vowel
                if before_moving:
                    sl.kind = 'ha'
                    sl.opts = [Opt('10', ['ه', MADD_LETTER[v]], 0.0, None),
                               Opt('1', ['ه'], 0.25, 'هاء الضمير غير مشبعة')]
                else:
                    sl.kind = 'ha'
                    sl.opts = [Opt('1', ['ه'], 0.0, None),
                               Opt('10', ['ه', MADD_LETTER[v]], 0.4, 'إشباع هاء الضمير بعد ساكن (ضرورة)')]
        if last.letter == 'م' and (last.sukun or not last.marked) and before.letter in 'هكت' and before.vowel == 'u':
            sl.kind = 'meem'
            sl.opts = [Opt('0', ['م'], 0.0, None), Opt('10', ['م', 'و'], 0.25, 'إشباع ميم الجمع (ـمُو)')]
        if skeleton(units) in ('انا', 'وانا', 'فانا') and sl.kind == 'madd':
            sl.kind = 'ana'
            sl.opts = [Opt('', [], 0.1, 'ألف «أنا» محذوفة لفظًا'), Opt('0', ['ا'], 0.1, 'ألف «أنا» منطوقة')]
    return slots, wasl_slot


def build_hemistich(text: str) -> List[Slot]:
    words = [rewrite_special(parse_word(w)) for w in clean(text).split(' ') if w]
    words = [w for w in words if w]
    all_slots: List[Slot] = []
    word_ranges = []
    for wi, units in enumerate(words):
        slots, wasl = build_word_slots(units, wi, wi == 0)
        if wasl is not None and wi > 0:
            slots[wasl].kind = 'silent'
            slots[wasl].fixed('', [])
            _join_to_wasl(all_slots, article=any(_is_article(units, k) for k in range(len(units))))
        word_ranges.append((len(all_slots), len(all_slots) + len(slots)))
        all_slots.extend(slots)
    if not all_slots:
        return all_slots
    _apply_end(all_slots)
    _constrain(all_slots)
    return all_slots


def _last_pronounced(slots):
    for k in range(len(slots) - 1, -1, -1):
        if slots[k].kind != 'silent':
            return k
    return None


QAT_COST = 0.35          # قطع همزة الوصل: a poetic licence, chosen only when it saves the meter


def _join_to_wasl(slots, article=False):
    """Previous word meets a hamzat wasl followed by sakin (iltiqa' as-sakinayn).
    The standard reading drops the wasl and moves/drops the preceding sakin; the licence
    قطع همزة الوصل (pronouncing it as a full hamza) is kept as a costlier alternative."""
    k = _last_pronounced(slots)
    if k is None:
        return
    s = slots[k]
    orig = [Opt(o.bits, list(o.disp), o.cost, o.note) for o in s.opts]
    orig_kind = s.kind
    if s.kind in ('madd', 'ana'):
        s.kind = 'silent'; s.fixed('', [], 'حُذف حرف المد لالتقاء الساكنين')
    elif s.kind == 'cons_tan':
        o = s.opts[0]
        s.fixed(o.bits[:-1] + '1', o.disp, 'تحريك نون التنوين لالتقاء الساكنين')
    elif s.kind in ('cons_o', 'unk', 'unk_end', 'meem'):
        s.kind = 'cons_v'; s.fixed('1', [s.opts[0].disp[0]], 'حُرّك الساكن لالتقاء الساكنين')
    elif s.kind == 'ha':
        s.fixed('1', ['ه'])
    if orig_kind in ('madd', 'ana', 'cons_tan', 'cons_o', 'unk', 'unk_end', 'meem', 'ha'):
        note = 'قطع همزة الوصل (ضرورة شعرية)'
        cost = QAT_COST + (0.2 if article else 0.0)
        s.opts = list(s.opts) + [Opt(o.bits + '1', o.disp + ['ء'], o.cost + cost, note) for o in orig if o.cost <= 0.1]
        if s.kind == 'silent':
            s.kind = 'wasl_join'


def _apply_end(slots):
    """Last letter of a hemistich: the vowel is lengthened (ishba') or the letter is sakin."""
    k = _last_pronounced(slots)
    s = slots[k]
    d = s.opts[0].disp
    if s.kind == 'cons_v':
        o = s.opts[0]
        vowel_letter = MADD_LETTER.get(s.vowel or 'a', 'ا')
        s.opts = [Opt(o.bits + '0', o.disp + [vowel_letter], 0.0, None)]
        s.kind = 'end_v'
    elif s.kind == 'shadda':
        o = s.opts[0]
        s.opts = [Opt(o.bits + '0', o.disp + [MADD_LETTER.get(s.vowel or 'a', 'ا')], 0.0, None)]
    elif s.kind == 'cons_tan':
        o = s.opts[0]
        s.opts = [Opt(o.bits, o.disp, 0.0, None)]
    elif s.kind == 'ha':
        s.opts = [Opt('10', ['ه', MADD_LETTER.get(s.vowel or 'u', 'و')], 0.0, None)]
    elif s.kind == 'meem':
        s.opts = [Opt('0', ['م'], 0.0, 'ميم ساكنة في آخر الشطر'), Opt('10', ['م', 'و'], 0.05, 'ميم مشبعة (ـمُو)')]
    elif s.kind in ('unk', 'unk_end'):
        dd = d[0]
        s.kind = 'end_amb'
        s.opts = [Opt('10', [dd, 'ـ'], 0.03, 'آخر الشطر: حركة مشبعة (إطلاق)'),
                  Opt('0', [dd], 0.08, 'آخر الشطر: سكون')]
    elif s.kind == 'ana':
        s.fixed('0', ['ا'])


def _constrain(slots):
    """Simple phonotactic pruning of ambiguous slots."""
    pron = [k for k, s in enumerate(slots) if s.kind != 'silent']
    for idx, k in enumerate(pron):
        s = slots[k]
        if s.kind not in ('unk', 'unk_end') or len(s.opts) < 2:
            continue
        nxt = slots[pron[idx + 1]] if idx + 1 < len(pron) else None
        prv = slots[pron[idx - 1]] if idx else None
        if nxt is not None and nxt.kind == 'madd' and nxt.w == s.w:
            s.opts = [o for o in s.opts if o.bits == '1'] or s.opts
            continue
        if prv is not None and all(o.bits.endswith('0') for o in prv.opts) and prv.w == s.w:
            s.opts = [o for o in s.opts if o.bits.startswith('1')] or s.opts


def describe(slots) -> str:
    """Default (lowest cost) arudi writing and pattern, for quick display."""
    txt, bits = [], []
    cur_w = 0
    for s in slots:
        if s.w != cur_w:
            cur_w = s.w
        o = min(s.opts, key=lambda o: o.cost)
        txt.extend(o.disp)
        bits.append(o.bits)
    return ''.join(txt), ''.join(bits)


def ambiguity_count(slots) -> int:
    n = 1
    for s in slots:
        n *= len(s.opts)
    return n

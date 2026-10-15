/* Arabic prosody engine — browser port of scripts/arud (lattice, aligner, classical, free verse).
   Meter tables come from meters.json (generated from meters.py). Keep the two in step:
   tests/parity.js compares this engine with the Python one on the gold verses. */
(function (root) {
  'use strict';
  const FATHA = 'َ', DAMMA = 'ُ', KASRA = 'ِ', SUKUN = 'ْ', SHADDA = 'ّ';
  const FATHATAN = 'ً', DAMMATAN = 'ٌ', KASRATAN = 'ٍ', DAGGER = 'ٰ';
  const MADDA_MARK = 'ٓ', HAMZA_ABOVE = 'ٔ', HAMZA_BELOW = 'ٕ', TATWEEL = 'ـ', ALEF_WASLA = 'ٱ';
  const VOWEL_OF = { [FATHA]: 'a', [DAMMA]: 'u', [KASRA]: 'i' };
  const TANWIN_OF = { [FATHATAN]: 'a', [DAMMATAN]: 'u', [KASRATAN]: 'i' };
  const MADD_LETTER = { a: 'ا', u: 'و', i: 'ي' };
  const LETTERS = new Set([...'ابتثجحخدذرزسشصضطظعغفقكلمنهويءأإآؤئىة', ALEF_WASLA]);
  const SUN = new Set([...'تثدذرزسشصضطظلن']);
  const ALEFS = new Set(['ا', ALEF_WASLA]);
  const PREFIX = new Set([...'وفبكل']);
  const MARKS = new Set([FATHA, DAMMA, KASRA, SUKUN, SHADDA, FATHATAN, DAMMATAN, KASRATAN, DAGGER, MADDA_MARK, HAMZA_ABOVE, HAMZA_BELOW]);
  const INF = Infinity, INS = 1, DEL = 1, SUB = 1;

  let M = null; // meter data
  function load(data) { M = data; TEMPL.clear(); }

  // ------------------------------------------------------------------ text
  function clean(text) {
    text = text.replace(/\s+([\u064b-\u0652\u0670\u0653-\u0655])/g, '$1');
    text = text.replace(/ک/g, 'ك').replace(/ی/g, 'ي').replace(/[ۀہ]/g, 'ه').replace(/ے/g, 'ي').split(TATWEEL).join('');
    let out = '';
    for (const ch of text) out += (LETTERS.has(ch) || MARKS.has(ch)) ? ch : ' ';
    return out.replace(/\s+/g, ' ').trim();
  }
  const unit = (letter, o = {}) => Object.assign({ letter, vowel: null, tanwin: null, sukun: false, shadda: false, dagger: false }, o);
  const marked = u => !!(u.vowel || u.tanwin || u.sukun || u.shadda || u.dagger);

  function parseWord(word) {
    const units = [];
    for (const ch of word) {
      if (LETTERS.has(ch)) { units.push(unit(ch)); continue; }
      if (!units.length) continue;
      const u = units[units.length - 1];
      if (VOWEL_OF[ch]) u.vowel = VOWEL_OF[ch];
      else if (TANWIN_OF[ch]) u.tanwin = TANWIN_OF[ch];
      else if (ch === SUKUN) u.sukun = true;
      else if (ch === SHADDA) u.shadda = true;
      else if (ch === DAGGER) u.dagger = true;
      else if (ch === MADDA_MARK && u.letter === 'ا') u.letter = 'آ';
      else if (ch === HAMZA_ABOVE && u.letter === 'ا') u.letter = 'أ';
      else if (ch === HAMZA_BELOW && u.letter === 'ا') u.letter = 'إ';
    }
    for (let k = 1; k < units.length; k++) {
      const u = units[k];
      if (u.letter === 'ا' && u.tanwin && !units[k - 1].tanwin) { units[k - 1].tanwin = u.tanwin; u.tanwin = null; }
    }
    return units;
  }
  const skeleton = units => units.map(u => u.letter).join('').replace(/[أإٱ]/g, 'ا');

  const SPECIAL = {
    'هذا': 'هَاذَا', 'هذه': 'هَاذِهِ', 'هذي': 'هَاذِي', 'هذان': 'هَاذَانِ', 'هذين': 'هَاذَيْنِ',
    'هؤلاء': 'هَاؤُلَاءِ', 'هكذا': 'هَاكَذَا', 'ههنا': 'هَاهُنَا',
    'ذلك': 'ذَالِكَ', 'ذلكم': 'ذَالِكُمْ', 'ذلكما': 'ذَالِكُمَا',
    'لكن': 'لَاكِنْ', 'لكنما': 'لَاكِنَّمَا', 'لكنه': 'لَاكِنَّهُ', 'لكنها': 'لَاكِنَّهَا', 'لكني': 'لَاكِنَّنِي',
    'اولئك': 'أُلَائِكَ', 'اولو': 'أُلُو', 'اولي': 'أُلِي', 'اولات': 'أُلَاتُ',
    'الرحمن': 'الرَّحْمَانُ', 'رحمن': 'رَحْمَانُ', 'عمرو': 'عَمْرُ', 'داود': 'دَاوُودُ', 'طاوس': 'طَاوُوسُ',
    'السموات': 'السَّمَاوَاتُ', 'سموات': 'سَمَاوَاتُ',
  };

  function rewriteSpecial(units) {
    if (!units.length || units.some(u => u.dagger)) return units;
    const s = skeleton(units);
    for (let k = 0; k < 3; k++) {
      const pre = s.slice(0, k);
      if (k && ![...pre].every(c => PREFIX.has(c) || c === 'ت')) break;
      const rest = s.slice(k), last = units[units.length - 1];
      if (rest === 'الله' || rest === 'اللهم') {
        if (pre.includes('ت') && pre !== 'ت') break;
        const h = units[k + 3];
        const nw = [unit('ا'), unit('ل', { sukun: true }), unit('ل', { vowel: 'a' }), unit('ا'),
          unit('ه', { vowel: h ? h.vowel : null, sukun: h ? h.sukun : false })];
        if (rest === 'اللهم') { nw[4].vowel = 'u'; nw.push(unit('م', { vowel: last.vowel, sukun: last.sukun, shadda: true })); }
        return units.slice(0, k).concat(nw);
      }
      if (rest === 'لله') {
        const hu = units[units.length - 1];
        return units.slice(0, k).concat([unit('ل', { vowel: 'i' }), unit('ل', { sukun: true }), unit('ل', { vowel: 'a' }), unit('ا'),
          unit('ه', { vowel: hu.vowel, sukun: hu.sukun })]);
      }
      if (pre.includes('ت')) continue;
      if (SPECIAL[rest]) {
        let nw = parseWord(SPECIAL[rest]);
        if (rest === 'لكن' && last.shadda) nw = parseWord('لَاكِنَّ');
        if (marked(last)) {
          const z = nw[nw.length - 1];
          z.vowel = last.vowel; z.tanwin = last.tanwin; z.sukun = last.sukun; z.shadda = z.shadda || last.shadda;
        }
        return units.slice(0, k).concat(nw);
      }
    }
    return units;
  }

  // ------------------------------------------------------------------ lattice
  const opt = (bits, disp, cost = 0, note = null) => ({ bits, disp, cost, note });
  function isArticle(units, k) {
    const u = units[k];
    if (u.letter !== 'ل' || u.vowel || u.tanwin || u.shadda) return false;
    if (k + 1 >= units.length) return false;
    if (k === 1 && ALEFS.has(units[0].letter)) return true;
    if (k === 2 && ALEFS.has(units[1].letter) && PREFIX.has(units[0].letter)) return true;
    if (k === 1 && units[0].letter === 'ل' && units.length > 3) return true;
    return false;
  }

  function buildWordSlots(units, wi) {
    const n = units.length, slots = [], forceDouble = new Set();
    let waslSlot = null;
    let hasArticle = false;
    for (let k = 0; k < n; k++) if (isArticle(units, k)) hasArticle = true;
    for (let k = 0; k < n; k++) {
      const u = units[k], L = u.letter, prev = k ? units[k - 1] : null, nxt = k + 1 < n ? units[k + 1] : null;
      const s = { w: wi, i: k, letter: L, kind: 'unk', opts: [], vowel: u.vowel || u.tanwin };
      const fixed = (bits, disp, note = null) => { s.opts = [opt(bits, disp, 0, note)]; };
      if (isArticle(units, k)) {
        if (nxt.shadda) { s.kind = 'silent'; fixed('', []); }
        else if (SUN.has(nxt.letter) && !nxt.sukun) { s.kind = 'silent'; fixed('', []); forceDouble.add(k + 1); }
        else { s.kind = 'cons_o'; fixed('0', ['ل']); }
        slots.push(s); continue;
      }
      if (ALEFS.has(L)) {
        const nxtSakin = nxt !== null && (nxt.sukun || isArticle(units, k + 1) ||
          (nxt.letter === 'ل' && k + 2 < n && units[k + 2].shadda && !nxt.vowel) || (nxt.letter === 'ل' && nxt.shadda));
        if (k === 1 && PREFIX.has(units[0].letter) && nxtSakin) { s.kind = 'silent'; fixed('', []); slots.push(s); continue; }
        if (k === 0) {
          if (u.vowel && !nxtSakin) { s.kind = 'cons_v'; fixed('1', ['أ']); }
          else if (nxtSakin || (nxt && isArticle(units, k + 1))) { s.kind = 'wasl'; waslSlot = slots.length; fixed('1', ['أ'], 'همزة وصل منطوقة في أول الشطر'); }
          else { s.kind = 'cons_v'; fixed('1', ['أ'], 'ألف أول الكلمة عُدّت همزة قطع'); }
          slots.push(s); continue;
        }
        if (prev && prev.tanwin === 'a') { s.kind = 'silent'; fixed('', []); slots.push(s); continue; }
        if (k === n - 1 && prev && prev.letter === 'و' && !prev.vowel && n >= 3) { s.kind = 'silent'; fixed('', []); slots.push(s); continue; }
        if (nxtSakin) { s.kind = 'silent'; fixed('', []); slots.push(s); continue; }
        s.kind = 'madd'; fixed('0', ['ا']); slots.push(s); continue;
      }
      if (L === 'آ') { s.kind = 'hamza_madd'; fixed('10', ['ء', 'ا']); slots.push(s); continue; }
      if (L === 'ى') {
        if (prev && prev.tanwin) { s.kind = 'silent'; fixed('', []); } else { s.kind = 'madd'; fixed('0', ['ى']); }
        slots.push(s); continue;
      }
      if ((L === 'و' || L === 'ي') && !u.vowel && !u.tanwin && !u.shadda) {
        const match = L === 'و' ? 'u' : 'i';
        if (!prev) { s.kind = 'cons_v'; fixed('1', [L]); }
        else if (u.sukun) { s.kind = prev.vowel === match ? 'madd' : 'cons_o'; fixed('0', [L]); }
        else if (prev.vowel === match) { s.kind = 'madd'; fixed('0', [L]); }
        else if (prev.vowel === 'a' || prev.sukun) { s.kind = 'unk'; s.opts = [opt('0', [L], 0.05, `«${L}» ساكنة`), opt('1', [L], 0.1, `«${L}» متحركة`)]; }
        else { s.kind = 'unk'; s.opts = [opt('0', [L], 0), opt('1', [L], 0.3, `«${L}» متحركة`)]; }
        slots.push(s); continue;
      }
      const disp = (L === 'ة' && u.sukun) ? 'ه' : (L === 'ة' ? 'ت' : L);
      let preB = '', preD = [];
      if (u.shadda || forceDouble.has(k)) { preB = '0'; preD = [disp]; }
      if (u.dagger) { s.kind = 'cons_v'; fixed(preB + '10', preD.concat([disp, 'ا'])); }
      else if (u.tanwin) { s.kind = 'cons_tan'; fixed(preB + '10', preD.concat([disp, 'ن'])); }
      else if (u.vowel) { s.kind = preB ? 'shadda' : 'cons_v'; fixed(preB + '1', preD.concat([disp])); }
      else if (u.sukun) { s.kind = 'cons_o'; fixed('0', [disp]); }
      else if (u.shadda || forceDouble.has(k)) { s.kind = 'shadda'; fixed(preB + '1', preD.concat([disp])); }
      else if (k === 0 || L === 'إ') { s.kind = 'cons_v'; fixed('1', [disp]); }
      else if (k === n - 1) {
        s.kind = 'unk_end';
        s.opts = [opt('1', [disp], 0.05, 'حركة إعراب مقدّرة'), opt('0', [disp], 0.05, 'سكون آخر الكلمة')];
        if (!hasArticle) s.opts.push(opt('10', [disp, 'ن'], 0.15, 'تنوين مقدّر'));
      } else { s.kind = 'unk'; s.opts = [opt('1', [disp], 0.05, `«${disp}» متحركة`), opt('0', [disp], 0.05, `«${disp}» ساكنة`)]; }
      slots.push(s);
    }
    if (n >= 2) {
      const last = units[n - 1], before = units[n - 2], sl = slots[n - 1], bs = slots[n - 2];
      const beforeMoving = bs.kind === 'cons_v' || bs.kind === 'shadda' || before.vowel !== null;
      const sk = skeleton(units);
      if (last.letter === 'ه' && (last.vowel === 'u' || last.vowel === 'i') && !last.tanwin && !last.shadda) {
        if (sk.slice(-3) !== 'لله' && !sk.endsWith('الله')) {
          sl.kind = 'ha';
          sl.opts = beforeMoving
            ? [opt('10', ['ه', MADD_LETTER[last.vowel]], 0), opt('1', ['ه'], 0.25, 'هاء الضمير غير مشبعة')]
            : [opt('1', ['ه'], 0), opt('10', ['ه', MADD_LETTER[last.vowel]], 0.4, 'إشباع هاء الضمير بعد ساكن (ضرورة)')];
        }
      }
      if (last.letter === 'م' && (last.sukun || !marked(last)) && 'هكت'.includes(before.letter) && before.vowel === 'u') {
        sl.kind = 'meem'; sl.opts = [opt('0', ['م'], 0), opt('10', ['م', 'و'], 0.25, 'إشباع ميم الجمع (ـمُو)')];
      }
      if (['انا', 'وانا', 'فانا'].includes(sk) && sl.kind === 'madd') {
        sl.kind = 'ana'; sl.opts = [opt('', [], 0.1, 'ألف «أنا» محذوفة لفظًا'), opt('0', ['ا'], 0.1, 'ألف «أنا» منطوقة')];
      }
    }
    return [slots, waslSlot];
  }

  function lastPronounced(slots) { for (let k = slots.length - 1; k >= 0; k--) if (slots[k].kind !== 'silent') return k; return null; }

  function joinToWasl(slots) {
    const k = lastPronounced(slots); if (k === null) return;
    const s = slots[k];
    if (s.kind === 'madd' || s.kind === 'ana') { s.kind = 'silent'; s.opts = [opt('', [], 0, 'حُذف حرف المد لالتقاء الساكنين')]; }
    else if (s.kind === 'cons_tan') { const o = s.opts[0]; s.opts = [opt(o.bits.slice(0, -1) + '1', o.disp, 0, 'تحريك نون التنوين لالتقاء الساكنين')]; }
    else if (['cons_o', 'unk', 'unk_end', 'meem'].includes(s.kind)) { s.kind = 'cons_v'; s.opts = [opt('1', [s.opts[0].disp[0]], 0, 'حُرّك الساكن لالتقاء الساكنين')]; }
    else if (s.kind === 'ha') s.opts = [opt('1', ['ه'], 0)];
  }

  function applyEnd(slots) {
    const k = lastPronounced(slots); const s = slots[k]; const o = s.opts[0];
    const ml = MADD_LETTER[s.vowel || 'a'] || 'ا';
    if (s.kind === 'cons_v') { s.opts = [opt(o.bits + '0', o.disp.concat([ml]), 0)]; s.kind = 'end_v'; }
    else if (s.kind === 'shadda') s.opts = [opt(o.bits + '0', o.disp.concat([ml]), 0)];
    else if (s.kind === 'cons_tan') s.opts = [opt(o.bits, o.disp, 0)];
    else if (s.kind === 'ha') s.opts = [opt('10', ['ه', MADD_LETTER[s.vowel || 'u'] || 'و'], 0)];
    else if (s.kind === 'meem') s.opts = [opt('0', ['م'], 0, 'ميم ساكنة في آخر الشطر'), opt('10', ['م', 'و'], 0.05, 'ميم مشبعة (ـمُو)')];
    else if (s.kind === 'unk' || s.kind === 'unk_end') {
      const dd = o.disp[0]; s.kind = 'end_amb';
      s.opts = [opt('10', [dd, 'ـ'], 0.03, 'آخر الشطر: حركة مشبعة (إطلاق)'), opt('0', [dd], 0.08, 'آخر الشطر: سكون')];
    } else if (s.kind === 'ana') s.opts = [opt('0', ['ا'], 0)];
  }

  function constrain(slots) {
    const pron = []; slots.forEach((s, k) => { if (s.kind !== 'silent') pron.push(k); });
    pron.forEach((k, idx) => {
      const s = slots[k];
      if ((s.kind !== 'unk' && s.kind !== 'unk_end') || s.opts.length < 2) return;
      const nxt = idx + 1 < pron.length ? slots[pron[idx + 1]] : null, prv = idx ? slots[pron[idx - 1]] : null;
      if (nxt && nxt.kind === 'madd' && nxt.w === s.w) { const f = s.opts.filter(o => o.bits === '1'); if (f.length) s.opts = f; return; }
      if (prv && prv.opts.every(o => o.bits.endsWith('0')) && prv.w === s.w) { const f = s.opts.filter(o => o.bits.startsWith('1')); if (f.length) s.opts = f; }
    });
  }

  function words(text) { return clean(text).split(' ').filter(Boolean); }

  function buildHemistich(text) {
    const ws = words(text).map(w => rewriteSpecial(parseWord(w))).filter(w => w.length);
    const all = [];
    ws.forEach((units, wi) => {
      const [slots, wasl] = buildWordSlots(units, wi);
      if (wasl !== null && wi > 0) { slots[wasl].kind = 'silent'; slots[wasl].opts = [opt('', [], 0)]; joinToWasl(all); }
      all.push(...slots);
    });
    if (!all.length) return all;
    applyEnd(all); constrain(all);
    return all;
  }

  // ------------------------------------------------------------------ graphs
  function latticeGraph(slots) {
    const out = [[]], slotStart = [];
    let node = 0;
    slots.forEach((s, k) => {
      slotStart.push(node);
      const chains = s.opts.map((o, j) => {
        const inter = [];
        for (let c = 0; c < Math.max(o.bits.length - 1, 0); c++) { out.push([]); inter.push(out.length - 1); }
        return [j, o, inter];
      });
      out.push([]); const nxt = out.length - 1;
      for (const [j, o, inter] of chains) {
        if (!o.bits) { out[node].push([nxt, null, o.cost, [k, j, -1]]); continue; }
        const seq = [node, ...inter, nxt];
        for (let c = 0; c < o.bits.length; c++) out[seq[c]].push([seq[c + 1], o.bits[c], c === 0 ? o.cost : 0, [k, j, c]]);
      }
      node = nxt;
    });
    const n = out.length, lo = new Array(n).fill(INF), hi = new Array(n).fill(-INF);
    lo[0] = hi[0] = 0;
    for (let u = 0; u < n; u++) {
      if (lo[u] === INF) continue;
      for (const [w, b] of out[u]) { const d = b === null ? 0 : 1; lo[w] = Math.min(lo[w], lo[u] + d); hi[w] = Math.max(hi[w], hi[u] + d); }
    }
    return { slots, out, slotStart, final: node, n, minLen: lo[node], maxLen: hi[node] };
  }

  function templateGraph(positions) {
    const out = [[]]; let node = 0;
    positions.forEach((variants, p) => {
      const chains = variants.map((v, vi) => {
        const inter = []; for (let c = 0; c < v[0].length - 1; c++) { out.push([]); inter.push(out.length - 1); }
        return [vi, v, inter];
      });
      out.push([]); const nxt = out.length - 1;
      for (const [vi, v, inter] of chains) {
        const seq = [node, ...inter, nxt];
        for (let c = 0; c < v[0].length; c++) out[seq[c]].push([seq[c + 1], v[0][c], c === 0 ? v[2] : 0, [p, vi, c]]);
      }
      node = nxt;
    });
    const minLen = positions.reduce((a, vs) => a + Math.min(...vs.map(v => v[0].length)), 0);
    const maxLen = positions.reduce((a, vs) => a + Math.max(...vs.map(v => v[0].length)), 0);
    return { positions, out, final: node, n: out.length, minLen, maxLen };
  }

  function align(L, T, cap = 4) {
    if (L.minLen - T.maxLen > cap || T.minLen - L.maxLen > cap) return null;
    const cost = [], back = [];
    for (let u = 0; u < L.n; u++) { cost.push(new Float64Array(T.n).fill(INF)); back.push(new Array(T.n)); }
    cost[0][0] = 0;
    for (let u = 0; u < L.n; u++) {
      const cu = cost[u], bu = back[u], lout = L.out[u];
      for (let s = 0; s < T.n; s++) {
        const c = cu[s]; if (c === INF || c > cap) continue;
        for (const [t, ch, ec, pin] of T.out[s]) { const nc = c + INS + ec; if (nc < cu[t]) { cu[t] = nc; bu[t] = [u, s, 'ins', null, null, pin, ch]; } }
        for (const [w, bit, lc, tin] of lout) {
          const cw = cost[w], bw = back[w];
          if (bit === null) { const nc = c + lc; if (nc < cw[s]) { cw[s] = nc; bw[s] = [u, s, 'eps', tin, null, null, null]; } continue; }
          let nc = c + lc + DEL; if (nc < cw[s]) { cw[s] = nc; bw[s] = [u, s, 'del', tin, bit, null, null]; }
          for (const [t, ch, ec, pin] of T.out[s]) {
            nc = c + lc + ec + (ch === bit ? 0 : SUB);
            if (nc < cw[t]) { cw[t] = nc; bw[t] = [u, s, ch === bit ? 'match' : 'sub', tin, bit, pin, ch]; }
          }
        }
      }
    }
    const fc = cost[L.final][T.final]; if (fc === INF) return null;
    const steps = []; let u = L.final, s = T.final;
    while (!(u === 0 && s === 0)) { const b = back[u][s]; steps.push({ op: b[2], tin: b[3], bit: b[4], pin: b[5], exp: b[6] }); u = b[0]; s = b[1]; }
    steps.reverse();
    return [fc, steps];
  }

  // ------------------------------------------------------------------ classical
  const TEMPL = new Map();
  const formsAll = () => M.forms;
  function darbGroup(label) { if (!label || !label.startsWith('ضرب')) return 'ضرب صحيح'; return label.split(/\s+/).slice(0, 2).join(' '); }
  function template(form, part, group) {
    const key = form.key + '|' + part + '|' + (group || '');
    if (!TEMPL.has(key)) {
      let last = (part === 'ajuz' || form.single) ? form.darb : form.arud;
      if (group) last = last.filter(v => darbGroup(v[3]) === group);
      TEMPL.set(key, last.length ? templateGraph(form.hashw.concat([last])) : null);
    }
    return TEMPL.get(key);
  }

  const LAT = new Map();
  function lattice(text) {
    if (!LAT.has(text)) { if (LAT.size > 4000) LAT.clear(); LAT.set(text, [latticeGraph(buildHemistich(text)), words(text)]); }
    return LAT.get(text);
  }

  function summarize(L, T, cost, steps, form, part, ws) {
    const per = T.positions.map(() => ({ v: null, got: '', let: '', err: 0, words: new Set() }));
    let cur = 0; const readings = [], seen = new Set();
    for (const st of steps) {
      if (st.pin) { cur = st.pin[0]; if (per[cur].v === null) per[cur].v = st.pin[1]; }
      if (st.tin) {
        const [k, j, c] = st.tin, sl = L.slots[k], o = sl.opts[j];
        if (!seen.has(k + ':' + j)) {
          seen.add(k + ':' + j);
          if (o.note && sl.opts.length > 1 && sl.kind !== 'unk' && !(sl.kind === 'unk_end' && (o.bits === '0' || o.bits === '1')))
            readings.push({ word: ws[sl.w], note: o.note, w: sl.w });
        }
        if (c >= 0) { per[cur].got += st.bit; per[cur].let += o.disp[c] || ''; per[cur].words.add(sl.w); }
      }
      if (st.op === 'sub' || st.op === 'del' || st.op === 'ins') per[cur].err++;
    }
    const feet = T.positions.map((vs, p) => {
      const d = per[p], v = vs[d.v === null ? 0 : d.v];
      return { pos: p, expected: v[0], name: v[1], label: v[3], got: d.got, letters: d.let, errors: d.err, words: [...d.words] };
    });
    const errors = steps.filter(s => s.op === 'sub' || s.op === 'del' || s.op === 'ins').length;
    const pattern = steps.filter(s => s.bit !== null && s.bit !== undefined).map(s => s.bit).join('');
    return { form: form.key, part, cost, errors, feet, readings, ending: feet[feet.length - 1].label, pattern, allowed: T.positions };
  }

  function scanHemistich(text, form, part, cap = 4, group = null) {
    const [L, ws] = lattice(text); const T = template(form, part, group); if (!T) return null;
    const r = align(L, T, cap); if (!r) return null;
    return summarize(L, T, r[0], r[1], form, part, ws);
  }

  const SEP = /\s*(?:\t+|\*+|\|+|…+|\.\.\.+|٭+|⁂|\s{3,}|\/\/+|-{2,}|—+)\s*/;
  function splitLine(line) { const p = line.trim().split(SEP).filter(x => x.trim()); return p.length === 2 ? p : null; }
  function autoSplits(line) {
    const ws = words(line), total = ws.reduce((a, w) => a + w.length, 0), out = []; let acc = 0;
    for (let i = 1; i < ws.length; i++) { acc += ws[i - 1].length; if (acc / total >= 0.33 && acc / total <= 0.67) out.push([ws.slice(0, i).join(' '), ws.slice(i).join(' ')]); }
    return out;
  }

  function scanLine(i, line, forms, cap = 4) {
    const sp = splitLine(line), cands = sp ? [sp] : autoSplits(line), results = {};
    for (const form of forms) {
      let best = null;
      if (form.single) {
        if (sp) continue;
        const r = scanHemistich(line, form, 'ajuz', cap); if (r) best = { cost: r.cost + form.rare, sadr: null, ajuz: r, split: null };
      } else {
        for (const [a, b] of cands) {
          const ra = scanHemistich(a, form, 'sadr', cap); if (!ra) continue;
          const rb = scanHemistich(b, form, 'ajuz', cap); if (!rb) continue;
          const c = ra.cost + rb.cost + form.rare;
          if (!best || c < best.cost) best = { cost: c, sadr: ra, ajuz: rb, split: [a, b] };
        }
      }
      if (best) results[form.key] = best;
    }
    return { index: i, text: line, sep: !!sp, results };
  }

  const LINE_CAP = 6, DARB_MISMATCH = 0.75;
  const exact = r => r && (!r.sadr || r.sadr.errors === 0) && r.ajuz.errors === 0;

  function rankPoem(scans, forms) {
    const ranking = [];
    for (const form of forms) {
      const per = scans.map(ls => { const r = ls.results[form.key]; return r ? [Math.min(r.cost, LINE_CAP), r] : [LINE_CAP, null]; });
      const darbs = {};
      per.forEach(([c, r]) => { if (r && r.ajuz.errors === 0) { const g = darbGroup(r.ajuz.ending); darbs[g] = (darbs[g] || 0) + 1; } });
      let dominant = null, dn = 0; for (const g in darbs) if (darbs[g] > dn) { dn = darbs[g]; dominant = g; }
      if (dominant && !form.single) {
        per.forEach(([c, r], idx) => {
          if (!exact(r) || darbGroup(r.ajuz.ending) === dominant) return;
          const aj = r.split ? r.split[1] : scans[idx].text;
          const rr = scanHemistich(aj, form, 'ajuz', 4, dominant);
          if (rr && rr.errors === 0) { const nc = (r.sadr ? r.sadr.cost : 0) + rr.cost + form.rare; per[idx] = [Math.min(nc, LINE_CAP), Object.assign({}, r, { cost: nc, ajuz: rr })]; }
        });
      }
      let total = 0, ex = 0, exH = 0; const mism = [];
      per.forEach(([c, r], idx) => {
        total += c;
        if (r) exH += (r.sadr && r.sadr.errors === 0 ? 1 : 0) + (r.ajuz.errors === 0 ? 1 : 0);
        if (exact(r)) { ex++; if (dominant && darbGroup(r.ajuz.ending) !== dominant) { total += DARB_MISMATCH; mism.push(idx); } }
      });
      ranking.push({ form, total, exact: ex, exactH: exH, n: scans.length, dominant, darbMismatch: mism, perLine: per });
    }
    const score = r => r.total - 0.25 * r.exactH;
    ranking.sort((a, b) => score(a) - score(b) || b.exact - a.exact);
    // lines too broken for the fast pass still count their sound half (top candidates only)
    for (const r of ranking.slice(0, 6)) {
      r.perLine.forEach(([c, x], idx) => {
        if (x) return;
        const rr = rescan(scans[idx].text, r.form);
        if (rr) { r.exactH += (rr.sadr && rr.sadr.errors === 0 ? 1 : 0) + (rr.ajuz.errors === 0 ? 1 : 0); r.perLine[idx] = [c, null, rr]; }
      });
    }
    ranking.sort((a, b) => score(a) - score(b) || b.exact - a.exact);
    const seen = new Set(), cands = [];
    for (const r of ranking) if (!seen.has(r.form.meter)) { seen.add(r.form.meter); cands.push(r); }
    return cands;
  }

  function discriminating(a, b) {
    const out = [];
    a.perLine.forEach(([, ra], i) => { if (exact(ra) && !exact(b.perLine[i][1])) out.push(i); });
    return out;
  }

  function rescan(text, form) {
    const sp = splitLine(text), cands = sp ? [sp] : autoSplits(text);
    if (form.single) { const r = scanHemistich(text, form, 'ajuz', 20); return r ? { cost: r.cost, sadr: null, ajuz: r, split: null } : null; }
    let best = null;
    for (const [a, b] of cands) {
      const ra = scanHemistich(a, form, 'sadr', 20), rb = scanHemistich(b, form, 'ajuz', 20);
      if (ra && rb && (!best || ra.cost + rb.cost < best.cost)) best = { cost: ra.cost + rb.cost, sadr: ra, ajuz: rb, split: [a, b] };
    }
    return best;
  }

  // ------------------------------------------------------------------ free verse
  const CROSS = 0.15, BEAM = 5;
  function loopTemplate(fam) {
    const variants = fam.hashw.map(v => [v, false]).concat(fam.endings.map(v => [v, true]));
    const out = [[]];
    variants.forEach(([v, isEnd], vi) => {
      let prev = 0;
      for (let c = 0; c < v[0].length; c++) {
        const last = c === v[0].length - 1; let to;
        if (last) to = 0; else { out.push([]); to = out.length - 1; }
        out[prev].push([to, v[0][c], c === 0 ? v[2] : 0, [vi, c], isEnd && last]);
        prev = to;
      }
    });
    return { variants, out, n: out.length };
  }
  function addTadwir(slots) {
    for (let k = slots.length - 1; k >= 0; k--) {
      const s = slots[k]; if (s.kind === 'silent') continue;
      const extra = [];
      for (const o of s.opts) if (o.bits.length >= 2 && o.bits.endsWith('0') && ['end_v', 'end_amb', 'ha', 'cons_tan', 'shadda'].includes(s.kind))
        extra.push(opt(o.bits.slice(0, -1), o.disp.slice(0, -1), o.cost + 0.3, 'تدوير: آخر السطر موصول بما بعده'));
      s.opts.push(...extra); return;
    }
  }
  function buildStream(lines) {
    const slots = [];
    lines.forEach((line, li) => { const sl = buildHemistich(line); addTadwir(sl); sl.forEach(s => { s.line = li; }); slots.push(...sl); });
    const L = latticeGraph(slots), lineEnd = new Set();
    for (let k = 1; k < slots.length; k++) if (slots[k].line !== slots[k - 1].line) lineEnd.add(L.slotStart[k]);
    lineEnd.add(L.final);
    let changed = true;
    while (changed) {
      changed = false;
      for (let u = 0; u < L.n; u++) {
        if (lineEnd.has(u) || !L.out[u].length) continue;
        if (L.out[u].every(([w, b]) => b === null && lineEnd.has(w))) { lineEnd.add(u); changed = true; }
      }
    }
    return [L, lineEnd];
  }
  function scanFamily(L, lineEnd, fam) {
    const T = loopTemplate(fam), cost = [], back = [];
    for (let u = 0; u < L.n; u++) { cost.push(new Float64Array(T.n).fill(INF)); back.push(new Array(T.n)); }
    cost[0][0] = 0;
    for (let u = 0; u < L.n; u++) {
      const cu = cost[u], bu = back[u]; let best = INF;
      for (let s = 0; s < T.n; s++) if (cu[s] < best) best = cu[s];
      if (best === INF) continue;
      for (let s = 0; s < T.n; s++) {
        const c = cu[s]; if (c === INF || c > best + BEAM) continue;
        for (const [t, ch, ec, pin, endOnly] of T.out[s]) {
          if (endOnly && !lineEnd.has(u)) continue;
          const nc = c + INS + ec; if (t > s && nc < cu[t]) { cu[t] = nc; bu[t] = [u, s, 'ins', null, null, pin, ch]; }
        }
        for (const [w, bit, lc, tin] of L.out[u]) {
          const cw = cost[w], bw = back[w], cross = (lineEnd.has(w) && w !== L.final) ? CROSS : 0;
          if (bit === null) { const nc = c + lc + (s !== 0 ? cross : 0); if (nc < cw[s]) { cw[s] = nc; bw[s] = [u, s, 'eps', tin, null, null, null]; } continue; }
          let nc = c + lc + DEL + (s !== 0 ? cross : 0); if (nc < cw[s]) { cw[s] = nc; bw[s] = [u, s, 'del', tin, bit, null, null]; }
          for (const [t, ch, ec, pin, endOnly] of T.out[s]) {
            if (endOnly && !lineEnd.has(w)) continue;
            nc = c + lc + ec + (ch === bit ? 0 : SUB) + (t !== 0 ? cross : 0);
            if (nc < cw[t]) { cw[t] = nc; bw[t] = [u, s, ch === bit ? 'match' : 'sub', tin, bit, pin, ch]; }
          }
        }
      }
    }
    const fin = cost[L.final]; let endState = 0;
    if (fin[0] === INF) { let b = INF; for (let s = 0; s < T.n; s++) if (fin[s] < b) { b = fin[s]; endState = s; } if (b === INF) return null; }
    const total = fin[endState] + (endState === 0 ? 0 : 2);
    const steps = []; let u = L.final, s = endState;
    while (!(u === 0 && s === 0)) { const b = back[u][s]; steps.push({ op: b[2], tin: b[3], bit: b[4], pin: b[5], exp: b[6] }); u = b[0]; s = b[1]; }
    steps.reverse();
    return { total, steps, T };
  }
  function summarizeFree(L, steps, T, lines) {
    const out = lines.map((t, i) => ({ index: i, text: t, feet: [], errors: 0 })); let cur = null; const readings = [];
    const flush = f => {
      if (!f) return;
      const li = f.lines.length ? f.lines[0] : 0, crosses = new Set(f.lines).size > 1;
      out[li].feet.push({ name: f.name, letters: f.let, got: f.bits, errors: f.err, crosses, words: f.ws.filter(x => x[0] === li).map(x => x[1]), allowed: f.allowed }); out[li].errors += f.err;
      for (const extra of new Set(f.lines.slice(1))) if (extra !== li) out[extra].feet.push({ cont: true, name: f.name, letters: '', got: '', errors: 0, crosses: true });
    };
    for (const st of steps) {
      if (st.pin && st.pin[1] === 0) { flush(cur); const v = T.variants[st.pin[0]][0]; cur = { name: v[1], let: '', bits: '', err: 0, lines: [], ws: [], allowed: T.variants.filter(x => !x[1]).map(x => x[0]) }; }
      if (!cur) cur = { name: '؟', let: '', bits: '', err: 0, lines: [], ws: [], allowed: [] };
      if (st.tin) {
        const [k, j, c] = st.tin, sl = L.slots[k], o = sl.opts[j];
        if (c >= 0) { cur.bits += st.bit; cur.let += o.disp[c] || ''; cur.lines.push(sl.line); cur.ws.push([sl.line, sl.w]); }
        if (o.note && sl.opts.length > 1 && sl.kind !== 'unk' && c <= 0) readings.push({ line: sl.line, note: o.note });
      }
      if (st.op === 'sub' || st.op === 'del' || st.op === 'ins') cur.err++;
    }
    flush(cur);
    return [out, readings];
  }
  function analyzeFree(lines, onlyMeter) {
    const [L, lineEnd] = buildStream(lines), res = [];
    for (const fam of M.families) {
      if (onlyMeter && fam.meter !== onlyMeter) continue;
      const r = scanFamily(L, lineEnd, fam); if (!r) continue;
      const errors = r.steps.filter(s => s.op === 'sub' || s.op === 'del' || s.op === 'ins').length;
      const nbits = r.steps.filter(s => s.bit !== null && s.bit !== undefined).length;
      res.push({ family: fam, total: r.total, errors, nbits, steps: r.steps, T: r.T });
    }
    res.sort((a, b) => a.total - b.total);
    res.slice(0, 3).forEach(r => { [r.lines, r.readings] = summarizeFree(L, r.steps, r.T, lines); });
    return res;
  }

  // ------------------------------------------------------------------ poem-level
  function patternLen(line) { const sl = buildHemistich(line); return sl.reduce((a, s) => a + Math.min(...s.opts.map(o => o.bits.length)), 0); }

  /** Pair consecutive lines as صدر * عجز (a poem written one hemistich per line). */
  function pairLines(lines) { const out = []; for (let i = 0; i + 1 < lines.length; i += 2) out.push(lines[i] + ' * ' + lines[i + 1]); return out; }

  /** Analyze a whole poem. opts: {mode: 'auto'|'classical'|'free'|'pairs', meter: key or null} */
  function analyze(lines, opts = {}) {
    lines = lines.filter(l => clean(l));
    if (!lines.length) return null;
    const meter = opts.meter || null;
    const forms = meter ? formsAll().filter(f => f.meter === meter) : formsAll();
    const canPair = lines.length >= 2 && lines.length % 2 === 0 && !lines.some(l => splitLine(l));
    const runPairs = () => { const pl = pairLines(lines); const scans = pl.map((l, i) => scanLine(i, l, forms.filter(f => !f.single))); return { scans, cands: rankPoem(scans, forms.filter(f => !f.single)) }; };
    if (opts.mode === 'pairs') {
      if (!canPair) return analyze(lines, Object.assign({}, opts, { mode: 'classical' }));
      const pr = runPairs();
      return { mode: 'classical', layout: 'pairs', lines, scans: pr.scans, cands: pr.cands };
    }
    const hasSep = lines.filter(l => splitLine(l)).length / lines.length;
    let mode = opts.mode || 'auto', cl = null, fr = null, pairsHint = null;
    const runClassical = () => { const scans = lines.map((l, i) => scanLine(i, l, forms)); return { scans, cands: rankPoem(scans, forms) }; };
    if (mode === 'auto') {
      if (hasSep >= 0.5) mode = 'classical';
      else {
        const lens = lines.map(patternLen), mean = lens.reduce((a, b) => a + b, 0) / lens.length;
        const sd = Math.sqrt(lens.reduce((a, b) => a + (b - mean) ** 2, 0) / lens.length), spread = lens.length > 1 ? sd / mean : 0;
        cl = runClassical(); fr = analyzeFree(lines, meter);
        let ce = cl.cands.length ? cl.cands[0].total / lines.length : 99; const fe = fr.length ? fr[0].total / lines.length : 99;
        if (spread > 0.2) ce += 0.5; else if (spread < 0.12) ce -= 0.3;
        mode = ce <= fe ? 'classical' : 'free';
        if (canPair && spread < 0.2) {
          const pr = runPairs(), top = pr.cands[0];
          const pe = top ? (top.total - 0.25 * top.exactH) / lines.length - 0.3 : 99;
          pairsHint = top ? { meter: top.form.meter, form: top.form.name, soundHalves: top.exactH, halves: lines.length } : null;
          if (pe < Math.min(ce, fe)) return { mode: 'classical', layout: 'pairs', lines, scans: pr.scans, cands: pr.cands, free: fr, pairsHint };
        }
      }
    }
    if (mode === 'free') {
      fr = fr || analyzeFree(lines, meter);
      return { mode, lines, free: fr, classical: cl, pairsHint };
    }
    cl = cl || runClassical();
    return { mode, lines, scans: cl.scans, cands: cl.cands, free: fr, pairsHint };
  }

  /** Check one candidate line against a meter. Returns {ok, feet...}. */
  function verifyLine(text, meter, mode, asHalf) {
    if (mode === 'free') {
      const fam = M.families.find(f => f.meter === meter); if (!fam) return null;
      const [L, le] = buildStream([text]); const r = scanFamily(L, le, fam); if (!r) return { ok: false, feet: [] };
      const [ls] = summarizeFree(L, r.steps, r.T, [text]); return { ok: ls[0].errors === 0, feet: ls[0].feet, mode };
    }
    const forms = formsAll().filter(f => f.meter === meter); let best = null;
    const sp = splitLine(text);
    for (const form of forms) {
      if (sp && !form.single) {
        const ra = scanHemistich(sp[0], form, 'sadr', 8), rb = scanHemistich(sp[1], form, 'ajuz', 8);
        if (ra && rb && (!best || ra.cost + rb.cost < best.cost)) best = { cost: ra.cost + rb.cost, parts: [ra, rb], form };
      } else if (!sp && asHalf && !form.single) {
        for (const part of ['sadr', 'ajuz']) { const r = scanHemistich(text, form, part, 8); if (r && (!best || r.cost < best.cost)) best = { cost: r.cost, parts: [r], form }; }
      } else if (!sp) {
        const r = scanHemistich(text, form, 'ajuz', 8);
        if (r && (!best || r.cost < best.cost)) best = { cost: r.cost, parts: [r], form };
      }
    }
    if (!best) return { ok: false, parts: [] };
    return { ok: best.parts.every(p => p.errors === 0), parts: best.parts, form: best.form, mode };
  }

  // ------------------------------------------------------------------ display helpers
  /** prosodic bits -> classical syllable notation: ب short (/), − long (/0), = overlong (/00) */
  function syll(bits) {
    const t = [];
    for (let i = 0; i < bits.length; i++) {
      if (bits[i] === '1') { if (bits[i + 1] === '0') { t.push('−'); i++; } else t.push('ب'); }
      else { if (t.length && t[t.length - 1] === '−') t[t.length - 1] = '='; else t.push('٠'); }
    }
    return t.join(' ');
  }
  const marks = bits => [...bits].map(b => b === '1' ? '/' : '0').join('');

  /** letters a word needs marked but lacks (for highlighting) */
  function unmarkedCount(word) {
    const units = parseWord(word); let n = 0;
    units.forEach((u, k) => {
      if (ALEFS.has(u.letter) || u.letter === 'ى' || u.letter === 'آ') return;
      const prev = k ? units[k - 1] : null;
      if ((u.letter === 'و' || u.letter === 'ي') && !marked(u) && prev && (prev.vowel === 'u' || prev.vowel === 'i')) return;
      if (!marked(u)) n++;
    });
    return n;
  }

  // ------------------------------------------------------------------ rhyme (light)
  function lineRhyme(text) {
    const ws = words(text); if (!ws.length) return null;
    const units = rewriteSpecial(parseWord(ws[ws.length - 1]));
    while (units.length > 1 && units[units.length - 1].letter === 'ا' && units[units.length - 2].letter === 'و' && !units[units.length - 2].vowel) units.pop();
    let i = units.length - 1;
    if (i > 0 && 'اىوي'.includes(units[i].letter) && !units[i].vowel && !units[i].shadda && !units[i].tanwin) i--;
    const r = units[i];
    const out = { word: ws[ws.length - 1], rawi: r.letter === 'ة' ? 'ت' : r.letter, vowel: r.vowel || r.tanwin || (r.sukun ? 'o' : null), alt: null };
    if ((r.letter === 'ه' || r.letter === 'ة') && i > 0 && !'اىوي'.includes(units[i - 1].letter)) out.alt = units[i - 1].letter;
    return out;
  }
  function rhymeCheck(endTexts) {
    const rows = endTexts.map(lineRhyme), votes = {};
    rows.forEach(r => { if (!r) return; for (const c of new Set([r.rawi, r.alt].filter(Boolean))) votes[c] = (votes[c] || 0) + 1; });
    let rawi = null, n = 0; for (const c in votes) if (votes[c] > n) { n = votes[c]; rawi = c; }
    return { rawi, rows: rows.map(r => r ? Object.assign({}, r, { ok: r.rawi === rawi || r.alt === rawi }) : null) };
  }

  const API = { pairLines, load, clean, words, parseWord, buildHemistich, analyze, verifyLine, rescan, discriminating, splitLine, syll, marks,
    unmarkedCount, rhymeCheck, scanHemistich, darbGroup, get data() { return M; } };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.Arud = API;
})(typeof window !== 'undefined' ? window : globalThis);

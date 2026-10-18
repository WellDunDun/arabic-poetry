/* Diwan exporter — builds a Word (.docx) manuscript from poems, as a map of {path: xml}.
   Used by the Diwan page (zipped with JSZip, saved via the downloads capability) and by
   scripts/export_book.py (zipped in Python, optionally converted to PDF with LibreOffice).

   model = { bookTitle, font, tashkeel: 'full'|'light'|'none', appendix: bool,
             poems: [{ title, meter, kind: 'verses'|'lines', verses: [[sadr, ajuz]], lines: [..],
                       scansion: [{ n, text, feet }] }] }                                           */
(function (root) {
  'use strict';
  const X = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const AR = n => String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);

  // ---------------------------------------------------------------- tashkeel levels
  const MARK = /[ً-ْٰ]/;
  function stripAll(s) { return s.replace(/[ً-ْٰ]/g, ''); }
  /** light: drop sukun and the short vowel written before its own long vowel (ـَا ـُو ـِي); keep the rest */
  function lighten(s) {
    const ch = [...s], out = [];
    for (let i = 0; i < ch.length; i++) {
      const c = ch[i];
      if (c === 'ْ') continue;
      if (c === 'َ' || c === 'ُ' || c === 'ِ') {
        let j = i + 1; while (j < ch.length && ch[j] === 'ّ') j++;
        const nx = ch[j], after = ch[j + 1] || '';
        const longOf = { 'َ': 'اى', 'ُ': 'و', 'ِ': 'ي' }[c];
        if (nx && longOf.includes(nx) && !MARK.test(after)) continue;
      }
      out.push(c);
    }
    return out.join('');
  }
  function level(s, how) { return how === 'none' ? stripAll(s) : how === 'light' ? lighten(s) : s; }

  // ---------------------------------------------------------------- xml helpers
  function run(text, o = {}) {
    const sz = o.size || 36;
    return `<w:r><w:rPr><w:rFonts w:ascii="${X(o.font)}" w:hAnsi="${X(o.font)}" w:cs="${X(o.font)}"/>${o.bold ? '<w:b/><w:bCs/>' : ''}` +
      `${o.color ? `<w:color w:val="${o.color}"/>` : ''}<w:sz w:val="${sz}"/><w:szCs w:val="${sz}"/><w:rtl/><w:lang w:bidi="ar-SA"/></w:rPr>` +
      `<w:t xml:space="preserve">${X(text)}</w:t></w:r>`;
  }
  function para(runs, o = {}) {
    return `<w:p><w:pPr>${o.style ? `<w:pStyle w:val="${o.style}"/>` : ''}${o.pageBreak ? '<w:pageBreakBefore/>' : ''}${o.keepNext ? '<w:keepNext/>' : ''}` +
      `<w:bidi/><w:spacing w:before="${o.before || 0}" w:after="${o.after == null ? 120 : o.after}" w:line="${o.line || 360}" w:lineRule="auto"/>` +
      `<w:jc w:val="${o.jc || 'center'}"/></w:pPr>${runs}</w:p>`;
  }
  const COLS = [4600, 438, 4600];               // صدر | فراغ | عجز  (A4 minus 2 cm margins)
  function cell(width, inner) {
    return `<w:tc><w:tcPr><w:tcW w:w="${width}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>${inner}</w:tc>`;
  }
  function verseTable(verses, font, size) {
    const rows = verses.map(([a, b]) => `<w:tr><w:trPr><w:cantSplit/></w:trPr>` +
      cell(COLS[0], para(run(a, { font, size }), { jc: 'center', after: 60 })) +
      cell(COLS[1], para('', { after: 60 })) +
      cell(COLS[2], para(run(b || '', { font, size }), { jc: 'center', after: 60 })) + '</w:tr>').join('');
    const none = '<w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/>';
    return `<w:tbl><w:tblPr><w:bidiVisual/><w:tblW w:w="${COLS.reduce((a, b) => a + b, 0)}" w:type="dxa"/><w:jc w:val="center"/>` +
      `<w:tblBorders>${none}</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>` +
      `<w:tblGrid>${COLS.map(w => `<w:gridCol w:w="${w}"/>`).join('')}</w:tblGrid>${rows}</w:tbl>`;
  }

  // a verse as ONE plain paragraph: «TAB صدر TAB عجز», no table, so it copies as plain text (halves split by tabs).
  // Two right-aligned tab stops (counted from the right margin in a RTL paragraph) anchor the right edge of each
  // half: the صدر at the right edge of a block centred on the page, the عجز just past the middle of that block.
  // The block is sized to the poem's longest half, so short-metre poems are not stretched across the page.
  const TEXT_W = 9638, GAP = 720;
  const halfWidth = (t, size) => stripAll(t).replace(/\s+/g, ' ').length * 125 * (size / 28);
  function verseParas(verses, font, size) {
    const col = Math.min(Math.round((TEXT_W - GAP) / 2), Math.max(1800, ...verses.flatMap(([a, b]) => [halfWidth(a, size), halfWidth(b || '', size)])));
    const right = Math.max(0, Math.round((TEXT_W - 2 * col - GAP) / 2)), s1 = Math.max(10, right), s2 = right + col + GAP;
    const tab = '<w:r><w:tab/></w:r>';
    return verses.map(([a, b]) => `<w:p><w:pPr><w:keepLines/><w:tabs><w:tab w:val="right" w:pos="${s1}"/><w:tab w:val="right" w:pos="${s2}"/></w:tabs>` +
      `<w:bidi/><w:spacing w:before="0" w:after="140" w:line="360" w:lineRule="auto"/></w:pPr>` +
      tab + run(a, { font, size }) + (b ? tab + run(b, { font, size }) : '') + '</w:p>').join('');
  }

  /** one row of foot cells (name over pattern), right to left; halves separated by a narrow ⁞ cell */
  function feetGrid(halves, font) {
    const cells = [];
    halves.forEach((h, hi) => {
      if (hi) cells.push({ sep: true });
      h.forEach(f => cells.push(f));
    });
    const total = 9638, sepW = 300, n = cells.filter(c => !c.sep).length, nsep = cells.length - n;
    const w = Math.floor((total - nsep * sepW) / Math.max(n, 1));
    const tcs = cells.map(c => c.sep
      ? cell(sepW, para(run('⁞', { font, size: 24, color: '999999' }), { after: 0 }))
      : cell(w, para(run(c.name, { font, size: 20, color: c.bad ? 'B3261E' : '0E6B66' }), { after: 0, line: 240 }) +
               para(run(c.syl, { font, size: 22, bold: true, color: c.bad ? 'B3261E' : '333333' }), { after: 0, line: 240 })));
    const grid = cells.map(c => `<w:gridCol w:w="${c.sep ? sepW : w}"/>`).join('');
    const b = '<w:top w:val="single" w:sz="2" w:color="DDDDDD"/><w:bottom w:val="single" w:sz="2" w:color="DDDDDD"/><w:left w:val="nil"/><w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="single" w:sz="2" w:color="EEEEEE"/>';
    return `<w:tbl><w:tblPr><w:bidiVisual/><w:tblW w:w="${total}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>${b}</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr>` +
      `<w:tblGrid>${grid}</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>${tcs.join('')}</w:tr></w:tbl>` + para('', { after: 120, line: 200 });
  }

  function build(model) {
    const font = model.font || 'Traditional Arabic', tk = model.tashkeel || 'full';
    const body = [];
    let first = true;
    if (model.bookTitle && model.poems.length > 1) {
      body.push(para(run(model.bookTitle, { font, size: 64, bold: true }), { before: 3600, after: 240 }));
      const n = model.poems.length, cnt = n === 2 ? 'قصيدتان' : n <= 10 ? `${AR(n)} قصائد` : `${AR(n)} قصيدة`;
      body.push(para(run(cnt, { font, size: 30, color: '666666' }), {}));
      first = false;
    }
    for (const p of model.poems) {
      // every poem opens on a new page (the first one too, when a title page precedes it)
      body.push(para(run(p.title || '', { font, size: 44, bold: true }), { pageBreak: !first, keepNext: true, after: 80 }));
      first = false;
      if (p.meter && model.meterUnderTitle !== false) body.push(para(run(p.meter, { font, size: 24, color: '777777' }), { keepNext: true, after: 360 }));
      if (p.kind === 'verses') body.push((model.verseLayout === 'table' ? verseTable : verseParas)(p.verses.map(([a, b]) => [level(a, tk), level(b || '', tk)]), font, model.verseSize || 28));
      // تفعيلة (and single-hemistich forms): one column, each line centred on the page
      else for (const l of p.lines) body.push(para(run(level(l, tk), { font, size: model.verseSize || 32 }), { jc: 'center', after: 80 }));
    }
    if (model.appendix) {
      body.push(para(run('ملحق: البحور والتقطيع', { font, size: 44, bold: true }), { pageBreak: true, after: 120 }));
      body.push(para(run('ب مقطع قصير (متحرك) · − مقطع طويل (متحرك فساكن) · = مقطع زائد الطول آخر الشطر · ✗ تفعيلة مكسورة', { font, size: 22, color: '666666' }), { after: 360 }));
      for (const p of model.poems) {
        body.push(para(run(p.title || '', { font, size: 32, bold: true }), { keepNext: true, before: 240, after: 40, jc: 'right' }));
        if (p.meter) body.push(para(run(p.meter, { font, size: 24, color: '555555' }), { keepNext: true, after: 120, jc: 'right' }));
        for (const r of p.scansion || []) {
          const label = `${AR(r.n)}.  ${level(r.verse ? r.verse[0] : r.text, tk)}${r.verse && r.verse[1] ? '     ' + level(r.verse[1], tk) : ''}${r.broken ? '   ✗' : ''}`;
          body.push(para(run(label, { font, size: 26, color: r.broken ? 'B3261E' : undefined }), { keepNext: true, after: 40, jc: 'right' }));
          if (r.halves && r.halves.length) body.push(feetGrid(r.halves, font));
          else body.push(para(run(r.feet, { font, size: 22 }), { after: 120, jc: 'right' }));
        }
      }
    }
    const sect = `<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1418" w:right="1134" w:bottom="1418" w:left="1134" w:header="709" w:footer="709" w:gutter="0"/><w:bidi/></w:sectPr>`;
    const doc = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>${body.join('')}${sect}</w:body></w:document>`;
    const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="${X(font)}" w:hAnsi="${X(font)}" w:cs="${X(font)}"/><w:sz w:val="32"/><w:szCs w:val="32"/><w:lang w:val="ar-SA" w:bidi="ar-SA"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:bidi/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:bidi/></w:pPr></w:style></w:styles>`;
    const settings = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:themeFontLang w:val="ar-SA" w:bidi="ar-SA"/><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>`;
    return {
      '[Content_Types].xml': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>`,
      '_rels/.rels': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`,
      'word/_rels/document.xml.rels': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/></Relationships>`,
      'word/document.xml': doc, 'word/styles.xml': styles, 'word/settings.xml': settings,
    };
  }

  /** Plain-text copy: verse halves separated by five spaces so they never read as one sentence. */
  function plainText(model) {
    const tk = model.tashkeel || 'full', out = [];
    for (const p of model.poems) {
      if (p.title) out.push(p.title, '');
      if (p.kind === 'verses') for (const [a, b] of p.verses) out.push(level(a, tk) + (b ? '     ' + level(b, tk) : ''));
      else for (const l of p.lines) out.push(level(l, tk));
      out.push('');
    }
    return out.join('\n').trim() + '\n';
  }

  /** Turn a Diwan poem {title, text, mode, meter} into an export entry, using the Arud engine A. */
  function poemModel(p, A) {
    const lines = (p.text || '').split('\n').filter(l => A.clean(l));
    const out = { title: p.title || '', meter: '', kind: 'lines', lines, verses: [], scansion: [] };
    if (!lines.length) return out;
    let a = null;
    try { a = A.analyze(lines, { mode: p.mode || 'auto', meter: p.meter || null }); } catch (e) { a = null; }
    const info = k => (A.data.info[k] || [k])[0];
    const feetStr = feet => feet.map(f => `${f.name} ${A.syll(f.got)}${f.errors ? ' ✗' : ''}`).join(' | ');
    if (!a) return out;
    if (a.mode === 'free') {
      const best = a.free[0];
      out.meter = `شعر تفعيلة — ${best.family.foot} (${info(best.family.meter)})`;
      (best.lines || []).forEach((ln, i) => {
        const feet = ln.feet.filter(f => !f.cont);
        out.scansion.push({ n: i + 1, text: lines[i], feet: feetStr(feet), broken: feet.some(f => f.errors),
          halves: [feet.map(f => ({ name: f.name, syl: A.syll(f.got), bad: f.errors > 0 }))] });
      });
      return out;
    }
    const c = a.cands[0];
    out.meter = `${info(c.form.meter)} — ${c.form.name}`;
    if (c.form.single) {          // مشطور / منهوك: one hemistich per line, so one column like تفعيلة
      a.scans.forEach((s, i) => {
        let r = c.perLine[i] ? (c.perLine[i][1] || c.perLine[i][2]) : null; if (!r) r = A.rescan(s.text, c.form);
        out.scansion.push({ n: i + 1, text: s.text, feet: r ? feetStr(r.ajuz.feet) : '—', broken: !r || r.ajuz.errors > 0,
          halves: r ? [r.ajuz.feet.map(f => ({ name: f.name, syl: A.syll(f.got), bad: f.errors > 0 }))] : [] });
      });
      return out;
    }
    out.kind = 'verses';
    if (a.layout === 'pairs') {
      for (let i = 0; i < lines.length; i += 2) out.verses.push([lines[i], lines[i + 1] || '']);
    } else {
      a.scans.forEach((s, i) => {
        const r = c.perLine[i] ? (c.perLine[i][1] || c.perLine[i][2]) : null;
        const sp = A.splitLine(s.text) || (r && r.split);
        out.verses.push(sp ? [sp[0], sp[1]] : [s.text, '']);
      });
    }
    out.verses.forEach((v, i) => {
      let r = c.perLine[i] ? (c.perLine[i][1] || c.perLine[i][2]) : null;
      if (!r) r = A.rescan(a.scans[i].text, c.form);
      if (!r) { out.scansion.push({ n: i + 1, text: v.join('     '), feet: '—', broken: true }); return; }
      const parts = r.sadr ? [r.sadr, r.ajuz] : [r.ajuz];
      out.scansion.push({ n: i + 1, text: v[1] ? v[0] + '     ' + v[1] : v[0], feet: parts.map(h => feetStr(h.feet)).join('   ⁞   '),
        broken: parts.some(h => h.errors), verse: v,
        halves: parts.map(h => h.feet.map(f => ({ name: f.name, syl: A.syll(f.got), bad: f.errors > 0 }))) });
    });
    return out;
  }

  const API = { build, plainText, lighten, stripAll, poemModel };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.DiwanExport = API;
})(typeof window !== 'undefined' ? window : globalThis);

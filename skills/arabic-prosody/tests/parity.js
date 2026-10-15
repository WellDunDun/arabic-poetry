// node tests/parity.js — the browser engine must agree with the Python gold results
const fs = require('fs'), path = require('path');
const A = require('../assets/workbench/engine.js');
A.load(JSON.parse(fs.readFileSync(path.join(__dirname, '../assets/workbench/meters.json'), 'utf8')));
let ok = 0, n = 0;
for (const line of fs.readFileSync(path.join(__dirname, 'gold_verses.tsv'), 'utf8').split('\n')) {
  if (!line.trim() || line.startsWith('#')) continue;
  const [meter, form, verse] = line.split('\t'); n++;
  const r = A.analyze([verse], { mode: 'classical' });
  const top = r.cands[0], good = top.form.meter === meter && top.exact === 1;
  ok += good; if (!good) console.log('FAIL', meter, '->', top.form.key, top.total);
}
console.log(`classical ${ok}/${n}`);
const fv = fs.readFileSync(path.join(__dirname, 'free_verse_kamil.txt'), 'utf8').split('\n').filter(l => l.trim());
const f = A.analyze(fv);
console.log('free verse', f.mode, f.free[0].family.meter, 'errors', f.free[0].errors);
const lines = ['قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِل * بِسِقْطِ اللِّوَى بَيْنَ الدَّخُولِ فَحَوْمَل',
  'فَتُوضِحَ فَالْمِقْرَاةِ لَمْ يَعْفُ رَسْمُهَا * لِمَا نَسَجَتْهَا مِنْ جَنُوبٍ وَشَمْأَلِ'];
const e = A.analyze(lines); const r0 = e.cands[0].perLine[0][1];
console.log('ending ambiguity', e.cands[0].form.meter, r0.ajuz.feet.at(-1).name);
if (process.argv[2]) {
  const p = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(l => l.trim());
  const t0 = Date.now(), r = A.analyze(p);
  console.log('poem', r.mode, r.mode === 'free' ? r.free[0].family.meter + ' err ' + r.free[0].errors : r.cands[0].form.key, (Date.now() - t0) + 'ms');
}

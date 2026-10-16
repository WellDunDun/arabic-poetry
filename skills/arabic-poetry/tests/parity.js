// Assert expected fixtures and compare sound sequences/feet across both runtimes.
const assert = require('node:assert/strict');
const fs = require('fs'), path = require('path');
const { spawnSync } = require('node:child_process');
const A = require('../assets/workbench/engine.js');
A.load(JSON.parse(fs.readFileSync(path.join(__dirname, '../assets/workbench/meters.json'), 'utf8')));
const half = h => h ? { pattern: h.pattern, errors: h.errors,
  feet: h.feet.map(f => ({ name: f.name, bits: f.got, errors: f.errors })) } : null;
function classical(lines) {
  const top = A.analyze(lines, { mode: 'classical' }).cands[0];
  return { meter: top.form.meter, form: top.form.key, exact: top.exact,
    parts: top.perLine.map(row => row[1] ? [half(row[1].sadr), half(row[1].ajuz)] : null) };
}
const gold = [];
for (const line of fs.readFileSync(path.join(__dirname, 'gold_verses.tsv'), 'utf8').split('\n')) {
  if (!line.trim() || line.startsWith('#')) continue;
  const [meter, form, verse] = line.split('\t');
  const result = classical([verse]);
  assert.equal(result.meter, meter, `wrong gold meter: ${verse}`);
  assert.equal(result.form, `${meter}/${form}`, `wrong gold form: ${verse}`);
  assert.equal(result.exact, 1, `broken gold verse: ${verse}`);
  gold.push(result);
}
assert.ok(gold.length > 0, 'gold fixture must not be empty');
const fv = fs.readFileSync(path.join(__dirname, 'free_verse_kamil.txt'), 'utf8').split('\n').filter(l => l.trim());
const f = A.analyze(fv, { mode: 'free' }).free[0];
assert.equal(f.family.meter, 'kamil');
assert.equal(f.errors, 0);
const free = { meter: f.family.meter, errors: f.errors,
  lines: f.lines.map(line => line.feet.map(foot => ({ name: foot.name, bits: foot.got,
    errors: foot.errors, crosses: foot.crosses }))) };
const endings = ['قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِل * بِسِقْطِ اللِّوَى بَيْنَ الدَّخُولِ فَحَوْمَل',
  'فَتُوضِحَ فَالْمِقْرَاةِ لَمْ يَعْفُ رَسْمُهَا * لِمَا نَسَجَتْهَا مِنْ جَنُوبٍ وَشَمْأَلِ'];
const ending = classical(endings);
assert.equal(ending.meter, 'tawil');
assert.equal(ending.parts[0][1].feet.at(-1).name, 'مفاعلن');
const python = spawnSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'parity_snapshot.py')],
  { encoding: 'utf8', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });
assert.equal(python.status, 0, python.stderr || String(python.error || 'Python parity snapshot failed'));
assert.deepEqual({ classical: gold, free, ending }, JSON.parse(python.stdout));
console.log(`PASS: ${gold.length} classical verses, taf‘ila, ending ambiguity, and Python/JS patterns and feet agree`);
if (process.argv[2]) {
  const lines = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(l => l.trim());
  const result = A.analyze(lines);
  console.log('poem', result.mode, result.mode === 'free' ? result.free[0].family.meter : result.cands[0].form.key);
}

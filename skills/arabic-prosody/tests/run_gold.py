"""Regression test: every gold verse must be identified with its known meter, with no broken foot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from arud.classical import scan_line, rank_poem, best_per_meter

ok = 0; rows = []
for line in open(os.path.join(os.path.dirname(__file__), 'gold_verses.tsv'), encoding='utf-8'):
    if line.startswith('#') or not line.strip(): continue
    meter, form, verse = line.rstrip('\n').split('\t')
    ls = scan_line(0, verse)
    rk = best_per_meter(rank_poem([ls]))
    top = rk[0]
    r = top['per_line'][0][1]
    good = top['form'].meter == meter and top['exact'] == 1
    ok += good
    feet = ' + '.join(' '.join(f.name + ('✗' if f.errors else '') for f in h.feet) for h in (r[1], r[2]) if h) if r else '-'
    print(('PASS' if good else 'FAIL'), meter, '->', top['form'].key, round(top['total'], 2),
          '| 2nd:', rk[1]['form'].key, round(rk[1]['total'], 2), '|', feet)
    if not good and r:
        for h in (r[1], r[2]):
            if h: print('      ', h.arudi, h.pattern, h.readings)
print(f'{ok}/{len([l for l in open(os.path.join(os.path.dirname(__file__), "gold_verses.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")])} passed')

# free verse: an original taf'ila sample on متفاعلن (with one تدوير)
from arud import freeverse
fv = [l for l in open(os.path.join(os.path.dirname(__file__), 'free_verse_kamil.txt'), encoding='utf-8').read().splitlines() if l.strip()]
res, _ = freeverse.analyze(fv)
good = res[0]['family'].meter == 'kamil' and res[0]['errors'] == 0
print(('PASS' if good else 'FAIL'), 'free verse kamil ->', res[0]['family'].meter, 'errors', res[0]['errors'])

# ambiguous endings resolved by the poem: unmarked last letters must be read as إطلاق
lines = ['قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِل * بِسِقْطِ اللِّوَى بَيْنَ الدَّخُولِ فَحَوْمَل',
         'فَتُوضِحَ فَالْمِقْرَاةِ لَمْ يَعْفُ رَسْمُهَا * لِمَا نَسَجَتْهَا مِنْ جَنُوبٍ وَشَمْأَلِ']
cands = best_per_meter(rank_poem([scan_line(i, l) for i, l in enumerate(lines)]))
r = cands[0]['per_line'][0][1]
good = cands[0]['form'].meter == 'tawil' and r[2].feet[-1].name == 'مفاعلن'
print(('PASS' if good else 'FAIL'), 'ending ambiguity ->', cands[0]['form'].meter, r[2].feet[-1].name)

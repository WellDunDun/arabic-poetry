"""Emit the Python engine's results for the cross-runtime regression suite."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from arud.classical import scan_line, rank_poem, best_per_meter
from arud.freeverse import analyze


def half(value):
    return None if value is None else {
        'pattern': value.pattern, 'errors': value.errors,
        'feet': [{'name': foot.name, 'bits': foot.got, 'errors': foot.errors}
                 for foot in value.feet],
    }


def classical(lines):
    top = best_per_meter(rank_poem([scan_line(i, text) for i, text in enumerate(lines)]))[0]
    return {'meter': top['form'].meter, 'form': top['form'].key, 'exact': top['exact'],
            'parts': [[half(row[1][1]), half(row[1][2])] if row[1] else None
                      for row in top['per_line']]}


gold = []
for line in (HERE / 'gold_verses.tsv').read_text().splitlines():
    if line.strip() and not line.startswith('#'):
        meter, form, verse = line.split('\t')
        gold.append(classical([verse]))
lines = (HERE / 'free_verse_kamil.txt').read_text().splitlines()
free = analyze([line for line in lines if line.strip()])[0][0]
free_result = {'meter': free['family'].meter, 'errors': free['errors'],
               'lines': [[{'name': foot[0].removeprefix('↩ '), 'bits': foot[2],
                           'errors': foot[3], 'crosses': foot[4]}
                          for foot in line.feet] for line in free['lines']]}
endings = ['قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِل * بِسِقْطِ اللِّوَى بَيْنَ الدَّخُولِ فَحَوْمَل',
           'فَتُوضِحَ فَالْمِقْرَاةِ لَمْ يَعْفُ رَسْمُهَا * لِمَا نَسَجَتْهَا مِنْ جَنُوبٍ وَشَمْأَلِ']
print(json.dumps({'classical': gold, 'free': free_result, 'ending': classical(endings)},
                 ensure_ascii=False))

"""Export meter tables to JSON for the browser engine (single source of truth = meters.py)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arud.meters import FORMS, FAMILIES, METER_INFO
data = {
    'info': {k: list(v) for k, v in METER_INFO.items()},
    'forms': [{'meter': f.meter, 'name': f.name, 'key': f.key, 'hashw': f.hashw, 'arud': f.arud,
               'darb': f.darb, 'single': f.single, 'rare': f.rare} for f in FORMS],
    'families': [{'meter': f.meter, 'foot': f.foot, 'hashw': f.hashw, 'endings': f.endings} for f in FAMILIES],
}
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'assets', 'workbench', 'meters.json')
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('wrote', out, len(data['forms']), 'forms')

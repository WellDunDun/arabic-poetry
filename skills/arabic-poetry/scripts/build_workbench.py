"""Build the single-file Diwan workbench page: page.html + engine.js + meters.json -> assets/workbench/diwan.html"""
import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
wb = os.path.join(here, '..', 'assets', 'workbench')
subprocess.run([sys.executable, os.path.join(here, 'export_meters.py')], check=True, stdout=subprocess.DEVNULL)
page = open(os.path.join(wb, 'page.html'), encoding='utf-8').read()
engine = open(os.path.join(wb, 'engine.js'), encoding='utf-8').read()
exporter = open(os.path.join(wb, 'export.js'), encoding='utf-8').read()
meters = open(os.path.join(wb, 'meters.json'), encoding='utf-8').read()
out = page.replace('/*METERS*/null', meters).replace('/*ENGINE*/', engine).replace('/*EXPORT*/', exporter)
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(wb, 'diwan.html')
open(dest, 'w', encoding='utf-8').write(out)
print('built', dest, len(out) // 1024, 'KB')

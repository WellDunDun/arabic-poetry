#!/usr/bin/env python3
"""Export Diwan poems to a Word manuscript (and optionally PDF).

  python3 scripts/export_book.py poems.json out.docx [--pdf] [--tashkeel full|light|none]
         [--appendix] [--title "عنوان الديوان"] [--font "Traditional Arabic"] [--text out.txt]

poems.json is a list of Diwan documents: [{"title", "text", "mode", "meter"}] — e.g. what
ArtifactData returns for the `poems` collection. Layout, verse halves and the scansion
appendix come from the same engine the Diwan page uses (assets/workbench/*.js, via node).
--pdf converts with LibreOffice using the bundled Amiri font (assets/fonts, SIL OFL).
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def ensure_amiri():
    dest = os.path.expanduser('~/.fonts')
    os.makedirs(dest, exist_ok=True)
    added = False
    for f in ('Amiri-Regular.ttf', 'Amiri-Bold.ttf'):
        src = os.path.join(ROOT, 'assets', 'fonts', f)
        if os.path.exists(src) and not os.path.exists(os.path.join(dest, f)):
            shutil.copy(src, dest); added = True
    if added:
        subprocess.run(['fc-cache', '-f'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('poems'); ap.add_argument('out')
    ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--tashkeel', default='full', choices=['full', 'light', 'none'])
    ap.add_argument('--appendix', action='store_true')
    ap.add_argument('--title', default='')
    ap.add_argument('--font', default=None)
    ap.add_argument('--text', help='also write a plain-text copy (halves separated by five spaces)')
    a = ap.parse_args()
    poems = json.load(open(a.poems, encoding='utf-8'))
    if isinstance(poems, dict):
        poems = [poems]
    poems = [p.get('data', p) for p in poems]
    font = a.font or ('Amiri' if a.pdf else 'Traditional Arabic')
    with tempfile.TemporaryDirectory() as td:
        pj, oj = os.path.join(td, 'p.json'), os.path.join(td, 'o.json')
        json.dump(poems, open(pj, 'w', encoding='utf-8'), ensure_ascii=False)
        opts = {'bookTitle': a.title, 'font': font, 'tashkeel': a.tashkeel, 'appendix': a.appendix}
        json.dump(opts, open(oj, 'w', encoding='utf-8'), ensure_ascii=False)
        parts = json.loads(subprocess.run(['node', os.path.join(HERE, 'export_book.js'), pj, oj],
                                          check=True, capture_output=True).stdout)
        with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml', parts.pop('[Content_Types].xml'))
            for k, v in parts.items():
                z.writestr(k, v)
        print('wrote', a.out)
        if a.text:
            opts['textOnly'] = True
            json.dump(opts, open(oj, 'w', encoding='utf-8'), ensure_ascii=False)
            t = json.loads(subprocess.run(['node', os.path.join(HERE, 'export_book.js'), pj, oj],
                                          check=True, capture_output=True).stdout)['text']
            open(a.text, 'w', encoding='utf-8').write(t)
            print('wrote', a.text)
    if a.pdf:
        ensure_amiri()
        outdir = os.path.dirname(os.path.abspath(a.out))
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', outdir, a.out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('wrote', os.path.splitext(a.out)[0] + '.pdf')


if __name__ == '__main__':
    main()

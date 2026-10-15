"""Pronounced sounds, contextual meter selection, and browser/CLI agreement."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))

from arud import freeverse
from arud.classical import scan_hemistich, scan_pair, scan_line, rank_poem, compatible_endings, same_rhyme
from arud.lattice import build_hemistich, describe
from arud.meters import FORMS_BY_KEY


class ScannerRegressions(unittest.TestCase):
    def test_tanwin_survives_enjambment(self):
        results, _ = freeverse.analyze(['يَدٌ', 'تَاهَتْ'], meter='kamil')
        self.assertGreater(results[0]['errors'], 0)
        letters = ''.join(f[1] for line in results[0]['lines'] for f in line.feet)
        self.assertIn('يدن', letters)
        correct, _ = freeverse.analyze(['يَدٌ', 'تَاهَتْ'], meter='hazaj')
        self.assertEqual(correct[0]['errors'], 0)

    def test_forced_family_has_text_and_json_evidence(self):
        args = [sys.executable, str(SKILL / 'scripts/scan.py'), 'analyze',
                'يَدٌ\nتَاهَتْ', '--mode', 'free', '--meter', 'kamil']
        text = subprocess.run(args, check=True, text=True, capture_output=True).stdout
        self.assertIn('متفاعلن', text)
        payload = json.loads(subprocess.run(args + ['--json'], check=True,
                                           text=True, capture_output=True).stdout)
        self.assertEqual(payload[0]['meter'], 'kamil')
        self.assertEqual(len(payload[0]['lines']), 2)
        self.assertGreater(payload[0]['errors'], 0)

    def test_alif_is_preserved_before_a_paused_final_consonant(self):
        self.assertEqual(describe(build_hemistich('كِتَابْ')), ('كتاب', '1100'))
        form = FORMS_BY_KEY['mutaqarib/تام']
        scan = scan_hemistich('فَعُولُنْ فَعُولُنْ فَعُولُنْ كِتَابْ', form, 'ajuz')
        self.assertEqual(scan.errors, 0)
        self.assertEqual(scan.ending_label, 'ضرب مقصور')
        self.assertEqual(scan.feet[-1].got, '1100')
        self.assertTrue(describe(build_hemistich('فِي الْبَيْتِ'))[0].startswith('فل'))

    def test_genuine_enjambment_still_scans(self):
        lines = (SKILL / 'tests/free_verse_kamil.txt').read_text().splitlines()
        results, _ = freeverse.analyze(lines, meter='kamil')
        self.assertEqual(results[0]['errors'], 0)
        self.assertTrue(any(f[4] for line in results[0]['lines'] for f in line.feet))

    def test_tasri_requires_matching_weight_rhyme_and_first_verse(self):
        form = FORMS_BY_KEY['tawil/تام']
        normal = 'فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ'
        expanded = 'فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِيلُنْ'
        different_rhyme = 'فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَنَادِيلْ'
        def errors(pair):
            return pair[1].errors + pair[2].errors
        self.assertGreater(errors(scan_pair(expanded, normal, form, first=True)), 0)
        self.assertGreater(errors(scan_pair(expanded, different_rhyme, form, first=True)), 0)
        self.assertEqual(errors(scan_pair(expanded, expanded, form, first=True)), 0)
        self.assertGreater(errors(scan_pair(expanded, expanded, form, first=False)), 0)
        self.assertGreater(scan_hemistich(expanded, form, 'sadr').errors, 0)
        source = ('أَرَاكَ عَصِيَّ الدَّمْعِ شِيمَتُكَ الصَّبْرُ * '
                  'أَمَا لِلْهَوَى نَهْيٌ عَلَيْكَ وَلَا أَمْرُ')
        scans = [scan_line(i, source, [form]) for i in range(2)]
        result = rank_poem(scans, [form])[0]
        self.assertEqual(result['exact'], 1)
        self.assertEqual(result['per_line'][0][1][1].errors, 0)
        self.assertGreater(result['per_line'][1][1][1].errors, 0)

    def test_madid_rejects_an_unlicensed_ending_pair(self):
        form = next(f for f in FORMS_BY_KEY.values() if f.meter == 'madid')
        full = 'فَاعِلَاتُنْ فَاعِلُنْ فَاعِلَاتُنْ'
        short = 'فَاعِلَاتُنْ فَاعِلُنْ فَاعِلُنْ'
        invalid = scan_pair(full, short, form, first=True)
        self.assertGreater(invalid[1].errors + invalid[2].errors, 0)
        for sadr, ajuz in [(full, full), (short, short)]:
            pair = scan_pair(sadr, ajuz, form, first=True)
            self.assertEqual(pair[1].errors + pair[2].errors, 0)

    def test_single_forms_have_no_sadr_pair_constraint(self):
        form = FORMS_BY_KEY['rajaz/مشطور']
        full = 'مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ'
        cut = 'مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلْ'
        scans = [scan_line(i, line, [form]) for i, line in enumerate([full, cut])]
        result = rank_poem(scans, [form])[0]
        self.assertEqual(result['exact'], 2)
        self.assertTrue(compatible_endings(None, result['per_line'][0][1][2], form))
        self.assertFalse(compatible_endings(None, result['per_line'][0][1][2], FORMS_BY_KEY['tawil/تام']))

    def test_tasri_rhyme_candidates_respect_ridf_and_tasis(self):
        self.assertFalse(same_rhyme('دَارُ', 'نَهْرُ'))
        self.assertFalse(same_rhyme('عَامِلُ', 'مُنْزِلُ'))
        self.assertTrue(same_rhyme('دَارُ', 'نَارُ'))

    def test_full_basit_does_not_accept_unlicensed_fa_ilun_endings(self):
        form = FORMS_BY_KEY['basit/تام']
        half = 'مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ'
        for part in ['sadr', 'ajuz']:
            self.assertGreater(scan_hemistich(half, form, part).errors, 0)

    @unittest.skipUnless(shutil.which('node'), 'Node is required for browser engine checks')
    def test_browser_preserves_the_same_sounds(self):
        script = """
const fs = require('fs');
const A = require('./assets/workbench/engine.js');
A.load(JSON.parse(fs.readFileSync('./assets/workbench/meters.json', 'utf8')));
const result = A.analyze(['يَدٌ', 'تَاهَتْ'], {mode:'free', meter:'kamil'}).free[0];
const slots = A.buildHemistich('كِتَابْ');
const half = A.verifyLine('فَعُولُنْ فَعُولُنْ فَعُولُنْ كِتَابْ', 'mutaqarib', 'classical');
console.log(JSON.stringify({errors: result.errors,
  letters: result.lines.flatMap(l => l.feet.map(f => f.letters)).join(''),
  pattern: slots.map(s => s.opts[0].bits).join(''),
  ending: half.parts[0].ending,
  tasri: A.verifyLine('فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِيلُنْ * فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ', 'tawil', 'classical').ok,
  basit: A.verifyLine('مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ', 'basit', 'classical').ok,
  ridf: A.rhymeCheck(['دَارُ','نَهْرُ']).rows.map(r => r.ridf),
  tasis: A.rhymeCheck(['عَامِلُ','مُنْزِلُ']).rows.map(r => r.tasis),
  validTasri: A.verifyLine('أَرَاكَ عَصِيَّ الدَّمْعِ شِيمَتُكَ الصَّبْرُ * أَمَا لِلْهَوَى نَهْيٌ عَلَيْكَ وَلَا أَمْرُ', 'tawil', 'classical').ok,
  madid: A.verifyLine('فَاعِلَاتُنْ فَاعِلُنْ فَاعِلَاتُنْ * فَاعِلَاتُنْ فَاعِلُنْ فَاعِلُنْ', 'madid', 'classical').ok}));
"""
        run = subprocess.run(['node', '-e', script], cwd=SKILL, check=True,
                             text=True, capture_output=True)
        result = json.loads(run.stdout)
        self.assertGreater(result['errors'], 0)
        self.assertIn('يدن', result['letters'])
        self.assertEqual(result['pattern'], '1100')
        self.assertEqual(result['ending'], 'ضرب مقصور')
        self.assertFalse(result['tasri'])
        self.assertFalse(result['madid'])
        self.assertFalse(result['basit'])
        self.assertEqual(result['ridf'], ['ا', None])
        self.assertEqual(result['tasis'], [True, False])
        self.assertTrue(result['validTasri'])


if __name__ == '__main__':
    unittest.main()

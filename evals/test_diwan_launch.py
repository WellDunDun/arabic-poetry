"""Check runner isolation and generated-draft evidence without calling a model."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class DiwanLaunchRunnerTests(unittest.TestCase):
    def test_case_context_and_generated_draft_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / 'skill'
            skill.mkdir()
            (skill / 'SKILL.md').write_text('# Fixture skill\n')
            binaries = root / 'bin'
            binaries.mkdir()
            fake = binaries / 'codex'
            fake.write_text(f'#!{sys.executable}\n' + '''import json, subprocess, sys
from pathlib import Path
if '--version' in sys.argv:
    print('offline runner fixture')
    raise SystemExit(0)
sys.stdin.read()
source = Path('current.txt')
text = source.read_text() if source.exists() else 'new poem'
initial = {'title':'fixture', 'text':text + '\\nrevised', 'status':'review'}
page = Path('draft.html').resolve()
page.write_text('<script>window.DiwanInitialPoem=' + json.dumps(initial) + ';</script>')
subprocess.run([sys.executable, 'open_local.py', str(page)], check=True, capture_output=True)
Path(sys.argv[sys.argv.index('--output-last-message') + 1]).write_text(text)
print(json.dumps({'type':'turn.completed'}))
''')
            fake.chmod(0o755)
            suite = root / 'suite.json'
            suite.write_text(json.dumps({
                'suite_id': 'offline-runner-fixture',
                'context': {'title': 'original', 'poem': 'original poem'},
                'cases': [
                    {'id': 'inherited', 'request': 'revise', 'viewer_available': True},
                    {'id': 'fresh', 'request': 'compose', 'context': None, 'viewer_available': True},
                    {'id': 'override', 'request': 'revise', 'viewer_available': True,
                     'context': {'title': 'other', 'poem': 'other poem'}}
                ]
            }))
            output = root / 'output'
            result = subprocess.run([
                sys.executable, str(Path(__file__).with_name('run_diwan_launch.py')),
                '--skill', str(skill), '--output', str(output), '--condition', 'fixture',
                '--suite', str(suite)
            ], env=dict(os.environ, PATH=str(binaries) + os.pathsep + os.environ['PATH']),
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((output / 'runs.json').read_text())
            self.assertEqual([c['response'] for c in report['cases']],
                             ['original poem', 'new poem', 'other poem'])
            self.assertFalse((output / 'fresh/current.txt').exists())
            for case in report['cases']:
                self.assertTrue(case['poem_unchanged'])
                self.assertTrue(case['package_unchanged'])
                self.assertTrue(case['opener_unchanged'])
                self.assertTrue(case['receipt_matches_file'])
                self.assertEqual(case['html'][0]['initial_poem']['text'], case['response'] + '\nrevised')
                self.assertEqual(case['html'][0]['initial_poem']['status'], 'review')
                self.assertFalse(case['html'][0]['initial_text_matches'])
                page = Path(case['opened']['path'])
                self.assertEqual(case['opened']['sha256'], hashlib.sha256(page.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()

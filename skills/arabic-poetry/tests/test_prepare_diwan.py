"""Private, preloaded editor handoff regressions; no publishing or model calls."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import prepare_diwan


class PreparedDiwanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='diwan-launch-test-')
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        self.input = self.workspace / 'current.txt'
        self.text = 'لَمْ أبع الوعد ولم أنسَ وجهك\nنصٌّ آخر </script><script>throw Error("injected")</script>\u2028&'
        self.input.write_text(self.text, encoding='utf-8')

    def prepare(self, **kwargs):
        return prepare_diwan.prepare(self.input, self.workspace, 'current-poem', 'قصيدة <خاصة>', **kwargs)

    def test_exact_poem_safely_embedded_and_no_open_claim(self):
        report = self.prepare()
        page = Path(report['path']).read_text(encoding='utf-8')
        script = re.search(r'<script>window.DiwanInitialPoem=(.*?);</script>', page).group(1)
        self.assertNotIn('<', script)
        poem = json.loads(script)
        self.assertEqual(poem['text'], self.text)
        self.assertEqual(poem['status'], 'review')
        self.assertEqual(poem['title'], 'قصيدة <خاصة>')
        self.assertFalse(report['opened'])
        self.assertEqual(report['url'], Path(report['path']).as_uri())
        self.assertEqual(Path(report['path']).parent, self.workspace / '.diwan')
        self.assertEqual((self.workspace / '.diwan/.gitignore').read_text(), '*\n')
        result = subprocess.run(['node', '-e', 'const vm=require("node:vm"); const c={window:{}}; vm.runInNewContext("window.DiwanInitialPoem="+process.argv[1],c); console.log(JSON.stringify(c.window.DiwanInitialPoem));', script], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['text'], self.text)

    def test_repeat_preparation_reuses_private_file_without_modifying_template(self):
        source = prepare_diwan.SKILL / 'assets/workbench/diwan.html'
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        first = self.prepare()
        contents = Path(first['path']).read_bytes()
        self.assertEqual(first, self.prepare())
        self.assertEqual(contents, Path(first['path']).read_bytes())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        if os.name == 'posix':
            self.assertEqual(Path(first['path']).stat().st_mode & 0o777, 0o600)
        self.assertEqual(list((self.workspace / '.diwan').glob('.diwan-*.tmp')), [])

    def test_workspace_and_supplied_revision_have_separate_identities(self):
        first = self.prepare()
        self.input.write_text('revised in chat', encoding='utf-8')
        changed = self.prepare()
        self.assertEqual(first['path'], changed['path'])
        self.assertNotEqual(first['poem_id'], changed['poem_id'])
        other = prepare_diwan.prepare(self.input, self.workspace / 'another-workspace', 'current-poem', 'قصيدة <خاصة>')
        self.assertNotEqual(changed['poem_id'], other['poem_id'])

    def test_invalid_id_and_installed_output_are_rejected(self):
        for identity in ('../other', '', 'x' * 65):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                prepare_diwan.prepare(self.input, self.workspace, identity, 'عنوان')
        with self.assertRaisesRegex(ValueError, 'outside'):
            prepare_diwan.prepare(self.input, prepare_diwan.SKILL / 'assets', 'current', 'عنوان')

    def test_empty_poem_and_input_output_collision_preserve_input(self):
        self.input.write_text('  \n')
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            self.prepare()
        self.input = self.workspace / '.diwan/diwan-current-poem.html'
        self.input.parent.mkdir(exist_ok=True)
        self.input.write_text('original poem')
        with self.assertRaisesRegex(ValueError, 'different files'):
            self.prepare()
        self.assertEqual(self.input.read_text(), 'original poem')

    def test_builder_help_and_unknown_flags_do_not_build(self):
        builder = prepare_diwan.SKILL / 'scripts/build_workbench.py'
        for flag, expected in (('--help', 0), ('--unknown-option', 2)):
            result = subprocess.run([sys.executable, str(builder), flag], cwd=self.workspace,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected)
            self.assertFalse((self.workspace / flag).exists())


if __name__ == '__main__':
    unittest.main()

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plugin_version', ROOT / 'scripts/plugin_version.py')
versions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(versions)


class PluginVersions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in versions.FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        self.current = versions.declarations(self.root)[2]
        parts = list(versions.version_tuple(self.current))
        parts[-1] += 1
        self.next = '.'.join(map(str, parts))

    def test_release_updates_every_declaration_and_is_repeatable(self):
        unrelated = self.root / 'poem.txt'
        unrelated.write_text('قِفَا نَبْكِ', encoding='utf-8')
        versions.set_version(self.root, self.next)
        first = {name: (self.root / name).read_bytes() for name in versions.FILES}
        self.assertEqual(versions.declarations(self.root)[2], self.next)
        versions.set_version(self.root, self.next)
        self.assertEqual(first, {name: (self.root / name).read_bytes() for name in versions.FILES})
        self.assertEqual(unrelated.read_text(encoding='utf-8'), 'قِفَا نَبْكِ')

    def test_mismatch_stops_release_without_writing(self):
        path = self.root / versions.FILES[1]
        data = json.loads(path.read_text())
        data['version'] = self.next
        path.write_text(json.dumps(data))
        before = {name: (self.root / name).read_bytes() for name in versions.FILES}
        with self.assertRaisesRegex(ValueError, 'differ'):
            versions.set_version(self.root, self.next)
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in versions.FILES})

    def test_invalid_versions_and_downgrades_do_not_write(self):
        before = {name: (self.root / name).read_bytes() for name in versions.FILES}
        for value in ('01.2.3', '1.2', '1.2.3-beta', '1.2.3٤', 'not-a-version', '0.0.0'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                versions.set_version(self.root, value)
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in versions.FILES})


if __name__ == '__main__':
    unittest.main()

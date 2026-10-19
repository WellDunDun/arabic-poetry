import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('package_directory', ROOT / 'scripts/package_directory.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class DirectoryPackage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        for name in ('plugin.json', '.claude-plugin', 'assets/plugin', *package.DOCUMENTS):
            source, target = ROOT / name, self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        skill = self.root / 'skills/arabic-poetry'
        shutil.copytree(ROOT / 'skills/arabic-poetry', skill, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('tests/fixture.txt', 'evals/fixture.txt', '.agents/plugins/marketplace.json'):
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('not part of the submission')
        subprocess.run(['git', 'init', '-q', str(self.root)], env=package.git_env(), check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, env=package.git_env(), check=True)
        subprocess.run(['git', '-c', 'user.name=Package test', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'Fixture'], cwd=self.root, env=package.git_env(), check=True)
        self.skill_files = set(package.git(
            self.root, 'ls-files', '-z', '--', 'skills').decode().strip('\0').split('\0'))

    def change_interface(self, key, value):
        path = self.root / 'plugin.json'
        data = json.loads(path.read_text())
        data['extensions']['com.openai']['interface'][key] = value
        path.write_text(json.dumps(data))

    def test_reproducible_archive_preserves_skill_and_omits_nonpackage_files(self):
        (self.root / 'skills/arabic-poetry/private-poem.txt').write_text('private')
        (self.root / '.env').write_text('secret')
        output = Path(self.temp.name) / 'candidate.zip'
        report = package.build(self.root, output)
        first = output.read_bytes()
        self.assertEqual(report, package.build(self.root, output))
        self.assertEqual(first, output.read_bytes())
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertEqual({n for n in names if n.startswith('skills/')}, self.skill_files)
            self.assertEqual(set(names), self.skill_files | set(package.DOCUMENTS) |
                             {'plugin.json', '.claude-plugin/plugin.json', 'assets/plugin/icon.svg'})
            self.assertNotIn('skills/arabic-poetry/private-poem.txt', names)
            self.assertNotIn('.env', names)
            self.assertNotIn('.claude-plugin/marketplace.json', names)
            self.assertFalse(any(n.startswith(('evals/', 'tests/', '.git/', '.agents/')) for n in names))
            for name in names:
                self.assertEqual(archive.read(name), (self.root / name).read_bytes())
            self.assertIn('skills/arabic-poetry/assets/fonts/OFL.txt', names)

    def test_public_listing_limits_are_stricter_than_draft_upload(self):
        self.change_interface('shortDescription', 'x' * 31)
        with self.assertRaisesRegex(ValueError, 'shortDescription'):
            package.package_files(self.root)

    def test_escaping_icon_is_rejected(self):
        self.change_interface('logo', './assets/plugin/../../private.svg')
        with self.assertRaisesRegex(ValueError, 'logo'):
            package.package_files(self.root)

    def test_nonsquare_icon_is_rejected(self):
        (self.root / 'assets/plugin/icon.svg').write_text('<svg viewBox="0 0 48 49"/>')
        with self.assertRaisesRegex(ValueError, 'square'):
            package.package_files(self.root)

    def test_version_mismatch_is_rejected(self):
        path = self.root / '.claude-plugin/plugin.json'
        data = json.loads(path.read_text())
        data['version'] = '99.0.0'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'differ'):
            package.package_files(self.root)

    def test_generated_output_cannot_pollute_checkout(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            package.build(self.root, self.root / 'release.zip')

    def test_dirty_package_inputs_cannot_be_released(self):
        (self.root / 'PRIVACY.md').write_text('uncommitted policy')
        with self.assertRaisesRegex(ValueError, 'Commit package inputs'):
            package.build(self.root, Path(self.temp.name) / 'candidate.zip')

    def test_report_cannot_overwrite_archive(self):
        output = Path(self.temp.name) / 'candidate.json'
        with self.assertRaisesRegex(ValueError, '.zip'):
            package.build(self.root, output)
        self.assertFalse(output.exists())

    def test_git_environment_cannot_redirect_repository_reads(self):
        with patch.dict('os.environ', {'GIT_DIR': '/missing', 'GIT_WORK_TREE': '/missing',
                                      'GIT_INDEX_FILE': '/missing', 'GIT_CONFIG_COUNT': 'bogus'}):
            self.assertEqual({n for n in package.package_files(self.root)[1] if n.startswith('skills/')},
                             self.skill_files)

    def test_missing_icon_fails_before_archive_is_written(self):
        (self.root / 'assets/plugin/icon.svg').unlink()
        output = Path(self.temp.name) / 'candidate.zip'
        with self.assertRaises(FileNotFoundError):
            package.build(self.root, output)
        self.assertFalse(output.exists())

    def test_staged_skill_removal_cannot_disappear_from_inventory(self):
        subprocess.run(['git', 'rm', '--cached', 'skills/arabic-poetry/tests/gold_verses.tsv'],
                       cwd=self.root, env=package.git_env(), check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, 'Commit package inputs'):
            package.build(self.root, Path(self.temp.name) / 'candidate.zip')

    def test_staged_skill_addition_requires_commit(self):
        p = self.root / 'skills/arabic-poetry/references/new.md'
        p.write_text('new reference')
        subprocess.run(['git', 'add', str(p)], cwd=self.root, env=package.git_env(), check=True)
        with self.assertRaisesRegex(ValueError, 'Commit package inputs'):
            package.build(self.root, Path(self.temp.name) / 'candidate.zip')


if __name__ == '__main__':
    unittest.main()

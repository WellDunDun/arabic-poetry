import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import github_release as releases
import plugin_version as versions

REPOSITORY = 'WellDunDun/arabic-poetry'
NOTES = '''# Arabic Poetry {version}

## English

Automatic suggestions and safe updates.
Read the [update guide](../../INSTALL.md).

## العربية

اقتراحات تلقائية وتحديثات آمنة.
اتبع [دليل التحديث](../../INSTALL.md).
'''


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', 'main')
        source = SCRIPTS.parent
        for name in versions.FILES:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((source / name).read_bytes())
        self.current = versions.declarations(self.root)[2]
        a, b, c = versions.version_tuple(self.current)
        self.next = f'{a}.{b}.{c + 1}'
        self.before = self.commit()
        versions.set_version(self.root, self.next)
        self.notes = self.root / f'docs/releases/{self.next}.md'
        self.notes.parent.mkdir(parents=True)
        self.notes.write_text(NOTES.format(version=self.next), encoding='utf-8')
        self.after = self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Release test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'Fixture')
        return self.git('rev-parse', 'HEAD')

    def plan(self, before=None, after=None):
        return releases.plan(self.root, before or self.before, after or self.after, REPOSITORY)

    def test_version_bump_uses_exact_commit_and_both_reviewed_languages(self):
        result = self.plan()
        self.assertTrue(result['publish'])
        self.assertEqual(result['tag'], 'v' + self.next)
        self.assertEqual(result['commit'], self.after)
        self.assertIn('## English', result['body'])
        self.assertIn('## العربية', result['body'])
        self.assertIn(f'/blob/{self.after}/INSTALL.md', result['body'])
        self.assertNotIn('../../INSTALL.md', result['body'])

    def test_unchanged_version_does_not_republish_or_require_notes(self):
        self.notes.unlink()
        later = self.commit()
        self.assertFalse(self.plan(before=self.after, after=later)['publish'])

    def test_working_tree_notes_cannot_change_release_body(self):
        self.notes.write_text('uncommitted changes', encoding='utf-8')
        self.assertIn('اقتراحات تلقائية', self.plan()['body'])

    def test_pr_behind_base_is_validated_using_its_prospective_merge(self):
        self.git('checkout', '-qb', 'updated-base', self.before)
        (self.root / 'maintenance.txt').write_text('A newer main commit\n')
        newer_base = self.commit()
        with self.assertRaises(ValueError):
            self.plan(before=newer_base, after=self.after)
        self.git('-c', 'user.name=Release test', '-c', 'user.email=test@example.invalid',
                 'merge', '--no-edit', self.after)
        result = self.plan(before=newer_base, after=self.git('rev-parse', 'HEAD'))
        self.assertTrue(result['publish'])
        self.assertEqual(result['version'], self.next)

    def test_all_manifests_must_agree(self):
        p = self.root / versions.FILES[1]
        data = json.loads(p.read_text())
        data['version'] = self.current
        p.write_text(json.dumps(data))
        after = self.commit()
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.plan(after=after)

    def test_version_decrease_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'decrease'):
            self.plan(before=self.after, after=self.before)

    def test_missing_version_specific_notes_fail(self):
        self.notes.unlink()
        with self.assertRaisesRegex(ValueError, 'notes'):
            self.plan(after=self.commit())

    def test_both_language_sections_need_content_in_their_language(self):
        for bad in ['## English\n\n## العربية\nنص',
                    '## English\nEnglish notes\n## العربية\n',
                    '## English\nEnglish notes\n## العربية\nTODO',
                    '## English\nنص فقط\n## العربية\nنص عربي']:
            with self.subTest(notes=bad):
                self.notes.write_text(bad, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'English|العربية'):
                    self.plan(after=self.commit())

    def test_headings_inside_code_fences_do_not_count_as_translations(self):
        self.notes.write_text('```md\n## English\nEnglish text\n## العربية\nنص عربي\n```\n')
        with self.assertRaisesRegex(ValueError, 'English|العربية'):
            self.plan(after=self.commit())

    def test_shorter_nested_fence_does_not_expose_fake_language_sections(self):
        self.notes.write_text('````md\n```\n## English\nEnglish text\n## العربية\nنص عربي\n````\n')
        with self.assertRaisesRegex(ValueError, 'English|العربية'):
            self.plan(after=self.commit())

    def test_plugin_names_must_agree(self):
        path = self.root / 'plugin.json'
        data = json.loads(path.read_text())
        data['name'] = 'another-plugin'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'declaration'):
            self.plan(after=self.commit())

    def test_duplicate_language_sections_fail(self):
        self.notes.write_text(NOTES.format(version=self.next) + '\n## English\nMore notes\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.plan(after=self.commit())

    def test_bad_revision_or_repository_fails_without_network(self):
        for before in ['main', '0' * 40, '--help']:
            with self.subTest(before=before), self.assertRaises(ValueError):
                self.plan(before=before)
        with self.assertRaises(ValueError):
            releases.plan(self.root, self.before, self.after, '../wrong/repo')

    def test_relative_links_are_pinned_and_external_or_anchor_links_unchanged(self):
        self.notes.write_text(NOTES.format(version=self.next) + '\n[web](https://example.com) [here](#english) [root](/README.md)\n')
        body = self.plan(after=self.commit())['body']
        self.assertIn('[web](https://example.com)', body)
        self.assertIn('[here](#english)', body)
        self.assertIn('/blob/', body)
        self.assertTrue(body.rstrip().endswith('/README.md)'))


class FakeGitHub:
    def __init__(self, commit='a' * 40, existing=False, tag=False):
        self.commit = commit
        self.release = {'tag_name': 'v0.3.2', 'name': 'Arabic Poetry v0.3.2',
                        'body': '## English\nNotes\n## العربية\nنص',
                        'draft': False, 'prerelease': False,
                        'html_url': 'https://github.com/example/repo/releases/tag/v0.3.2'} if existing else None
        self.tag = {'object': {'type': 'commit', 'sha': commit}} if tag else None
        self.calls = []

    def request(self, method, path, data=None, missing=False):
        self.calls.append((method, path, data))
        if method == 'POST':
            if self.release is not None:
                raise RuntimeError('Duplicate release')
            self.tag = {'object': {'type': 'commit', 'sha': data['target_commitish']}}
            self.release = dict(data, html_url='https://github.com/example/repo/releases/tag/v0.3.2')
            return self.release
        if path.startswith('git/ref/tags/'):
            return self.tag
        if path == 'git/tags/annotated':
            return {'object': {'type': 'commit', 'sha': self.commit}}
        if path.startswith('releases/tags/'):
            return self.release
        raise AssertionError(path)


class Publication(unittest.TestCase):
    def setUp(self):
        self.plan = {'publish': True, 'version': '0.3.2', 'tag': 'v0.3.2',
                     'commit': 'a' * 40, 'name': 'Arabic Poetry v0.3.2',
                     'body': '## English\nNotes\n## العربية\nنص'}

    def test_first_publication_targets_exact_commit_and_uses_reviewed_notes(self):
        api = FakeGitHub()
        releases.publish(self.plan, api)
        posts = [c for c in api.calls if c[0] == 'POST']
        self.assertEqual(len(posts), 1)
        payload = posts[0][2]
        self.assertEqual(payload['target_commitish'], self.plan['commit'])
        self.assertEqual(payload['body'], self.plan['body'])
        self.assertFalse(payload['draft'])
        self.assertFalse(payload['prerelease'])
        self.assertEqual(payload['make_latest'], 'legacy')

    def test_rerun_is_idempotent(self):
        api = FakeGitHub()
        releases.publish(self.plan, api)
        before = list(api.calls)
        releases.publish(self.plan, api)
        self.assertEqual(sum(c[0] == 'POST' for c in api.calls), 1)
        self.assertGreater(len(api.calls), len(before))

    def test_existing_tag_can_recover_missing_release(self):
        api = FakeGitHub(tag=True)
        releases.publish(self.plan, api)
        self.assertEqual(sum(c[0] == 'POST' for c in api.calls), 1)

    def test_foreign_tag_is_never_moved_or_released(self):
        api = FakeGitHub(commit='b' * 40, tag=True)
        with self.assertRaisesRegex(ValueError, 'tag'):
            releases.publish(self.plan, api)
        self.assertFalse(any(c[0] != 'GET' for c in api.calls))

    def test_annotated_tag_is_resolved_to_its_commit(self):
        api = FakeGitHub(existing=True)
        api.tag = {'object': {'type': 'tag', 'sha': 'annotated'}}
        releases.publish(self.plan, api)
        self.assertFalse(any(c[0] != 'GET' for c in api.calls))

    def test_existing_release_cannot_be_overwritten(self):
        for field, value in [('body', 'different'), ('body', None), ('draft', True), ('prerelease', True)]:
            api = FakeGitHub(existing=True, tag=True)
            api.release[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'release'):
                releases.publish(self.plan, api)
            self.assertFalse(any(c[0] != 'GET' for c in api.calls))

    def test_network_or_permission_failure_is_not_treated_as_absence(self):
        api = FakeGitHub()
        with patch.object(api, 'request', side_effect=RuntimeError('HTTP 403')):
            with self.assertRaisesRegex(RuntimeError, '403'):
                releases.publish(self.plan, api)
        self.assertIsNone(api.release)

    def test_read_back_checks_actual_published_response(self):
        api = FakeGitHub()
        original = api.request
        def wrong(method, path, data=None, missing=False):
            result = original(method, path, data, missing)
            if method == 'POST':
                result['draft'] = True
            return result
        with patch.object(api, 'request', side_effect=wrong):
            with self.assertRaisesRegex(ValueError, 'release'):
                releases.publish(self.plan, api)
        self.assertEqual(sum(c[0] == 'POST' for c in api.calls), 1)

    def test_only_404_is_missing_at_http_boundary(self):
        api = releases.GitHub(REPOSITORY, 'test-token')
        for code in (401, 403, 429, 500):
            with self.subTest(code=code), patch('urllib.request.urlopen', side_effect=HTTPError('https://api.github.com', code, 'failure', {}, None)):
                with self.assertRaises(RuntimeError):
                    api.request('GET', 'releases/tags/v0.3.2', missing=True)
        with patch('urllib.request.urlopen', side_effect=HTTPError('https://api.github.com', 404, 'missing', {}, None)):
            self.assertIsNone(api.request('GET', 'releases/tags/v0.3.2', missing=True))


if __name__ == '__main__':
    unittest.main()

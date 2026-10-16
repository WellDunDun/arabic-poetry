"""Exercise acceptance and coordinated-mutation failures in saved eval evidence."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import check_results


class EvidenceIntegrityTests(unittest.TestCase):
    """Mutate isolated copies while keeping the recorded source trials intact."""

    def setUp(self):
        """Copy the complete known-good package and evidence for each mutation."""
        self.temp = tempfile.TemporaryDirectory(prefix='poetry-evidence-test-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        source = Path(__file__).resolve().parent
        self.root = self.repo / 'evals'
        self.root.mkdir()
        for name in ['prompts.json', 'rubric.json']:
            shutil.copy2(source / name, self.root / name)
        shutil.copytree(source.parent / 'skills', self.repo / 'skills',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.results = self.root / 'results'
        shutil.copytree(source / 'results/2026-10-16', self.results)

    @staticmethod
    def sha(path):
        """Hash the exact copied bytes used by a record's checksum."""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def update(self, name, mutate, root=None):
        """Apply a JSON mutation without changing any original evidence file."""
        path = (root or self.results) / name
        data = json.loads(path.read_text(encoding='utf-8'))
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def rehash_artifacts(self):
        """Keep editable metadata consistent to expose deeper inventory checks."""
        self.update('runs.json', lambda data: data.update(
            artifacts_sha256=self.sha(self.results / 'artifacts.json')))

    def check(self):
        """Run the production validator against the isolated trial copy."""
        with redirect_stdout(io.StringIO()):
            check_results.check(self.root, self.results)

    def test_valid_evidence_passes(self):
        """The saved trial remains usable without temporary generated artifacts."""
        self.check()

    def test_false_pass_is_rejected(self):
        """A failed criterion cannot be hidden by a passing case summary."""
        self.update('grades.json', lambda data: data['current-both']['provisional-reading'].update(status='pass'))
        with self.assertRaisesRegex(ValueError, 'case status'):
            self.check()

    def test_false_fail_is_rejected(self):
        """A fully passing case cannot retain a stale failure summary."""
        self.update('grades.json', lambda data: data['combined']['prose-compose'].update(status='fail'))
        with self.assertRaisesRegex(ValueError, 'case status'):
            self.check()

    def test_not_applicable_criterion_does_not_fail_case(self):
        """An excluded criterion leaves passing applicable judgments intact."""
        self.update('grades.json', lambda data: data['combined']['prose-compose']['criteria'][0].update(status='not_applicable'))
        self.check()

    def test_coordinated_prompt_edit_is_rejected(self):
        """Changing a request and its editable checksum does not change the freeze."""
        self.update('prompts.json', lambda data: data['cases'][0].update(request='Changed request'), self.root)
        self.update('runs.json', lambda data: data.update(prompts_sha256=self.sha(self.root / 'prompts.json')))
        with self.assertRaisesRegex(ValueError, 'corpus snapshot'):
            self.check()

    def test_coordinated_rubric_edit_is_rejected(self):
        """Changing criterion wording and its checksum violates the frozen corpus."""
        self.update('rubric.json', lambda data: data['criteria']['prose-compose'].__setitem__(0, 'Changed criterion'), self.root)
        self.update('runs.json', lambda data: data.update(rubric_sha256=self.sha(self.root / 'rubric.json')))
        with self.assertRaisesRegex(ValueError, 'corpus snapshot'):
            self.check()

    def test_corpus_commit_cannot_be_repointed(self):
        """The provenance record cannot nominate an arbitrary replacement commit."""
        self.update('runs.json', lambda data: data.update(corpus_commit='0' * 40))
        with self.assertRaisesRegex(ValueError, 'Corpus commit'):
            self.check()

    def test_coordinated_baseline_manifest_edit_is_rejected(self):
        """A fake baseline file digest cannot be blessed by rehashing its manifest."""
        name = 'original-only.package-hashes.json'
        self.update(name, lambda data: data.update({'skills/arabic-poetry/SKILL.md': '0' * 64}))
        self.update('runs.json', lambda data: data['conditions']['original-only'].update(
            package_manifest_sha256=self.sha(self.results / name)))
        with self.assertRaisesRegex(ValueError, 'frozen baseline'):
            self.check()

    def test_missing_artifact_manifest_is_rejected(self):
        """The durable artifact inventory is required even when outputs are absent."""
        (self.results / 'artifacts.json').unlink()
        with self.assertRaises(OSError):
            self.check()

    def test_artifact_digest_mismatch_is_rejected(self):
        """An unrecorded inventory change must fail its checksum binding."""
        self.update('artifacts.json', lambda data: data['original-only'][0].update(bytes=0))
        with self.assertRaisesRegex(ValueError, 'Artifact manifest changed'):
            self.check()

    def test_truncated_inventory_is_rejected_after_rehash(self):
        """Rehashing cannot hide an artifact path recorded by a case."""
        self.update('artifacts.json', lambda data: data['original-only'].pop())
        self.rehash_artifacts()
        with self.assertRaisesRegex(ValueError, 'artifact inventory'):
            self.check()

    def test_wrong_artifact_case_is_rejected_after_rehash(self):
        """An inventory item must belong to a real request and recorded path."""
        self.update('artifacts.json', lambda data: data['original-only'][0].update(case_id='unknown'))
        self.rehash_artifacts()
        with self.assertRaisesRegex(ValueError, 'artifact case'):
            self.check()

    def test_duplicate_artifact_is_rejected_after_rehash(self):
        """Repeated inventory rows cannot inflate durable evidence counts."""
        self.update('artifacts.json', lambda data: data['original-only'].append(data['original-only'][0].copy()))
        self.rehash_artifacts()
        with self.assertRaisesRegex(ValueError, 'duplicate artifact'):
            self.check()

    def test_invalid_artifact_digest_is_rejected_after_rehash(self):
        """Artifact checksums must have the recorded SHA-256 format."""
        self.update('artifacts.json', lambda data: data['original-only'][0].update(sha256='invalid'))
        self.rehash_artifacts()
        with self.assertRaisesRegex(ValueError, 'artifact digest'):
            self.check()

    def test_negative_artifact_size_is_rejected_after_rehash(self):
        """Artifact sizes must represent nonnegative byte counts."""
        self.update('artifacts.json', lambda data: data['original-only'][0].update(bytes=-1))
        self.rehash_artifacts()
        with self.assertRaisesRegex(ValueError, 'artifact size'):
            self.check()


if __name__ == '__main__':
    unittest.main()

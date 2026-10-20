#!/usr/bin/env python3
"""Validate frozen-suite provenance and recorded evidence, not poetry quality."""
import argparse
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile


BASE_COMMIT = '3286f489881b9fbc5bb2fc2bca7dd064835b1a4c'
CORPUS_COMMIT = 'e1f91bf645fd0e06fc4fd94f89f67ca2cb00ee3a'
DEFAULT_RESULTS = Path(__file__).parent / 'results/2026-10-20-automatic-suggestions'


def read_json(path):
    """Load a UTF-8 evaluation record for protocol validation."""
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    """Report an evidence-contract failure through the CLI's error boundary."""
    if not condition:
        raise ValueError(message)


def digest(path):
    """Hash the exact bytes of a recorded file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def git_bytes(*args):
    """Read pinned history locally; shallow clones must fetch it explicitly."""
    repo = Path(__file__).resolve().parent.parent
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    require(result.returncode == 0,
            'Frozen Git history unavailable; fetch the pinned base and corpus commits before validating')
    return result.stdout


@lru_cache(maxsize=1)
def frozen_packages():
    """Derive baseline file digests from Git objects rather than editable metadata."""
    result = {}
    with tarfile.open(fileobj=io.BytesIO(git_bytes('archive', BASE_COMMIT, 'skills'))) as archive:
        for entry in archive:
            if entry.isfile():
                result[entry.name] = hashlib.sha256(archive.extractfile(entry).read()).hexdigest()
    return result


def check_artifacts(rows, cases, condition, ids):
    """Require a one-to-one inventory for the artifacts claimed by each response."""
    require(isinstance(rows, list), f'{condition}: invalid artifact inventory')
    indexed = set()
    for row in rows:
        require(row['case_id'] in ids, f'{condition}: unknown artifact case')
        require(isinstance(row['path'], str) and row['path'], f'{condition}: invalid artifact path')
        require(isinstance(row['sha256'], str) and re.fullmatch(r'[0-9a-f]{64}', row['sha256']),
                f'{condition}: invalid artifact digest')
        require(type(row['bytes']) is int and row['bytes'] >= 0, f'{condition}: invalid artifact size')
        key = (row['case_id'], row['path'])
        require(key not in indexed, f'{condition}: duplicate artifact inventory entry')
        indexed.add(key)
    expected = set()
    for case in cases:
        for path in case['artifacts']:
            require(isinstance(path, str) and path, f'{condition}: invalid response artifact path')
            key = (case['id'], path)
            require(key not in expected, f'{condition}: duplicate artifact claim')
            expected.add(key)
    require(indexed == expected, f'{condition}: artifact inventory differs from response records')


def check(root, results):
    """Validate corpus, package, response, grade and artifact record consistency."""
    prompts = read_json(root / 'prompts.json')
    rubric = read_json(root / 'rubric.json')
    runs = read_json(results / 'runs.json')
    grades = read_json(results / 'grades.json')
    ids = [row['id'] for row in prompts['cases']]
    conditions = ['original-only', 'prosody-only', 'current-both', 'combined']
    require(len(ids) == len(set(ids)) and ids, 'Prompt IDs must be unique and nonempty')
    require(set(ids) == set(rubric['criteria']), 'Rubric and request IDs differ')
    require(runs['suite_id'] == prompts['suite_id'] == rubric['suite_id'], 'Suite IDs differ')
    require(runs['corpus_commit'] == CORPUS_COMMIT, 'Corpus commit differs from the pinned snapshot')
    for name in ['prompts.json', 'rubric.json']:
        frozen = git_bytes('show', f'{CORPUS_COMMIT}:evals/{name}')
        require(digest(root / name) == hashlib.sha256(frozen).hexdigest(),
                f'{name} differs from the corpus snapshot')
    require(runs['prompts_sha256'] == digest(root / 'prompts.json'), 'Frozen requests changed')
    require(runs['rubric_sha256'] == digest(root / 'rubric.json'), 'Frozen criteria changed')
    require(runs['base_commit'] == rubric['frozen_base'] == BASE_COMMIT, 'Baseline commit differs')
    require(set(runs['conditions']) == set(conditions), 'Missing or unexpected conditions')
    require(set(grades) == set(conditions), 'Missing condition grades')
    artifacts_path = results / 'artifacts.json'
    require(digest(artifacts_path) == runs['artifacts_sha256'], 'Artifact manifest changed')
    artifacts = read_json(artifacts_path)
    require(set(artifacts) == set(conditions), 'Missing or unexpected artifact conditions')
    count = 0
    for condition in conditions:
        meta = runs['conditions'][condition]
        record_path = results / meta['record']
        require(digest(record_path) == meta['record_sha256'], f'{condition}: record changed')
        record = read_json(record_path)
        require(record['condition'] == condition, f'{condition}: wrong record identity')
        require([case['id'] for case in record['cases']] == ids, f'{condition}: missing/reordered cases')
        package_path = results / meta['package_manifest']
        require(digest(package_path) == meta['package_manifest_sha256'], f'{condition}: package manifest changed')
        hashes = read_json(package_path)
        require(hashes and all(re.fullmatch(r'[0-9a-f]{64}', h) for h in hashes.values()), f'{condition}: invalid package hashes')
        if condition == 'combined':
            actual = {str(path.relative_to(root.parent)): digest(path)
                      for path in (root.parent / 'skills').rglob('*')
                      if path.is_file() and '__pycache__' not in path.parts
                      and path.suffix != '.pyc' and path.name != '.DS_Store'}
            require(actual == hashes, 'Combined package differs from the evaluated snapshot; rerun the trial')
        else:
            installed = {'arabic-poetry'} if condition == 'original-only' else {'arabic-prosody'}
            if condition == 'current-both':
                installed = {'arabic-poetry', 'arabic-prosody'}
            expected = {path: value for path, value in frozen_packages().items()
                        if path.split('/')[1] in installed}
            require(hashes == expected, f'{condition}: package differs from the frozen baseline')
            require(meta['source'] == BASE_COMMIT, f'{condition}: baseline source commit differs')
        require(set(grades[condition]) == set(ids), f'{condition}: missing case grades')
        for case in record['cases']:
            label = f'{condition}/{case["id"]}'
            require(isinstance(case['response'], str) and case['response'].strip(), f'{label}: missing response')
            require(isinstance(case['artifacts'], list), f'{label}: missing artifact record')
            for command in case['commands']:
                require(isinstance(command['command'], (str, list)) and command['command'], f'{label}: missing command')
                require(isinstance(command['exit_code'], int), f'{label}: missing exit status')
                require(all(isinstance(command[key], str) for key in ['stdout', 'stderr']), f'{label}: missing command output')
            grade = grades[condition][case['id']]
            require(len(grade['criteria']) == len(rubric['criteria'][case['id']]), f'{label}: missing criterion judgments')
            for judgment in grade['criteria']:
                require(judgment['status'] in ['pass', 'fail', 'not_applicable'], f'{label}: invalid judgment')
                require(bool(judgment['evidence'].strip()), f'{label}: missing semantic evidence')
            expected_status = 'fail' if any(j['status'] == 'fail' for j in grade['criteria']) else 'pass'
            require(grade['status'] == expected_status, f'{label}: case status contradicts criterion judgments')
            count += 1
        check_artifacts(artifacts[condition], record['cases'], condition, ids)
    print(f'PASS: {len(conditions)} conditions, {count} response records, frozen criteria and evidence integrity')
    print('Semantic grades remain reviewer judgments; this check does not certify their correctness.')


def main():
    """Run saved evidence validation without regenerating or regrading responses."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    try:
        check(Path(__file__).parent, args.results)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Evaluation evidence invalid: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Validate frozen-suite provenance and recorded evidence, not poetry quality."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root, results):
    prompts = read_json(root / 'prompts.json')
    rubric = read_json(root / 'rubric.json')
    runs = read_json(results / 'runs.json')
    grades = read_json(results / 'grades.json')
    ids = [row['id'] for row in prompts['cases']]
    conditions = ['original-only', 'prosody-only', 'current-both', 'combined']
    require(len(ids) == len(set(ids)) and ids, 'Prompt IDs must be unique and nonempty')
    require(set(ids) == set(rubric['criteria']), 'Rubric and request IDs differ')
    require(runs['suite_id'] == prompts['suite_id'] == rubric['suite_id'], 'Suite IDs differ')
    require(runs['prompts_sha256'] == digest(root / 'prompts.json'), 'Frozen requests changed')
    require(runs['rubric_sha256'] == digest(root / 'rubric.json'), 'Frozen criteria changed')
    require(runs['base_commit'] == rubric['frozen_base'], 'Baseline commit differs')
    require(set(runs['conditions']) == set(conditions), 'Missing or unexpected conditions')
    require(set(grades) == set(conditions), 'Missing condition grades')
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
            count += 1
    print(f'PASS: {len(conditions)} conditions, {count} response records, frozen criteria and evidence integrity')
    print('Semantic grades remain reviewer judgments; this check does not certify their correctness.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=Path(__file__).parent / 'results/2026-10-16')
    args = parser.parse_args()
    try:
        check(Path(__file__).parent, args.results)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Evaluation evidence invalid: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

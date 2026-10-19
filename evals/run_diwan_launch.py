"""Run frozen Diwan launch requests through an isolated Codex CLI session.

The fixture opener records a local display request; it does not render HTML.
Use a real browser separately to verify the resulting editor and persistence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess

SUITE = Path(__file__).with_name('diwan-launch.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--condition', required=True)
    parser.add_argument('--case', action='append', help='Default: all frozen cases')
    parser.add_argument('--suite', type=Path, default=SUITE, help='Frozen request JSON, default: Diwan launch suite')
    args = parser.parse_args()
    suite = json.loads(args.suite.read_text(encoding='utf-8'))
    output = args.output.resolve()
    if output.exists():
        parser.error('Choose a new output directory to preserve prior receipts')
    output.mkdir(parents=True)
    installed = output / 'skill'
    shutil.copytree(args.skill, installed, ignore=shutil.ignore_patterns('__pycache__'))
    hashes = {p.relative_to(installed).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(installed.rglob('*')) if p.is_file()}
    for p in installed.rglob('*'):
        p.chmod(0o555 if p.is_dir() else 0o444)
    installed.chmod(0o555)
    version = subprocess.check_output(['codex', '--version'], text=True).strip()
    records = []
    for case in suite['cases']:
        if args.case and case['id'] not in args.case:
            continue
        work = output / case['id']
        work.mkdir()
        context = case.get('context', suite.get('context'))
        if context:
            (work / 'current.txt').write_text(context['poem'], encoding='utf-8')
        poem_before = hashlib.sha256((work / 'current.txt').read_bytes()).hexdigest() if context else None
        capability = 'No local HTML viewer or opener is available. You can still create files.'
        opener = None
        if case.get('viewer_available', False):
            opener = work / 'open_local.py'
            opener.write_text('''import hashlib, json, sys
from pathlib import Path
path = Path(sys.argv[1]).resolve()
if Path(__file__).parent not in path.parents or path.suffix != '.html' or not path.is_file():
    raise SystemExit('Expected a prepared HTML file inside this workspace')
receipt = {'path':str(path), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'display_request_accepted':True, 'rendered':False}
Path(__file__).with_name('opened.json').write_text(json.dumps(receipt))
print('Local viewer fixture accepted the file. This fixture records delivery, not rendered browser behavior.')
''', encoding='utf-8')
            capability = 'A local HTML viewer test fixture is available as `python3 open_local.py /absolute/path/to/file.html`. It records a display request but does not render HTML. No other viewer exists.'
        opener_before = hashlib.sha256(opener.read_bytes()).hexdigest() if opener else None
        poem_context = f"The current poem is in {work / 'current.txt'} and its title is «{context['title']}»." if context else ''
        prompt = f'''Use the arabic-poetry skill at {installed / 'SKILL.md'} for this request. {poem_context} Use only this skill and this workspace. Local Python, Node and file/command tools are available. Network, publishing, package installation, hosted databases and model-service connections are unavailable. Do not modify the installed skill. {capability}

User request:
{case['request']}
'''
        (work / 'request.txt').write_text(prompt, encoding='utf-8')
        command = ['codex', '--ask-for-approval', 'never', 'exec', '--ignore-user-config',
                   '--ignore-rules', '--ephemeral', '--sandbox', 'workspace-write',
                   '--skip-git-repo-check', '--json', '--output-last-message', str(work / 'response.txt'), '-']
        with (work / 'events.jsonl').open('w') as events, (work / 'stderr.txt').open('w') as errors:
            timed_out = False
            process = subprocess.Popen(command, text=True, cwd=work, stdin=subprocess.PIPE,
                                       stdout=events, stderr=errors, start_new_session=True)
            try:
                process.communicate(prompt, timeout=240)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                exit_code = 124
                errors.write('Evaluation timed out after 240 seconds\n')
        events = (work / 'events.jsonl').read_bytes()
        final_hashes = {p.relative_to(installed).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(installed.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
        html_files = []
        for path in sorted(work.rglob('*.html')):
            raw = path.read_bytes()
            row = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
            match = re.search(r'<script>window.DiwanInitialPoem=(.*?);</script>', raw.decode('utf-8'))
            if match:
                initial = json.loads(match.group(1))
                row['initial_poem'] = {key: initial[key] for key in ('title', 'text', 'status')}
                row['initial_text_matches'] = bool(context) and initial['text'] == context['poem']
                row['review_status'] = initial['status']
            html_files.append(row)
        opened = json.loads((work / 'opened.json').read_text()) if (work / 'opened.json').exists() else None
        opener_after = hashlib.sha256(opener.read_bytes()).hexdigest() if opener and opener.exists() else None
        records.append({'id': case['id'], 'exit_code': exit_code, 'timed_out': timed_out,
                        'package_unchanged': final_hashes == hashes,
                        'poem_unchanged': not context or (work / 'current.txt').exists() and hashlib.sha256((work / 'current.txt').read_bytes()).hexdigest() == poem_before,
                        'opener_unchanged': opener_before == opener_after,
                        'receipt_matches_file': opened is None or any(p['path'] == opened['path'] and p['sha256'] == opened['sha256'] for p in html_files),
                        'response': (work / 'response.txt').read_text() if (work / 'response.txt').exists() else '',
                        'events_sha256': hashlib.sha256(events).hexdigest(),
                        'opened': opened, 'html': html_files, 'command': command})
        report = {'suite_id': suite['suite_id'], 'suite_sha256': hashlib.sha256(args.suite.read_bytes()).hexdigest(),
                  'condition': args.condition, 'client': version, 'skill_hashes': hashes,
                  'limits': 'One session per case. Fixture opener only; browser rendering is a separate check. No poetry-quality or general reliability claim.',
                  'cases': records}
        (output / 'runs.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(f"{args.condition} {case['id']}: exit {exit_code}, display request {records[-1]['opened'] is not None}", flush=True)


if __name__ == '__main__':
    main()

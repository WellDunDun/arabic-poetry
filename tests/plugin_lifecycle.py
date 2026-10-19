"""Test real Claude/Codex Git installs and updates without model calls or user-state writes."""
import argparse
import hashlib
import importlib.util
import json
import os
import selectors
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/WellDunDun/arabic-poetry.git'
MARKET = 'arabic-poetry-plugins'
PLUGIN = f'arabic-poetry@{MARKET}'
PROBE = 'assets/plugin-lifecycle-probe.txt'
spec = importlib.util.spec_from_file_location('plugin_version', ROOT / 'scripts/plugin_version.py')
versions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(versions)


def hashes(skill):
    return {str(p.relative_to(skill)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in skill.rglob('*') if p.is_file() and str(p.relative_to(skill)) != PROBE}


def runtime_skill(env, cwd, receipts):
    """Use Codex's real skill loader; retain only this plugin's rows."""
    process = subprocess.Popen(['codex', 'app-server', '--stdio'], env=env, cwd=cwd,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, bufsize=1)

    def send(value):
        process.stdin.write(json.dumps(value) + '\n')
        process.stdin.flush()

    def receive(identity):
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + 30
        try:
            while time.monotonic() < deadline:
                if not selector.select(timeout=1):
                    continue
                line = process.stdout.readline()
                if not line:
                    raise RuntimeError('Codex app-server exited before replying')
                value = json.loads(line)
                if value.get('id') == identity:
                    if 'error' in value:
                        raise RuntimeError(value['error'])
                    return value['result']
            raise TimeoutError('Codex skill discovery timed out')
        finally:
            selector.close()

    try:
        send({'id': 0, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'poetry_plugin_lifecycle', 'version': '1.0.0'}}})
        receive(0)
        send({'method': 'initialized', 'params': {}})
        send({'id': 1, 'method': 'skills/list', 'params': {'cwds': [str(cwd)], 'forceReload': True}})
        data = receive(1)
        rows = [skill for group in data['data'] for skill in group['skills']
                if skill.get('pluginId') == PLUGIN]
        assert len(rows) == 1 and rows[0]['enabled'], rows
        receipts.append({'command': ['codex', 'app-server', 'skills/list'], 'plugin_rows': rows})
        return Path(rows[0]['path'])
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdin.close()
        process.stdout.close()


def test_lifecycle(report):
    for executable in ('git', 'python3', 'codex', 'claude'):
        if not shutil.which(executable):
            raise RuntimeError(f'Missing required executable: {executable}')
    report['commands'] = receipts = []
    with tempfile.TemporaryDirectory(prefix='poetry-plugin-lifecycle-') as temp:
        scratch = Path(temp).resolve()
        source = scratch / 'source'
        source.mkdir()
        for name in ('plugin.json', '.claude-plugin', '.agents/plugins', 'skills', 'README.md', 'LICENSE'):
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if (ROOT / name).is_dir():
                shutil.copytree(ROOT / name, target, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copy2(ROOT / name, target)
        original_hashes = hashes(source / 'skills/arabic-poetry')
        report['source_skill_sha256'] = hashlib.sha256(
            json.dumps(original_hashes, sort_keys=True).encode()).hexdigest()
        report['manifest_sha256'] = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                     for name in (*versions.FILES, '.agents/plugins/marketplace.json')}
        initial = versions.declarations(source)[2]
        parts = list(versions.version_tuple(initial))
        parts[-1] += 1
        updated = '.'.join(map(str, parts))
        probe = source / 'skills/arabic-poetry' / PROBE
        probe.write_text(initial, encoding='utf-8')
        base = os.environ.copy()
        # These variables keep their documented meanings and apply only to child clients.
        # The calling agent's environment and the user's existing state are unchanged.
        base.update({'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull,
                     'GIT_TERMINAL_PROMPT': '0', 'GIT_AUTHOR_NAME': 'Plugin lifecycle test',
                     'GIT_AUTHOR_EMAIL': 'test@example.invalid', 'GIT_COMMITTER_NAME': 'Plugin lifecycle test',
                     'GIT_COMMITTER_EMAIL': 'test@example.invalid', 'PYTHONDONTWRITEBYTECODE': '1',
                     'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1', 'DISABLE_TELEMETRY': '1'})
        for key in list(base):
            if key.startswith(('ANTHROPIC_API', 'CLAUDE_CODE_OAUTH', 'OPENAI_API')):
                base.pop(key)

        def run(command, env=base, cwd=scratch):
            result = subprocess.run(command, env=env, cwd=cwd, capture_output=True, text=True, timeout=90)
            receipts.append({'command': command, 'exit_code': result.returncode,
                             'stdout': result.stdout, 'stderr': result.stderr})
            if result.returncode:
                raise RuntimeError(f'{command}: {result.stderr or result.stdout}')
            return result.stdout

        for client in ('codex', 'claude'):
            report.setdefault('client_versions', {})[client] = run([client, '--version']).strip()
        run(['git', 'init', '-q', '-b', 'main'], cwd=source)
        run(['git', 'add', '.'], cwd=source)
        run(['git', 'commit', '-qm', f'Fixture {initial}'], cwd=source)
        remote = scratch / 'mirror.git'
        run(['git', 'clone', '-q', '--bare', str(source), str(remote)])
        # Real Git transports and update commands, with no GitHub writes or network clones.
        base.update({'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': f'url.{remote.as_uri()}.insteadOf',
                     'GIT_CONFIG_VALUE_0': URL})
        codex = dict(base, CODEX_HOME=str(scratch / 'codex-state'))
        claude = dict(base, CLAUDE_CONFIG_DIR=str(scratch / 'claude-state'))
        for path in (codex['CODEX_HOME'], claude['CLAUDE_CONFIG_DIR']):
            Path(path).mkdir()
        run(['codex', 'plugin', 'marketplace', 'add', URL, '--ref', 'main', '--json'], codex)
        run(['codex', 'plugin', 'add', PLUGIN, '--json'], codex)
        run(['claude', 'plugin', 'marketplace', 'add', URL, '--json'], claude)
        run(['claude', 'plugin', 'install', PLUGIN, '--json'], claude)

        def verify(version):
            codex_rows = json.loads(run(['codex', 'plugin', 'list', '--json'], codex))['installed']
            row = next(r for r in codex_rows if r['pluginId'] == PLUGIN)
            assert row['version'] == version and row['enabled'], row
            assert row['marketplaceSource']['sourceType'] == 'git', row
            discovered = runtime_skill(codex, scratch, receipts)
            codex_path = discovered.parents[2]
            claude_rows = json.loads(run(['claude', 'plugin', 'list', '--json'], claude))
            row = next(r for r in claude_rows if r['id'] == PLUGIN)
            assert row['version'] == version and row['enabled'], row
            claude_path = Path(row['installPath'])
            details = run(['claude', 'plugin', 'details', 'arabic-poetry'], claude)
            assert 'Skills (1)' in details and 'arabic-poetry' in details, details
            for host, installed in [('codex', codex_path), ('claude', claude_path)]:
                assert installed.is_relative_to(scratch), installed
                assert json.loads((installed / 'plugin.json').read_text())['version'] == version
                skill = installed / 'skills/arabic-poetry'
                assert (skill / PROBE).read_text() == version
                assert hashes(skill) == original_hashes, f'{host}: installed skill files differ'
                run(['python3', str(skill / 'scripts/scan.py'), '--help'], cwd=scratch)
                report.setdefault('verified', []).append({
                    'host': host, 'version': version, 'skill_files_matching_source': len(original_hashes),
                    'updated_payload': (skill / PROBE).read_text(), 'skill_available': True})

        verify(initial)
        versions.set_version(source, updated)
        probe.write_text(updated, encoding='utf-8')
        run(['git', 'add', '.'], cwd=source)
        run(['git', 'commit', '-qm', f'Fixture {updated}'], cwd=source)
        run(['git', 'push', '-q', str(remote), 'main'], cwd=source)
        run(['codex', 'plugin', 'marketplace', 'upgrade', MARKET, '--json'], codex)
        run(['codex', 'plugin', 'add', PLUGIN, '--json'], codex)
        run(['claude', 'plugin', 'marketplace', 'update', MARKET, '--json'], claude)
        update = json.loads(run(['claude', 'plugin', 'update', PLUGIN, '--json'], claude))
        assert update['oldVersion'] == initial and update['newVersion'] == updated, update
        verify(updated)
        # Repeating the update must keep a usable installed package.
        run(['codex', 'plugin', 'add', PLUGIN, '--json'], codex)
        run(['claude', 'plugin', 'update', PLUGIN, '--json'], claude)
        verify(updated)
        report['fixture_versions'] = [initial, updated]
        report['limits'] = ('Git mirror and isolated client settings/cache; no model calls, '
                            'browser admin sync, public publication or automatic timer test.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Write actual command receipts as JSON')
    args = parser.parse_args()
    report = {'passed': False,
              'harness_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'release_helper_sha256': hashlib.sha256((ROOT / 'scripts/plugin_version.py').read_bytes()).hexdigest()}
    try:
        if not __debug__:
            raise RuntimeError('Lifecycle checks require assertions; disable Python optimization')
        test_lifecycle(report)
        report['passed'] = True
        print('PASS Claude and Codex Git install, update, repeat update, skill discovery and payload checks')
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

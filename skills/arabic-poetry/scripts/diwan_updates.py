"""Follow installed package updates, keeping a supervised Diwan address stable."""
import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit
from diwan_store import DiwanError, Store, VERSION

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = 1
RESTART = 75
TOKEN_ENV = 'DIWAN_RUNTIME_TOKEN'
BLOCKED_ENV = 'DIWAN_RUNTIME_BLOCKED'
SCRIPTS = Path('skills/arabic-poetry/scripts')


def package(root):
    value = json.loads((root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    version = value.get('version', '')
    if value.get('name') != 'arabic-poetry' or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Expected a versioned Arabic Poetry package')
    return version


def compatible(root):
    return json.loads((root / 'skills/arabic-poetry/assets/workbench/runtime.json').read_text()) == {'protocol': PROTOCOL}


class InstalledRuntime:
    """Read the current installation, never fetch or install another package."""
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        try:
            self.version = package(self.root)
            self.packaged = True
        except (OSError, ValueError):
            self.version = VERSION
            self.packaged = False
        self.checked = 0
        self.available = None
        self.blocked = os.environ.get(BLOCKED_ENV, '')

    def candidate(self, force=False):
        if not self.packaged:
            return None
        if not force and time.monotonic() - self.checked < 15:
            return self.available
        self.checked = time.monotonic()
        self.available = None
        try:
            target = self.root
            installed_version = None
            if self.root.parent.name == 'arabic-poetry' and self.root.parents[2].name == 'cache' and self.root.parents[3].name == 'plugins':
                config = self.root.parents[4]
                market = self.root.parents[1].name
                identity = 'arabic-poetry@' + market
                if (config / 'plugins/installed_plugins.json').is_file():
                    records = json.loads((config / 'plugins/installed_plugins.json').read_text())['plugins'].get(identity, [])
                    settings = json.loads((config / 'settings.json').read_text())
                    if settings.get('enabledPlugins', {}).get(identity) is False:
                        return None
                    # Follow only the same install scope, never another project or marketplace.
                    rows = [r for r in records if r.get('scope') == 'user' and r.get('installPath')]
                    if len(rows) != 1:
                        return None
                    target = Path(rows[0]['installPath']).resolve()
                    installed_version = rows[0].get('version')
                elif (config / 'config.toml').is_file() and shutil.which('codex'):
                    env = dict(os.environ, CODEX_HOME=str(config))
                    result = subprocess.run(['codex', 'plugin', 'list', '--json'], env=env,
                                            capture_output=True, text=True, timeout=5)
                    if result.returncode or len(result.stdout) > 2_000_000:
                        return None
                    rows = [r for r in json.loads(result.stdout).get('installed', [])
                            if r.get('pluginId') == identity and r.get('enabled') and r.get('installed')]
                    if len(rows) != 1:
                        return None
                    target = self.root.parent / rows[0]['version']
                    installed_version = rows[0]['version']
                else:
                    return None
                if target.parent != self.root.parent:
                    return None
            if target == self.root:
                return None
            version = package(target)
            if installed_version != version:
                return None
            if tuple(map(int, version.split('.'))) <= tuple(map(int, self.version.split('.'))):
                return None
            if str(target) == self.blocked or not compatible(target):
                return None
            for name in ('diwan.py', 'diwan_updates.py', 'serve_diwan.py'):
                if not (target / SCRIPTS / name).is_file():
                    return None
            if not (target / 'skills/arabic-poetry/assets/workbench/diwan.html').is_file():
                return None
            self.available = {'version': version, 'root': str(target)}
        except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
            pass
        return self.available

    def status(self):
        value = self.candidate()
        return {'protocol': PROTOCOL, 'version': self.version,
                'available': value['version'] if value else None,
                'recovered': bool(self.blocked)}


def acknowledgement(process, timeout=6):
    """A partial line is not readiness, and must not defeat the startup deadline."""
    deadline = time.monotonic() + timeout
    raw = b''
    while len(raw) < 16384:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([process.stdout], [], [], remaining)[0]:
            break
        chunk = os.read(process.stdout.fileno(), 16384 - len(raw))
        if not chunk:
            break
        raw += chunk
        if b'\n' in raw:
            return raw.split(b'\n', 1)[0]
    return b''


def supervise(file, port, agent):
    """Restart only an owned worker, rolling back if its successor cannot start."""
    script = Path(__file__).with_name('diwan.py').resolve()
    current = ROOT
    good = ROOT
    good_script = script
    identity = Store(file).get()['poem']['id']
    previous = {}
    child = None
    first = True
    token = None
    blocked = ''
    stopping = False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True
        if child and child.poll() is None:
            child.terminate()

    def terminate():
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=6)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=3)

    for number in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        previous[number] = signal.signal(number, stop)
    try:
        while not stopping:
            command = [sys.executable, str(script), 'serve', str(file), '--port', str(port), '--json', '--runtime-worker']
            if agent is not None:
                command += ['--agent', agent]
            env = dict(os.environ, **{BLOCKED_ENV: blocked})
            if token:
                env[TOKEN_ENV] = token
            else:
                env.pop(TOKEN_ENV, None)
            child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env)
            line = acknowledgement(child)
            try:
                receipt = json.loads(line)
                address = urlsplit(receipt['url'])
                if receipt['path'] != str(file) or receipt['id'] != identity or address.hostname != '127.0.0.1' or not address.port:
                    raise ValueError('Invalid worker acknowledgement')
                if token and (address.path != '/' + token + '/diwan.html' or address.port != port):
                    raise ValueError('Worker changed the Diwan address')
            except (ValueError, KeyError, TypeError):
                terminate()
                if first or current == good:
                    raise DiwanError('START_FAILED', 'Diwan worker could not start; the poem was not changed', 6)
                blocked = str(current)
                current = good
                script = good_script
                continue
            finally:
                child.stdout.close()
            if first:
                print(json.dumps(receipt, ensure_ascii=False), flush=True)
                first = False
            if receipt.get('reused'):
                child.wait(timeout=5)
                return
            port = address.port
            token = address.path.split('/')[1]
            agent = 'manual' if receipt.get('manual') else receipt['agent']
            good = current
            good_script = script
            code = child.wait()
            if stopping or code != RESTART:
                return
            monitor = InstalledRuntime(current)
            candidate = monitor.candidate(force=True)
            current = Path(candidate['root']) if candidate else current
            script = current / SCRIPTS / 'diwan.py'
    finally:
        if child:
            terminate()
        for number, handler in previous.items():
            signal.signal(number, handler)

"""Follow installed package updates, keeping a supervised Diwan address stable."""
import json
import fcntl
import os
from pathlib import Path
import re
import select
import shutil
import signal
import subprocess
import sys
import time
import uuid
from urllib.parse import urlsplit
from diwan_agent import session_mode
from diwan_store import DiwanError, Store, VERSION, atomic_write, bounded_read, encode, parse

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = 2
RESTART = 75
STOP_WAIT = 10  # Covers the supervisor's 6-second TERM and 3-second KILL bounds.
TOKEN_ENV = 'DIWAN_RUNTIME_TOKEN'
BLOCKED_ENV = 'DIWAN_RUNTIME_BLOCKED'
RECOVERED_ENV = 'DIWAN_RUNTIME_RECOVERED'
CONTROL_ENV = 'DIWAN_RUNTIME_ID'
SCRIPTS = Path('skills/arabic-poetry/scripts')


class RuntimeControl:
    """A session-specific stop request and supervisor-owned shutdown receipt."""
    def __init__(self, store, identity):
        if not isinstance(identity,str) or not re.fullmatch(r'[0-9a-f]{32}',identity):
            raise DiwanError('STOP_UNKNOWN','Invalid supervisor identity; preserve the session receipt.',6)
        self.identity = identity
        self.poem = store.get()['poem']['id']
        self.path = store.state/f'runtime-{identity}.json'
        self.request = store.state/f'runtime-{identity}.stop.json'

    def publish(self, state):
        atomic_write(self.path,encode({'runtime_id':self.identity,'id':self.poem,'state':state}))

    def lease(self):
        return os.fdopen(os.open(self.path.with_suffix('.lock'),os.O_RDWR|os.O_CREAT,0o600),'r+b')

    def alive(self):
        with self.lease() as lease:
            try:
                fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                return True
        return False

    def state(self):
        try:
            value = parse(bounded_read(self.path))
            if value.get('runtime_id') == self.identity and value.get('id') == self.poem and value.get('state') in ('starting','running','stopped'):
                return value['state']
        except (OSError,ValueError,DiwanError,AttributeError):
            pass
        raise DiwanError('STOP_UNKNOWN','Could not verify the supervisor. Keep its session receipt and retry stop.',6)

    def request_stop(self):
        self.state()
        atomic_write(self.request,encode({'runtime_id':self.identity,'id':self.poem}))

    def stopping(self):
        try:
            return parse(bounded_read(self.request)) == {'runtime_id':self.identity,'id':self.poem}
        except (OSError,ValueError,DiwanError):
            return False


def stop_supervised(store, timeout):
    receipt_path = store.state/'session.json'
    if not receipt_path.exists():
        return None
    receipt = parse(bounded_read(receipt_path))
    identity = receipt.get('runtime_id') if isinstance(receipt,dict) else None
    if identity is None:
        return None
    control = RuntimeControl(store,identity)
    if not control.alive():
        return None  # No supervisor owns the lease; verify/stop any orphan through HTTP.
    if control.state() == 'stopped':
        return False
    control.request_stop()
    deadline = time.monotonic()+timeout
    while time.monotonic()<deadline:
        if control.state() == 'stopped':
            return True
        time.sleep(.05)
    if not control.alive():
        return None
    raise DiwanError('STOP_UNKNOWN','Shutdown is not yet confirmed. Keep the session receipt and retry stop.',6)


def prune_stopped_controls(store):
    """Keep the current receipt and uncertain generations; remove acknowledged old ones."""
    receipt = store.state/'session.json'
    try:
        value = parse(bounded_read(receipt)) if receipt.exists() else {}
        if not isinstance(value,dict):
            return
        current = value.get('runtime_id')
    except (OSError,DiwanError):
        return
    for path in store.state.glob('runtime-*.json'):
        identity = path.name[len('runtime-'):-len('.json')]
        if identity == current or not re.fullmatch(r'[0-9a-f]{32}',identity):
            continue
        control = RuntimeControl(store,identity)
        try:
            if not control.alive() and control.state() == 'stopped':
                control.request.unlink(missing_ok=True)
                control.path.unlink()
                control.path.with_suffix('.lock').unlink(missing_ok=True)
        except (OSError,DiwanError):
            pass


def package(root):
    value = json.loads((root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    version = value.get('version', '')
    if value.get('name') != 'arabic-poetry' or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Expected a versioned Arabic Poetry package')
    return version


def compatible(root):
    return json.loads((root / 'skills/arabic-poetry/assets/workbench/runtime.json').read_text()) == {'protocol': PROTOCOL}


def recovery_marker(blocked, current):
    if not blocked:
        return False
    try:
        running = tuple(map(int, package(current).split('.')))
        return any(tuple(map(int, package(Path(root)).split('.'))) > running for root in blocked)
    except (OSError, ValueError):
        return True


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
        raw = os.environ.get(BLOCKED_ENV, '[]')
        try:
            values = json.loads(raw)
        except ValueError:
            values = [raw] if raw else []
        self.blocked = set(values) if isinstance(values, list) and all(isinstance(p, str) for p in values) else set()
        self.recovered = os.environ.get(RECOVERED_ENV) == '1'

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
            if str(target) in self.blocked or not compatible(target):
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
                'recovered': self.recovered}


def acknowledgement(process, timeout=6, cancelled=lambda:False):
    """A partial line is not readiness, and must not defeat the startup deadline."""
    deadline = time.monotonic() + timeout
    raw = b''
    while len(raw) < 16384:
        if cancelled():
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        if not select.select([process.stdout], [], [], min(remaining,.1))[0]:
            continue
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
    store = Store(file)
    identity = store.get()['poem']['id']
    control = RuntimeControl(store,uuid.uuid4().hex)
    with store.locked():
        prune_stopped_controls(store)
        lease = control.lease()
        try:
            fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            control.publish('starting')
        except BaseException:
            lease.close()
            raise
    previous = {}
    child = None
    first = True
    token = None
    blocked = set()
    stopping = False

    def cancelled():
        return stopping or control.stopping()

    def stop(signum, frame):
        nonlocal stopping
        stopping = True
        if child and child.poll() is None:
            try:
                child.terminate()
            except ProcessLookupError:
                pass

    def terminate():
        if child.poll() is None:
            try:
                child.terminate()
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=6)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=3)

    for number in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        previous[number] = signal.signal(number, stop)
    try:
        while not cancelled():
            command = [sys.executable, str(script), 'serve', str(file), '--port', str(port), '--json', '--runtime-worker']
            if agent is not None:
                command += ['--agent', agent]
            env = dict(os.environ, **{BLOCKED_ENV: json.dumps(sorted(blocked)),
                                      RECOVERED_ENV: '1' if recovery_marker(blocked, current) else '0',
                                      CONTROL_ENV:control.identity})
            if token:
                env[TOKEN_ENV] = token
            else:
                env.pop(TOKEN_ENV, None)
            child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env)
            if cancelled():
                terminate()
                child.stdout.close()
                return
            line = acknowledgement(child,timeout=STOP_WAIT+6 if first else 6,cancelled=cancelled)
            try:
                receipt = json.loads(line)
                address = urlsplit(receipt['url'])
                if receipt['path'] != str(file) or receipt['id'] != identity or address.hostname != '127.0.0.1' or not address.port:
                    raise ValueError('Invalid worker acknowledgement')
                if not receipt.get('reused') and receipt.get('runtime_id') != control.identity:
                    raise ValueError('Worker changed its supervisor identity')
                if token and (address.path != '/' + token + '/diwan.html' or address.port != port):
                    raise ValueError('Worker changed the Diwan address')
            except (ValueError, KeyError, TypeError):
                terminate()
                if cancelled():
                    return
                if first or current == good:
                    raise DiwanError('START_FAILED', 'Diwan worker could not start; the poem was not changed', 6)
                blocked.add(str(current))
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
            control.publish('running')
            port = address.port
            token = address.path.split('/')[1]
            agent = session_mode(receipt)
            while child.poll() is None and not cancelled():
                time.sleep(.05)
            if cancelled():
                return
            code = child.wait()
            if code == 0:
                return
            if code != RESTART:
                if current == good:
                    raise DiwanError('RUNTIME_FAILED', 'Diwan stopped unexpectedly; reopen the poem. Its saved text is unchanged.', 6)
                blocked.add(str(current))
                current, script = good, good_script
                continue
            # A real update request proves this worker served the document and runtime API.
            good, good_script = current, script
            monitor = InstalledRuntime(current)
            monitor.blocked = set(blocked)
            candidate = monitor.candidate(force=True)
            current = Path(candidate['root']) if candidate else current
            script = current / SCRIPTS / 'diwan.py'
    finally:
        try:
            if child:
                terminate()
            control.publish('stopped')
            control.request.unlink(missing_ok=True)
        finally:
            lease.close()
            for number, handler in previous.items():
                signal.signal(number, handler)

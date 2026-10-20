"""One authoritative poem document, conditional writes and recoverable history."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

try:
    import fcntl
except ImportError:
    fcntl = None

VERSION = '0.3.1'
MAX_BYTES = 2_000_000
FIELDS = {'title', 'text', 'choices', 'suggestions', 'status', 'mode', 'meter'}
MODES = ('auto', 'classical', 'free', 'pairs')


class DiwanError(Exception):
    def __init__(self, code, message, exit_code=2, **details):
        super().__init__(message)
        self.code, self.exit_code, self.details = code, exit_code, details


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
    except FileNotFoundError:
        raise DiwanError('NOT_FOUND', f'File not found: {path}', 4)
    if len(raw) > MAX_BYTES:
        raise DiwanError('TOO_LARGE', f'File exceeds {MAX_BYTES} bytes: {path}')
    return raw


def parse(raw):
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError):
        raise DiwanError('INVALID_JSON', 'Expected UTF-8 JSON; use create --text-file to import poem text.')


def validate_patch(patch):
    if not isinstance(patch, dict) or not patch or set(patch) - FIELDS:
        raise DiwanError('INVALID_PATCH', 'Supply a nonempty object using: ' + ', '.join(sorted(FIELDS)))
    for key in ('title', 'text', 'status', 'mode', 'meter'):
        if key in patch and not isinstance(patch[key], str):
            raise DiwanError('INVALID_PATCH', f'{key} must be a string')
    if 'title' in patch and not 0 < len(patch['title'].strip()) <= 300:
        raise DiwanError('INVALID_PATCH', 'title must contain 1–300 characters')
    if 'text' in patch and not patch['text'].strip():
        raise DiwanError('INVALID_PATCH', 'text must contain a poem; empty input is not a deletion command')
    if 'status' in patch and patch['status'] not in ('review', 'confirmed'):
        raise DiwanError('INVALID_PATCH', 'status must be review or confirmed')
    if 'mode' in patch and patch['mode'] not in MODES:
        raise DiwanError('INVALID_PATCH', 'mode must be ' + ', '.join(MODES))
    if 'meter' in patch and not re.fullmatch(r'[a-z]*', patch['meter']):
        raise DiwanError('INVALID_PATCH', 'meter must be an empty string or a lowercase scanner key')
    if 'choices' in patch and (not isinstance(patch['choices'], list) or not all(isinstance(x, dict) for x in patch['choices'])):
        raise DiwanError('INVALID_PATCH', 'choices must be an array of objects')
    if 'suggestions' in patch and not isinstance(patch['suggestions'], dict):
        raise DiwanError('INVALID_PATCH', 'suggestions must be an object')
    if len(encode(patch)) > MAX_BYTES - 1000:
        raise DiwanError('TOO_LARGE', 'Poem document exceeds the 2 MB limit')


def validate_document(doc):
    if not isinstance(doc, dict) or set(doc) != FIELDS | {'schema_version', 'id', 'revision', 'last_save_id'}:
        raise DiwanError('INVALID_DOCUMENT', 'Expected a Diwan poem document; import .txt/.md with create --text-file.')
    if type(doc['schema_version']) is not int or doc['schema_version'] != 1 or type(doc['revision']) is not int or doc['revision'] < 1:
        raise DiwanError('INVALID_DOCUMENT', 'Unsupported document schema or revision')
    if not isinstance(doc['id'], str) or not re.fullmatch(r'[0-9a-f]{32}', doc['id']):
        raise DiwanError('INVALID_DOCUMENT', 'Invalid poem id')
    if not isinstance(doc['last_save_id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', doc['last_save_id']):
        raise DiwanError('INVALID_DOCUMENT', 'Invalid save identity')
    validate_patch({key: doc[key] for key in FIELDS})
    return doc


def atomic_write(path, raw, exclusive=False):
    """Publish complete private bytes; never truncate the destination."""
    path = Path(path)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.diwan-', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            os.link(temp, path)
        else:
            os.replace(temp, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


class Store:
    def __init__(self, path):
        path = Path(path).absolute()
        if path.is_symlink():
            raise DiwanError('INVALID_PATH', 'Use the real poem path, not a symbolic link')
        self.path = path.resolve()
        skill = Path(__file__).resolve().parent.parent
        if self.path == skill or skill in self.path.parents:
            raise DiwanError('INVALID_PATH', 'Keep poem files outside the installed skill')
    @property
    def state(self):
        identity = self.get()['poem']['id'] if self.path.exists() else 'pending'
        return self.path.parent / '.diwan' / 'shared' / identity

    def get(self):
        if self.path.exists() and self.path.stat().st_nlink != 1:
            staging = self.staging_links()
            if len(staging) == self.path.stat().st_nlink - 1:
                raise DiwanError('INITIALIZATION_INTERRUPTED', 'Creation was interrupted. Retry create with the same input to recover its staging files.', 6, staging_files=[str(p) for p in staging])
            raise DiwanError('INVALID_PATH', 'Hard-linked documents are unsupported; import a separate poem instead')
        raw = bounded_read(self.path)
        doc = validate_document(parse(raw))
        return {'schema_version': 1, 'path': str(self.path), 'version': digest(raw), 'poem': doc}

    def staging_links(self):
        return [p for p in self.path.parent.glob('.diwan-*')
                if not p.is_symlink() and p.is_file() and os.path.samefile(p, self.path)]

    @contextlib.contextmanager
    def locked(self):
        if fcntl is None:
            raise DiwanError('UNSUPPORTED_PLATFORM', 'Safe writes currently require macOS or Linux file locking', 6)
        if not self.path.parent.is_dir():
            raise DiwanError('NOT_FOUND', 'Create the poem directory first: ' + str(self.path.parent), 4)
        private = self.path.parent / '.diwan'
        private.mkdir(parents=True, exist_ok=True, mode=0o700)
        ignore = self.path.parent / '.diwan/.gitignore'
        try:
            with ignore.open('x') as stream:
                stream.write('*\n')
        except FileExistsError:
            pass
        lock = private / 'write.lock'
        fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            if self.path.exists():
                if self.path.stat().st_nlink > 1:
                    staging = self.staging_links()
                    if len(staging) == self.path.stat().st_nlink - 1:
                        for path in staging:
                            path.unlink()
                self.bind()
            yield
        finally:
            os.close(fd)

    def bind(self):
        """Aliases share document history; unrelated copies must get a new id."""
        self.check_binding()
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        binding = self.state / 'binding.json'
        atomic_write(binding, encode({'path': str(self.path)}))

    def snapshot(self, envelope):
        self.bind()
        folder = self.state / 'history'
        folder.mkdir(exist_ok=True, mode=0o700)
        raw = bounded_read(self.path)
        if digest(raw) != envelope['version']:
            raise DiwanError('CONFLICT', 'Poem changed outside the CLI; reread it before saving', 5)
        path = folder / f"{envelope['poem']['revision']:012d}-{envelope['version']}.json"
        if path.exists():
            if bounded_read(path) != raw:
                raise DiwanError('CORRUPT_HISTORY', 'Historical snapshot bytes do not match their version', 6)
        else:
            atomic_write(path, raw, exclusive=True)

    def create(self, patch, dry_run=False):
        patch = dict(title=self.path.stem, text='', choices=[], suggestions={}, status='review', mode='auto', meter='') | patch
        validate_patch(patch)
        if not self.path.parent.is_dir():
            raise DiwanError('NOT_FOUND', 'Create the poem directory first: ' + str(self.path.parent), 4)
        if self.path.exists():
            try:
                current = self.get()
            except DiwanError as error:
                if error.code != 'INITIALIZATION_INTERRUPTED' or dry_run:
                    raise
                with self.locked():
                    current = self.get()
                    self.snapshot(current)
            if all(current['poem'][key] == patch[key] for key in FIELDS):
                self.check_binding()
                return dict(current, replayed=True, dry_run=dry_run)
            raise DiwanError('ALREADY_EXISTS', 'This poem path already exists with different content; use get then update --if-version', 5)
        if dry_run:
            return {'path': str(self.path), 'dry_run': True, 'would_create': patch}
        with self.locked():
            if self.path.exists():
                return self.create(patch)
            doc = dict(patch, schema_version=1, id=uuid.uuid4().hex, revision=1, last_save_id='create-' + uuid.uuid4().hex)
            atomic_write(self.path, encode(doc), exclusive=True)
            result = self.get()
            self.snapshot(result)
            return dict(result, replayed=False)

    def _finish(self, path, operation, current):
        self.snapshot(current)
        operation['state'] = 'committed'
        operation.pop('document', None)
        atomic_write(path, encode(operation))

    def _reconcile(self, current):
        folder = self.state / 'operations'
        folder.mkdir(exist_ok=True, mode=0o700)
        for path in folder.glob('*.json'):
            operation = parse(bounded_read(path))
            if operation.get('state') == 'prepared' and operation['new_version'] == current['version']:
                self._finish(path, operation, current)
        return folder

    def update(self, patch, expected, request_id, dry_run=False):
        validate_patch(patch)
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise DiwanError('PRECONDITION_REQUIRED', 'Read get --json, then supply its version with --if-version')
        if not isinstance(request_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', request_id):
            raise DiwanError('INVALID_REQUEST_ID', '--request-id must be 1–80 letters, digits, hyphens or underscores')
        fingerprint = digest(json.dumps({'patch': patch, 'if_version': expected}, ensure_ascii=False, sort_keys=True).encode())
        self.get()
        if dry_run:
            self.check_binding()
            current = self.get()
            self.check_version(current, expected)
            return dict(current, dry_run=True, would_update=patch)
        with self.locked():
            current = self.get()
            folder = self._reconcile(current)
            receipt = folder / (request_id + '.json')
            operation = parse(bounded_read(receipt)) if receipt.exists() else None
            if operation and operation['request_hash'] != fingerprint:
                raise DiwanError('IDEMPOTENCY_CONFLICT', 'Request id was already used with different input; reassess and use a new id', 5)
            if operation and operation['state'] == 'committed':
                return dict(current, replayed=True, applied_version=operation['new_version'], request_id=request_id)
            self.check_version(current, expected)
            if all(current['poem'][key] == value for key, value in patch.items()):
                operation = {'state': 'committed', 'request_hash': fingerprint, 'new_version': current['version']}
                atomic_write(receipt, encode(operation))
                return dict(current, replayed=False, unchanged=True, request_id=request_id)
            doc = current['poem'] | patch | {'revision': current['poem']['revision'] + 1, 'last_save_id': request_id}
            validate_document(doc)
            raw = encode(doc)
            operation = {'state': 'prepared', 'request_hash': fingerprint, 'base_version': expected,
                         'new_version': digest(raw), 'document': doc}
            self.snapshot(current)
            atomic_write(receipt, encode(operation))
            self.check_version(self.get(), expected)
            atomic_write(self.path, raw)
            result = self.get()
            self._finish(receipt, operation, result)
            return dict(result, replayed=False, applied_version=result['version'], request_id=request_id)

    @staticmethod
    def check_version(current, expected):
        if current['version'] != expected:
            raise DiwanError('CONFLICT', 'Another writer saved this poem. Get the latest version and reassess; do not blindly retry.', 5,
                             expected_version=expected, current_version=current['version'], path=current['path'])

    def check_binding(self):
        current = self.get()
        binding = self.state / 'binding.json'
        if binding.exists():
            old = Path(parse(bounded_read(binding))['path'])
            if old.exists() and not os.path.samefile(old, self.path):
                try:
                    previous = validate_document(parse(bounded_read(old)))
                except DiwanError:
                    return
                if previous['id'] == current['poem']['id']:
                    raise DiwanError('DUPLICATE_ID', 'This copied JSON shares another document id; import a new poem instead.', 5)

    def history(self, limit=20, before=None):
        if not 1 <= limit <= 100:
            raise DiwanError('INVALID_LIMIT', '--limit must be between 1 and 100')
        current = self.get()
        self.check_binding()
        rows = {current['version']: {'version': current['version'], 'revision': current['poem']['revision'], 'current': True}}
        for path in (self.state / 'history').glob('*.json'):
            match = re.fullmatch(r'(\d+)-([0-9a-f]{64})\.json', path.name)
            if match:
                revision, version = int(match[1]), match[2]
                rows[version] = {'version': version, 'revision': revision, 'current': version == current['version']}
        items = sorted((x for x in rows.values() if before is None or x['revision'] < before), key=lambda x: x['revision'], reverse=True)
        return {'path': str(self.path), 'revisions': items[:limit], 'truncated': len(items) > limit,
                'next_cursor': items[limit - 1]['revision'] if len(items) > limit else None}

    def restore(self, version, expected, request_id, dry_run=False):
        self.check_binding()
        if not isinstance(version, str) or not re.fullmatch(r'[0-9a-f]{64}', version):
            raise DiwanError('INVALID_VERSION', '--revision must be a full version from history --json')
        paths = list((self.state / 'history').glob('*-' + version + '.json'))
        if not paths:
            raise DiwanError('NOT_FOUND', 'Historical version not found; use history --json', 4)
        raw = bounded_read(paths[0])
        if digest(raw) != version:
            raise DiwanError('CORRUPT_HISTORY', 'Historical snapshot does not match its version', 6)
        old = validate_document(parse(raw))
        return self.update({key: old[key] for key in FIELDS}, expected, request_id, dry_run)

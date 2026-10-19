#!/usr/bin/env python3
"""Agent-native commands for a shared local Diwan poem document."""
import argparse
import http.client
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import webbrowser

sys.dont_write_bytecode = True
from diwan_store import DiwanError, Store, VERSION, MAX_BYTES, atomic_write, bounded_read, digest, encode, parse, validate_patch
import serve_diwan

SCRIPT = Path(__file__).resolve()
EXAMPLES = {
    'create': 'create poem.diwan.json --title نافذة --text-file poem.txt --json',
    'get': 'get poem.diwan.json --json',
    'update': 'update poem.diwan.json --text-file revised.txt --if-version "$VERSION" --request-id edit-1 --json',
    'history': 'history poem.diwan.json --limit 20 --json',
    'restore': 'restore poem.diwan.json --revision "$OLD_VERSION" --if-version "$VERSION" --request-id restore-1 --json',
    'open': 'open poem.diwan.json --no-browser --json',
    'serve': 'serve poem.diwan.json --port 0 --json',
    'stop': 'stop poem.diwan.json --json',
    'scan': 'scan poem.diwan.json --json',
    'export': 'export poem.diwan.json --format txt --output poem-export.txt --json',
    'pending': 'pending poem.diwan.json --limit 20 --json',
    'respond': 'respond poem.diwan.json --id "$REQUEST_ID" --input answer.json --json',
    'agent-context': 'agent-context --command update --json',
}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise DiwanError('INVALID_ARGUMENT', message + '; use diwan.py --help or agent-context --json')


def parser():
    root = Parser(description=__doc__, epilog='Examples:\n  python3 diwan.py agent-context --json\n  python3 diwan.py open poem.diwan.json --json', formatter_class=argparse.RawDescriptionHelpFormatter)
    root.add_argument('--version', action='version', version=VERSION)
    root.add_argument('--json', action='store_true', default=argparse.SUPPRESS, help='Structured results and structured stderr errors')
    commands = root.add_subparsers(dest='command', required=True)
    for name, example in EXAMPLES.items():
        p = commands.add_parser(name, help=name.replace('-', ' '), epilog='Examples:\n  python3 diwan.py ' + example + '\nVersion variables come from get/history --json; request ids come from pending --json.', formatter_class=argparse.RawDescriptionHelpFormatter)
        p.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
        if name == 'agent-context':
            p.add_argument('--command', dest='selected', choices=list(EXAMPLES))
            continue
        p.add_argument('file', type=Path, help='Authoritative .diwan.json poem document')
        if name in ('create', 'update'):
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument('--text-file', help='UTF-8 text/Markdown body; - reads stdin literally')
            group.add_argument('--input', help='JSON field object; - reads stdin')
        if name == 'create':
            p.add_argument('--title', help='Poem title; otherwise use JSON title or file stem')
        if name in ('create', 'update', 'restore', 'open', 'export'):
            p.add_argument('--dry-run', action='store_true', help='Validate and preview without writes or browser launch')
        if name in ('update', 'restore'):
            p.add_argument('--if-version', required=True, help='Exact current opaque version from get --json')
            p.add_argument('--request-id', required=True, help='Stable id for this logical save; reuse unchanged on retry')
        if name == 'restore':
            p.add_argument('--revision', required=True, help='Full historical version; restoration creates a new revision')
        if name in ('history', 'pending'):
            p.add_argument('--limit', type=int, default=20)
        if name == 'history':
            p.add_argument('--before', type=int, help='next_cursor from a previous history page')
        if name in ('open', 'serve'):
            p.add_argument('--port', type=int, default=0)
        if name == 'open':
            p.add_argument('--no-browser', action='store_true', help='Return the local URL for the agent to open')
        if name == 'export':
            p.add_argument('--format', choices=('txt', 'md', 'docx'), required=True)
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--overwrite', action='store_true')
        if name == 'respond':
            p.add_argument('--id', required=True)
            p.add_argument('--input', required=True, help='JSON answer file or - for stdin')
    return root, commands


def input_bytes(path):
    if path != '-':
        return bounded_read(path)
    if sys.stdin.isatty():
        raise DiwanError('INPUT_REQUIRED', 'Pipe input or use a file; interactive prompts are not supported')
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise DiwanError('INVALID_INPUT', 'stdin must contain 1–2000000 UTF-8 bytes')
    return raw


def request(url, route, body=None):
    parsed = urlsplit(url)
    if parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or not parsed.port or not parsed.path.endswith('/diwan.html'):
        raise DiwanError('INVALID_SESSION', 'Invalid local Diwan session receipt', 6)
    conn = http.client.HTTPConnection('127.0.0.1', parsed.port, timeout=3)
    try:
        path = parsed.path.removesuffix('/diwan.html') + route
        conn.request('GET' if body is None else 'POST', path, body=None if body is None else encode(body), headers={} if body is None else {'Content-Type': 'application/json'})
        response = conn.getresponse()
        data = parse(response.read(MAX_BYTES + 1))
        if response.status != 200:
            raise DiwanError('SESSION_UNAVAILABLE', 'Local server refused the request; run open again', 6)
        return data
    finally:
        conn.close()


def session(store):
    path = store.state / 'session.json'
    if not path.exists():
        return None
    receipt = parse(bounded_read(path))
    try:
        health = request(receipt['url'], '/status')
        if os.path.samefile(health['path'], store.path) and health['id'] == store.get()['poem']['id']:
            return receipt
    except (OSError, DiwanError, KeyError, http.client.HTTPException):
        pass
    return None


def serve(store, port):
    with store.locked():
        existing = session(store)
        if existing:
            print(json.dumps(dict(existing, reused=True)), flush=True)
            return
        current = store.get()
        server, url = serve_diwan.make_server(store.state / 'agent', port=port, document=store)
        receipt = {'path': str(store.path), 'id': current['poem']['id'], 'url': url, 'pid': os.getpid(), 'reused': False, 'rendered': False}
        atomic_write(store.state / 'session.json', encode(receipt))
        print(json.dumps(receipt, ensure_ascii=False), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def open_poem(store, args):
    store.get()
    if args.dry_run:
        return {'path': str(store.path), 'dry_run': True, 'would_open': True}
    receipt = session(store)
    if receipt:
        receipt = dict(receipt, reused=True)
    else:
        with store.locked():
            log = (store.state / 'server.log').open('ab')
        child = subprocess.Popen([sys.executable, str(SCRIPT), 'serve', str(store.path), '--port', str(args.port), '--json'],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=log, start_new_session=True)
        log.close()
        ready, _, _ = select.select([child.stdout], [], [], 8)
        if not ready:
            raise DiwanError('START_UNKNOWN', 'Server startup did not acknowledge. Run open again to discover an existing session; do not kill an unrelated PID.', 6)
        line = child.stdout.readline(MAX_BYTES)
        child.stdout.close()
        if not line:
            raise DiwanError('START_FAILED', 'Server failed; inspect ' + str(store.state / 'server.log'), 6)
        receipt = parse(line)
    receipt['browser_open_requested'] = False
    if not args.no_browser:
        receipt['browser_open_requested'] = bool(webbrowser.open(receipt['url']))
        if not receipt['browser_open_requested']:
            print(json.dumps(dict(receipt, status='partial_failure'), ensure_ascii=False))
            raise DiwanError('DISPLAY_UNAVAILABLE', 'The local server is running. Open its returned URL through your agent browser; do not recreate the poem.', 6, url=receipt['url'])
    return receipt


def export(store, args):
    current = store.get()
    destination = Store(args.output).path
    same_poem = destination.exists() and os.path.samefile(destination, store.path)
    private = store.path.parent / '.diwan'
    in_history = any(parent.exists() and private.exists() and os.path.samefile(parent, private) for parent in destination.parents)
    if same_poem or in_history:
        raise DiwanError('INVALID_OUTPUT', 'Export to a separate file outside the document and its private .diwan directory')
    if not destination.parent.is_dir():
        raise DiwanError('NOT_FOUND', 'Create the output directory first', 4)
    if args.dry_run:
        return {'path': str(destination), 'format': args.format, 'source_version': current['version'], 'dry_run': True}
    with tempfile.TemporaryDirectory() as folder:
        if args.format in ('txt', 'md'):
            raw = current['poem']['text'].encode('utf-8')
        else:
            source = Path(folder) / 'poems.json'
            output = Path(folder) / 'poem.docx'
            source.write_bytes(encode([current['poem']]))
            command = subprocess.run([sys.executable, str(SCRIPT.with_name('export_book.py')), str(source), str(output)], capture_output=True, text=True)
            if command.returncode:
                raise DiwanError('EXPORT_FAILED', command.stderr[-2000:] or 'Word export failed; check Node.js is available', 6)
            raw = output.read_bytes()
    if destination.exists() and destination.read_bytes() != raw and not args.overwrite:
        raise DiwanError('ALREADY_EXISTS', 'Output exists with different content; choose another --output or explicitly use --overwrite', 5)
    reused = destination.exists() and destination.read_bytes() == raw
    if not reused:
        atomic_write(destination, raw, exclusive=not args.overwrite)
    return {'path': str(destination), 'bytes': len(raw), 'sha256': digest(raw), 'format': args.format, 'source_version': current['version'], 'reused': reused}


def run(args, commands):
    if args.command == 'agent-context':
        names = [args.selected] if args.selected else list(EXAMPLES)
        definitions = {}
        for name in names:
            p = commands.choices[name]
            definitions[name] = {'example': 'python3 diwan.py ' + EXAMPLES[name],
                'mutates_poem': name in ('create', 'update', 'restore'), 'local_server': name in ('open', 'serve', 'stop'),
                'one_of': [{'required': group.required, 'flags': [a.option_strings[0] for a in group._group_actions]} for group in p._mutually_exclusive_groups],
                'arguments': [
                {'flags': a.option_strings or [a.dest], 'required': a.required, 'type': 'boolean' if isinstance(a, argparse._StoreTrueAction) else getattr(a.type, '__name__', 'string'),
                 'choices': list(a.choices) if a.choices is not None else None,
                 'default': None if a.default == argparse.SUPPRESS else a.default}
                for a in p._actions if a.dest != 'help']}
            if not args.selected:
                definitions[name].pop('arguments')
                definitions[name].pop('one_of')
        return {'schema_version': 1, 'cli_version': VERSION, 'commands': definitions,
                'detail_command': 'agent-context --command COMMAND --json',
                'delivery_schemes': ['stdout:json', 'file:atomic', 'browser:loopback'],
                'exit_codes': {'0': 'success', '2': 'invalid input', '4': 'not found', '5': 'conflict', '6': 'I/O or delivery uncertainty'},
                'conditional_capabilities': {'profiles': 'not applicable: explicit document paths, no credentials/configuration',
                   'remote_jobs': 'not applicable: local synchronous operations; open owns a reusable local server',
                   'upstream_feedback': 'not configured; no remote sending', 'platforms': 'safe writes: macOS/Linux'},
                'mutations': 'update/restore require if-version and a stable request-id. Conflicts require rereading/reassessment. Direct writes outside this API do not honor advisory locks.'}
    store = Store(args.file)
    if args.command in ('create', 'update'):
        patch = parse(input_bytes(args.input)) if args.input else {'text': input_bytes(args.text_file).decode('utf-8')}
        validate_patch(patch)
        if args.command == 'create':
            if args.title:
                patch = patch | {'title': args.title}
            return store.create(patch, args.dry_run)
        return store.update(patch, args.if_version, args.request_id, args.dry_run)
    if args.command == 'get':
        return store.get()
    if args.command == 'history':
        return store.history(args.limit, args.before)
    if args.command == 'restore':
        return store.restore(args.revision, args.if_version, args.request_id, args.dry_run)
    if args.command in ('open', 'serve'):
        if not 0 <= args.port <= 65535:
            raise DiwanError('INVALID_PORT', '--port must be 0–65535')
        if args.command == 'open':
            return open_poem(store, args)
        serve(store, args.port)
        return None
    if args.command == 'stop':
        current = session(store)
        if current:
            request(current['url'], '/shutdown', {})
        return {'path': str(store.path), 'stopped': bool(current), 'already_stopped': not bool(current)}
    if args.command == 'scan':
        current = store.get()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'poem.txt'
            path.write_text(current['poem']['text'], encoding='utf-8')
            command = [sys.executable, str(SCRIPT.with_name('scan.py')), 'analyze', str(path), '--json', '--mode', current['poem']['mode']]
            if current['poem']['meter']:
                command += ['--meter', current['poem']['meter']]
            result = subprocess.run(command, text=True, capture_output=True)
            if result.returncode:
                raise DiwanError('SCAN_FAILED', result.stderr[-2000:] or 'Scanner could not analyze this reading', 6)
            return {'path': str(store.path), 'source_version': current['version'], 'analysis': parse(result.stdout.encode())}
    if args.command == 'export':
        return export(store, args)
    if args.command == 'pending':
        store.check_binding()
        if not 1 <= args.limit <= 100:
            raise DiwanError('INVALID_LIMIT', '--limit must be 1–100')
        workspace = store.state / 'agent'
        rows = serve_diwan.pending(workspace) if (workspace/'.diwan/requests').is_dir() else []
        return {'requests': rows[:args.limit], 'truncated': len(rows) > args.limit, 'hint': 'respond to oldest pending requests before requesting more'}
    if args.command == 'respond':
        store.check_binding()
        if not (store.state/'agent/.diwan/requests').is_dir():
            raise DiwanError('NOT_FOUND', 'No pending request workspace; open Diwan and ask the existing chat to handle a request', 4)
        try:
            serve_diwan.respond(store.state / 'agent', args.id, parse(input_bytes(args.input)))
        except serve_diwan.RequestError as error:
            raise DiwanError(error.code, str(error), error.exit_code) from error
        return {'id': args.id, 'status': 'response_saved', 'poem_changed': False}


def main():
    try:
        root, commands = parser()
        args = root.parse_args()
        result = run(args, commands)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DiwanError, OSError, UnicodeError, ValueError) as error:
        if isinstance(error, UnicodeError):
            error = DiwanError('INVALID_UTF8', 'Use UTF-8 text/Markdown or a Diwan JSON document; binary document import is not supported')
        if not isinstance(error, DiwanError):
            error = DiwanError('IO_ERROR', str(error) + '; inspect get before retrying a mutation with the same request-id', 6)
        value = {'error': {'code': error.code, 'message': str(error), **error.details}}
        print(json.dumps(value, ensure_ascii=False), file=sys.stderr)
        return error.exit_code
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())

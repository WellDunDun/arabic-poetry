"""Serve Diwan with automatic local-client suggestions or a manual chat queue."""
import argparse
import json
import os
import re
import secrets
import signal
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from diwan_agent import AgentError, Dispatcher, MAX_PROMPT, select_agent
from diwan_updates import CONTROL_ENV, InstalledRuntime, RuntimeControl, TOKEN_ENV
from diwan_store import DiwanError

MAX_BODY = 2_000_000
REQUEST_TTL = 10 * 60
ID = re.compile(r'^[0-9a-f]{32}$')


class RequestError(ValueError):
    def __init__(self, code, message, exit_code):
        super().__init__(message)
        self.code, self.exit_code = code, exit_code


def write_json(path, value, *, overwrite=True):
    """Publish complete JSON atomically, optionally rejecting an existing file."""
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if overwrite:
            temp.replace(path)
        else:
            os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def queue_dirs(workspace):
    """Keep the bridge's files together, separate from the installed skill."""
    queue = Path(workspace).resolve() / '.diwan'
    for name in ('requests', 'responses', 'cancelled', 'failed'):
        (queue / name).mkdir(parents=True, exist_ok=True)
    try:
        with (queue / '.gitignore').open('x', encoding='utf-8') as ignore:
            ignore.write('*\n')
    except FileExistsError:
        pass
    return queue


def open_requests(queue):
    """List unanswered, uncancelled files, including expired requests."""
    return [path for path in (queue / 'requests').glob('*.json')
            if not (queue / 'responses' / path.name).exists()
            and not (queue / 'failed' / path.name).exists()
            and not (queue / 'cancelled' / path.name).exists()]


def make_server(workspace, port=None, page=None, document=None, agent='manual'):
    """Start a loopback session and invalidate requests from earlier sessions."""
    if page is not None:
        page = Path(page).resolve()
        if Path(workspace).resolve() not in page.parents or page.suffix != '.html' or not page.is_file():
            raise ValueError('Prepared page must be an HTML file inside the poem workspace')
    client = select_agent(agent)
    queue = queue_dirs(workspace)
    dispatcher = Dispatcher(client, queue, respond, write_json) if client else None
    port_file = queue / 'port.json'
    if port is None:
        port = 0
        if port_file.exists():
            saved = json.loads(port_file.read_text(encoding='utf-8'))
            if not isinstance(saved, dict) or type(saved.get('port')) is not int or not 1 <= saved['port'] <= 65535:
                raise ValueError('Invalid saved Diwan port; use --port to choose one explicitly')
            port = saved['port']
    assets = Path(__file__).resolve().parent.parent / 'assets' / 'workbench'
    page_html = (page or assets / 'diwan.html').read_text(encoding='utf-8')
    if '<script' not in page_html or 'DiwanFileConnection' not in page_html:
        raise ValueError('Diwan page is incomplete; keep the previous runtime')
    token = os.environ.pop(TOKEN_ENV, '') if document is not None else ''
    if token and not re.fullmatch(r'[A-Za-z0-9_-]{43}', token):
        raise ValueError('Invalid runtime handoff token')
    token = token or secrets.token_urlsafe(32)
    prefix = '/' + token
    lock = threading.Lock()
    document_writes = 0
    served = None if document is None else {'path': str(document.path), 'id': document.get()['poem']['id']}
    runtime = InstalledRuntime() if document is not None else None
    control = RuntimeControl(document,os.environ[CONTROL_ENV]) if document is not None and os.environ.get(CONTROL_ENV) else None

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            """Suppress request logging so session URLs and poem data stay private."""
            pass  # Do not log poem contents or the session URL.

        def send(self, code, value, content_type='application/json; charset=utf-8'):
            """Return a bounded response without cache or referrer disclosure."""
            data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def route(self):
            """Enforce this loopback host, origin and secret session prefix."""
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host') != urlsplit(origin).netloc:
                self.send(403, {'error': 'Invalid host'})
                return None
            if self.headers.get('Origin') not in (None, origin):
                self.send(403, {'error': 'Cross-origin requests are not allowed'})
                return None
            path = urlsplit(self.path).path
            if not path.startswith(prefix + '/'):
                self.send(404, {'error': 'Unknown session'})
                return None
            return path[len(prefix):]

        def do_GET(self):
            """Serve the editor or the current state of a queued response."""
            path = self.route()
            if path is None:
                return
            if path in ('/', '/diwan.html'):
                config = {'base': prefix, 'workspace': str(Path(workspace).resolve()),
                          'script': str(Path(__file__).resolve()), 'agent': client.name if client else 'manual',
                          'manual': agent == 'manual'}
                encoded = json.dumps(config, ensure_ascii=False).replace('<', '\\u003c')
                html = page_html
                html = '<script>window.DiwanLocal=' + encoded + ';</script>\n' + html
                if document is not None:
                    html = '<script>window.DiwanFile=' + json.dumps({'base': prefix, 'runtime': runtime.version, 'id': served['id']}).replace('<', '\\u003c') + ';</script>\n' + html
                self.send(200, html.encode('utf-8'), 'text/html; charset=utf-8')
            elif runtime is not None and path == '/runtime':
                self.send(200, dict(runtime.status(), id=served['id']))
            elif document is not None and path in ('/document', '/status', '/history'):
                self.document_call(path)
            elif path.startswith('/responses/') and ID.fullmatch(path.split('/')[-1]):
                identity = path.split('/')[-1]
                response = queue / 'responses' / (identity + '.json')
                if not (queue / 'requests' / (identity + '.json')).exists():
                    self.send(404, {'error': 'Unknown request'})
                elif (queue / 'cancelled' / (identity + '.json')).exists():
                    self.send(410, {'error': 'Cancelled'})
                elif (queue / 'failed' / (identity + '.json')).exists():
                    self.send(502, (queue / 'failed' / (identity + '.json')).read_bytes())
                elif response.exists():
                    self.send(200, response.read_bytes())
                else:
                    self.send(202, {'pending': True})
            else:
                self.send(404, {'error': 'Not found'})

        def do_POST(self):
            """Validate JSON input before queuing or cancelling a request."""
            nonlocal document_writes
            path = self.route()
            if path is None:
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= MAX_BODY or self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('Expected bounded application/json body')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('Expected an object')
            except (ValueError, UnicodeError):
                self.send(400, {'error': 'Invalid JSON request'})
                return
            if document is not None and path == '/document':
                with lock:
                    if self.server.diwan_restart:
                        self.send(503, {'error': {'code': 'UPDATING', 'message': 'Diwan is updating. Keep the draft and retry this same save after reconnecting.'}})
                        return
                    document_writes += 1
                try:
                    self.document_call(path, data)
                finally:
                    with lock:
                        document_writes -= 1
                return
            if document is not None and path == '/shutdown':
                with lock:
                    if control:
                        try:
                            control.request_stop()
                        except (OSError,DiwanError):
                            pass  # Still stop this owned worker; its supervisor observes exit 0.
                    self.server.diwan_stopping = True
                    self.server.diwan_restart = False
                    self.send(200, {'stopped': True})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            if runtime is not None and path == '/runtime':
                # A browser sends no paths or executable arguments. The installation decides.
                if data:
                    self.send(400, {'error': 'Runtime updates take no arguments'})
                    return
                with lock:
                    if self.server.diwan_stopping:
                        self.send(200,{'restarting':False})
                        return
                    try:
                        if document.get()['poem']['id'] != served['id']:
                            raise ValueError('Document identity changed')
                    except (OSError, ValueError, DiwanError):
                        self.send(409, {'error': 'Reopen the intended poem before updating Diwan'})
                        return
                    candidate = runtime.candidate(force=True)
                    if dispatcher:
                        with dispatcher.lock:
                            active = bool(dispatcher.jobs)
                    else:
                        active = bool(pending(workspace))
                    if candidate and not active and not document_writes and not self.server.diwan_restart:
                        self.server.diwan_restart = True
                        self.send(200, {'restarting': True})
                        threading.Thread(target=self.server.shutdown, daemon=True).start()
                    else:
                        self.send(200, {'restarting': self.server.diwan_restart})
                return
            if path == '/requests':
                value = data.get('input')
                if not isinstance(value, str) and not (isinstance(value, list) and value and all(
                        isinstance(t, dict) and t.get('role') in ('user', 'assistant') and
                        isinstance(t.get('content'), str) for t in value)):
                    self.send(400, {'error': 'Expected a prompt or conversation turns'})
                    return
                if not value or len(json.dumps(value, ensure_ascii=False).encode('utf-8')) > MAX_PROMPT:
                    self.send(400, {'error': {'code': 'PROMPT_TOO_LARGE', 'message': 'Use a nonempty poetry request under 128000 UTF-8 bytes.'}})
                    return
                identity = uuid.uuid4().hex
                with lock:
                    if self.server.diwan_restart:
                        self.send(503, {'error': {'code': 'UPDATING', 'message': 'Diwan is updating. Retry this suggestion after it reconnects.'}})
                        return
                    write_json(queue / 'requests' / (identity + '.json'), {'id': identity, 'input': value})
                    if dispatcher:
                        try:
                            dispatcher.submit(identity, value)
                        except AgentError as error:
                            write_json(queue / 'cancelled' / (identity + '.json'), {'cancelled': True})
                            self.send(409, {'error': {'code': error.code, 'message': str(error)}})
                            return
                self.send(201, {'id': identity})
            elif path.startswith('/cancel/') and ID.fullmatch(path.split('/')[-1]):
                identity = path.split('/')[-1]
                with lock:
                    write_json(queue / 'cancelled' / (identity + '.json'), {'cancelled': True})
                if dispatcher:
                    dispatcher.cancel(identity)
                self.send(200, {'cancelled': True})
            else:
                self.send(404, {'error': 'Not found'})

        def document_call(self, path, data=None):
            from diwan_store import DiwanError
            if path == '/status':
                self.send(200, served)
                return
            try:
                current = document.get()
                if current['poem']['id'] != served['id']:
                    raise DiwanError('DOCUMENT_REPLACED', 'This path contains another poem. Reopen the intended shared document.', 5)
                if data is not None:
                    result = document.update(data.get('patch'), data.get('if_version'), data.get('request_id'))
                elif path == '/history':
                    result = document.history()
                else:
                    result = current
                self.send(200, result)
            except DiwanError as error:
                self.send(409 if error.exit_code == 5 else 400, {'error': {'code': error.code, 'message': str(error), **error.details}})
            except OSError:
                self.send(500, {'error': {'code': 'IO_ERROR', 'message': 'Save may be incomplete. Keep the draft and retry the same request id, or inspect the document with get.'}})

    class Server(ThreadingHTTPServer):
        def server_close(self):
            if dispatcher:
                dispatcher.close()
            super().server_close()

    try:
        server = Server(('127.0.0.1', port), Handler)
    except OSError as error:
        raise OSError(f'Diwan port {port} is unavailable. Stop the existing server or choose --port explicitly; a different port uses separate browser storage.') from error
    try:
        write_json(port_file, {'port': server.server_port})
        for stale in open_requests(queue):
            write_json(queue / 'cancelled' / stale.name, {'cancelled': True})
    except OSError:
        server.server_close()
        raise
    server.diwan_agent = client.name if client else 'manual'
    server.diwan_restart = False
    server.diwan_stopping = False
    return server, f'http://127.0.0.1:{server.server_port}{prefix}/diwan.html'


def pending(workspace):
    """Return live requests oldest first, matching the browser's ten-minute wait."""
    queue = queue_dirs(workspace)
    cutoff = time.time() - REQUEST_TTL
    files = sorted(open_requests(queue), key=lambda path: (path.stat().st_mtime, path.name))
    return [json.loads(path.read_text(encoding='utf-8')) for path in files
            if path.stat().st_mtime >= cutoff]


def respond(workspace, identity, value):
    """Publish one complete answer; concurrent responders cannot overwrite it."""
    queue = queue_dirs(workspace)
    if not ID.fullmatch(identity):
        raise RequestError('INVALID_REQUEST_ID', 'Unknown request ID format; expected 32 lowercase hexadecimal characters', 2)
    if not (queue / 'requests' / (identity + '.json')).exists():
        raise RequestError('NOT_FOUND', 'Unknown request ID; use pending to select a live request', 4)
    if (queue / 'cancelled' / (identity + '.json')).exists():
        raise RequestError('CONFLICT', 'Request was cancelled; use pending to select a live request', 5)
    if (queue / 'responses' / (identity + '.json')).exists():
        raise RequestError('CONFLICT', 'Request already has a response; do not resubmit it', 5)
    if (queue / 'failed' / (identity + '.json')).exists():
        raise RequestError('CONFLICT', 'Request failed; request new suggestions instead of answering it', 5)
    if (queue / 'requests' / (identity + '.json')).stat().st_mtime < time.time() - REQUEST_TTL:
        raise RequestError('NOT_FOUND', 'Request expired; use pending to select a live request', 4)
    if not isinstance(value, (dict, list)):
        raise RequestError('INVALID_RESPONSE', 'Response must be a JSON object or array', 2)
    try:
        write_json(queue / 'responses' / (identity + '.json'), value, overwrite=False)
    except FileExistsError as error:
        raise RequestError('CONFLICT', 'Request already has a response; do not resubmit it', 5) from error


def run_server(server):
    """Drain owned client workers on normal stop, Ctrl-C, SIGTERM and SIGHUP."""
    previous = {}
    def stop(signum, frame):
        raise KeyboardInterrupt
    if threading.current_thread() is threading.main_thread():
        for name in ('SIGTERM', 'SIGHUP'):
            number = getattr(signal, name, None)
            if number is not None:
                previous[number] = signal.signal(number, stop)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        for number, handler in previous.items():
            signal.signal(number, handler)


def main():
    """Run the selected local server, pending-list or response command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('serve', 'pending', 'respond'))
    parser.add_argument('--workspace', required=True, help='Writable poem workspace, outside the installed skill')
    parser.add_argument('--port', type=int, help='Override the saved workspace port; 0 chooses a new free port')
    parser.add_argument('--page', type=Path, help='Prepared Diwan HTML inside the workspace, for serve')
    parser.add_argument('--agent', choices=('auto', 'claude', 'codex', 'manual'), default='auto',
                        help='AI client for serve; auto detects installed Codex/Claude, manual queues for the existing chat')
    parser.add_argument('--id', help='Request ID for respond')
    parser.add_argument('--response', type=Path, help='UTF-8 JSON answer file for respond')
    args = parser.parse_args()
    if args.action == 'serve':
        try:
            server, url = make_server(args.workspace, args.port, args.page, agent=args.agent)
        except (OSError, ValueError) as error:
            parser.exit(1, str(error) + '\n')
        print(url, flush=True)
        print('AI: ' + server.diwan_agent + '. Automatic requests use the selected installed client; manual requests wait for your chat.', flush=True)
        run_server(server)
    elif args.action == 'pending':
        print(json.dumps(pending(args.workspace), ensure_ascii=False, indent=2))
    else:
        if not args.id or not args.response:
            parser.error('respond requires --id and --response')
        try:
            respond(args.workspace, args.id, json.loads(args.response.read_text(encoding='utf-8')))
        except (OSError, ValueError) as error:
            parser.exit(1, str(error) + '\n')
        print('Response saved; Diwan will pick it up if the request is still open.')


if __name__ == '__main__':
    main()

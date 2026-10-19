"""Serve Diwan with a local file queue for an existing agent. No model calls."""
import argparse
import json
import os
import re
import secrets
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAX_BODY = 2_000_000
REQUEST_TTL = 10 * 60
ID = re.compile(r'^[0-9a-f]{32}$')


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
    for name in ('requests', 'responses', 'cancelled'):
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
            and not (queue / 'cancelled' / path.name).exists()]


def make_server(workspace, port=None, page=None, document=None):
    """Start a loopback session and invalidate requests from earlier sessions."""
    if page is not None:
        page = Path(page).resolve()
        if Path(workspace).resolve() not in page.parents or page.suffix != '.html' or not page.is_file():
            raise ValueError('Prepared page must be an HTML file inside the poem workspace')
    queue = queue_dirs(workspace)
    port_file = queue / 'port.json'
    if port is None:
        port = 0
        if port_file.exists():
            saved = json.loads(port_file.read_text(encoding='utf-8'))
            if not isinstance(saved, dict) or type(saved.get('port')) is not int or not 1 <= saved['port'] <= 65535:
                raise ValueError('Invalid saved Diwan port; use --port to choose one explicitly')
            port = saved['port']
    assets = Path(__file__).resolve().parent.parent / 'assets' / 'workbench'
    token = secrets.token_urlsafe(32)
    prefix = '/' + token
    lock = threading.Lock()

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
                          'script': str(Path(__file__).resolve())}
                encoded = json.dumps(config, ensure_ascii=False).replace('<', '\\u003c')
                html = (page or assets / 'diwan.html').read_text(encoding='utf-8')
                html = '<script>window.DiwanLocal=' + encoded + ';</script>\n' + html
                if document is not None:
                    html = '<script>window.DiwanFile=' + json.dumps({'base': prefix}).replace('<', '\\u003c') + ';</script>\n' + html
                self.send(200, html.encode('utf-8'), 'text/html; charset=utf-8')
            elif document is not None and path in ('/document', '/status', '/history'):
                self.document_call(path)
            elif path.startswith('/responses/') and ID.fullmatch(path.split('/')[-1]):
                identity = path.split('/')[-1]
                response = queue / 'responses' / (identity + '.json')
                if not (queue / 'requests' / (identity + '.json')).exists():
                    self.send(404, {'error': 'Unknown request'})
                elif (queue / 'cancelled' / (identity + '.json')).exists():
                    self.send(410, {'error': 'Cancelled'})
                elif response.exists():
                    self.send(200, response.read_bytes())
                else:
                    self.send(202, {'pending': True})
            else:
                self.send(404, {'error': 'Not found'})

        def do_POST(self):
            """Validate JSON input before queuing or cancelling a request."""
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
                self.document_call(path, data)
                return
            if document is not None and path == '/shutdown':
                self.send(200, {'stopped': True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            if path == '/requests':
                value = data.get('input')
                if not isinstance(value, str) and not (isinstance(value, list) and value and all(
                        isinstance(t, dict) and t.get('role') in ('user', 'assistant') and
                        isinstance(t.get('content'), str) for t in value)):
                    self.send(400, {'error': 'Expected a prompt or conversation turns'})
                    return
                identity = uuid.uuid4().hex
                write_json(queue / 'requests' / (identity + '.json'), {'id': identity, 'input': value})
                self.send(201, {'id': identity})
            elif path.startswith('/cancel/') and ID.fullmatch(path.split('/')[-1]):
                identity = path.split('/')[-1]
                with lock:
                    write_json(queue / 'cancelled' / (identity + '.json'), {'cancelled': True})
                self.send(200, {'cancelled': True})
            else:
                self.send(404, {'error': 'Not found'})

        def document_call(self, path, data=None):
            from diwan_store import DiwanError
            try:
                if data is not None:
                    result = document.update(data.get('patch'), data.get('if_version'), data.get('request_id'))
                elif path == '/history':
                    result = document.history()
                else:
                    result = document.get()
                    if path == '/status':
                        result = {'path': result['path'], 'id': result['poem']['id'], 'version': result['version']}
                self.send(200, result)
            except DiwanError as error:
                self.send(409 if error.exit_code == 5 else 400, {'error': {'code': error.code, 'message': str(error), **error.details}})
            except OSError:
                self.send(500, {'error': {'code': 'IO_ERROR', 'message': 'Save may be incomplete. Keep the draft and retry the same request id, or inspect the document with get.'}})

    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except OSError as error:
        raise OSError(f'Diwan port {port} is unavailable. Stop the existing server or choose --port explicitly; a different port uses separate browser storage.') from error
    try:
        write_json(port_file, {'port': server.server_port})
        for stale in open_requests(queue):
            write_json(queue / 'cancelled' / stale.name, {'cancelled': True})
    except OSError:
        server.server_close()
        raise
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
    if not ID.fullmatch(identity) or not (queue / 'requests' / (identity + '.json')).exists():
        raise ValueError('Unknown request ID')
    if (queue / 'cancelled' / (identity + '.json')).exists():
        raise ValueError('Request was cancelled')
    if (queue / 'responses' / (identity + '.json')).exists():
        raise ValueError('Request already has a response')
    if (queue / 'requests' / (identity + '.json')).stat().st_mtime < time.time() - REQUEST_TTL:
        raise ValueError('Request expired')
    if not isinstance(value, (dict, list)):
        raise ValueError('Response must be a JSON object or array')
    try:
        write_json(queue / 'responses' / (identity + '.json'), value, overwrite=False)
    except FileExistsError as error:
        raise ValueError('Request already has a response') from error


def main():
    """Run the selected local server, pending-list or response command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('serve', 'pending', 'respond'))
    parser.add_argument('--workspace', required=True, help='Writable poem workspace, outside the installed skill')
    parser.add_argument('--port', type=int, help='Override the saved workspace port; 0 chooses a new free port')
    parser.add_argument('--page', type=Path, help='Prepared Diwan HTML inside the workspace, for serve')
    parser.add_argument('--id', help='Request ID for respond')
    parser.add_argument('--response', type=Path, help='UTF-8 JSON answer file for respond')
    args = parser.parse_args()
    if args.action == 'serve':
        try:
            server, url = make_server(args.workspace, args.port, args.page)
        except (OSError, ValueError) as error:
            parser.exit(1, str(error) + '\n')
        print(url, flush=True)
        print('Uses the existing agent via local request files. No agent is started automatically.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
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

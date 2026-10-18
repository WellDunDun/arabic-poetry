"""Serve Diwan with a local file queue for an existing agent. No model calls."""
import argparse
import json
import re
import secrets
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAX_BODY = 2_000_000
ID = re.compile(r'^[0-9a-f]{32}$')


def write_json(path, value):
    """Publish complete UTF-8 JSON so readers never see a partial answer."""
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def queue_dirs(workspace):
    """Keep the bridge's files together, separate from the installed skill."""
    queue = Path(workspace).resolve() / '.diwan'
    for name in ('requests', 'responses', 'cancelled'):
        (queue / name).mkdir(parents=True, exist_ok=True)
    return queue


def make_server(workspace, port=0):
    queue = queue_dirs(workspace)
    assets = Path(__file__).resolve().parent.parent / 'assets' / 'workbench'
    token = secrets.token_urlsafe(32)
    prefix = '/' + token
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not log poem contents or the session URL.

        def send(self, code, value, content_type='application/json; charset=utf-8'):
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
            path = self.route()
            if path is None:
                return
            if path in ('/', '/diwan.html'):
                config = {'base': prefix, 'workspace': str(Path(workspace).resolve()),
                          'script': str(Path(__file__).resolve())}
                encoded = json.dumps(config, ensure_ascii=False).replace('<', '\\u003c')
                page = (assets / 'diwan.html').read_text(encoding='utf-8')
                page = '<script>window.DiwanLocal=' + encoded + ';</script>\n' + page
                self.send(200, page.encode('utf-8'), 'text/html; charset=utf-8')
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

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    return server, f'http://127.0.0.1:{server.server_port}{prefix}/diwan.html'


def pending(workspace):
    queue = queue_dirs(workspace)
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((queue / 'requests').glob('*.json'))
            if not (queue / 'responses' / p.name).exists() and not (queue / 'cancelled' / p.name).exists()]


def respond(workspace, identity, value):
    queue = queue_dirs(workspace)
    if not ID.fullmatch(identity) or not (queue / 'requests' / (identity + '.json')).exists():
        raise ValueError('Unknown request ID')
    if (queue / 'cancelled' / (identity + '.json')).exists():
        raise ValueError('Request was cancelled')
    if (queue / 'responses' / (identity + '.json')).exists():
        raise ValueError('Request already has a response')
    if not isinstance(value, (dict, list)):
        raise ValueError('Response must be a JSON object or array')
    write_json(queue / 'responses' / (identity + '.json'), value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('serve', 'pending', 'respond'))
    parser.add_argument('--workspace', required=True, help='Writable poem workspace, outside the installed skill')
    parser.add_argument('--port', type=int, default=0, help='Local port; default chooses a free port')
    parser.add_argument('--id', help='Request ID for respond')
    parser.add_argument('--response', type=Path, help='UTF-8 JSON answer file for respond')
    args = parser.parse_args()
    if args.action == 'serve':
        server, url = make_server(args.workspace, args.port)
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

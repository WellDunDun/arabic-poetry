"""Automatic suggestion delivery through real subprocess and HTTP boundaries."""
import http.client
import json
import os
import select
import subprocess
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import serve_diwan
import diwan_agent


class AutomaticSuggestionTests(unittest.TestCase):
    def test_sigterm_stops_the_owned_model_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pid = root / 'client.pid'
            client = root / 'codex'
            client.write_text('#!' + sys.executable + '\nimport os,time,pathlib\n' +
                              'pathlib.Path(' + repr(str(pid)) + ').write_text(str(os.getpid()))\ntime.sleep(30)\n')
            client.chmod(0o755)
            source = ('import serve_diwan; server,url=serve_diwan.make_server(' + repr(str(root)) +
                      ',agent="codex"); print(url,flush=True); serve_diwan.run_server(server)')
            env = dict(os.environ, PYTHONPATH=str(Path(serve_diwan.__file__).parent),
                       PATH=str(root) + os.pathsep + os.environ['PATH'])
            process = subprocess.Popen([sys.executable, '-c', source], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True, env=env)
            try:
                self.assertTrue(select.select([process.stdout], [], [], 8)[0])
                url = process.stdout.readline().strip()
                address = urlsplit(url)
                conn = http.client.HTTPConnection('127.0.0.1', address.port, timeout=3)
                conn.request('POST', address.path.removesuffix('/diwan.html') + '/requests',
                             json.dumps({'input':'word suggestions'}), {'Content-Type':'application/json'})
                response = conn.getresponse()
                self.assertEqual(response.status, 201)
                response.read(); conn.close()
                deadline = time.monotonic() + 8
                while not pid.exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue(pid.exists())
                process.terminate()
                self.assertEqual(process.wait(5), 0)
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid.read_text()), 0)
            finally:
                if process.poll() is None:
                    process.kill(); process.wait()
                process.stdout.close(); process.stderr.close()
    def test_detection_and_manual_mode_never_start_a_client(self):
        with mock.patch('diwan_agent.shutil.which', return_value=None), mock.patch('subprocess.Popen') as process:
            self.assertIsNone(diwan_agent.select_agent('manual'))
            self.assertIsNone(diwan_agent.select_agent('auto'))
            with self.assertRaisesRegex(diwan_agent.AgentError, 'not installed'):
                diwan_agent.select_agent('claude')
            process.assert_not_called()

    def test_busy_and_shutdown_do_not_leave_a_worker_running(self):
        started, finished = threading.Event(), threading.Event()
        class WaitingAgent:
            def sample(self, value, cancelled):
                started.set()
                cancelled.wait(3)
                finished.set()
                raise diwan_agent.AgentError('CANCELLED', 'Request cancelled.')
        with tempfile.TemporaryDirectory() as directory:
            queue = serve_diwan.queue_dirs(directory)
            dispatcher = diwan_agent.Dispatcher(WaitingAgent(), queue, serve_diwan.respond, serve_diwan.write_json)
            try:
                dispatcher.submit('a' * 32, 'word suggestions')
                self.assertTrue(started.wait(1))
                with self.assertRaisesRegex(diwan_agent.AgentError, 'already running'):
                    dispatcher.submit('b' * 32, 'another request')
            finally:
                dispatcher.close()
            self.assertTrue(finished.is_set(), 'shutdown must wait for the owned worker to stop')
            self.assertEqual(dispatcher.jobs, {})
            self.assertFalse(list((queue / 'responses').glob('*.json')))
            self.assertFalse(list((queue / 'failed').glob('*.json')))

    def test_unexpected_worker_errors_complete_as_failures(self):
        class BrokenAgent:
            def sample(self, value, cancelled):
                raise RuntimeError('internal detail must not leak into the browser')
        with tempfile.TemporaryDirectory() as directory:
            queue = serve_diwan.queue_dirs(directory)
            dispatcher = diwan_agent.Dispatcher(BrokenAgent(), queue, serve_diwan.respond, serve_diwan.write_json)
            dispatcher.submit('a' * 32, 'word suggestions')
            deadline = time.monotonic() + 2
            failure = queue / 'failed' / ('a' * 32 + '.json')
            while not failure.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            dispatcher.close()
            self.assertEqual(json.loads(failure.read_text())['error']['code'], 'AGENT_FAILED')
            self.assertNotIn('internal detail', failure.read_text())

    def test_timeout_and_cancellation_reap_the_owned_client(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = root / 'codex'
            client.write_text('#!' + sys.executable + '\nimport time\ntime.sleep(30)\n')
            client.chmod(0o755)
            agent = diwan_agent.Agent('codex', str(client))
            started = []
            original = diwan_agent.subprocess.Popen
            def capture(*args, **kwargs):
                process = original(*args, **kwargs)
                started.append(process.pid)
                return process
            with mock.patch('diwan_agent.subprocess.Popen', side_effect=capture):
                with self.assertRaisesRegex(diwan_agent.AgentError, 'timed out'):
                    agent.sample('word suggestions', threading.Event(), timeout=.25)
            with self.assertRaises(ProcessLookupError):
                os.kill(started[-1], 0)
            cancelled = threading.Event()
            timer = threading.Timer(.25, cancelled.set)
            timer.start()
            try:
                with mock.patch('diwan_agent.subprocess.Popen', side_effect=capture):
                    with self.assertRaisesRegex(diwan_agent.AgentError, 'cancelled'):
                        agent.sample('word suggestions', cancelled)
            finally:
                timer.join()
            with self.assertRaises(ProcessLookupError):
                os.kill(started[-1], 0)

    def test_invalid_agent_outputs_are_actionable_failures(self):
        for name, output in [('codex', 'not JSON'), ('codex', '```'), ('claude', '[]'),
                             ('claude', '{"is_error":true,"result":"Login required"}')]:
            with self.subTest(name=name, output=output), tempfile.TemporaryDirectory() as directory:
                client = Path(directory) / name
                client.write_text('#!' + sys.executable + '\nprint(' + repr(output) + ')\n')
                client.chmod(0o755)
                with self.assertRaises(diwan_agent.AgentError) as failed:
                    diwan_agent.Agent(name, str(client)).sample('word suggestions', threading.Event())
                self.assertIn(failed.exception.code, ('INVALID_RESPONSE', 'AGENT_FAILED'))

    def test_single_line_fenced_json_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            client = Path(directory) / 'codex'
            client.write_text('#!' + sys.executable + '\nprint(\'```{"synonyms":[]}```\')\n')
            client.chmod(0o755)
            result = diwan_agent.Agent('codex', str(client)).sample('word suggestions', threading.Event())
            self.assertEqual(result, {'synonyms': []})

    def test_both_clients_deliver_without_manual_response(self):
        for agent in ('claude', 'codex'):
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                client = root / agent
                client.write_text('#!' + sys.executable + '\n' + '''
import json, pathlib, sys
prompt = sys.stdin.read()
assert 'كتابي' in prompt
args = sys.argv[1:]
assert '--resume' not in args and '--continue' not in args
if pathlib.Path(sys.argv[0]).name == 'claude':
    assert args[args.index('--tools') + 1] == ''
    assert '--no-session-persistence' in args
    print(json.dumps({'is_error':False, 'result':json.dumps({'synonyms':[{'text':'دَفْتَرِي','note':'my notebook'}]})}))
else:
    assert args[args.index('--sandbox') + 1] == 'read-only'
    assert 'features.shell_tool=false' in args
    assert 'features.plugins=false' in args
    assert '--ephemeral' in args
    print(json.dumps({'synonyms':[{'text':'دَفْتَرِي','note':'my notebook'}]}))
''')
                client.chmod(0o755)
                with mock.patch.dict(os.environ, {'PATH': str(root) + os.pathsep + os.environ['PATH']}):
                    server, url = serve_diwan.make_server(root, agent=agent)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base = urlsplit(url).path.removesuffix('/diwan.html')
                def request(method, path, value=None):
                    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=4)
                    try:
                        conn.request(method, base + path, None if value is None else json.dumps(value),
                                     {'Content-Type':'application/json'})
                        response = conn.getresponse()
                        return response.status, response.read()
                    finally:
                        conn.close()
                try:
                    code, html = request('GET', '/diwan.html')
                    self.assertEqual(code, 200)
                    self.assertIn(('"agent": "' + agent + '"').encode(), html)
                    code, raw = request('POST', '/requests', {'input':'Suggest a replacement for كتابي. JSON only.'})
                    self.assertEqual(code, 201)
                    identity = json.loads(raw)['id']
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        code, raw = request('GET', '/responses/' + identity)
                        if code != 202:
                            break
                        time.sleep(.02)
                    self.assertEqual(code, 200, raw)
                    self.assertEqual(json.loads(raw)['synonyms'][0]['text'], 'دَفْتَرِي')
                    self.assertEqual(serve_diwan.pending(root), [])
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(2)


if __name__ == '__main__':
    unittest.main()

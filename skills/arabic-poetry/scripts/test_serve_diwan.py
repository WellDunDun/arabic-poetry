"""Local bridge lifecycle and origin boundary regressions; no model requests."""
import concurrent.futures
import http.client
import json
import os
import tempfile
import threading
import time
import unittest
from unittest import mock
from urllib.parse import urlsplit

import serve_diwan as bridge


class LocalBridgeTests(unittest.TestCase):
    def setUp(self):
        """Start an isolated workspace and loopback server for each regression."""
        self.temp = tempfile.TemporaryDirectory(prefix='diwan-bridge-test-')
        self.addCleanup(self.temp.cleanup)
        self.server, url = bridge.make_server(self.temp.name)
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.shutdown)
        self.base = urlsplit(url).path.removesuffix('/diwan.html')

    def request(self, method, path, data=None, headers=None):
        """Send a request to this test session and return its status and body."""
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            body = None if data is None else json.dumps(data)
            connection.request(method, self.base + path, body, headers or {'Content-Type': 'application/json'})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def create(self):
        """Queue a valid prompt and return its assigned request ID."""
        code, raw = self.request('POST', '/requests', {'input': 'شكّل سلام وأجب بـ JSON'})
        self.assertEqual(code, 201)
        return json.loads(raw)['id']

    def test_round_trip_and_no_duplicate_reply(self):
        """Verify request delivery and rejection of a second sequential answer."""
        identity = self.create()
        self.assertEqual(bridge.pending(self.temp.name)[0]['id'], identity)
        self.assertEqual(self.request('GET', '/responses/' + identity)[0], 202)
        answer = {'lines': ['سَلَام'], 'choices': []}
        bridge.respond(self.temp.name, identity, answer)
        code, raw = self.request('GET', '/responses/' + identity)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw), answer)
        self.assertEqual(bridge.pending(self.temp.name), [])
        with self.assertRaisesRegex(ValueError, 'already'):
            bridge.respond(self.temp.name, identity, answer)

    def test_concurrent_replies_do_not_overwrite(self):
        """Both responders pass the precheck, but only one can publish an answer."""
        identity = self.create()
        barrier = threading.Barrier(2)
        publish = bridge.write_json

        def together(path, value, **options):
            """Pause both publishers after their existing-answer prechecks."""
            barrier.wait(timeout=3)
            return publish(path, value, **options)

        def answer(number):
            """Return the winning response ID or confirm duplicate rejection."""
            try:
                bridge.respond(self.temp.name, identity, {'answer': number})
                return number
            except ValueError as error:
                self.assertIn('already', str(error))
                return None

        with mock.patch.object(bridge, 'write_json', side_effect=together):
            with concurrent.futures.ThreadPoolExecutor(2) as pool:
                results = list(pool.map(answer, [1, 2]))
        accepted = [number for number in results if number is not None]
        self.assertEqual(len(accepted), 1)
        code, raw = self.request('GET', '/responses/' + identity)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw), {'answer': accepted[0]})
        self.assertEqual(list((bridge.queue_dirs(self.temp.name) / 'responses').glob('*.tmp')), [])

    def test_pending_order_and_expiry(self):
        """Ignore expired requests and order live requests by their creation write."""
        queue = bridge.queue_dirs(self.temp.name)
        now = time.time()
        identities = ['f' * 32, '0' * 32, '1' * 32]
        for identity, age in zip(identities, [60, 5, 601]):
            path = queue / 'requests' / (identity + '.json')
            bridge.write_json(path, {'id': identity, 'input': identity})
            os.utime(path, (now - age, now - age))
        self.assertEqual([r['id'] for r in bridge.pending(self.temp.name)], identities[:2])
        with self.assertRaisesRegex(ValueError, 'expired'):
            bridge.respond(self.temp.name, identities[2], {})

    def test_restart_cancels_live_and_expired_requests(self):
        """A new session invalidates all open old-token work, not completed answers."""
        live, expired, answered = self.create(), self.create(), self.create()
        queue = bridge.queue_dirs(self.temp.name)
        old = time.time() - 601
        os.utime(queue / 'requests' / (expired + '.json'), (old, old))
        bridge.respond(self.temp.name, answered, {'answer': 'done'})
        restarted, _ = bridge.make_server(self.temp.name)
        self.addCleanup(restarted.server_close)
        self.assertEqual(bridge.pending(self.temp.name), [])
        for identity in [live, expired]:
            self.assertTrue((queue / 'cancelled' / (identity + '.json')).exists())
            with self.assertRaisesRegex(ValueError, 'cancelled'):
                bridge.respond(self.temp.name, identity, {})
        self.assertFalse((queue / 'cancelled' / (answered + '.json')).exists())
        self.assertEqual(json.loads((queue / 'responses' / (answered + '.json')).read_text()), {'answer': 'done'})

    def test_failed_restart_preserves_active_requests(self):
        """Failing to bind an occupied port must not cancel the active session."""
        identity = self.create()
        with self.assertRaises(OSError):
            bridge.make_server(self.temp.name, self.server.server_port)
        self.assertEqual([r['id'] for r in bridge.pending(self.temp.name)], [identity])

    def test_queue_ignore_file_is_created_and_preserved(self):
        """New queue data is ignored without overwriting an existing ignore policy."""
        ignore = bridge.queue_dirs(self.temp.name) / '.gitignore'
        self.assertEqual(ignore.read_text(), '*\n')
        ignore.write_text('custom-rule\n')
        bridge.queue_dirs(self.temp.name)
        self.assertEqual(ignore.read_text(), 'custom-rule\n')

    def test_cancelled_request_is_not_answered(self):
        """Keep cancelled requests out of pending work and reject late answers."""
        identity = self.create()
        self.assertEqual(self.request('POST', '/cancel/' + identity, {})[0], 200)
        self.assertEqual(bridge.pending(self.temp.name), [])
        self.assertEqual(self.request('GET', '/responses/' + identity)[0], 410)
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            bridge.respond(self.temp.name, identity, {})

    def test_host_and_origin_are_restricted(self):
        """Reject foreign hosts and origins before reading or writing queue data."""
        self.assertEqual(self.request('GET', '/diwan.html', headers={'Host': 'attacker.example'})[0], 403)
        self.assertEqual(self.request('POST', '/requests', {'input': 'x'},
                         {'Origin': 'https://attacker.example', 'Content-Type': 'application/json'})[0], 403)
        self.assertEqual(bridge.pending(self.temp.name), [])

    def test_invalid_input_and_path_are_rejected(self):
        """Reject malformed turns, traversal paths and unknown request IDs."""
        self.assertEqual(self.request('POST', '/requests', {'input': [{'role': 'user'}]})[0], 400)
        self.assertEqual(self.request('GET', '/responses/../../secrets')[0], 404)
        self.assertEqual(self.request('GET', '/responses/' + '0' * 32)[0], 404)
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            bridge.respond(self.temp.name, '../outside', {})

    def test_served_editor_has_local_config(self):
        """Embed the active local connection settings in the served editor."""
        code, raw = self.request('GET', '/diwan.html')
        self.assertEqual(code, 200)
        self.assertIn(b'window.DiwanLocal=', raw)
        self.assertIn(self.base.encode(), raw)


if __name__ == '__main__':
    unittest.main()

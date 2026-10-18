"""Local bridge lifecycle and origin boundary regressions; no model requests."""
import http.client
import json
import tempfile
import threading
import unittest
from urllib.parse import urlsplit

import serve_diwan as bridge


class LocalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='diwan-bridge-test-')
        self.addCleanup(self.temp.cleanup)
        self.server, url = bridge.make_server(self.temp.name)
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.shutdown)
        self.base = urlsplit(url).path.removesuffix('/diwan.html')

    def request(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            body = None if data is None else json.dumps(data)
            connection.request(method, self.base + path, body, headers or {'Content-Type': 'application/json'})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def create(self):
        code, raw = self.request('POST', '/requests', {'input': 'شكّل سلام وأجب بـ JSON'})
        self.assertEqual(code, 201)
        return json.loads(raw)['id']

    def test_round_trip_and_no_duplicate_reply(self):
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

    def test_cancelled_request_is_not_answered(self):
        identity = self.create()
        self.assertEqual(self.request('POST', '/cancel/' + identity, {})[0], 200)
        self.assertEqual(bridge.pending(self.temp.name), [])
        self.assertEqual(self.request('GET', '/responses/' + identity)[0], 410)
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            bridge.respond(self.temp.name, identity, {})

    def test_host_and_origin_are_restricted(self):
        self.assertEqual(self.request('GET', '/diwan.html', headers={'Host': 'attacker.example'})[0], 403)
        self.assertEqual(self.request('POST', '/requests', {'input': 'x'},
                         {'Origin': 'https://attacker.example', 'Content-Type': 'application/json'})[0], 403)
        self.assertEqual(bridge.pending(self.temp.name), [])

    def test_invalid_input_and_path_are_rejected(self):
        self.assertEqual(self.request('POST', '/requests', {'input': [{'role': 'user'}]})[0], 400)
        self.assertEqual(self.request('GET', '/responses/../../secrets')[0], 404)
        self.assertEqual(self.request('GET', '/responses/' + '0' * 32)[0], 404)
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            bridge.respond(self.temp.name, '../outside', {})

    def test_served_editor_has_local_config(self):
        code, raw = self.request('GET', '/diwan.html')
        self.assertEqual(code, 200)
        self.assertIn(b'window.DiwanLocal=', raw)
        self.assertIn(self.base.encode(), raw)


if __name__ == '__main__':
    unittest.main()

"""Executable CLI, concurrent writer, recovery and local HTTP contracts."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import select
import shlex
import shutil
import unicodedata
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import diwan
import diwan_store as storage
import serve_diwan


class DiwanCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.file = self.root / 'نافذة with spaces.diwan.json'
        self.text = 'لَمْ أبع الوعد\nوأتركُ نافذتي للضوء\n'
        self.source = self.root / 'poem.txt'
        self.source.write_text(self.text)

    def cli(self, *args, input=None, status=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'diwan.py'), *map(str, args)],
                                input=input, stdin=subprocess.DEVNULL if input is None else None,
                                text=True, capture_output=True, timeout=12,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        self.assertNotIn('\x1b', result.stdout + result.stderr)
        return json.loads(result.stdout if status == 0 else result.stderr)

    def create(self):
        return self.cli('create', self.file, '--title', 'نافذة', '--text-file', self.source, '--json')

    def update(self, version, identity='edit-1', text='نصّ جديد\n', status=0):
        return self.cli('update', self.file, '--if-version', version, '--request-id', identity,
                        '--input', '-', '--json', input=json.dumps({'text': text}), status=status)

    def test_unicode_create_stdin_retry_and_get(self):
        first = self.create()
        self.assertEqual(first['poem']['text'], self.text)
        again = self.create()
        self.assertTrue(again['replayed'])
        self.assertEqual(first['version'], again['version'])
        self.assertEqual(self.file.stat().st_mode & 0o777, 0o600)
        result = self.update(first['version'])
        self.assertEqual(result['poem']['revision'], 2)
        replay = self.update(first['version'])
        self.assertTrue(replay['replayed'])
        self.assertEqual(replay['version'], result['version'])
        self.assertEqual(self.cli('get', self.file, '--json')['poem']['text'], 'نصّ جديد\n')
        self.update(first['version'], text='different', status=5)

    def test_stale_write_does_not_change_newer_poem(self):
        initial = self.create()
        current = self.update(initial['version'])
        failure = self.update(initial['version'], identity='stale', text='old draft', status=5)
        self.assertEqual(failure['error']['code'], 'CONFLICT')
        self.assertEqual(self.cli('get', self.file)['version'], current['version'])

    def test_two_processes_share_atomic_precondition(self):
        version = self.create()['version']
        def write(identity):
            return subprocess.run([sys.executable, str(SCRIPTS/'diwan.py'), 'update', str(self.file),
                '--if-version', version, '--request-id', identity, '--input', '-', '--json'],
                input=json.dumps({'text': identity}), text=True, capture_output=True, timeout=12,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(write, ('client-a', 'client-b')))
        self.assertEqual(sorted(r.returncode for r in results), [0, 5])
        self.assertEqual(self.cli('get', self.file)['poem']['revision'], 2)
        self.assertEqual(len(self.cli('history', self.file)['revisions']), 2)

    def test_case_aliases_share_lock_history_and_cannot_export_over_poem(self):
        first = self.create()
        alias = self.file.with_name(self.file.name.upper())
        if not alias.exists():
            self.skipTest('Filesystem is case-sensitive')
        self.assertEqual(storage.Store(alias).state, storage.Store(self.file).state)
        def write(file, identity):
            return subprocess.run([sys.executable,str(SCRIPTS/'diwan.py'),'update',str(file),'--if-version',first['version'],
                '--request-id',identity,'--input','-','--json'], input=json.dumps({'text':identity}),text=True,capture_output=True,timeout=12,
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            a = pool.submit(write,self.file,'alias-a');b = pool.submit(write,alias,'alias-b')
            results = [a.result(),b.result()]
        self.assertEqual(sorted(r.returncode for r in results),[0,5])
        self.assertEqual(len(self.cli('history',alias)['revisions']),2)
        before = self.file.read_bytes()
        error = self.cli('export',self.file,'--format','txt','--output',alias,'--overwrite',status=2)
        self.assertEqual(error['error']['code'],'INVALID_OUTPUT')
        self.assertEqual(self.file.read_bytes(),before)

    def test_unicode_aliases_reuse_document_identity(self):
        path = self.root/'أمل.diwan.json'
        first = storage.Store(path).create({'text':self.text,'title':'أمل'})
        alias = path.with_name(unicodedata.normalize('NFD',path.name))
        if not alias.exists():self.skipTest('Filesystem distinguishes Unicode normalization')
        self.assertEqual(storage.Store(path).state,storage.Store(alias).state)
        updated = storage.Store(alias).update({'text':'نص جديد'},first['version'],'unicode-edit')
        self.assertEqual(storage.Store(path).get()['version'],updated['version'])
        self.assertEqual(len(storage.Store(path).history()['revisions']),2)

    def test_unrelated_copy_cannot_share_an_existing_poem_id(self):
        first = self.create()
        copied = self.root/'copy.diwan.json';shutil.copyfile(self.file,copied)
        with self.assertRaises(storage.DiwanError) as error:
            storage.Store(copied).update({'text':'overwrite'},first['version'],'duplicate')
        self.assertEqual(error.exception.code,'DUPLICATE_ID')
        self.assertEqual(self.cli('get',self.file)['version'],first['version'])

    def test_create_replay_rejects_a_copied_document_without_writes(self):
        self.create()
        copied = self.root/'copy.diwan.json';shutil.copyfile(self.file,copied)
        before = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for extra in [(), ('--dry-run',)]:
            error = self.cli('create',copied,'--title','نافذة','--text-file',self.source,*extra,status=5)
            self.assertEqual(error['error']['code'],'DUPLICATE_ID')
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_export_cannot_replace_lock_or_another_poems_history(self):
        self.create()
        other = storage.Store(self.root/'other.diwan.json')
        other.create({'text': 'another poem'})
        for destination in [self.root/'.diwan/write.lock', next((other.state/'history').glob('*.json'))]:
            before = destination.read_bytes()
            error = self.cli('export',self.file,'--format','txt','--output',destination,'--overwrite',status=2)
            self.assertEqual(error['error']['code'],'INVALID_OUTPUT')
            self.assertEqual(destination.read_bytes(),before)

    def test_interrupted_exclusive_create_recovers_on_exact_retry(self):
        first = self.create()
        staging = self.root/'.diwan-crash-fixture'
        os.link(self.file, staging)
        error = self.cli('get',self.file,status=6)
        self.assertEqual(error['error']['code'],'INITIALIZATION_INTERRUPTED')
        self.assertEqual(error['error']['staging_files'],[str(staging)])
        self.cli('create',self.file,'--title','نافذة','--text-file',self.source,'--dry-run',status=6)
        self.assertTrue(staging.exists())
        again = self.create()
        self.assertEqual(again['version'],first['version'])
        self.assertFalse(staging.exists())
        os.link(self.file,self.root/'ordinary-link.json')
        self.assertEqual(self.cli('get',self.file,status=2)['error']['code'],'INVALID_PATH')

    def test_copied_document_cannot_access_agent_queue_or_restore_preview(self):
        first = self.create()
        copied = self.root/'copy.diwan.json';shutil.copyfile(self.file,copied)
        for args in [('pending',copied),('respond',copied,'--id','test','--input','-'),
                     ('restore',copied,'--revision',first['version'],'--if-version',first['version'],'--request-id','preview','--dry-run')]:
            result = self.cli(*args,input='{}' if args[0]=='respond' else None,status=5)
            self.assertEqual(result['error']['code'],'DUPLICATE_ID')

    def test_restore_is_new_revision_and_history_paginates(self):
        first = self.create()
        second = self.update(first['version'])
        restored = self.cli('restore', self.file, '--revision', first['version'], '--if-version', second['version'], '--request-id', 'restore-1')
        self.assertEqual(restored['poem']['text'], self.text)
        self.assertEqual(restored['poem']['revision'], 3)
        self.assertNotEqual(restored['version'], first['version'])
        page = self.cli('history', self.file, '--limit', 1)
        self.assertTrue(page['truncated'])
        next_page = self.cli('history', self.file, '--before', page['next_cursor'])
        self.assertEqual([x['revision'] for x in next_page['revisions']], [2, 1])

    def test_dry_run_and_bad_input_have_no_side_effects(self):
        self.cli('create', self.file, '--title', 'نافذة', '--text-file', self.source, '--dry-run')
        self.assertFalse(self.file.exists())
        self.assertFalse((self.root/'.diwan').exists())
        self.cli('create', self.file, '--text-file', '-', input='', status=2)
        self.cli('create', self.file, '--input', '-', input='[]', status=2)
        self.cli('get', self.file, status=4)
        self.assertFalse((self.root/'.diwan').exists())
        current = self.create()
        before = self.file.read_bytes()
        self.cli('update', self.file, '--if-version', current['version'], '--request-id', 'preview',
                 '--text-file', self.source, '--dry-run')
        self.assertEqual(before, self.file.read_bytes())

    def test_help_and_discovery_are_side_effect_free(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob('*'))
        for name in diwan.EXAMPLES:
            result = subprocess.run([sys.executable, str(SCRIPTS/'diwan.py'), name, '--help'],
                cwd=self.root, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=5,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Examples:', result.stdout)
        context = self.cli('agent-context', '--json')
        self.assertEqual(set(context['commands']), set(diwan.EXAMPLES))
        self.assertEqual(before, sorted(p.relative_to(self.root) for p in self.root.rglob('*')))

    def test_documented_command_examples_execute_on_disposable_fixtures(self):
        for name, example in diwan.EXAMPLES.items():
            with self.subTest(command=name):
                folder = self.root/name;folder.mkdir()
                file = folder/'poem.diwan.json'
                (folder/'poem.txt').write_text('قَرِيبٌ صَدِيقِي بَعِيدٌ مَكَانِي')
                (folder/'revised.txt').write_text('قَرِيبٌ صَدِيقِي بَعِيدٌ مَكَانِي\n')
                (folder/'answer.json').write_text('{"answer":"تمّ"}')
                version = old = None
                if name != 'create' and name != 'agent-context':
                    store = storage.Store(file)
                    initial = store.create({'text':'قَرِيبٌ صَدِيقِي بَعِيدٌ مَكَانِي','title':'نافذة'})
                    version = old = initial['version']
                    if name == 'restore':
                        version = store.update({'text':'نص آخر'},version,'fixture')['version']
                identity = '0'*32
                if name == 'respond':
                    queue = serve_diwan.queue_dirs(storage.Store(file).state/'agent')
                    serve_diwan.write_json(queue/'requests'/f'{identity}.json',{'id':identity,'input':'fixture'})
                replacements = {'$VERSION':version,'$OLD_VERSION':old,'$REQUEST_ID':identity}
                args = [replacements.get(token,token) for token in shlex.split(example)]
                command = [sys.executable,str(SCRIPTS/'diwan.py'),*args]
                env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
                if name == 'serve':
                    process = subprocess.Popen(command,cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
                    try:
                        self.assertTrue(select.select([process.stdout],[],[],6)[0])
                        receipt = json.loads(process.stdout.readline());self.assertIn('url',receipt)
                        self.cli('stop',file)
                        self.assertEqual(process.wait(timeout=6),0)
                    finally:
                        if process.poll() is None:process.terminate();process.wait(timeout=6)
                        process.stdout.close();process.stderr.close()
                else:
                    result = subprocess.run(command,cwd=folder,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=10,env=env)
                    self.assertEqual(result.returncode,0,result.stderr)
                    json.loads(result.stdout)
                    if name == 'open':self.cli('stop',file)

    def test_atomic_failure_keeps_original_and_retry_recovers_commit(self):
        store = storage.Store(self.file)
        first = store.create({'text': self.text, 'title': 'نافذة'})
        actual_write = storage.atomic_write
        def fail_document(path, raw, **kwargs):
            if Path(path) == self.file:
                raise OSError('injected before rename')
            return actual_write(path, raw, **kwargs)
        with patch.object(storage, 'atomic_write', side_effect=fail_document):
            with self.assertRaises(OSError): store.update({'text': 'revision'}, first['version'], 'before-rename')
        self.assertEqual(store.get()['version'], first['version'])
        second = store.update({'text': 'revision'}, first['version'], 'before-rename')
        actual_finish = store._finish
        with patch.object(store, '_finish', side_effect=OSError('injected after rename')):
            with self.assertRaises(OSError): store.update({'text': 'committed'}, second['version'], 'after-rename')
        self.assertEqual(store.get()['poem']['text'], 'committed')
        recovered = store.update({'text': 'committed'}, second['version'], 'after-rename')
        self.assertTrue(recovered['replayed'])
        self.assertEqual(recovered['poem']['revision'], 3)
        self.assertEqual(len(store.history()['revisions']), 3)

    def test_export_preserves_exact_text_and_rejects_overwrite(self):
        self.create()
        output = self.root/'export.md'
        receipt = self.cli('export', self.file, '--format', 'md', '--output', output)
        self.assertEqual(output.read_text(), self.text)
        self.assertEqual(receipt['bytes'], len(self.text.encode()))
        self.assertTrue(self.cli('export', self.file, '--format', 'md', '--output', output)['reused'])
        output.write_text('keep me')
        self.cli('export', self.file, '--format', 'md', '--output', output, status=5)
        self.assertEqual(output.read_text(), 'keep me')

    def test_other_writer_identical_text_does_not_complete_an_aborted_save(self):
        store = storage.Store(self.file)
        first = store.create({'text': self.text, 'title': 'نافذة'})
        original = storage.atomic_write
        def interrupt(path, raw, **kwargs):
            if Path(path) == store.path:
                raise OSError('interrupted before document commit')
            return original(path, raw, **kwargs)
        with patch.object(storage, 'atomic_write', side_effect=interrupt):
            with self.assertRaises(OSError):store.update({'text': 'same intended text'}, first['version'], 'writer-a')
        saved = store.update({'text': 'same intended text'}, first['version'], 'writer-b')
        with self.assertRaises(storage.DiwanError) as error:
            store.update({'text': 'same intended text'}, first['version'], 'writer-a')
        self.assertEqual(error.exception.code, 'CONFLICT')
        self.assertEqual(store.get()['version'], saved['version'])
        self.assertEqual(store.get()['poem']['last_save_id'], 'writer-b')

    def test_http_and_cli_use_the_same_document_and_conflicts(self):
        initial = self.create()
        store = storage.Store(self.file)
        server, url = serve_diwan.make_server(self.root/'agent', port=0, document=store)
        worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        first = diwan.request(url, '/document')
        current = self.update(initial['version'])
        parsed = __import__('urllib.parse', fromlist=['urlsplit']).urlsplit(url)
        address = url.removesuffix('/diwan.html') + '/document'
        body = storage.encode({'if_version': first['version'], 'request_id': 'browser-stale', 'patch': {'text': 'browser draft'}})
        request = urllib.request.Request(address, data=body, headers={'Content-Type':'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 409)
        error.exception.close()
        self.assertEqual(store.get()['version'], current['version'])
        changed = diwan.request(url, '/document', {'if_version': current['version'], 'request_id': 'browser-fresh', 'patch': {'text':'من المتصفح'}})
        self.assertEqual(self.cli('get', self.file)['poem']['text'], 'من المتصفح')
        self.assertEqual(changed['poem']['revision'], 3)
        request = urllib.request.Request(address, headers={'Origin':'https://example.com'})
        with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

    def test_response_failures_use_actionable_exit_codes_without_writing(self):
        initial = self.create()
        queue = serve_diwan.queue_dirs(storage.Store(self.file).state/'agent')
        cases = [('unknown',4,'NOT_FOUND'),('expired',4,'NOT_FOUND'),
                 ('answered',5,'CONFLICT'),('cancelled',5,'CONFLICT'),
                 ('invalid-value',2,'INVALID_RESPONSE'),('invalid-id',2,'INVALID_REQUEST_ID')]
        for index,(kind,status,code) in enumerate(cases):
            with self.subTest(kind=kind):
                identity = f'{index:032x}'
                request = queue/'requests'/(identity+'.json')
                response = queue/'responses'/(identity+'.json')
                if kind not in ('unknown','invalid-id'):
                    serve_diwan.write_json(request,{'id':identity,'input':'test'})
                if kind == 'expired':
                    expired = time.time()-serve_diwan.REQUEST_TTL-5
                    os.utime(request,(expired,expired))
                if kind == 'answered':serve_diwan.write_json(response,{'answer':'keep existing'})
                if kind == 'cancelled':serve_diwan.write_json(queue/'cancelled'/(identity+'.json'),{'cancelled':True})
                if kind == 'invalid-id':identity = '../invalid'
                error = self.cli('respond',self.file,'--id',identity,'--input','-',
                                 input='42' if kind=='invalid-value' else '{}',status=status)
                self.assertEqual(error['error']['code'],code)
                self.assertNotIn('inspect get',error['error']['message'])
                if kind == 'answered':self.assertEqual(json.loads(response.read_text()),{'answer':'keep existing'})
                else:self.assertFalse(response.exists())
        self.assertEqual(self.cli('get',self.file)['version'],initial['version'])

    def test_open_reuses_owned_session_and_stop_does_not_modify_poem(self):
        before = self.create()['version']
        receipt = self.cli('open', self.file, '--no-browser')
        self.addCleanup(lambda: self.cli('stop', self.file))
        self.assertFalse(receipt['rendered'])
        self.assertFalse(receipt['browser_open_requested'])
        again = self.cli('open', self.file, '--no-browser')
        self.assertTrue(again['reused'])
        self.assertEqual(receipt['url'], again['url'])
        copied = self.root/'copy.diwan.json';shutil.copyfile(self.file,copied)
        for args in [('open',copied,'--no-browser'),('stop',copied)]:
            self.assertEqual(self.cli(*args,status=5)['error']['code'],'DUPLICATE_ID')
        self.assertEqual(diwan.request(receipt['url'],'/status')['id'],again['id'])
        self.assertTrue(self.cli('stop', self.file)['stopped'])
        self.assertEqual(self.cli('get', self.file)['version'], before)

    def test_open_after_rename_shuts_down_the_previous_owned_server(self):
        before = self.create()['version']
        receipt = self.cli('open',self.file,'--no-browser')
        renamed = self.root/'renamed.diwan.json'
        def cleanup():
            try:diwan.request(receipt['url'],'/shutdown',{})
            except (OSError,storage.DiwanError):pass
        self.addCleanup(cleanup)
        self.file.rename(renamed)
        replacement = self.cli('open',renamed,'--no-browser')
        self.addCleanup(lambda:self.cli('stop',renamed))
        self.assertNotEqual(receipt['url'],replacement['url'])
        deadline = time.monotonic()+3
        while True:
            try:diwan.request(receipt['url'],'/diwan.html')
            except OSError:break
            except (storage.DiwanError,ValueError):pass
            if time.monotonic()>=deadline:self.fail('Old server still owns its loopback port after rename/open')
            time.sleep(0.02)
        self.assertEqual(self.cli('get',renamed)['version'],before)
        self.assertTrue(self.cli('stop',renamed)['stopped'])


if __name__ == '__main__':
    unittest.main()

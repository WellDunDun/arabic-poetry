"""Installed-package detection and real supervised HTTP handoffs, without models."""
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import diwan
import diwan_updates as updates
import serve_diwan
from diwan_store import Store


class RuntimeUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = self.root / 'claude'
        self.cache = self.config / 'plugins/cache/arabic-poetry-plugins/arabic-poetry'
        self.old = self.copy_package('0.3.1')
        self.new = self.copy_package('0.3.2')
        self.config.joinpath('settings.json').write_text(json.dumps({'enabledPlugins': {'arabic-poetry@arabic-poetry-plugins': True}}))
        self.install(self.old)
        self.folder = self.root / 'poems'
        self.folder.mkdir()
        self.file = self.folder / 'poem.diwan.json'
        self.store = Store(self.file)
        self.store.create({'text': '  سَلامٌ\n\n\nعلى نافذتي\n', 'title': 'نافذة'})
        self.before = self.store.get()

    def copy_package(self, version):
        target = self.cache / version
        shutil.copytree(updates.ROOT / 'skills/arabic-poetry', target / 'skills/arabic-poetry',
                        ignore=shutil.ignore_patterns('__pycache__', 'tests'))
        target.joinpath('.claude-plugin').mkdir()
        target.joinpath('.claude-plugin/plugin.json').write_text(json.dumps({'name': 'arabic-poetry', 'version': version}))
        return target

    def install(self, target):
        self.config.joinpath('plugins/installed_plugins.json').write_text(json.dumps({'version': 2, 'plugins': {
            'arabic-poetry@arabic-poetry-plugins': [{'scope': 'user', 'version': target.name, 'installPath': str(target)}]}}))

    def launch(self, agent='manual'):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        env.pop(updates.TOKEN_ENV, None)
        env.pop(updates.BLOCKED_ENV, None)
        process = subprocess.Popen([sys.executable, str(self.old / updates.SCRIPTS / 'diwan.py'),
                                    'serve', str(self.file), '--port', '0', '--agent', agent, '--json'],
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
        def cleanup():
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
            process.stdout.close()
        self.addCleanup(cleanup)
        self.assertTrue(select.select([process.stdout], [], [], 8)[0])
        receipt = json.loads(process.stdout.readline())
        return process, receipt

    def wait_version(self, url, version, recovered=False):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                state = diwan.request(url, '/runtime')
                if state['version'] == version and state['recovered'] == recovered:
                    return state
            except (OSError, ValueError, diwan.DiwanError):
                pass
            time.sleep(.04)
        self.fail('The supervised runtime did not reconnect')

    def test_detection_requires_an_installed_enabled_compatible_upgrade(self):
        monitor = updates.InstalledRuntime(self.old)
        self.assertIsNone(monitor.candidate(force=True), 'a cached newer directory is not an install')
        self.install(self.new)
        self.assertEqual(monitor.candidate(force=True), {'version': '0.3.2', 'root': str(self.new)})
        self.new.joinpath('skills/arabic-poetry/assets/workbench/runtime.json').write_text('{"protocol":1}')
        self.assertIsNone(monitor.candidate(force=True))
        self.new.joinpath('skills/arabic-poetry/assets/workbench/runtime.json').write_text(json.dumps({'protocol':updates.PROTOCOL}))
        self.config.joinpath('settings.json').write_text('{"enabledPlugins":{"arabic-poetry@arabic-poetry-plugins":false}}')
        self.assertIsNone(monitor.candidate(force=True))

    def test_foreign_install_paths_and_invalid_inventory_do_not_run(self):
        monitor = updates.InstalledRuntime(self.old)
        self.install(self.root / 'unrelated/0.3.2')
        self.assertIsNone(monitor.candidate(force=True))
        self.config.joinpath('plugins/installed_plugins.json').write_text('incomplete download')
        self.assertIsNone(monitor.candidate(force=True))
        self.assertIsNone(updates.InstalledRuntime(updates.ROOT).candidate(force=True), 'a developer checkout has no newer install')
        self.assertIsNone(updates.InstalledRuntime(self.root / 'standalone').candidate(force=True))

    def test_standalone_skill_still_opens_without_plugin_metadata(self):
        skill = self.root / 'standalone-skill'
        shutil.copytree(updates.ROOT / 'skills/arabic-poetry', skill, ignore=shutil.ignore_patterns('__pycache__', 'tests'))
        command = [sys.executable, str(skill / 'scripts/diwan.py')]
        result = subprocess.run([*command, 'open', str(self.file), '--agent', 'manual', '--no-browser', '--json'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.addCleanup(lambda: diwan.request(receipt['url'], '/shutdown', {}))
        self.assertIsNone(diwan.request(receipt['url'], '/runtime')['available'])
        self.assertEqual(diwan.request(receipt['url'], '/document'), self.before)

    def test_codex_inventory_selects_only_the_enabled_installed_version(self):
        self.config.joinpath('plugins/installed_plugins.json').unlink()
        self.config.joinpath('config.toml').write_text('')
        row = {'pluginId': 'arabic-poetry@arabic-poetry-plugins', 'version': '0.3.2', 'installed': True, 'enabled': True}
        result = subprocess.CompletedProcess([], 0, json.dumps({'installed': [row]}), '')
        with patch.object(updates.shutil, 'which', return_value='/fixture/codex'), patch.object(updates.subprocess, 'run', return_value=result) as run:
            self.assertEqual(updates.InstalledRuntime(self.old).candidate(force=True)['root'], str(self.new))
            self.assertEqual(run.call_args.kwargs['env']['CODEX_HOME'], str(self.config))
            row['enabled'] = False
            result.stdout = json.dumps({'installed': [row]})
            self.assertIsNone(updates.InstalledRuntime(self.old).candidate(force=True))

    def test_real_handoff_keeps_address_identity_poem_history_and_agent(self):
        process, first = self.launch()
        self.assertEqual(diwan.request(first['url'], '/runtime')['version'], '0.3.1')
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.wait_version(first['url'], '0.3.2')
        self.assertEqual(self.store.get(), self.before)
        self.assertEqual(len(self.store.history()['revisions']), 1)
        session = json.loads((self.store.state / 'session.json').read_text())
        self.assertEqual(session['url'], first['url'])
        self.assertEqual(session['id'], first['id'])
        self.assertNotEqual(session['pid'], first['pid'])
        self.assertEqual(session['agent'], 'manual')
        self.assertTrue(session['manual'])
        self.assertIsNone(process.poll(), 'the supervisor stays available for subsequent upgrades')
        # An already-open stale browser must still conflict after a runtime handoff.
        changed = self.store.update({'text': 'saved by agent'}, self.before['version'], 'agent-edit')
        with self.assertRaises(diwan.DiwanError):
            diwan.request(first['url'], '/document', {'patch': {'text': 'unsaved browser draft'},
                           'if_version': self.before['version'], 'request_id': 'browser-edit'})
        self.assertEqual(self.store.get()['version'], changed['version'])

    def test_failed_successor_rolls_back_and_does_not_retry_in_a_loop(self):
        process, first = self.launch()
        self.new.joinpath(updates.SCRIPTS / 'diwan.py').write_text('raise RuntimeError("broken fixture")\n')
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        state = self.wait_version(first['url'], '0.3.1', recovered=True)
        self.assertIsNone(state['available'])
        self.assertFalse(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.assertEqual(self.store.get(), self.before)
        self.assertIsNone(process.poll())
        newer = self.copy_package('0.3.3')
        self.install(newer)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        state = self.wait_version(first['url'], '0.3.3')
        self.assertFalse(state['recovered'], 'a later successful update must clear the rollback notice')

    def test_successor_crash_after_acknowledgement_rolls_back(self):
        process, first = self.launch()
        receipt = dict(first, pid=1)
        self.new.joinpath(updates.SCRIPTS / 'diwan.py').write_text(
            'import json\nprint(' + repr(json.dumps(receipt)) + ', flush=True)\nraise SystemExit(23)\n')
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.wait_version(first['url'], '0.3.1', recovered=True)
        self.assertEqual(self.store.get(), self.before)
        self.assertIsNone(process.poll())

    def test_termination_during_startup_is_a_clean_stop(self):
        marker = self.root / 'worker-starting'
        script = self.old / updates.SCRIPTS / 'diwan.py'
        text = script.read_text()
        insert = 'import sys,time\nfrom pathlib import Path\nif "--runtime-worker" in sys.argv:\n    Path(' + repr(str(marker)) + ').write_text("starting")\n    time.sleep(30)\n'
        script.write_text(insert + text)
        process = subprocess.Popen([sys.executable, str(script), 'serve', str(self.file), '--agent', 'manual', '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertTrue(marker.exists())
            process.terminate()
            self.assertEqual(process.wait(timeout=8), 0)
            self.assertEqual(self.store.get(), self.before)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            process.stdout.close()

    def test_registry_change_between_approval_and_handoff_cannot_retry_failed_root(self):
        flag = self.root / 'flip-on-restart'
        index = self.config / 'plugins/installed_plugins.json'
        self.install(self.new)
        failed_index = index.read_text()
        self.install(self.old)
        script = self.old / updates.SCRIPTS / 'diwan.py'
        injected = '        from pathlib import Path\n        if Path(' + repr(str(flag)) + ').exists():\n            Path(' + repr(str(index)) + ').write_text(' + repr(failed_index) + ')\n            Path(' + repr(str(flag)) + ').unlink()\n'
        script.write_text(script.read_text().replace('        raise SystemExit(diwan_updates.RESTART)', injected + '        raise SystemExit(diwan_updates.RESTART)'))
        attempts = self.root / 'failed-attempts'
        self.new.joinpath(updates.SCRIPTS / 'diwan.py').write_text('from pathlib import Path\nwith Path(' + repr(str(attempts)) + ').open("a") as f:f.write("attempt\\n")\nraise SystemExit(23)\n')
        process, first = self.launch()
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.wait_version(first['url'], '0.3.1', recovered=True)
        newer = self.copy_package('0.3.3')
        self.install(newer)
        flag.write_text('flip')
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        deadline = time.monotonic() + 5
        while flag.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertFalse(flag.exists())
        self.wait_version(first['url'], '0.3.1', recovered=True)
        self.assertEqual(attempts.read_text(), 'attempt\n')
        self.assertEqual(self.store.get(), self.before)
        self.assertIsNone(process.poll())

    def test_each_failed_root_stays_blocked_after_another_failure(self):
        attempts = self.root / 'attempts'
        third = self.copy_package('0.3.3')
        for root in (self.new, third):
            root.joinpath(updates.SCRIPTS / 'diwan.py').write_text('from pathlib import Path\nwith Path(' + repr(str(attempts)) + ').open("a") as f:f.write(' + repr(root.name + '\n') + ')\nraise SystemExit(23)\n')
        process, first = self.launch()
        for root in (self.new, third):
            self.install(root)
            self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
            self.wait_version(first['url'], '0.3.1', recovered=True)
        self.install(self.new)
        self.assertFalse(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.assertEqual(attempts.read_text(), '0.3.2\n0.3.3\n')
        working = self.copy_package('0.3.4')
        self.install(working)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.wait_version(first['url'], '0.3.4')
        self.assertEqual(self.store.get(), self.before)
        self.assertIsNone(process.poll())

    def test_update_waits_for_document_writes_and_rejects_late_saves(self):
        server, url = serve_diwan.make_server(self.root / 'agent', document=self.store, agent='manual', port=0)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        entered, release = threading.Event(), threading.Event()
        update = self.store.update
        results = []
        def blocked_update(*args):
            entered.set()
            if not release.wait(5):
                raise RuntimeError('test writer was not released')
            return update(*args)
        def save():
            results.append(diwan.request(url, '/document', {'patch': {'text': 'saved during version check'},
                'if_version': self.before['version'], 'request_id': 'overlapping-save'}))
        with patch.object(self.store, 'update', side_effect=blocked_update), patch.object(updates.InstalledRuntime, 'candidate', return_value={'version':'0.3.2','root':str(self.new)}), patch.object(server, 'shutdown'):
            writer = threading.Thread(target=save)
            writer.start()
            try:
                self.assertTrue(entered.wait(3))
                self.assertFalse(diwan.request(url, '/runtime', {})['restarting'])
            finally:
                release.set()
                writer.join(timeout=5)
            self.assertEqual(len(results), 1)
            current = self.store.get()
            self.assertEqual(current['poem']['text'], 'saved during version check')
            self.assertTrue(diwan.request(url, '/runtime', {})['restarting'])
            with self.assertRaises(diwan.DiwanError):
                diwan.request(url, '/document', {'patch': {'text': 'late draft'},
                    'if_version': current['version'], 'request_id': 'too-late'})
            self.assertEqual(self.store.get(), current)

    def test_partial_startup_acknowledgement_obeys_its_deadline(self):
        child = subprocess.Popen([sys.executable, '-c', 'import sys,time;sys.stdout.write("{");sys.stdout.flush();time.sleep(10)'], stdout=subprocess.PIPE)
        try:
            start = time.monotonic()
            self.assertEqual(updates.acknowledgement(child, timeout=.2), b'')
            self.assertLess(time.monotonic() - start, 1)
        finally:
            child.terminate()
            child.wait(timeout=3)
            child.stdout.close()

    def test_incomplete_successor_page_rolls_back_before_serving_it(self):
        process, first = self.launch()
        self.new.joinpath('skills/arabic-poetry/assets/workbench/diwan.html').write_text('incomplete download')
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
        self.wait_version(first['url'], '0.3.1', recovered=True)
        self.assertEqual(self.store.get(), self.before)
        self.assertIsNone(process.poll())

    def test_pending_requests_and_replaced_documents_prevent_restart(self):
        process, first = self.launch()
        self.install(self.new)
        post = urllib.request.Request(first['url'].removesuffix('/diwan.html') + '/requests',
            data=b'{"input":"manual request"}', headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(post) as response:
            request = json.load(response)
        self.assertFalse(diwan.request(first['url'], '/runtime', {})['restarting'])
        diwan.request(first['url'], '/cancel/' + request['id'], {})
        renamed = self.folder / 'renamed.diwan.json'
        self.file.rename(renamed)
        Store(self.file).create({'text': 'another poem', 'title': 'آخر'})
        with self.assertRaises(diwan.DiwanError):
            diwan.request(first['url'], '/runtime', {})
        self.assertIsNone(process.poll())

    def test_handoff_preserves_each_selected_installed_client_without_a_model_call(self):
        binaries = self.root / 'bin'
        binaries.mkdir()
        for name in ('claude', 'codex'):
            client = binaries / name
            client.write_text('#!' + sys.executable + '\nraise SystemExit("No model call expected")\n')
            client.chmod(0o755)
        with patch.dict(os.environ, {'PATH': str(binaries) + os.pathsep + os.environ['PATH']}):
            for agent in ('claude', 'codex'):
                with self.subTest(agent=agent):
                    self.install(self.old)
                    process, first = self.launch(agent)
                    self.install(self.new)
                    self.assertTrue(diwan.request(first['url'], '/runtime', {})['restarting'])
                    self.wait_version(first['url'], '0.3.2')
                    session = json.loads((self.store.state / 'session.json').read_text())
                    self.assertEqual(session['agent'], agent)
                    self.assertFalse(session['manual'])
                    diwan.request(first['url'], '/shutdown', {})
                    self.assertEqual(process.wait(timeout=8), 0)
        self.assertEqual(self.store.get(), self.before)

    def test_explicit_http_shutdown_cancels_an_accepted_update(self):
        server,url = serve_diwan.make_server(self.root/'agent',document=self.store,agent='manual')
        thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        with patch.object(updates.InstalledRuntime,'candidate',return_value={'version':'0.3.2','root':str(self.new)}), patch.object(server,'shutdown'):
            self.assertTrue(diwan.request(url,'/runtime',{})['restarting'])
            self.assertTrue(diwan.request(url,'/shutdown',{})['stopped'])
            self.assertFalse(server.diwan_restart)
            self.assertFalse(diwan.request(url,'/runtime',{})['restarting'])

    def test_stop_cancels_an_update_during_the_socket_gap(self):
        marker = self.root/'successor-started'
        release = self.root/'release-successor'
        script = self.new/updates.SCRIPTS/'diwan.py'
        original = script.read_text()
        script.write_text('import time\nfrom pathlib import Path\n'
            + f'Path({str(marker)!r}).touch()\n'
            + f'while not Path({str(release)!r}).exists(): time.sleep(.01)\n' + original)
        process,first = self.launch()
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'],'/runtime',{})['restarting'])
        deadline = time.monotonic()+5
        while not marker.exists() and time.monotonic()<deadline: time.sleep(.01)
        self.assertTrue(marker.exists(),'Successor did not reach the controlled socket gap')
        with self.assertRaises(ConnectionRefusedError):diwan.request(first['url'],'/status')
        result = subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),'stop',str(self.file),'--json'],
                                capture_output=True,text=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['stopped'])
        self.assertEqual(process.wait(timeout=3),0)
        release.touch()
        with self.assertRaises(ConnectionRefusedError):diwan.request(first['url'],'/status')
        self.assertEqual(self.store.get(),self.before)

    def test_handoff_keeps_auto_mode_without_an_installed_client(self):
        bins = self.root/'no-clients'; bins.mkdir()
        with patch.dict(os.environ,{'PATH':str(bins)}):
            process,first = self.launch('auto')
            self.assertFalse(first['manual'])
            self.install(self.new)
            self.assertTrue(diwan.request(first['url'],'/runtime',{})['restarting'])
            self.wait_version(first['url'],'0.3.2')
            receipt = json.loads((self.store.state/'session.json').read_text())
            self.assertEqual(receipt.get('mode'),'auto')
            self.assertFalse(receipt['manual'])
            diwan.request(first['url'],'/shutdown',{})
            self.assertEqual(process.wait(timeout=8),0)

    def test_unconfirmed_stop_retains_the_receipt_and_rejects_foreign_control(self):
        identity = 'a'*32
        control = updates.RuntimeControl(self.store,identity)
        control.publish('running')
        lease = control.lease()
        updates.fcntl.flock(lease,updates.fcntl.LOCK_EX|updates.fcntl.LOCK_NB)
        self.addCleanup(lease.close)
        receipt = self.store.state/'session.json'
        receipt.write_text(json.dumps({'runtime_id':identity,'url':'http://127.0.0.1:1/fixture/diwan.html'}))
        before = receipt.read_bytes()
        with self.assertRaises(diwan.DiwanError) as error:updates.stop_supervised(self.store,.05)
        self.assertEqual(error.exception.code,'STOP_UNKNOWN')
        self.assertEqual(receipt.read_bytes(),before)
        control.request.unlink()
        value = json.loads(control.path.read_text()); value['id'] = 'b'*32
        control.path.write_text(json.dumps(value))
        with self.assertRaises(diwan.DiwanError):updates.stop_supervised(self.store,.05)
        self.assertFalse(control.request.exists())
        self.assertEqual(receipt.read_bytes(),before)

    def test_a_new_session_ignores_an_older_sessions_stop_request(self):
        process,first = self.launch()
        self.assertTrue(updates.stop_supervised(self.store,5))
        self.assertEqual(process.wait(timeout=3),0)
        other,second = self.launch()
        self.assertNotEqual(first['runtime_id'],second['runtime_id'])
        self.assertEqual(diwan.request(second['url'],'/status')['id'],first['id'])
        self.assertIsNone(other.poll())
        self.assertTrue(updates.stop_supervised(self.store,5))
        self.assertEqual(other.wait(timeout=3),0)
        self.assertEqual(self.store.get(),self.before)

    def test_stop_recovers_a_crashed_supervisor_and_its_orphan_worker(self):
        process,first = self.launch()
        def cleanup():
            try:diwan.request(first['url'],'/shutdown',{})
            except (OSError,diwan.DiwanError):pass
        self.addCleanup(cleanup)
        process.kill(); process.wait(timeout=3)
        self.assertEqual(diwan.request(first['url'],'/status')['id'],first['id'])
        result = subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),'stop',str(self.file),'--json'],
                                capture_output=True,text=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['stopped'])
        repeated = subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),'stop',str(self.file),'--json'],
                                  capture_output=True,text=True,timeout=8)
        self.assertEqual(repeated.returncode,0,repeated.stderr)
        self.assertTrue(json.loads(repeated.stdout)['already_stopped'])

    def test_http_stop_survives_an_unreadable_control_record(self):
        process,first = self.launch()
        control = updates.RuntimeControl(self.store,first['runtime_id'])
        control.path.write_text('{incomplete')
        self.assertTrue(diwan.request(first['url'],'/shutdown',{})['stopped'])
        self.assertEqual(process.wait(timeout=3),0)
        self.assertEqual(self.store.get(),self.before)

    def test_open_and_serve_do_not_create_a_second_runtime_in_the_socket_gap(self):
        marker = self.root/'gap-started'; release = self.root/'gap-release'
        script = self.new/updates.SCRIPTS/'diwan.py'
        script.write_text('import time\nfrom pathlib import Path\n'
            + f'Path({str(marker)!r}).touch()\n'
            + f'while not Path({str(release)!r}).exists(): time.sleep(.01)\n' + script.read_text())
        process,first = self.launch()
        self.install(self.new)
        self.assertTrue(diwan.request(first['url'],'/runtime',{})['restarting'])
        deadline = time.monotonic()+5
        while not marker.exists() and time.monotonic()<deadline:time.sleep(.01)
        self.assertTrue(marker.exists())
        receipt = self.store.state/'session.json'; before = receipt.read_bytes()
        for command in ('open','serve'):
            args = [sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),command,str(self.file),'--json']
            if command=='open':args.append('--no-browser')
            result = subprocess.run(args,capture_output=True,text=True,timeout=5)
            if result.returncode==0:
                other = json.loads(result.stdout)
                diwan.request(other['url'],'/shutdown',{})
            self.assertEqual(result.returncode,6,result.stdout+result.stderr)
            self.assertEqual(receipt.read_bytes(),before)
        release.touch()
        self.wait_version(first['url'],'0.3.2')
        diwan.request(first['url'],'/shutdown',{})
        self.assertEqual(process.wait(timeout=3),0)

    def test_stop_waits_for_the_supervisors_bounded_forced_teardown(self):
        script = self.old/updates.SCRIPTS/'diwan.py'
        script.write_text('import signal\n'+script.read_text().replace('serve_diwan.run_server(server)',
            'signal.signal(signal.SIGTERM,signal.SIG_IGN)\n    server.serve_forever()'))
        process,first = self.launch()
        result = subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),'stop',str(self.file),'--json'],
                                capture_output=True,text=True,timeout=13)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['stopped'])
        self.assertEqual(process.wait(timeout=3),0)
        with self.assertRaises(ConnectionRefusedError):diwan.request(first['url'],'/status')
        self.assertEqual(self.store.get(),self.before)

    def test_control_cleanup_preserves_current_live_and_uncertain_generations(self):
        old = updates.RuntimeControl(self.store,'1'*32); old.publish('stopped')
        current = updates.RuntimeControl(self.store,'2'*32); current.publish('stopped')
        uncertain = updates.RuntimeControl(self.store,'3'*32); uncertain.publish('running')
        live = updates.RuntimeControl(self.store,'4'*32); live.publish('stopped')
        lease = live.lease(); updates.fcntl.flock(lease,updates.fcntl.LOCK_EX|updates.fcntl.LOCK_NB)
        self.addCleanup(lease.close)
        (self.store.state/'session.json').write_text(json.dumps({'runtime_id':current.identity}))
        updates.prune_stopped_controls(self.store)
        self.assertFalse(old.path.exists())
        self.assertTrue(current.path.exists())
        self.assertTrue(uncertain.path.exists())
        self.assertTrue(live.path.exists())

    def test_explicit_replacement_waits_for_supervisor_shutdown_acknowledgement(self):
        script = self.old/updates.SCRIPTS/'diwan_updates.py'
        script.write_text(script.read_text().replace("            control.publish('stopped')",
            "            time.sleep(1)\n            control.publish('stopped')"))
        process,first = self.launch('manual')
        bins = self.root/'empty-path'; bins.mkdir()
        result = subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),'open',str(self.file),
            '--no-browser','--agent','auto','--json'],capture_output=True,text=True,timeout=10,
            env=dict(os.environ,PATH=str(bins)))
        if result.returncode==0:
            second = json.loads(result.stdout)
            self.addCleanup(lambda:subprocess.run([sys.executable,str(self.old/updates.SCRIPTS/'diwan.py'),
                'stop',str(self.file),'--json'],capture_output=True,timeout=12))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(second['mode'],'auto')
        self.assertFalse(second['manual'])
        self.assertEqual(diwan.urlsplit(second['url']).port,diwan.urlsplit(first['url']).port)
        self.assertEqual(process.wait(timeout=3),0)
        self.assertEqual(self.store.get(),self.before)

    def test_serve_replacement_can_outlast_the_old_workers_term_grace(self):
        script = self.old/updates.SCRIPTS/'diwan.py'
        script.write_text('import signal\n'+script.read_text().replace('serve_diwan.run_server(server)',
            "if selected_mode == 'manual':\n        signal.signal(signal.SIGTERM,signal.SIG_IGN)\n        server.serve_forever()\n    else:\n        serve_diwan.run_server(server)"))
        supervisor = self.old/updates.SCRIPTS/'diwan_updates.py'
        supervisor.write_text(supervisor.read_text().replace("            control.publish('stopped')",
            "            time.sleep(1)\n            control.publish('stopped')"))
        process,first = self.launch('manual')
        bins = self.root/'replacement-bin';bins.mkdir()
        child = subprocess.Popen([sys.executable,str(script),'serve',str(self.file),'--agent','auto','--json'],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,PATH=str(bins)))
        def cleanup():
            if child.poll() is None:child.terminate();child.wait(timeout=10)
            child.stdout.close();child.stderr.close()
        self.addCleanup(cleanup)
        self.assertTrue(select.select([child.stdout],[],[],14)[0])
        line = child.stdout.readline()
        self.assertTrue(line,'Replacement failed before old teardown could complete')
        second = json.loads(line)
        self.assertEqual(second['mode'],'auto')
        self.assertEqual(diwan.urlsplit(second['url']).port,diwan.urlsplit(first['url']).port)
        self.assertEqual(process.wait(timeout=3),0)
        diwan.request(second['url'],'/shutdown',{})
        self.assertEqual(child.wait(timeout=4),0)
        self.assertEqual(self.store.get(),self.before)


if __name__ == '__main__':
    unittest.main()

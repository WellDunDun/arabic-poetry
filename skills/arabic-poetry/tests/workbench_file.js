// Exercise production transport with stale snapshots and lost acknowledgements.
const assert = require('node:assert/strict');
const fs = require('node:fs'), vm = require('node:vm'), path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/workbench/file.js'), 'utf8');

function harness() {
  let state = { version: 'v1', poem: { id: 'one', title: 'نافذة', text: 'original', revision: 1,
    choices: [], suggestions: {}, status: 'review', mode: 'auto', meter: '' } };
  const operations = new Map(), callbacks = [], posted = [], messages = [];
  let drop = false, writes = 0, poll;
  function node() { return { textContent: '', appendChild() {}, prepend() {}, replaceChildren() {} }; }
  const context = { window: { DiwanFile: { base: '/session' } }, crypto: require('node:crypto').webcrypto,
    setInterval(fn) { poll = fn; return 1; }, clearInterval() {},
    document: { createElement: node, querySelector: node, body: node() },
    async fetch(url, options) {
      if (!options.method) return { ok: true, async json() { return structuredClone(state); } };
      const request = JSON.parse(options.body); posted.push(request);
      if (operations.has(request.request_id)) {
        const applied = operations.get(request.request_id);
        return { ok: true, async json() { return { ...structuredClone(state), replayed: true, applied_version: applied }; } };
      }
      if (request.if_version !== state.version) return { ok: false, async json() { return { error: { code: 'CONFLICT', message: 'stale' } }; } };
      writes++;
      state = { version: 'v' + (state.poem.revision + 1), poem: { ...state.poem, ...request.patch, revision: state.poem.revision + 1 } };
      operations.set(request.request_id, state.version);
      if (drop) { drop = false; throw new Error('lost acknowledgement'); }
      return { ok: true, async json() { return { ...structuredClone(state), applied_version: state.version }; } };
    }
  };
  vm.createContext(context); vm.runInContext(source, context);
  const host = context.window.DiwanFileConnection({ downloads: { save(value) { messages.push(value); } } });
  host.db.collection('poems').onSnapshot(s => callbacks.push(s.docs[0].data()));
  return { host, callbacks, posted, get state() { return state; }, get writes() { return writes; },
    async tick() { await new Promise(resolve => setImmediate(resolve)); await poll(); },
    external(text) { state = { version: 'v' + (state.poem.revision + 1), poem: { ...state.poem, text, revision: state.poem.revision + 1 } }; },
    dropNext() { drop = true; } };
}

(async () => {
  const h = harness(); await h.tick();
  const original = h.callbacks.at(-1);
  h.external('agent saved'); await h.tick();
  assert.equal(h.callbacks.at(-1).text, 'agent saved');
  await assert.rejects(h.host.db.collection('poems').doc('one').set({ ...original, text: 'stale browser' }), { code: 'CONFLICT' });
  assert.equal(h.state.poem.text, 'agent saved');
  assert.equal(h.posted.at(-1).if_version, 'v1', 'polling must not refresh the edit precondition');

  const retry = harness(); await retry.tick();
  const body = { ...retry.callbacks.at(-1), text: 'browser saved' };
  retry.dropNext();
  await assert.rejects(retry.host.db.collection('poems').doc('one').set(body), /lost acknowledgement/);
  await retry.tick();
  const receipt = await retry.host.db.collection('poems').doc('one').set(body);
  assert.equal(receipt.version, 'v2'); assert.equal(retry.writes, 1);
  assert.equal(retry.posted[0].request_id, retry.posted[1].request_id);

  const advanced = harness(); await advanced.tick();
  const staleBody = { ...advanced.callbacks.at(-1), text: 'saved before response was lost' };
  advanced.dropNext();
  await assert.rejects(advanced.host.db.collection('poems').doc('one').set(staleBody));
  advanced.external('newer agent update'); await advanced.tick();
  await assert.rejects(advanced.host.db.collection('poems').doc('one').set(staleBody), { code: 'CONFLICT' });
  assert.equal(advanced.state.poem.text, 'newer agent update');
  console.log('PASS shared-file transport: external refresh, stale preconditions, one-write retry and later-version preservation');
})().catch(error => { console.error(error); process.exitCode = 1; });

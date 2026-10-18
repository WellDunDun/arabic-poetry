// Exercise the production adapter, including the portable request/response exchange.
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/workbench/host.js'), 'utf8');

function harness(claude) {
  const nodes = [], clicked = [], revoked = [];
  let copied;
  const context = { window: { claude }, Blob, AbortController, DOMException, setTimeout: fn => fn(),
    URL: { createObjectURL: () => 'blob:local', revokeObjectURL: x => revoked.push(x) },
    navigator: { clipboard: { async writeText(text) { copied = text; } } },
    document: { body: { appendChild(node) { nodes.push(node); } }, createElement(tag) {
      const parts = new Map();
      return { tag, value: '', listeners: {}, querySelector(selector) {
        if (!parts.has(selector)) parts.set(selector, { value: '', textContent: '' });
        return parts.get(selector);
      }, addEventListener(name, fn) { this.listeners[name] = fn; },
      showModal() { this.open = true; }, close() { this.open = false; },
      remove() { this.removed = true; }, click() { clicked.push(this); } };
    } } };
  vm.createContext(context); vm.runInContext(source, context);
  return { connect: context.window.DiwanConnection.connect, nodes, clicked, revoked, get copied() { return copied; } };
}

(async () => {
  const h = harness(), host = await h.connect();
  assert.equal(host.db, null);
  assert.equal(host.sample.requiresUserHandoff, true);
  assert.equal((await host.sample.limits()).tools, false);
  const pending = host.sample.json('شكّل سلام، وأجب بكائن JSON');
  const dialog = h.nodes[0];
  assert(dialog.open);
  await dialog.querySelector('.agent-copy').onclick();
  assert(h.copied.includes('شكّل سلام'));
  await assert.rejects(host.sample.json('second request'), /أكمل الطلب/);
  dialog.querySelector('.agent-response').value = 'not JSON';
  dialog.querySelector('.agent-apply').onclick();
  assert(dialog.open, 'invalid JSON must not close the exchange');
  assert(dialog.querySelector('.agent-error').textContent);
  dialog.querySelector('.agent-response').value = '```json\n{"lines":["سَلَام"]}\n```';
  dialog.querySelector('.agent-apply').onclick();
  assert.equal(JSON.stringify(await pending), '{"lines":["سَلَام"]}');
  assert(dialog.removed);

  const controller = new AbortController();
  const cancelled = host.sample.json('private poem', { signal: controller.signal });
  const rejection = assert.rejects(cancelled, { name: 'AbortError' });
  controller.abort(); await rejection;
  assert(h.nodes[1].removed);
  await assert.rejects(host.sample.json('already cancelled', { signal: controller.signal }), { name: 'AbortError' });
  assert.equal(h.nodes.length, 2, 'an already cancelled request must not open a dialog');

  const closing = host.sample.json('cancel with Escape');
  const closed = assert.rejects(closing, { name: 'AbortError' });
  h.nodes[2].listeners.cancel({ preventDefault() {} }); await closed;
  await host.downloads.save({ filename: 'poem.docx', data: new Uint8Array([1, 2]) });
  assert.equal(h.clicked[0].download, 'poem.docx');
  assert.deepEqual(h.revoked, ['blob:local']);

  const services = { sample: { json() {} }, db: {}, downloads: { save() {} } };
  const calls = [];
  const compatible = await harness({ async use(name) { calls.push(name); return services[name]; } }).connect();
  assert.equal(compatible.sample, services.sample);
  assert.equal(compatible.db, services.db);
  assert.equal(compatible.downloads, services.downloads);
  assert.deepEqual(calls.sort(), ['db', 'downloads', 'sample']);
  const fallback = await harness({ async use() { throw new Error('not granted'); } }).connect();
  assert.equal(fallback.db, null); assert.equal((await fallback.sample.limits()).tools, false);
  assert.equal(fallback.downloads, null, 'a Claude host without downloads must keep the unavailable-download guard');

  const injected = await h.connect({ label: 'Codex adapter', sample: services.sample });
  assert.equal(injected.label, 'Codex adapter');
  assert.equal(injected.sample, services.sample);
  assert.equal(injected.db, null);
  assert.equal((await h.connect({ downloads: null })).downloads, null, 'an embedder can explicitly disable downloads');
  console.log('PASS workbench host: portable exchange, invalid input, cancellation, native download, optional host adapters');
})().catch(error => { console.error(error); process.exitCode = 1; });

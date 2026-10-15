// node skills/arabic-prosody/tests/workbench_state.js — deterministic production-page state regressions
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const page = fs.readFileSync(path.join(__dirname, '../assets/workbench/page.html'), 'utf8');
const application = page.slice(page.lastIndexOf('<script>') + '<script>'.length);
const boot = application.indexOf('  // ---------------------------------------------------------------- boot');
assert(boot > 0, 'application boot marker must exist');
const snapshotStart = application.indexOf("    db.collection('poems').onSnapshot(snap => {");
const snapshotEnd = application.indexOf("    }, () => { toast('انقطع الاتصال بالديوان'); });", snapshotStart);
assert(snapshotStart > 0 && snapshotEnd > snapshotStart, 'production snapshot callback must exist');
const snapshot = application.slice(application.indexOf('\n', snapshotStart) + 1, snapshotEnd);
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const poem = (id, text = 'سلام') => ({ id, title: id, text, mode: 'auto', meter: '', choices: [], suggestions: {} });

function harness(initial) {
  const elements = new Map(), timers = new Map(), storage = new Map();
  let timerId = 0;
  const element = id => {
    if (!elements.has(id)) elements.set(id, { id, hidden: true, value: '', options: [], dataset: {}, listeners: {},
      addEventListener(type, fn) { this.listeners[type] = fn; }, setAttribute() {}, focus() {}, select() {} });
    return elements.get(id);
  };
  const context = { console, AbortController,
    window: { Arud: { data: { info: {} }, load() {}, clean: s => s, rhymeCheck: () => ({ rows: [] }) } },
    document: { getElementById: element, addEventListener() {}, querySelectorAll: () => [], activeElement: null },
    localStorage: { getItem: k => storage.has(k) ? storage.get(k) : null, setItem: (k, v) => storage.set(k, v) },
    setTimeout(fn) { const id = ++timerId; timers.set(id, fn); return id; }, clearTimeout(id) { timers.delete(id); } };
  vm.createContext(context);
  // Keep all production functions intact; replace rendering/scansion only, outside the behavior under test.
  const expose = `
    render = () => renderSelect(); renderLines = () => {};
    checkLine = text => ({text, ok: true}); meterLabel = () => 'test meter';
    lineViews = () => [{diag: []}];
    globalThis.api = { save, flush, askLine, askAlternatives, askDiacritics, preservesDiacritics,
      snapshot(snap) { ${snapshot} },
      setup(initial) { poems = initial; curId = initial[0].id; analysis = {mode:'free',free:[{family:{foot:'test',meter:'test'}}]}; renderSelect(); },
      sample(value, tools = false) { sample = value; sampleTools = tools; }, db(value) { db = value; },
      get poems() { return poems; }, get chats() { return askState; }, get alternatives() { return altResults; },
      dirty, revisions
    };
  })();`;
  vm.runInContext(application.slice(0, boot) + expose, context, { filename: 'production-page.html' });
  const api = context.api; api.setup(initial);
  function select(id) {
    element('pmList').listeners.click({ target: { closest: () => ({ dataset: { pm: 'open', id } }) } });
  }
  function receive(rows) { api.snapshot({ docs: rows.map(p => ({ id: p.id, data: () => p })) }); }
  return { api, select, receive, elements, timers };
}

async function staleSave() {
  const h = harness([poem('a', 'old')]), writes = [];
  h.api.db({ collection: () => ({ doc: () => ({ set(body) { const done = deferred(); writes.push({ body, done }); return done.promise; } }) }) });
  h.api.save(h.api.poems[0]);
  const first = h.api.flush('a');
  h.api.poems[0].text = 'new'; h.api.poems[0].choices.push({ word: 'new' }); h.api.save(h.api.poems[0]);
  assert.equal(writes[0].body.choices.length, 0, 'in-flight body must not share mutable choices');
  writes[0].done.resolve(); await first;
  assert(h.api.dirty.has('a'), 'older save cannot acknowledge a newer edit');
  h.receive([{ id: 'a', ...writes[0].body }]);
  assert.equal(h.api.poems[0].text, 'new', 'old snapshot cannot erase pending edit');
  const second = h.api.flush('a');
  assert.equal(writes[1].body.text, 'new');
  writes[1].done.resolve(); await second;
  assert(!h.api.dirty.has('a'), 'matching acknowledgement clears dirty');
  h.receive([{ id: 'a', ...writes[1].body }]);
  assert.equal(h.api.poems[0].text, 'new');
}

async function conversations() {
  const h = harness([poem('a', 'poem A'), poem('b', 'poem B')]), requests = [];
  h.api.sample({ json(turns, opts) { const done = deferred(); requests.push({ turns: JSON.parse(JSON.stringify(turns)), opts, done }); return done.promise; } }, true);
  const first = h.api.askLine(0, 'question A');
  h.select('b');
  assert(requests[0].opts.signal.aborted, 'switch cancels existing conversation');
  assert.throws(() => requests[0].opts.tools[0].execute({ lines: ['stale candidate'] }), /stale poem/, 'late tool cannot scan against another poem');
  assert.equal(Object.keys(h.api.chats).length, 0, 'switch clears prior poem conversation');
  const second = h.api.askLine(0, 'question B');
  assert(requests[1].turns[0].content.includes('poem B'));
  assert(!JSON.stringify(requests[1].turns).includes('poem A'));
  requests[0].done.resolve({ answer: 'reply A', alternatives: [{ text: 'poem A replacement' }] }); await first;
  assert.equal(h.api.chats[0].msgs.length, 1, 'late reply cannot appear in other poem');
  requests[1].done.resolve({ answer: 'reply B', alternatives: [] }); await second;
  assert.equal(h.api.chats[0].msgs[1].text, 'reply B');
  h.api.poems[1].text = 'edited B'; h.api.save(h.api.poems[1]);
  const third = h.api.askLine(0, 'new draft question');
  assert(requests[2].turns[0].content.includes('edited B'));
  assert(!JSON.stringify(requests[2].turns).includes('reply B'));
  h.api.poems[1].text = 'edited again'; h.api.save(h.api.poems[1]);
  requests[2].done.resolve({ answer: 'outdated reply' }); await third;
  assert.equal(h.api.chats[0].msgs.length, 1, 'reply to previous draft is discarded');
}

async function staleAlternatives() {
  const h = harness([poem('a'), poem('b')]), done = deferred();
  h.api.sample({ json: () => done.promise });
  const request = h.api.askAlternatives(0);
  h.select('b');
  done.resolve([{ text: 'late alternative' }]); await request;
  assert.equal(Object.keys(h.api.alternatives).length, 0, 'late alternatives cannot populate another poem');
}

async function diacritics() {
  const cases = [
    ['سلام', ['سَلَام'], true, 'valid added marks'],
    ['سَلام', ['سَلَام'], true, 'preserved existing vowel'],
    ['سَلّام', ['سَلَّام'], true, 'canonical combining-mark order'],
    ['سَلام', ['سُلَام'], false, 'changed vowel'],
    ['سَلام', ['سلام'], false, 'removed vowel'],
    ['سلّام', ['سَلَام'], false, 'removed shadda'],
    ['سلام', ['كَلَام'], false, 'changed base word'],
    ['سلام\nسلام', ['سَلَام'], false, 'removed line'],
    ['سلام', ['سَلَام\nسَلَام'], false, 'embedded newline'],
    ['سلام', [42], false, 'non-string line'],
    ['سلام', ['سَُلَام'], false, 'conflicting added vowels'],
  ];
  for (const [before, lines, valid, label] of cases) {
    const h = harness([poem('a', before)]);
    h.api.sample({ json: async () => ({ lines }) });
    await h.api.askDiacritics();
    assert.equal(h.api.poems[0].text, valid ? lines.join('\n') : before, label);
  }
  for (const action of ['edit', 'edit-and-undo', 'switch', 'switch-back', 'snapshot']) {
    const h = harness([poem('a'), poem('b')]), done = deferred();
    h.api.sample({ json: () => done.promise });
    const request = h.api.askDiacritics();
    if (action.startsWith('edit')) {
      h.api.poems[0].text = 'newer draft'; h.api.save(h.api.poems[0]);
      if (action === 'edit-and-undo') { h.api.poems[0].text = 'سلام'; h.api.save(h.api.poems[0]); }
    } else if (action === 'snapshot') h.receive([poem('a', 'remote edit'), poem('b')]);
    else { h.select('b'); if (action === 'switch-back') h.select('a'); }
    const expected = h.api.poems[0].text;
    done.resolve({ lines: ['سَلَام'] }); await request;
    assert.equal(h.api.poems[0].text, expected, `stale diacritics after ${action}`);
  }
}

(async () => {
  await staleSave(); await conversations(); await staleAlternatives(); await diacritics();
  console.log('PASS workbench state: revision-safe saves, isolated conversations, stale responses, preserved wording/marks');
})().catch(error => { console.error(error); process.exitCode = 1; });

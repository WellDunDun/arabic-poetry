// node skills/arabic-poetry/tests/workbench_state.js — deterministic production-page state regressions
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const page = fs.readFileSync(process.env.WORKBENCH_PAGE || path.join(__dirname, '../assets/workbench/page.html'), 'utf8');
const application = page.slice(page.lastIndexOf('<script>') + '<script>'.length);
const boot = application.indexOf('  // ---------------------------------------------------------------- boot');
assert(boot > 0, 'application boot marker must exist');
const snapshotStart = application.indexOf("    db.collection('poems').onSnapshot(snap => {");
const snapshotEnd = application.indexOf("    }, () => { toast('انقطع الاتصال بالديوان'); });", snapshotStart);
assert(snapshotStart > 0 && snapshotEnd > snapshotStart, 'production snapshot callback must exist');
const snapshot = application.slice(application.indexOf('\n', snapshotStart) + 1, snapshotEnd);
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const poem = (id, text = 'سلام') => ({ id, title: id, text, mode: 'auto', meter: '', choices: [], suggestions: {} });

function harness(initial, options = {}) {
  const elements = new Map(), timers = new Map(), storage = new Map(), listeners = new Map();
  let timerId = 0;
  const element = id => {
    if (!elements.has(id)) elements.set(id, { id, hidden: true, value: '', options: [], dataset: {}, listeners: {}, style: {}, offsetWidth: 200, offsetHeight: 100,
      querySelector() { return {focus() {}, getBoundingClientRect: () => ({left:300,right:500,top:100})}; },
      getBoundingClientRect: () => ({left:300,right:500,top:100}),
      addEventListener(type, fn) { this.listeners[type] = fn; }, setAttribute() {}, focus() {}, select() {}, scrollIntoView() {} });
    return elements.get(id);
  };
  const context = { console, AbortController,
    window: { ...(options.shared ? {DiwanFile: {}} : {}), addEventListener() {}, innerWidth: 1200, innerHeight: 800, Arud: { data: { info: {} }, load() {}, clean: s => s, words: s => s.split(/\s+/).filter(Boolean), syll: s => s, verifyLine: () => ({ok:true,feet:[]}), rhymeCheck: () => ({ rows: [] }) } },
    document: { getElementById: element, addEventListener(type, fn) { if (!listeners.has(type)) listeners.set(type, []); listeners.get(type).push(fn); }, querySelectorAll: () => [], querySelector: () => null, activeElement: null,
      createElement: tag => ({ tag, hidden: true, dataset: {}, style: {}, classList: { add() {}, remove() {}, toggle() {} }, listeners: {},
        addEventListener(type, fn) { this.listeners[type] = fn; }, setAttribute() {}, appendChild() {} }),
      body: { appendChild(el) { if (el.id) element(el.id); } } },
    localStorage: { getItem: k => { if (options.blockStorage) throw new Error('storage denied'); return storage.has(k) ? storage.get(k) : null; },
      setItem: (k, v) => { if (options.blockStorage) throw new Error('storage denied'); storage.set(k, v); } },
    setTimeout(fn) { const id = ++timerId; timers.set(id, fn); return id; }, clearTimeout(id) { timers.delete(id); } };
  vm.createContext(context);
  // Keep all production functions intact; replace rendering/scansion only, outside the behavior under test.
  const expose = `
    render = () => renderSelect(); renderLines = () => {};
    checkLine = text => ({text, ok: true}); meterLabel = () => 'test meter';
    lineViews = () => [{diag: []}];
    globalThis.api = { save, flush, askLine, askAlternatives, askDiacritics, preservesDiacritics,
      addLineAt, dropPending, saveLine, doUndo, fetchWordAlts, openCm, openPop, closePop,
      context(li, wi = 0) { cmCtx = { li, wi, word: linesOf(cur())[li].split(' ')[wi], bits: '' }; },
      get wordAlternatives() { return wordAlts.get(altKey()); }, get editing() { return editing; },
      snapshot(snap) { ${snapshot} },
      setup(initial) { poems = initial; curId = initial.length ? initial[0].id : null; analysis = {mode:'free',free:[{family:{foot:'test',meter:'test'}}]}; renderSelect(); },
      launch(initial) { window.DiwanInitialPoem = initial; openInitialPoem(); },
      get currentId() { return curId; },
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
  function click(act, li) {
    const fn = listeners.get('click').find(f => f.toString().includes("act === 'edit'"));
    fn({ target: { closest: query => query === '[data-act]' ? { dataset: { act, li: String(li) } } : null } });
  }
  return { api, select, receive, element, elements, timers, storage, click,
    runtimeReady() { return context.window.DiwanFileReady(); }, focus(el) { context.document.activeElement = el; }, dialogMouseDown() {
    const fn = listeners.get('mousedown').find(f => f.toString().includes("$('cmenu')"));
    fn({target:{closest: selector => selector.includes('.agent-exchange') ? {} : null}});
  } };
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

async function lineEditing() {
  for (const action of ['delline', 'edit', 'addbelow']) {
    const h = harness([poem('a', 'أول\nثان\nثالث\nرابع')]);
    h.api.addLineAt(1);
    h.click(action, 2); // rendered index 2 is ثان, after the temporary blank
    if (action === 'delline') assert.equal(h.api.poems[0].text, 'أول\nثالث\nرابع', 'delete the selected row, not its successor');
    if (action === 'edit') assert.equal(h.api.editing, 1, 'edit the row after discarding the earlier draft');
    if (action === 'addbelow') assert.equal(h.api.poems[0].text, 'أول\nثان\n\nثالث\nرابع');
  }
  const switched = harness([poem('a', 'أول\nثان'), poem('b', 'آخر\nنهاية')]);
  switched.api.addLineAt(1); switched.select('b');
  assert.equal(switched.api.poems[0].text, 'أول\nثان', 'leaving a poem discards its transient empty row');
  assert.equal(switched.api.poems[1].text, 'آخر\nنهاية', 'another poem is not touched by pending-row cleanup');
  const p = poem('a', 'أول\nثان');
  p.choices = [{ line: 2, word: 'ثان' }]; p.suggestions = { '2': [{ text: 'بديل الثاني' }] };
  const h = harness([p]);
  h.api.addLineAt(1);
  assert.equal(p.choices[0].line, 3);
  assert(p.suggestions['3']);
  h.api.dropPending();
  assert.equal(p.choices[0].line, 2); assert(p.suggestions['2']);
  h.click('delline', 0);
  assert.equal(p.text, 'ثان'); assert.equal(p.choices[0].line, 1); assert(p.suggestions['1']);
  h.api.doUndo();
  assert.equal(p.text, 'أول\nثان'); assert.equal(p.choices[0].line, 2); assert(p.suggestions['2']);
  h.click('delline', 1);
  assert.equal(p.choices.length, 0); assert.equal(Object.keys(p.suggestions).length, 0);
}

async function wordContext() {
  const h = harness([poem('a', 'سلام حاضر\nسياق أول'), poem('b', 'سلام حاضر\nسياق ثان')]), requests = [];
  h.api.sample({ json(input) { const done = deferred(); requests.push({ input, done }); return done.promise; } });
  h.api.context(0); const first = h.api.fetchWordAlts();
  h.select('b'); h.api.context(0); const second = h.api.fetchWordAlts();
  assert.equal(requests.length, 2, 'a shared line in another poem needs its own context');
  requests[0].done.resolve({ synonyms: [{ text: 'قديم' }] }); await first;
  assert(!h.api.wordAlternatives.syn, 'the previous poem response cannot populate the current cache');
  requests[1].done.resolve({ synonyms: [{ text: 'جديد' }] }); await second;
  assert.equal(h.api.wordAlternatives.syn[0].text, 'جديد');
  h.api.poems[1].meter = 'other'; h.api.context(0);
  const third = h.api.fetchWordAlts(); assert.equal(requests.length, 3, 'meter changes invalidate word suggestions');
  requests[2].done.resolve({ synonyms: [{ text: 'وزن' }] }); await third;
}

async function manualWordMenu() {
  const h = harness([poem('a', 'سلام حاضر')]), requests = [];
  h.api.sample({ requiresUserHandoff: true, json(input) { const done = deferred(); requests.push({input,done}); return done.promise; } });
  h.api.openCm({dataset:{li:'0',wi:'0'},textContent:'سلام'}, 500, 200);
  assert.equal(requests.length, 0, 'opening a word menu must leave edit/delete available without an agent dialog');
  const button = {dataset:{cm:'syn'}};
  h.elements.get('cmenu').listeners.mouseover({target:{closest:()=>button}});
  assert.equal(requests.length, 0, 'hovering must not queue a manual handoff');
  assert(h.elements.get('cmsub').innerHTML.includes('اضغط لطلب'));
  h.elements.get('cmenu').listeners.click({target:{closest:selector=>selector==='[data-cm]'?button:null}});
  assert.equal(requests.length, 1, 'an explicit AI choice queues the requested handoff');
  h.dialogMouseDown();
  requests[0].done.resolve({synonyms:[{text:'جديد',note:'اقتراح'}]});
  await new Promise(setImmediate);
  assert.equal(h.elements.get('cmsub').hidden, false);
  assert(h.elements.get('cmsub').innerHTML.includes('جديد'), 'handoff results appear without reopening the word menu');
}

async function automaticWordMenu() {
  const h = harness([poem('a', 'سلام حاضر')]), requests = [];
  h.api.sample({ requiresUserHandoff: false, json(input) {
    const done = deferred(); requests.push({input,done}); return done.promise;
  } });
  h.api.openCm({dataset:{li:'0',wi:'0'},textContent:'سلام'}, 500, 200);
  assert.equal(requests.length, 1, 'opening the word menu automatically requests suggestions');
  const button = {dataset:{cm:'syn'}};
  h.elements.get('cmenu').listeners.click({target:{closest:selector=>selector==='[data-cm]'?button:null}});
  assert.equal(requests.length, 1, 'selecting a category must reuse the in-flight word request');
  requests[0].done.reject(new Error('Client timed out. Try again.'));
  await new Promise(setImmediate);
  assert(h.elements.get('cmsub').innerHTML.includes('Client timed out'), 'failures stay visible instead of reverting to an endless spinner');
  assert(h.elements.get('cmsub').innerHTML.includes('data-cm="more"'), 'a failed request still offers retry');
  const more = {dataset:{cm:'more'}};
  h.elements.get('cmsub').listeners.click({target:{closest:selector=>selector==='[data-cm]'?more:null}});
  assert.equal(requests.length, 2);
  requests[1].done.resolve({synonyms:[{text:'أمان',note:'peace'}]});
  await new Promise(setImmediate);
  assert(h.elements.get('cmsub').innerHTML.includes('أمان'));
}

async function approvalReadback() {
  const local = harness([poem('a')]); local.click('confirm', 0);
  assert.equal(local.api.poems[0].status, 'confirmed');
  assert(local.elements.get('toast').textContent.includes('انسخ القصيدة والصقها'), 'local approval must request the latest text, not imply agent access to browser storage');
  const hosted = harness([poem('a')]); hosted.api.db({}); hosted.click('confirm', 0);
  assert(hosted.elements.get('toast').textContent.includes('انتهيت'), 'connected host retains the original readback workflow');
}

async function preloadedLaunch() {
  const original = { ...poem('current', 'لَمْ أبع الوعد\nسلام'), status: 'review', source_id: 'workspace-poem' };
  const h = harness([poem('other', 'another poem')]);
  h.api.launch(original);
  assert.equal(h.api.currentId, 'current', 'launch selects the requested poem rather than the last open poem');
  assert.equal(h.api.poems[1].text, original.text, 'marks and line breaks arrive without a paste');
  assert.equal(h.api.poems[1].status, 'review', 'opening does not approve a reading');
  h.api.poems[1].text = 'newer browser edit';
  h.api.launch(original);
  assert.equal(h.api.poems.length, 2, 'reopening does not duplicate a poem');
  assert.equal(h.api.poems[1].text, 'newer browser edit', 'reopening cannot replace saved edits with the seed');
  assert(h.elements.get('launchStatus').textContent.includes('مسودتك'));
  const revised = {...original, id:'chat-revision', text:'revised and accepted in chat'};
  h.api.launch(revised);
  assert.equal(h.api.currentId, revised.id, 'new supplied text must open rather than silently selecting the old browser draft');
  assert.equal(h.api.poems[1].text, 'newer browser edit', 'a new supplied revision preserves the earlier browser draft');
  assert.equal(h.api.poems[2].text, revised.text);
  assert(h.elements.get('launchStatus').textContent.includes('مستقلة'));
  h.api.launch(revised);
  assert.equal(h.api.poems.length, 3, 'reopening a supplied revision does not create duplicate drafts');
  const blocked = harness([], {blockStorage: true});
  blocked.api.launch(original);
  assert.equal(blocked.api.poems[0].text, original.text, 'storage denial must not produce an empty editor');
  assert.equal(blocked.api.currentId, original.id);
  assert.equal(blocked.elements.get('launchStatus').hidden, false);
  assert(blocked.elements.get('launchStatus').textContent.includes('الحفظ'));
}

module.exports = { harness };

if (require.main === module) (async () => {
  await staleSave(); await conversations(); await staleAlternatives(); await diacritics(); await lineEditing(); await wordContext(); await manualWordMenu(); await automaticWordMenu(); await approvalReadback(); await preloadedLaunch();
  console.log('PASS workbench state: revision-safe saves, isolated conversations, stale responses, preserved wording/marks, line identities/metadata and word context');
})().catch(error => { console.error(error); process.exitCode = 1; });

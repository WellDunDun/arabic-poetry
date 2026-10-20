// Exercise the real page's readiness gate and real update polling through races.
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const {harness: pageHarness} = require('./workbench_state.js');
const {harness: transportHarness} = require('./workbench_file.js');
const source = fs.readFileSync(path.join(__dirname, '../assets/workbench/updates.js'), 'utf8');

async function fixture() {
  const transport = transportHarness();
  const page = pageHarness([{...transport.state.poem, _file_version:'v1'}], {shared:true});
  page.api.db(transport.host.db);
  const state = {id:'one', protocol:2, version:'0.3.1', available:'0.3.2'};
  let poll, reloads = 0, restarts = 0, delay;
  const messages = [];
  const context = {window:{DiwanFile:{runtime:'0.3.1', id:'one'}, location:{reload(){reloads++;}}},
    document:{createElement(){const node={setAttribute(){}};messages.push(node);return node;}, querySelector(){return {prepend(){}};}},
    setInterval(fn){poll=fn;return 1;}, clearInterval(){}};
  vm.createContext(context); vm.runInContext(source, context);
  context.window.DiwanRuntimeUpdates(async (route, body) => {
    assert.equal(route, '/runtime');
    if (body) {restarts++;return {restarting:true};}
    if (delay) {const fn=delay;delay=null;await fn();}
    return {...state};
  }, () => page.runtimeReady());
  return {page,transport,state,poll, get reloads(){return reloads;}, get restarts(){return restarts;}, messages,
    delay(fn){delay=fn;}};
}

async function run() {
  for (const kind of ['bulk','line','word','title','question','dirty','saving','export','ai']) {
    const h = await fixture();
    assert.equal(h.page.runtimeReady(), true);
    if (kind==='bulk') {h.page.element('bulkBtn').onclick();h.page.element('bulk').value='unsaved bulk draft';}
    if (kind==='line') {h.page.click('edit',0);h.page.element('edit-0').value='unsaved line draft';}
    if (kind==='word') h.page.api.openPop({dataset:{li:'0',wi:'0'},textContent:'original',getBoundingClientRect:()=>({left:20,top:20,bottom:40,width:30})});
    if (kind==='title') h.page.focus({tagName:'INPUT',value:'unsaved title'});
    if (kind==='question') h.page.api.chats[0]={draft:'unsent question'};
    if (kind==='dirty' || kind==='saving') {h.page.api.poems[0].text='unsaved poem';h.page.api.save(h.page.api.poems[0]);}
    if (kind==='saving') {
      h.page.api.db({collection(){return {doc(){return {set(){return new Promise(()=>{});}};}};}});
      h.page.api.flush('one');
    }
    if (kind==='export') h.page.element('exportDlg').hidden=false;
    if (kind==='ai') h.page.element('diacBtn').disabled=true;
    const text=h.page.api.poems[0].text;
    assert.equal(h.page.runtimeReady(), false, kind);
    await h.poll(); assert.equal(h.restarts,0,kind+' prevents a restart request');
    h.state.version='0.3.2'; await h.poll();
    assert.equal(h.reloads,0,kind+' survives a restart initiated by another tab');
    assert.equal(h.page.api.poems[0].text,text,kind+' poem retained');
    if (kind==='bulk') assert.equal(h.page.element('bulk').value,'unsaved bulk draft');
    if (kind==='line') assert.equal(h.page.element('edit-0').value,'unsaved line draft');
  }
  const clean = await fixture();await clean.poll();assert.equal(clean.restarts,1);
  clean.state.version='0.3.2';await clean.poll();assert.equal(clean.reloads,1);
  assert.equal(clean.transport.writes,0,'runtime updates never save the poem');

  const race=await fixture();let resume;
  race.delay(()=>new Promise(resolve=>{resume=resolve;}));const checking=race.poll();
  race.page.element('bulkBtn').onclick();race.page.element('bulk').value='typed during update check';
  resume();await checking;assert.equal(race.restarts,0,'readiness is checked after the asynchronous response');
  race.page.element('bulkCancel').onclick();await race.poll();assert.equal(race.restarts,1,'update resumes after explicit edit cancellation');
  race.page.api.poems[0].text='typed after restart began';race.page.api.save(race.page.api.poems[0]);
  race.state.version='0.3.2';await race.poll();assert.equal(race.reloads,0,'a new edit during restart is kept');
  await race.page.api.flush('one');await race.poll();assert.equal(race.reloads,1,'reload follows acknowledgement of the latest edit');
  assert.equal(race.transport.state.poem.text,'typed after restart began');

  const conflict=await fixture();conflict.page.api.poems[0].text='local conflict draft';conflict.page.api.save(conflict.page.api.poems[0]);
  conflict.transport.external('agent saved');await conflict.page.api.flush('one');
  conflict.state.version='0.3.2';await conflict.poll();
  assert.equal(conflict.reloads,0);assert.equal(conflict.page.api.poems[0].text,'local conflict draft');
  assert.equal(conflict.transport.state.poem.text,'agent saved');

  for (const changes of [{protocol:1},{protocol:3},{id:'another-poem'}]) {
    const h=await fixture();Object.assign(h.state,changes);await h.poll();assert.equal(h.restarts,0);assert.equal(h.reloads,0);
  }
  const rollback=await fixture();await rollback.poll();rollback.state.available=null;rollback.state.recovered=true;
  await rollback.poll();assert.equal(rollback.reloads,0);assert.equal(rollback.restarts,1);
  assert(rollback.messages.some(n=>n.textContent.includes('النسخة السابقة')));
  console.log('PASS runtime updates: clean reload, active editor/draft/AI guards, late typing, save acknowledgement, conflict, foreign identity and rollback');
}
run().catch(error=>{console.error(error);process.exitCode=1;});

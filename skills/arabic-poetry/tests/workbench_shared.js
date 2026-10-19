// Production page and transport together: deferred snapshots and literal bulk edits.
const assert = require('node:assert/strict');
const {harness: pageHarness} = require('./workbench_state.js');
const {harness: transportHarness} = require('./workbench_file.js');

async function shared() {
  const transport = transportHarness();
  const page = pageHarness([{...transport.state.poem,_file_version:transport.state.version}],{shared:true});
  page.api.db(transport.host.db);
  transport.host.db.collection('poems').onSnapshot(snap=>page.api.snapshot(snap));
  await transport.tick();
  return {page,transport};
}

async function deferredRefresh(kind) {
  const {page,transport}=await shared();
  if(kind==='bulk') page.element('bulkBtn').onclick();
  if(kind==='line') page.click('edit',0);
  if(kind==='word') page.api.openPop({dataset:{li:'0',wi:'0'},textContent:'original',getBoundingClientRect:()=>({left:20,top:20,bottom:40,width:30})});
  const menu=page.element('pmList');let redraws=0,html=menu.innerHTML;
  Object.defineProperty(menu,'innerHTML',{get:()=>html,set:value=>{html=value;redraws++;}});
  transport.external('newer agent poem');await transport.tick();await transport.tick();
  assert.equal(redraws,0,'a held snapshot must not repeatedly rebuild the menu');
  assert.equal(page.api.poems[0].text,'original','active editing retains its draft');
  if(kind==='bulk') page.element('bulkCancel').onclick();
  if(kind==='line') page.click('cancel',0);
  if(kind==='word') page.api.closePop();
  await transport.tick();
  assert.equal(page.api.poems[0].text,'newer agent poem','clean editor adopts the deferred remote snapshot');
  assert.equal(page.api.poems[0]._file_version,transport.state.version);
  assert.equal(transport.writes,0,'cancel/close must never write the poem');
  assert.equal(transport.posted.length,0,'cancel/close must not send even a rejected save');
  assert.equal(page.api.dirty.size,0,'cancel/close must not queue a save');
}

async function unchangedBulk(text) {
  const {page,transport}=await shared();
  page.api.poems[0].text=text;
  let value='';
  // Real textarea values normalize CRLF on assignment; canonical bytes need not.
  Object.defineProperty(page.element('bulk'),'value',{get:()=>value,set:v=>{value=v.replace(/\r\n?/g,'\n');}});
  page.element('bulkBtn').onclick();page.element('bulkSave').onclick();
  assert.equal(page.api.poems[0].text,text,'unchanged bulk Save preserves canonical text, including original line endings');
  assert.equal(page.api.dirty.size,0,'unchanged bulk Save does not queue a revision');
  assert.equal(transport.writes,0);
  assert.equal(transport.posted.length,0,'unchanged Save must not send even a rejected save');
}

async function literalBulkEdit() {
  const {page,transport}=await shared();
  const text='  أول\n\n\nثان\n';
  page.element('bulkBtn').onclick();page.element('bulk').value=text;page.element('bulkSave').onclick();
  await page.api.flush('one');
  assert.equal(transport.state.poem.text,text,'shared bulk Save preserves the actual edited whitespace');
  assert.equal(transport.writes,1);
}

async function dirtyConflict() {
  const {page,transport}=await shared();
  page.api.poems[0].text='local draft';page.api.save(page.api.poems[0]);
  transport.external('newer agent poem');await transport.tick();await transport.tick();
  assert.equal(page.api.poems[0].text,'local draft');
  assert.equal(page.api.poems[0]._file_version,'v1','repeated deferred polls do not refresh a draft precondition');
  await page.api.flush('one');
  assert.equal(transport.state.poem.text,'newer agent poem');
  assert(page.api.dirty.has('one'),'conflict keeps local draft dirty and recoverable');
}

(async()=>{
  const tests=[...['bulk','line','word'].map(kind=>[kind+' cancel/close refresh',()=>deferredRefresh(kind)]),
    ['unchanged LF',()=>unchangedBulk('  أول\n\n\nثان\n')],
    ['unchanged CRLF',()=>unchangedBulk('  أول\r\n\r\nثان\r\n')],
    ['literal bulk edit',literalBulkEdit],['dirty conflict remains protected',dirtyConflict]];
  let failed=0;
  for(const [name,run]of tests){try{await run();console.log('PASS '+name);}catch(error){failed++;console.error('FAIL '+name+': '+error.message);}}
  assert.equal(failed,0,'shared page/transport regressions');
})().catch(error=>{console.error(error);process.exitCode=1;});

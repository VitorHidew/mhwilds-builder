const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup(fetch) {
    const fields=new Map();
    const document={addEventListener(){},querySelectorAll:()=>[],getElementById(id){if(!fields.has(id))fields.set(id,{value:'id',checked:false});return fields.get(id);}};
    const context=vm.createContext({document,window:{},localStorage:{getItem:()=>null},fetch,setTimeout,clearTimeout,AbortController,console});
    vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/js/app.js'),'utf8'),context);
    vm.runInContext('GAME_DATA={};currentScenarioPayload=()=>({});updateUI=()=>{};setCalculationStatus=()=>{};',context);
    return {context,fields,run:code=>vm.runInContext(code,context)};
}

test('late calculation responses cannot replace the newest result',async()=>{
    const pending=[];
    const c=setup(()=>new Promise(resolve=>pending.push(resolve)));
    const first=c.run('runRecalculate()'),second=c.run('runRecalculate()');
    pending[1]({ok:true,json:async()=>({practical_dps:200})});await second;
    pending[0]({ok:true,json:async()=>({practical_dps:100})});await first;
    assert.equal(c.run('CURRENT_RESULT.practical_dps'),200);
});
test('direct save calculation settles pending debounce callers',async()=>{
    const c=setup(async()=>({ok:true,json:async()=>({practical_dps:75})}));
    const debounced=c.run('recalculate(60000)');
    const direct=await c.run('runRecalculate()');
    assert.equal(direct.practical_dps,75);
    assert.equal((await debounced).practical_dps,75);
    assert.equal(c.run('RECALC_WAITERS.length'),0);
});
test('a stale validation error cannot overwrite current warnings',async()=>{
    const pending=[];
    const c=setup(()=>new Promise(resolve=>pending.push(resolve)));
    const first=c.run('runRecalculate()'),second=c.run('runRecalculate()');
    pending[1]({ok:true,json:async()=>({practical_dps:200})});await second;
    pending[0]({ok:false,json:async()=>({detail:'outdated error'})});await first;
    assert.notEqual(c.fields.get('slot-warnings-container')?.innerText,'outdated error');
    assert.equal(c.run('CURRENT_RESULT.practical_dps'),200);
});

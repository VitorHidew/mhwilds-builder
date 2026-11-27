const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function appContext() {
    const storage = new Map();
    const context = vm.createContext({
        console, structuredClone, window: {},
        MaterialPlan: require('../static/js/material-plan.js'),
        localStorage: {getItem:key=>storage.get(key), setItem:(key,value)=>storage.set(key,value)},
        document: {addEventListener() {}}
    });
    for (const file of ['app.js', 'planner.js']) {
        vm.runInContext(fs.readFileSync(path.join(__dirname, '../static/js', file), 'utf8'), context);
    }
    return context;
}

test('Portuguese optimizer skill names are sent using canonical names', () => {
    const context = appContext();
    const result = vm.runInContext(`
        GAME_DATA = {skills:[{name:'Exploração de Fraqueza',name_en:'Weakness Exploit'}]};
        document.querySelectorAll = () => [{querySelector: selector => ({value: selector.includes('name') ? 'Exploração de Fraqueza' : '5'})}];
        JSON.stringify(collectOptimizerSkills());
    `, context);
    assert.deepEqual(JSON.parse(result), {'Weakness Exploit':5});
});

test('wishlist preserves both custom items and duplicate decoration counts without repeated inflation', () => {
    const context = appContext();
    const result = vm.runInContext(`
        GAME_DATA = {decorations:[{id:'deco_1'}]};
        renderWishlist = () => {}; renderSettingsCounts = () => {};
        const equipment = {weapon_id:'custom_gog_weapon',talisman_id:'custom_talisman',
            custom_weapon:{name:'Gog test',weapon_type:'Great Sword'},custom_talisman:{name:'Charm test'},decorations:['deco_1','deco_1']};
        wishlistEntriesFromEquipment(equipment);
        wishlistEntriesFromEquipment(equipment);
        JSON.stringify(WISHLIST);
    `, context);
    const entries = JSON.parse(result);
    assert.equal(entries.length, 3);
    assert.equal(entries.find(item=>item.type==='decoration').quantity, 2);
    assert.ok(entries.some(item=>item.type==='custom_gog'));
    assert.ok(entries.some(item=>item.type==='custom_talisman'));
});

test('comparison never serves scores from an outdated scenario or locale', () => {
    const context = appContext();
    vm.runInContext(`
        let target = 'head';
        currentScenarioPayload = () => ({target_part:target});
        document.getElementById = () => ({value:'saved'});
        SHARED_COMPARISON = {rows:[{build:{id:'one'},skill_impacts:[]}]};
        COMPARISON_INPUT_KEY = comparisonInputKey();
    `, context);
    assert.equal(vm.runInContext('comparedBuilds().length', context), 1);
    assert.equal(vm.runInContext("target='tail'; comparedBuilds().length", context), 0);
    assert.equal(vm.runInContext("target='head'; SITE_LOCALE='en'; comparedBuilds().length", context), 0);
});

test('loading a scenario restores omitted uptimes and non-UI parameters', () => {
    const context = appContext();
    const result = vm.runInContext(`
        const fields = new Map();
        document.getElementById = id => {if (!fields.has(id)) fields.set(id,{style:{}}); return fields.get(id);};
        renderMonsterIdentity = () => {}; renderMonsterIntel = () => {}; currentMonsterForChart = () => ({});
        restoreScenarioDetails({maximum_might_uptime:.7,elemental_absorption_uptime:.4,elemental_absorption_hits:3,custom_monster:null});
        JSON.stringify({might:fields.get('uptime-maxmight').value,absorb:fields.get('uptime-eleabsorb').value,
            hits:SCENARIO_BASE.elemental_absorption_hits,custom:fields.get('use-custom-monster').checked});
    `, context);
    assert.deepEqual(JSON.parse(result), {might:70,absorb:40,hits:3,custom:false});
});

test('cached optimizer conditions replace preset controls with the actual calculation values', () => {
    const context = appContext();
    const result = vm.runInContext(`
        const inputs = new Map();
        document.getElementById = id => {if (!inputs.has(id)) inputs.set(id,{value:80}); return inputs.get(id);};
        document.querySelectorAll = () => [];
        restoreOptimizerUptimes({agitator_uptime:.95,peak_performance_uptime:0});
        JSON.stringify({agi:inputs.get('opt-up-agi').value,peak:inputs.get('opt-up-peak').value});
    `, context);
    assert.deepEqual(JSON.parse(result), {agi:95,peak:0});
});

test('locale switching preserves optimizer settings after catalog reload', async () => {
    const context = appContext();
    await vm.runInContext(`
        GAME_DATA = {};
        let selectedOptimizer = {monster:'arkveld',part:'head',skills:{Agitator:5},uptime:90};
        const beforeOptimizer = JSON.stringify(selectedOptimizer);
        snapshotWorkspace = () => ({});
        snapshotOptimizer = () => structuredClone(selectedOptimizer);
        restoreOptimizerSnapshot = data => {selectedOptimizer=data;};
        restoreWorkspaceSnapshot = async () => {};
        document.getElementById = () => null;
        translateStaticInterface = () => {};
        loadGameData = async () => {selectedOptimizer={monster:'ajarakan'};};
        loadDataVersion = async () => {};
        setSaveStatus = () => {};
        switchSiteLocale('en');
    `, context);
    assert.equal(vm.runInContext('JSON.stringify(selectedOptimizer)===beforeOptimizer', context), true);
});

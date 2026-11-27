const {test} = require('node:test');
const assert = require('node:assert/strict');
const plan = require('../static/js/material-plan.js');

test('duplicate decorations keep the build quantity', () => {
    assert.deepEqual(plan.equipmentEntries({weapon_id:'custom_gog_weapon', helm_id:'helm_none', decorations:['a','a','b']}), [
        {type:'decoration', id:'a', quantity:2}, {type:'decoration', id:'b', quantity:1}
    ]);
});
test('materials aggregate quantities, discount inventory and never go negative', () => {
    const result = plan.requirements([{entry:{quantity:2}, item:{crafting_cost:100, crafting_materials:[
        {item:{gameId:10, name:'Scale'}, quantity:3}, {item:{gameId:11, name:'Claw'}, quantity:1}
    ]}}], {'game:10':4, 'game:11':100});
    assert.equal(result.cost, 200);
    assert.equal(result.materials[0].required, 6);
    assert.equal(result.materials[0].missing, 2);
    assert.equal(result.materials[1].missing, 0);
});
test('invalid inventory values and prototype keys are discarded', () => {
    const input = JSON.parse('{"__proto__":{"polluted":1}, "game:1":-3, "item:2":1e100, "game:3":"bad"}');
    assert.deepEqual(plan.normalizeInventory(input), {'game:1':0, 'item:2':999999, 'game:3':0});
    assert.deepEqual(plan.normalizeInventory([]), {});
    assert.equal({}.polluted, undefined);
});
test('missing recipes are incomplete, not free materials', () => {
    assert.equal(plan.requirements([{entry:{}, item:{}}]).incomplete, 1);
});
test('inventory survives a JSON round trip without depending on translated names', () => {
    const inventory = plan.normalizeInventory(JSON.parse(JSON.stringify({'game:1':5})));
    const make = name => plan.requirements([{entry:{}, item:{crafting_materials:[{item:{gameId:1,name},quantity:8}]}}], inventory);
    assert.equal(make('Scale').materials[0].missing, make('Escama').materials[0].missing);
    assert.equal(make('Escama').materials[0].missing, 3);
});

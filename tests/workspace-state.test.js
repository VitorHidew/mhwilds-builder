const {test} = require('node:test');
const assert = require('node:assert/strict');
const state = require('../static/js/workspace-state.js');

const draft = () => ({version:1, build:{name:'Test',equipment:{weapon_id:'wpn_1',decorations:['deco_1']},scenario:{monster_id:'m_1'}},slots:{weapon:['','deco_1','']},route:'comparator',optimizer:{'opt-weapon-type':'Great Sword','opt-use-transcendence':true},savedId:'build_1'});

test('route only permits known screens and safely defaults to builder', () => {
    assert.equal(state.route('#/comparator'),'comparator');
    assert.equal(state.route('optimizer'),'optimizer');
    assert.equal(state.route('#/unknown'),'builder');
    assert.equal(state.route('javascript:alert(1)'),'builder');
});
test('draft retains empty slot positions, saved identity and optimizer settings', () => {
    const value=state.decodeDraft(JSON.stringify(draft()));
    assert.deepEqual(value.slots.weapon,['','deco_1','']);
    assert.equal(value.savedId,'build_1');
    assert.equal(value.optimizer['opt-use-transcendence'],true);
    assert.equal(value.route,'comparator');
});
test('malformed and incompatible drafts are rejected without mutating input', () => {
    for(const raw of ['null','[]','{',JSON.stringify({...draft(),version:99}), 'x'.repeat(1000001)]) assert.equal(state.decodeDraft(raw),null);
    const bad=draft(); bad.slots.weapon={x:'deco_1'};
    assert.equal(state.decodeDraft(JSON.stringify(bad)),null);
    bad.slots.weapon=[''];bad.build.equipment.decorations=[null];
    assert.equal(state.decodeDraft(JSON.stringify(bad)),null);
});
test('search ignores accents without changing canonical names', () => {
    assert.equal(state.normalize('Exploração de Fraqueza'),'exploracao de fraqueza');
});
test('baseline comparison reports signed deltas and never divides by zero', () => {
    assert.ok(Math.abs(state.percent(103,100)-3)<0.00001);
    assert.equal(state.percent(50,100),-50);
    assert.equal(state.percent(1,0),null);
    assert.equal(state.percent(Infinity,1),null);
});
test('scenario identity ignores rotation but detects target and uptime changes', () => {
    const scenario={target_part:'head',agitator_uptime:.5,rotation_id:'a'};
    assert.equal(state.scenarioKey(scenario),state.scenarioKey({...scenario,rotation_id:'b'}));
    assert.notEqual(state.scenarioKey(scenario),state.scenarioKey({...scenario,agitator_uptime:.8}));
    assert.notEqual(state.scenarioKey(scenario),state.scenarioKey({...scenario,target_part:'tail'}));
});
test('undo/redo clones snapshots, deduplicates and truncates abandoned branches', () => {
    const h=state.history(3), original=draft();
    h.push(original);original.slots.weapon[0]='external mutation';
    h.push({value:2});assert.equal(h.push({value:2}),false);
    assert.deepEqual(h.undo().slots.weapon,['','deco_1','']);
    assert.equal(h.redo().value,2);
    h.undo();h.push({value:3});assert.equal(h.canRedo,false);
    h.push({value:4});h.push({value:5});
    assert.equal(h.undo().value,4);assert.equal(h.undo().value,3);assert.equal(h.undo(),null);
});

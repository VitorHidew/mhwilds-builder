(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) module.exports = api;
    else root.WorkspaceState = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';
    const screens = new Set(['builder','optimizer','scenario','comparator','wishlist','library','builds','registry','inventory','settings','sources','dashboard','gog','talisman','suggestions']);
    const clone = value => JSON.parse(JSON.stringify(value));
    const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
    function route(hash) {
        const key = String(hash || '').replace(/^#\/?/, '').split('?')[0];
        return screens.has(key) ? key : 'builder';
    }
    function decodeDraft(raw) {
        try {
            if (!raw || raw.length > 1000000) return null;
            const data = JSON.parse(raw);
            if (!data || data.version !== 1 || !data.build?.equipment || !data.build?.scenario) return null;
            if (typeof data.build.equipment.weapon_id !== 'string') return null;
            if (!Array.isArray(data.build.equipment.decorations) || !data.build.equipment.decorations.every(id=>typeof id==='string')) return null;
            if (typeof data.build.scenario.monster_id !== 'string' || typeof data.build.name !== 'string') return null;
            const slots={};
            for (const slot of ['weapon','helm','chest','arms','waist','legs','talisman']) {
                const values=data.slots?.[slot] || [];
                if (!Array.isArray(values) || values.length>6 || !values.every(id=>typeof id==='string')) return null;
                slots[slot]=values;
            }
            const optimizer=Object.fromEntries(Object.entries(data.optimizer || {}).filter(([key,value])=>key.startsWith('opt-') && ['string','boolean'].includes(typeof value)));
            const optimizerSkills=Object.fromEntries(Object.entries(data.optimizerSkills || {}).filter(([name,level])=>name.length<160 && Number.isInteger(level) && level>0 && level<=10));
            return {version:1, build:clone(data.build), slots, route:route(data.route), optimizer, optimizerSkills,
                optimizerScenario:typeof data.optimizerScenario?.monster_id==='string' ? clone(data.optimizerScenario) : null,
                savedId:typeof data.savedId === 'string' ? data.savedId : null};
        } catch { return null; }
    }
    function percent(value, baseline) {
        const current = Number(value), reference = Number(baseline);
        return Number.isFinite(current) && Number.isFinite(reference) && reference > 0 ? (current / reference - 1) * 100 : null;
    }
    function scenarioKey(value) {
        const fields = Object.entries(value || {}).filter(([key]) => key !== 'rotation_id').sort(([a],[b]) => a.localeCompare(b));
        return JSON.stringify(fields);
    }
    function history(limit = 30) {
        let items = [], index = -1;
        return {
            push(value) {
                const serialized = JSON.stringify(value);
                if (items[index] === serialized) return false;
                items = items.slice(0, index + 1);
                items.push(serialized);
                if (items.length > limit) items.shift();
                index = items.length - 1;
                return true;
            },
            undo() { return index > 0 ? JSON.parse(items[--index]) : null; },
            redo() { return index + 1 < items.length ? JSON.parse(items[++index]) : null; },
            get canUndo() { return index > 0; },
            get canRedo() { return index + 1 < items.length; }
        };
    }
    return {route, decodeDraft, percent, scenarioKey, normalize, history};
});

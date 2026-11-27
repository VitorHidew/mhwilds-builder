'use strict';
const MaterialPlan = (() => {
    function quantity(value, fallback = 0) {
        const number = Number(value);
        return Number.isFinite(number) ? Math.max(0, Math.min(999999, Math.floor(number))) : fallback;
    }
    function normalizeInventory(value) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
        return Object.fromEntries(Object.entries(value).filter(([key]) => /^(game|item):\d+$/.test(key))
            .slice(0, 5000).map(([key, amount]) => [key, quantity(amount)]));
    }
    function materialKey(item) {
        if (Number.isInteger(item.gameId)) return `game:${item.gameId}`;
        if (Number.isInteger(item.id)) return `item:${item.id}`;
        return null;
    }
    function requirements(records, inventory = {}) {
        const materials = new Map();
        let cost = 0;
        let incomplete = 0;
        for (const {entry, item} of records) {
            const count = Math.max(1, quantity(entry.quantity, 1));
            cost += quantity(item.crafting_cost) * count;
            const recipe = item.crafting_materials || [];
            if (!recipe.length) incomplete += 1;
            for (const ingredient of recipe) {
                const source = ingredient.item || {};
                const key = materialKey(source);
                if (!key) { incomplete += 1; continue; }
                const row = materials.get(key) || {key, name: source.name || source.name_en || key, required: 0};
                row.required += quantity(ingredient.quantity, 1) * count;
                materials.set(key, row);
            }
        }
        return {cost, incomplete, materials: [...materials.values()].map(row => ({...row,
            owned: quantity(inventory[row.key]), missing: Math.max(0, row.required - quantity(inventory[row.key]))}))};
    }
    function equipmentEntries(equipment = {}) {
        const counts = new Map();
        const slots = [['weapon', equipment.weapon_id], ...['helm', 'chest', 'arms', 'waist', 'legs'].map(slot => ['armor', equipment[`${slot}_id`]]),
            ['talisman', equipment.talisman_id], ...(equipment.decorations || []).map(id => ['decoration', id])];
        for (const [type, id] of slots) {
            if (!id || String(id).includes('_none') || ['custom_gog_weapon', 'custom_talisman'].includes(id)) continue;
            const key = `${type}:${id}`;
            const entry = counts.get(key) || {type, id, quantity: 0};
            entry.quantity += 1;
            counts.set(key, entry);
        }
        return [...counts.values()];
    }
    return {quantity, normalizeInventory, requirements, equipmentEntries};
})();
if (typeof module !== 'undefined' && module.exports) module.exports = MaterialPlan;

// Shared comparison state is deliberately separate from saved snapshots.
let SHARED_COMPARISON = null;
let COMPARISON_REQUEST_ID = 0;
let COMPARISON_INPUT_KEY = '';
let SCENARIO_BASE = {};
let ROTATION_REQUEST_ID = 0;
let OPTIMIZER_REQUEST_ID = 0;
let OPTIMIZER_SCENARIO_BASE = null;
const plannerText = (pt, en) => SITE_LOCALE === 'en' ? en : pt;

function optimizerInputKey() {
    return JSON.stringify([OPTIMIZER_SCENARIO_BASE,
        [...document.querySelectorAll('#screen-optimizer input, #screen-optimizer select')]
            .map(input => [input.id, input.value, input.checked])]);
}

function restoreOptimizerUptimes(scenario) {
    const uptimes = {agi:'agitator', burst:'burst', wex:'weakness_exploit', og:'offensive_guard',
        foray:'foray', adrenaline:'adrenaline_rush', ambush:'ambush', heroics:'heroics',
        frenzy:'frenzy_antivirus', peak:'peak_performance', resentment:'resentment', coal:'coalescence'};
    Object.entries(uptimes).forEach(([id, key]) => { document.getElementById(`opt-up-${id}`).value = Math.round(100 * (scenario[`${key}_uptime`] || 0)); });
    document.querySelectorAll('[data-opt-uptime]').forEach(button => button.classList.remove('active'));
}

function clearComparedRotations() {
    ROTATION_REQUEST_ID += 1;
    ROTATION_COMPARISONS = [];
    for (const id of ['rotation-ranking-container', 'rotation-explanation', 'nerd-stats-container', 'hits-table-body']) {
        document.getElementById(id)?.replaceChildren();
    }
    document.getElementById('hit-engine-title').textContent = plannerText('Detalhamento do combo', 'Combo breakdown');
    const button = document.getElementById('btn-compare-rotations');
    button.disabled = false;
    button.textContent = plannerText('Comparar combos', 'Compare combos');
}

function comparisonInputKey() {
    return JSON.stringify([SITE_LOCALE, currentScenarioPayload(), SAVED_BUILDS,
        document.getElementById('comparison-rotation-mode')?.value]);
}

function comparedBuilds() {
    if (!SHARED_COMPARISON || COMPARISON_INPUT_KEY !== comparisonInputKey()) return [];
    return SHARED_COMPARISON.rows.map(row => ({...row.build, skill_impacts: row.skill_impacts}));
}

async function refreshSharedComparison() {
    if (!GAME_DATA) return;
    const status = document.getElementById('shared-comparison-status');
    const button = document.getElementById('refresh-shared-comparison');
    const key = comparisonInputKey();
    if (SHARED_COMPARISON && COMPARISON_INPUT_KEY === key) {
        renderComparatorTable();
        return;
    }
    const requestId = ++COMPARISON_REQUEST_ID;
    SHARED_COMPARISON = null;
    clearComparedRotations();
    renderComparatorTable();
    if (!SAVED_BUILDS.length) {
        status.textContent = plannerText('Nenhuma build salva.', 'No saved builds.');
        return;
    }
    button.disabled = true;
    status.textContent = plannerText('Recalculando no cenário compartilhado...', 'Recalculating in the shared scenario...');
    try {
        const response = await fetch('/api/builds/compare', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({builds: SAVED_BUILDS, scenario: currentScenarioPayload(),
                rotation_mode: document.getElementById('comparison-rotation-mode').value})
        });
        if (!response.ok) throw new Error(plannerText('Não foi possível comparar as builds.', 'Could not compare builds.'));
        const data = await response.json();
        if (requestId !== COMPARISON_REQUEST_ID || key !== comparisonInputKey()) return;
        SHARED_COMPARISON = data;
        COMPARISON_INPUT_KEY = key;
        const monster = currentMonsterForChart();
        status.textContent = `${monster?.name || '-'} · ${translatePart(data.scenario.target_part)} · ${data.rows.length} builds · ${plannerText('Motor', 'Engine')} ${data.engine_version}`;
        if (data.errors.length) status.textContent += ` · ${data.errors.map(item => `${item.name}: ${item.message}`).join(' | ')}`;
        renderComparatorTable();
        compareSelectedBuildRotations();
    } catch (error) {
        if (requestId === COMPARISON_REQUEST_ID) status.textContent = error.message;
    } finally {
        if (requestId === COMPARISON_REQUEST_ID) button.disabled = false;
    }
}

function skillContribution(build) {
    const impact = build.skill_impacts?.[0];
    return impact
        ? `${skillDisplayName(impact.skill)}: ${impact.dps_delta} DPS (${impact.percent}%)`
        : plannerText('Sem contribuição de habilidade de dano isolada.', 'No isolated damage-skill contribution.');
}

function updatePlannerUI() {
    document.querySelectorAll('[data-planner-pt]').forEach(element => {
        element.textContent = plannerText(element.dataset.plannerPt, element.dataset.plannerEn);
    });
    const count = document.getElementById('comparator-nav-count');
    if (count) count.textContent = String(SAVED_BUILDS.length);
    const context = document.getElementById('hunt-context');
    if (context && GAME_DATA) {
        const monster = currentMonsterForChart();
        context.textContent = `${monster?.name || '-'} · ${translatePart(document.getElementById('scenario-part').value)}`;
    }
    if (typeof updateWorkspaceContext === 'function' && GAME_DATA) updateWorkspaceContext();
}

function onPlannerScreen(screenId) {
    updatePlannerUI();
    if (screenId === 'comparator') refreshSharedComparison();
}

function loadMaterialInventory() {
    try { return MaterialPlan.normalizeInventory(JSON.parse(localStorage.getItem('mhwilds_material_inventory') || '{}')); }
    catch { return {}; }
}

function setMaterialOwned(key, value) {
    const inventory = loadMaterialInventory();
    inventory[key] = MaterialPlan.quantity(value);
    try {
        localStorage.setItem('mhwilds_material_inventory', JSON.stringify(MaterialPlan.normalizeInventory(inventory)));
        const focused = document.activeElement?.getAttribute('aria-label');
        renderWishlist();
        if (focused) [...document.querySelectorAll('#wishlist-materials input')].find(input => input.getAttribute('aria-label') === focused)?.focus({preventScroll:true});
    } catch {
        const status = document.getElementById('material-status');
        if (status) status.textContent = plannerText('Não foi possível salvar neste navegador.', 'Could not save in this browser.');
    }
}

function renderMaterialPlan(records, container) {
    const plan = MaterialPlan.requirements(records, loadMaterialInventory());
    const rows = plan.materials.sort((a, b) => a.name.localeCompare(b.name, SITE_LOCALE === 'en' ? 'en' : 'pt-BR'));
    const missing = rows.reduce((total, row) => total + row.missing, 0);
    const required = rows.reduce((total, row) => total + row.required, 0);
    const completion = required ? Math.round(100 * (required - missing) / required) : 0;
    container.innerHTML = `<div class="material-summary"><strong>${plannerText('Materiais faltantes', 'Missing materials')}: ${missing}</strong><span>${completion}% · ${plan.cost.toLocaleString()}z</span></div>
        <progress class="material-progress" max="100" value="${completion}" aria-label="${plannerText('Materiais reunidos', 'Materials collected')}"></progress>
        <div class="material-table-wrap"><table class="material-table"><thead><tr><th>${plannerText('Material', 'Material')}</th><th>${plannerText('Precisa', 'Required')}</th><th>${plannerText('Tenho', 'Owned')}</th><th>${plannerText('Falta', 'Missing')}</th></tr></thead><tbody></tbody></table></div>
        <p id="material-status" class="metric-note" aria-live="polite">${plan.incomplete ? plannerText('Total parcial: há itens sem receita cadastrada. Reforços aleatórios e etapas anteriores de upgrade não estão incluídos.', 'Partial total: some recipes are unavailable. Random reinforcement costs and earlier upgrade steps are not included.') : plannerText('Receitas da etapa selecionada; upgrades anteriores não incluídos.', 'Recipes for the selected upgrade step; earlier upgrades not included.')}</p>`;
    const body = container.querySelector('tbody');
    rows.forEach(row => {
        if (document.getElementById('only-missing-materials')?.checked && !row.missing) return;
        const tr = document.createElement('tr');
        tr.className = row.missing ? '' : 'material-complete';
        tr.append(createUiElement('td', '', row.name), createUiElement('td', '', row.required));
        const owned = document.createElement('td');
        const input = document.createElement('input');
        Object.assign(input, {type: 'number', min: '0', max: '999999', step: '1', value: row.owned});
        input.setAttribute('aria-label', `${plannerText('Tenho', 'Owned')}: ${row.name}`);
        input.addEventListener('change', () => setMaterialOwned(row.key, input.value));
        if (typeof uxButton === 'function') {
            const stepper = createUiElement('div', 'material-stepper');
            const decrease = uxButton('-', () => setMaterialOwned(row.key, row.owned - 1), 'icon-button');
            decrease.setAttribute('aria-label', plannerText('Diminuir ', 'Decrease ') + row.name);
            const increase = uxButton('+', () => setMaterialOwned(row.key, row.owned + 1), 'icon-button');
            increase.setAttribute('aria-label', plannerText('Aumentar ', 'Increase ') + row.name);
            stepper.append(decrease, input, increase); owned.append(stepper);
        } else owned.append(input);
        tr.append(owned, createUiElement('td', '', row.missing));
        body.append(tr);
    });
}

function optimizerEvidence(build) {
    const stats = build.search_stats || {};
    const version = build.result?.engine_version || 'legacy';
    if (build.provenance?.needs_search_refresh) return plannerText('Cache antigo recalculado; busca ainda não atualizada.', 'Legacy cache recalculated; search not yet refreshed.');
    if (!stats.evaluated) return `${plannerText('Cobertura de busca não registrada', 'Search coverage not recorded')} · ${version}`;
    return `${stats.cache_hit ? plannerText('Pré-calculada', 'Precalculated') : plannerText('Busca atual', 'Current search')} · ${stats.evaluated} ${plannerText('avaliações', 'evaluations')} · ${stats.weapon_count} ${plannerText('armas', 'weapons')} · ${plannerText('busca limitada', 'bounded search')}${stats.portfolio_runs ? ` · ${stats.portfolio_runs.length} ${plannerText('buscas comparadas', 'compared searches')}` : ''} · ${version}`;
}

function useHuntScenarioInOptimizer() {
    const scenario = currentScenarioPayload();
    if (scenario.custom_monster) {
        document.getElementById('optimizer-scenario-status').textContent = plannerText('Alvo personalizado: use o Montador e o Comparador.', 'Custom target: use the Builder and Comparator.');
        return;
    }
    setSelectValue('opt-monster-id', scenario.monster_id);
    populateOptimizerParts(scenario.target_part);
    OPTIMIZER_SCENARIO_BASE = structuredClone(scenario);
    restoreOptimizerUptimes(scenario);
    if (typeof WORKSPACE_READY !== 'undefined' && WORKSPACE_READY) {
        OPTIMIZER_REQUEST_ID += 1;
        OPTIMIZER_RESULTS = [];
        renderOptimizerResults();
    }
    document.getElementById('optimizer-scenario-status').textContent = plannerText('Alvo, parte e uptimes aplicados.', 'Target, part and uptimes applied.');
    if (typeof updateWorkspaceContext === 'function') updateWorkspaceContext();
}

function restoreScenarioDetails(scenario) {
    SCENARIO_BASE = structuredClone(scenario);
    const names = {agi:'agitator', burst:'burst', wex:'weakness_exploit', maxmight:'maximum_might',
        peak:'peak_performance', og:'offensive_guard', counter:'counterstrike', coal:'coalescence',
        latent:'latent_power', frenzy:'frenzy_antivirus', seed:'might_seed', powder:'demon_powder',
        mantle:'mantle', resentment:'resentment', eleabsorb:'elemental_absorption', adrenaline:'adrenaline_rush',
        foray:'foray', ambush:'ambush', heroics:'heroics'};
    Object.entries(names).forEach(([id,key]) => {
        const input = document.getElementById(`uptime-${id}`);
        if (input) input.value = Math.round(100 * (scenario[`${key}_uptime`] || 0));
    });
    const custom = scenario.custom_monster;
    document.getElementById('use-custom-monster').checked = Boolean(custom);
    document.getElementById('custom-monster-editor').style.display = custom ? 'block' : 'none';
    if (custom) {
        document.getElementById('custom-monster-name').value = custom.name;
        for (const key of ['sever','blunt','shot','fire','water','thunder','ice','dragon']) {
            document.getElementById(`custom-hz-${key}`).value = custom.weighted_hitzone[key];
        }
    }
    renderMonsterIdentity(currentMonsterForChart());
    renderMonsterIntel();
}

document.addEventListener('change', event => {
    if (event.target.closest('#screen-scenario')) {
        COMPARISON_REQUEST_ID += 1;
        SHARED_COMPARISON = null;
        clearComparedRotations();
        document.getElementById('refresh-shared-comparison').disabled = false;
        updatePlannerUI();
        const status = document.getElementById('shared-comparison-status');
        if (status) status.textContent = plannerText('Cenário alterado; comparação pendente.', 'Scenario changed; comparison pending.');
    }
});

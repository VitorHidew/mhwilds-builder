/* Interaction layer. Calculation payloads and saved snapshots remain owned by app.js. */
'use strict';
let WORKSPACE_READY = false;
let WORKSPACE_RESTORING = false;
let ACTIVE_SCREEN = 'builder';
let EDITING_BUILD_ID = null;
let VISUAL_ASSETS = {};
let WORKSPACE_TIMER = null;
let PREVIOUS_DPS = null;
let LAST_RESULT_KEY = '';
let LAST_SCENARIO_KEY = '';
let PICKER = null;
let DIALOG_ORIGIN = null;
let DIALOG_NODE = null;
let DIALOG_PLACEHOLDER = null;
let WIKI_TRAIL = [];
let COMPARISON_BASELINE = '';
let COMPARISON_SELECTED = null;
const WORKSPACE_HISTORY = WorkspaceState.history();
const UX_SLOTS = ['weapon','helm','chest','arms','waist','legs','talisman'];
const UX_UPTIMES = {agi:'Agitator',burst:'Burst',wex:'Weakness Exploit',maxmight:'Maximum Might',peak:'Peak Performance',og:'Offensive Guard',counter:'Counterstrike',coal:'Coalescence',latent:'Latent Power',frenzy:'Antivirus',resentment:'Resentment',eleabsorb:'Elemental Absorption',adrenaline:'Adrenaline Rush',foray:'Foray',ambush:'Ambush',heroics:'Heroics'};
const UX_TRANSLATIONS = new Map();
const ux = (pt,en) => { UX_TRANSLATIONS.set(pt,[pt,en]); UX_TRANSLATIONS.set(en,[pt,en]); return SITE_LOCALE === 'en' ? en : pt; };
const uxNode = (tag,cls,text) => createUiElement(tag,cls,text);
const uxIcon = name => { const icon = document.createElement('i'); icon.dataset.lucide = name; return icon; };
const uxButton = (label,handler,cls='btn btn-secondary',icon='') => {
    const button = createActionButton(label,cls,handler);
    if (icon) button.prepend(uxIcon(icon));
    return button;
};
function refreshIcons() { window.lucide?.createIcons({attrs:{'aria-hidden':'true'}}); }
function uxMessage(message) {
    const box = document.getElementById('workspace-toast');
    box.textContent = message; box.hidden = false;
    clearTimeout(box.hideTimer);
    box.hideTimer = setTimeout(() => { box.hidden = true; }, 6000);
}
function translateExperience() {
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    while(walker.nextNode()) {
        const node=walker.currentNode;
        if(node.parentElement?.closest('script,style,input,textarea'))continue;
        const pair=UX_TRANSLATIONS.get(node.textContent.trim());
        if(pair)node.textContent=SITE_LOCALE==='en'?pair[1]:pair[0];
    }
    document.querySelectorAll('[data-ux-pt]').forEach(node => { node.textContent = ux(node.dataset.uxPt,node.dataset.uxEn); });
    document.querySelectorAll('[data-ux-title-pt]').forEach(node => {
        const label = ux(node.dataset.uxTitlePt,node.dataset.uxTitleEn);
        node.title = label; node.setAttribute('aria-label',label);
    });
    document.querySelectorAll('label:not([for])').forEach(label => {
        if (label.querySelector('input,select')) return;
        const input = label.parentElement.querySelector('input,select,textarea');
        if (input?.id) label.htmlFor = input.id;
    });
    document.querySelectorAll('input:not([aria-label]),select:not([aria-label])').forEach(input => {
        if (!input.labels?.length) input.setAttribute('aria-label',input.placeholder || input.id || ux('Valor','Value'));
    });
    const search = document.getElementById('saved-build-search');
    search.placeholder = ux('Pesquisar builds','Search builds'); search.setAttribute('aria-label',search.placeholder);
    document.getElementById('dialog-back').title = ux('Definição anterior','Previous definition');
    const sharpnessLabels={white:['Branco','White'],purple:['Roxo','Purple'],blue:['Azul','Blue'],green:['Verde','Green'],yellow:['Amarelo','Yellow']};
    for(const id of ['gog-sharp','gog-prev-sharp']) {
        for(const option of document.getElementById(id).options) {
            const label=sharpnessLabels[option.value.toLowerCase()];
            if(label)option.textContent=ux(...label)+(option.textContent.match(/\s*\([^)]+\)/)?.[0] || '');
        }
    }
    const blast=document.querySelector('#gog-ele-type option[value="Blast"]');
    if(blast)blast.textContent=ux('Explosão','Blast');
    for(const id of ['opt-weapon-type','gog-type']) {
        const select=document.getElementById(id);
        for(const option of select?.options || []) {
            if(!option.hasAttribute('value'))option.value=option.textContent;
            option.textContent=weaponTypeDisplay({weapon_type:option.value});
        }
    }
    document.querySelectorAll('.opt-skill-name').forEach(input=>{input.placeholder=ux('Pesquisar habilidade...','Search skill...');input.setAttribute('aria-label',input.placeholder);});
    refreshIcons();
}
function routeChanged(screenId, fromHistory=false) {
    if (!document.getElementById(`screen-${screenId}`)) return;
    ACTIVE_SCREEN = screenId;
    const group = screenId === 'builds' ? 'builds' : ['library','registry','inventory','settings','sources'].includes(screenId) ? 'library' : 'hunt';
    document.querySelectorAll('[data-route-group]').forEach(button => {
        if (button.dataset.routeGroup === group) button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current');
    });
    document.querySelectorAll('.hunt-flow [data-route]').forEach(button => {
        if (button.dataset.route === (screenId === 'optimizer' ? 'builder' : screenId)) button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current');
    });
    const titles = {builder:['Sua caçada','Your hunt'],optimizer:['Encontrar uma build','Find a build'],scenario:['Conheça seu alvo','Know your target'],comparator:['Compare suas opções','Compare your options'],wishlist:['Prepare o equipamento','Prepare your equipment'],builds:['Minhas builds','My builds'],library:['Biblioteca','Library'],registry:['Wiki do caçador','Hunter wiki'],settings:['Preferências','Preferences'],inventory:['Seus talismãs','Your talismans'],sources:['Fontes e limites','Sources and limits'],dashboard:['Resumo da caçada','Hunt overview']};
    document.getElementById('workspace-title').textContent = ux(...(titles[screenId] || ['Sua caçada','Your hunt']));
    document.querySelector('.hunt-flow').hidden = group !== 'hunt';
    document.querySelector('.hunt-context-bar').hidden = group !== 'hunt';
    document.querySelector('.app-topbar').hidden = screenId !== 'builder';
    if (!fromHistory && location.hash !== `#/${screenId}`) history.pushState(null,'',`#/${screenId}`);
    if (screenId === 'builds') renderBuildLibrary();
    updateWorkspaceContext();
    if (WORKSPACE_READY) {
        saveWorkspaceDraft(false);
        const main = document.getElementById('workspace-main');
        main.scrollTop = 0;
        main.focus({preventScroll:true});
    }
}
function optimizerScenario() {
    const scenario = {...(OPTIMIZER_SCENARIO_BASE || currentScenarioPayload()), custom_monster:null,
        monster_id:document.getElementById('opt-monster-id').value,
        target_part:document.getElementById('opt-target-part').value || 'Media_Ponderada',
        rotation_id:document.getElementById('opt-rotation-id').value || null};
    const keys = {agi:'agitator',burst:'burst',wex:'weakness_exploit',og:'offensive_guard',foray:'foray',adrenaline:'adrenaline_rush',ambush:'ambush',heroics:'heroics',frenzy:'frenzy_antivirus',peak:'peak_performance',resentment:'resentment',coal:'coalescence'};
    for (const [id,key] of Object.entries(keys)) scenario[`${key}_uptime`] = pct(`opt-up-${id}`);
    return scenario;
}
function updateWorkspaceContext() {
    if (!GAME_DATA) return;
    const isOptimizer = ACTIVE_SCREEN === 'optimizer';
    const scenario = isOptimizer ? optimizerScenario() : currentScenarioPayload();
    const monster = scenario.custom_monster || GAME_DATA.monsters.find(item=>item.id === scenario.monster_id);
    const selectedWeapon = equipmentPreviewItems()[0].item;
    const type = isOptimizer ? document.getElementById('opt-weapon-type').value : selectedWeapon?.weapon_type;
    const mismatch = isOptimizer && WorkspaceState.scenarioKey(scenario) !== WorkspaceState.scenarioKey(currentScenarioPayload());
    document.getElementById('hunt-context-title').textContent = monsterDisplayName(monster);
    document.getElementById('hunt-context-detail').textContent = [weaponTypeDisplay({weapon_type:type}), translatePart(scenario.target_part),
        mismatch ? ux('Cenário da recomendação','Recommendation scenario') : ux('Cenário da caçada','Hunt scenario')].filter(Boolean).join(' · ');
    renderMonsterImage(document.getElementById('hunt-context-photo'),monster);
    const status = document.getElementById('optimizer-scenario-status');
    status.textContent = mismatch ? ux('Esta recomendação tem condições diferentes da caçada atual.','This recommendation has different conditions from your current hunt.') : ux('Mesmo alvo e condições da caçada.','Same target and conditions as the hunt.');
    document.getElementById('adopt-optimizer-scenario').hidden = !mismatch;
}
function toggleWoundBonusVisibility() {
    const checked = !!document.getElementById('scenario-wound')?.checked;
    const wrap = document.getElementById('scenario-wound-bonus-wrap');
    if (wrap) wrap.hidden = !checked;
}
function renderMonsterGallery() {
    const strip = document.getElementById('monster-gallery-strip');
    if (!strip || !GAME_DATA?.monsters) return;
    const query = WorkspaceState.normalize(document.getElementById('monster-gallery-search')?.value || '');
    const selectedId = document.getElementById('scenario-monster')?.value || '';
    const monsters = GAME_DATA.monsters.filter(m => !query || WorkspaceState.normalize(`${monsterDisplayName(m)} ${m.name_en || ''}`).includes(query));
    strip.replaceChildren();
    monsters.forEach(monster => {
        const card = uxButton('', () => {
            setSelectValue('scenario-monster', monster.id);
            document.getElementById('use-custom-monster').checked = false;
            onMonsterChange();
            renderMonsterGallery();
            renderPartTable();
        }, 'monster-card-btn');
        card.setAttribute('role', 'option');
        const isSelected = monster.id === selectedId;
        card.setAttribute('aria-selected', String(isSelected));
        if (isSelected) card.classList.add('active');
        const art = uxNode('div', 'monster-card-art');
        renderMonsterImage(art, monster);
        const bestEle = bestElementForPart(monster.weighted_hitzone || {});
        const label = uxNode('span', 'monster-card-name', monsterDisplayName(monster));
        const sub = uxNode('small', 'monster-card-weakness', bestEle?.[0] || '');
        card.append(art, label, sub);
        strip.append(card);
    });
}
function buildGearStrip(build) {
    const strip = uxNode('div', 'build-gear-strip');
    const equip = build?.equipment || {};
    const weapon = equip.custom_weapon || GAME_DATA?.weapons?.find(w => w.id === equip.weapon_id);
    const entries = [
        ['weapon', weapon, 'weapon'],
        ...['helm', 'chest', 'arms', 'waist', 'legs'].map(slot => ['armor', GAME_DATA?.armors?.find(a => a.id === equip[`${slot}_id`]), slot]),
    ];
    entries.forEach(([kind, item, slot]) => {
        if (!item || String(item.id || '').includes('_none')) return;
        const thumb = uxNode('span', 'gear-strip-item');
        thumb.title = displayName(item);
        const src = equipVisualSrc(kind, item, slot);
        if (src) {
            const img = document.createElement('img');
            img.src = src; img.alt = displayName(item); img.loading = 'lazy'; img.decoding = 'async';
            img.onerror = () => img.remove();
            thumb.append(img);
        }
        strip.append(thumb);
    });
    const monster = GAME_DATA?.monsters?.find(m => m.id === build?.scenario?.monster_id);
    if (monster) {
        const mThumb = uxNode('span', 'gear-strip-item gear-strip-monster');
        mThumb.title = monsterDisplayName(monster);
        renderMonsterImage(mThumb, monster);
        strip.append(mThumb);
    }
    return strip;
}
function applyHuntScenario(scenario) {
    setSelectValue('scenario-monster',scenario.monster_id);
    onMonsterChange();
    setSelectValue('scenario-part',scenario.target_part || 'Media_Ponderada');
    document.getElementById('scenario-wound').checked = !!scenario.wound_active;
    if (document.getElementById('scenario-wound-bonus')) {
        document.getElementById('scenario-wound-bonus').value = String(scenario.wound_hitzone_bonus ?? 0);
    }
    toggleWoundBonusVisibility();
    restoreScenarioDetails(scenario);
    CURRENT_ROTATION_ID = scenario.rotation_id || null;
    invalidateComparison();
    recalculate();
    updateWorkspaceContext();
    renderMonsterGallery();
}
function adoptOptimizerScenario() {
    applyHuntScenario(optimizerScenario());
    saveWorkspaceDraft();
    uxMessage(ux('Condições aplicadas à caçada.','Conditions applied to the hunt.'));
}
function invalidateComparison() {
    SHARED_COMPARISON = null; COMPARISON_REQUEST_ID += 1; clearComparedRotations();
    document.getElementById('refresh-shared-comparison').disabled = false;
    updateComparisonExperience([]);
}
function snapshotWorkspace() {
    const build = currentBuildPayload('draft'); build.result = null;
    const slots = Object.fromEntries(UX_SLOTS.map(slot=>[slot,[...document.querySelectorAll(`#slots-${slot} .deco-select`)].map(input=>input.value)]));
    return {version:1, build, slots, savedId:EDITING_BUILD_ID};
}
function snapshotOptimizer() {
    return {
        optimizer:Object.fromEntries([...document.querySelectorAll('#screen-optimizer input[id],#screen-optimizer select[id]')].map(input=>[input.id,input.type==='checkbox'?input.checked:input.value])),
        optimizerSkills:collectOptimizerSkills(),optimizerScenario:optimizerScenario()
    };
}
function restoreOptimizerSnapshot(data) {
    if(!data?.optimizer)return;
    if(data.optimizer['opt-weapon-type']) {setSelectValue('opt-weapon-type',data.optimizer['opt-weapon-type']);populateOptimizerWeapons();}
    if(data.optimizer['opt-monster-id']) {setSelectValue('opt-monster-id',data.optimizer['opt-monster-id']);populateOptimizerParts();}
    for(const [id,value] of Object.entries(data.optimizer)) {
        const input=document.getElementById(id);
        if(!input?.closest('#screen-optimizer') || input.tagName==='BUTTON')continue;
        if(input.type==='checkbox')input.checked=!!value;
        else if(input.tagName!=='SELECT' || [...input.options].some(option=>option.value===value))input.value=value;
    }
    if(data.optimizerScenario)OPTIMIZER_SCENARIO_BASE=data.optimizerScenario;
    if(data.optimizerSkills) {document.getElementById('opt-skill-targets').replaceChildren();Object.entries(data.optimizerSkills).forEach(([name,level])=>addOptimizerSkillRow(name,level));}
    updateWorkspaceContext();
}
function saveWorkspaceDraft(checkpoint=true) {
    if (!WORKSPACE_READY || WORKSPACE_RESTORING || !GAME_DATA) return;
    const data = snapshotWorkspace();
    if (checkpoint) WORKSPACE_HISTORY.push(data);
    data.route = ACTIVE_SCREEN;
    Object.assign(data,snapshotOptimizer());
    try {
        localStorage.setItem('mhwilds_workspace_v1',JSON.stringify(data));
        document.getElementById('draft-status').textContent = ux('Rascunho neste navegador','Draft in this browser');
    } catch {
        document.getElementById('draft-status').textContent = ux('Rascunho não salvo','Draft not saved');
        uxMessage(ux('Armazenamento indisponível. Exporte um backup antes de fechar.','Storage unavailable. Export a backup before closing.'));
    }
    updateUndoButtons();
}
function updateUndoButtons() {
    document.getElementById('undo-build').disabled = !WORKSPACE_HISTORY.canUndo;
    document.getElementById('redo-build').disabled = !WORKSPACE_HISTORY.canRedo;
}
async function restoreWorkspaceSnapshot(data) {
    WORKSPACE_RESTORING = true;
    try {
        await applyBuildEquipment(data.build,false);
        for (const slot of UX_SLOTS) {
            const selects = [...document.querySelectorAll(`#slots-${slot} .deco-select`)];
            (data.slots[slot] || []).forEach((value,index)=>{ if (selects[index] && [...selects[index].options].some(option=>option.value===value)) selects[index].value=value; });
        }
        EDITING_BUILD_ID = data.savedId || null;
        refreshSlotPickers();
        await runRecalculate();
    } finally { WORKSPACE_RESTORING = false; updateUndoButtons(); }
}
async function undoWorkspace() { const data = WORKSPACE_HISTORY.undo(); if (data) { await restoreWorkspaceSnapshot(data); saveWorkspaceDraft(false); } }
async function redoWorkspace() { const data = WORKSPACE_HISTORY.redo(); if (data) { await restoreWorkspaceSnapshot(data); saveWorkspaceDraft(false); } }
async function loadVisualAssets() {
    if (Object.keys(VISUAL_ASSETS).length) return VISUAL_ASSETS;
    try {
        const response = await fetch('/assets/catalog/manifest.json');
        if (response.ok) VISUAL_ASSETS = await response.json();
    } catch { /* Existing icon fallbacks remain usable offline. */ }
    return VISUAL_ASSETS;
}
async function startWorkspace() {
    await loadVisualAssets();
    if (!GAME_DATA) {
        document.getElementById('hunt-context-title').textContent = ux('Catálogo indisponível','Catalog unavailable');
        document.getElementById('hunt-context-detail').replaceChildren(uxButton(ux('Tentar novamente','Try again'),async()=>{await loadGameData();await startWorkspace();}));
        return;
    }
    let draft = null;
    try { draft = WorkspaceState.decodeDraft(localStorage.getItem('mhwilds_workspace_v1')); } catch {}
    if (draft) {
        try { await restoreWorkspaceSnapshot(draft); } catch {
            try { localStorage.setItem('mhwilds_workspace_recovery',JSON.stringify(draft)); } catch {}
            uxMessage(ux('Falha ao restaurar o rascunho. Verifique seus equipamentos antes de salvar.','Draft restore failed. Check your equipment before saving.'));
        }
    }
    WORKSPACE_READY = true;
    WORKSPACE_HISTORY.push(snapshotWorkspace());
    useHuntScenarioInOptimizer();
    restoreOptimizerSnapshot(draft);
    renderEquipmentRows(); renderMonsterIdentity(currentMonsterForChart()); renderDashboard();
    renderMonsterGallery(); toggleWoundBonusVisibility();
    renderOptimizerResults();
    prepareUptimes(); renderPartTable(); translateExperience();
    showScreen(WorkspaceState.route(location.hash || draft?.route));
    saveWorkspaceDraft(false);
}
function localAsset(kind,name) { const record = VISUAL_ASSETS[`${kind}:${name}`] || VISUAL_ASSETS[`${kind}:${String(name).toLowerCase()}`]; return record?.path?.startsWith('/assets/catalog/') ? record.path : ''; }
function renderMonsterImage(box,monster) {
    if (!box) return;
    const name = monster?.name_en || monster?.name;
    const source = localAsset('monster',name) || (monster?.id !== 'custom_monster' ? monsterIconFiles(name)[0] : '');
    if (box.dataset.source === source && box.childElementCount) return;
    box.dataset.source = source || '';
    box.replaceChildren();
    if (!source) { box.append(uxNode('span','metric-note',monsterDisplayName(monster))); return; }
    const img = document.createElement('img'); img.src=source; img.alt=monsterDisplayName(monster); img.decoding='async';
    img.onerror=()=>{if(img.parentElement!==box)return;img.remove();box.append(uxNode('span','metric-note',ux('Imagem indisponível','Image unavailable')));};
    box.append(img);
}
function equipVisualSrc(kind, item, slotType = '') {
    if (!item) {
        const icon = kind === 'weapon' ? weaponIconFiles('Great Sword')[0] : kind === 'armor' ? armorIconFiles(slotType)[0] : 'MH3icon-Accessory.png';
        return icon ? wikiFileUrl(icon) : '';
    }
    if (kind === 'decoration') {
        const sk = item.skill || Object.keys(item.skills || {})[0] || '';
        return sk ? `/api/equipment-photo/skill?name=${encodeURIComponent(sk)}` : wikiFileUrl('MH3icon-Accessory.png');
    }
    if (kind === 'talisman') return wikiFileUrl('MH3icon-Accessory.png');
    const src = equipmentPhotoSrc({ kind, slotType, item, is_gog: item.id === 'custom_gog_weapon' });
    if (src) return src;
    const fallbackFiles = kind === 'weapon' ? weaponIconFiles(item.weapon_type) : armorIconFiles(slotType || item.slot_type);
    return fallbackFiles[0] ? wikiFileUrl(fallbackFiles[0]) : '';
}
function equipMetaSummary(kind, item) {
    if (!item || String(item.id || '').includes('_none')) return '';
    if (kind === 'weapon') {
        const ele = item.element_type && item.element_type !== 'None'
            ? `${item.element_type} ${item.element_display || Math.round((item.element_val || 0) * 10)}`
            : ux('Sem elemento', 'No element');
        const aff = Number(item.affinity || 0);
        return `R${item.rarity || '-'} · Raw ${item.raw ?? '-'} · ${aff >= 0 ? '+' : ''}${aff}% · ${ele}`;
    }
    if (kind === 'armor') {
        const slots = (item.slots || []).length ? item.slots.map(s => `[${s}]`).join('') : ux('Sem slots', 'No slots');
        return `R${item.rarity || '-'} · Def ${item.defense_base ?? '-'} · ${slots}`;
    }
    if (kind === 'talisman') {
        const slots = (item.slots || []).length ? item.slots.map(s => `[${s}]`).join('') : '';
        return slots ? `${ux('Talismã', 'Talisman')} · ${slots}` : ux('Talismã', 'Talisman');
    }
    return '';
}
function renderLoadoutVisualStrip(items) {
    const strip = document.getElementById('loadout-visual-strip');
    if (!strip) return;
    strip.replaceChildren();
    items.forEach((entry, index) => {
        const slot = UX_SLOTS[index];
        const tile = uxButton('', () => openEquipmentPicker(slot), 'loadout-tile');
        const isEmpty = !entry.item || String(entry.item.id || '').includes('_none');
        tile.classList.toggle('is-empty', isEmpty);
        tile.title = `${entry.label}: ${displayName(entry.item) || ux('Nenhum', 'None')}`;
        const src = equipVisualSrc(entry.kind, isEmpty ? null : entry.item, slot);
        const fallbackFiles = entry.kind === 'weapon' ? weaponIconFiles(entry.item?.weapon_type) : entry.kind === 'armor' ? armorIconFiles(slot) : ['MH3icon-Accessory.png'];
        const fallback = fallbackFiles[0] ? wikiFileUrl(fallbackFiles[0]) : '';
        if (src) {
            const img = document.createElement('img');
            img.src = src; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
            img.onerror = () => { if (fallback && img.getAttribute('src') !== fallback) img.src = fallback; else img.remove(); };
            tile.append(img);
        }
        const cap = uxNode('span', 'loadout-tile-label', entry.label);
        tile.append(cap);
        strip.append(tile);
    });
}
function renderEquipmentRows() {
    if (!GAME_DATA) return;
    const previewItems = equipmentPreviewItems();
    renderLoadoutVisualStrip(previewItems);
    previewItems.forEach((entry,index)=>{
        const slot = UX_SLOTS[index], select=document.getElementById(`sel-${slot}`), row=select.closest('.equip-row');
        if (!row) return;
        let photo=row.querySelector('.equip-photo');
        if (!photo) {
            photo=uxNode('div','equip-photo'); row.prepend(photo); select.classList.add('native-equipment-select');
            const button=uxButton('',()=>openEquipmentPicker(slot),'equip-select-button'); button.id=`pick-${slot}`; row.insertBefore(button,select);
            const skills=uxNode('div','equip-piece-skills'); row.insertBefore(skills,row.querySelector('.deco-slots-row'));
        }
        const name=displayName(entry.item) || ux('Nenhum','None'), source=equipmentPhotoSrc(entry);
        const fallbackFiles=entry.kind==='weapon' ? weaponIconFiles(entry.item?.weapon_type) : entry.kind==='armor' ? armorIconFiles(slot) : ['MH3icon-Accessory.png'];
        const fallback=fallbackFiles[0] ? wikiFileUrl(fallbackFiles[0]) : '';
        if (photo.dataset.source !== (source || fallback)) {
            photo.dataset.source=source || fallback; photo.replaceChildren(); photo.classList.toggle('empty',!source);
            if (source || fallback) {
                const img=document.createElement('img'); img.src=source || fallback; img.alt=name; img.loading='lazy'; img.decoding='async';
                img.onerror=()=>{if (fallback && img.getAttribute('src') !== fallback) {img.src=fallback;img.className='game-icon';} else img.remove();};
                photo.append(img);
            }
        }
        if(photo.querySelector('img'))photo.querySelector('img').alt=name;
        const rarity = entry.item?.rarity;
        photo.dataset.rarity = rarity ? String(rarity) : '';
        const button=document.getElementById(`pick-${slot}`); button.replaceChildren(uxNode('span','',name),uxIcon('chevrons-up-down'));
        button.setAttribute('aria-label',`${entry.label}: ${name}`);
        const skillText=Object.entries(entry.item?.skills || {}).map(([name,level])=>`${skillDisplayName(name)} ${level}`).join(' · ');
        const metaText = equipMetaSummary(entry.kind, entry.item);
        const skills=row.querySelector('.equip-piece-skills');
        skills.replaceChildren();
        if (metaText) skills.append(uxNode('span', 'equip-meta-pill', metaText));
        if (skillText) skills.append(uxNode('span', 'equip-skill-line', skillText));
        if (slot==='weapon' || slot==='talisman') {
            skills.append(uxButton(ux('Personalizar','Customize'),()=>openEditor(slot==='weapon'?'gog':'talisman'),'text-button'));
        }
    });
    refreshSlotPickers(); refreshIcons();
}
function refreshSlotPickers() {
    document.querySelectorAll('.deco-select').forEach((select,index)=>{
        select.hidden=true;
        select.id=`deco-field-${index}`;
        let button=select.parentElement.querySelector('.deco-picker');
        if (!button) { button=uxButton('',()=>openDecorationPicker(select),'deco-picker'); select.parentElement.append(button); }
        const text=select.selectedOptions[0]?.textContent || ux('Vazio','Empty');
        button.replaceChildren(uxNode('span','',text),uxIcon('plus'));
        button.setAttribute('aria-label',`${ux('Adorno','Decoration')} ${index+1}: ${text}`);
    });
}
function itemSearchText(item,label) {
    return WorkspaceState.normalize([label,item?.name_en,...Object.keys(item?.skills || {}),...Object.keys(item?.skills || {}).map(skillDisplayName),item?.skill,skillDisplayName(item?.skill || '')].join(' '));
}
function openEquipmentPicker(slot) {
    const select=document.getElementById(`sel-${slot}`);
    const collection=slot==='weapon' ? [customGogPreview(),...GAME_DATA.weapons] : slot==='talisman' ? [customTalismanPreview(),...GAME_DATA.talismans] : GAME_DATA.armors;
    const items=[...select.options].map(option=>{const item=collection.find(item=>item?.id===option.value);return {value:option.value,label:option.textContent,item,search:itemSearchText(item,option.textContent)};});
    openPicker(select,items,ux('Escolher equipamento','Choose equipment'),slot);
}
function openDecorationPicker(select) {
    const items=[...select.options].map(option=>{const item=DECORATION_BY_ID.get(option.value);return {value:option.value,label:option.textContent,item,search:itemSearchText(item,option.textContent)};});
    openPicker(select,items,ux('Escolher adorno','Choose decoration'),'decoration');
}
function openPicker(select,items,title,kind) {
    PICKER={select,items,kind,choice:null,visible:[],focus:-1,origin:document.activeElement};
    document.getElementById('picker-title').textContent=title;
    const input=document.getElementById('picker-search'); input.value=''; input.placeholder=ux('Nome ou habilidade','Name or skill'); input.setAttribute('aria-label',input.placeholder);
    document.getElementById('picker-apply').disabled=true;
    document.getElementById('picker-preview').textContent=ux('Atual: ','Current: ')+(select.selectedOptions[0]?.textContent || ux('Nenhum','None'));
    filterPicker(); document.getElementById('equipment-picker').showModal(); input.focus();
}
function filterPicker() {
    if (!PICKER) return;
    const query=WorkspaceState.normalize(document.getElementById('picker-search').value).split(/\s+/).filter(Boolean);
    const matches=PICKER.items.filter(item=>query.every(term=>item.search.includes(term)));
    PICKER.visible=matches.slice(0,80); PICKER.focus=-1;
    document.getElementById('picker-search').removeAttribute('aria-activedescendant');
    document.getElementById('picker-count').textContent=ux(`${matches.length} opções${matches.length>80?' · refine a busca para ver mais':''}`,`${matches.length} options${matches.length>80?' · refine your search to see more':''}`);
    const box=document.getElementById('picker-options'); box.replaceChildren();
    PICKER.visible.forEach((entry,index)=>{
        const option=uxButton('',()=>selectPickerOption(index),'picker-option'); option.id=`picker-option-${index}`; option.setAttribute('role','option');option.setAttribute('aria-selected',String(PICKER.choice?.value===entry.value));option.tabIndex=-1;
        const thumbKind = PICKER.kind === 'weapon' ? 'weapon' : PICKER.kind === 'decoration' ? 'decoration' : PICKER.kind === 'talisman' ? 'talisman' : 'armor';
        const thumbSrc = equipVisualSrc(thumbKind, entry.item, PICKER.kind);
        if (thumbSrc) {
            const img = document.createElement('img');
            img.src = thumbSrc; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
            img.onerror = () => {
                const fb = thumbKind === 'weapon' ? wikiFileUrl(weaponIconFiles(entry.item?.weapon_type)[0] || 'Great Sword Icon White.png') : thumbKind === 'armor' ? wikiFileUrl(armorIconFiles(PICKER.kind)[0] || 'MH3icon-Helm.png') : wikiFileUrl('MH3icon-Accessory.png');
                if (img.getAttribute('src') !== fb) img.src = fb; else img.remove();
            };
            option.append(img);
        }
        const content=uxNode('span','picker-option-copy'); content.append(uxNode('strong','',entry.label));
        const meta = equipMetaSummary(thumbKind, entry.item);
        const skillText=Object.entries(entry.item?.skills || {}).map(([name,level])=>`${skillDisplayName(name)} ${level}`).join(' · ');
        if (meta || skillText) content.append(uxNode('small','',[meta, skillText].filter(Boolean).join(' · ')));
        option.append(content); box.append(option);
    });
    if (!matches.length) box.append(uxNode('p','empty-state',ux('Nenhuma opção corresponde à busca.','No options match your search.')));
}
function selectPickerOption(index) {
    const choice=PICKER?.visible[index]; if (!choice) return;
    PICKER.choice=choice; PICKER.focus=index;
    document.querySelectorAll('.picker-option').forEach((node,i)=>node.setAttribute('aria-selected',String(i===index)));
    document.getElementById('picker-search').setAttribute('aria-activedescendant',`picker-option-${index}`);
    const current=PICKER.select.selectedOptions[0]?.textContent || ux('Nenhum','None');
    const preview=document.getElementById('picker-preview');
    const thumbKind = PICKER.kind === 'weapon' ? 'weapon' : PICKER.kind === 'decoration' ? 'decoration' : PICKER.kind === 'talisman' ? 'talisman' : 'armor';
    const item=choice.item;
    const previewRow = uxNode('div', 'picker-preview-card');
    const previewSrc = equipVisualSrc(thumbKind, item, PICKER.kind);
    if (previewSrc) {
        const pImg = document.createElement('img');
        pImg.src = previewSrc; pImg.alt = choice.label; pImg.className = 'picker-preview-photo';
        pImg.onerror = () => pImg.remove();
        previewRow.append(pImg);
    }
    const previewCopy = uxNode('div', 'picker-preview-copy');
    previewCopy.append(uxNode('strong','',choice.label), uxNode('p','metric-note',ux(`Substitui: ${current}`,`Replaces: ${current}`)));
    if (item) previewCopy.append(uxNode('p','metric-note',`${equipMetaSummary(thumbKind, item) || `${ux('Slots','Slots')}: ${(item.slots || []).join(' / ') || '-'}`}`));
    const old=PICKER.items.find(entry=>entry.value===PICKER.select.value)?.item;
    const names=new Set([...Object.keys(old?.skills || {}),...Object.keys(item?.skills || {})]);
    const changes=[...names].map(name=>({name,delta:(item?.skills?.[name] || 0)-(old?.skills?.[name] || 0)})).filter(change=>change.delta);
    if(changes.length) previewCopy.append(uxNode('p','picker-skill-delta',changes.map(({name,delta})=>`${delta>0?'+':''}${delta} ${skillDisplayName(name)}`).join(' · ')));
    previewRow.append(previewCopy);
    preview.replaceChildren(previewRow);
    document.getElementById('picker-apply').disabled=false;
}
function applyPickerChoice() {
    if (!PICKER?.choice) return;
    const {select,choice}=PICKER;
    if (![...select.options].some(option=>option.value===choice.value)) return;
    const before=[...document.querySelectorAll('.deco-select')].filter(input=>input.value).length;
    select.value=choice.value;
    select.dispatchEvent(new Event('change',{bubbles:true}));
    const after=[...document.querySelectorAll('.deco-select')].filter(input=>input.value).length;
    refreshSlotPickers(); saveWorkspaceDraft();
    document.getElementById('equipment-picker').close();
    if (after<before) uxMessage(ux(`${before-after} adorno(s) incompatível(is) removido(s). Desfazer restaura a troca.`,`${before-after} incompatible decoration(s) removed. Undo restores the change.`));
}
function onWorkspaceResult(result) {
    const key=JSON.stringify(currentBuilderEquipment());
    const scenarioKey=WorkspaceState.scenarioKey(currentScenarioPayload());
    const delta=document.getElementById('build-delta');
    if (LAST_SCENARIO_KEY!==scenarioKey || WORKSPACE_RESTORING) delta.textContent='';
    if (!WORKSPACE_RESTORING && LAST_SCENARIO_KEY===scenarioKey && LAST_RESULT_KEY && key!==LAST_RESULT_KEY && PREVIOUS_DPS!==null) {
        const change=WorkspaceState.percent(result.practical_dps,PREVIOUS_DPS);
        delta.textContent=change===null?'':`${change>=0?'+':''}${change.toFixed(1)}% ${ux('DPS desde a última troca','DPS since the last change')}`;
        delta.style.color=change>=0?'var(--success)':'var(--danger)';
    }
    LAST_RESULT_KEY=key; LAST_SCENARIO_KEY=scenarioKey; PREVIOUS_DPS=result.practical_dps;
    document.getElementById('mobile-build-metrics').textContent=`${Number(result.practical_dps).toFixed(1)} DPS · ${Math.round(result.damage_per_cycle)} ${ux('dano/rotação','damage/rotation')}`;
    const missing=UX_SLOTS.slice(1,6).filter(slot=>String(document.getElementById(`sel-${slot}`).value).includes('_none')).length;
    document.getElementById('build-validity').textContent=missing ? ux(`Build parcial · ${missing} peças de armadura vazias`,`Partial build · ${missing} empty armor pieces`) : ux('Dano estimado · condições da caçada','Estimated damage · hunt conditions');
    const badgesBox = document.getElementById('engine-transparency-badges');
    if (badgesBox) {
        badgesBox.replaceChildren();
        const partial = uxNode('span', 'engine-badge', ux('Estimativa parcial · MVs legados', 'Partial estimate · legacy MVs'));
        partial.title = ux('Tempos e motion values estimados; não representa medição exata de caçada.', 'Estimated timings and motion values; not an in-game measurement.');
        badgesBox.append(partial);
        if (result.element_capped) {
            const capBadge = uxNode('span', 'engine-badge warn', ux(`Teto elemental: ${result.element_cap_display}`, `Element cap: ${result.element_cap_display}`));
            capBadge.title = ux('Elemento limitado pelo teto da classe em MH Wilds.', 'Element capped by MH Wilds weapon class ceiling.');
            badgesBox.append(capBadge);
        }
        if (result.wound_hitzone_applied > 0) {
            badgesBox.append(uxNode('span', 'engine-badge accent', ux(`Ferida +${result.wound_hitzone_applied} HZV`, `Wound +${result.wound_hitzone_applied} HZV`)));
        }
    }
    toggleWoundBonusVisibility();
    refreshUptimeVisibility(); updateWorkspaceContext();
    if (WORKSPACE_READY) saveWorkspaceDraft();
}
function openWorkspaceDialog(node,title) {
    const dialog=document.getElementById('workspace-dialog');
    if (DIALOG_NODE && DIALOG_NODE!==node) restoreDialogNode();
    if (!dialog.open) DIALOG_ORIGIN=document.activeElement;
    if (!DIALOG_NODE) { DIALOG_NODE=node; DIALOG_PLACEHOLDER=document.createComment('dialog origin'); node.before(DIALOG_PLACEHOLDER); document.getElementById('dialog-content').replaceChildren(node); }
    document.getElementById('dialog-title').textContent=title;
    if (!dialog.open) dialog.showModal();
    refreshIcons();
}
function restoreDialogNode() {
    if (DIALOG_NODE && DIALOG_PLACEHOLDER) {
        if(DIALOG_NODE.dataset.ephemeral) {DIALOG_NODE.remove();DIALOG_PLACEHOLDER.remove();}
        else DIALOG_PLACEHOLDER.replaceWith(DIALOG_NODE);
    }
    DIALOG_NODE=null; DIALOG_PLACEHOLDER=null;
}
function closeWorkspaceDialog() { document.getElementById('workspace-dialog').close(); }
function chooseBuildScenario(scenario) {
    if (WorkspaceState.scenarioKey(scenario)===WorkspaceState.scenarioKey(currentScenarioPayload())) return Promise.resolve(false);
    return new Promise(resolve=>{
        const dialog=document.getElementById('workspace-dialog'),content=uxNode('section','scenario-choice');
        const monster=GAME_DATA.monsters.find(item=>item.id===scenario.monster_id);
        content.append(uxNode('p','',ux('A build tem um cenário diferente. Qual deseja usar?','This build has a different scenario. Which should be used?')),
            uxNode('p','metric-note',`${monsterDisplayName(scenario.custom_monster || monster)} · ${translatePart(scenario.target_part)}`));
        let choice=null;
        content.append(uxButton(ux('Manter minha caçada','Keep my hunt'),()=>{choice=true;dialog.close();}),uxButton(ux('Usar cenário da build','Use build scenario'),()=>{choice=false;dialog.close();}),uxButton(ux('Cancelar','Cancel'),()=>dialog.close(),'btn btn-secondary'));
        document.body.append(content);document.getElementById('dialog-back').hidden=true;
        openWorkspaceDialog(content,ux('Condições da build','Build conditions'));
        dialog.addEventListener('close',()=>{content.remove();resolve(choice);},{once:true});
    });
}
function openEditor(kind) {
    if (kind==='gog' && CUSTOM_GOG) fillGogEditor(CUSTOM_GOG);
    document.getElementById('dialog-back').hidden=true;
    openWorkspaceDialog(document.getElementById(`screen-${kind}`),ux(kind==='gog'?'Arma Gogartiana':'Talismã personalizado',kind==='gog'?'Gog Artian weapon':'Custom talisman'));
}
function openContextWiki(type,id,back=false) {
    const entry=findWikiEntry(type,id); if (!entry) return;
    if (!back) WIKI_TRAIL.push(wikiEntryKey(entry));
    WIKI_SELECTED_KEY=wikiEntryKey(entry); renderWikiArticle();
    document.getElementById('dialog-back').hidden=WIKI_TRAIL.length<2;
    openWorkspaceDialog(document.getElementById('wiki-article'),wikiEntryTitle(entry));
    document.getElementById('workspace-dialog').scrollTop=0;
}
function wikiBack() { if (WIKI_TRAIL.length<2) return; WIKI_TRAIL.pop(); openContextWiki(...WIKI_TRAIL.at(-1).split(':'),true); }
function favoriteIds() { try { const ids=JSON.parse(localStorage.getItem('mhwilds_favorites') || '[]'); return Array.isArray(ids)?ids:[]; } catch { return []; } }
function toggleFavorite(id) {
    const ids=new Set(favoriteIds()); ids.has(id)?ids.delete(id):ids.add(id);
    try { localStorage.setItem('mhwilds_favorites',JSON.stringify([...ids])); } catch { uxMessage(ux('Não foi possível salvar favorita.','Could not save favorite.')); }
    renderBuildLibrary();
}
function buildPhoto(build) {
    const weapon=build.equipment.custom_weapon || GAME_DATA.weapons.find(item=>item.id===build.equipment.weapon_id);
    return equipmentPhotoSrc({kind:'weapon',item:weapon,is_gog:!!build.equipment.custom_weapon});
}
function renderBuildLibrary() {
    const box=document.getElementById('build-library-list'); if (!box || !GAME_DATA) return;
    const query=WorkspaceState.normalize(document.getElementById('saved-build-search').value), favorites=favoriteIds();
    const builds=SAVED_BUILDS.filter(build=>WorkspaceState.normalize(build.name).includes(query) && (!document.getElementById('favorite-builds-only').checked || favorites.includes(build.id)));
    box.replaceChildren();
    if (!builds.length) { box.append(emptyState(ux('Nenhuma build nesta lista','No builds in this list'),ux('Montar uma build','Create a build'),()=>showScreen('builder'))); return; }
    for (const build of builds) {
        const row=uxNode('article','saved-build-row'), image=document.createElement('img'); image.src=buildPhoto(build);image.alt='';image.loading='lazy';image.onerror=()=>image.remove();
        const copy=uxNode('div','saved-build-copy'); copy.append(uxNode('strong','',build.name),uxNode('span','metric-note',`${equipmentName(build.equipment.weapon_id,build.equipment)} · ${build.result?.practical_dps ?? '-'} DPS ${ux('no cenário salvo','in saved scenario')}`), buildGearStrip(build));
        const actions=uxNode('div','saved-build-actions');
        const favorite=uxButton(ux('Favorita','Favorite'),()=>toggleFavorite(build.id),'icon-button','star'); favorite.setAttribute('aria-label',ux('Favoritar ','Favorite ')+build.name);favorite.setAttribute('aria-pressed',String(favorites.includes(build.id)));favorite.replaceChildren(uxIcon('star'));if(favorites.includes(build.id))favorite.style.color='var(--accent)';
        actions.append(favorite,uxButton(ux('Editar','Edit'),()=>loadBuildIntoBuilder(build.id),'btn btn-secondary','pencil'),uxButton(ux('Comparar','Compare'),()=>{ COMPARISON_SELECTED=null; showScreen('comparator'); },'btn btn-secondary','chart-no-axes-combined'));
        const menu=uxNode('details','action-menu'), summary=uxNode('summary','icon-button');summary.setAttribute('aria-label',ux('Opções da build','Build options'));summary.append(uxIcon('ellipsis'));const commands=uxNode('div','');
        commands.append(uxButton(ux('Renomear','Rename'),()=>renameBuild(build.id)),uxButton(ux('Duplicar','Duplicate'),async()=>{const duplicate=structuredClone(build);duplicate.id=`build_${Date.now()}`;duplicate.name+=ux(' (cópia)',' (copy)');try{saveBuildLocal(duplicate);await loadSavedBuilds();renderBuildLibrary();}catch{uxMessage(ux('Não foi possível salvar cópia.','Could not save copy.'));}}),uxButton(ux('Excluir','Delete'),async()=>{if(confirm(ux(`Excluir "${build.name}"?`,`Delete "${build.name}"?`))){await deleteBuild(build.id);renderBuildLibrary();}},'btn btn-danger'));
        menu.append(summary,commands);actions.append(menu);row.append(image,copy,actions);box.append(row);
    }
    refreshIcons();
}
function emptyState(title,label,action) { const box=uxNode('div','empty-state'); box.append(uxNode('h3','',title),uxButton(label,action,'btn'));return box; }
function renderRecommendationCards() {
    const container=document.getElementById('optimizer-results-container');container.replaceChildren();
    if (!OPTIMIZER_RESULTS.length) {
        container.append(uxNode('p','empty-state',ux('Escolha uma categoria ou ajuste as habilidades para buscar uma build.','Choose a category or adjust skills to find a build.')));return;
    }
    const best=Math.max(...OPTIMIZER_RESULTS.map(build=>Number(build.result?.practical_dps || 0)));
    OPTIMIZER_RESULTS.slice(0,2).forEach((build,index)=>{
        const result=build.result || {},article=uxNode('article','recommendation'),head=uxNode('div','recommendation-head');
        const photo=document.createElement('img');photo.src=buildPhoto(build);photo.alt='';photo.loading='lazy';photo.onerror=()=>photo.remove();
        const title=uxNode('div','');title.append(uxNode('span','eyebrow',ux(`Opção ${index+1}`,`Option ${index+1}`)),uxNode('h3','',build.name || ux('Build recomendada','Recommended build')));
        head.append(photo,title);article.append(head);
        const metrics=uxNode('div','recommendation-metrics');
        [[result.practical_dps,'DPS'],[result.damage_per_cycle,ux('Dano / rotação','Damage / rotation')],[result.damage_per_min,'DPM']].forEach(([value,label])=>{const field=uxNode('div','');field.append(uxNode('strong','',Number(value || 0).toLocaleString(SITE_LOCALE==='en'?'en-US':'pt-BR',{maximumFractionDigits:1})),uxNode('span','',label));metrics.append(field);});article.append(metrics);
        const difference=WorkspaceState.percent(result.practical_dps,best);
        article.append(uxNode('p','metric-note',difference===0?ux('Maior DPS entre as opções calculadas neste cenário.','Highest DPS among the options calculated for this scenario.'):ux(`${difference?.toFixed(1)}% DPS em relação à melhor opção calculada.`,`${difference?.toFixed(1)}% DPS versus the best calculated option.`)));
        const skills=uxNode('div','recommendation-skills');
        Object.entries(result.active_skills || {}).slice(0,8).forEach(([name,level])=>skills.append(uxButton(`${skillDisplayName(name)} ${level}`,()=>openWikiEntry('skill',name),'skill-link')));article.append(buildGearStrip(build), skills);
        const details=uxNode('details','detail-section');details.append(uxNode('summary','',ux('Equipamento, arma e evidências','Equipment, weapon and evidence')));
        UX_SLOTS.forEach(slot=>details.append(uxNode('p','metric-note',equipmentName(build.equipment[`${slot}_id`],build.equipment))));
        const weapon=build.equipment.custom_weapon;
        if(weapon)details.append(uxNode('p','', [weapon.skill_1,weapon.skill_2].filter(Boolean).map(skillDisplayName).join(' + ')));
        details.append(uxNode('p','metric-note',optimizerEvidence(build)),uxNode('p','metric-note',`${ux('Parte','Part')}: ${translatePart(result.target_part_name || build.scenario.target_part)} · HZ ${ux('físico','physical')} ${result.physical_hitzone ?? '-'} · ${ux('elemental','elemental')} ${result.elemental_hitzone ?? '-'}`));article.append(details);
        const actions=uxNode('div','optimizer-actions');actions.append(uxButton(ux('Usar build','Use build'),()=>loadOptimizerResult(index),'btn','check'),uxButton(ux('Salvar','Save'),()=>saveOptimizerResult(index),'btn btn-secondary','bookmark'),uxButton(ux('Materiais','Materials'),()=>addOptimizerResultToWishlist(index),'btn btn-secondary','hammer'));
        const status=uxNode('p','metric-note');status.dataset.wishlistStatus=index;article.append(actions,status);container.append(article);
    });refreshIcons();
}
async function compareCurrentBuild() { await saveCurrentBuild(); if (EDITING_BUILD_ID) { COMPARISON_SELECTED=null; showScreen('comparator'); } }
function updateComparisonExperience(builds) {
    const empty=document.getElementById('comparison-empty'); if (!empty) return;
    const hasSaved=SAVED_BUILDS.length>0;
    empty.hidden=hasSaved;
    for (const node of document.querySelectorAll('#screen-comparator > .card,#screen-comparator > .grid-2,#screen-comparator > .grid-4,#comparison-insights')) node.hidden=!hasSaved;
    document.getElementById('btn-compare-rotations').disabled=!hasSaved;
    document.getElementById('refresh-shared-comparison').disabled=!hasSaved;
    const baseline=document.getElementById('comparison-baseline');
    if (!builds.length) { document.getElementById('comparison-bars').replaceChildren(); document.getElementById('comparison-diff').replaceChildren();return; }
    if (!builds.some(build=>build.id===COMPARISON_BASELINE)) COMPARISON_BASELINE=builds[0].id;
    baseline.replaceChildren(...builds.map(build=>new Option(build.name,build.id)));baseline.value=COMPARISON_BASELINE;
    const selected=COMPARISON_SELECTED || builds.slice(0,4).map(build=>build.id);
    const choices=document.getElementById('comparison-selection');choices.replaceChildren();
    builds.forEach(build=>{const label=uxNode('label',''),input=document.createElement('input');input.type='checkbox';input.checked=selected.includes(build.id);input.disabled=!input.checked && selected.length>=4;input.onchange=()=>{COMPARISON_SELECTED=[...choices.querySelectorAll('input:checked')].map(input=>input.value);renderComparatorTable();};input.value=build.id;label.append(input,document.createTextNode(build.name));choices.append(label);});
    const visible=builds.filter(build=>selected.includes(build.id));
    const metric=document.getElementById('comparator-sort').value, max=Math.max(1,...visible.map(build=>metricValue(build,metric)));
    const bars=document.getElementById('comparison-bars');bars.replaceChildren();
    visible.forEach(build=>{const row=uxNode('div',`comparison-bar ${build.id===COMPARISON_BASELINE?'baseline':''}`), track=uxNode('div','comparison-bar-track'),fill=uxNode('div','comparison-bar-fill');fill.style.width=`${metricValue(build,metric)/max*100}%`;track.append(fill);row.append(uxNode('span','comparison-bar-name',build.name),track,uxNode('strong','',metricValue(build,metric)));bars.append(row);});
    const reference=builds.find(build=>build.id===COMPARISON_BASELINE);
    const diff=document.getElementById('comparison-diff');diff.replaceChildren();
    const onlyChanges=document.getElementById('comparison-diff-only').checked;
    visible.filter(build=>build!==reference).forEach(build=>{
        const column=uxNode('div',''); column.append(uxNode('h3','',build.name));
        UX_SLOTS.forEach(slot=>{const key=`${slot}_id`,a=equipmentName(reference.equipment[key],reference.equipment),b=equipmentName(build.equipment[key],build.equipment);if (!onlyChanges || a!==b) column.append(uxNode('div','mini-item',`${a} → ${b}`));});
        const weaponOf=item=>item.equipment.custom_weapon || GAME_DATA.weapons.find(weapon=>weapon.id===item.equipment.weapon_id) || {};
        const weaponA=weaponOf(reference),weaponB=weaponOf(build);
        const weaponFields=[['raw',ux('Ataque base','Base attack')],['affinity',ux('Afinidade base','Base affinity')],['element_display',ux('Elemento exibido','Displayed element')],['sharpness_hits',ux('Unidades de fio','Sharpness units')]];
        weaponFields.forEach(([key,label])=>{
            const a=weaponA[key],b=weaponB[key];
            if(a!=null && b!=null && (!onlyChanges || a!==b))column.append(uxNode('div','mini-item',`${label}: ${a} → ${b}`));
        });
        const skillNames=new Set([...Object.keys(reference.result.active_skills || {}),...Object.keys(build.result.active_skills || {})]);
        [...skillNames].forEach(name=>{const a=reference.result.active_skills[name]||0,b=build.result.active_skills[name]||0;if(!onlyChanges || a!==b)column.append(uxNode('div','mini-item',`${skillDisplayName(name)}: ${a} → ${b}`));});
        if(column.childElementCount===1)column.append(uxNode('p','metric-note',ux('Mesmas peças, atributos de arma e níveis de habilidade exibidos. Consulte os combos e reforços para outras diferenças.','Same displayed pieces, weapon attributes and skill levels. Check combos and reinforcements for other differences.')));
        diff.append(column);
    });
}
function prepareUptimes() {
    const card=document.querySelector('.scenario-uptime-card'); if (!card || card.dataset.prepared) return;
    card.dataset.prepared='true';
    const controls=uxNode('div','action-strip');
    const label=uxNode('label','scenario-check'),check=document.createElement('input');check.type='checkbox';check.id='show-all-uptimes';check.checked=true;check.onchange=refreshUptimeVisibility;
    const span=uxNode('span','');span.dataset.uxPt='Todas as condições';span.dataset.uxEn='All conditions';label.append(check,span);controls.append(label,uxNode('span','metric-note'));card.insertBefore(controls,card.querySelector('.segmented'));
    const grid=uxNode('div','uptime-fields');
    [...card.querySelectorAll('input[id^="uptime-"]')].forEach(input=>{const field=input.parentElement;grid.append(field);field.classList.add('form-group');});
    card.append(grid);
    refreshUptimeVisibility();
}
function refreshUptimeVisibility() {
    if (!GAME_DATA) return;
    const showAll=document.getElementById('show-all-uptimes')?.checked ?? true;
    document.querySelectorAll('input[id^="uptime-"],input[id^="opt-up-"]').forEach(input=>{
        const key=input.id.replace(/^uptime-|^opt-up-/,''), skill=UX_UPTIMES[key];
        const label=input.parentElement.querySelector('label');
        if (label) { label.textContent=skill ? `${skillDisplayName(skill)} (%)` : `${ux({seed:'Semente/pílula de força',powder:'Pó demoníaco',mantle:'Manto'}[key]||key,{seed:'Might seed/pill',powder:'Demon powder',mantle:'Mantle'}[key]||key)} (%)`;label.htmlFor=input.id; }
        if (input.id.startsWith('uptime-')) input.parentElement.hidden=!showAll && !!skill && !(CURRENT_RESULT?.active_skills?.[skill]>0);
    });
}
function renderPartTable() {
    if (!GAME_DATA) return;
    const container=document.getElementById('monster-all-parts'); if (!container) return;
    const monster=currentMonsterForChart(), selected=document.getElementById('scenario-part').value;
    const type=equipmentPreviewItems()[0].item?.weapon_type;
    const damageType=['Hammer','Hunting Horn'].includes(type)?'blunt':['Bow','Light Bowgun','Heavy Bowgun'].includes(type)?'shot':'sever';
    const keys=['sever','blunt','shot','fire','water','thunder','ice','dragon'];
    const names=SITE_LOCALE==='en'?['Part','Sever','Blunt','Shot','Fire','Water','Thunder','Ice','Dragon']:['Parte','Corte','Impacto','Projétil','Fogo','Água','Raio','Gelo','Dragão'];
    const table=uxNode('table',''),head=table.createTHead().insertRow();names.forEach(name=>head.append(uxNode('th','',name)));
    const body=table.createTBody();
    [...(monster?.hitzones || [])].sort((a,b)=>Number(b[damageType]||0)-Number(a[damageType]||0)).forEach(hz=>{
        const row=body.insertRow(),cell=row.insertCell();
        const label=translatePart(hz.part_name);
        const button=uxButton(label,()=>{setSelectValue('scenario-part',hz.part_name);document.getElementById('scenario-part').dispatchEvent(new Event('change',{bubbles:true}));},'text-button');
        if(hz.part_name===selected)button.setAttribute('aria-current','true');cell.append(button);
        keys.forEach(key=>row.append(uxNode('td',key===damageType?'best-cell':'',hz[key] ?? '-')));
    });container.replaceChildren(table);
}
function initializeExperience() {
    const mobileMetrics=uxNode('output','mobile-build-metrics');mobileMetrics.id='mobile-build-metrics';
    document.querySelector('#screen-builder > .build-mode').after(mobileMetrics);
    const settings=document.querySelector('#screen-settings > .grid-2');
    const preferences=uxNode('section','card');preferences.append(uxNode('h3','',ux('Aparência e idioma','Appearance and language')));
    // Move original fields on mobile via the settings screen, avoiding duplicate IDs.
    const prefButton=uxButton(ux('Idioma e bioma','Language and biome'),()=>{
        document.getElementById('dialog-back').hidden=true;
        const form=uxNode('div','');form.dataset.ephemeral='true';
        [['language-select',ux('Idioma','Language'),switchSiteLocale],['appearance-select',ux('Bioma','Biome'),switchVisualTheme]].forEach(([id,title,change])=>{
            const field=uxNode('div','form-group'),label=uxNode('label','',title),select=document.getElementById(id).cloneNode(true);select.id=`dialog-${id}`;label.htmlFor=select.id;select.removeAttribute('onchange');select.value=document.getElementById(id).value;select.onchange=()=>change(select.value);field.append(label,select);form.append(field);
        }); document.body.append(form);openWorkspaceDialog(form,ux('Aparência e idioma','Appearance and language'));
    },'btn btn-secondary','palette');preferences.append(prefButton); settings.before(preferences);
    const destructive=[...document.querySelectorAll('#screen-settings .btn-danger')];const danger=uxNode('div','danger-zone action-strip');destructive.forEach(button=>danger.append(button));settings.after(danger);
    const optimizerTools=document.querySelector('#screen-optimizer .shared-comparison-tools');
    const adopt=uxButton(ux('Aplicar à caçada','Apply to hunt'),adoptOptimizerScenario);adopt.id='adopt-optimizer-scenario';adopt.hidden=true;optimizerTools.append(adopt);
    const optimizer=document.querySelector('.optimizer-workspace'),criteria=optimizer.firstElementChild;
    const advanced=uxNode('details','detail-section'),advancedTitle=uxNode('summary','');advancedTitle.dataset.uxPt='Restrições e busca';advancedTitle.dataset.uxEn='Constraints and search';advanced.append(advancedTitle);
    ['opt-specific-weapon-group','opt-sort-by','opt-search-mode','opt-use-transcendence','opt-use-inventory'].forEach(id=>{const field=document.getElementById(id);const group=id==='opt-specific-weapon-group'?field:field.closest('.form-group') || field.parentElement;advanced.append(group);});
    criteria.append(advanced);
    const run=document.getElementById('btn-run-optimizer');criteria.append(run);
    const cancel=uxButton(ux('Cancelar busca','Cancel search'),()=>{OPTIMIZER_REQUEST_ID+=1;OPTIMIZER_RESULTS=[];run.disabled=false;run.textContent=uiText('Executar Otimização');cancel.hidden=true;renderOptimizerResults();uxMessage(ux('Busca descartada nesta tela.','Search discarded in this view.'));});cancel.id='cancel-optimizer';cancel.hidden=true;criteria.append(cancel);
    const gogDetails=uxNode('details','detail-section'),gogSummary=uxNode('summary','');gogSummary.dataset.uxPt='Arma e reforços';gogSummary.dataset.uxEn='Weapon and reinforcements';gogDetails.append(gogSummary,document.getElementById('gog-recommendation-panel'),document.getElementById('progression-weapon-recommendation-panel'));optimizer.lastElementChild.append(gogDetails);
    const comparator=document.getElementById('screen-comparator');
    const empty=emptyState(ux('Escolha suas builds para comparar','Choose your builds to compare'),ux('Encontrar uma build','Find a build'),()=>showScreen('optimizer'));empty.id='comparison-empty';comparator.querySelector('.header-bar').after(empty);
    const insights=uxNode('section','');insights.id='comparison-insights';
    const controls=uxNode('div','shared-comparison-tools'),label=uxNode('label','');label.htmlFor='comparison-baseline';label.dataset.uxPt='Referência';label.dataset.uxEn='Baseline';
    const baseline=document.createElement('select');baseline.id='comparison-baseline';baseline.onchange=()=>{COMPARISON_BASELINE=baseline.value;renderComparatorTable();};controls.append(label,baseline);
    const selection=uxNode('div','comparison-selection');selection.id='comparison-selection';
    const bars=uxNode('div','comparison-bars');bars.id='comparison-bars';
    const diffLabel=uxNode('label','scenario-check'),diffCheck=document.createElement('input');diffCheck.type='checkbox';diffCheck.id='comparison-diff-only';diffCheck.checked=true;diffCheck.onchange=()=>renderComparatorTable();const diffText=uxNode('span','');diffText.dataset.uxPt='Mostrar apenas diferenças';diffText.dataset.uxEn='Show differences only';diffLabel.append(diffCheck,diffText);
    const diff=uxNode('div','equipment-diff');diff.id='comparison-diff';
    insights.append(controls,selection,bars,diffLabel,diff);comparator.querySelector('.shared-comparison-tools').after(insights);
    const table=document.getElementById('comparator-table-body').closest('.card');insights.after(table);
    document.querySelector('.comparison-tools').hidden=true;
    const materialsControls=uxNode('div','action-strip');const missingLabel=uxNode('label','scenario-check'),missingCheck=document.createElement('input');missingCheck.type='checkbox';missingCheck.id='only-missing-materials';missingCheck.checked=true;missingCheck.onchange=()=>renderWishlist();const missingText=uxNode('span','');missingText.dataset.uxPt='Somente faltantes';missingText.dataset.uxEn='Missing only';missingLabel.append(missingCheck,missingText);materialsControls.append(missingLabel,uxButton(ux('Adicionar build atual','Add current build'),addCurrentBuildToWishlist));document.querySelector('#screen-wishlist .header-bar').after(materialsControls);
    const parts=uxNode('details','detail-section'),summary=uxNode('summary','');summary.dataset.uxPt='Todas as partes e hitzones';summary.dataset.uxEn='All parts and hitzones';const partTable=uxNode('div','table-wrap');partTable.id='monster-all-parts';parts.append(summary,partTable);document.querySelector('.scenario-intel-panel').append(parts);
    document.getElementById('workspace-dialog').addEventListener('close',()=>{restoreDialogNode();WIKI_TRAIL=[];DIALOG_ORIGIN?.focus({preventScroll:true});});
    document.getElementById('equipment-picker').addEventListener('close',()=>{PICKER?.origin?.focus({preventScroll:true});});
    document.getElementById('picker-search').addEventListener('keydown',event=>{
        if (!PICKER) return;
        if (['ArrowDown','ArrowUp'].includes(event.key)) {event.preventDefault();const offset=event.key==='ArrowDown'?1:-1;const index=Math.max(0,Math.min(PICKER.visible.length-1,PICKER.focus+offset));selectPickerOption(index);document.getElementById(`picker-option-${index}`)?.scrollIntoView({block:'nearest'});}
        if(event.key==='Enter' && PICKER.choice){event.preventDefault();applyPickerChoice();}
    });
    window.addEventListener('popstate',()=>showScreen(WorkspaceState.route(location.hash),true));
    document.addEventListener('change',event=>{
        if(!WORKSPACE_READY || WORKSPACE_RESTORING)return;
        if(event.target.closest('#screen-scenario')){useHuntScenarioInOptimizer();OPTIMIZER_RESULTS=[];renderOptimizerResults();refreshUptimeVisibility();renderPartTable();renderMonsterGallery();toggleWoundBonusVisibility();}
        if(event.target.closest('#screen-optimizer')) {
            updateWorkspaceContext();
            if(!['opt-meta-preset','opt-weapon-type','filter-opt-weapons'].includes(event.target.id)) {
                OPTIMIZER_REQUEST_ID+=1;OPTIMIZER_RESULTS=[];renderOptimizerResults();
                document.getElementById('btn-run-optimizer').disabled=false;
                document.getElementById('btn-run-optimizer').textContent=uiText('Executar Otimização');
                document.getElementById('cancel-optimizer').hidden=true;
                document.getElementById('gog-recommendation-panel').style.display='none';
                document.getElementById('progression-weapon-recommendation-panel').style.display='none';
            }
        }
        refreshSlotPickers();saveWorkspaceDraft();
    });
    document.addEventListener('input',event=>{if(event.target.id==='build-name-input'){clearTimeout(WORKSPACE_TIMER);WORKSPACE_TIMER=setTimeout(()=>saveWorkspaceDraft(),300);}});
    translateExperience();
}

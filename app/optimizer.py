from itertools import product
from time import perf_counter

from app.combat_rules import ENGINE_VERSION

from app.data import ARMORS_DB, DECORATIONS_DB, EXTRA_GAME_DATA, TALISMANS_DB, WEAPONS_DB
from app.engine import (
    calculate_build, decoration_skills, transcended_slots_for_armor,
    weapon_scenario_base_damage_score,
)
from app.gog_recommendations import gog_set_requirements, recommend_gog_weapon
from app.meta_presets import META_PRESETS_BY_ID, SLOW_WEAPONS, WEAPON_DAMAGE_PRIORITIES, comfort_priorities_for
from app.models import BuildEquipment, GogRecommendationRequest, OptimizerSettings, SavedBuild, ScenarioSettings, Talisman
from app.progression_rules import progression_rule_for
from app.rotations import rotations_for_weapon


SORT_METRICS = {
    "practical_dps", "damage_per_min", "damage_per_cycle",
    "combined_score", "effective_raw", "capped_affinity", "effective_element"
}

DECORATION_SKILLS_BY_ID = {
    decoration.id: decoration_skills(decoration)
    for decoration in DECORATIONS_DB
}
DECORATIONS_BY_KIND = {"weapon": [], "armor": []}
DECORATIONS_BY_SKILL: dict[str, list] = {}
for decoration in DECORATIONS_DB:
    DECORATIONS_BY_KIND[decoration.kind].append(decoration)
    for skill in DECORATION_SKILLS_BY_ID[decoration.id]:
        DECORATIONS_BY_SKILL.setdefault(skill, []).append(decoration)
for decorations in DECORATIONS_BY_SKILL.values():
    decorations.sort(key=lambda item: (item.level, -item.points, item.name.casefold()))
WEAPONS_BY_ID = {weapon.id: weapon for weapon in WEAPONS_DB}
WEAPONS_BY_TYPE = {}
for weapon in WEAPONS_DB:
    WEAPONS_BY_TYPE.setdefault(weapon.weapon_type, []).append(weapon)
ARMORS_BY_SLOT = {}
for armor in ARMORS_DB:
    ARMORS_BY_SLOT.setdefault(armor.slot_type, []).append(armor)
TALISMANS_BY_ID = {talisman.id: talisman for talisman in TALISMANS_DB}


def _optimizer_talismans(settings: OptimizerSettings) -> list[tuple[str, object | None]]:
    fixed = [(t.id, None) for t in TALISMANS_DB]
    custom = [(f"custom_talisman:{item.id}", item.talisman) for item in settings.talismans]
    return fixed + custom


def _slots_for(weapon, talisman, pieces) -> list[tuple[str, int]]:
    slots = [("weapon", slot) for slot in weapon.slots]
    slots.extend(zip(talisman.slot_kinds, talisman.slots))
    for piece in pieces:
        slots.extend(("armor", slot) for slot in piece.slots)
    return sorted(
        [(kind, slot) for kind, slot in slots if slot > 0],
        key=lambda item: item[1],
    )


def _auto_decorations_for_targets(base_result, target_skills, slots) -> list[str]:
    slot_pool = list(slots)
    chosen: list[str] = []
    for skill, min_level in target_skills.items():
        missing = max(0, min_level - base_result.active_skills.get(skill, 0))
        if missing <= 0:
            continue
        candidates = DECORATIONS_BY_SKILL.get(skill, [])
        while missing > 0 and candidates:
            fitted = False
            for deco in candidates:
                slot_idx = next(
                    (
                        idx for idx, (kind, slot) in enumerate(slot_pool)
                        if kind == deco.kind and slot >= deco.level
                    ),
                    None,
                )
                if slot_idx is None:
                    continue
                slot_pool.pop(slot_idx)
                chosen.append(deco.id)
                missing -= DECORATION_SKILLS_BY_ID[deco.id].get(skill, deco.points)
                fitted = True
                break
            if not fitted:
                break
    return chosen


def run_optimizer(settings: OptimizerSettings) -> list[SavedBuild]:
    if settings.sort_by not in SORT_METRICS:
        raise ValueError(f"Métrica de ordenação inválida: {settings.sort_by}")

    if settings.weapon_id:
        weapon = WEAPONS_BY_ID.get(settings.weapon_id)
        if not weapon:
            raise ValueError(f"Arma não encontrada para otimização: {settings.weapon_id}")
        weapons_pool = [weapon]
    else:
        weapons_pool = list(WEAPONS_BY_TYPE.get(settings.weapon_type, []))
        if not weapons_pool:
            raise ValueError(f"Nenhuma arma encontrada para o tipo: {settings.weapon_type.value}")
        weapons_pool = weapons_pool[:settings.weapon_pool_limit]

    helms = ARMORS_BY_SLOT.get("helm", [])
    chests = ARMORS_BY_SLOT.get("chest", [])
    arms = ARMORS_BY_SLOT.get("arms", [])
    waists = ARMORS_BY_SLOT.get("waist", [])
    legs = ARMORS_BY_SLOT.get("legs", [])

    req_skills = [s for s, lvl in settings.target_skills.items() if lvl > 0]

    def filter_useful(piece_list):
        if not req_skills:
            return piece_list[:settings.armor_pool_limit]
        useful = []
        for p in piece_list:
            if any(s in p.skills for s in req_skills) or len(p.slots) > 0:
                useful.append(p)
        return (useful if useful else piece_list)[:settings.armor_pool_limit]

    pools = [
        filter_useful(helms),
        filter_useful(chests),
        filter_useful(arms),
        filter_useful(waists),
        filter_useful(legs),
    ]
    talisman_pool = _optimizer_talismans(settings)[:settings.talisman_pool_limit]

    candidates: list[SavedBuild] = []
    scenario = ScenarioSettings(monster_id=settings.monster_id)
    count = 0

    for weapon in weapons_pool:
        for h, c, a, w, l in product(*pools):
            count += 1
            if count > settings.search_limit:
                break
            for talisman_id, custom_talisman in talisman_pool:
                equip = BuildEquipment(
                    weapon_id=weapon.id,
                    helm_id=h.id,
                    chest_id=c.id,
                    arms_id=a.id,
                    waist_id=w.id,
                    legs_id=l.id,
                    talisman_id="custom_talisman" if custom_talisman else talisman_id,
                    decorations=[],
                    custom_talisman=custom_talisman,
                )
                result = calculate_build(equip, scenario)
                if settings.target_skills:
                    talisman_obj = custom_talisman.to_talisman() if custom_talisman else TALISMANS_BY_ID[talisman_id]
                    auto_decos = _auto_decorations_for_targets(
                        result,
                        settings.target_skills,
                        _slots_for(weapon, talisman_obj, [h, c, a, w, l])
                    )
                    if auto_decos:
                        equip.decorations = auto_decos
                        result = calculate_build(equip, scenario)
                if any(result.active_skills.get(skill, 0) < min_lvl for skill, min_lvl in settings.target_skills.items()):
                    continue

                candidates.append(SavedBuild(
                    id=f"opt_build_{len(candidates)+1}",
                    name=f"Opt {weapon.name} #{len(candidates)+1}",
                    description=(
                        f"{result.practical_dps} DPS | {result.damage_per_cycle} ciclo | "
                        f"{result.active_skills.get('Attack Boost', 0)} Atk / "
                        f"{result.active_skills.get('Weakness Exploit', 0)} WEX / "
                        f"{result.active_skills.get('Critical Boost', 0)} CB"
                    ),
                    equipment=equip,
                    scenario=scenario,
                    result=result,
                ))
            if len(candidates) >= settings.max_results * 12:
                break
        if len(candidates) >= settings.max_results * 12:
            break

    candidates.sort(key=lambda b: getattr(b.result, settings.sort_by), reverse=True)
    return candidates[:settings.max_results]


# The v2 search below replaces the original lexicographic product above. Keeping
# the small original implementation nearby makes cache migrations reproducible.
DEFAULT_DAMAGE_SKILLS = {
    "Weakness Exploit": 5, "Critical Boost": 5, "Agitator": 5,
    "Critical Eye": 5, "Attack Boost": 5, "Burst": 5,
}


def _equipment_signature(build: SavedBuild) -> tuple:
    equip = build.equipment
    custom = equip.custom_weapon
    return (
        equip.weapon_id, equip.helm_id, equip.chest_id, equip.arms_id,
        equip.waist_id, equip.legs_id, equip.talisman_id, tuple(equip.decorations),
        custom.skill_1 if custom else None, custom.skill_2 if custom else None,
    )


def _meaningful_alternative(primary: SavedBuild, candidate: SavedBuild) -> bool:
    primary_armor = {
        primary.equipment.helm_id, primary.equipment.chest_id, primary.equipment.arms_id,
        primary.equipment.waist_id, primary.equipment.legs_id,
    }
    candidate_armor = {
        candidate.equipment.helm_id, candidate.equipment.chest_id, candidate.equipment.arms_id,
        candidate.equipment.waist_id, candidate.equipment.legs_id,
    }
    return len(primary_armor & candidate_armor) <= 4

FILLER_SKILL_WEIGHTS = {
    "Weakness Exploit": 120, "Critical Boost": 118, "Agitator": 116,
    "Critical Eye": 114, "Attack Boost": 112, "Burst": 110,
    "Critical Element": 108, "Maximum Might": 104, "Peak Performance": 102,
    "Offensive Guard": 102, "Counterstrike": 100, "Coalescence": 98,
    "Resentment": 96, "Antivirus": 94, "Adrenaline Rush": 92,
    "Foray": 90, "Ambush": 88, "Fire Attack": 86, "Water Attack": 86,
    "Thunder Attack": 86, "Ice Attack": 86, "Dragon Attack": 86,
    "Partbreaker": 72, "Divine Blessing": 60, "Evade Window": 58,
    "Stun Resistance": 56, "Speed Eating": 54, "Blight Resistance": 52,
}

SKILL_CAPS = {
    skill.get("name"): max(
        [int(rank.get("level", 0)) for rank in (skill.get("ranks") or [])] or [5]
    )
    for skill in EXTRA_GAME_DATA.get("skills", [])
    if isinstance(skill, dict) and skill.get("name")
}


def _skill_score_v2(skills, preferred):
    return sum(
        min(desired, skills.get(skill, 0))
        * (18.0 if skill in DEFAULT_DAMAGE_SKILLS else 10.0)
        for skill, desired in preferred.items()
    )


def _requirements_met(result, required: dict[str, int]) -> bool:
    """A set/group skill only meets a target once its piece threshold is active."""
    details = {detail.name: detail for detail in result.skill_details}
    for skill, level in required.items():
        if result.active_skills.get(skill, 0) < level:
            return False
        detail = details.get(skill)
        if detail and detail.kind in {"group", "set"} and not detail.active:
            return False
    return True


def _piece_score_v2(piece, preferred, transcended, required=None):
    slots = transcended_slots_for_armor(piece) if transcended else piece.slots
    required_score = sum(
        min(level, piece.skills.get(skill, 0)) * 80.0
        for skill, level in (required or {}).items()
    )
    slot_value = sum(
        s * 2.6 + (1.4 if s >= 2 else 0.0) + (1.6 if s >= 3 else 0.0)
        for s in slots
    )
    return _skill_score_v2(piece.skills, preferred) + required_score + slot_value + len(slots) * 1.5 + piece.rarity * 0.15


def _armor_combinations_v2(pools, preferred, transcended, limit, required=None):
    beam = [([], 0.0)]
    beam_width = max(80, min(limit, 3500))
    for pool in pools:
        beam = sorted(
            [
                (pieces + [piece], score + _piece_score_v2(piece, preferred, transcended, required))
                for pieces, score in beam for piece in pool
            ],
            key=lambda row: row[1], reverse=True,
        )[:beam_width]
    return [pieces for pieces, _ in beam]


def armor_family(piece) -> str:
    """Return the exact armor-set family without its alpha/beta/gamma suffix."""
    family = piece.set_bonus_group or ""
    for suffix in (" α", " β", " γ"):
        if family.endswith(suffix):
            return family[:-len(suffix)]
    return family


def _progression_armor_combinations_v2(pools, rule, preferred, transcended, limit, required=None):
    required_counts = dict(rule.armor_requirements)
    allowed = set(required_counts)
    # Keep several best variants for each partial family-count signature. This
    # compares alpha/beta and individual slot choices without losing a valid
    # five-piece composition during beam pruning.
    states = [([], {}, 0.0)]
    per_signature = max(12, min(48, limit // 30))
    for pool in pools:
        buckets = {}
        for pieces, counts, score in states:
            for piece in pool:
                family = armor_family(piece)
                if family not in allowed or counts.get(family, 0) >= required_counts[family]:
                    continue
                next_counts = dict(counts)
                next_counts[family] = next_counts.get(family, 0) + 1
                signature = tuple(sorted(next_counts.items()))
                row = (
                    pieces + [piece], next_counts,
                    score + _piece_score_v2(piece, preferred, transcended, required),
                )
                buckets.setdefault(signature, []).append(row)
        states = []
        for rows in buckets.values():
            states.extend(sorted(rows, key=lambda row: row[2], reverse=True)[:per_signature])

    complete = [
        (pieces, score) for pieces, counts, score in states
        if all(counts.get(family, 0) == count for family, count in required_counts.items())
    ]
    complete.sort(key=lambda row: row[1], reverse=True)
    return [pieces for pieces, _ in complete[:limit]]


def _slots_for_v2(weapon, talisman, pieces, transcended):
    slots = [("weapon", slot) for slot in weapon.slots]
    slots.extend(zip(talisman.slot_kinds, talisman.slots))
    for piece in pieces:
        piece_slots = transcended_slots_for_armor(piece) if transcended else piece.slots
        slots.extend(("armor", slot) for slot in piece_slots)
    return sorted(
        [(kind, slot) for kind, slot in slots if slot > 0],
        key=lambda item: item[1],
    )


def _choose_decorations_v2(base_result, required, preferred, slots, filler_weights=None):
    slot_pool = list(slots)
    chosen = []
    levels = dict(base_result.active_skills)
    filler_weights = filler_weights or FILLER_SKILL_WEIGHTS
    ordered = [(skill, level) for skill, level in required.items() if level > 0]
    ordered.extend(
        (skill, level) for skill, level in preferred.items()
        if level > 0 and skill not in required
    )
    for skill, desired in ordered:
        while levels.get(skill, 0) < desired and slot_pool:
            options = []
            for deco in DECORATIONS_BY_SKILL.get(skill, []):
                deco_skills = DECORATION_SKILLS_BY_ID[deco.id]
                for index, (kind, slot) in enumerate(slot_pool):
                    if kind == deco.kind and slot >= deco.level:
                        points = deco_skills[skill]
                        synergy = sum(
                            5 for bonus_skill, bonus_points in deco_skills.items()
                            if bonus_skill != skill and levels.get(bonus_skill, 0) < preferred.get(bonus_skill, 0)
                            and bonus_points > 0
                        )
                        options.append((points * 20 + synergy - (slot - deco.level) * 2 - deco.level, deco, index))
            if not options:
                break
            _, deco, slot_index = max(options, key=lambda row: row[0])
            slot_pool.pop(slot_index)
            chosen.append(deco.id)
            for bonus_skill, points in DECORATION_SKILLS_BY_ID[deco.id].items():
                levels[bonus_skill] = levels.get(bonus_skill, 0) + points

    # The requested levels may not consume every available slot. Fill the
    # remainder with capped damage, farming and comfort skills so optimized
    # builds do not arrive in the builder half-empty.
    while slot_pool:
        options = []
        for kind in {kind for kind, _ in slot_pool}:
            for deco in DECORATIONS_BY_KIND[kind]:
                deco_skills = DECORATION_SKILLS_BY_ID[deco.id]
                weight = sum(filler_weights.get(skill, 0) for skill in deco_skills)
                if weight <= 0:
                    continue
                gain = sum(
                    min(points, max(0, SKILL_CAPS.get(skill, 5) - levels.get(skill, 0)))
                    for skill, points in deco_skills.items()
                )
                if gain <= 0:
                    continue
                if any(skill in preferred for skill in deco_skills):
                    weight += 20
                for index, (slot_kind, slot) in enumerate(slot_pool):
                    if slot_kind == deco.kind and slot >= deco.level:
                        waste = slot - deco.level
                        options.append((weight + gain * 8 + deco.level - waste * 2, deco, index, gain))
        if not options:
            break
        _, deco, slot_index, gain = max(options, key=lambda row: row[0])
        slot_pool.pop(slot_index)
        chosen.append(deco.id)
        for skill, points in DECORATION_SKILLS_BY_ID[deco.id].items():
            levels[skill] = levels.get(skill, 0) + points
    return chosen


def _rank_weapons_v2(settings, preferred, scenario, max_rarity=None, series_terms=()):
    weapons = [
        weapon for weapon in WEAPONS_BY_TYPE.get(settings.weapon_type, [])
        if (max_rarity is None or weapon.rarity <= max_rarity)
        and (not series_terms or weapon.series in series_terms)
    ]
    weapons.sort(
        key=lambda weapon: (
            weapon_scenario_base_damage_score(weapon, scenario)
            + _skill_score_v2(weapon.skills, preferred) + sum(weapon.slots) * 2
        ),
        reverse=True,
    )
    return weapons[:settings.weapon_pool_limit]


def _rank_talismans_v2(settings, preferred, required=None, talisman_skills=()):
    rows = _optimizer_talismans(settings)

    if talisman_skills:
        filtered = []
        for talisman_id, custom in rows:
            talisman = custom.to_talisman() if custom else TALISMANS_BY_ID.get(talisman_id)
            if talisman and all(talisman.skills.get(skill, 0) == level for skill, level in talisman_skills):
                filtered.append((talisman_id, custom))
        rows = filtered

    def score(row):
        talisman_id, custom = row
        talisman = custom.to_talisman() if custom else TALISMANS_BY_ID.get(talisman_id)
        if not talisman:
            return -1
        required_score = sum(
            min(level, talisman.skills.get(skill, 0)) * 80.0
            for skill, level in (required or {}).items()
        )
        return _skill_score_v2(talisman.skills, preferred) + required_score + sum(talisman.slots) * 2

    return sorted(rows, key=score, reverse=True)[:settings.talisman_pool_limit]


def run_optimizer(settings: OptimizerSettings) -> list[SavedBuild]:
    """Ranked beam search with selected rotation, uptime and preset support."""
    from app.legality import preset_context, validate_build
    from app.models import ProgressionContext
    started = perf_counter()
    if settings.sort_by not in SORT_METRICS:
        raise ValueError(f"Métrica de ordenação inválida: {settings.sort_by}")

    preset = META_PRESETS_BY_ID.get(settings.preset_id or "")
    if settings.preset_id and not preset:
        raise ValueError(f"Preset não encontrado: {settings.preset_id}")
    if preset and preset.weapon_type != settings.weapon_type:
        raise ValueError("O preset selecionado pertence a outra classe de arma.")

    # A preset represents one build category. Keep the two genuinely useful
    # alternatives after ranking; unrestricted custom searches can still show
    # more results for manual exploration.
    result_limit = min(settings.max_results, 2) if preset else settings.max_results

    max_rarity = preset.max_rarity if preset else None
    progression_rule = progression_rule_for(settings.weapon_type, preset.profile) if preset else None
    use_transcendence = settings.use_transcendence and (preset.use_transcendence if preset else True)

    scenario = settings.scenario.model_copy(deep=True) if settings.scenario else ScenarioSettings()
    scenario.monster_id = settings.monster_id or (preset.monster_id if preset else scenario.monster_id)
    if settings.rotation_id:
        scenario.rotation_id = settings.rotation_id
    elif preset:
        rotations = rotations_for_weapon(settings.weapon_type)
        selected = next(
            (rotation for rotation in rotations if rotation.category == preset.rotation_category), rotations[0]
        )
        scenario.rotation_id = selected.id

    required = dict(preset.target_skills if preset else {})
    required.update({skill: level for skill, level in settings.target_skills.items() if level > 0})
    preferred = dict(WEAPON_DAMAGE_PRIORITIES[settings.weapon_type])
    if preset:
        preferred.update(preset.preferred_skills)
        if preset.uptime_preset in {"realistic", "comfort"}:
            preferred.update(comfort_priorities_for(settings.weapon_type))
    if progression_rule:
        preferred.update(dict(progression_rule.talisman_skills))
    preferred.update({skill: level for skill, level in settings.preferred_skills.items() if level > 0})
    preferred.update(required)

    gog_custom_weapon = None
    if preset and preset.weapon_recommendation_mode == "gog":
        recommendation = recommend_gog_weapon(GogRecommendationRequest(
            weapon_type=settings.weapon_type,
            monster_id=scenario.monster_id,
            rotation_id=scenario.rotation_id,
            preset_id=preset.id,
            target_part=scenario.target_part,
        ))
        gog_custom_weapon = recommendation.perfect.weapon
        gog_requirements = gog_set_requirements(
            gog_custom_weapon.skill_1 or "", gog_custom_weapon.skill_2
        )
        required.update(gog_requirements)
        preferred.update(gog_requirements)

    if gog_custom_weapon:
        weapons_pool = [gog_custom_weapon.to_weapon()]
    elif settings.weapon_id:
        weapon = WEAPONS_BY_ID.get(settings.weapon_id)
        if not weapon:
            raise ValueError(f"Arma não encontrada para otimização: {settings.weapon_id}")
        if weapon.weapon_type != settings.weapon_type:
            raise ValueError("A arma específica não pertence à classe escolhida.")
        if max_rarity is not None and weapon.rarity > max_rarity:
            raise ValueError(f"A arma específica excede o limite R{max_rarity} deste preset de progressão.")
        weapons_pool = [weapon]
    else:
        weapons_pool = _rank_weapons_v2(
            settings, preferred, scenario, max_rarity,
            progression_rule.weapon_series if progression_rule else (),
        )
    if not weapons_pool:
        detail = " nas árvores recomendadas pelo guia" if progression_rule else ""
        raise ValueError(f"Nenhuma arma encontrada para {settings.weapon_type.value}{detail}.")

    def useful(slot_type):
        pieces = [
            piece for piece in ARMORS_BY_SLOT.get(slot_type, [])
            if (max_rarity is None or piece.rarity <= max_rarity)
            and (
                not progression_rule
                or armor_family(piece) in dict(progression_rule.armor_requirements)
            )
        ]
        pieces.sort(
            key=lambda piece: _piece_score_v2(piece, preferred, use_transcendence, required),
            reverse=True,
        )
        return pieces[:settings.armor_pool_limit]

    pools = [useful(slot) for slot in ("helm", "chest", "arms", "waist", "legs")]
    if progression_rule:
        armor_sets = _progression_armor_combinations_v2(
            pools, progression_rule, preferred, use_transcendence,
            settings.search_limit, required,
        )
    else:
        armor_sets = _armor_combinations_v2(
            pools, preferred, use_transcendence, settings.search_limit, required
        )
    if not armor_sets:
        raise ValueError("Nenhuma combinação de armadura satisfaz o guia desta etapa.")
    talisman_pool = _rank_talismans_v2(
        settings, preferred, required,
        progression_rule.talisman_skills if progression_rule else (),
    )
    if not talisman_pool:
        raise ValueError("O amuleto indicado pelo guia não foi encontrado na base local.")

    candidates = []
    evaluated = 0
    legal_candidates = 0
    evaluated_by_weapon = {weapon.id: 0 for weapon in weapons_pool}
    filler_weights = dict(FILLER_SKILL_WEIGHTS)
    if settings.weapon_type in SLOW_WEAPONS:
        filler_weights["Burst"] = 0
    context = settings.progression or (preset_context(preset) if preset else ProgressionContext())
    provisional_candidates = 0
    rejected_illegal = 0
    # Every weapon receives one evaluation before the next equipment pair.
    # A global budget must not be exhausted by the first weapon in the pool.
    for pieces in armor_sets:
        for talisman_id, custom_talisman in talisman_pool:
            for weapon in weapons_pool:
                if evaluated >= settings.search_limit:
                    break
                evaluated += 1
                evaluated_by_weapon[weapon.id] += 1
                h, c, a, w, l = pieces
                equip = BuildEquipment(
                    weapon_id=weapon.id, helm_id=h.id, chest_id=c.id, arms_id=a.id,
                    waist_id=w.id, legs_id=l.id,
                    talisman_id="custom_talisman" if custom_talisman else talisman_id,
                    decorations=[], transcended_armor=[piece.slot_type for piece in pieces if use_transcendence and piece.rarity >= 5],
                    progression=context,
                    custom_weapon=gog_custom_weapon,
                    custom_talisman=custom_talisman,
                )
                try:
                    base_result = calculate_build(equip, scenario)
                    talisman_obj = custom_talisman.to_talisman() if custom_talisman else TALISMANS_BY_ID[talisman_id]
                    equip.decorations = _choose_decorations_v2(
                        base_result, required, preferred,
                        _slots_for_v2(weapon, talisman_obj, pieces, use_transcendence),
                        filler_weights,
                    )
                    result = calculate_build(equip, scenario)
                except (ValueError, StopIteration):
                    continue
                if result.slot_warnings or not _requirements_met(result, required):
                    continue
                legality = validate_build(equip, expected_weapon_type=settings.weapon_type,
                                          required_skills=required,
                                          context_basis="user_declared" if settings.progression else "category_checkpoint" if preset else "unknown")
                if legality.status == "invalid":
                    rejected_illegal += 1
                    continue
                if settings.verified_only and not legality.recommendation_eligible:
                    continue
                if legality.recommendation_eligible:
                    legal_candidates += 1
                else:
                    provisional_candidates += 1
                prefix = preset.name if preset else f"Opt {weapon.name}"
                source_label = "Guia atualizado | " if progression_rule else ""
                if gog_custom_weapon:
                    source_label += "Gog de duas habilidades ativas | "
                candidates.append(SavedBuild(
                    legality=legality,
                    id=f"{settings.preset_id or 'opt'}_{evaluated}",
                    name=f"{prefix} #{len(candidates) + 1}",
                    description=(
                        f"{source_label}{result.rotation_name} | {result.practical_dps} DPS | "
                        f"{result.damage_per_cycle} dano/rotação | {result.damage_per_min} DPM"
                    ),
                    equipment=equip,
                    scenario=scenario.model_copy(deep=True),
                    result=result,
                    provenance={
                        "engine_version": ENGINE_VERSION,
                        "method": "bounded_beam_search",
                        "preset_id": settings.preset_id,
                        "source_urls": preset.source_urls if preset else [],
                        "target_skills": required,
                    },
                ))
                if len(candidates) > max(result_limit * 60, 80):
                    candidates.sort(key=lambda build: getattr(build.result, settings.sort_by), reverse=True)
                    candidates = candidates[:max(result_limit * 40, 60)]
            if evaluated >= settings.search_limit:
                break
        if evaluated >= settings.search_limit:
            break

    candidates.sort(key=lambda build: getattr(build.result, settings.sort_by), reverse=True)
    unique = []
    fallback = []
    seen = set()
    for candidate in candidates:
        signature = _equipment_signature(candidate)
        if signature in seen:
            continue
        seen.add(signature)
        if unique and not _meaningful_alternative(unique[0], candidate):
            fallback.append(candidate)
            continue
        unique.append(candidate)
        if len(unique) >= result_limit:
            break
    for candidate in fallback:
        if len(unique) >= result_limit:
            break
        unique.append(candidate)
    stats = {
        "evaluated": evaluated,
        "legal_candidates": legal_candidates,
        "provisional_candidates": provisional_candidates,
        "rejected_illegal": rejected_illegal,
        "search_limit": settings.search_limit,
        "evaluated_by_weapon": evaluated_by_weapon,
        "weapon_count": len(weapons_pool),
        "armor_combinations": len(armor_sets),
        "talisman_count": len(talisman_pool),
        "budget_exhausted": evaluated >= settings.search_limit,
        "global_optimum_proven": False,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "cache_hit": False,
    }
    for candidate in unique:
        candidate.search_stats = dict(stats)
    return unique

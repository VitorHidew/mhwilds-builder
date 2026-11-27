from math import prod

from app.data import ARMORS_DB, DECORATIONS_DB, EXTRA_GAME_DATA, MONSTERS_DB, TALISMANS_DB, WEAPONS_DB
from app.models import (
    ActiveSkillDetail, BuildEquipment, BuildResult, CustomGogWeapon, CustomTalisman,
    ElementType, HitAudit, MonsterProfile, ScenarioSettings,
    SharpnessLevel, SkillSource, Weapon, WeaponType
)
from app.rotations import resolve_rotation
from app.combat_rules import (
    ENGINE_VERSION, RULE_SOURCES, burst_bonus, attack_element_components, absorption_bonus,
    coalescence_multiplier, critical_element_bonus as element_crit_bonus,
    charge_master_bonus as charged_bonus, critical_status_bonus, element_cap,
)

SHARPNESS_MODIFIERS = {
    SharpnessLevel.RED: (0.50, 0.25),
    SharpnessLevel.ORANGE: (0.75, 0.50),
    SharpnessLevel.YELLOW: (1.00, 0.75),
    SharpnessLevel.GREEN: (1.05, 1.00),
    SharpnessLevel.BLUE: (1.20, 1.0625),
    SharpnessLevel.WHITE: (1.32, 1.15),
    SharpnessLevel.PURPLE: (1.39, 1.25),
}

ATTACK_BOOST_TABLE = {
    0: (0.0, 0.0),
    1: (3.0, 0.0),
    2: (5.0, 0.0),
    3: (7.0, 0.0),
    4: (8.0, 0.02),
    5: (9.0, 0.04),
}

CRITICAL_EYE_TABLE = {0: 0.0, 1: 4.0, 2: 8.0, 3: 12.0, 4: 16.0, 5: 20.0}
WEAKNESS_EXPLOIT_TABLE = {0: 0.0, 1: 5.0, 2: 10.0, 3: 15.0, 4: 20.0, 5: 30.0}
WEAKNESS_EXPLOIT_WOUND_TABLE = {0: 0.0, 1: 3.0, 2: 5.0, 3: 10.0, 4: 15.0, 5: 20.0}
CRITICAL_BOOST_TABLE = {0: 1.25, 1: 1.28, 2: 1.31, 3: 1.34, 4: 1.37, 5: 1.40}
AGITATOR_RAW_TABLE = {0: 0.0, 1: 4.0, 2: 8.0, 3: 12.0, 4: 16.0, 5: 20.0}
AGITATOR_AFF_TABLE = {0: 0.0, 1: 3.0, 2: 5.0, 3: 7.0, 4: 10.0, 5: 15.0}
MAXIMUM_MIGHT_AFF_TABLE = {0: 0.0, 1: 10.0, 2: 20.0, 3: 30.0}
LATENT_POWER_AFF_TABLE = {0: 0.0, 1: 10.0, 2: 20.0, 3: 30.0, 4: 40.0, 5: 50.0}
PEAK_PERFORMANCE_RAW_TABLE = {0: 0.0, 1: 3.0, 2: 6.0, 3: 10.0, 4: 15.0, 5: 20.0}
OFFENSIVE_GUARD_RAW_PCT_TABLE = {0: 0.0, 1: 0.05, 2: 0.10, 3: 0.15}
COUNTERSTRIKE_RAW_TABLE = {0: 0.0, 1: 10.0, 2: 15.0, 3: 25.0}
RESENTMENT_RAW_TABLE = {0: 0.0, 1: 5.0, 2: 10.0, 3: 15.0, 4: 20.0, 5: 25.0}
ANTIVIRUS_AFF_TABLE = {0: 0.0, 1: 3.0, 2: 6.0, 3: 10.0}
ADRENALINE_RUSH_RAW_TABLE = {0: 0.0, 1: 10.0, 2: 15.0, 3: 20.0, 4: 25.0, 5: 30.0}
FORAY_RAW_TABLE = {0: 0.0, 1: 6.0, 2: 8.0, 3: 10.0, 4: 12.0, 5: 15.0}
FORAY_AFF_TABLE = {0: 0.0, 1: 0.0, 2: 5.0, 3: 10.0, 4: 15.0, 5: 20.0}
AMBUSH_RAW_PCT_TABLE = {0: 0.0, 1: 0.05, 2: 0.10, 3: 0.15}
HEROICS_RAW_PCT_TABLE = {0: 0.0, 1: 0.0, 2: 0.05, 3: 0.05, 4: 0.10, 5: 0.30}
MANTLE_RAW_PCT_BONUS = 0.05
MIGHT_SEED_RAW_BONUS = 10.0
DEMON_POWDER_RAW_BONUS = 10.0

RANGED_WEAPONS = {WeaponType.BOW, WeaponType.LIGHT_BOWGUN, WeaponType.HEAVY_BOWGUN}
SHARPNESS_ORDER = (
    SharpnessLevel.PURPLE, SharpnessLevel.WHITE, SharpnessLevel.BLUE,
    SharpnessLevel.GREEN, SharpnessLevel.YELLOW, SharpnessLevel.ORANGE, SharpnessLevel.RED,
)
ELEMENTAL_RESISTANCE_KEYS = ("fire", "water", "thunder", "ice", "dragon")
WEAPONS_BY_ID = {weapon.id: weapon for weapon in WEAPONS_DB}
ARMORS_BY_ID = {armor.id: armor for armor in ARMORS_DB}
DECORATIONS_BY_ID = {decoration.id: decoration for decoration in DECORATIONS_DB}
TALISMANS_BY_ID = {talisman.id: talisman for talisman in TALISMANS_DB}
MONSTERS_BY_ID = {monster.id: monster for monster in MONSTERS_DB}


def hitzone_for_monster(monster: MonsterProfile, target_part: str = "Media_Ponderada"):
    if target_part and target_part != "Media_Ponderada":
        selected = next((hitzone for hitzone in monster.hitzones if hitzone.part_name == target_part), None)
        if selected is not None:
            return selected
        raise ValueError(f"Parte não encontrada para este monstro: {target_part}")
    return monster.weighted_hitzone


def physical_hitzone_for_weapon(weapon_type: WeaponType, hitzone) -> float:
    if weapon_type in (WeaponType.HAMMER, WeaponType.HUNTING_HORN):
        return hitzone.blunt
    if weapon_type in RANGED_WEAPONS:
        return hitzone.shot
    return hitzone.sever


def physical_hitzone_for_hit(hit, weapon_type, hitzone):
    if hit.damage_kind in {"shell", "impact_phial", "element_phial"}:
        return 100.0
    if hit.damage_kind in {"sever", "blunt", "shot"}:
        return getattr(hitzone, hit.damage_kind)
    return physical_hitzone_for_weapon(weapon_type, hitzone)


def validate_equipment(equip):
    for slot in ("helm", "chest", "arms", "waist", "legs"):
        piece_id = getattr(equip, f"{slot}_id")
        piece = ARMORS_BY_ID.get(piece_id)
        if piece is None or piece.slot_type != slot:
            raise ValueError(f"Peça inválida para {slot}: {piece_id}")


def elemental_hitzone_for_element(element_type: ElementType, hitzone) -> float:
    return {
        ElementType.FIRE: hitzone.fire,
        ElementType.WATER: hitzone.water,
        ElementType.THUNDER: hitzone.thunder,
        ElementType.ICE: hitzone.ice,
        ElementType.DRAGON: hitzone.dragon,
    }.get(element_type, 0.0)


def weapon_scenario_base_damage_score(weapon: Weapon, scenario: ScenarioSettings) -> float:
    """Estimate an unskilled cycle with the same HZ and true-element rules as the engine."""
    if scenario.monster_id == "custom_monster" and scenario.custom_monster:
        monster = scenario.custom_monster
    else:
        monster = MONSTERS_BY_ID.get(scenario.monster_id)
    if monster is None:
        return 0.0

    hitzone = hitzone_for_monster(monster, scenario.target_part)
    rotation = resolve_rotation(weapon.weapon_type, scenario.rotation_id)
    if weapon.weapon_type in RANGED_WEAPONS:
        sharp_raw_mult, sharp_ele_mult = (1.0, 1.0)
    else:
        sharp_raw_mult, sharp_ele_mult = SHARPNESS_MODIFIERS.get(weapon.sharpness, (1.0, 1.0))

    affinity = min(100.0, max(-100.0, weapon.affinity)) / 100.0
    crit_mod = (1.0 + affinity * 0.25) if affinity >= 0 else (1.0 + affinity * 0.25)
    elemental_hzv = elemental_hitzone_for_element(weapon.element_type, hitzone)
    is_status = weapon.element_type in {
        ElementType.POISON, ElementType.PARALYSIS, ElementType.SLEEP, ElementType.BLAST,
    }

    total = 0.0
    for hit in rotation.hits:
        motion_value = hit.motion_value if scenario.custom_motion_value is None else scenario.custom_motion_value
        raw_damage = (
            weapon.raw * (sharp_raw_mult if hit.uses_sharpness else 1.0) * (motion_value / 100.0)
            * (physical_hitzone_for_hit(hit, weapon.weapon_type, hitzone) / 100.0) * (crit_mod if hit.can_crit else 1.0)
        )
        element_damage = 0.0 if is_status else (
            weapon.element_val * (sharp_ele_mult if hit.uses_sharpness else 1.0) * hit.element_mult * (elemental_hzv / 100.0)
        )
        if hit.fixed_fire:
            element_damage = hit.fixed_fire * hitzone.fire / 100.0
        total += (raw_damage + element_damage) * hit.hit_count
    return total

# These values are intentionally kept in one place. The API supplies ranks and
# descriptions but not all numerical combat tables, so every approximate effect
# is exposed in BuildResult.audit_notes instead of being presented as exact.
RAPID_MORPH_TIME_MULTIPLIER = {0: 1.0, 1: 0.98, 2: 0.96, 3: 0.94}
FOCUS_TIME_MULTIPLIER = {0: 1.0, 1: 0.985, 2: 0.97, 3: 0.955}
RAZOR_SHARP_REDUCTION = {0: 0.0, 1: 0.10, 2: 0.25, 3: 0.50}
ARTILLERY_BONUS = {0: 0.0, 1: 0.05, 2: 0.10, 3: 0.15}

DIRECT_DAMAGE_SKILLS = {
    "Attack Boost", "Agitator", "Burst", "Peak Performance", "Counterstrike",
    "Coalescence", "Resentment", "Adrenaline Rush", "Foray", "Offensive Guard",
    "Ambush", "Heroics", "Critical Eye", "Weakness Exploit", "Maximum Might",
    "Latent Power", "Antivirus", "Critical Boost", "Critical Element",
    "Charge Master", "Artillery", "Normal Shots", "Piercing Shots",
    "Spread/Power Shots", "Rapid Fire Up", "Special Ammo Boost", "Airborne",
    "Doshaguma's Might", "Gogmapocalypse", "Ebony Odogaron's Power",
}
TEMPO_SKILLS = {"Focus", "Rapid Morph", "Quick Sheathe"}
SURVIVAL_SKILLS = {
    "Guard", "Guard Up", "Divine Blessing", "Stun Resistance", "Fortify",
}

WEAPON_LIMITATIONS = {
    WeaponType.GREAT_SWORD: "Cargas, offset e acerto do primeiro TCS são pressupostos da rotação; sem hitstop medido.",
    WeaponType.LONG_SWORD: "Aura vermelha e contra-ataques bem-sucedidos são pressupostos; sem custo de manutenção da aura.",
    WeaponType.SWORD_AND_SHIELD: "Perfect Rush/Charged Chop usam sequências fixas; sem janela de guarda ou KO.",
    WeaponType.DUAL_BLADES: "Golpes compostos de DB têm contagens e multiplicadores elementais não validados; sem gestão de vigor/modo Demon.",
    WeaponType.HAMMER: "Cargas são pressupostas; KO, exaustão e acerto de todos os golpes não são simulados.",
    WeaponType.HUNTING_HORN: "Sem ciclo de canções/bolhas; o bônus de ataque externo de 5% é uma aproximação manual.",
    WeaponType.LANCE: "Contra-ataques pressupõem sucesso; sem bloqueio, dano residual ou tempo até o ataque inimigo.",
    WeaponType.GUNLANCE: "Shelling fixo Nv.3, não adaptado ao tipo/nível da arma; recarga e munição não são simuladas.",
    WeaponType.SWITCH_AXE: "Sem bônus por tipo de frasco, estado amplificado ou gestão dos medidores.",
    WeaponType.CHARGE_BLADE: "AED/SAED usam frascos de impacto fixos, inclusive em armas elementais; sem carga de escudo/frasco.",
    WeaponType.INSECT_GLAIVE: "Sem dano do kinsecto, bônus/manutenção de extratos ou orçamento de vigor.",
    WeaponType.LIGHT_BOWGUN: "Sem munição elemental/status, distância crítica, recarga, capacidade ou validação da munição disponível.",
    WeaponType.HEAVY_BOWGUN: "Sem munição elemental/status, distância crítica, recarga, capacidade ou recarga de Wyvernheart.",
    WeaponType.BOW: "Sem revestimentos, distância crítica, medidor de Tracer ou recuperação de vigor.",
}

SKILL_METADATA = {
    skill.get("name"): skill
    for skill in EXTRA_GAME_DATA.get("skills", [])
    if isinstance(skill, dict) and skill.get("name")
}


from app.equipment_rules import transcended_slots_for_armor
from app.legality import validate_build


def decoration_skills(decoration) -> dict[str, int]:
    """Supports old single-skill cache records and current multi-skill jewels."""
    if decoration.skills:
        return decoration.skills
    return {decoration.skill: decoration.points}


def _active_effect_skills(skills: dict[str, int], details: list[ActiveSkillDetail]) -> dict[str, int]:
    inactive_sets = {
        detail.name for detail in details
        if detail.kind in {"group", "set"} and not detail.active
    }
    return {name: level for name, level in skills.items() if name not in inactive_sets}


def _set_rank(detail_by_name: dict[str, ActiveSkillDetail], skill_name: str) -> int:
    detail = detail_by_name.get(skill_name)
    return detail.active_rank_level if detail and detail.active else 0


def _equipped_armors(equip: BuildEquipment):
    return [
        ARMORS_BY_ID[piece_id] for piece_id in (
            equip.helm_id, equip.chest_id, equip.arms_id, equip.waist_id, equip.legs_id
        ) if piece_id in ARMORS_BY_ID
    ]


def _defense_summary(equip: BuildEquipment, weapon: Weapon, scenario: ScenarioSettings, skills: dict[str, int]) -> tuple[int, int, dict[str, int], float]:
    armors = _equipped_armors(equip)
    total_defense = sum(piece.defense for piece in armors) + weapon.defense_bonus + int(scenario.food_defense_bonus)
    max_defense = sum(piece.defense_max for piece in armors) + weapon.defense_bonus + int(scenario.food_defense_bonus)
    resistances = {
        element: sum(int(piece.elemental_resistances.get(element, 0)) for piece in armors)
        for element in ELEMENTAL_RESISTANCE_KEYS
    }
    resilience = (
        max_defense
        + sum(max(0, value) for value in resistances.values()) * 2.0
        + min(skills.get("Guard", 0), 3) * 8
        + min(skills.get("Guard Up", 0), 3) * 6
        + min(skills.get("Divine Blessing", 0), 5) * 7
        + min(skills.get("Stun Resistance", 0), 3) * 4
        + scenario.fortify_stacks * 18
    )
    return total_defense, max_defense, resistances, round(resilience, 1)


def _sharpness_segments(weapon: Weapon, handicraft: int = 0) -> dict[SharpnessLevel, float]:
    segments = {
        SharpnessLevel(color): float(units)
        for color, units in weapon.sharpness_segments.items()
        if color in {item.value for item in SharpnessLevel} and units > 0
    }
    if not segments:
        segments = {weapon.sharpness: max(1, weapon.sharpness_hits)}
    # MHDB gives levels available in each successive color, starting at the top.
    # Missing metadata is not permission to invent an extra sharpness bar.
    colors = list(reversed(SHARPNESS_ORDER))
    top = max(colors.index(color) for color in segments)
    remaining = max(0, min(5, handicraft))
    for index, capacity in enumerate(weapon.weapon_features.get("handicraft", [])):
        if top + index >= len(colors) or remaining <= 0:
            break
        levels = min(remaining, max(0, int(capacity)))
        if levels:
            color = colors[top + index]
            segments[color] = segments.get(color, 0) + levels * 10
            remaining -= levels
    return segments


def _sharpness_projection(
    weapon: Weapon,
    skills: dict[str, int],
    scenario: ScenarioSettings,
    hits_per_cycle_cost: int,
    cycle_time: float,
    affinity: float,
    critical_cost: float | None = None,
) -> tuple[float, float, float, float]:
    """Expected sharpness depletion, without sharpening downtime or resource recovery."""
    if weapon.weapon_type in RANGED_WEAPONS:
        return 1.0, 1.0, 0, 0.0

    base_cost = max(0, hits_per_cycle_cost)
    consumed = float(base_cost)
    if skills.get("Master's Touch", 0):
        if critical_cost is None:
            critical_cost = base_cost * max(0.0, min(1.0, affinity / 100.0))
        consumed -= .80 * min(base_cost, max(0, critical_cost))
    consumed *= 1.0 - RAZOR_SHARP_REDUCTION.get(min(3, skills.get("Razor Sharp", 0)), 0.0)
    if skills.get("Protective Polish", 0):
        consumed *= 1.0 - scenario.sharpness_management_uptime

    segments = _sharpness_segments(weapon, skills.get("Handicraft", 0))
    top_color = next(color for color in SHARPNESS_ORDER if segments.get(color, 0) > 0)
    cycles = scenario.hunt_duration_seconds / max(cycle_time, 0.1)
    if consumed <= 0:
        raw_mult, ele_mult = SHARPNESS_MODIFIERS[top_color]
        return raw_mult, ele_mult, 0.0, cycles
    remaining_cycles = cycles
    weighted_raw = 0.0
    weighted_ele = 0.0
    top_cycles = 0.0
    for color in SHARPNESS_ORDER:
        units = segments.get(color, 0)
        if units <= 0 or remaining_cycles <= 0:
            continue
        color_cycles = min(remaining_cycles, units / consumed)
        raw_mult, ele_mult = SHARPNESS_MODIFIERS[color]
        weighted_raw += raw_mult * color_cycles
        weighted_ele += ele_mult * color_cycles
        if color == top_color:
            top_cycles = color_cycles
        remaining_cycles -= color_cycles
    if remaining_cycles > 0:
        raw_mult, ele_mult = SHARPNESS_MODIFIERS[SharpnessLevel.RED]
        weighted_raw += raw_mult * remaining_cycles
        weighted_ele += ele_mult * remaining_cycles
    return weighted_raw / cycles, weighted_ele / cycles, consumed, top_cycles


def _weapon_mechanics(weapon: Weapon, rotation, skills: dict[str, int]) -> list[str]:
    mechanics: list[str] = []
    if weapon.coatings:
        mechanics.append(f"Revestimentos disponíveis: {', '.join(weapon.coatings)}.")
    if weapon.ammo:
        rapid = [f"{row.get('kind')} {row.get('level')}" for row in weapon.ammo if row.get("rapid")]
        mechanics.append("Munições de tiro rápido: " + (", ".join(rapid) if rapid else "nenhuma na arma selecionada") + ".")
    if weapon.shell_type:
        mechanics.append(f"Shelling {weapon.shell_type} Nv.{weapon.shell_level}; a biblioteca ainda usa exemplos fixos Nv.3, sem adaptar tipo/nível.")
    if weapon.phial:
        mechanics.append(f"Frasco: {weapon.phial}; as rotações de CB usam impacto fixo, e bônus de frasco de SA não estão modelados.")
    if weapon.kinsect_level:
        mechanics.append(f"Kinsecto Nv.{weapon.kinsect_level}; dano do kinsecto e manutenção de extratos não estão modelados.")
    if weapon.melody:
        mechanics.append("Canções: " + ", ".join(weapon.melody[:3]) + ("." if len(weapon.melody) <= 3 else "…"))
    if rotation.category == "offset":
        mechanics.append("Rotação de offset: Doshaguma's Might só entra se o requisito de peças estiver ativo.")
    return mechanics


def resolve_weapon(equip: BuildEquipment) -> Weapon:
    if equip.weapon_id == "custom_gog_weapon":
        if equip.custom_weapon:
            return equip.custom_weapon.to_weapon()
        raise ValueError("Arma Gog personalizada selecionada, mas nenhum editor de arma foi enviado.")
    weapon = WEAPONS_BY_ID.get(equip.weapon_id)
    if weapon:
        return weapon
    raise ValueError(f"Arma não encontrada: {equip.weapon_id}")


def resolve_talisman(equip: BuildEquipment):
    if equip.talisman_id == "custom_talisman":
        if equip.custom_talisman:
            return equip.custom_talisman.to_talisman()
        raise ValueError("Talismã personalizado selecionado, mas nenhum editor de talismã foi enviado.")
    talisman = TALISMANS_BY_ID.get(equip.talisman_id)
    if talisman:
        return talisman
    raise ValueError(f"Talismã não encontrado: {equip.talisman_id}")


def aggregate_skills(
    equip: BuildEquipment, weapon: Weapon, talisman
) -> tuple[dict[str, int], list[str], list[ActiveSkillDetail]]:
    validate_equipment(equip)
    skills: dict[str, int] = {}
    warnings: list[str] = []
    sources: dict[str, dict[tuple[str, str, str | None], SkillSource]] = {}

    def add_skill(skill: str, level: int, kind: str, name: str, slot_type: str | None = None) -> None:
        skills[skill] = skills.get(skill, 0) + level
        key = (kind, name, slot_type)
        source = sources.setdefault(skill, {}).get(key)
        if source:
            source.level += level
        else:
            sources[skill][key] = SkillSource(
                kind=kind, name=name, slot_type=slot_type, level=level
            )

    for s, lvl in weapon.skills.items():
        add_skill(s, lvl, "weapon", weapon.name, "weapon")
    for s, lvl in talisman.skills.items():
        add_skill(s, lvl, "talisman", talisman.name, "talisman")

    slots_by_kind = {"weapon": list(weapon.slots), "armor": []}
    talisman_slot_kinds = list(getattr(talisman, "slot_kinds", []))
    for index, slot in enumerate(talisman.slots):
        kind = talisman_slot_kinds[index] if index < len(talisman_slot_kinds) else "armor"
        slots_by_kind[kind].append(slot)

    for piece_id in [equip.helm_id, equip.chest_id, equip.arms_id, equip.waist_id, equip.legs_id]:
        armor = ARMORS_BY_ID.get(piece_id)
        if armor:
            for s, lvl in armor.skills.items():
                add_skill(s, lvl, "armor", armor.name, armor.slot_type)
            armor_slots = (
                transcended_slots_for_armor(armor)
                if armor.slot_type in equip.transcended_armor
                else list(armor.slots)
            )
            slots_by_kind["armor"].extend(armor_slots)

    equipped_decos = []
    for d_id in equip.decorations:
        deco = DECORATIONS_BY_ID.get(d_id)
        if deco:
            equipped_decos.append(deco)
        else:
            warnings.append(f"Jóia não encontrada: {d_id}.")
    sorted_decos = sorted(equipped_decos, key=lambda decoration: decoration.level, reverse=True)
    slot_pools = {
        kind: sorted((slot for slot in slots if slot > 0), reverse=True)
        for kind, slots in slots_by_kind.items()
    }
    for deco in sorted_decos:
        slot_pool = slot_pools.get(deco.kind, [])
        fit = False
        for idx, slot_size in enumerate(slot_pool):
            if slot_size >= deco.level:
                slot_pool.pop(idx)
                fit = True
                for skill_name, points in decoration_skills(deco).items():
                    add_skill(skill_name, points, "decoration", deco.name, deco.kind)
                break
        if not fit:
            kind_label = "arma" if deco.kind == "weapon" else "armadura"
            warnings.append(
                f"O adorno de {kind_label} '{deco.name}' (Nível {deco.level}) "
                f"não coube em nenhum slot de {kind_label} disponível."
            )

    caps = {}
    for skill_name, metadata in SKILL_METADATA.items():
        ranks = metadata.get("ranks") or []
        piece_thresholds = [
            int(rank["setPiecesRequired"])
            for rank in ranks if rank.get("setPiecesRequired") is not None
        ]
        levels = [int(rank.get("level", 0)) for rank in ranks]
        if piece_thresholds and metadata.get("kind") in {"group", "set"}:
            caps[skill_name] = max(piece_thresholds)
        elif levels:
            caps[skill_name] = max(levels)
    for skill_name, max_lvl in caps.items():
        if skill_name in skills:
            skills[skill_name] = min(max_lvl, skills[skill_name])

    details: list[ActiveSkillDetail] = []
    for skill_name, level in skills.items():
        metadata = SKILL_METADATA.get(skill_name, {})
        ranks = metadata.get("ranks") or []
        thresholds = sorted({
            int(rank["setPiecesRequired"])
            for rank in ranks
            if rank.get("setPiecesRequired") is not None
        })
        is_set_skill = metadata.get("kind") in {"group", "set"} and bool(thresholds)
        required = thresholds[0] if thresholds else None
        active_rank = None
        next_required = None
        if is_set_skill:
            eligible = [
                rank for rank in ranks
                if rank.get("setPiecesRequired") is not None
                and int(rank["setPiecesRequired"]) <= level
            ]
            if eligible:
                active_rank = max(eligible, key=lambda rank: int(rank["setPiecesRequired"]))
            next_required = next((value for value in thresholds if value > level), None)

        details.append(ActiveSkillDetail(
            name=skill_name,
            level=level,
            kind=metadata.get("kind") or "armor",
            active=not is_set_skill or active_rank is not None,
            required_pieces=required,
            next_required_pieces=next_required,
            active_rank_name=active_rank.get("name") if active_rank else None,
            active_rank_level=int(active_rank.get("level", 0)) if active_rank else 0,
            sources=list(sources.get(skill_name, {}).values()),
        ))
    details.sort(key=lambda detail: (not detail.active, detail.name.casefold()))

    return skills, warnings, details


def calculate_build(equip: BuildEquipment, scenario: ScenarioSettings, *, skill_overrides=None) -> BuildResult:
    weapon = resolve_weapon(equip)
    talisman = resolve_talisman(equip)
    skills, warnings, skill_details = aggregate_skills(equip, weapon, talisman)
    effect_skills = _active_effect_skills(skills, skill_details)
    # Used only for controlled comparisons, never to grant extra equipment skills.
    for name, level in (skill_overrides or {}).items():
        effect_skills[name] = max(0, min(effect_skills.get(name, 0), level))
        for detail in skill_details:
            if detail.name == name and not effect_skills[name]:
                detail.active_rank_level = 0
    detail_by_name = {detail.name: detail for detail in skill_details}

    if scenario.monster_id == "custom_monster" and scenario.custom_monster:
        monster = scenario.custom_monster
    else:
        monster = MONSTERS_BY_ID.get(scenario.monster_id)
    if monster is None:
        raise ValueError(f"Monstro não encontrado: {scenario.monster_id}")
    hitzone = hitzone_for_monster(monster, scenario.target_part)

    rotation = resolve_rotation(weapon.weapon_type, scenario.rotation_id)
    if weapon.weapon_type in RANGED_WEAPONS:
        sharp_raw_mult, sharp_ele_mult = (1.0, 1.0)
    else:
        segments = _sharpness_segments(weapon, effect_skills.get("Handicraft", 0))
        top_color = next(color for color in SHARPNESS_ORDER if segments.get(color, 0) > 0)
        sharp_raw_mult, sharp_ele_mult = SHARPNESS_MODIFIERS[top_color]
    audit_notes: list[str] = []

    ab_flat, ab_pct = ATTACK_BOOST_TABLE.get(effect_skills.get("Attack Boost", 0), (0.0, 0.0))
    agi_lvl = effect_skills.get("Agitator", 0)
    agi_raw = AGITATOR_RAW_TABLE.get(agi_lvl, 0.0) * scenario.agitator_uptime
    agi_aff = AGITATOR_AFF_TABLE.get(agi_lvl, 0.0) * scenario.agitator_uptime

    burst_lvl = min(5, effect_skills.get("Burst", 0))
    burst_raw, burst_ele = burst_bonus(weapon.weapon_type, burst_lvl)
    burst_raw *= scenario.burst_uptime
    burst_ele *= scenario.burst_uptime

    peak_raw = PEAK_PERFORMANCE_RAW_TABLE.get(effect_skills.get("Peak Performance", 0), 0.0) * scenario.peak_performance_uptime
    counter_raw = COUNTERSTRIKE_RAW_TABLE.get(effect_skills.get("Counterstrike", 0), 0.0) * scenario.counterstrike_uptime
    coal_raw = 0.0
    resentment_raw = RESENTMENT_RAW_TABLE.get(effect_skills.get("Resentment", 0), 0.0) * scenario.resentment_uptime
    adrenaline_raw = ADRENALINE_RUSH_RAW_TABLE.get(effect_skills.get("Adrenaline Rush", 0), 0.0) * scenario.adrenaline_rush_uptime
    foray_raw = FORAY_RAW_TABLE.get(effect_skills.get("Foray", 0), 0.0) * scenario.foray_uptime
    item_raw = (
        MIGHT_SEED_RAW_BONUS * scenario.might_seed_uptime
        + DEMON_POWDER_RAW_BONUS * scenario.demon_powder_uptime
        + scenario.food_attack_bonus
    )

    og_pct = OFFENSIVE_GUARD_RAW_PCT_TABLE.get(effect_skills.get("Offensive Guard", 0), 0.0) * scenario.offensive_guard_uptime
    mantle_pct = MANTLE_RAW_PCT_BONUS * scenario.mantle_uptime
    ambush_pct = AMBUSH_RAW_PCT_TABLE.get(effect_skills.get("Ambush", 0), 0.0) * scenario.ambush_uptime
    heroics_pct = HEROICS_RAW_PCT_TABLE.get(effect_skills.get("Heroics", 0), 0.0) * scenario.heroics_uptime
    fortify_pct = min(2, scenario.fortify_stacks) * 0.10
    horn_pct = 0.05 * scenario.hunting_horn_attack_uptime

    # Active set ranks are represented by their required piece count in the
    # data, therefore the rank is read from ActiveSkillDetail instead.
    powerhouse_raw = {0: 0.0, 1: 10.0, 2: 25.0}.get(_set_rank(detail_by_name, "Doshaguma's Might"), 0.0)
    powerhouse_raw *= 1.0 if rotation.category == "offset" else 0.0
    burst_boost_raw = {0: 0.0, 1: 8.0, 2: 18.0}.get(_set_rank(detail_by_name, "Ebony Odogaron's Power"), 0.0)
    burst_boost_raw *= scenario.burst_uptime if burst_lvl else 0.0

    flat_raw_bonus = (
        agi_raw + burst_raw + peak_raw + counter_raw + coal_raw + resentment_raw
        + adrenaline_raw + foray_raw + item_raw + powerhouse_raw + burst_boost_raw
    )
    pct_raw_bonus = prod(1.0 + bonus for bonus in (
        ab_pct, og_pct, mantle_pct, ambush_pct, heroics_pct, fortify_pct, horn_pct,
    )) - 1.0
    total_raw = (weapon.raw * (1.0 + pct_raw_bonus)) + ab_flat + flat_raw_bonus

    if flat_raw_bonus or pct_raw_bonus:
        audit_notes.append(
            f"Bônus aproximados de raw: fixo +{round(ab_flat + flat_raw_bonus, 1)}, percentual +{round(pct_raw_bonus * 100, 1)}%."
        )

    wound_bonus = scenario.wound_hitzone_bonus if (scenario.wound_active or hitzone.is_wound) else 0.0

    def effective_hit_hitzone(hit) -> float:
        base_hz = physical_hitzone_for_hit(hit, weapon.weapon_type, hitzone)
        if wound_bonus > 0 and hit.damage_kind not in {"shell", "impact_phial", "element_phial"}:
            return min(100.0, base_hz + wound_bonus)
        return base_hz

    phys_base_hzv = physical_hitzone_for_weapon(weapon.weapon_type, hitzone)
    effective_phys_hzv = min(100.0, phys_base_hzv + wound_bonus)
    if wound_bonus > 0:
        audit_notes.append(f"Ferida ativa aplicada: +{round(wound_bonus, 1)} de hitzone físico nos golpes elegíveis.")

    ce_aff = CRITICAL_EYE_TABLE.get(effect_skills.get("Critical Eye", 0), 0.0)
    wex_lvl = effect_skills.get("Weakness Exploit", 0)
    weak_point = effective_phys_hzv >= 45
    wex_aff = WEAKNESS_EXPLOIT_TABLE.get(wex_lvl, 0.0) * scenario.weakness_exploit_uptime if weak_point else 0.0
    wound_aff = WEAKNESS_EXPLOIT_WOUND_TABLE.get(wex_lvl, 0.0) * scenario.weakness_exploit_uptime if (scenario.wound_active or hitzone.is_wound) else 0.0
    max_might_aff = MAXIMUM_MIGHT_AFF_TABLE.get(effect_skills.get("Maximum Might", 0), 0.0) * scenario.maximum_might_uptime
    latent_aff = LATENT_POWER_AFF_TABLE.get(effect_skills.get("Latent Power", 0), 0.0) * scenario.latent_power_uptime
    frenzy_aff = ANTIVIRUS_AFF_TABLE.get(effect_skills.get("Antivirus", 0), 0.0) * scenario.frenzy_antivirus_uptime
    foray_aff = FORAY_AFF_TABLE.get(effect_skills.get("Foray", 0), 0.0) * scenario.foray_uptime

    total_aff = weapon.affinity + ce_aff + wex_aff + agi_aff + wound_aff + max_might_aff + latent_aff + frenzy_aff + foray_aff
    if max_might_aff or latent_aff or frenzy_aff:
        audit_notes.append(
            f"Bônus aproximados de afinidade: Maximum Might +{round(max_might_aff, 1)}%, Latent Power +{round(latent_aff, 1)}%, Antivirus +{round(frenzy_aff, 1)}%."
        )
    capped_aff = min(100.0, max(-100.0, total_aff))
    aff_decimal = capped_aff / 100.0

    cb_mult = CRITICAL_BOOST_TABLE.get(effect_skills.get("Critical Boost", 0), 1.25)
    crit_mod = (1.0 + aff_decimal * (cb_mult - 1.0)) if aff_decimal >= 0 else (1.0 + aff_decimal * 0.25)

    total_ele = weapon.element_val
    is_status = weapon.element_type in {
        ElementType.POISON, ElementType.PARALYSIS, ElementType.SLEEP, ElementType.BLAST
    }
    ele_cap_val = 0.0
    element_capped = False
    if weapon.element_type != ElementType.NONE:
        ele_skill_name = f"{weapon.element_type.value} Attack"
        ele_lvl = effect_skills.get(ele_skill_name, 0)
        ele_multiplier, ele_flat = attack_element_components(ele_lvl, status=is_status)
        absorb_ele = 0.0 if is_status else absorption_bonus(
            weapon.weapon_type, effect_skills.get("Elemental Absorption", 0), scenario.elemental_absorption_hits
        ) * scenario.elemental_absorption_uptime
        hostility_ele = {0: 0.0, 1: 10.0, 2: 20.0}.get(_set_rank(detail_by_name, "Gogmapocalypse"), 0.0)
        hostility_ele *= scenario.agitator_uptime
        if is_status:
            burst_ele = 0.0
            hostility_ele = 0.0
        coal_multiplier = coalescence_multiplier(
            weapon.weapon_type, effect_skills.get("Coalescence", 0), scenario.coalescence_uptime, is_status
        )
        total_ele = weapon.element_val * ele_multiplier * coal_multiplier + ele_flat + burst_ele + absorb_ele + hostility_ele
        if not is_status and weapon.element_val > 0:
            ele_cap_val = element_cap(weapon.element_val)
            if total_ele > ele_cap_val:
                total_ele = ele_cap_val
                element_capped = True
                audit_notes.append(
                    f"Teto elemental atingido: limitado a {round(ele_cap_val * 10, 1)} exibidos (base {round(weapon.element_val * 10, 1)})."
                )
        if total_ele != weapon.element_val:
            audit_notes.append(
                f"Bônus aproximados de elemento/status: +{round(total_ele - weapon.element_val, 1)}."
            )

    base_cycle_time = rotation.cycle_time_seconds
    rotation_time_mult = 1.0
    if effect_skills.get("Focus", 0) and any(hit.charged for hit in rotation.hits):
        rotation_time_mult *= FOCUS_TIME_MULTIPLIER.get(min(3, effect_skills["Focus"]), 1.0)
    if weapon.weapon_type in {WeaponType.SWITCH_AXE, WeaponType.CHARGE_BLADE}:
        rotation_time_mult *= RAPID_MORPH_TIME_MULTIPLIER.get(min(3, effect_skills.get("Rapid Morph", 0)), 1.0)
    if weapon.weapon_type == WeaponType.LONG_SWORD and "iai" in rotation.name.casefold():
        rotation_time_mult *= 1.0 - min(3, effect_skills.get("Quick Sheathe", 0)) * 0.015
    cycle_time = max(0.1, base_cycle_time * rotation_time_mult)

    def affinity_for_hit(hit):
        if not hit.can_crit:
            return 0.0
        value = weapon.affinity + ce_aff + agi_aff + max_might_aff + latent_aff + frenzy_aff + foray_aff + wound_aff
        if effective_hit_hitzone(hit) >= 45:
            value += WEAKNESS_EXPLOIT_TABLE.get(wex_lvl, 0) * scenario.weakness_exploit_uptime
        return max(-1.0, min(1.0, value / 100.0))

    sharpness_cost = sum(hit.sharpness_consumed * hit.hit_count for hit in rotation.hits)
    critical_cost = sum(hit.sharpness_consumed * hit.hit_count * max(0, affinity_for_hit(hit)) for hit in rotation.hits)
    avg_sharp_raw, avg_sharp_ele, sharpness_consumed, top_sharpness_cycles = _sharpness_projection(
        weapon, effect_skills, scenario, sharpness_cost, cycle_time, capped_aff, critical_cost
    )
    effective_raw = total_raw * crit_mod * sharp_raw_mult
    effective_ele = total_ele if is_status else total_ele * sharp_ele_mult
    hits_breakdown: list[HitAudit] = []
    cycle_total_damage = 0.0
    sustained_cycle_total = 0.0
    physical_cycle_damage = 0.0
    elemental_cycle_damage = 0.0
    status_buildup = 0.0

    phys_hzv = effective_phys_hzv
    ele_hzv = elemental_hitzone_for_element(weapon.element_type, hitzone)
    critical_element_bonus = element_crit_bonus(weapon.weapon_type, effect_skills.get("Critical Element", 0))
    critical_element_bonus *= scenario.critical_element_uptime
    charge_master_bonus = charged_bonus(weapon.weapon_type, effect_skills.get("Charge Master", 0))
    charge_master_bonus *= scenario.charge_master_uptime
    artillery_bonus = ARTILLERY_BONUS.get(min(3, effect_skills.get("Artillery", 0)), 0.0)
    status_crit_bonus = critical_status_bonus(weapon.weapon_type, effect_skills.get("Critical Status", 0))

    for hit in rotation.hits:
        mv = hit.motion_value if scenario.custom_motion_value is None else scenario.custom_motion_value
        hit_hz = effective_hit_hitzone(hit)
        hit_aff = affinity_for_hit(hit)
        raw_normal = total_raw * (sharp_raw_mult if hit.uses_sharpness else 1.0) * (mv / 100.0) * (hit_hz / 100.0)
        raw_crit = raw_normal * (cb_mult if hit.can_crit else 1.0)
        expected_raw_hit = (raw_normal * (1.0 - hit_aff) + raw_crit * hit_aff) if hit_aff >= 0 else raw_normal * (1.0 + hit_aff * .25)
        special_mult = 1.0
        if hit.damage_kind == "shell":
            special_mult += artillery_bonus
        if hit.damage_kind == "impact_phial":
            special_mult += min(3, effect_skills.get("Artillery", 0)) * .10
        if weapon.weapon_type in RANGED_WEAPONS:
            ammo_skill = {"normal": "Normal Shots", "pierce": "Piercing Shots", "spread": "Spread/Power Shots"}.get(hit.ammo_kind)
            if ammo_skill and effect_skills.get(ammo_skill, 0):
                special_mult *= 1.05
            if hit.rapid_fire and effect_skills.get("Rapid Fire Up", 0):
                special_mult *= 1.05
            if hit.special_ammo:
                special_mult *= 1.0 + .10 * min(2, effect_skills.get("Special Ammo Boost", 0))
        if hit.airborne and effect_skills.get("Airborne", 0):
            special_mult *= 1.10
        raw_normal *= special_mult
        raw_crit *= special_mult
        expected_raw_hit *= special_mult

        expected_element_crit = 1.0 + max(0.0, hit_aff) * critical_element_bonus
        ele_damage = 0.0 if is_status else (
            total_ele * (sharp_ele_mult if hit.uses_sharpness else 1.0) * hit.element_mult * (ele_hzv / 100.0)
            * expected_element_crit * (1.0 + (charge_master_bonus if hit.charged else 0.0))
        )
        if hit.fixed_fire:
            ele_damage = (hit.fixed_fire + min(3, effect_skills.get("Artillery", 0)) * 3) * hitzone.fire / 100.0
        if is_status:
            proc_chance = 1.0 if weapon.weapon_type in RANGED_WEAPONS else 1.0 / 3.0
            status_buildup += (
                total_ele * hit.element_mult * hit.hit_count * proc_chance
                * (1 + max(0, hit_aff) * status_crit_bonus)
                * (1 + (charge_master_bonus if hit.charged else 0))
            )
        total_hit_dmg = (expected_raw_hit + ele_damage) * hit.hit_count
        physical_cycle_damage += expected_raw_hit * hit.hit_count
        elemental_cycle_damage += ele_damage * hit.hit_count
        cycle_total_damage += total_hit_dmg
        sustained_cycle_total += (
            expected_raw_hit * (avg_sharp_raw / max(sharp_raw_mult, 0.01) if hit.uses_sharpness else 1)
            + ele_damage * (avg_sharp_ele / max(sharp_ele_mult, 0.01) if hit.uses_sharpness else 1)
        ) * hit.hit_count

        hits_breakdown.append(HitAudit(
            hit_name=hit.hit_name,
            motion_value=mv,
            physical_damage=round(raw_normal * hit.hit_count, 1),
            crit_physical_damage=round(raw_crit * hit.hit_count, 1),
            elemental_damage=round(ele_damage * hit.hit_count, 1),
            expected_damage=round(total_hit_dmg, 1),
            hit_count=hit.hit_count,
        ))

    status_damage = 0.0
    if is_status:
        audit_notes.append(
            f"Status: {round(status_buildup, 1)} de acúmulo estimado por rotação; dano de procs não modelado. "
            "Estrelas de fraqueza não fornecem limiares, duração ou dano de Explosão/Veneno."
        )

    practical_dps = cycle_total_damage / cycle_time if cycle_time > 0 else 0.0
    damage_per_min = practical_dps * 60.0
    sustained_dps = sustained_cycle_total / cycle_time if cycle_time > 0 else 0.0
    sustained_damage_per_min = sustained_dps * 60.0
    total_defense, max_defense, total_resistances, survivability_score = _defense_summary(
        equip, weapon, scenario, effect_skills
    )
    combined_score = round((practical_dps * 0.80) + (survivability_score * 0.20), 1)

    if rotation.timing_is_estimate:
        audit_notes.append("Tempo estimado e motion values legados sem validação no patch atual; DPS não é medição no jogo.")
    audit_notes.append(WEAPON_LIMITATIONS[weapon.weapon_type])
    audit_notes.append(
        "DPS sustentado é somente projeção de afiamento, sem afiar, recarregar, recuperar vigor ou reposicionar. "
        "Uptimes médios não simulam a sequência nem a correlação dos buffs."
    )
    if any(effect_skills.get(name, 0) for name in TEMPO_SKILLS):
        audit_notes.append("Focus/Rapid Morph/Quick Sheathe usam ajustes globais aproximados de tempo, não frames medidos por ação.")
    if effect_skills.get("Constitution", 0) or effect_skills.get("Stamina Surge", 0):
        audit_notes.append("Constitution/Stamina Surge não aceleram animações; seu efeito no vigor ainda não é simulado.")
    if effect_skills.get("Handicraft", 0) and not weapon.weapon_features.get("handicraft"):
        audit_notes.append("Sem extensão de Handicraft disponível nos dados desta arma; nenhuma barra extra foi presumida.")
    if any(_set_rank(detail_by_name, name) for name in ("Doshaguma's Might", "Gogmapocalypse")):
        audit_notes.append("Powerhouse/Hostility usam aproximações de ativação e duração; precisam de validação temporal no jogo.")
    if weapon.element_type not in {
        ElementType.NONE, ElementType.POISON, ElementType.PARALYSIS, ElementType.SLEEP, ElementType.BLAST,
    }:
        audit_notes.append(
            f"Elemento: valor interno {round(total_ele, 1)} (exibido {round(total_ele * 10, 1)}) "
            f"× HZ {round(ele_hzv, 1)}/100, com afiamento e multiplicador elemental de cada golpe."
        )
    if weapon.weapon_type not in RANGED_WEAPONS and avg_sharp_raw < sharp_raw_mult:
        audit_notes.append(
            f"Afiamento de longo prazo: {round(avg_sharp_raw, 3)}x raw em {int(scenario.hunt_duration_seconds)}s; "
            f"cor máxima dura cerca de {round(top_sharpness_cycles, 1)} rotações."
        )
    inactive_set_names = [detail.name for detail in skill_details if detail.kind in {"group", "set"} and not detail.active]
    if inactive_set_names:
        audit_notes.append("Não aplicadas por peças insuficientes: " + ", ".join(sorted(inactive_set_names)) + ".")

    modeled_names = set(DIRECT_DAMAGE_SKILLS) | set(TEMPO_SKILLS) | set(SURVIVAL_SKILLS) | {
        "Handicraft", "Razor Sharp", "Master's Touch", "Protective Polish", "Critical Status", "Elemental Absorption",
        "Fire Attack", "Water Attack", "Thunder Attack", "Ice Attack", "Dragon Attack",
        "Poison Attack", "Paralysis Attack", "Sleep Attack", "Blast Attack",
    }
    modeled_skills = sorted(name for name in effect_skills if name in modeled_names)
    informational_skills = sorted(name for name in effect_skills if name not in modeled_names)

    return BuildResult(
        legality=validate_build(equip),
        engine_version=ENGINE_VERSION,
        calculation_status="partial",
        rule_sources=RULE_SOURCES + ([rotation.source_url] if rotation.source_url else []),
        total_raw=round(total_raw, 1),
        effective_raw=round(effective_raw, 1),
        total_affinity=round(total_aff, 1),
        capped_affinity=round(capped_aff, 1),
        total_element=round(total_ele, 1),
        effective_element=round(effective_ele, 1),
        total_element_display=round(total_ele * 10, 1),
        effective_element_display=round(effective_ele * 10, 1),
        element_capped=element_capped,
        element_cap_display=round(ele_cap_val * 10, 1),
        wound_hitzone_applied=round(wound_bonus, 1),
        target_part_name=scenario.target_part,
        physical_hitzone=round(phys_hzv, 1),
        elemental_hitzone=round(ele_hzv, 1),
        physical_damage_per_cycle=round(physical_cycle_damage, 1),
        elemental_damage_per_cycle=round(elemental_cycle_damage, 1),
        crit_multiplier=cb_mult,
        sharpness_raw_mult=sharp_raw_mult,
        sharpness_ele_mult=sharp_ele_mult,
        average_sharpness_raw_mult=round(avg_sharp_raw, 4),
        average_sharpness_ele_mult=round(avg_sharp_ele, 4),
        sharpness_consumed_per_cycle=sharpness_consumed,
        top_sharpness_cycles=round(top_sharpness_cycles, 1),
        total_defense=total_defense,
        max_defense=max_defense,
        total_resistances=total_resistances,
        survivability_score=survivability_score,
        status_buildup_per_cycle=round(status_buildup, 1),
        estimated_status_damage_per_cycle=round(status_damage, 1),
        modeled_skills=modeled_skills,
        informational_skills=informational_skills,
        weapon_mechanics=_weapon_mechanics(weapon, rotation, effect_skills),
        active_skills=skills,
        skill_details=skill_details,
        damage_per_cycle=round(cycle_total_damage, 1),
        practical_dps=round(practical_dps, 1),
        damage_per_min=round(damage_per_min, 1),
        sustained_damage_per_cycle=round(sustained_cycle_total, 1),
        sustained_dps=round(sustained_dps, 1),
        sustained_damage_per_min=round(sustained_damage_per_min, 1),
        combined_score=combined_score,
        hits_breakdown=hits_breakdown,
        slot_warnings=warnings,
        audit_notes=audit_notes,
        rotation_id=rotation.id,
        rotation_name=rotation.name,
        cycle_time_seconds=round(cycle_time, 3),
    )

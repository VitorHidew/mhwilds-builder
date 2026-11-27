"""Situation-aware Gogma Artian recommendations used by the optimizer UI."""

from app.data import MONSTERS_DB, WEAPONS_DB
from app.artian_rules import BASE_ELEMENT_DISPLAY
from app.engine import hitzone_for_monster
from app.meta_presets import META_PRESETS_BY_ID
from app.models import (
    CustomGogWeapon, ElementType, GogRecommendationRequest,
    GogWeaponOption, GogWeaponRecommendation, SharpnessLevel, WeaponType,
)
from app.rotations import resolve_rotation


GOG_SOURCES = [
    "https://www.phantombrawlers.com/mhwilds/Artian",
    "https://lescarnetsdelawycademie.fr/gogmazios-weapons/",
    "https://www.icy-veins.com/monster-hunter-wilds/gogma-artian-weapons",
    "https://monsterhunterhq.com/monster-hunter-wilds/monster-hunter-wilds-complete-gogmazios-artian-weapons-crafting-guide/",
    "https://game8.co/games/Monster-Hunter-Wilds/archives/571311",
    "https://www.monsterhunterwiki.org/wiki/Artian_Weapons_%28MHWilds%29",
    "https://www.youtube.com/watch?v=ERdbP00S8iQ",
    "https://github.com/WiseHorror/Gogma-Artian-Roll-Planner",
]

ELEMENT_FOCUSED = {
    WeaponType.SWORD_AND_SHIELD, WeaponType.DUAL_BLADES, WeaponType.SWITCH_AXE,
    WeaponType.CHARGE_BLADE, WeaponType.INSECT_GLAIVE, WeaponType.LIGHT_BOWGUN,
    WeaponType.BOW,
}

WEAPON_LABELS = {
    WeaponType.GREAT_SWORD: "Espadão", WeaponType.LONG_SWORD: "Espada Longa",
    WeaponType.SWORD_AND_SHIELD: "Espada e Escudo", WeaponType.DUAL_BLADES: "Duplas-Lâminas",
    WeaponType.HAMMER: "Martelo", WeaponType.HUNTING_HORN: "Berrante de Caça",
    WeaponType.LANCE: "Lança", WeaponType.GUNLANCE: "Lançarma",
    WeaponType.SWITCH_AXE: "Espada Machado", WeaponType.CHARGE_BLADE: "Lâmina Dínamo",
    WeaponType.INSECT_GLAIVE: "Glaive Inseto", WeaponType.LIGHT_BOWGUN: "Fuzilarco Leve",
    WeaponType.HEAVY_BOWGUN: "Fuzilarco Pesado", WeaponType.BOW: "Arco",
}

ELEMENT_LABELS = {
    ElementType.FIRE: "Fogo", ElementType.WATER: "Água", ElementType.THUNDER: "Trovão",
    ElementType.ICE: "Gelo", ElementType.DRAGON: "Dragão", ElementType.NONE: "Sem elemento",
}


def _best_element(monster, target_part: str = "Media_Ponderada") -> tuple[ElementType, float]:
    hitzone = hitzone_for_monster(monster, target_part)
    values = {
        ElementType.FIRE: hitzone.fire, ElementType.WATER: hitzone.water,
        ElementType.THUNDER: hitzone.thunder, ElementType.ICE: hitzone.ice,
        ElementType.DRAGON: hitzone.dragon,
    }
    return max(values.items(), key=lambda row: row[1])


def _situation_skill(weapon_type: WeaponType, rotation_category: str, elemental: bool) -> tuple[str, str]:
    if rotation_category == "offset" or weapon_type == WeaponType.GREAT_SWORD:
        return "Doshaguma's Might", "Powerhouse favorece Offset e Power Clash desta rotação."
    if elemental:
        return "Gogmapocalypse", "Mutual Hostility reforça o dano elemental quando o monstro entra em fúria."
    if weapon_type in {WeaponType.DUAL_BLADES, WeaponType.BOW}:
        return "Fulgur Anjanath's Will", "Second Wind melhora a sustentação de stamina da rotação."
    return "Ebony Odogaron's Power", "Burst Boost favorece pressão contínua e sequências de vários golpes."


def gog_skill_pair(weapon_type: WeaponType, rotation_category: str, elemental: bool) -> tuple[str, str, str]:
    """Return the two desired Gog rolls and the armor plan that activates both.

    Gog skills are set/group skills. A roll without matching armor is not a
    completed build, so every perfect recommendation reserves the required
    armor pieces instead of treating the second roll as a generic luxury.
    """
    primary, reason = _situation_skill(weapon_type, rotation_category, elemental)
    return primary, "Lord's Soul", reason


def gog_set_requirements(primary_skill: str, second_skill: str | None = None) -> dict[str, int]:
    thresholds = {
        "Doshaguma's Might": 2,
        "Gogmapocalypse": 2,
        "Ebony Odogaron's Power": 2,
        "Fulgur Anjanath's Will": 2,
        "Lord's Soul": 3,
    }
    required = {primary_skill: thresholds.get(primary_skill, 1)}
    if second_skill:
        required[second_skill] = thresholds.get(second_skill, 1)
    return required


def recommend_gog_weapon(payload: GogRecommendationRequest) -> GogWeaponRecommendation:
    monster = next((item for item in MONSTERS_DB if item.id == payload.monster_id), None)
    if not monster:
        raise ValueError(f"Monstro não encontrado: {payload.monster_id}")

    preset = META_PRESETS_BY_ID.get(payload.preset_id or "")
    if not preset or preset.weapon_recommendation_mode != "gog":
        raise ValueError(
            "Builds de progressão recomendam somente armas normais das árvores do guia. "
            "Escolha uma categoria de endgame para receber uma recomendação GogmaArtiana."
        )
    if preset.hunter_rank_min < 100:
        raise ValueError(
            "Armas GogmaArtianas só são recomendadas para builds RC100+. "
            "Escolha um perfil de endgame RC100+ para liberar esta recomendação."
        )
    rotation = resolve_rotation(payload.weapon_type, payload.rotation_id)
    best_element, element_hitzone = _best_element(monster, payload.target_part)
    elemental = payload.weapon_type in ELEMENT_FOCUSED and element_hitzone >= 8
    situation_skill, second_skill, skill_reason = gog_skill_pair(
        payload.weapon_type, rotation.category, elemental
    )
    focus = "Foco Elemental" if elemental else "Foco em Ataque"
    weapon_label = WEAPON_LABELS[payload.weapon_type]
    element_label = ELEMENT_LABELS[best_element]
    situation = f"{monster.name} · {rotation.name} · {payload.target_part}"

    if elemental:
        perfect_reinforcements = ["Elemento EX ×2", "Ataque EX ×2", "Afiamento EX ×1"]
        accessible_reinforcements = ["Elemento III ou superior ×2", "Ataque útil ×2", "Afiamento ×1"]
        perfect_rolls = ["element_ex", "element_ex", "attack_ex", "attack_ex", "sharpness_ex"]
        accessible_rolls = ["element_ii", "element_ii", "attack_iii", "attack_iii", "sharpness_i"]
        gog_focus = "element"
    else:
        perfect_reinforcements = ["Ataque EX ×2", "Elemento EX ×2", "Afiamento EX ×1"]
        accessible_reinforcements = ["Ataque III ou superior ×2", "Qualquer bônus útil ×2", "Afiamento ×1"]
        perfect_rolls = ["attack_ex", "attack_ex", "element_ex", "element_ex", "sharpness_ex"]
        accessible_rolls = ["attack_iii", "attack_iii", "element_ii", "affinity_ii", "sharpness_i"]
        gog_focus = "attack"

    base = next((weapon for weapon in WEAPONS_DB
                 if weapon.weapon_type == payload.weapon_type and weapon.rarity == 8
                 and not weapon.series and weapon.raw == 190 and weapon.affinity == 5
                 and weapon.slots == [3, 3, 3]), None)
    if not base:
        raise ValueError("Base Artiana R8 não encontrada no catálogo.")
    is_bowgun = payload.weapon_type in {WeaponType.LIGHT_BOWGUN, WeaponType.HEAVY_BOWGUN}
    if is_bowgun:
        gog_focus = "attack"
        focus = "Foco em Ataque"
        perfect_rolls = ["attack_ex", "attack_ex", "affinity_ex", "affinity_ex", "attack_iii"]
        accessible_rolls = ["attack_iii", "attack_iii", "affinity_ii", "affinity_ii", "attack_ii"]
    if payload.weapon_type == WeaponType.BOW:
        perfect_rolls = ["element_ex", "element_ex", "attack_ex", "attack_ex", "affinity_ex"]
        accessible_rolls = ["element_ii", "element_ii", "attack_iii", "attack_iii", "affinity_ii"]
    perfect_reinforcements = perfect_rolls
    accessible_reinforcements = accessible_rolls
    common_weapon = dict(
        base_weapon_id=base.id, raw=base.raw + 15, affinity=base.affinity,
        element_display=BASE_ELEMENT_DISPLAY[payload.weapon_type.value],
        weapon_type=payload.weapon_type, element_nature="element", element_type=best_element,
        slots=[3, 3, 3], best_sharpness=SharpnessLevel.WHITE,
        prev_sharpness=SharpnessLevel.BLUE,
        sharpness_units=20,
        shell_type={"attack": "normal", "affinity": "long", "element": "wide"}[gog_focus] if payload.weapon_type == WeaponType.GUNLANCE else None,
        shell_level=4 if payload.weapon_type == WeaponType.GUNLANCE else 0,
        phial=("impact" if gog_focus == "attack" else "element") if payload.weapon_type == WeaponType.CHARGE_BLADE else base.phial,
        ammo=base.ammo, coatings=base.coatings, melody=base.melody,
    )
    if is_bowgun:
        common_weapon.update(element_nature="none", element_type=ElementType.NONE)
    perfect_weapon = CustomGogWeapon(
        name=f"{weapon_label} Gog Alto RNG · {element_label}",
        skill_1=situation_skill, skill_1_lvl=1,
        skill_2=second_skill, skill_2_lvl=1, gog_focus=gog_focus,
        reinforcements=perfect_rolls, **common_weapon,
    )
    accessible_weapon = CustomGogWeapon(
        name=f"{weapon_label} Gog Acessível · {element_label}",
        skill_1=situation_skill, skill_1_lvl=1,
        gog_focus=gog_focus, reinforcements=accessible_rolls, **common_weapon,
    )

    base_artian = (
        f"Artian R8 de {element_label}, totalmente reforçada; use três peças de elemento igual "
        "quando quiser a infusão elemental."
    )
    crafting_steps = [
        "Forje uma Artian R8 e complete os cinco reforços.",
        f"Converta na forja usando materiais de Gogmazios e escolha {focus}.",
        "Use Redefinir Habilidades; a sequência é predeterminada por tipo de arma e elemento.",
        "Teste a sequência em uma arma reserva antes de consumir materiais na arma principal.",
    ]

    perfect = GogWeaponOption(
        id="perfect", label="Modelo de alto RNG para esta situação", rng_level="RNG alto",
        weapon=perfect_weapon, focus=focus, base_artian=base_artian,
        artian_reinforcements=perfect_reinforcements,
        desired_skills=[situation_skill, second_skill], acceptable_second_skill=second_skill,
        crafting_steps=crafting_steps,
        rationale=(
            f"{skill_reason} {second_skill} completa o alvo de alto RNG. "
            "A otimização reserva peças compatíveis para ativar os dois bônus de set/grupo. "
            f"O elemento {element_label} tem o maior HZ elemental ({element_hitzone:g}) "
            f"em {payload.target_part} para {monster.name}."
        ),
    )
    accessible = GogWeaponOption(
        id="accessible", label="Arma forte com uma habilidade necessária", rng_level="RNG reduzido",
        weapon=accessible_weapon, focus=focus, base_artian=base_artian,
        artian_reinforcements=accessible_reinforcements,
        desired_skills=[situation_skill], acceptable_second_skill="Aceite qualquer segunda habilidade",
        crafting_steps=crafting_steps[:3],
        rationale=(
            f"Exige somente {situation_skill}; a outra habilidade aleatória não é requisito. "
            f"{skill_reason} É a rota recomendada para começar a usar a Gogartiana sem perseguir uma rolagem perfeita."
        ),
    )

    return GogWeaponRecommendation(
        weapon_type=payload.weapon_type, monster_id=monster.id, monster_name=monster.name,
        best_element=best_element, target_part=payload.target_part,
        element_hitzone=element_hitzone, situation=situation, perfect=perfect,
        accessible=accessible, source_urls=GOG_SOURCES,
    )

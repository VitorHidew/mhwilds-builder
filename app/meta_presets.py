"""Versioned optimizer profiles used to generate the local meta-build cache."""

from app.models import MetaBuildPreset, WeaponType
from app.progression_rules import GUIDE_URLS


META_SOURCES = [
    "https://www.switchbladegaming.com/monster-hunter-wilds/best-builds-all-weapons/",
    "https://game8.co/games/Monster-Hunter-Wilds/archives/500759",
    "https://game8.co/games/Monster-Hunter-Wilds/archives/545602",
    "https://www.onehitkill.space/mh-wilds/tu4-meta-builds/",
    "https://github.com/nztom/wilds-ai-expert/blob/master/memory/mh-wilds/current_meta_notes.md",
    "https://www.reddit.com/r/MonsterHunterMeta/comments/1rcjh62/10410100_mh_wilds_dual_blades_guide_and_set/",
    "https://mobalytics.gg/mhw/builds/endgame-dual-blades-meta",
    "https://questduo.com/monster-hunter-wilds/great-sword/",
    "https://www.monsterhunterwiki.org/wiki/Artian_Weapons_%28MHWilds%29",
    "https://www.youtube.com/watch?v=ERdbP00S8iQ",
    "https://docs.wilds.mhdb.io/",
]

CORE_BY_WEAPON: dict[WeaponType, dict[str, int]] = {
    WeaponType.GREAT_SWORD: {"Focus": 3, "Critical Boost": 5, "Weakness Exploit": 5},
    WeaponType.LONG_SWORD: {"Critical Boost": 5, "Weakness Exploit": 5, "Quick Sheathe": 3},
    WeaponType.SWORD_AND_SHIELD: {"Critical Boost": 5, "Weakness Exploit": 5, "Burst": 3},
    WeaponType.DUAL_BLADES: {"Burst": 5, "Critical Element": 3, "Weakness Exploit": 5, "Marathon Runner": 3, "Stamina Surge": 3},
    WeaponType.HAMMER: {"Charge Up": 3, "Critical Boost": 5, "Weakness Exploit": 5},
    WeaponType.HUNTING_HORN: {"Horn Maestro": 2, "Critical Boost": 5, "Weakness Exploit": 5},
    WeaponType.LANCE: {"Offensive Guard": 3, "Critical Boost": 5, "Weakness Exploit": 5},
    WeaponType.GUNLANCE: {"Artillery": 3, "Load Shells": 2, "Offensive Guard": 3},
    WeaponType.SWITCH_AXE: {"Rapid Morph": 3, "Power Prolonger": 3, "Critical Boost": 5},
    WeaponType.CHARGE_BLADE: {"Artillery": 3, "Load Shells": 2, "Rapid Morph": 3},
    WeaponType.INSECT_GLAIVE: {"Power Prolonger": 3, "Burst": 5, "Weakness Exploit": 5},
    WeaponType.LIGHT_BOWGUN: {"Normal Shots": 1, "Ballistics": 3, "Critical Boost": 5},
    WeaponType.HEAVY_BOWGUN: {"Spread/Power Shots": 1, "Ballistics": 3, "Critical Boost": 5},
    WeaponType.BOW: {"Constitution": 5, "Stamina Surge": 3, "Marathon Runner": 3, "Tetrad Shot": 3, "Burst": 5},
}

# Burst is valuable only for weapons that can sustain repeated hits. Slow,
# commitment-heavy weapons instead invest their spare slots in their own core
# mechanic and reliable affinity/critical damage.
WEAPON_DAMAGE_PRIORITIES: dict[WeaponType, dict[str, int]] = {
    WeaponType.GREAT_SWORD: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Attack Boost": 4, "Focus": 3, "Offensive Guard": 2},
    WeaponType.LONG_SWORD: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Quick Sheathe": 3, "Burst": 3},
    WeaponType.SWORD_AND_SHIELD: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Burst": 5, "Attack Boost": 3},
    WeaponType.DUAL_BLADES: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Element": 3, "Burst": 5, "Constitution": 3},
    WeaponType.HAMMER: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Charge Up": 3, "Slugger": 2},
    WeaponType.HUNTING_HORN: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Horn Maestro": 2, "Burst": 3},
    WeaponType.LANCE: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Agitator": 4, "Offensive Guard": 3, "Guard": 3, "Guard Up": 3},
    WeaponType.GUNLANCE: {"Artillery": 3, "Load Shells": 2, "Offensive Guard": 3, "Agitator": 4, "Attack Boost": 3, "Guard": 3, "Burst": 5},
    WeaponType.SWITCH_AXE: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Rapid Morph": 3, "Power Prolonger": 3, "Burst": 4, "Flayer": 4, "Counterstrike": 3},
    WeaponType.CHARGE_BLADE: {"Artillery": 3, "Load Shells": 2, "Rapid Morph": 3, "Offensive Guard": 3, "Weakness Exploit": 4, "Critical Boost": 4},
    WeaponType.INSECT_GLAIVE: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Burst": 5, "Power Prolonger": 3, "Antivirus": 3, "Counterstrike": 3},
    WeaponType.LIGHT_BOWGUN: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Ballistics": 3, "Burst": 5, "Critical Element": 3},
    WeaponType.HEAVY_BOWGUN: {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 5, "Attack Boost": 4, "Ballistics": 3, "Spread/Power Shots": 1, "Peak Performance": 3},
    WeaponType.BOW: {"Weakness Exploit": 5, "Critical Element": 3, "Burst": 5, "Constitution": 5, "Stamina Surge": 3, "Marathon Runner": 3, "Tetrad Shot": 3},
}

# Gunlance is intentionally not here: Full Burst can sustain Burst despite the
# weapon's commitment, while the other three do not keep it reliably active.
SLOW_WEAPONS = {WeaponType.GREAT_SWORD, WeaponType.HAMMER, WeaponType.HEAVY_BOWGUN}


def comfort_priorities_for(weapon_type: WeaponType) -> dict[str, int]:
    """Video-guided comfort priority: Immunizer makes Recovery Speed more valuable."""
    if weapon_type in SLOW_WEAPONS:
        return {"Recovery Speed": 3, "Divine Blessing": 2, "Speed Eating": 1, "Stun Resistance": 3}
    return {"Recovery Speed": 3, "Speed Eating": 2, "Divine Blessing": 1, "Stun Resistance": 3}

ROTATION_CATEGORY_BY_WEAPON: dict[WeaponType, str] = {
    WeaponType.GREAT_SWORD: "offset",
    WeaponType.LONG_SWORD: "burst",
    WeaponType.SWORD_AND_SHIELD: "sustained",
    WeaponType.DUAL_BLADES: "burst",
    WeaponType.HAMMER: "offset",
    WeaponType.HUNTING_HORN: "sustained",
    WeaponType.LANCE: "counter",
    WeaponType.GUNLANCE: "burst",
    WeaponType.SWITCH_AXE: "burst",
    WeaponType.CHARGE_BLADE: "burst",
    WeaponType.INSECT_GLAIVE: "burst",
    WeaponType.LIGHT_BOWGUN: "sustained",
    WeaponType.HEAVY_BOWGUN: "sustained",
    WeaponType.BOW: "sustained",
}

PROFILE_DATA = {
    "progressao_inicio": {
        "label": "Progressão - Ranque Baixo",
        "description": "Ranque Baixo conforme o guia atualizado da arma; compara somente as árvores e combinações de conjuntos recomendadas.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Divine Blessing": 1, "Speed Eating": 1, "Attack Boost": 1},
        "library_group": "progression", "max_rarity": 4, "use_transcendence": False, "hunter_rank_min": 1,
        "uptime_preset": "default", "core_limit": 1,
    },
    "progressao_lr_final": {
        "label": "Progressão - Ranque Elevado (início)",
        "description": "Primeira troca de equipamento do Ranque Elevado conforme o guia atualizado da arma.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Weakness Exploit": 2, "Critical Eye": 2, "Divine Blessing": 2},
        "library_group": "progression", "max_rarity": 6, "use_transcendence": False, "hunter_rank_min": 8,
        "uptime_preset": "default", "core_limit": 2,
    },
    "progressao_hr_inicio": {
        "label": "Progressão - RC21+",
        "description": "Conjunto de RC21+ comparado dentro das árvores, peças e amuletos indicados pelo guia da arma.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Weakness Exploit": 3, "Critical Eye": 3, "Agitator": 2, "Divine Blessing": 2},
        "library_group": "progression", "max_rarity": 6, "use_transcendence": False, "hunter_rank_min": 21,
        "uptime_preset": "default", "core_limit": 3,
    },
    "progressao_hr_avancado": {
        "label": "Progressão - RC31+",
        "description": "Conjunto de RC31+ do guia, com as variantes de peças comparadas pelo dano prático da rotação.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Weakness Exploit": 4, "Critical Boost": 3, "Agitator": 3, "Critical Eye": 3},
        "library_group": "progression", "max_rarity": 7, "use_transcendence": False, "hunter_rank_min": 31,
        "uptime_preset": "realistic", "core_limit": 4,
    },
    "progressao_hr_41": {
        "label": "Progressão - RC41+",
        "description": "Última etapa do guia de progressão antes dos conjuntos especiais de endgame.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Weakness Exploit": 5, "Critical Boost": 4, "Agitator": 4, "Critical Eye": 4},
        "library_group": "progression", "max_rarity": 8, "use_transcendence": False, "hunter_rank_min": 41,
        "uptime_preset": "realistic", "core_limit": 5,
    },
    "progressao_pre_gog": {
        "label": "Progressão - preparação para Gog",
        "description": "Build R8 determinística para chegar ao farm de Gogmazios antes de exigir uma Gogartiana perfeita.",
        "monster_id": "mon_34", "target": {"Blast Resistance": 1},
        "preferred": {"Blast Resistance": 3, "Partbreaker": 3, "Weakness Exploit": 5, "Agitator": 4},
        "library_group": "progression", "max_rarity": 8, "use_transcendence": True, "hunter_rank_min": 41,
        "uptime_preset": "realistic", "core_limit": 5,
    },
    "dps_max": {
        "label": "DPS Máximo - zero conforto",
        "description": "Prioriza dano esperado e habilidades ofensivas, sem reservar espaço para conforto.",
        "monster_id": "mon_20",
        "target": {},
        "preferred": {"Agitator": 5, "Attack Boost": 5, "Critical Eye": 5, "Weakness Exploit": 5, "Critical Boost": 5, "Burst": 5},
        "library_group": "normal", "uptime_preset": "aggressive", "hunter_rank_min": 100,
    },
    "dps_conforto": {
        "label": "DPS com conforto",
        "description": "Mantém o núcleo de dano e reserva habilidades para recuperação rápida e resistência a atordoamento.",
        "monster_id": "mon_20",
        "target": {"Recovery Speed": 1, "Stun Resistance": 1},
        "preferred": {"Recovery Speed": 3, "Speed Eating": 1, "Stun Resistance": 3, "Weakness Exploit": 5, "Critical Boost": 5, "Agitator": 5},
        "library_group": "normal", "uptime_preset": "realistic", "hunter_rank_min": 100,
    },
    "geral": {
        "label": "Build geral",
        "description": "Configuração estável para a maioria dos monstros; prioriza Recuperação com Immunizer para manter o uptime sem desperdiçar slots em Defesa.",
        "monster_id": "mon_20",
        "target": {},
        "preferred": {"Weakness Exploit": 5, "Critical Boost": 5, "Agitator": 3, "Evade Window": 3, "Recovery Speed": 3},
        "library_group": "normal", "uptime_preset": "realistic", "hunter_rank_min": 100,
    },
    "dano_consistente": {
        "label": "Dano consistente",
        "description": "Favorece dano que permanece ativo em uma caçada normal e evita depender de Heroísmo ou janelas irreais.",
        "monster_id": "mon_20", "target": {},
        "preferred": {"Weakness Exploit": 5, "Critical Boost": 5, "Critical Eye": 4, "Agitator": 4, "Recovery Speed": 3},
        "library_group": "normal", "uptime_preset": "realistic", "hunter_rank_min": 100,
    },
    "farm_partes": {
        "label": "Farm e quebra de partes",
        "description": "Build normal para materiais, mantendo dano consistente e priorizando quebra de partes.",
        "monster_id": "mon_20", "target": {"Partbreaker": 1},
        "preferred": {"Partbreaker": 3, "Weakness Exploit": 5, "Critical Boost": 4, "Agitator": 3},
        "library_group": "normal", "uptime_preset": "realistic", "hunter_rank_min": 100,
    },
    "at_arkveld": {
        "label": "AT Arkveld",
        "description": "Perfil para Arkveld Arquitemperado, com dano em feridas e tolerância a dragão/flagelos.",
        "monster_id": "mon_20",
        "target": {"Blight Resistance": 1},
        "preferred": {"Dragon Resistance": 3, "Blight Resistance": 3, "Recovery Speed": 3, "Weakness Exploit": 5, "Partbreaker": 3, "Agitator": 5}, "hunter_rank_min": 100,
    },
    "at_jin_dahaad": {
        "label": "AT Jin Dahaad",
        "description": "Perfil para Jin Dahaad Arquitemperado, com resistência a gelo e estabilidade contra tremores.",
        "monster_id": "mon_26",
        "target": {"Ice Resistance": 1},
        "preferred": {"Ice Resistance": 3, "Tremor Resistance": 3, "Recovery Speed": 3, "Weakness Exploit": 5, "Agitator": 5}, "hunter_rank_min": 100,
    },
    "at_uth_duna": {
        "label": "AT Uth Duna",
        "description": "Perfil para Uth Duna Arquitemperado, com resistência a água e mobilidade defensiva.",
        "monster_id": "mon_25",
        "target": {"Water Resistance": 1},
        "preferred": {"Water Resistance": 3, "Evade Extender": 2, "Recovery Speed": 3, "Weakness Exploit": 5, "Agitator": 5}, "hunter_rank_min": 100,
    },
    "at_nu_udra": {
        "label": "AT Nu Udra",
        "description": "Perfil para Nu Udra Arquitemperado, com resistência a fogo e proteção contra flagelo.",
        "monster_id": "mon_27",
        "target": {"Fire Resistance": 1},
        "preferred": {"Fire Resistance": 3, "Blight Resistance": 3, "Recovery Speed": 3, "Weakness Exploit": 5, "Agitator": 5}, "hunter_rank_min": 100,
    },
    "gogmazios": {
        "label": "Gogmazios farm",
        "description": "Perfil para farm de Gogmazios, priorizando quebra de partes, fogo e resistência a explosão.",
        "monster_id": "mon_34",
        "target": {"Blast Resistance": 1},
        "preferred": {"Blast Resistance": 3, "Partbreaker": 3, "Recovery Speed": 3, "Fire Attack": 3, "Weakness Exploit": 5, "Agitator": 5}, "hunter_rank_min": 100,
    },
}


def build_meta_presets() -> list[MetaBuildPreset]:
    presets: list[MetaBuildPreset] = []
    for weapon_type in WeaponType:
        core = CORE_BY_WEAPON[weapon_type]
        slug = weapon_type.value.lower().replace("&", "and").replace(" ", "_")
        for profile, data in PROFILE_DATA.items():
            preferred = dict(WEAPON_DAMAGE_PRIORITIES[weapon_type])
            preferred.update(data["preferred"])
            if weapon_type in SLOW_WEAPONS:
                preferred.pop("Burst", None)
            if data.get("uptime_preset") in {"realistic", "comfort"}:
                preferred.update(comfort_priorities_for(weapon_type))
            core_limit = data.get("core_limit")
            preferred.update({
                skill: min(level, core_limit) if core_limit else level
                for skill, level in core.items()
            })
            presets.append(MetaBuildPreset(
                id=f"meta_{slug}_{profile}",
                weapon_type=weapon_type,
                profile=profile,
                name=f"{weapon_type.value} - {data['label']}",
                description=data["description"],
                monster_id=data["monster_id"],
                target_skills=dict(data["target"]),
                preferred_skills=preferred,
                rotation_category=ROTATION_CATEGORY_BY_WEAPON[weapon_type],
                library_group=data.get("library_group", "endgame"),
                max_rarity=data.get("max_rarity"),
                use_transcendence=data.get("use_transcendence", True),
                uptime_preset=data.get("uptime_preset", "realistic"),
                hunter_rank_min=data.get("hunter_rank_min", 100),
                weapon_recommendation_mode=("progression" if data.get("library_group") == "progression" else "gog"),
                source_urls=([GUIDE_URLS[weapon_type]] + META_SOURCES if profile.startswith("progressao_") else META_SOURCES),
            ))
    return presets


META_BUILD_PRESETS = build_meta_presets()
META_PRESETS_BY_ID = {preset.id: preset for preset in META_BUILD_PRESETS}

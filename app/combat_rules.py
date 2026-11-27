"""Versioned combat rules. Element bonuses below use internal (display / 10) units.

References: Les Carnets de la Wycademie /skills-wilds/ and Wiggler's
intermediate_damage_calculation. Rotation timing remains an estimate.
"""
from app.models import WeaponType

ENGINE_VERSION = "2026.09.25.1"
RULE_SOURCES = [
    "https://lescarnetsdelawycademie.fr/skills-wilds/",
    "https://wiggler.pet/other/guides/intermediate_damage_calculation",
    "https://wilds.mhdb.io/en/skills",
    "https://docs.wilds.mhdb.io/#handicraft",
    "https://www.phantombrawlers.com/mhwilds/Artian",
]
HEAVY_ELEMENT = {WeaponType.GREAT_SWORD, WeaponType.HAMMER, WeaponType.HUNTING_HORN,
                 WeaponType.GUNLANCE, WeaponType.SWITCH_AXE, WeaponType.CHARGE_BLADE,
                 WeaponType.HEAVY_BOWGUN}
BOWGUNS = {WeaponType.LIGHT_BOWGUN, WeaponType.HEAVY_BOWGUN}


def burst_bonus(kind, level):
    level = max(0, min(5, level))
    if not level:
        return 0.0, 0.0
    raw = [0, 6, 7, 8, 9, 10] if kind in BOWGUNS | {WeaponType.BOW} else [0, 8, 10, 12, 15, 18]
    if kind in BOWGUNS:
        element = [0] * 6
    elif kind in {WeaponType.GREAT_SWORD, WeaponType.HUNTING_HORN}:
        element = [0, 8, 10, 12, 16, 20]
    elif kind in {WeaponType.DUAL_BLADES, WeaponType.BOW}:
        element = [0, 4, 6, 8, 10, 12]
    else:
        element = [0, 6, 8, 10, 12, 14]
    return raw[level], element[level]


def attack_element_components(level, *, status=False):
    """Separate base multipliers from flat additions, in internal units."""
    table = ([(1, 0), (1.05, 1), (1.10, 2), (1.20, 5)] if status else
             [(1, 0), (1, 4), (1.10, 5), (1.20, 6)])
    return table[max(0, min(3, level))]


def critical_status_bonus(kind, level):
    heavy_status = HEAVY_ELEMENT - {WeaponType.HEAVY_BOWGUN}
    table = [0, .10, .20, .40] if kind in heavy_status else [0, .05, .10, .20]
    return table[max(0, min(3, level))]


def absorption_bonus(kind, level, hits=1):
    level = max(0, min(3, level))
    if not level:
        return 0.0
    values = ([0, 3, 4, 5] if kind in {WeaponType.DUAL_BLADES, WeaponType.BOW}
              else [0, 5, 8, 10] if kind in {WeaponType.GREAT_SWORD, WeaponType.HUNTING_HORN}
              else [0, 4, 5, 6])
    return values[level] + max(0, min(2, hits - 1))


def coalescence_multiplier(kind, level, uptime, status=False):
    per_level = .05 if status or kind not in HEAVY_ELEMENT else .10
    return 1 + per_level * max(0, min(3, level)) * uptime


def critical_element_bonus(kind, level):
    return (.07 if kind in HEAVY_ELEMENT else .05) * max(0, min(3, level))


def charge_master_bonus(kind, level):
    if kind == WeaponType.BOW:
        return [0, .05, .10, .15][max(0, min(3, level))]
    supported = {WeaponType.GREAT_SWORD, WeaponType.LONG_SWORD, WeaponType.SWORD_AND_SHIELD,
                 WeaponType.HAMMER, WeaponType.LANCE, WeaponType.CHARGE_BLADE, WeaponType.INSECT_GLAIVE}
    return [0, .15, .20, .25][max(0, min(3, level))] if kind in supported else 0.0


def element_cap(base_element: float) -> float:
    """MH Wilds elemental cap in internal (display / 10) units."""
    if base_element <= 0:
        return 0.0
    return max(base_element + 35.0, base_element * 1.9)

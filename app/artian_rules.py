"""Displayed elemental values, before skill multipliers, for R8 Artians.

Source: https://www.phantombrawlers.com/mhwilds/Artian (2026-09-23).
The three matching parts' infusion is included in BASE_ELEMENT_DISPLAY.
"""

BASE_ELEMENT_DISPLAY = {
    "Great Sword": 480, "Long Sword": 300, "Sword & Shield": 280,
    "Dual Blades": 270, "Hammer": 350, "Hunting Horn": 350,
    "Lance": 300, "Gunlance": 350, "Switch Axe": 280,
    "Charge Blade": 300, "Insect Glaive": 280, "Bow": 230,
    "Light Bowgun": 0, "Heavy Bowgun": 0,
}
ELEMENT_ROLLS = {
    "Great Sword": (80, 90, 110), "Long Sword": (50, 60, 90),
    "Sword & Shield": (30, 50, 80), "Dual Blades": (20, 30, 50),
    "Hammer": (50, 60, 90), "Hunting Horn": (50, 60, 90),
    "Lance": (50, 60, 90), "Gunlance": (50, 60, 90),
    "Switch Axe": (30, 50, 80), "Charge Blade": (50, 60, 80),
    "Insect Glaive": (30, 50, 80), "Bow": (30, 40, 60),
    "Light Bowgun": (0, 0, 0), "Heavy Bowgun": (0, 0, 0),
}


def element_roll(weapon_type, roll):
    return ELEMENT_ROLLS[weapon_type][{"element_i": 0, "element_ii": 1, "element_ex": 2}[roll]]


def focus_element(weapon_type, focus, *, status=False):
    if weapon_type in {"Bow", "Light Bowgun", "Heavy Bowgun"}:
        return 0
    if weapon_type == "Hunting Horn":
        return {"none": 0, "attack": 30, "affinity": 20, "element": 80}[focus]
    if weapon_type == "Gunlance":
        return {"none": 0, "attack": 40, "affinity": 30, "element": 80}[focus]
    if focus == "affinity":
        return -10 if weapon_type in {"Great Sword", "Hammer"} else -20
    if focus == "element":
        if weapon_type == "Charge Blade" and status:
            return 40
        if weapon_type == "Dual Blades":
            return 30
        return 40 if weapon_type in {"Sword & Shield", "Hammer", "Switch Axe", "Insect Glaive"} else 50
    return 0

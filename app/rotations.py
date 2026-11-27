"""Legacy community rotations, not verified against the current game patch.

Motion values are sourced from chanleyou/mhwilds-calculator (MIT), which in turn
credits the 717999vlr datamine. Its README explicitly leaves v1.040 changes
unchecked. Animation times and composite hit counts need in-game validation.
See docs/production-readiness/01-motor.md before treating these as references.
"""

from app.models import HitDetail, Rotation, WeaponType


SOURCE_URL = "https://github.com/chanleyou/mhwilds-calculator/tree/bf5f6cf78386e374ee5d15c8d9193ff31532e8b1/src/data/attacks"

# Per-hit traits are data, never inferred from a translated attack name.
HIT_TRAITS = {
    "gs_tcs": {i: {"charged": True} for i in range(4)},
    "gs_offset": {0: {"charged": True}},
    "gs_tackle_tcs": {0: {"damage_kind": "blunt", "sharpness_consumed": 0}, 1: {"charged": True}, 2: {"charged": True}},
    "sns_lateral": {i: {"charged": True} for i in (4, 5, 6)},
    "sns_perfect_rush": {i: {"damage_kind": "blunt", "sharpness_consumed": 0} for i in (0, 3)},
    "hammer_mighty": {i: {"charged": True} for i in range(3)},
    "lance_charge_counter": {0: {"charged": True}},
    "hh_offset": {1: {"damage_kind": "sever", "uses_sharpness": False, "sharpness_consumed": 0}},
    "gl_full_burst": {1: {"damage_kind": "shell", "fixed_fire": 8}},
    "gl_wyrmstake": {1: {"uses_sharpness": False, "sharpness_consumed": 0}, 2: {"damage_kind": "shell", "fixed_fire": 23}},
    "gl_shell_loop": {0: {"damage_kind": "shell", "fixed_fire": 11}},
    "cb_aed": {1: {"damage_kind": "impact_phial"}},
    "cb_saed": {3: {"damage_kind": "impact_phial"}},
    "ig_rising_spiral": {0: {"charged": True}},
    "ig_aerial": {i: {"airborne": True} for i in range(2)},
    "lbg_normal": {i: {"ammo_kind": "normal"} for i in range(2)},
    "lbg_rapid": {i: {"ammo_kind": "normal", "rapid_fire": True} for i in range(2)},
    "lbg_pierce": {i: {"ammo_kind": "pierce", "rapid_fire": True} for i in range(2)},
    "hbg_normal": {0: {"ammo_kind": "normal"}},
    "hbg_spread": {0: {"ammo_kind": "spread"}},
    "hbg_wyvernheart": {0: {"special_ammo": True}},
    "bow_power_loop": {0: {"ammo_kind": "normal"}, 1: {"ammo_kind": "spread"}, 2: {"ammo_kind": "spread"}},
    "bow_tracer": {0: {"ammo_kind": "normal"}, 1: {"ammo_kind": "spread"}, 2: {"ammo_kind": "spread"}},
    "bow_thousand": {0: {"special_ammo": True}, 1: {"ammo_kind": "pierce", "special_ammo": True}},
}


def h(name: str, mv: float, ele: float = 1.0, count: int = 1) -> HitDetail:
    return HitDetail(hit_name=name, motion_value=mv, element_mult=ele, hit_count=count)


def r(
    rotation_id: str,
    name: str,
    weapon_type: WeaponType,
    seconds: float,
    hits: list[HitDetail],
    category: str = "sustained",
) -> Rotation:
    for index, hit in enumerate(hits):
        for key, value in HIT_TRAITS.get(rotation_id, {}).get(index, {}).items():
            setattr(hit, key, value)
        if hit.damage_kind in {"shell", "impact_phial", "element_phial"}:
            hit.can_crit = False
            hit.uses_sharpness = False
            hit.sharpness_consumed = 0
        if weapon_type in {WeaponType.BOW, WeaponType.LIGHT_BOWGUN, WeaponType.HEAVY_BOWGUN}:
            hit.uses_sharpness = False
            hit.sharpness_consumed = 0
            if weapon_type != WeaponType.BOW:
                hit.element_mult = 0.0
        if weapon_type == WeaponType.BOW and rotation_id in {"bow_power_loop", "bow_tracer"}:
            hit.charged = True
    return Rotation(
        id=rotation_id,
        name=name,
        weapon_type=weapon_type,
        cycle_time_seconds=seconds,
        hits=hits,
        category=category,
        source_url=SOURCE_URL,
        timing_is_estimate=True,
    )


ROTATIONS = [
    r("gs_tcs", "TCS completo Nv.3", WeaponType.GREAT_SWORD, 8.2, [h("Charged Slash Lv3", 168, 1.3), h("Strong Charged Slash Lv3", 181, 1.5), h("True Charged Slash Lv3 1", 16), h("True Charged Slash Lv3 2 (Power)", 248, 2.0)], "burst"),
    r("gs_offset", "Offset Nv.3 + Cross Slash", WeaponType.GREAT_SWORD, 4.8, [h("Offset Rising Slash Lv3", 154, 1.3), h("Follow-up Cross Slash Lv3 1", 58), h("Follow-up Cross Slash Lv3 2", 230)], "offset"),
    r("gs_tackle_tcs", "Atalho Tackle para TCS", WeaponType.GREAT_SWORD, 5.7, [h("Tackle Lv3", 48, 0), h("True Charged Slash Lv3 1", 16), h("True Charged Slash Lv3 2 (Power)", 248, 2.0)]),

    r("ls_red_loop", "Loop Crimson Slash em aura vermelha", WeaponType.LONG_SWORD, 4.7, [h("Crimson Slash I 1", 33, .5), h("Crimson Slash I 2", 16, .5), h("Crimson Slash II 1", 11, 1.05), h("Crimson Slash II 2", 22, 1.05), h("Crimson Slash III 1", 30, 1.1), h("Crimson Slash III 2", 18, 1.1), h("Crimson Slash III 3", 55, 1.1)]),
    r("ls_helmbreaker", "Spirit Helmbreaker + Release", WeaponType.LONG_SWORD, 5.5, [h("Spirit Helmbreaker (Red)", 23, .2, 7), h("Spirit Release Slash 1", 5, 1, 2), h("Spirit Release Slash 2", 10, .1, 3), h("Spirit Release Slash 3", 15, .1, 3), h("Spirit Release Slash 4", 22, .1, 3), h("Spirit Release Slash 5", 35, .1, 3)], "burst"),
    r("ls_iai", "Iai Spirit Slash vermelho", WeaponType.LONG_SWORD, 3.5, [h("Iai Spirit Slash 1 (Red)", 39), h("Iai Spirit Slash 2 (Red) (Success)", 86), h("Spinning Crimson Slash", 60)], "counter"),

    r("sns_lateral", "Lateral + Reaper + Charged Chop", WeaponType.SWORD_AND_SHIELD, 5.3, [h("Lateral Slash", 27, 1.2), h("Return Stroke", 28, 1.2), h("Spinning Rising Slash", 39, 1.2), h("Spinning Reaper", 65), h("Charged Chop 1", 18), h("Charged Chop 2", 28, 1.2), h("Power Charged Chop 3", 28, 1.25)]),
    r("sns_perfect_rush", "Power Perfect Rush", WeaponType.SWORD_AND_SHIELD, 5.9, [h("Power Perfect Rush I 1", 40, 0), h("Power Perfect Rush I 2", 40, 1.5), h("Power Perfect Rush I 3", 45, 1.5), h("Power Perfect Rush II", 60, 0), h("Power Perfect Rush III", 80, 1.5), h("Power Perfect Rush III Hits", 34, 1, 3)], "burst"),
    r("sns_counter", "Guard Slash + Counter", WeaponType.SWORD_AND_SHIELD, 3.2, [h("Guard Slash", 14), h("Counter Slash", 55, 1.5), h("Spinning Reaper", 65)], "counter"),

    r("db_blade_dance", "Blade Dance I-III", WeaponType.DUAL_BLADES, 7.0, [h("Blade Dance I", 69, .7, 2), h("Blade Dance II", 47, .7, 2), h("Blade Dance III", 153, .7, 2)], "burst"),
    r("db_sixfold", "Sixfold Demon Slash loop", WeaponType.DUAL_BLADES, 3.7, [h("Demon Fangs", 14, .6), h("Twofold Demon Slash", 22, .6), h("Sixfold Demon Slash", 80, .6)]),
    r("db_perfect_evade", "Perfect Evade + Screw Slicer", WeaponType.DUAL_BLADES, 3.9, [h("Perfect Evade 1", 6, .3, 2), h("Perfect Evade 2", 10, .6, 2), h("Screw Slicer", 60, .8)], "counter"),

    r("hammer_mighty", "Mighty Charge Slam", WeaponType.HAMMER, 4.8, [h("Mighty Charge Slam 1", 20), h("Mighty Charge Slam 2", 20, 1.8), h("Mighty Charge Slam 3", 200, 2.25)], "burst"),
    r("hammer_big_bang", "Big Bang completo", WeaponType.HAMMER, 7.2, [h("Big Bang I", 43, 1.65), h("Big Bang II", 48, 1.65), h("Big Bang III", 70, 1.65), h("Big Bang IV", 90, 1.65), h("Big Bang Finisher 1", 28, 1.65, 2), h("Big Bang Finisher 2", 130, 2.25)]),
    r("hammer_offset", "Upswing offset + Spinslam", WeaponType.HAMMER, 4.3, [h("Upswing", 95, 1.95), h("Follow-Up Spinslam Spin", 20), h("Follow-Up Spinslam 1", 20), h("Follow-Up Spinslam 2", 210, 2.25)], "offset"),

    r("hh_echo", "Overhead + Resounding Melody", WeaponType.HUNTING_HORN, 5.2, [h("Overhead Smash 1", 14), h("Overhead Smash 2", 42), h("Overhead Smash Follow-up Attack", 65), h("Resounding Melody 1", 20), h("Resounding Melody 2", 22), h("Resounding Melody 3", 20)]),
    r("hh_performance", "Performance Beat + Encore", WeaponType.HUNTING_HORN, 5.7, [h("Neutral / Forward Perform", 35), h("Performance Beat I (Power)", 35), h("Performance Beat II (Power)", 45), h("Encore 1", 20), h("Encore 2 (Power)", 75)], "burst"),
    r("hh_offset", "Offset Melody + Echo Wave III", WeaponType.HUNTING_HORN, 4.1, [h("Offset Melody", 75), h("Echo Wave (Slash) III", 100, 0)], "offset"),

    r("lance_triple", "Triple Thrust loop", WeaponType.LANCE, 3.0, [h("Triple Thrust 1", 22, 1.2, 2), h("Triple Thrust 3", 35, 1.4), h("High Thrust III", 40)]),
    r("lance_charge_counter", "Charge Counter Nv.3 + Double Counter", WeaponType.LANCE, 3.8, [h("Charge Counter Lv3", 73.1), h("Double Counter-thrust Lv3 1", 42.5), h("Double Counter-thrust Lv3 2", 85)], "counter"),
    r("lance_retribution", "Perfect Guard + Retribution", WeaponType.LANCE, 3.5, [h("Perfect Guard Counter", 25, 0), h("Retribution Thrust 1 (Power)", 58, 1.6), h("Retribution Thrust 2", 15), h("Return Thrust (Power)", 31, 1.4)], "counter"),

    r("gl_full_burst", "Full Burst + Wide Sweep", WeaponType.GUNLANCE, 5.1, [h("Overhead Smash", 57, 2), h("Normal Lv3 Full Burst Shell", 12.6, 0, 6), h("Wide Sweep", 40, 1.5)]),
    r("gl_wyrmstake", "Wyrmstake Full Blast", WeaponType.GUNLANCE, 6.0, [h("Wyrmstake Full Blast Thrust", 20), h("Long Lv3 Wyrmstake Ticks", 7, .5, 8), h("Long Lv3 Wyrmstake Explosion", 42, 0), h("Multi Wyrmstake Sweep", 30)], "burst"),
    r("gl_shell_loop", "Charged Shell loop", WeaponType.GUNLANCE, 4.0, [h("Wide Lv3 Charged Shell", 37.8, 0, 3)], "sustained"),

    r("sa_morph_loop", "Morph Double Slash loop", WeaponType.SWITCH_AXE, 4.2, [h("Axe: Morph Rising Double Slash 1", 32), h("Axe: Morph Rising Double Slash 2", 28), h("Sword: Morph Double Slash 1", 30), h("Sword: Morph Double Slash 2", 50)]),
    r("sa_full_release", "Full Release Slash", WeaponType.SWITCH_AXE, 5.2, [h("Unbridled Slash", 70), h("Full Release Slash 1", 50), h("Full Release Slash 2", 82), h("Full Release Slash Explosion 1", 20, .35, 3), h("Full Release Slash Explosion 2", 35, .35, 5)], "burst"),
    r("sa_offset", "Offset + Follow-up Morph", WeaponType.SWITCH_AXE, 4.4, [h("Axe: Offset Rising Slash", 50), h("Axe: Follow-up Heavy Slam 1", 32), h("Axe: Follow-up Heavy Slam 2", 90), h("Axe: Follow-up Morph Slash", 123)], "offset"),

    r("cb_savage_axe", "Savage Axe ED I-II", WeaponType.CHARGE_BLADE, 5.0, [h("Savage Axe Slash", 48), h("Axe: Elemental Discharge I", 53), h("Power Axe Tick", 12, .2, 5), h("Axe: Elemental Discharge II 1", 35), h("Axe: Elemental Discharge II 2", 58)]),
    r("cb_aed", "AED + follow-up", WeaponType.CHARGE_BLADE, 4.5, [h("Axe: Amped Elemental Discharge", 68), h("Impact Phial (AED)", 16, 0, 3), h("Axe: Amped Elemental Discharge Follow-up", 78)], "burst"),
    r("cb_saed", "SAED com 5 frascos", WeaponType.CHARGE_BLADE, 6.2, [h("Axe: Super Amped Elemental Discharge 1", 16), h("Axe: Super Amped Elemental Discharge 2", 78), h("Axe: Super Amped Elemental Discharge 3", 45), h("Impact Phial (SAED)", 28, 0, 5)], "burst"),

    r("ig_tornado", "Triple Up + Tornado Slash", WeaponType.INSECT_GLAIVE, 4.4, [h("Strong Rising Slash Combo", 60, .8), h("Strong Reaping Slash", 46, .8), h("Tornado Slash 1", 22), h("Tornado Slash 2", 48)]),
    r("ig_rising_spiral", "Descending Thrust + Rising Spiral", WeaponType.INSECT_GLAIVE, 5.2, [h("Strong Descending Thrust Lv2", 117, .8), h("Rising Spiral Slash Lv2", 64, .8, 5)], "burst"),
    r("ig_aerial", "Aerial Triple Up", WeaponType.INSECT_GLAIVE, 4.8, [h("Strong Jumping Advancing Slash III", 78, .7), h("Strong Descending Slash Lv2", 108, .8)]),

    r("lbg_normal", "Normal 3 + Chaser", WeaponType.LIGHT_BOWGUN, 2.0, [h("Normal Lv3", 19.89), h("Normal Lv3 Chaser", 39.78)]),
    r("lbg_rapid", "Rapid Normal 3 + Chaser", WeaponType.LIGHT_BOWGUN, 2.3, [h("Rapid Normal Lv3", 15.3, 1, 3), h("Rapid Normal Lv3 Chaser", 45.9, 1, 3)]),
    r("lbg_pierce", "Rapid Pierce 3", WeaponType.LIGHT_BOWGUN, 2.5, [h("Rapid Pierce Lv3", 7.8, 1, 6), h("Rapid Pierce Lv3 Chaser", 23.4, 1, 6)]),

    r("hbg_normal", "Normal 3 - três disparos", WeaponType.HEAVY_BOWGUN, 3.0, [h("Normal Lv3", 32.3, 1, 3)]),
    r("hbg_spread", "Spread 3 - três disparos", WeaponType.HEAVY_BOWGUN, 3.2, [h("Spread Lv3", 18.2, 1, 15)]),
    r("hbg_wyvernheart", "Wyvernheart Nv.2 aquecido", WeaponType.HEAVY_BOWGUN, 5.0, [h("Wyvernheart Lv2", 10.8, 1, 20)], "burst"),

    r("bow_power_loop", "Charged Shot + Power Shot", WeaponType.BOW, 3.2, [h("Charged Shot Lv3", 11, .5, 3), h("Power Shot Lv3", 11, .6, 5), h("Power Volley Lv3", 14, .75, 6)]),
    r("bow_tracer", "Tracer Power loop", WeaponType.BOW, 3.4, [h("Tracer Charged Shot", 12, .5, 3), h("Tracer Power Shot", 12, .6, 5), h("Tracer Power Volley", 15, .65, 6)]),
    r("bow_thousand", "Tracer Thousand Dragons", WeaponType.BOW, 4.2, [h("Tracer Arrow", 25, 1), h("Tracer Thousand Dragons", 26, .3, 6)], "burst"),
]


ROTATIONS_DB: dict[str, Rotation] = {rotation.id: rotation for rotation in ROTATIONS}
DEFAULT_ROTATION_BY_WEAPON: dict[WeaponType, str] = {}
for rotation in ROTATIONS:
    DEFAULT_ROTATION_BY_WEAPON.setdefault(rotation.weapon_type, rotation.id)


def rotations_for_weapon(weapon_type: WeaponType) -> list[Rotation]:
    return [rotation for rotation in ROTATIONS if rotation.weapon_type == weapon_type]


def resolve_rotation(weapon_type: WeaponType, rotation_id: str | None = None) -> Rotation:
    if rotation_id:
        rotation = ROTATIONS_DB.get(rotation_id)
        if not rotation:
            raise ValueError(f"Rotação não encontrada: {rotation_id}")
        if rotation.weapon_type != weapon_type:
            raise ValueError("A rotação escolhida não pertence ao tipo da arma equipada.")
        return rotation
    return ROTATIONS_DB[DEFAULT_ROTATION_BY_WEAPON[weapon_type]]

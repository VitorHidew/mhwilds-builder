import pytest

from app.data import ARMORS_DB
from app.engine import calculate_build
from app.models import BuildEquipment, CustomGogWeapon, Hitzone, MonsterProfile, ScenarioSettings, WeaponType


def equipment(kind=WeaponType.GREAT_SWORD, skill=None, level=0, **weapon_options):
    return BuildEquipment(
        weapon_id="custom_gog_weapon", talisman_id="talisman_none",
        custom_weapon=CustomGogWeapon(weapon_type=kind, raw=220, element_display=200,
                                    skill_1=skill, skill_1_lvl=level, **weapon_options),
        **{f"{slot}_id": f"{slot}_none" for slot in ("helm", "chest", "arms", "waist", "legs")},
    )


def scenario(hz=50, **options):
    zone = Hitzone(part_name="Probe", sever=hz, blunt=hz, shot=hz, fire=20, water=20, thunder=20, ice=20, dragon=20)
    monster = MonsterProfile(id="custom_monster", name="Probe", description="Test", weighted_hitzone=zone)
    return ScenarioSettings(monster_id=monster.id, custom_monster=monster, **options)


@pytest.mark.parametrize("level,expected", [(0, 200), (1, 240), (2, 270), (3, 300)])
def test_fire_attack_display_units(level, expected):
    assert calculate_build(equipment(skill="Fire Attack", level=level), scenario()).total_element_display == expected


@pytest.mark.parametrize("kind,expected", [(WeaponType.GREAT_SWORD, 280), (WeaponType.DUAL_BLADES, 240), (WeaponType.LONG_SWORD, 260)])
def test_burst_true_element(kind, expected):
    result = calculate_build(equipment(kind, "Burst", 1), scenario(burst_uptime=1))
    assert result.total_element_display == expected


def test_absorption_requires_skill_and_respects_hits():
    assert calculate_build(equipment(), scenario(elemental_absorption_uptime=1)).total_element_display == 200
    assert calculate_build(equipment(skill="Elemental Absorption", level=1), scenario(elemental_absorption_uptime=1)).total_element_display == 250
    assert calculate_build(equipment(skill="Elemental Absorption", level=1), scenario(elemental_absorption_uptime=1, elemental_absorption_hits=3)).total_element_display == 270


def test_coalescence_changes_element_not_raw():
    result = calculate_build(equipment(skill="Coalescence", level=1), scenario(coalescence_uptime=1))
    assert result.total_raw == 220
    assert result.total_element_display == 220


def test_charge_master_does_not_buff_uncharged_db():
    base = calculate_build(equipment(WeaponType.DUAL_BLADES), scenario(rotation_id="db_sixfold"))
    buff = calculate_build(equipment(WeaponType.DUAL_BLADES, "Charge Master", 3), scenario(rotation_id="db_sixfold", charge_master_uptime=1))
    assert base.elemental_damage_per_cycle == buff.elemental_damage_per_cycle


@pytest.mark.parametrize("kind,rotation,label", [(WeaponType.GUNLANCE, "gl_shell_loop", "Shell"), (WeaponType.CHARGE_BLADE, "cb_saed", "Phial")])
def test_shell_and_impact_phial_ignore_physical_hz_and_affinity(kind, rotation, label):
    values = []
    for hz, affinity in [(10, 0), (80, 0), (80, 100)]:
        result = calculate_build(equipment(kind, affinity=affinity), scenario(hz, rotation_id=rotation))
        values.append(next(hit.expected_damage for hit in result.hits_breakdown if label in hit.hit_name))
    assert len(set(values)) == 1
    assert values[0] == (256.1 if kind == WeaponType.GUNLANCE else 308.0)


def test_wex_does_not_apply_to_hard_part():
    result = calculate_build(equipment(skill="Weakness Exploit", level=5), scenario(10, weakness_exploit_uptime=1))
    assert result.total_affinity == 0


def test_rejects_wrong_armor_slot_and_unknown_part():
    equip = equipment()
    helm = next(piece for piece in ARMORS_DB if piece.slot_type == "helm")
    equip.chest_id = helm.id
    with pytest.raises(ValueError, match="Peça inválida"):
        calculate_build(equip, scenario())
    with pytest.raises(ValueError, match="Parte não encontrada"):
        calculate_build(equipment(), scenario(target_part="not-a-part"))


def test_counterfactual_does_not_modify_input_or_grant_skills():
    equip = equipment(skill="Attack Boost", level=5)
    original = equip.model_dump()
    full = calculate_build(equip, scenario())
    without = calculate_build(equip, scenario(), skill_overrides={"Attack Boost": 0, "Agitator": 5})
    assert without.total_raw == 220
    assert full.total_raw > without.total_raw
    assert equip.model_dump() == original
    assert full.engine_version != "legacy"


def test_rejects_three_identical_gog_rolls():
    with pytest.raises(ValueError, match="dois reforços"):
        CustomGogWeapon(reinforcements=["attack_ex"] * 3)

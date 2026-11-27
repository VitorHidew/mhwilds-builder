"""Independent arithmetic probes, not recorded in-game damage.

Evidence and hand calculations: docs/production-readiness/01-motor.md.
Fixtures deliberately supply synthetic MVs/times instead of trusting another
calculator or deriving expected values from the production rule tables.
"""
import pytest
from pydantic import ValidationError

from app import engine
from app.models import (
    BuildEquipment, CustomGogWeapon, ElementType, HitDetail, Hitzone,
    MonsterProfile, Rotation, ScenarioSettings, SharpnessLevel, Weapon, WeaponType,
)
from app.rotations import ROTATIONS, ROTATIONS_DB


@pytest.fixture
def reference(monkeypatch):
    def calculate(*, kind=WeaponType.GREAT_SWORD, skills=None, hits=None,
                  weapon_options=None, scenario_options=None, zone_options=None):
        weapon = Weapon(
            id="reference", name="Arithmetic probe", weapon_type=kind,
            **{"raw": 200, "affinity": 0, "element_type": ElementType.FIRE,
               "element_val": 20, "sharpness": SharpnessLevel.WHITE,
               "sharpness_segments": {"White": 20, "Blue": 40},
               "skills": skills or {}, **(weapon_options or {})},
        )
        monkeypatch.setitem(engine.WEAPONS_BY_ID, weapon.id, weapon)
        rotation = Rotation(id="reference", name="Synthetic rotation", weapon_type=kind,
                            cycle_time_seconds=2, timing_is_estimate=False,
                            hits=hits or [HitDetail(hit_name="Synthetic hit", motion_value=100)])
        monkeypatch.setitem(ROTATIONS_DB, rotation.id, rotation)
        zone = Hitzone(part_name="Probe", **{
            "sever": 50, "blunt": 25, "shot": 10,
            "fire": 20, "water": 0, "thunder": 0, "ice": 0, "dragon": 20,
            **(zone_options or {}),
        })
        monster = MonsterProfile(id="custom_monster", name="Probe", description="Test only",
                                 weighted_hitzone=zone, hitzones=[zone], status_weaknesses={"blastblight": 3})
        scenario = ScenarioSettings(**{
            "monster_id": monster.id, "custom_monster": monster, "rotation_id": rotation.id,
            "agitator_uptime": 0, "burst_uptime": 0, "weakness_exploit_uptime": 0,
            "hunt_duration_seconds": 30, **(scenario_options or {}),
        })
        equip = BuildEquipment(weapon_id=weapon.id, talisman_id="talisman_none", **{
            f"{slot}_id": f"{slot}_none" for slot in ("helm", "chest", "arms", "waist", "legs")
        })
        before = (equip.model_dump(), scenario.model_dump(), weapon.model_dump(), rotation.model_dump())
        result = engine.calculate_build(equip, scenario)
        assert before == (equip.model_dump(), scenario.model_dump(), weapon.model_dump(), rotation.model_dump())
        return result
    return calculate


@pytest.mark.parametrize("kind,physical,element", [
    (WeaponType.GREAT_SWORD, 132, 4.6), (WeaponType.LONG_SWORD, 132, 4.6),
    (WeaponType.SWORD_AND_SHIELD, 132, 4.6), (WeaponType.DUAL_BLADES, 132, 4.6),
    (WeaponType.HAMMER, 66, 4.6), (WeaponType.HUNTING_HORN, 66, 4.6),
    (WeaponType.LANCE, 132, 4.6), (WeaponType.GUNLANCE, 132, 4.6),
    (WeaponType.SWITCH_AXE, 132, 4.6), (WeaponType.CHARGE_BLADE, 132, 4.6),
    (WeaponType.INSECT_GLAIVE, 132, 4.6), (WeaponType.BOW, 20, 4),
    (WeaponType.LIGHT_BOWGUN, 20, 4), (WeaponType.HEAVY_BOWGUN, 20, 4),
])
def test_generic_kernel_for_all_classes(reference, kind, physical, element):
    # Synthetic direct-element hit, NOT a claim that bowgun elemental ammo is implemented.
    result = reference(kind=kind)
    assert result.physical_damage_per_cycle == physical
    assert result.elemental_damage_per_cycle == element
    assert result.total_element == 20
    assert result.total_element_display == 200
    assert result.damage_per_cycle == pytest.approx(physical + element)
    assert result.calculation_status == "partial"
    assert not result.motion_values_verified


@pytest.mark.parametrize("affinity,expected", [(-100, 99), (-50, 115.5), (0, 132), (50, 148.5), (100, 165)])
def test_affinity_is_expected_damage_not_always_a_critical(reference, affinity, expected):
    result = reference(weapon_options={"affinity": affinity, "element_val": 0})
    assert result.damage_per_cycle == expected


def test_negative_crit_ignores_critical_boost_and_positive_affinity_caps(reference):
    negative = reference(skills={"Critical Boost": 5}, weapon_options={"affinity": -100, "element_val": 0})
    assert negative.damage_per_cycle == 99
    positive = reference(skills={"Critical Eye": 5, "Critical Boost": 5},
                         weapon_options={"affinity": 95, "element_val": 0})
    assert positive.total_affinity == 115
    assert positive.capped_affinity == 100
    assert positive.damage_per_cycle == 184.8


def test_distinct_raw_percentages_multiply_before_flat_bonuses(reference):
    # 200 * 1.04 * 1.15 * 1.30 + 9 + 10 (seed) = 329.96.
    result = reference(skills={"Attack Boost": 5, "Offensive Guard": 3, "Heroics": 5},
                       scenario_options={"offensive_guard_uptime": 1, "heroics_uptime": 1, "might_seed_uptime": 1})
    assert result.total_raw == 330.0
    assert result.physical_damage_per_cycle == 217.8


def test_element_percentages_do_not_multiply_flat_bonuses(reference):
    # GS: 20 * 1.2 (Fire 3) * 1.1 (Coalescence 1) + 6 + 8 (Burst 1) = 40.4.
    result = reference(skills={"Fire Attack": 3, "Coalescence": 1, "Burst": 1},
                       scenario_options={"coalescence_uptime": 1, "burst_uptime": 1})
    assert result.total_element == 40.4
    assert result.total_element_display == 404
    assert result.elemental_damage_per_cycle == 9.3


@pytest.mark.parametrize("status", [ElementType.POISON, ElementType.PARALYSIS, ElementType.SLEEP, ElementType.BLAST])
@pytest.mark.parametrize("level,expected", [(1, 22), (2, 24), (3, 29)])
def test_status_attack_has_its_own_table(reference, status, level, expected):
    result = reference(skills={f"{status.value} Attack": level},
                       weapon_options={"element_type": status})
    assert result.total_element == expected
    assert result.effective_element == expected  # Status has no sharpness multiplier.
    assert result.elemental_damage_per_cycle == 0


@pytest.mark.parametrize("kind,expected", [(WeaponType.GREAT_SWORD, 14), (WeaponType.DUAL_BLADES, 9.6)])
def test_status_critical_and_charge_effects_are_class_and_hit_specific(reference, kind, expected):
    # Base 24 / 3 chance; GS crit *1.4 and charge *1.25 = 14; DB *1.2 = 9.6.
    result = reference(kind=kind, skills={"Critical Status": 3, "Charge Master": 3},
                       weapon_options={"element_type": ElementType.POISON, "element_val": 24, "affinity": 100},
                       hits=[HitDetail(hit_name="Charged", motion_value=100, charged=True)],
                       scenario_options={"charge_master_uptime": 1})
    assert result.status_buildup_per_cycle == expected


def test_noncritical_hit_cannot_trigger_critical_status(reference):
    result = reference(skills={"Critical Status": 3}, weapon_options={
        "element_type": ElementType.POISON, "element_val": 30, "affinity": 100},
        hits=[HitDetail(hit_name="No crit", motion_value=100, can_crit=False)])
    assert result.status_buildup_per_cycle == 10


def test_blast_stars_do_not_create_fictional_hp_damage(reference):
    result = reference(weapon_options={"element_type": ElementType.BLAST}, scenario_options={"status_uptime": 1})
    assert result.status_buildup_per_cycle == 6.7
    assert not result.status_damage_modeled
    assert result.estimated_status_damage_per_cycle == 0
    assert result.damage_per_cycle == result.physical_damage_per_cycle == 132


@pytest.mark.parametrize("kind,expected", [(WeaponType.GREAT_SWORD, 7.0), (WeaponType.BOW, 5.3)])
def test_critical_element_and_charge_master(reference, kind, expected):
    # GS: 20*1.15*.20*1.21*1.25 = 6.9575; Bow: 20*.20*1.15*1.15 = 5.29.
    result = reference(kind=kind, skills={"Critical Element": 3, "Charge Master": 3},
                       weapon_options={"affinity": 100}, scenario_options={"charge_master_uptime": 1},
                       hits=[HitDetail(hit_name="Charged", motion_value=100, charged=True)])
    assert result.elemental_damage_per_cycle == expected


def test_wex_uses_each_hits_physical_hitzone(reference):
    result = reference(skills={"Weakness Exploit": 5}, weapon_options={"element_val": 0},
                       scenario_options={"weakness_exploit_uptime": 1}, hits=[
                           HitDetail(hit_name="Blade", motion_value=100, damage_kind="sever"),
                           HitDetail(hit_name="Shield", motion_value=100, damage_kind="blunt"),
                       ])
    assert [h.expected_damage for h in result.hits_breakdown] == [141.9, 66]


@pytest.mark.parametrize("hz,expected", [(44, 0), (45, 30)])
def test_wex_boundary(reference, hz, expected):
    result = reference(skills={"Weakness Exploit": 5}, zone_options={"sever": hz},
                       scenario_options={"weakness_exploit_uptime": 1})
    assert result.capped_affinity == expected


def test_set_piece_threshold_and_burst_dependency(reference):
    for pieces,burst,expected in [(1, 0, 200), (2, 0, 200), (2, 1, 216), (4, 1, 226)]:
        result = reference(skills={"Ebony Odogaron's Power": pieces, "Burst": burst},
                           scenario_options={"burst_uptime": 1})
        assert result.total_raw == expected
        detail = next(s for s in result.skill_details if s.name == "Ebony Odogaron's Power")
        assert detail.active == (pieces >= 2)


@pytest.mark.parametrize("level,cost", [(0, 1), (1, .9), (2, .75), (3, .5)])
def test_razor_sharp_preserves_fractional_expected_cost(reference, level, cost):
    assert reference(skills={"Razor Sharp": level}).sharpness_consumed_per_cycle == pytest.approx(cost)


def test_masters_touch_and_polish(reference):
    assert reference(skills={"Master's Touch": 1}, weapon_options={"affinity": 100}).sharpness_consumed_per_cycle == pytest.approx(.2)
    combined = reference(skills={"Master's Touch": 1, "Razor Sharp": 3}, weapon_options={"affinity": 100})
    assert combined.sharpness_consumed_per_cycle == pytest.approx(.1)
    polished = reference(skills={"Protective Polish": 3}, scenario_options={"sharpness_management_uptime": 1})
    assert polished.sharpness_consumed_per_cycle == 0
    assert polished.average_sharpness_raw_mult == 1.32
    assert polished.sustained_dps == polished.practical_dps


def test_noncritical_zero_cost_hit_does_not_lose_sharpness(reference):
    result = reference(skills={"Master's Touch": 1}, weapon_options={"affinity": 100},
                       hits=[HitDetail(hit_name="Wave", motion_value=100, sharpness_consumed=0, uses_sharpness=False)])
    assert result.sharpness_consumed_per_cycle == 0
    assert result.physical_damage_per_cycle == 125


def test_handicraft_follows_mhdb_color_extension_and_affects_current_damage(reference):
    options = {"sharpness": SharpnessLevel.BLUE, "sharpness_segments": {"Blue": 50},
               "weapon_features": {"handicraft": [1, 4]}}
    first = reference(skills={"Handicraft": 1}, weapon_options=options)
    second = reference(skills={"Handicraft": 2}, weapon_options=options)
    assert first.sharpness_raw_mult == 1.2
    assert second.sharpness_raw_mult == 1.32
    assert second.physical_damage_per_cycle == 132
    # 10 cycles white, then 5 blue within the controlled 30-second horizon.
    assert second.average_sharpness_raw_mult == 1.28
    assert second.top_sharpness_cycles == 10
    no_extension = reference(skills={"Handicraft": 5}, weapon_options={**options, "weapon_features": {}})
    assert no_extension.sharpness_raw_mult == 1.2
    assert engine._sharpness_segments(Weapon(id="p", name="p", weapon_type=WeaponType.GREAT_SWORD,
        raw=200, affinity=0, **options), 5) == {SharpnessLevel.BLUE: 60, SharpnessLevel.WHITE: 40}


@pytest.mark.parametrize("kind,traits,skills,expected", [
    (WeaponType.LIGHT_BOWGUN, {"ammo_kind": "normal", "rapid_fire": True}, {"Normal Shots": 1, "Rapid Fire Up": 1}, 22.1),
    (WeaponType.HEAVY_BOWGUN, {"special_ammo": True}, {"Special Ammo Boost": 2}, 24),
    (WeaponType.BOW, {"ammo_kind": "spread"}, {"Spread/Power Shots": 1}, 21),
    (WeaponType.BOW, {"ammo_kind": "pierce", "special_ammo": True}, {"Piercing Shots": 1, "Special Ammo Boost": 2}, 25.2),
])
def test_projectile_skills_use_traits_and_consistent_breakdown(reference, kind, traits, skills, expected):
    result = reference(kind=kind, skills=skills, weapon_options={"element_val": 0},
                       hits=[HitDetail(hit_name="Nome traduzido", motion_value=100, uses_sharpness=False, **traits)])
    assert result.damage_per_cycle == expected
    assert result.hits_breakdown[0].physical_damage == expected
    assert result.hits_breakdown[0].expected_damage == expected


def test_airborne_value_is_ten_percent_and_not_a_name_heuristic(reference):
    result = reference(skills={"Airborne": 1}, weapon_options={"element_val": 0},
                       hits=[HitDetail(hit_name="Localized", motion_value=100, airborne=True)])
    assert result.damage_per_cycle == result.hits_breakdown[0].physical_damage == 145.2


@pytest.mark.parametrize("kind", [WeaponType.BOW, WeaponType.DUAL_BLADES])
def test_stamina_skills_do_not_accelerate_animations(reference, kind):
    base = reference(kind=kind)
    skilled = reference(kind=kind, skills={"Constitution": 5, "Stamina Surge": 3})
    assert skilled.cycle_time_seconds == base.cycle_time_seconds == 2
    assert skilled.practical_dps == base.practical_dps
    assert "Constitution" in skilled.informational_skills


def test_hit_rotation_dps_and_minute_are_distinct(reference):
    result = reference(hits=[HitDetail(hit_name="Repeated", motion_value=100, hit_count=3)])
    # One contact = 132 + 4.6. The row represents 3 contacts, not one.
    assert result.hits_breakdown[0].hit_count == 3
    assert result.hits_breakdown[0].expected_damage == result.damage_per_cycle == 409.8
    assert result.practical_dps == 204.9
    assert result.damage_per_min == 12294
    assert result.sustained_dps < result.practical_dps
    assert result.sustained_model == "sharpness_only_no_recovery"


def test_zero_motion_value_is_not_replaced_with_default(reference):
    result = reference(scenario_options={"custom_motion_value": 0})
    assert result.physical_damage_per_cycle == 0
    assert result.damage_per_cycle == 4.6


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), float("-inf")])
def test_invalid_motion_value_is_rejected(value):
    with pytest.raises(ValidationError):
        ScenarioSettings(custom_motion_value=value)


@pytest.mark.parametrize("kind,display", [
    (WeaponType.GREAT_SWORD, 590), (WeaponType.LONG_SWORD, 570),
    (WeaponType.SWORD_AND_SHIELD, 560), (WeaponType.DUAL_BLADES, 530),
    (WeaponType.HAMMER, 570), (WeaponType.HUNTING_HORN, 570),
    (WeaponType.LANCE, 570), (WeaponType.GUNLANCE, 570),
    (WeaponType.SWITCH_AXE, 560), (WeaponType.CHARGE_BLADE, 560),
    (WeaponType.INSECT_GLAIVE, 560), (WeaponType.BOW, 540),
    (WeaponType.LIGHT_BOWGUN, 480), (WeaponType.HEAVY_BOWGUN, 480),
])
def test_gog_element_ex_uses_class_specific_display_units(kind, display):
    # Synthetic 480 baseline isolates the roll; bowguns gain zero from Element EX.
    weapon = CustomGogWeapon(weapon_type=kind, element_display=480, reinforcements=["element_ex"]).to_weapon()
    assert weapon.element_display == display
    assert weapon.element_val == display / 10


def test_gog_570_example_and_mixed_reinforcements():
    weapon = CustomGogWeapon(raw=205, affinity=5, element_type=ElementType.DRAGON,
                             element_display=480, reinforcements=["element_ii"]).to_weapon()
    assert weapon.element_display == 570
    assert weapon.element_val == 57
    mixed = CustomGogWeapon(raw=205, affinity=5, element_display=480, gog_focus="attack",
                            reinforcements=["attack_ex", "attack_ex", "affinity_ex", "element_ii", "sharpness_ex"]).to_weapon()
    assert mixed.raw == 239
    assert mixed.affinity == 0
    assert mixed.element_val == 57
    assert mixed.sharpness_hits == 90


def test_gog_charge_blade_status_focus_differs_from_element():
    status = CustomGogWeapon(weapon_type=WeaponType.CHARGE_BLADE, element_type=ElementType.POISON,
                              element_nature="status", element_display=150, gog_focus="element").to_weapon()
    elemental = CustomGogWeapon(weapon_type=WeaponType.CHARGE_BLADE, element_display=300, gog_focus="element").to_weapon()
    assert status.element_display == 190
    assert elemental.element_display == 350


def test_all_real_rotations_remain_explicit_estimates_with_pinned_provenance():
    assert {r.weapon_type for r in ROTATIONS} == set(WeaponType)
    assert len(ROTATIONS) == 42
    for rotation in ROTATIONS:
        assert rotation.timing_is_estimate
        assert "bf5f6cf78386e374ee5d15c8d9193ff31532e8b1" in rotation.source_url
    wave = ROTATIONS_DB["hh_offset"].hits[1]
    assert not wave.uses_sharpness
    assert wave.sharpness_consumed == 0
    assert wave.damage_kind == "sever"


def test_imported_weapon_units_match_the_independent_api_snapshot():
    import json
    from pathlib import Path
    from app.data import WEAPONS_DB

    source = json.loads((Path(__file__).parents[1] / "app/mhdb_raw_data.json").read_text(encoding="utf-8"))
    records = {f"wpn_{row['id']}": row for row in source["weapons"]}
    imported = [w for w in WEAPONS_DB if w.id in records]
    assert len(imported) == len(records) == 1188
    for weapon in imported:
        record = records[weapon.id]
        assert weapon.raw == record["damage"]["raw"], weapon.id
        if record.get("specials"):
            special = record["specials"][0]["damage"]
            assert weapon.element_val == special["raw"], weapon.id
            assert weapon.element_display == special["display"], weapon.id
            assert weapon.element_display == weapon.element_val * 10, weapon.id


def test_api_serializes_current_engine_and_all_42_rotations():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.combat_rules import ENGINE_VERSION
    from tests.test_combat_regressions import equipment, scenario

    with TestClient(app) as client:
        for kind in WeaponType:
            equip = equipment(kind, "Razor Sharp", 3)
            target = scenario()
            response = client.post("/api/calculate", json={**equip.model_dump(mode="json"),
                                   "scenario": target.model_dump(mode="json")})
            assert response.status_code == 200, response.text
            calculated = response.json()
            assert calculated["engine_version"] == ENGINE_VERSION
            assert calculated["calculation_status"] == "partial"
            assert calculated["status_damage_modeled"] is False
            comparison = client.post("/api/rotations/compare", json={
                "equipment": equip.model_dump(mode="json"), "scenario": target.model_dump(mode="json"),
            })
            assert comparison.status_code == 200, comparison.text
            rows = comparison.json()
            assert len(rows) == 3
            assert all(row["result"]["damage_per_cycle"] > 0 for row in rows)


def test_element_cap_limits_extreme_stacking_and_exposes_audit(reference):
    # Base 20 -> cap max(20 + 35, 20 * 1.9) = 55.0 internal (550 displayed).
    capped = reference(
        kind=WeaponType.GREAT_SWORD,
        skills={
            "Fire Attack": 3, "Coalescence": 3, "Burst": 5,
            "Elemental Absorption": 3, "Gogmapocalypse": 4,
        },
        scenario_options={
            "coalescence_uptime": 1, "burst_uptime": 1,
            "elemental_absorption_uptime": 1, "elemental_absorption_hits": 3,
            "agitator_uptime": 1,
        },
    )
    assert capped.element_capped is True
    assert capped.element_cap_display == 550.0
    assert capped.total_element == 55.0
    assert capped.total_element_display == 550.0
    assert any("Teto elemental atingido" in note for note in capped.audit_notes)


def test_wound_hitzone_bonus_elevates_physical_hitzone_and_wex_threshold(reference):
    base = reference(
        skills={"Weakness Exploit": 5},
        weapon_options={"element_val": 0},
        zone_options={"sever": 40},
        scenario_options={"wound_active": True, "weakness_exploit_uptime": 1},
    )
    assert base.physical_hitzone == 40.0
    assert base.capped_affinity == 20.0
    assert base.wound_hitzone_applied == 0.0

    boosted = reference(
        skills={"Weakness Exploit": 5},
        weapon_options={"element_val": 0},
        zone_options={"sever": 40},
        scenario_options={
            "wound_active": True, "wound_hitzone_bonus": 10.0, "weakness_exploit_uptime": 1,
        },
        hits=[
            HitDetail(hit_name="Slash", motion_value=100, damage_kind="sever"),
            HitDetail(hit_name="Shell", motion_value=100, damage_kind="shell", can_crit=False, uses_sharpness=False),
        ],
    )
    assert boosted.physical_hitzone == 50.0
    assert boosted.wound_hitzone_applied == 10.0
    assert boosted.capped_affinity == 50.0
    assert boosted.hits_breakdown[0].expected_damage > base.hits_breakdown[0].expected_damage
    # Shell hits always use HZV 100 and must not be inflated above 100 by wound_hitzone_bonus
    assert boosted.hits_breakdown[1].physical_damage == 200.0

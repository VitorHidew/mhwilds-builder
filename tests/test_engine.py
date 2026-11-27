import pytest
from pydantic import ValidationError

import app.optimizer as optimizer_module
from app.data import ARMORS_DB, DECORATIONS_DB, EXTRA_GAME_DATA, MONSTERS_DB, TALISMANS_DB, WEAPONS_DB
from app.engine import calculate_build, resolve_talisman, resolve_weapon, transcended_slots_for_armor
from app.gog_recommendations import recommend_gog_weapon
from app.main import (
    ARMOR_SET_BY_NAME, META_BUILD_CACHE, META_BUILD_CANDIDATES, SKILL_ICON_DIR, STATIC_ASSET_DIR,
    _armor_set_path, _localized_data, _skill_icon_index, compare_rotations,
)
from app.models import (
    ArmorPiece, BuildEquipment, BuildResult, CustomGogWeapon, CustomTalisman, ElementType,
    GogRecommendationRequest, OptimizerSettings, RotationCompareRequest, SavedBuild,
    ScenarioSettings, SharpnessLevel, Weapon, WeaponType,
    rank_saved_builds
)
from app.meta_presets import META_BUILD_PRESETS
from app.optimizer import _rank_weapons_v2, _requirements_met, armor_family, run_optimizer
from app.progression_rules import PROGRESSION_RULES
from app.rotations import ROTATIONS, rotations_for_weapon


def first_weapon(weapon_type=None):
    if weapon_type:
        return next((w for w in WEAPONS_DB if w.weapon_type == weapon_type), WEAPONS_DB[0])
    return WEAPONS_DB[0]


def first_armor(slot_type):
    return next(a for a in ARMORS_DB if a.slot_type == slot_type)


def base_equipment(**overrides):
    weapon = overrides.pop("weapon", first_weapon())
    data = {
        "weapon_id": weapon.id,
        "helm_id": first_armor("helm").id,
        "chest_id": first_armor("chest").id,
        "arms_id": first_armor("arms").id,
        "waist_id": first_armor("waist").id,
        "legs_id": first_armor("legs").id,
        "talisman_id": "talisman_none",
        "decorations": [],
    }
    data.update(overrides)
    return BuildEquipment(**data)


def test_calculation_uses_selected_monster_hitzones():
    weapon = first_weapon(WeaponType.GREAT_SWORD)
    equip = base_equipment(weapon=weapon)
    best = max(MONSTERS_DB, key=lambda m: m.weighted_hitzone.sever)
    worst = min(MONSTERS_DB, key=lambda m: m.weighted_hitzone.sever)

    res_best = calculate_build(equip, ScenarioSettings(monster_id=best.id))
    res_worst = calculate_build(equip, ScenarioSettings(monster_id=worst.id))

    assert best.id != worst.id
    assert res_best.damage_per_cycle != res_worst.damage_per_cycle


def test_custom_gog_weapon_integration():
    custom_gog = CustomGogWeapon(
        name="Destruidora Gogartiana",
        weapon_type=WeaponType.HAMMER,
        raw=260.0,
        affinity=10.0,
        element_nature="element",
        element_type=ElementType.FIRE,
        element_val=35.0,
        slots=[3, 2, 1],
        best_sharpness=SharpnessLevel.PURPLE,
        skill_1="Agitator",
        skill_1_lvl=2,
        skill_3="Burst",
        skill_3_lvl=1,
    )

    equip = base_equipment(
        weapon_id="custom_gog_weapon",
        custom_weapon=custom_gog,
    )
    res = calculate_build(equip, ScenarioSettings(monster_id=MONSTERS_DB[0].id))

    assert res.active_skills.get("Agitator", 0) >= 2
    assert res.active_skills.get("Burst", 0) >= 1
    assert res.total_element >= 35.0
    assert res.total_element_display >= 350.0
    assert res.sharpness_raw_mult == 1.39
    assert res.practical_dps > 0.0


def test_custom_talisman_validation_and_skill_integration():
    custom_tali = CustomTalisman(
        name="Amuleto Lendario",
        skill_1="Attack Boost",
        skill_1_lvl=3,
        skill_2="Critical Eye",
        skill_2_lvl=2,
        skill_3="Critical Boost",
        skill_3_lvl=1,
        slots=[3, 1, 0],
        slot_kinds=["weapon", "armor", "armor"],
    )

    equip = base_equipment(
        talisman_id="custom_talisman",
        custom_talisman=custom_tali,
    )
    res = calculate_build(equip, ScenarioSettings(monster_id=MONSTERS_DB[0].id))

    assert res.active_skills["Attack Boost"] >= 3
    assert res.active_skills["Critical Eye"] >= 2
    assert res.active_skills["Critical Boost"] >= 1
    converted = custom_tali.to_talisman()
    assert converted.slots == [3, 1]
    assert converted.slot_kinds == ["weapon", "armor"]

    with pytest.raises(ValidationError):
        CustomTalisman(slots=[5, 0, 0])


def test_decoration_database_preserves_weapon_and_armor_kinds():
    weapon_decorations = [item for item in DECORATIONS_DB if item.kind == "weapon"]
    armor_decorations = [item for item in DECORATIONS_DB if item.kind == "armor"]

    assert len(weapon_decorations) == 295
    assert len(armor_decorations) == 66
    assert len(weapon_decorations) + len(armor_decorations) == len(DECORATIONS_DB)


def test_decorations_only_fit_slots_of_their_own_kind():
    empty = {
        slot: next(item for item in ARMORS_DB if item.id == f"{slot}_none")
        for slot in ("helm", "chest", "arms", "waist", "legs")
    }
    weapon_deco = next(item for item in DECORATIONS_DB if item.kind == "weapon" and item.level <= 3)
    armor_deco = next(item for item in DECORATIONS_DB if item.kind == "armor" and item.level <= 3)
    common = {
        "helm_id": empty["helm"].id,
        "chest_id": empty["chest"].id,
        "arms_id": empty["arms"].id,
        "waist_id": empty["waist"].id,
        "legs_id": empty["legs"].id,
        "talisman_id": "custom_talisman",
    }

    wrong_weapon_slot = base_equipment(
        **common,
        weapon_id="custom_gog_weapon",
        custom_weapon=CustomGogWeapon(slots=[]),
        custom_talisman=CustomTalisman(slots=[3], slot_kinds=["armor"]),
        decorations=[weapon_deco.id],
    )
    wrong_weapon_result = calculate_build(wrong_weapon_slot, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    assert wrong_weapon_result.active_skills.get(weapon_deco.skill, 0) == 0
    assert any("adorno de arma" in warning for warning in wrong_weapon_result.slot_warnings)

    right_weapon_slot = wrong_weapon_slot.model_copy(deep=True)
    right_weapon_slot.custom_weapon.slots = [3]
    right_weapon_slot.custom_talisman = CustomTalisman(slots=[])
    right_weapon_result = calculate_build(right_weapon_slot, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    assert right_weapon_result.active_skills.get(weapon_deco.skill, 0) >= weapon_deco.points
    assert right_weapon_result.slot_warnings == []

    wrong_armor_slot = right_weapon_slot.model_copy(deep=True)
    wrong_armor_slot.decorations = [armor_deco.id]
    wrong_armor_result = calculate_build(wrong_armor_slot, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    assert wrong_armor_result.active_skills.get(armor_deco.skill, 0) == 0
    assert any("adorno de armadura" in warning for warning in wrong_armor_result.slot_warnings)

    right_armor_slot = wrong_armor_slot.model_copy(deep=True)
    right_armor_slot.custom_weapon.slots = []
    right_armor_slot.custom_talisman = CustomTalisman(slots=[3], slot_kinds=["armor"])
    right_armor_result = calculate_build(right_armor_slot, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    assert right_armor_result.active_skills.get(armor_deco.skill, 0) >= armor_deco.points
    assert right_armor_result.slot_warnings == []


def test_invalid_ids_are_explicit_errors():
    equip = base_equipment(weapon_id="arma_inexistente")
    with pytest.raises(ValueError, match="Arma não encontrada"):
        calculate_build(equip, ScenarioSettings(monster_id=MONSTERS_DB[0].id))

    equip = base_equipment()
    with pytest.raises(ValueError, match="Monstro não encontrado"):
        calculate_build(equip, ScenarioSettings(monster_id="monstro_inexistente"))


def make_saved_build(name, dps, cycle, score):
    result = BuildResult(
        total_raw=100,
        effective_raw=100,
        total_affinity=0,
        capped_affinity=0,
        total_element=0,
        effective_element=0,
        crit_multiplier=1.25,
        sharpness_raw_mult=1.0,
        sharpness_ele_mult=1.0,
        active_skills={},
        damage_per_cycle=cycle,
        practical_dps=dps,
        damage_per_min=dps * 60,
        combined_score=score,
    )
    return SavedBuild(
        id=name,
        name=name,
        equipment=base_equipment(),
        scenario=ScenarioSettings(monster_id=MONSTERS_DB[0].id),
        result=result,
    )


def test_comparator_ranking_helper():
    builds = [
        make_saved_build("A", dps=20, cycle=100, score=30),
        make_saved_build("B", dps=35, cycle=90, score=25),
        make_saved_build("C", dps=10, cycle=200, score=40),
    ]

    assert [b.name for b in rank_saved_builds(builds, "practical_dps")] == ["B", "A", "C"]
    assert [b.name for b in rank_saved_builds(builds, "damage_per_cycle")] == ["C", "A", "B"]
    assert [b.name for b in rank_saved_builds(builds)] == ["C", "A", "B"]


def test_visual_metadata_covers_armor_sets_and_skill_icons():
    assert _armor_set_path("Conga Helm α") == "Conga α"
    assert _armor_set_path("Chatacabra Greaves β") == "Chatacabra β"
    assert _skill_icon_index("Attack Boost") == 0
    assert _skill_icon_index("Opening Shot") == 4
    assert _skill_icon_index("Reforço de Ataque") == 0

    armor_names = [armor.name for armor in ARMORS_DB if not armor.name.startswith("(")]
    assert all(name.casefold() in ARMOR_SET_BY_NAME for name in armor_names)

    for skill in EXTRA_GAME_DATA["skills"]:
        icon_index = _skill_icon_index(skill["name"])
        assert icon_index is not None
        assert (SKILL_ICON_DIR / f"SKILL_{icon_index:04d}.png").stat().st_size > 500

    equipment_icons = list((STATIC_ASSET_DIR / "equipment-icons").iterdir())
    assert len(equipment_icons) == 20
    assert all(icon.stat().st_size > 100 for icon in equipment_icons)


def test_official_ptbr_names_are_loaded_from_mhdb_locale():
    localized = _localized_data("pt")
    skills = {skill["name_en"]: skill["name"] for skill in localized["skills"]}

    assert skills["Attack Boost"] == "Reforço de Ataque"
    assert skills["Critical Boost"] == "Reforço Crítico"
    assert skills["Weakness Exploit"] == "Exploração de Fraqueza"
    assert all(item.get("name") for item in localized["weapons"])
    assert all(item.get("name") for item in localized["armors"])
    assert all(item.get("name") for item in localized["decorations"])


def test_group_skill_is_gray_until_required_armor_count_and_tracks_sources():
    conga = {armor.slot_type: armor for armor in ARMORS_DB if armor.name.startswith("Conga ")}
    empty = {slot: next(a for a in ARMORS_DB if a.id == f"{slot}_none") for slot in ("helm", "chest", "arms", "waist", "legs")}

    one_piece = base_equipment(
        helm_id=conga["helm"].id,
        chest_id=empty["chest"].id,
        arms_id=empty["arms"].id,
        waist_id=empty["waist"].id,
        legs_id=empty["legs"].id,
    )
    one_result = calculate_build(one_piece, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    one_detail = next(detail for detail in one_result.skill_details if detail.name == "Fortifying Pelt")

    assert one_detail.active is False
    assert one_detail.level == 1
    assert one_detail.required_pieces == 3
    assert [(source.slot_type, source.level) for source in one_detail.sources] == [("helm", 1)]

    three_pieces = base_equipment(
        helm_id=conga["helm"].id,
        chest_id=conga["chest"].id,
        arms_id=conga["arms"].id,
        waist_id=empty["waist"].id,
        legs_id=empty["legs"].id,
    )
    three_result = calculate_build(three_pieces, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    three_detail = next(detail for detail in three_result.skill_details if detail.name == "Fortifying Pelt")

    assert three_detail.active is True
    assert three_detail.active_rank_name == "Fortify"
    assert {source.slot_type for source in three_detail.sources} == {"helm", "chest", "arms"}


@pytest.mark.parametrize(
    ("rarity", "slots", "expected"),
    [
        (5, [], [1, 1, 1]),
        (5, [1], [2, 1, 1]),
        (5, [2, 2, 1], [3, 3, 2]),
        (6, [], [1, 1]),
        (6, [2], [3, 1]),
        (6, [3, 2, 1], [3, 3, 1]),
        (7, [2, 1], [2, 1]),
        (8, [3], [3]),
    ],
)
def test_transcended_armor_slot_rules(rarity, slots, expected):
    armor = ArmorPiece(id="test", name="Test", slot_type="helm", rarity=rarity, slots=slots)
    assert transcended_slots_for_armor(armor) == expected


def test_transcended_piece_adds_usable_decoration_slots():
    weapon = next(weapon for weapon in WEAPONS_DB if not weapon.slots)
    conga_chest = next(
        armor for armor in ARMORS_DB
        if armor.name == "Conga Mail α" and armor.rarity == 5 and not armor.slots
    )
    empty = {slot: next(a for a in ARMORS_DB if a.id == f"{slot}_none") for slot in ("helm", "arms", "waist", "legs")}
    decoration = next(deco for deco in DECORATIONS_DB if deco.kind == "armor" and deco.level == 1)
    base = BuildEquipment(
        weapon_id=weapon.id,
        helm_id=empty["helm"].id,
        chest_id=conga_chest.id,
        arms_id=empty["arms"].id,
        waist_id=empty["waist"].id,
        legs_id=empty["legs"].id,
        talisman_id="talisman_none",
        decorations=[decoration.id],
    )

    normal = calculate_build(base, ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    transcended = calculate_build(
        base.model_copy(update={"transcended_armor": ["chest"]}),
        ScenarioSettings(monster_id=MONSTERS_DB[0].id),
    )

    assert any("não coube" in warning for warning in normal.slot_warnings)
    assert not any("não coube" in warning for warning in transcended.slot_warnings)
    assert transcended.active_skills.get(decoration.skill, 0) >= decoration.points


def test_every_weapon_has_three_versioned_rotations():
    assert len(ROTATIONS) == 42
    assert len({rotation.id for rotation in ROTATIONS}) == len(ROTATIONS)
    for weapon_type in WeaponType:
        rotations = rotations_for_weapon(weapon_type)
        assert len(rotations) == 3
        assert all(rotation.source_url for rotation in rotations)
        assert all(rotation.cycle_time_seconds > 0 for rotation in rotations)


def test_selected_rotation_is_used_and_comparison_ranks_all_combos():
    weapon = first_weapon(WeaponType.GREAT_SWORD)
    equip = base_equipment(weapon=weapon)
    rotations = rotations_for_weapon(WeaponType.GREAT_SWORD)
    first = calculate_build(equip, ScenarioSettings(monster_id=MONSTERS_DB[0].id, rotation_id=rotations[0].id))
    second = calculate_build(equip, ScenarioSettings(monster_id=MONSTERS_DB[0].id, rotation_id=rotations[1].id))

    assert first.rotation_id == rotations[0].id
    assert first.rotation_name == rotations[0].name
    assert first.damage_per_cycle != second.damage_per_cycle

    rows = compare_rotations(RotationCompareRequest(
        equipment=equip,
        scenario=ScenarioSettings(monster_id=MONSTERS_DB[0].id),
    ))
    assert len(rows) == 3
    assert rows[0].result.practical_dps >= rows[-1].result.practical_dps


def test_precalculated_meta_library_covers_every_weapon_and_profile():
    assert len(META_BUILD_PRESETS) == 14 * 16
    assert len(META_BUILD_CACHE) == 14 * 16
    assert not ({preset.id for preset in META_BUILD_PRESETS} - set(META_BUILD_CACHE))
    assert all(build.result.rotation_id for build in META_BUILD_CACHE.values())
    assert set(META_BUILD_CANDIDATES) == {preset.id for preset in META_BUILD_PRESETS}
    assert all(len(candidates) == 2 for candidates in META_BUILD_CANDIDATES.values())
    assert all(
        [build.result.practical_dps for build in candidates]
        == sorted([build.result.practical_dps for build in candidates], reverse=True)
        for candidates in META_BUILD_CANDIDATES.values()
    )


def test_progression_presets_respect_rarity_and_transcendence_limits():
    weapons = {weapon.id: weapon for weapon in WEAPONS_DB}
    armors = {armor.id: armor for armor in ARMORS_DB}
    for preset in (item for item in META_BUILD_PRESETS if item.library_group == "progression"):
        build = META_BUILD_CACHE[preset.id]
        assert weapons[build.equipment.weapon_id].rarity <= preset.max_rarity
        for armor_id in (
            build.equipment.helm_id, build.equipment.chest_id, build.equipment.arms_id,
            build.equipment.waist_id, build.equipment.legs_id,
        ):
            assert armors[armor_id].rarity <= preset.max_rarity
        if not preset.use_transcendence:
            assert build.equipment.transcended_armor == []


def test_guided_progression_builds_match_weapon_armor_and_talisman_rules():
    weapons = {weapon.id: weapon for weapon in WEAPONS_DB}
    armors = {armor.id: armor for armor in ARMORS_DB}
    talismans = {talisman.id: talisman for talisman in TALISMANS_DB}
    for (weapon_type, profile), rule in PROGRESSION_RULES.items():
        slug = weapon_type.value.lower().replace("&", "and").replace(" ", "_")
        build = META_BUILD_CACHE[f"meta_{slug}_{profile}"]
        assert weapons[build.equipment.weapon_id].series in rule.weapon_series
        armor_ids = (
            build.equipment.helm_id, build.equipment.chest_id, build.equipment.arms_id,
            build.equipment.waist_id, build.equipment.legs_id,
        )
        actual_counts = {}
        for armor_id in armor_ids:
            family = armor_family(armors[armor_id])
            actual_counts[family] = actual_counts.get(family, 0) + 1
        assert actual_counts == dict(rule.armor_requirements)
        talisman = talismans[build.equipment.talisman_id]
        assert all(talisman.skills.get(skill) == level for skill, level in rule.talisman_skills)


def test_gog_recommendation_has_perfect_and_single_target_routes():
    result = recommend_gog_weapon(GogRecommendationRequest(
        weapon_type=WeaponType.GREAT_SWORD,
        monster_id="mon_34",
        rotation_id="gs_offset",
        preset_id="meta_great_sword_dps_max",
    ))
    assert result.best_element == ElementType.DRAGON
    assert result.perfect.weapon.slots == [3, 3, 3]
    assert len(result.perfect.desired_skills) == 2
    assert result.accessible.desired_skills == ["Doshaguma's Might"]
    assert result.accessible.weapon.skill_2 is None


def test_gog_recommendation_is_locked_before_hunter_rank_100():
    with pytest.raises(ValueError, match="progressão"):
        recommend_gog_weapon(GogRecommendationRequest(
            weapon_type=WeaponType.GREAT_SWORD,
            monster_id="mon_34",
            rotation_id="gs_offset",
            preset_id="meta_great_sword_progressao_hr_41",
        ))


def test_weapon_tempo_and_immunizer_comfort_priorities_are_applied():
    great_sword_damage = next(item for item in META_BUILD_PRESETS if item.id == "meta_great_sword_dps_max")
    great_sword_comfort = next(item for item in META_BUILD_PRESETS if item.id == "meta_great_sword_dps_conforto")
    dual_blades_damage = next(item for item in META_BUILD_PRESETS if item.id == "meta_dual_blades_dps_max")
    assert "Burst" not in great_sword_damage.preferred_skills
    assert great_sword_comfort.preferred_skills["Recovery Speed"] == 3
    assert great_sword_comfort.preferred_skills["Speed Eating"] == 1
    assert dual_blades_damage.preferred_skills["Burst"] == 5


def test_weapon_recommendation_policy_only_allows_normal_weapons_for_progression():
    progression = next(item for item in META_BUILD_PRESETS if item.id == "meta_great_sword_progressao_hr_41")
    endgame = next(item for item in META_BUILD_PRESETS if item.id == "meta_great_sword_dps_max")
    gunlance = next(item for item in META_BUILD_PRESETS if item.id == "meta_gunlance_dps_max")

    assert progression.weapon_recommendation_mode == "progression"
    assert endgame.weapon_recommendation_mode == "gog"
    assert gunlance.preferred_skills["Burst"] == 5


def test_preset_optimization_keeps_only_two_ranked_alternatives():
    builds = run_optimizer(OptimizerSettings(
        weapon_type=WeaponType.GREAT_SWORD,
        preset_id="meta_great_sword_dps_max",
        max_results=10,
        search_limit=150,
        armor_pool_limit=6,
        weapon_pool_limit=2,
        talisman_pool_limit=3,
    ))
    assert len(builds) == 2


def test_optimizer_respects_level_five_skill_targets_and_selected_combo():
    results = run_optimizer(OptimizerSettings(
        weapon_type=WeaponType.GREAT_SWORD,
        target_skills={"Weakness Exploit": 5, "Agitator": 5},
        monster_id=MONSTERS_DB[0].id,
        rotation_id="gs_offset",
        search_limit=100,
        armor_pool_limit=4,
        weapon_pool_limit=1,
        talisman_pool_limit=1,
        max_results=1,
    ))

    assert results
    assert results[0].result.active_skills["Weakness Exploit"] == 5
    assert results[0].result.active_skills["Agitator"] == 5
    assert results[0].result.rotation_id == "gs_offset"


def test_optimizer_fills_every_available_decoration_slot():
    build = run_optimizer(OptimizerSettings(
        weapon_type=WeaponType.GREAT_SWORD,
        preset_id="meta_great_sword_dps_max",
        monster_id="mon_20",
        search_limit=120,
        armor_pool_limit=5,
        weapon_pool_limit=1,
        talisman_pool_limit=2,
        max_results=1,
    ))[0]
    armor_by_id = {armor.id: armor for armor in ARMORS_DB}
    weapon = resolve_weapon(build.equipment)
    talisman = next(item for item in TALISMANS_DB if item.id == build.equipment.talisman_id)
    slots_by_kind = {"weapon": list(weapon.slots), "armor": []}
    for index, slot in enumerate(talisman.slots):
        slots_by_kind[talisman.slot_kinds[index]].append(slot)
    for armor_id in (
        build.equipment.helm_id, build.equipment.chest_id, build.equipment.arms_id,
        build.equipment.waist_id, build.equipment.legs_id,
    ):
        slots_by_kind["armor"].extend(transcended_slots_for_armor(armor_by_id[armor_id]))
    assert len(build.equipment.decorations) == sum(
        len([slot for slot in slots if slot > 0]) for slots in slots_by_kind.values()
    )
    decoration_by_id = {decoration.id: decoration for decoration in DECORATIONS_DB}
    remaining = {
        kind: sorted((slot for slot in slots if slot > 0), reverse=True)
        for kind, slots in slots_by_kind.items()
    }
    for decoration_id in sorted(
        build.equipment.decorations,
        key=lambda item: decoration_by_id[item].level,
        reverse=True,
    ):
        decoration = decoration_by_id[decoration_id]
        slot_index = next(
            index for index, slot in enumerate(remaining[decoration.kind])
            if slot >= decoration.level
        )
        remaining[decoration.kind].pop(slot_index)
    assert build.result.slot_warnings == []


def test_every_cached_build_has_full_legal_decoration_slots():
    armor_by_id = {armor.id: armor for armor in ARMORS_DB}
    builds = list(META_BUILD_CACHE.values())
    builds.extend(
        build
        for candidates in META_BUILD_CANDIDATES.values()
        for build in candidates
    )

    for build in builds:
        weapon = resolve_weapon(build.equipment)
        talisman = resolve_talisman(build.equipment)
        expected_slots = len([slot for slot in weapon.slots if slot > 0])
        expected_slots += len([slot for slot in talisman.slots if slot > 0])
        for armor_id in (
            build.equipment.helm_id, build.equipment.chest_id, build.equipment.arms_id,
            build.equipment.waist_id, build.equipment.legs_id,
        ):
            armor = armor_by_id[armor_id]
            slots = (
                transcended_slots_for_armor(armor)
                if armor.slot_type in build.equipment.transcended_armor
                else armor.slots
            )
            expected_slots += len([slot for slot in slots if slot > 0])

        recalculated = calculate_build(build.equipment, build.scenario)
        assert len(build.equipment.decorations) == expected_slots, build.id
        assert recalculated.slot_warnings == [], build.id


def test_synced_data_keeps_defense_resistances_and_weapon_systems():
    armor = next(item for item in ARMORS_DB if item.elemental_resistances)
    gunlance = next(item for item in WEAPONS_DB if item.weapon_type == WeaponType.GUNLANCE and item.shell_type)
    bow = next(item for item in WEAPONS_DB if item.weapon_type == WeaponType.BOW and item.coatings)
    multi_skill_deco = next(item for item in DECORATIONS_DB if len(item.skills) > 1)

    assert armor.defense_max >= armor.defense
    assert gunlance.shell_level > 0
    assert bow.coatings
    assert len(multi_skill_deco.skills) > 1


def test_element_display_is_preserved_without_changing_true_damage_math():
    weapon = next(item for item in WEAPONS_DB if item.name == "True Shadowbringer")

    assert weapon.element_val == 60
    assert weapon.element_display == 600

    result = calculate_build(base_equipment(weapon=weapon), ScenarioSettings(monster_id=MONSTERS_DB[0].id))
    assert result.total_element_display == result.total_element * 10


def test_element_damage_uses_true_value_and_selected_element_hitzone():
    custom_gog = CustomGogWeapon(
        name="Espadão elemental de teste",
        weapon_type=WeaponType.GREAT_SWORD,
        raw=200,
        affinity=0,
        element_type=ElementType.FIRE,
        element_val=50,
        element_display=500,
        reinforcements=[],
    )
    equipment = base_equipment(
        weapon_id="custom_gog_weapon",
        custom_weapon=custom_gog,
    )

    head = calculate_build(equipment, ScenarioSettings(
        monster_id="mon_26", target_part="head", rotation_id="gs_offset",
    ))
    sealed_core = calculate_build(equipment, ScenarioSettings(
        monster_id="mon_26", target_part="frozen-bigcore-before", rotation_id="gs_offset",
    ))

    assert head.total_element == 50
    assert head.total_element_display == 500
    assert head.elemental_hitzone == 20
    assert head.elemental_damage_per_cycle > 0
    assert sealed_core.elemental_hitzone == 0
    assert sealed_core.elemental_damage_per_cycle == 0


def test_optimizer_weapon_prefilter_changes_with_selected_element_hitzone(monkeypatch):
    raw_weapon = Weapon(
        id="test_raw", name="Raw", weapon_type=WeaponType.DUAL_BLADES,
        raw=220, affinity=0, slots=[], element_type=ElementType.NONE,
    )
    elemental_weapon = Weapon(
        id="test_fire", name="Fire", weapon_type=WeaponType.DUAL_BLADES,
        raw=180, affinity=0, slots=[], element_type=ElementType.FIRE, element_val=400,
    )
    monkeypatch.setattr(optimizer_module, "WEAPONS_DB", [raw_weapon, elemental_weapon])
    monkeypatch.setattr(optimizer_module, "WEAPONS_BY_TYPE", {
        WeaponType.DUAL_BLADES: [raw_weapon, elemental_weapon]
    })
    settings = OptimizerSettings(weapon_type=WeaponType.DUAL_BLADES, weapon_pool_limit=1)

    head = ScenarioSettings(monster_id="mon_26", target_part="head")
    sealed_core = ScenarioSettings(monster_id="mon_26", target_part="frozen-bigcore-before")

    assert _rank_weapons_v2(settings, {}, head)[0].id == "test_fire"
    assert _rank_weapons_v2(settings, {}, sealed_core)[0].id == "test_raw"


def test_gog_recommendation_uses_selected_part_element_hitzone():
    result = recommend_gog_weapon(GogRecommendationRequest(
        weapon_type=WeaponType.GREAT_SWORD,
        monster_id="mon_26",
        rotation_id="gs_offset",
        preset_id="meta_great_sword_dps_max",
        target_part="head",
    ))

    assert result.best_element == ElementType.FIRE
    assert result.target_part == "head"
    assert result.element_hitzone == 20


def test_gog_focus_and_reinforcements_affect_the_weapon_used_by_engine():
    gog = CustomGogWeapon(
        raw=220, affinity=5, element_val=48, element_display=480, gog_focus="attack",
        reinforcements=["attack_ex", "attack_ex", "element_ex", "sharpness_ex"],
    )
    weapon = gog.to_weapon()

    assert weapon.raw == 254
    assert weapon.affinity == -10
    # GS Element EX is +110 displayed; +90 is the generic/LS value.
    assert weapon.element_display == 590
    assert weapon.element_val == 59
    assert weapon.sharpness_hits == 90


def test_sharpness_reports_current_and_sustained_damage_separately():
    weapon = next(
        item for item in WEAPONS_DB
        if item.weapon_type == WeaponType.GREAT_SWORD and item.sharpness_segments
    )
    result = calculate_build(
        base_equipment(weapon=weapon),
        ScenarioSettings(monster_id=MONSTERS_DB[0].id, hunt_duration_seconds=600),
    )

    assert result.sharpness_raw_mult > 1.0
    assert result.average_sharpness_raw_mult <= result.sharpness_raw_mult
    assert result.sustained_dps <= result.practical_dps
    assert result.sharpness_consumed_per_cycle > 0


def test_ranged_damage_does_not_receive_melee_sharpness_multiplier():
    weapon = first_weapon(WeaponType.BOW)
    result = calculate_build(base_equipment(weapon=weapon), ScenarioSettings(monster_id=MONSTERS_DB[0].id))

    assert result.sharpness_raw_mult == 1.0
    assert result.average_sharpness_raw_mult == 1.0
    assert result.sharpness_consumed_per_cycle == 0


def test_optimizer_requires_an_active_set_skill_not_just_a_displayed_level():
    conga = next(item for item in ARMORS_DB if item.name.startswith("Conga ") and item.slot_type == "helm")
    empties = {slot: next(item for item in ARMORS_DB if item.id == f"{slot}_none") for slot in ("chest", "arms", "waist", "legs")}
    result = calculate_build(base_equipment(
        helm_id=conga.id,
        chest_id=empties["chest"].id,
        arms_id=empties["arms"].id,
        waist_id=empties["waist"].id,
        legs_id=empties["legs"].id,
    ), ScenarioSettings(monster_id=MONSTERS_DB[0].id))

    assert result.active_skills["Fortifying Pelt"] == 1
    assert _requirements_met(result, {"Fortifying Pelt": 1}) is False


def test_endgame_optimizer_integrates_gog_pair_with_active_armor_sets():
    build = run_optimizer(OptimizerSettings(
        weapon_type=WeaponType.GREAT_SWORD,
        preset_id="meta_great_sword_dps_max",
        monster_id="mon_20",
        search_limit=350,
        armor_pool_limit=12,
        talisman_pool_limit=6,
        max_results=1,
    ))[0]
    custom = build.equipment.custom_weapon
    details = {detail.name: detail for detail in build.result.skill_details}

    assert build.equipment.weapon_id == "custom_gog_weapon"
    assert custom and custom.skill_1 and custom.skill_2
    assert details[custom.skill_1].active is True
    assert details[custom.skill_2].active is True

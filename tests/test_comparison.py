from app.comparison import compare_builds
from app.engine import calculate_build
from app.models import BuildCompareRequest, SavedBuild
from tests.test_combat_regressions import equipment, scenario


def build(build_id, hz=50, skill=None, level=0):
    equip, target = equipment(skill=skill, level=level), scenario(hz)
    return SavedBuild(id=build_id, name=build_id, equipment=equip, scenario=target, result=calculate_build(equip, target))


def test_comparison_recalculates_same_equipment_under_shared_target():
    one, two = build("one", 10), build("two", 80)
    before = [one.model_dump(), two.model_dump()]
    response = compare_builds(BuildCompareRequest(builds=[one, two], scenario=scenario(50)))
    assert len(response["rows"]) == 2
    assert not response["errors"]
    assert {row["dps_difference_percent"] for row in response["rows"]} == {0}
    assert [one.model_dump(), two.model_dump()] == before


def test_impacts_are_recalculated_and_more_than_two_builds_work():
    rows = [build(str(i), skill="Attack Boost", level=i) for i in range(5)]
    response = compare_builds(BuildCompareRequest(builds=rows, scenario=scenario(), rotation_mode="best"))
    assert len(response["rows"]) == 5
    winner = response["rows"][0]
    assert winner["build"].id == "4"
    assert winner["skill_impacts"][0]["skill"] == "Attack Boost"
    assert winner["skill_impacts"][0]["dps_delta"] > 0
    assert response["rows"][-1]["dps_difference_percent"] < 0


def test_invalid_build_does_not_hide_valid_rows():
    bad, good = build("bad"), build("good")
    bad.equipment.chest_id = "helm_none"
    response = compare_builds(BuildCompareRequest(builds=[bad, good], scenario=scenario()))
    assert len(response["rows"]) == 1
    assert response["errors"][0]["id"] == "bad"


def test_selected_combo_cannot_silently_change_weapon_class():
    from app.rotations import rotations_for_weapon

    target = scenario()
    target.rotation_id = rotations_for_weapon("Bow")[0].id
    response = compare_builds(BuildCompareRequest(builds=[build("gs")], scenario=target, rotation_mode="selected"))
    assert not response["rows"]
    assert response["errors"][0]["id"] == "gs"

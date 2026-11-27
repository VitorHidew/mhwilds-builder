import pytest

from app.combat_rules import ENGINE_VERSION
from app.data import WEAPONS_DB
from app.gog_recommendations import recommend_gog_weapon
from app.models import GogRecommendationRequest, OptimizerSettings, WeaponType
from app.optimizer import run_optimizer


def test_global_budget_is_distributed_across_all_weapons():
    builds = run_optimizer(OptimizerSettings(
        weapon_type=WeaponType.GREAT_SWORD, search_limit=100,
        armor_pool_limit=4, weapon_pool_limit=4, talisman_pool_limit=2,
        max_results=2,
    ))
    assert builds
    stats = builds[0].search_stats
    assert stats["evaluated"] == 100
    assert len(stats["evaluated_by_weapon"]) == 4
    assert set(stats["evaluated_by_weapon"].values()) == {25}
    assert not stats["global_optimum_proven"]
    assert builds[0].provenance["engine_version"] == ENGINE_VERSION
    assert all(not build.result.slot_warnings for build in builds)


@pytest.mark.parametrize("kind", list(WeaponType))
def test_gog_models_start_from_a_traceable_same_base(kind):
    slug = kind.value.lower().replace("&", "and").replace(" ", "_")
    rec = recommend_gog_weapon(GogRecommendationRequest(
        weapon_type=kind, monster_id="mon_20", preset_id=f"meta_{slug}_dps_max",
    ))
    high, low = rec.perfect.weapon, rec.accessible.weapon
    base = next(w for w in WEAPONS_DB if w.id == high.base_weapon_id)
    assert high.raw == low.raw == base.raw + 15
    assert high.affinity == low.affinity == base.affinity
    assert high.element_display == low.element_display
    assert high.sharpness_units == low.sharpness_units == 20
    assert len(high.reinforcements) == 5
    if kind in {WeaponType.LIGHT_BOWGUN, WeaponType.HEAVY_BOWGUN}:
        assert high.to_weapon().element_val == 0
        assert not any(r.startswith(("element_", "sharpness_")) for r in high.reinforcements)
    if kind == WeaponType.GUNLANCE:
        assert high.to_weapon().shell_type
        assert high.to_weapon().shell_level == 4

import json
from pathlib import Path

from app.combat_rules import ENGINE_VERSION
from app.engine import calculate_build
from app.meta_presets import META_BUILD_PRESETS
from app.models import SavedBuild


def test_cache_portfolio_keeps_best_distinct_equipment_and_reports_total_work():
    from app.generate_meta_cache import rank_portfolio
    from tests.test_comparison import build

    weak = build('weak')
    strong = build('strong', skill='Attack Boost', level=4)
    duplicate = strong.model_copy(update={'id': 'duplicate'}, deep=True)
    for candidate in (weak, strong, duplicate):
        candidate.search_stats = {'evaluated': 100, 'search_limit': 100,
                                  'elapsed_seconds': .5, 'evaluated_by_weapon': {'test': 100}}
    ranked = rank_portfolio([[weak, strong], [duplicate]])
    assert len(ranked) == 2
    assert ranked[0].result.practical_dps == strong.result.practical_dps
    assert ranked[1].id == 'weak'
    assert ranked[0].search_stats['evaluated'] == 200
    assert ranked[0].search_stats['elapsed_seconds'] == 1
    assert ranked[0].search_stats['evaluated_by_weapon'] == {'test': 200}


def test_every_cached_alternative_is_legal_current_and_reproducible():
    from app.main import META_BUILD_CANDIDATES, load_meta_build_cache

    path = Path(__file__).parents[1] / 'app/meta_build_cache.json'
    original = path.read_bytes()
    cache = json.loads(original)
    # Saved equipment stays intact; the existing loader refreshes legacy math in memory.
    load_meta_build_cache()
    assert not cache['failures']
    assert set(cache['candidates']) == {preset.id for preset in META_BUILD_PRESETS}
    for preset in META_BUILD_PRESETS:
        candidates = META_BUILD_CANDIDATES[preset.id]
        assert len(candidates) == 2, preset.id
        saved_equipment = {raw['id']: SavedBuild.model_validate(raw).equipment for raw in cache['candidates'][preset.id]}
        scores = []
        for build in candidates:
            assert build.equipment == saved_equipment[build.id]
            if cache['engine_version'] != ENGINE_VERSION:
                assert build.provenance['needs_search_refresh'] is True
            calculated = calculate_build(build.equipment, build.scenario)
            assert not calculated.slot_warnings, build.id
            assert build.result.engine_version == ENGINE_VERSION, build.id
            assert calculated.practical_dps == build.result.practical_dps, build.id
            assert calculated == build.result, build.id
            assert bool(build.equipment.custom_weapon) == ('progress' not in preset.profile), build.id
            assert all(calculated.active_skills.get(skill, 0) >= level
                       for skill, level in build.provenance.get('required_skills', {}).items()), build.id
            scores.append(calculated.practical_dps)
        assert scores == sorted(scores, reverse=True), preset.id
    assert path.read_bytes() == original

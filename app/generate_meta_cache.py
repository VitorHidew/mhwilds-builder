import json
from datetime import datetime, timezone
from pathlib import Path

from app.meta_presets import META_BUILD_PRESETS, META_SOURCES
from app.models import OptimizerSettings, ScenarioSettings
from app.optimizer import run_optimizer
from app.combat_rules import ENGINE_VERSION


CACHE_PATH = Path(__file__).with_name("meta_build_cache.json")


def rank_portfolio(runs: list[list]) -> list:
    unique = {}
    stats = [run[0].search_stats for run in runs if run]
    by_weapon = {}
    for stat in stats:
        for weapon_id, count in stat.get("evaluated_by_weapon", {}).items():
            by_weapon[weapon_id] = by_weapon.get(weapon_id, 0) + count
    for run in runs:
        for candidate in run:
            key = json.dumps(candidate.equipment.model_dump(mode="json"), sort_keys=True)
            if key not in unique or candidate.result.practical_dps > unique[key].result.practical_dps:
                unique[key] = candidate
    ranked = sorted(unique.values(), key=lambda build: build.result.practical_dps, reverse=True)[:2]
    for candidate in ranked:
        candidate.provenance = {**candidate.provenance, "method": "portfolio_beam_search",
                                "search_configs": ["fast", "expanded_pool"]}
        candidate.search_stats = {**candidate.search_stats,
            "evaluated": sum(stat.get("evaluated", 0) for stat in stats),
            "search_limit": sum(stat.get("search_limit", 0) for stat in stats),
            "elapsed_seconds": round(sum(stat.get("elapsed_seconds", 0) for stat in stats), 3),
            "legal_candidates": sum(stat.get("legal_candidates", 0) for stat in stats),
            "budget_exhausted": any(stat.get("budget_exhausted", False) for stat in stats),
            "evaluated_by_weapon": by_weapon, "weapon_count": len(by_weapon),
            "global_optimum_proven": False, "portfolio_runs": stats,
            "evaluation_count_includes_repeats": True}
    return ranked


def scenario_for(profile: str, monster_id: str) -> ScenarioSettings:
    scenario = ScenarioSettings(
        monster_id=monster_id,
        agitator_uptime=0.8,
        burst_uptime=0.9,
        weakness_exploit_uptime=0.85,
    )
    if profile == "dps_max":
        scenario.agitator_uptime = 0.95
        scenario.burst_uptime = 0.95
        scenario.weakness_exploit_uptime = 0.95
    elif profile == "dps_conforto":
        scenario.agitator_uptime = 0.75
        scenario.burst_uptime = 0.8
    return scenario


def generate_cache() -> dict:
    builds = []
    candidates_by_preset = {}
    failures = []
    for index, preset in enumerate(META_BUILD_PRESETS, start=1):
        settings = OptimizerSettings(
            weapon_type=preset.weapon_type,
            preset_id=preset.id,
            monster_id=preset.monster_id,
            scenario=scenario_for(preset.profile, preset.monster_id),
            max_results=2,
            sort_by="practical_dps",
            search_limit=900,
            armor_pool_limit=12,
            weapon_pool_limit=4,
            talisman_pool_limit=8,
            use_transcendence=preset.use_transcendence,
        )
        fast_settings = settings.model_copy(update={"armor_pool_limit": 8, "weapon_pool_limit": 2, "talisman_pool_limit": 6})
        result = rank_portfolio([run_optimizer(fast_settings), run_optimizer(settings)])
        if len(result) < 2:
            failures.append(preset.id)
            continue
        best_dps = result[0].result.practical_dps
        serialized_candidates = []
        for rank, candidate in enumerate(result, start=1):
            gap = (1 - candidate.result.practical_dps / best_dps) * 100 if best_dps else 0
            candidate.id = preset.id if rank == 1 else f"{preset.id}_alternativa_{rank}"
            candidate.name = preset.name if rank == 1 else f"{preset.name} - alternativa {rank}"
            comparison = "melhor encontrada na busca" if rank == 1 else f"{gap:.1f}% atrás da melhor encontrada"
            candidate.description = (
                f"Pré-calculada | {comparison} | {preset.description} | {candidate.description}"
            )
            serialized_candidates.append(candidate.model_dump(mode="json"))
        builds.append(serialized_candidates[0])
        candidates_by_preset[preset.id] = serialized_candidates
        print(f"[{index:03d}/{len(META_BUILD_PRESETS)}] {preset.id}")

    payload = {
        "version": ENGINE_VERSION,
        "engine_version": ENGINE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": META_SOURCES,
        "builds": builds,
        "candidates": candidates_by_preset,
        "failures": failures,
    }
    if failures:
        raise RuntimeError(f"Cache anterior preservado; presets sem resultado: {failures}")
    pending = CACHE_PATH.with_suffix(".pending.json")
    pending.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    pending.replace(CACHE_PATH)
    return payload


if __name__ == "__main__":
    generated = generate_cache()
    print(f"Cache salvo: {len(generated['builds'])} builds; falhas: {len(generated['failures'])}")

"""Recalculate snapshots without modifying the user's saved builds."""
import hashlib
import json

from app.combat_rules import ENGINE_VERSION
from app.engine import calculate_build, resolve_weapon
from app.models import BuildCompareRequest
from app.rotations import rotations_for_weapon


def compare_builds(payload: BuildCompareRequest):
    rows, errors = [], []
    for saved in payload.builds:
        try:
            weapon = resolve_weapon(saved.equipment)
            available = rotations_for_weapon(weapon.weapon_type)
            if payload.rotation_mode == "selected" and payload.scenario.rotation_id not in {r.id for r in available}:
                raise ValueError("O combo selecionado nao pertence a esta classe de arma.")
            if payload.rotation_mode == "best":
                rotation_ids = [rotation.id for rotation in available]
            else:
                rotation_ids = [payload.scenario.rotation_id if payload.rotation_mode == "selected" else saved.scenario.rotation_id]
            candidates = []
            for rotation_id in rotation_ids:
                scenario = payload.scenario.model_copy(update={"rotation_id": rotation_id}, deep=True)
                candidates.append((calculate_build(saved.equipment, scenario), scenario))
            result, scenario = max(candidates, key=lambda row: row[0].practical_dps)
            if result.slot_warnings:
                raise ValueError("; ".join(result.slot_warnings))
            build = saved.model_copy(update={"result": result, "scenario": scenario}, deep=True)
            impacts = []
            # Isolated removal is contextual, not an additive attribution of total DPS.
            for name in result.modeled_skills:
                without = calculate_build(build.equipment, scenario, skill_overrides={name: 0})
                delta = round(result.practical_dps - without.practical_dps, 1)
                if delta > 0:
                    impacts.append({"skill": name, "dps_delta": delta,
                                    "percent": round(delta / max(result.practical_dps, .1) * 100, 2)})
            impacts.sort(key=lambda item: (-item["dps_delta"], item["skill"]))
            rows.append({"build": build, "skill_impacts": impacts, "dps_difference_percent": 0.0})
        except ValueError as exc:
            errors.append({"id": saved.id, "name": saved.name, "message": str(exc)})
    rows.sort(key=lambda row: (-row["build"].result.practical_dps, row["build"].id))
    best = rows[0]["build"].result.practical_dps if rows else 0
    for row in rows:
        row["dps_difference_percent"] = round((row["build"].result.practical_dps / best - 1) * 100, 2) if best else 0
    shared = payload.scenario.model_dump(mode="json", exclude={"rotation_id"})
    fingerprint = hashlib.sha256(json.dumps(shared, sort_keys=True).encode()).hexdigest()[:12]
    return {"engine_version": ENGINE_VERSION, "scenario": shared,
            "scenario_fingerprint": fingerprint, "rotation_mode": payload.rotation_mode,
            "rows": rows, "errors": errors}

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.models import BuildEquipment, BuildResult, InventoryTalisman, SavedBuild, SavedDamage, ScenarioSettings


@pytest.fixture(autouse=True)
def isolated_persistent_storage(monkeypatch):
    stores = (
        main_module.SAVED_BUILDS_STORAGE,
        main_module.TALISMAN_INVENTORY_STORAGE,
        main_module.SAVED_DAMAGE_STORAGE,
    )
    snapshots = [dict(store) for store in stores]
    for store in stores:
        store.clear()

    monkeypatch.setattr(main_module, "save_builds_storage", lambda: None)
    monkeypatch.setattr(main_module, "save_talismans_storage", lambda: None)
    monkeypatch.setattr(main_module, "save_damage_storage", lambda: None)
    yield

    for store, snapshot in zip(stores, snapshots):
        store.clear()
        store.update(snapshot)


def saved_build_payload(record_id="build_security", name="Build segura"):
    equipment = BuildEquipment(
        weapon_id="weapon_test",
        helm_id="helm_test",
        chest_id="chest_test",
        arms_id="arms_test",
        waist_id="waist_test",
        legs_id="legs_test",
        talisman_id="talisman_test",
    )
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
        damage_per_cycle=100,
        practical_dps=20,
        damage_per_min=1200,
        combined_score=20,
    )
    return SavedBuild(
        id=record_id,
        name=name,
        equipment=equipment,
        scenario=ScenarioSettings(),
        result=result,
    ).model_dump(mode="json")


def saved_damage_payload(record_id="damage_security"):
    build = saved_build_payload()
    return SavedDamage(
        id=record_id,
        name="Resultado seguro",
        build_name=build["name"],
        equipment=build["equipment"],
        scenario=build["scenario"],
        result=build["result"],
    ).model_dump(mode="json")


def talisman_payload(record_id="talisman_security"):
    return InventoryTalisman(
        id=record_id,
        talisman={
            "name": "Talismã seguro",
            "skill_1": "Attack Boost",
            "skill_1_lvl": 1,
            "slots": [1],
            "slot_kinds": ["armor"],
        },
    ).model_dump(mode="json")


def test_session_cookie_is_private_and_owner_is_not_returned():
    with TestClient(main_module.app) as client:
        response = client.get("/api/session")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "owner" not in response.text.lower()


@pytest.mark.parametrize(
    ("list_url", "save_url", "delete_url", "payload"),
    [
        ("/api/builds", "/api/builds/save", "/api/builds/build_security", saved_build_payload()),
        (
            "/api/talismans/inventory",
            "/api/talismans/inventory",
            "/api/talismans/inventory/talisman_security",
            talisman_payload(),
        ),
        ("/api/damage", "/api/damage/save", "/api/damage/damage_security", saved_damage_payload()),
    ],
)
def test_saved_records_are_isolated_between_browser_sessions(list_url, save_url, delete_url, payload):
    with TestClient(main_module.app) as owner, TestClient(main_module.app) as outsider:
        assert owner.get("/api/session").status_code == 200
        assert outsider.get("/api/session").status_code == 200

        created = owner.post(save_url, json=payload)
        assert created.status_code == 200
        assert "owner_id" not in created.json()
        assert [item["id"] for item in owner.get(list_url).json()] == [payload["id"]]
        assert outsider.get(list_url).json() == []
        assert outsider.delete(delete_url).status_code == 404
        assert [item["id"] for item in owner.get(list_url).json()] == [payload["id"]]
        assert owner.delete(delete_url).status_code == 200
        assert owner.get(list_url).json() == []


def test_tampered_session_cookie_cannot_select_an_owner():
    with TestClient(main_module.app) as owner, TestClient(main_module.app) as attacker:
        owner.get("/api/session")
        assert owner.post("/api/builds/save", json=saved_build_payload()).status_code == 200
        attacker.cookies.set(main_module.SESSION_COOKIE_NAME, "known-owner.invalid-signature")

        response = attacker.get("/api/builds")

        assert response.status_code == 200
        assert response.json() == []
        assert response.headers.get("set-cookie")


def test_legacy_local_records_are_claimed_by_only_the_first_local_session():
    legacy = SavedBuild(**saved_build_payload()).model_copy(update={"owner_id": main_module.LEGACY_OWNER_ID})
    main_module.SAVED_BUILDS_STORAGE[(main_module.LEGACY_OWNER_ID, legacy.id)] = legacy

    with TestClient(main_module.app) as first_browser, TestClient(main_module.app) as second_browser:
        assert first_browser.get("/api/session").status_code == 200
        assert [item["id"] for item in first_browser.get("/api/builds").json()] == [legacy.id]
        assert second_browser.get("/api/session").status_code == 200
        assert second_browser.get("/api/builds").json() == []


def test_cors_allows_local_frontend_and_rejects_external_origin():
    with TestClient(main_module.app) as client:
        allowed = client.options(
            "/api/builds",
            headers={"Origin": "http://localhost:8000", "Access-Control-Request-Method": "GET"},
        )
        blocked = client.options(
            "/api/builds",
            headers={"Origin": "https://attacker.example", "Access-Control-Request-Method": "GET"},
        )

    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:8000"
    assert "access-control-allow-origin" not in blocked.headers


def test_security_headers_are_applied_to_frontend_and_api():
    with TestClient(main_module.app) as client:
        responses = (client.get("/"), client.get("/api/data/version"))

    for response in responses:
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
        assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
        assert "object-src 'none'" in response.headers["content-security-policy"]
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_sensitive_frontend_renderers_do_not_interpolate_saved_values_as_html():
    script = (Path(__file__).parents[1] / "static" / "js" / "app.js").read_text(encoding="utf-8")

    forbidden_fragments = (
        "<strong>${d.name",
        "<strong>${b.name}",
        "<strong>${best.name}",
        "<strong>${t.name",
        "onclick=\"deleteSavedDamage('${d.id}')\"",
        "onclick=\"loadBuildIntoBuilder('${b.id}')\"",
        "onclick=\"equipInventoryTalisman('${item.id}')\"",
    )
    assert all(fragment not in script for fragment in forbidden_fragments)
    assert "box.replaceChildren(heading, equipment, stats, skills)" in script
    assert "tbody.appendChild(row)" in script
    assert "button.addEventListener('click', handler)" in script
    assert "prompt(" not in script
    assert "requestBuildName(build.name)" in script


def test_frontend_assets_are_modular_and_served():
    with TestClient(main_module.app) as client:
        index = client.get("/")
        script = client.get("/static/js/app.js")
        stylesheet = client.get("/static/css/app.css")

    assert index.status_code == script.status_code == stylesheet.status_code == 200
    assert '<script src="/static/js/app.js?v=20260925"></script>' in index.text
    assert '<link rel="stylesheet" href="/static/css/app.css?v=20260925">' in index.text
    assert '/static/js/experience.js?v=20260925' in index.text
    assert '/static/css/experience.css?v=20260925' in index.text
    assert "function saveCurrentBuild()" in script.text
    assert ":root" in stylesheet.text


def test_health_endpoint_verifies_versioned_game_data():
    with TestClient(main_module.app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == main_module.app.version
    assert payload["data"]["schema_version"] == 1
    assert payload["data"]["counts"]["weapons"] == len(main_module.WEAPONS_DB)
    assert payload["data"]["counts"]["armors"] == len(main_module.ARMORS_DB)
    assert payload["data"]["mismatches"] == {}
    assert all(dataset["exists"] for dataset in payload["data"]["datasets"].values())
    assert all(len(dataset["sha256"]) == 64 for dataset in payload["data"]["datasets"].values())


def test_data_file_hashes_are_cached_until_a_dataset_changes():
    main_module.DATA_HASH_CACHE.clear()
    first = main_module._data_integrity()
    cached = dict(main_module.DATA_HASH_CACHE)
    second = main_module._data_integrity()

    assert first["datasets"] == second["datasets"]
    assert cached == main_module.DATA_HASH_CACHE


def test_backup_contract_is_versioned_bounded_and_local_first():
    script = (Path(__file__).parents[1] / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert "const BACKUP_SCHEMA_VERSION = 1" in script
    assert "BACKUP_MAX_BYTES = 5 * 1024 * 1024" in script
    assert "async function importLocalData(event)" in script
    assert "mergeRecordsById(localBuilds(), backupArray(data, 'builds'), 30)" in script
    assert "mergeRecordsById(localDamage(), backupArray(data, 'damage'), 60)" in script
    assert "mergeRecordsById(localTalismans(), backupArray(data, 'talismans'), 100)" in script
    assert "[...serverBuilds, ...localBuilds()]" in script


def test_equipment_photo_endpoints_use_local_contextual_fallbacks(monkeypatch):
    monkeypatch.setattr(main_module, "get_weapon_equipment_image", lambda name: {"image_url": ""})
    monkeypatch.setattr(main_module, "get_armor_equipment_image", lambda name: {"image_url": ""})
    armor = next(item for item in main_module.ARMORS_DB if not item.name.startswith("("))

    with TestClient(main_module.app) as client:
        weapon_response = client.get("/api/equipment-photo/weapon", params={"name": "Abaddonian Chobotnice"})
        armor_response = client.get("/api/equipment-photo/armor", params={"name": armor.name})
        unknown_response = client.get("/api/equipment-photo/weapon", params={"name": "Unknown Weapon"})

    assert weapon_response.status_code == 200
    assert weapon_response.headers["content-type"] == "image/png"
    assert armor_response.status_code == 200
    assert armor_response.headers["content-type"] == "image/png"
    assert unknown_response.status_code == 404


def test_weapon_photo_uses_local_fallback_when_remote_download_fails(monkeypatch):
    proxied_url = main_module._proxied_url(main_module.GOGMA_WEAPON_IMAGES["ostrak oblivion"])
    monkeypatch.setattr(main_module, "get_weapon_equipment_image", lambda name: {"image_url": proxied_url})

    def reject_remote_image(url):
        raise main_module.HTTPException(status_code=502, detail="Remote image unavailable")

    monkeypatch.setattr(main_module, "proxy_image", reject_remote_image)

    with TestClient(main_module.app) as client:
        response = client.get("/api/equipment-photo/weapon", params={"name": "Ostrak Oblivion"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

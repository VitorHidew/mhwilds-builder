import json
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
import urllib.parse
import urllib.request
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.data import ARMORS_DB, DECORATIONS_DB, EXTRA_GAME_DATA, MONSTERS_DB, ROTATIONS_DB, TALISMANS_DB, WEAPONS_DB
from app.engine import calculate_build, resolve_weapon
from app.legality import preset_context, validate_build
from app.meta_presets import META_PRESETS_BY_ID
from app.comparison import compare_builds
from app.gog_recommendations import recommend_gog_weapon
from app.meta_presets import META_BUILD_PRESETS
from app.models import (
    BuildEquipment, BuildResult, BuildCompareRequest, GogRecommendationRequest, GogWeaponRecommendation,
    InventoryTalisman, MetaBuildPreset,
    OptimizerSettings, RotationCompareRequest, RotationComparison,
    SavedBuild, SavedDamage, ScenarioSettings
)
from app.optimizer import run_optimizer
from app.rotations import rotations_for_weapon

app = FastAPI(
    title="MH Wilds Build Optimizer & Calculator API",
    description="Motor completo de cálculo e otimização de builds de Monster Hunter Wilds.",
    version="2.0.0"
)

DEFAULT_ALLOWED_ORIGINS = "http://127.0.0.1:8000,http://localhost:8000"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("MHWILDS_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]
if "*" in ALLOWED_ORIGINS:
    raise RuntimeError("MHWILDS_ALLOWED_ORIGINS não pode conter '*' quando cookies de sessão estão ativos.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith(("/static/js/", "/static/css/")):
        response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "frame-ancestors 'none'; form-action 'self'"
    )
    if APP_ENV == "production" and request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

DEFAULT_STORAGE_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "mhwilds_builder"
STORAGE_DIR = Path(os.getenv("MHWILDS_STORAGE_DIR", DEFAULT_STORAGE_DIR))
BUILDS_FILE = STORAGE_DIR / "saved_builds.json"
TALISMANS_FILE = STORAGE_DIR / "talisman_inventory.json"
DAMAGE_FILE = STORAGE_DIR / "saved_damage.json"
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
STATIC_DIR = PROJECT_DIR / "static"
STATIC_ASSET_DIR = STATIC_DIR / "assets"
DATA_MANIFEST_FILE = APP_DIR / "data_manifest.json"
META_BUILD_CACHE_FILE = APP_DIR / "meta_build_cache.json"

SAVED_BUILDS_STORAGE: dict[tuple[str, str], SavedBuild] = {}
SAVED_DAMAGE_STORAGE: dict[tuple[str, str], SavedDamage] = {}
TALISMAN_INVENTORY_STORAGE: dict[tuple[str, str], InventoryTalisman] = {}
META_BUILD_CACHE: dict[str, SavedBuild] = {}
META_BUILD_CANDIDATES: dict[str, list[SavedBuild]] = {}
EQUIPMENT_IMAGE_CACHE: dict[str, str] = {}
REMOTE_IMAGE_CACHE: OrderedDict[str, tuple[bytes, str]] = OrderedDict()
REMOTE_IMAGE_CACHE_LIMIT = 256
REMOTE_IMAGE_FAILURES: dict[str, float] = {}
REMOTE_IMAGE_FAILURE_TTL = 300.0
DATA_HASH_CACHE: dict[Path, tuple[int, int, str]] = {}
STORAGE_LOCK = threading.RLock()
LEGACY_OWNER_ID = "__legacy_local_data__"
SESSION_COOKIE_NAME = "mhwilds_session"
SESSION_SECRET_FILE = STORAGE_DIR / ".session_secret"
APP_ENV = os.getenv("MHWILDS_ENV", "development").strip().casefold()


def _load_session_secret() -> bytes:
    configured = os.getenv("MHWILDS_SESSION_SECRET", "")
    if configured:
        if len(configured) < 32:
            raise RuntimeError("MHWILDS_SESSION_SECRET deve ter pelo menos 32 caracteres.")
        return configured.encode("utf-8")
    if APP_ENV == "production":
        raise RuntimeError("MHWILDS_SESSION_SECRET é obrigatório em produção.")

    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        if SESSION_SECRET_FILE.exists():
            stored = SESSION_SECRET_FILE.read_text(encoding="utf-8").strip()
            if len(stored) >= 32:
                return stored.encode("utf-8")
        generated = secrets.token_urlsafe(48)
        try:
            descriptor = os.open(SESSION_SECRET_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(generated)
        except FileExistsError:
            generated = SESSION_SECRET_FILE.read_text(encoding="utf-8").strip()
        return generated.encode("utf-8")
    except OSError as exc:
        print(f"[AVISO] Segredo de sessão apenas em memória: {exc}")
        return secrets.token_bytes(48)


SESSION_SECRET = _load_session_secret()


def _sign_session(owner_id: str) -> str:
    signature = hmac.new(SESSION_SECRET, owner_id.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{owner_id}.{signature}"


def _verify_session(token: str | None) -> str | None:
    if not token or "." not in token:
        return None
    owner_id, signature = token.rsplit(".", 1)
    if not re.fullmatch(r"[A-Za-z0-9_-]{24,128}", owner_id):
        return None
    expected = hmac.new(SESSION_SECRET, owner_id.encode("utf-8"), hashlib.sha256).hexdigest()
    return owner_id if hmac.compare_digest(signature, expected) else None

# Imagens verificadas na tabela de armas Gogartianas da FextraLife.  A wiki
# Fandom não distingue de forma confiável a aparência Artiana da Gogartiana.
GOGMA_WEAPON_IMAGES: dict[str, str] = {
    "ostrak oblivion": "https://static0.fextralifeimages.com/file/monsterhunterwilds/8/8b/Ostrak_oblivion-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "eternal cusp": "https://static0.fextralifeimages.com/file/monsterhunterwilds/7/7f/Eternal_cusp-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "promised abyss": "https://static0.fextralifeimages.com/file/monsterhunterwilds/f/f5/Promised-abyss-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "wicked regnum": "https://static0.fextralifeimages.com/file/monsterhunterwilds/a/aa/Wicked_regnum-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "headsman's hamus": "https://static0.fextralifeimages.com/file/monsterhunterwilds/6/69/Headsmans_hamus-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "auguring omen": "https://static0.fextralifeimages.com/file/monsterhunterwilds/f/fb/Auguring_omen-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "limbo llor": "https://static0.fextralifeimages.com/file/monsterhunterwilds/7/70/Limbo_llor-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "calamitous angel": "https://static0.fextralifeimages.com/file/monsterhunterwilds/8/8d/Calamitous_angel-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "trembling hels": "https://static0.fextralifeimages.com/file/monsterhunterwilds/a/aa/Trembling_hels-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "bound admonition": "https://static0.fextralifeimages.com/file/monsterhunterwilds/f/fa/Bound_admonition-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "bethorned agony": "https://static0.fextralifeimages.com/file/monsterhunterwilds/2/22/Bethorned_agony-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "onyx choros": "https://static0.fextralifeimages.com/file/monsterhunterwilds/0/0d/Onyx_choros-gogma-artian-weapon-mhwilds-wiki-guide.png",
    "kyrie verd": "https://static0.fextralifeimages.com/file/monsterhunterwilds/d/d0/Kyrie_verd-gogma-artian-weapon-mhwilds-wiki-guide.png",
    # A página usa a grafia "Ather Pike" para a Lança.
    "aether pike": "https://static0.fextralifeimages.com/file/monsterhunterwilds/3/3b/Ather_pike-artian-weapon-mhwilds-wiki-guide.png",
}

WEAPON_TYPE_ICON_FILES: dict[str, str] = {
    "Great Sword": "Great Sword Icon White.png",
    "Long Sword": "Long Sword Icon White.png",
    "Sword & Shield": "Sword and Shield Icon White.png",
    "Dual Blades": "Dual Blades Icon White.png",
    "Hammer": "Hammer Icon White.png",
    "Hunting Horn": "Hunting Horn Icon White.png",
    "Lance": "Lance Icon White.png",
    "Gunlance": "Gunlance Icon White.png",
    "Switch Axe": "Switch Axe Icon White.png",
    "Charge Blade": "Charge Blade Icon White.png",
    "Insect Glaive": "Insect Glaive Icon White.png",
    "Light Bowgun": "Light Bowgun Icon White.png",
    "Heavy Bowgun": "Heavy Bowgun Icon White.png",
    "Bow": "Bow Icon White.png",
}

GOGMA_WEAPON_TYPES: dict[str, str] = {
    "ostrak oblivion": "Great Sword",
    "headsman's hamus": "Long Sword",
    "kyrie verd": "Sword & Shield",
    "eternal cusp": "Dual Blades",
    "bound admonition": "Hammer",
    "onyx choros": "Hunting Horn",
    "aether pike": "Lance",
    "auguring omen": "Gunlance",
    "wicked regnum": "Switch Axe",
    "promised abyss": "Charge Blade",
    "limbo llor": "Insect Glaive",
    "bethorned agony": "Light Bowgun",
    "trembling hels": "Heavy Bowgun",
    "calamitous angel": "Bow",
}

ARMOR_SLOT_ICON_FILES: dict[str, str] = {
    "helm": "MH3icon-Helm.png",
    "chest": "MH3icon-Plate.png",
    "arms": "MH3icon-Gauntlets.png",
    "waist": "MH3icon-Waist.png",
    "legs": "MH3icon-Leggings.png",
}


def load_meta_build_cache() -> None:
    from app.combat_rules import ENGINE_VERSION

    def refresh(item):
        build = SavedBuild.model_validate(item)
        if build.result.engine_version != ENGINE_VERSION:
            build.result = calculate_build(build.equipment, build.scenario)
            build.provenance = {**build.provenance, "engine_version": ENGINE_VERSION,
                                "method": "recalculated_legacy_cache", "needs_search_refresh": True}
            build.description = "Cache legado recalculado. Execute uma nova busca para atualizar as alternativas."
        build.search_stats = {**build.search_stats, "cache_hit": True}
        preset_id = build.provenance.get("preset_id") or build.id.split("_alternativa_")[0]
        preset = META_PRESETS_BY_ID.get(preset_id)
        build.legality = validate_build(build.equipment,
            context=preset_context(preset) if preset else None,
            expected_weapon_type=preset.weapon_type if preset else None,
            required_skills=build.provenance.get("required_skills", {}),
            context_basis="category_checkpoint" if preset else "unknown")
        return build

    try:
        raw = json.loads(META_BUILD_CACHE_FILE.read_text(encoding="utf-8"))
        META_BUILD_CACHE.clear()
        META_BUILD_CANDIDATES.clear()
        for item in raw.get("builds", []):
            build = refresh(item)
            META_BUILD_CACHE[build.id] = build
        for preset_id, items in raw.get("candidates", {}).items():
            candidates = sorted([refresh(item) for item in items],
                                key=lambda build: build.result.practical_dps, reverse=True)
            META_BUILD_CANDIDATES[preset_id] = candidates
            if candidates:
                META_BUILD_CACHE[preset_id] = candidates[0].model_copy(update={"id": preset_id})
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[AVISO] Cache de builds meta indisponível: {exc}")


load_meta_build_cache()


def _load_visual_metadata() -> tuple[dict[str, str], dict[str, int]]:
    raw_path = APP_DIR / "mhdb_raw_data.json"
    try:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, {}

    armor_sets = {
        armor.get("name", "").casefold(): armor.get("armorSet", {}).get("name", "")
        for armor in raw.get("armor", raw.get("armors", []))
        if armor.get("name") and armor.get("armorSet", {}).get("name")
    }
    skill_icons = {
        skill.get("name", "").casefold(): int(skill.get("icon", {}).get("id", 0)) - 1
        for skill in raw.get("skills", [])
        if skill.get("name") and skill.get("icon", {}).get("id")
    }
    return armor_sets, skill_icons


ARMOR_SET_BY_NAME, SKILL_ICON_INDEX_BY_NAME = _load_visual_metadata()
SKILL_ICON_DIR = STATIC_ASSET_DIR / "skill-icons"
app.mount("/assets", StaticFiles(directory=STATIC_ASSET_DIR), name="assets")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def sort_by_name(items):
    return sorted(items, key=lambda item: item.name.casefold())


def _load_owned_items(path: Path, model_type):
    if not path.exists():
        return {}
    raw_items = json.loads(path.read_text(encoding="utf-8"))
    loaded = {}
    for raw_item in raw_items:
        payload = dict(raw_item)
        owner_id = str(payload.pop("_owner_id", payload.pop("owner_id", LEGACY_OWNER_ID)))
        item = model_type(**payload).model_copy(update={"owner_id": owner_id})
        loaded[(owner_id, item.id)] = item
    return loaded


def load_storage():
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[AVISO] Não foi possível criar pasta de armazenamento: {exc}")
        return
    if BUILDS_FILE.exists():
        try:
            SAVED_BUILDS_STORAGE.clear()
            SAVED_BUILDS_STORAGE.update(_load_owned_items(BUILDS_FILE, SavedBuild))
        except Exception as exc:
            print(f"[AVISO] Não foi possível carregar builds salvas: {exc}")
    if TALISMANS_FILE.exists():
        try:
            TALISMAN_INVENTORY_STORAGE.clear()
            TALISMAN_INVENTORY_STORAGE.update(_load_owned_items(TALISMANS_FILE, InventoryTalisman))
        except Exception as exc:
            print(f"[AVISO] Não foi possível carregar inventário de talismãs: {exc}")
    if DAMAGE_FILE.exists():
        try:
            SAVED_DAMAGE_STORAGE.clear()
            SAVED_DAMAGE_STORAGE.update(_load_owned_items(DAMAGE_FILE, SavedDamage))
        except Exception as exc:
            print(f"[AVISO] Não foi possível carregar danos salvos: {exc}")


def _write_owned_storage(path: Path, items) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    data = []
    for item in items:
        payload = item.model_dump(mode="json")
        payload["_owner_id"] = item.owner_id or LEGACY_OWNER_ID
        data.append(payload)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def save_builds_storage():
    try:
        with STORAGE_LOCK:
            _write_owned_storage(BUILDS_FILE, SAVED_BUILDS_STORAGE.values())
    except OSError as exc:
        print(f"[AVISO] Builds mantidas em memória; não foi possível gravar em disco: {exc}")


def save_talismans_storage():
    try:
        with STORAGE_LOCK:
            _write_owned_storage(TALISMANS_FILE, TALISMAN_INVENTORY_STORAGE.values())
    except OSError as exc:
        print(f"[AVISO] Talismãs mantidos em memória; não foi possível gravar em disco: {exc}")


def save_damage_storage():
    try:
        with STORAGE_LOCK:
            _write_owned_storage(DAMAGE_FILE, SAVED_DAMAGE_STORAGE.values())
    except OSError as exc:
        print(f"[AVISO] Danos mantidos em memória; não foi possível gravar em disco: {exc}")


load_storage()


def _claim_legacy_local_data(owner_id: str, request: Request) -> None:
    client_host = request.client.host if request.client else ""
    if APP_ENV == "production" or client_host not in {"127.0.0.1", "::1", "testclient"}:
        return

    changed_builds = changed_talismans = changed_damage = False
    with STORAGE_LOCK:
        for storage_name, storage in (
            ("builds", SAVED_BUILDS_STORAGE),
            ("talismans", TALISMAN_INVENTORY_STORAGE),
            ("damage", SAVED_DAMAGE_STORAGE),
        ):
            changed = False
            for key, item in list(storage.items()):
                if item.owner_id != LEGACY_OWNER_ID:
                    continue
                storage.pop(key)
                owned_item = item.model_copy(update={"owner_id": owner_id})
                storage[(owner_id, owned_item.id)] = owned_item
                changed = True
            if storage_name == "builds":
                changed_builds = changed
            elif storage_name == "talismans":
                changed_talismans = changed
            else:
                changed_damage = changed

    if changed_builds:
        save_builds_storage()
    if changed_talismans:
        save_talismans_storage()
    if changed_damage:
        save_damage_storage()


def get_owner_id(request: Request, response: Response) -> str:
    owner_id = _verify_session(request.cookies.get(SESSION_COOKIE_NAME))
    if owner_id:
        response.headers["Cache-Control"] = "no-store"
        return owner_id

    owner_id = secrets.token_urlsafe(24)
    secure_cookie = APP_ENV == "production" or request.url.scheme == "https"
    response.set_cookie(
        SESSION_COOKIE_NAME,
        _sign_session(owner_id),
        max_age=31_536_000,
        httponly=True,
        secure=secure_cookie,
        samesite="strict",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    _claim_legacy_local_data(owner_id, request)
    return owner_id


@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/session")
def initialize_session(owner_id: str = Depends(get_owner_id)):
    return {"status": "ready"}


def _data_integrity() -> dict:
    try:
        manifest = json.loads(DATA_MANIFEST_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "error",
            "schema_version": None,
            "message": f"Manifesto de dados indisponível: {exc}",
            "datasets": {},
        }

    collections = {
        "weapons": len(WEAPONS_DB),
        "armors": len(ARMORS_DB),
        "decorations": len(DECORATIONS_DB),
        "talismans": len(TALISMANS_DB),
        "monsters": len(MONSTERS_DB),
        "skills": len(EXTRA_GAME_DATA.get("skills", [])),
        "items": len(EXTRA_GAME_DATA.get("items", [])),
        "locations": len(EXTRA_GAME_DATA.get("locations", [])),
        "armor_sets": len(EXTRA_GAME_DATA.get("armor_sets", [])),
    }
    expected = manifest.get("expected_counts", {})
    mismatches = {
        key: {"expected": expected.get(key), "actual": value}
        for key, value in collections.items()
        if expected.get(key) != value
    }
    datasets = {}
    for filename in manifest.get("datasets", []):
        path = APP_DIR / filename
        datasets[filename] = {
            "exists": path.is_file(),
            "sha256": _cached_file_sha256(path) if path.is_file() else None,
        }
    status = "ok" if not mismatches and all(item["exists"] for item in datasets.values()) else "degraded"
    return {
        "status": status,
        "schema_version": manifest.get("schema_version"),
        "game_data_version": manifest.get("game_data_version"),
        "generated_at": manifest.get("generated_at"),
        "source": manifest.get("source"),
        "counts": collections,
        "mismatches": mismatches,
        "datasets": datasets,
    }


def _cached_file_sha256(path: Path) -> str:
    stat = path.stat()
    cache_key = (stat.st_mtime_ns, stat.st_size)
    cached = DATA_HASH_CACHE.get(path)
    if cached and cached[:2] == cache_key:
        return cached[2]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    DATA_HASH_CACHE[path] = (cache_key[0], cache_key[1], digest)
    return digest


@app.get("/api/health")
def health_check():
    integrity = _data_integrity()
    payload = {
        "status": "ok" if integrity["status"] == "ok" else "degraded",
        "application": app.title,
        "version": app.version,
        "data": integrity,
    }
    return JSONResponse(payload, status_code=200 if integrity["status"] == "ok" else 503)


@app.get("/api/data/version")
def get_data_version():
    return _data_integrity()



LEGACY_SKILL_PT = {
    "Attack Boost": "Ataque", "Critical Eye": "Olho Crítico", "Critical Boost": "Impulso Crítico",
    "Weakness Exploit": "Ponto Fraco", "Agitator": "Desafiante", "Burst": "Ímpeto",
    "Maximum Might": "Poder Máximo", "Peak Performance": "Performance Máxima", "Offensive Guard": "Guarda Ofensiva",
    "Counterstrike": "Contra-ataque", "Coalescence": "Coalescência", "Latent Power": "Poder Latente",
    "Resentment": "Ressentimento", "Antivirus": "Antivírus", "Foray": "Incursão",
    "Fire Attack": "Ataque de Fogo", "Water Attack": "Ataque de Água", "Thunder Attack": "Ataque de Raio",
    "Ice Attack": "Ataque de Gelo", "Dragon Attack": "Ataque de Dragão", "Poison Attack": "Ataque de Veneno",
    "Paralysis Attack": "Ataque de Paralisia", "Sleep Attack": "Ataque de Sono", "Blast Attack": "Ataque de Explosão",
    "Fire Resistance": "Resistência a Fogo", "Water Resistance": "Resistência a Água",
    "Thunder Resistance": "Resistência a Raio", "Ice Resistance": "Resistência a Gelo",
    "Dragon Resistance": "Resistência a Dragão", "Poison Resistance": "Resistência a Veneno",
    "Paralysis Resistance": "Resistência a Paralisia", "Sleep Resistance": "Resistência a Sono",
    "Bleeding Resistance": "Resistência a Sangramento", "Hunger Resistance": "Resistência à Fome",
    "Bind Resistance": "Resistência a Amarras", "Stun Resistance": "Resistência a Atordoamento",
    "Evade Window": "Janela de Esquiva", "Evade Extender": "Extensor de Esquiva", "Constitution": "Constituição",
    "Stamina Surge": "Recuperação de Vigor", "Stamina Thief": "Ladrão de Vigor",
    "Speed Eating": "Comer Rápido", "Free Meal": "Refeição Grátis", "Mushroomancer": "Cogumeleiro",
    "Wide-Range": "Área Ampla", "Recovery Speed": "Velocidade de Recuperação", "Recovery Up": "Recuperação Aumentada",
    "Partbreaker": "Destruidor", "Slugger": "Nocauteador", "Stamina Thief": "Ladrão de Vigor",
    "Earplugs": "Tampões de Ouvido", "Windproof": "À Prova de Vento", "Tremor Resistance": "Resistência a Tremor",
    "Flinch Free": "Inabalável", "Intimidator": "Intimidador", "Survival Expert": "Especialista em Sobrevivência",
    "Handicraft": "Artesanato", "Razor Sharp": "Afiação Navalha", "Protective Polish": "Polimento Protetor",
    "Master's Touch": "Toque do Mestre", "Mind's Eye": "Olho da Mente", "Bludgeoner": "Contundente",
    "Critical Draw": "Saque Crítico", "Punishing Draw": "Saque Punitivo", "Critical Element": "Elemento Crítico",
    "Critical Status": "Status Crítico", "Charge Master": "Mestre de Carga", "Focus": "Foco",
    "Power Prolonger": "Prolongador de Poder", "Rapid Morph": "Transformação Rápida",
    "Guard": "Guarda", "Guard Up": "Guarda Reforçada", "Load Shells": "Carregar Projéteis",
    "Artillery": "Artilharia", "Capacity Boost": "Capacidade Aumentada", "Horn Maestro": "Maestro do Berrante",
    "Special Ammo Boost": "Munição Especial", "Rapid Fire Up": "Tiro Rápido+", "Normal Shots": "Tiros Normais",
    "Piercing Shots": "Tiros Perfurantes", "Spread/Power Shots": "Tiros Espalhados/Poder",
    "Ballistics": "Balística", "Tetrad Shot": "Tiro Tétrade", "Opening Shot": "Tiro Inicial",
    "Airborne": "Aerotransportado", "Jump Master": "Mestre do Salto", "Entomologist": "Entomologista",
    "Aquatic/Oilsilt Mobility": "Mobilidade Aquática/Oleosa", "Iron Skin": "Pele de Ferro",
}

ARMOR_TERM_PT = {
    "Helm": "Elmo", "Helmet": "Elmo", "Mail": "Peitoral", "Vambraces": "Braçadeiras",
    "Braces": "Braçadeiras", "Coil": "Cintura", "Greaves": "Grevas", "Boots": "Botas",
    "Earrings": "Brincos", "Headdress": "Adorno de Cabeça", "Mask": "Máscara",
    "Headgear": "Elmo", "Hat": "Chapéu", "Hood": "Capuz", "Crown": "Coroa",
    "Armguards": "Guarda-braços", "Guards": "Guardas", "Faulds": "Cintura",
    "Coat": "Cota", "Vest": "Colete", "Jacket": "Jaqueta", "Suit": "Traje",
    "Pants": "Calças", "Leggings": "Perneiras", "Alpha": "Alfa", "Beta": "Beta",
    "Gamma": "Gama", "Low Rank": "Rank Baixo", "High Rank": "Rank Alto",
}


def _load_official_skill_names() -> dict[str, str]:
    localized_path = APP_DIR / "game_data_pt.json"
    try:
        localized = json.loads(localized_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    english_by_id = {
        skill.get("id"): skill.get("name")
        for skill in EXTRA_GAME_DATA.get("skills", [])
        if isinstance(skill, dict) and skill.get("id") is not None and skill.get("name")
    }
    return {
        english_by_id[skill.get("id")]: skill.get("name")
        for skill in localized.get("skills", [])
        if skill.get("id") in english_by_id and skill.get("name")
    }


# Nomes usados pelo cálculo permanecem em inglês; esta tabela vem diretamente
# do locale pt-BR da MHDB e serve apenas à apresentação e à busca reversa.
SKILL_PT = _load_official_skill_names()

JEWEL_TERM_PT = {
    "Jewel": "Joia", "Jwl": "Joia", "Res": "Resist.", "Attack": "Ataque", "Blaze": "Fogo",
    "Stream": "Água", "Bolt": "Raio", "Frost": "Gelo", "Dragon": "Dragão", "Venom": "Veneno",
    "Sleep": "Sono", "Paralyzer": "Paralisia", "Guardian": "Guarda", "Ironwall": "Muralha",
    "Grinder": "Amolador", "Handicraft": "Artesanato", "Destroyer": "Destruidor",
    "Mighty": "Poder Máximo", "Precise": "Precisão", "Sonorous": "Sonoro", "Recovery": "Recuperação",
    "Physique": "Físico", "Jumping": "Salto", "Drain": "Dreno", "Enhancer": "Prolongador",
    "Sane": "Sanidade", "Earplugs": "Tampões", "Mind's Eye": "Olho da Mente",
}

WEAPON_TYPE_PT = {
    "Great Sword": "Espadão",
    "Long Sword": "Espada Longa",
    "Sword & Shield": "Espada e Escudo",
    "Dual Blades": "Duplas-Lâminas",
    "Hammer": "Martelo",
    "Hunting Horn": "Berrante de Caça",
    "Lance": "Lança",
    "Gunlance": "Lançarma",
    "Switch Axe": "Transmachado",
    "Charge Blade": "Lâmina Dínamo",
    "Insect Glaive": "Glaive Inseto",
    "Light Bowgun": "Fuzilarco Leve",
    "Heavy Bowgun": "Fuzilarco Pesado",
    "Bow": "Arco",
}

WEAPON_TERM_PT = {
    "Great Sword": "Espadão", "Long Sword": "Espada Longa", "Sword": "Espada",
    "Shield": "Escudo", "Dual Blades": "Duplas-Lâminas", "Blades": "Lâminas",
    "Hammer": "Martelo", "Hunting Horn": "Berrante de Caça", "Horn": "Berrante",
    "Lance": "Lança", "Gunlance": "Lançarma", "Switch Axe": "Transmachado",
    "Axe": "Machado", "Charge Blade": "Lâmina Dínamo", "Insect Glaive": "Glaive Inseto",
    "Glaive": "Glaive", "Light Bowgun": "Fuzilarco Leve", "Heavy Bowgun": "Fuzilarco Pesado",
    "Bowgun": "Fuzilarco", "Bow": "Arco", "Blade": "Lâmina", "Knife": "Faca",
    "Saber": "Sabre", "Katana": "Katana", "Dagger": "Adaga", "Club": "Clava",
    "Staff": "Cajado", "Spear": "Lança", "Cannon": "Canhão", "Rifle": "Rifle",
    "Alpha": "Alfa", "Beta": "Beta", "Gamma": "Gama", "Tree": "Árvore",
}

SLOT_TYPE_PT = {
    "helm": "Elmo",
    "chest": "Peitoral",
    "arms": "Braços",
    "waist": "Cintura",
    "legs": "Pernas",
}


def _translate_terms(name: str, mapping: dict[str, str]) -> str:
    if not name:
        return name
    translated = str(name)
    for src, dst in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        translated = translated.replace(src, dst)
    return translated


def _translate_armor_name(name: str) -> str:
    return _translate_terms(name, ARMOR_TERM_PT)


def _translate_weapon_name(name: str) -> str:
    return _translate_terms(name, WEAPON_TERM_PT)


def _translate_deco_name(name: str, skill: str | None = None) -> str:
    if skill and skill in SKILL_PT:
        level = ""
        if name and "[" in name:
            level = " " + name[name.rfind("["):]
        return f"Joia de {SKILL_PT[skill]}{level}"
    return _translate_terms(name, JEWEL_TERM_PT)


def _prepare_pt_display_data(data: dict, english: dict) -> dict:
    english_skills_by_id = {
        item.get("id"): item for item in english.get("skills", []) if isinstance(item, dict)
    }
    skill_names = {
        english_skills_by_id[item.get("id")].get("name"): item.get("name")
        for item in data.get("skills", [])
        if isinstance(item, dict)
        and item.get("id") in english_skills_by_id
        and item.get("name")
    }

    for skill in data.get("skills", []):
        english_skill = english_skills_by_id.get(skill.get("id"), {})
        english_ranks = {
            rank.get("id"): rank
            for rank in english_skill.get("ranks", [])
            if isinstance(rank, dict)
        }
        for rank in skill.get("ranks", []):
            if isinstance(rank, dict):
                rank["name_en"] = english_ranks.get(rank.get("id"), {}).get("name")

    for weapon in data.get("weapons", []):
        weapon["weapon_type_display"] = WEAPON_TYPE_PT.get(weapon.get("weapon_type"), weapon.get("weapon_type") or "")
    for armor in data.get("armors", []):
        armor["slot_type_display"] = SLOT_TYPE_PT.get(armor.get("slot_type"), armor.get("slot_type") or "")
        armor["skills_display"] = {skill_names.get(k, k): v for k, v in (armor.get("skills") or {}).items()}
    for deco in data.get("decorations", []):
        deco["skill_display"] = skill_names.get(deco.get("skill"), deco.get("skill") or "")
    for talisman in data.get("talismans", []):
        talisman["skills_display"] = {skill_names.get(k, k): v for k, v in (talisman.get("skills") or {}).items()}
    return data

def _merge_non_null(base, localized):
    if isinstance(base, dict) and isinstance(localized, dict):
        merged = dict(base)
        for key, value in localized.items():
            if value is None:
                continue
            if key == "skills" and isinstance(value, dict) and "null" in value:
                continue
            merged[key] = _merge_non_null(base.get(key), value)
        return merged
    if isinstance(base, list) and isinstance(localized, list):
        if all(isinstance(x, dict) and "id" in x for x in base):
            by_id = {x["id"]: x for x in base}
            return [_merge_non_null(by_id.get(item.get("id"), {}), item) for item in localized if isinstance(item, dict)]
        return localized or base
    return localized if localized is not None else base


def _english_payload():
    return {
        "weapons": [w.model_dump(mode="json") for w in sort_by_name(WEAPONS_DB)],
        "armors": [a.model_dump(mode="json") for a in sort_by_name(ARMORS_DB)],
        "decorations": [d.model_dump(mode="json") for d in sort_by_name(DECORATIONS_DB)],
        "talismans": [t.model_dump(mode="json") for t in sort_by_name(TALISMANS_DB)],
        "monsters": [m.model_dump(mode="json") for m in sort_by_name(MONSTERS_DB)],
        "rotations": [r.model_dump(mode="json") for r in ROTATIONS_DB.values()],
        "skills": EXTRA_GAME_DATA.get("skills", []),
        "items": EXTRA_GAME_DATA.get("items", []),
        "locations": EXTRA_GAME_DATA.get("locations", []),
        "armor_sets": EXTRA_GAME_DATA.get("armor_sets", []),
        "ailments": EXTRA_GAME_DATA.get("ailments", []),
        "motion_values": EXTRA_GAME_DATA.get("motion_values", []),
        "api_version": EXTRA_GAME_DATA.get("api_version", {}),
        "locale": "en"
    }


def _localized_data(locale: str):
    english = _english_payload()
    if locale not in {"en", "pt"}:
        locale = "en"
    localized_path = APP_DIR / f"game_data_{locale}.json"
    if locale != "en" and localized_path.exists():
        try:
            raw = json.loads(localized_path.read_text(encoding="utf-8"))
            raw["rotations"] = [r.model_dump(mode="json") for r in ROTATIONS_DB.values()]
            merged = _merge_non_null(english, raw)
            for key in (
                "weapons", "armors", "decorations", "talismans", "monsters",
                "skills", "items", "locations", "armor_sets", "ailments",
            ):
                english_by_id = {item.get("id"): item for item in english.get(key, []) if isinstance(item, dict)}
                for item in merged.get(key, []):
                    if isinstance(item, dict):
                        english_item = english_by_id.get(item.get("id"), {})
                        item["name_en"] = english_item.get("name", item.get("name"))
                        if key in {"weapons", "armors", "talismans"}:
                            item["skills"] = english_item.get("skills", item.get("skills", {}))
                        elif key == "decorations":
                            item["skill"] = english_item.get("skill", item.get("skill"))
            return _prepare_pt_display_data(merged, english)
        except Exception as exc:
            print(f"[AVISO] Não foi possível carregar dados locale={locale}: {exc}")
    return english


@lru_cache(maxsize=4)
def _serialized_catalog(locale: str, localized_mtime: int):
    from app.artian_rules import ELEMENT_ROLLS
    data = _localized_data(locale)
    data["artian_rules"] = {"element_rolls": ELEMENT_ROLLS}
    data["locale"] = locale if locale == "pt" and (APP_DIR / "game_data_pt.json").exists() else "en"
    content = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return content, '"' + hashlib.sha256(content).hexdigest() + '"'


@app.get("/api/data/all")
def get_all_game_data(request: Request, locale: str = Query(default="en", pattern="^(en|pt)$")):
    path = APP_DIR / f"game_data_{locale}.json"
    content, etag = _serialized_catalog(locale, path.stat().st_mtime_ns if path.exists() else 0)
    headers = {"ETag": etag, "Cache-Control": "private, max-age=0, must-revalidate"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content, media_type="application/json", headers=headers)


@app.get("/api/meta-presets", response_model=list[MetaBuildPreset])
def list_meta_presets():
    return META_BUILD_PRESETS


@app.get("/api/meta-builds/{preset_id}", response_model=SavedBuild)
def get_meta_build(preset_id: str, include_experimental: bool = False, verified_only: bool = False):
    build = META_BUILD_CACHE.get(preset_id)
    if not build:
        raise HTTPException(status_code=404, detail="Build pré-calculada não encontrada; execute o gerador de cache.")
    if (build.legality.status == "invalid" and not include_experimental) or (verified_only and not build.legality.recommendation_eligible):
        raise HTTPException(status_code=409, detail="Cache sem build elegível neste contexto. Equipamento original preservado para inspeção experimental.")
    return build


@app.get("/api/meta-builds/{preset_id}/candidates", response_model=list[SavedBuild])
def get_meta_build_candidates(preset_id: str, include_experimental: bool = False, verified_only: bool = False):
    candidates = META_BUILD_CANDIDATES.get(preset_id)
    if candidates:
        return [build for build in candidates
                if (include_experimental or build.legality.status != "invalid")
                and (not verified_only or build.legality.recommendation_eligible)]
    build = META_BUILD_CACHE.get(preset_id)
    if build:
        return [get_meta_build(preset_id, include_experimental, verified_only)]
    raise HTTPException(status_code=404, detail="Comparação pré-calculada não encontrada; execute o gerador de cache.")


@app.post("/api/rotations/compare", response_model=list[RotationComparison])
def compare_rotations(payload: RotationCompareRequest):
    try:
        weapon = resolve_weapon(payload.equipment)
        comparisons = []
        for rotation in rotations_for_weapon(weapon.weapon_type):
            scenario = payload.scenario.model_copy(deep=True)
            scenario.rotation_id = rotation.id
            comparisons.append(RotationComparison(
                rotation=rotation,
                result=calculate_build(payload.equipment, scenario),
            ))
        return sorted(comparisons, key=lambda row: row.result.practical_dps, reverse=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _armor_set_path(name: str) -> str:
    exact_set = ARMOR_SET_BY_NAME.get(name.casefold())
    if exact_set:
        return exact_set
    return re.sub(
        r"\s+(Helm|Helmet|Crown|Mask|Headgear|Hat|Hood|Mail|Plate|Chest|Vest|Shroud|Jacket|Suit|Vambraces|Armguards|Braces|Guards|Coil|Waist|Faulds|Overlay|Coat|Tasset|Greaves|Boots|Leggings|Pants)\b",
        "",
        name,
        flags=re.IGNORECASE,
    ).strip()


def _phantom_image_from_page(url: str, name: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as response:
        html = response.read().decode("utf-8", errors="ignore")
    pattern = r'<img[^>]+src="([^"]+)"[^>]+alt="[^"]*main image"'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    if not match:
        escaped_name = re.escape(name)
        pattern = rf'<img[^>]+src="([^"]+)"[^>]+alt="{escaped_name}[^"]*"'
        match = re.search(pattern, html, flags=re.IGNORECASE)
    if not match:
        return ""
    src = match.group(1)
    if src.startswith("/"):
        return f"https://www.phantombrawlers.com{src}"
    return src


def _proxied_url(image_url: str) -> str:
    if not image_url:
        return ""
    return f"/api/image-proxy?url={urllib.parse.quote(image_url, safe='')}"


def _wiki_page_image(title: str) -> str:
    api_url = (
        "https://monsterhunter.fandom.com/api.php?action=query&titles="
        f"{urllib.parse.quote(title)}&prop=pageimages&pithumbsize=280&format=json&origin=*"
    )
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8", errors="ignore"))
    page = next(iter(data.get("query", {}).get("pages", {}).values()), {})
    return page.get("thumbnail", {}).get("source", "")


def _phantom_skill_icon(skill_name: str) -> str:
    url = f"https://www.phantombrawlers.com/MHWilds/Skill/{urllib.parse.quote(skill_name)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as response:
        html = response.read().decode("utf-8", errors="ignore")
    pattern = r'<img[^>]+src="([^"]*?/static/MHWilds/Skills/[^"]+)"[^>]+alt="[^"]*icon"'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    if not match:
        return ""
    src = match.group(1)
    if src.startswith("/"):
        return f"https://www.phantombrawlers.com{src}"
    return src


def _skill_icon_index(skill_name: str) -> int | None:
    icon_index = SKILL_ICON_INDEX_BY_NAME.get(skill_name.casefold())
    if icon_index is not None:
        return icon_index
    english_name = next(
        (english for english, translated in SKILL_PT.items() if translated.casefold() == skill_name.casefold()),
        "",
    )
    return SKILL_ICON_INDEX_BY_NAME.get(english_name.casefold())


@app.get("/api/skill-icon/{icon_index}")
def get_local_skill_icon(icon_index: int):
    if not 0 <= icon_index <= 13:
        raise HTTPException(status_code=404, detail="Categoria de habilidade desconhecida.")
    icon_path = SKILL_ICON_DIR / f"SKILL_{icon_index:04d}.png"
    if not icon_path.exists():
        raise HTTPException(status_code=404, detail="Ícone local não encontrado.")
    return FileResponse(icon_path, media_type="image/png", headers={"Cache-Control": "public, max-age=604800"})


@app.get("/api/equipment-image/armor")
def get_armor_equipment_image(name: str = Query(..., min_length=2)):
    clean_name = name.strip()
    local = _catalog_asset("armor", clean_name)
    if local:
        return {"image_url": "/assets/catalog/" + local.name}
    if EQUIPMENT_IMAGE_CACHE.get(clean_name):
        return {"image_url": EQUIPMENT_IMAGE_CACHE[clean_name]}
    set_path = _armor_set_path(clean_name)
    candidates = [
        f"https://www.phantombrawlers.com/MHWilds/Armours/{urllib.parse.quote(set_path)}/{urllib.parse.quote(clean_name)}",
    ]
    if " α" in clean_name or " β" in clean_name:
        base_name = clean_name.replace(" α", "").replace(" β", "")
        base_set = _armor_set_path(base_name)
        candidates.append(
            f"https://www.phantombrawlers.com/MHWilds/Armours/{urllib.parse.quote(base_set)}/{urllib.parse.quote(base_name)}"
        )
    image_url = ""
    for url in candidates:
        try:
            image_url = _phantom_image_from_page(url, clean_name)
            if image_url:
                break
        except Exception:
            continue
    image_url = _proxied_url(image_url)
    if image_url:
        EQUIPMENT_IMAGE_CACHE[clean_name] = image_url
    return {"image_url": image_url}


@app.get("/api/equipment-image/weapon")
def get_weapon_equipment_image(name: str = Query(..., min_length=2)):
    clean_name = name.strip()
    local = _catalog_asset("weapon", clean_name)
    if local:
        return {"image_url": "/assets/catalog/" + local.name}
    cache_key = f"weapon:{clean_name}"
    if EQUIPMENT_IMAGE_CACHE.get(cache_key):
        return {"image_url": EQUIPMENT_IMAGE_CACHE[cache_key]}
    image_url = GOGMA_WEAPON_IMAGES.get(clean_name.casefold(), "")
    if not image_url:
        for title in (f"{clean_name} (MHWilds)", clean_name):
            try:
                image_url = _wiki_page_image(title)
                if image_url:
                    break
            except Exception:
                continue
    image_url = _proxied_url(image_url)
    if image_url:
        EQUIPMENT_IMAGE_CACHE[cache_key] = image_url
    return {"image_url": image_url}


@app.get("/api/equipment-image/skill")
def get_skill_equipment_image(name: str = Query(..., min_length=2)):
    clean_name = name.strip()
    cache_key = f"skill:{clean_name}"
    if EQUIPMENT_IMAGE_CACHE.get(cache_key):
        return {"image_url": EQUIPMENT_IMAGE_CACHE[cache_key]}
    icon_index = _skill_icon_index(clean_name)
    if icon_index is not None and (SKILL_ICON_DIR / f"SKILL_{icon_index:04d}.png").exists():
        image_url = f"/api/skill-icon/{icon_index}"
        EQUIPMENT_IMAGE_CACHE[cache_key] = image_url
        return {"image_url": image_url}
    image_url = ""
    for candidate in (clean_name, SKILL_PT.get(clean_name, clean_name)):
        try:
            image_url = _phantom_skill_icon(candidate)
            if image_url:
                break
        except Exception:
            continue
    image_url = _proxied_url(image_url)
    if image_url:
        EQUIPMENT_IMAGE_CACHE[cache_key] = image_url
    return {"image_url": image_url}


@app.get("/api/image-proxy")
def proxy_image(url: str = Query(..., min_length=10)):
    parsed = urllib.parse.urlparse(url)
    allowed_hosts = {
        "static.wikia.nocookie.net",
        "www.phantombrawlers.com",
        "static0.fextralifeimages.com",
    }
    if parsed.scheme != "https" or parsed.netloc not in allowed_hosts:
        raise HTTPException(status_code=400, detail="Origem de imagem não permitida.")
    if url in REMOTE_IMAGE_CACHE:
        content, content_type = REMOTE_IMAGE_CACHE.pop(url)
        REMOTE_IMAGE_CACHE[url] = (content, content_type)
        return Response(content=content, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})
    failed_at = REMOTE_IMAGE_FAILURES.get(url)
    if failed_at and (time.monotonic() - failed_at) < REMOTE_IMAGE_FAILURE_TTL:
        raise HTTPException(status_code=502, detail="Imagem remota temporariamente indisponível.")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            content_type = response.headers.get("content-type", "image/png")
            if not content_type.startswith("image/"):
                raise HTTPException(status_code=415, detail="URL não retornou imagem.")
            content = response.read()
    except HTTPException:
        raise
    except Exception as exc:
        REMOTE_IMAGE_FAILURES[url] = time.monotonic()
        raise HTTPException(status_code=502, detail=f"Não foi possível carregar imagem: {exc}")
    REMOTE_IMAGE_FAILURES.pop(url, None)
    REMOTE_IMAGE_CACHE[url] = (content, content_type)
    while len(REMOTE_IMAGE_CACHE) > REMOTE_IMAGE_CACHE_LIMIT:
        REMOTE_IMAGE_CACHE.popitem(last=False)
    return Response(content=content, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})


def _remote_from_proxied_url(proxied_url: str) -> str:
    if not proxied_url:
        return ""
    parsed = urllib.parse.urlparse(proxied_url)
    return urllib.parse.parse_qs(parsed.query).get("url", [""])[0]


def _local_weapon_icon(name: str) -> Path | None:
    clean_name = name.strip().casefold()
    weapon_type = GOGMA_WEAPON_TYPES.get(clean_name)
    if not weapon_type:
        weapon = next((item for item in WEAPONS_DB if item.name.casefold() == clean_name), None)
        weapon_type = weapon.weapon_type.value if weapon else ""
    filename = WEAPON_TYPE_ICON_FILES.get(weapon_type)
    icon_path = STATIC_ASSET_DIR / "equipment-icons" / filename if filename else None
    return icon_path if icon_path and icon_path.exists() else None


def _local_armor_icon(name: str) -> Path | None:
    clean_name = name.strip().casefold()
    armor = next((item for item in ARMORS_DB if item.name.casefold() == clean_name), None)
    filename = ARMOR_SLOT_ICON_FILES.get(armor.slot_type) if armor else None
    icon_path = STATIC_ASSET_DIR / "equipment-icons" / filename if filename else None
    return icon_path if icon_path and icon_path.exists() else None


@lru_cache(maxsize=4)
def _parse_catalog_manifest(raw_text: str) -> dict:
    parsed = json.loads(raw_text)
    return parsed if isinstance(parsed, dict) else {}


def _find_manifest_record(manifest: dict, kind: str, name: str):
    record = manifest.get(f"{kind}:{name}") or manifest.get(f"{kind}:{name.casefold()}")
    if isinstance(record, dict):
        return record
    if kind == "armor":
        stripped = re.sub(r"\s+[αβγ]$", "", name).strip()
        for candidate in (stripped, *(f"{stripped} {suffix}" for suffix in ("α", "β", "γ"))):
            rec = manifest.get(f"armor:{candidate}") or manifest.get(f"armor:{candidate.casefold()}")
            if isinstance(rec, dict):
                return rec
        armor = next((item for item in ARMORS_DB if item.name.casefold() == name.casefold()), None)
        if armor and armor.set_bonus_group:
            base_set = re.sub(r"\s+[αβγ]$", "", armor.set_bonus_group).strip().casefold()
            for sibling in ARMORS_DB:
                if sibling.slot_type != armor.slot_type or not sibling.set_bonus_group:
                    continue
                if re.sub(r"\s+[αβγ]$", "", sibling.set_bonus_group).strip().casefold() == base_set:
                    rec = manifest.get(f"armor:{sibling.name}") or manifest.get(f"armor:{sibling.name.casefold()}")
                    if isinstance(rec, dict):
                        return rec
    return None


def _catalog_asset(kind: str, name: str) -> Path | None:
    catalog = STATIC_ASSET_DIR / "catalog"
    try:
        manifest = _parse_catalog_manifest((catalog / "manifest.json").read_text(encoding="utf-8"))
        record = _find_manifest_record(manifest, kind, name)
        if not isinstance(record, dict):
            return None
        value = record.get("path", "")
        if not isinstance(value, str) or not value.startswith("/assets/catalog/"):
            return None
        path = (catalog / value.removeprefix("/assets/catalog/")).resolve()
        if path.parent != catalog.resolve() or path.suffix not in {".png", ".jpg", ".webp"}:
            return None
        return path if path.is_file() else None
    except (OSError, ValueError, TypeError):
        return None


def _local_equipment_response(icon_path: Path) -> FileResponse:
    return FileResponse(
        icon_path,
        media_type={".webp": "image/webp", ".jpg": "image/jpeg"}.get(icon_path.suffix, "image/png"),
        headers={"Cache-Control": "public, max-age=604800"},
    )


@app.get("/api/equipment-photo/weapon")
def get_weapon_equipment_photo(name: str = Query(..., min_length=2)):
    local = _catalog_asset("weapon", name.strip())
    if local:
        return _local_equipment_response(local)
    fallback = _local_weapon_icon(name)
    image_url = _remote_from_proxied_url(get_weapon_equipment_image(name)["image_url"])
    if not image_url:
        if fallback:
            return _local_equipment_response(fallback)
        raise HTTPException(status_code=404, detail="Foto da arma não encontrada.")
    try:
        return proxy_image(image_url)
    except HTTPException:
        if fallback:
            return _local_equipment_response(fallback)
        raise


@app.get("/api/equipment-photo/armor")
def get_armor_equipment_photo(name: str = Query(..., min_length=2)):
    local = _catalog_asset("armor", name.strip())
    if local:
        return _local_equipment_response(local)
    fallback = _local_armor_icon(name)
    image_url = _remote_from_proxied_url(get_armor_equipment_image(name)["image_url"])
    if not image_url:
        if fallback:
            return _local_equipment_response(fallback)
        raise HTTPException(status_code=404, detail="Foto da armadura não encontrada.")
    try:
        return proxy_image(image_url)
    except HTTPException:
        if fallback:
            return _local_equipment_response(fallback)
        raise


@app.get("/api/equipment-photo/monster")
def get_monster_equipment_photo(name: str = Query(..., min_length=2)):
    local = _catalog_asset("monster", name.strip())
    if local:
        return _local_equipment_response(local)
    raise HTTPException(status_code=404, detail="Foto do monstro não encontrada.")


@app.get("/api/equipment-photo/skill")
def get_skill_equipment_photo(name: str = Query(..., min_length=2)):
    clean_name = name.strip()
    icon_index = _skill_icon_index(clean_name)
    if icon_index is not None:
        icon_path = SKILL_ICON_DIR / f"SKILL_{icon_index:04d}.png"
        if icon_path.exists():
            return FileResponse(icon_path, media_type="image/png", headers={"Cache-Control": "public, max-age=604800"})
    image_url = _remote_from_proxied_url(get_skill_equipment_image(clean_name)["image_url"])
    if not image_url:
        raise HTTPException(status_code=404, detail="Ícone da habilidade não encontrado.")
    return proxy_image(image_url)


class CalculatePayload(BuildEquipment):
    scenario: ScenarioSettings = ScenarioSettings()


@app.post("/api/builds/validate")
def validate_build_endpoint(payload: dict):
    return validate_build(payload.get("equipment", payload), context=payload.get("context"),
                          expected_weapon_type=payload.get("weapon_type"),
                          required_skills=payload.get("required_skills"))


@app.post("/api/builds/validate-batch")
def validate_build_batch(payload: list[dict]):
    if len(payload) > 200:
        raise HTTPException(status_code=400, detail="Limite de 200 registros por validação.")
    return [validate_build(item.get("equipment", item)) for item in payload]


@app.post("/api/calculate", response_model=BuildResult)
def calculate_endpoint(payload: CalculatePayload):
    equipment = BuildEquipment(
        progression=payload.progression,
        weapon_id=payload.weapon_id,
        helm_id=payload.helm_id,
        chest_id=payload.chest_id,
        arms_id=payload.arms_id,
        waist_id=payload.waist_id,
        legs_id=payload.legs_id,
        talisman_id=payload.talisman_id,
        decorations=payload.decorations,
        transcended_armor=payload.transcended_armor,
        custom_weapon=payload.custom_weapon,
        custom_talisman=payload.custom_talisman
    )
    try:
        return calculate_build(equipment, payload.scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/optimizer", response_model=list[SavedBuild])
def optimizer_endpoint(settings: OptimizerSettings):
    try:
        return run_optimizer(settings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/builds/compare")
def compare_builds_endpoint(payload: BuildCompareRequest):
    return compare_builds(payload)


@app.post("/api/gog-recommendation", response_model=GogWeaponRecommendation)
def gog_recommendation_endpoint(payload: GogRecommendationRequest):
    try:
        return recommend_gog_weapon(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/builds", response_model=list[SavedBuild])
def list_saved_builds(owner_id: str = Depends(get_owner_id)):
    with STORAGE_LOCK:
        return [build.model_copy(update={"legality": validate_build(build.equipment)})
                for build in SAVED_BUILDS_STORAGE.values() if build.owner_id == owner_id]


@app.post("/api/builds/save", response_model=SavedBuild)
def save_build_endpoint(build: SavedBuild, owner_id: str = Depends(get_owner_id)):
    key = (owner_id, build.id)
    with STORAGE_LOCK:
        owner_count = sum(item.owner_id == owner_id for item in SAVED_BUILDS_STORAGE.values())
        if owner_count >= 30 and key not in SAVED_BUILDS_STORAGE:
            raise HTTPException(status_code=400, detail="Limite máximo de 30 builds atingido.")
        owned_build = build.model_copy(update={"owner_id": owner_id, "legality": validate_build(build.equipment)})
        SAVED_BUILDS_STORAGE[key] = owned_build
        save_builds_storage()
    return owned_build


@app.delete("/api/builds/{build_id}")
def delete_build_endpoint(build_id: str, owner_id: str = Depends(get_owner_id)):
    key = (owner_id, build_id)
    with STORAGE_LOCK:
        if key not in SAVED_BUILDS_STORAGE:
            raise HTTPException(status_code=404, detail="Build não encontrada.")
        del SAVED_BUILDS_STORAGE[key]
        save_builds_storage()
    return {"status": "success", "message": f"Build {build_id} removida."}



@app.get("/api/talismans/inventory", response_model=list[InventoryTalisman])
def list_talisman_inventory(owner_id: str = Depends(get_owner_id)):
    with STORAGE_LOCK:
        return [item for item in TALISMAN_INVENTORY_STORAGE.values() if item.owner_id == owner_id]


@app.post("/api/talismans/inventory", response_model=InventoryTalisman)
def save_talisman_inventory(item: InventoryTalisman, owner_id: str = Depends(get_owner_id)):
    owned_item = item.model_copy(update={"owner_id": owner_id})
    with STORAGE_LOCK:
        TALISMAN_INVENTORY_STORAGE[(owner_id, item.id)] = owned_item
        save_talismans_storage()
    return owned_item


@app.delete("/api/talismans/inventory/{talisman_id}")
def delete_talisman_inventory(talisman_id: str, owner_id: str = Depends(get_owner_id)):
    key = (owner_id, talisman_id)
    with STORAGE_LOCK:
        if key not in TALISMAN_INVENTORY_STORAGE:
            raise HTTPException(status_code=404, detail="Talismã do inventário não encontrado.")
        del TALISMAN_INVENTORY_STORAGE[key]
        save_talismans_storage()
    return {"status": "success", "message": f"Talismã {talisman_id} removido."}



@app.get("/api/damage", response_model=list[SavedDamage])
def list_saved_damage(owner_id: str = Depends(get_owner_id)):
    with STORAGE_LOCK:
        return [damage for damage in SAVED_DAMAGE_STORAGE.values() if damage.owner_id == owner_id]


@app.post("/api/damage/save", response_model=SavedDamage)
def save_damage_endpoint(damage: SavedDamage, owner_id: str = Depends(get_owner_id)):
    key = (owner_id, damage.id)
    with STORAGE_LOCK:
        owner_count = sum(item.owner_id == owner_id for item in SAVED_DAMAGE_STORAGE.values())
        if owner_count >= 60 and key not in SAVED_DAMAGE_STORAGE:
            raise HTTPException(status_code=400, detail="Limite máximo de 60 resultados salvos atingido.")
        owned_damage = damage.model_copy(update={"owner_id": owner_id})
        SAVED_DAMAGE_STORAGE[key] = owned_damage
        save_damage_storage()
    return owned_damage


@app.delete("/api/damage/{damage_id}")
def delete_damage_endpoint(damage_id: str, owner_id: str = Depends(get_owner_id)):
    key = (owner_id, damage_id)
    with STORAGE_LOCK:
        if key not in SAVED_DAMAGE_STORAGE:
            raise HTTPException(status_code=404, detail="Resultado não encontrado.")
        del SAVED_DAMAGE_STORAGE[key]
        save_damage_storage()
    return {"status": "success", "message": f"Resultado {damage_id} removido."}

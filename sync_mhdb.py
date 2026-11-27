"""
Sincronizador Oficial MHDB API (Monster Hunter Wilds)
Documentação: https://docs.wilds.mhdb.io/
"""

import argparse
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any

LOCALE = "en"
BASE_URL = f"https://wilds.mhdb.io/{LOCALE}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

WEAPON_KIND_MAP = {
    "great-sword": "Great Sword",
    "long-sword": "Long Sword",
    "sword-shield": "Sword & Shield",
    "dual-blades": "Dual Blades",
    "hammer": "Hammer",
    "hunting-horn": "Hunting Horn",
    "lance": "Lance",
    "gunlance": "Gunlance",
    "switch-axe": "Switch Axe",
    "charge-blade": "Charge Blade",
    "insect-glaive": "Insect Glaive",
    "light-bowgun": "Light Bowgun",
    "heavy-bowgun": "Heavy Bowgun",
    "bow": "Bow"
}

ARMOR_SLOT_MAP = {
    "head": "helm",
    "chest": "chest",
    "arms": "arms",
    "waist": "waist",
    "legs": "legs"
}

def fetch_json(endpoint: str) -> Any:
    if endpoint.startswith("../"):
        url = f"https://wilds.mhdb.io/{endpoint[3:].lstrip('/')}"
    else:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    print(f"[*] Buscando: {url}...")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[-] Erro HTTP {e.code} ao acessar {url}")
    except Exception as e:
        print(f"[-] Erro ao acessar {url}: {e}")
    return []

def determine_sharpness(sharp_obj: Dict[str, int]) -> str:
    if not sharp_obj:
        return "White"
    for color in ["purple", "white", "blue", "green", "yellow", "orange", "red"]:
        if sharp_obj.get(color, 0) > 0:
            return color.capitalize()
    return "White"

def process_weapons(raw_weapons: List[Dict]) -> List[Dict]:
    processed = []
    for w in raw_weapons:
        kind = w.get("kind", "")
        if kind not in WEAPON_KIND_MAP:
            continue

        weapon_type = WEAPON_KIND_MAP[kind]
        raw_damage = w.get("damage", {}).get("raw", 100)
        affinity = w.get("affinity", 0)
        
        # Elemento / Status
        ele_type = "None"
        ele_val = 0.0
        ele_display = 0.0
        specials = w.get("specials", [])
        if specials:
            spec = specials[0]
            if spec.get("kind") == "element":
                ele_type = spec.get("element", "None").capitalize()
                damage = spec.get("damage", {})
                ele_val = float(damage.get("raw", 0))
                ele_display = float(damage.get("display", ele_val * 10))
            elif spec.get("kind") == "status":
                status = spec.get("status", "None").casefold()
                ele_type = {
                    "blastblight": "Blast",
                    "paralysis": "Paralysis",
                    "poison": "Poison",
                    "sleep": "Sleep",
                }.get(status, status.capitalize())
                damage = spec.get("damage", {})
                ele_val = float(damage.get("raw", 0))
                ele_display = float(damage.get("display", ele_val * 10))

        # Afiamento e propriedades específicas são mantidos para o motor e a UI.
        sharpness_segments = {
            str(color).capitalize(): int(amount or 0)
            for color, amount in (w.get("sharpness") or {}).items()
            if int(amount or 0) > 0
        }
        sharpness = determine_sharpness(w.get("sharpness", {}))
        sharpness_hits = sum(sharpness_segments.values()) or 50
        crafting = w.get("crafting") or {}
        crafting_materials = crafting.get("upgradeMaterials") or crafting.get("craftingMaterials") or []
        melody = (w.get("melody") or {}).get("songs") or []
        
        # Habilidades embutidas
        skills = {}
        for s in w.get("skills", []):
            s_info = s.get("skill", {})
            if s_info and "name" in s_info:
                skills[s_info["name"]] = s.get("level", 1)

        processed.append({
            "id": f"wpn_{w.get('id', len(processed))}",
            "name": w.get("name", "Arma Desconhecida"),
            "weapon_type": weapon_type,
            "rarity": int(w.get("rarity", 1) or 1),
            "series": (w.get("series") or {}).get("name", ""),
            "raw": float(raw_damage),
            "affinity": float(affinity),
            "element_type": ele_type,
            "element_val": ele_val,
            "element_display": ele_display,
            "sharpness": sharpness,
            "sharpness_hits": sharpness_hits,
            "sharpness_segments": sharpness_segments,
            "slots": w.get("slots", []),
            "skills": skills,
            "coatings": w.get("coatings") or [],
            "ammo": w.get("ammo") or [],
            "special_ammo": w.get("specialAmmo"),
            "shell_type": w.get("shell"),
            "shell_level": int(w.get("shellLevel") or 0),
            "phial": (w.get("phial") or {}).get("kind") if isinstance(w.get("phial"), dict) else w.get("phial"),
            "kinsect_level": int(w.get("kinsectLevel") or 0),
            "melody": [song.get("name", "") for song in melody if song.get("name")],
            "weapon_features": {
                "echo_bubble": (w.get("echoBubble") or {}).get("name"),
                "echo_wave": (w.get("echoWave") or {}).get("name"),
                "handicraft": w.get("handicraft") or [],
            },
            "defense_bonus": int(w.get("defenseBonus") or 0),
            "craftable": bool(crafting.get("craftable", True)),
            "crafting_materials": crafting_materials,
            "crafting_cost": int(crafting.get("upgradeZennyCost") or crafting.get("craftingZennyCost") or 0),
            "is_custom": False
        })
    return processed

def process_armors(raw_armors: List[Dict]) -> List[Dict]:
    processed = [
        {"id": "helm_none", "name": "(Nenhum)", "slot_type": "helm", "defense": 0, "defense_max": 0, "skills": {}, "slots": []},
        {"id": "chest_none", "name": "(Nenhum)", "slot_type": "chest", "defense": 0, "defense_max": 0, "skills": {}, "slots": []},
        {"id": "arms_none", "name": "(Nenhum)", "slot_type": "arms", "defense": 0, "defense_max": 0, "skills": {}, "slots": []},
        {"id": "waist_none", "name": "(Nenhum)", "slot_type": "waist", "defense": 0, "defense_max": 0, "skills": {}, "slots": []},
        {"id": "legs_none", "name": "(Nenhum)", "slot_type": "legs", "defense": 0, "defense_max": 0, "skills": {}, "slots": []}
    ]
    for a in raw_armors:
        kind = a.get("kind", "")
        slot_type = ARMOR_SLOT_MAP.get(kind)
        if not slot_type:
            continue

        skills = {}
        for s in a.get("skills", []):
            s_info = s.get("skill", {})
            if s_info and "name" in s_info:
                skills[s_info["name"]] = s.get("level", 1)

        set_name = a.get("armorSet", {}).get("name") if a.get("armorSet") else None

        processed.append({
            "id": f"arm_{a.get('id', len(processed))}",
            "name": a.get("name", "Armadura"),
            "slot_type": slot_type,
            "rarity": int(a.get("rarity", 0) or 0),
            "defense": a.get("defense", {}).get("base", 60),
            "defense_max": a.get("defense", {}).get("max", a.get("defense", {}).get("base", 60)),
            "elemental_resistances": a.get("resistances") or {},
            "skills": skills,
            "slots": a.get("slots", []),
            "set_bonus_group": set_name,
            "crafting_materials": (a.get("crafting") or {}).get("materials") or [],
            "crafting_cost": int((a.get("crafting") or {}).get("zennyCost") or 0),
        })
    return processed

def process_decorations(raw_decos: List[Dict]) -> List[Dict]:
    processed = []
    for d in raw_decos:
        skills = d.get("skills", [])
        skill_levels = {
            item.get("skill", {}).get("name"): int(item.get("level", 1) or 1)
            for item in skills if item.get("skill", {}).get("name")
        }
        skill_name = next(iter(skill_levels), "Habilidade")
        points = skill_levels.get(skill_name, 1)

        processed.append({
            "id": f"deco_{d.get('id', len(processed))}",
            "name": d.get("name", "Jóia"),
            "level": int(d.get("slot", 1)),
            "kind": d.get("kind", "armor"),
            "skill": skill_name,
            "points": points,
            "skills": skill_levels,
        })
    return processed

def process_charms(raw_charms: List[Dict]) -> List[Dict]:
    processed = [{"id": "talisman_none", "name": "(Nenhum)", "skills": {}, "slots": [], "is_custom": False}]
    for c in raw_charms:
        for r in c.get("ranks", []):
            skills = {}
            for s in r.get("skills", []):
                s_info = s.get("skill", {})
                if s_info and "name" in s_info:
                    skills[s_info["name"]] = s.get("level", 1)

            processed.append({
                "id": f"charm_{r.get('id', len(processed))}",
                "name": r.get("name", "Amuleto"),
                "skills": skills,
                "slots": [],
                "is_custom": False
            })
    return processed

def process_monsters(raw_monsters: List[Dict]) -> List[Dict]:
    processed = []
    for m in raw_monsters:
        if m.get("kind") != "large":
            continue

        hitzones = []
        sum_sever, sum_blunt, sum_shot = 0.0, 0.0, 0.0
        sum_fire, sum_water, sum_thun, sum_ice, sum_drag = 0.0, 0.0, 0.0, 0.0, 0.0
        parts = m.get("parts", [])

        for p in parts:
            mults = p.get("multipliers", {})
            sever = round(mults.get("slash", 0.45) * 100, 1)
            blunt = round(mults.get("blunt", 0.45) * 100, 1)
            shot = round(mults.get("pierce", 0.40) * 100, 1)
            fire = round(mults.get("fire", 0.0) * 100, 1)
            water = round(mults.get("water", 0.0) * 100, 1)
            thunder = round(mults.get("thunder", 0.0) * 100, 1)
            ice = round(mults.get("ice", 0.0) * 100, 1)
            dragon = round(mults.get("dragon", 0.0) * 100, 1)

            sum_sever += sever
            sum_blunt += blunt
            sum_shot += shot
            sum_fire += fire
            sum_water += water
            sum_thun += thunder
            sum_ice += ice
            sum_drag += dragon

            hitzones.append({
                "part_name": p.get("name", p.get("part", "Parte")),
                "sever": sever, "blunt": blunt, "shot": shot,
                "fire": fire, "water": water, "thunder": thunder,
                "ice": ice, "dragon": dragon,
                "is_wound": "wound" in p.get("kind", "").lower()
            })

        count = max(1, len(parts))
        weighted_hz = {
            "part_name": "Media_Ponderada",
            "sever": round(sum_sever / count, 1),
            "blunt": round(sum_blunt / count, 1),
            "shot": round(sum_shot / count, 1),
            "fire": round(sum_fire / count, 1),
            "water": round(sum_water / count, 1),
            "thunder": round(sum_thun / count, 1),
            "ice": round(sum_ice / count, 1),
            "dragon": round(sum_drag / count, 1),
            "is_wound": False
        }

        status_weaknesses = {
            str(item.get("status", "")).casefold(): int(item.get("level") or 0)
            for item in (m.get("weaknesses") or [])
            if item.get("kind") == "status" and item.get("status")
        }
        processed.append({
            "id": f"mon_{m.get('id', len(processed))}",
            "name": m.get("name", "Monstro"),
            "description": m.get("description") or "Sem descrição disponível.",
            "weighted_hitzone": weighted_hz,
            "hitzones": hitzones,
            "status_weaknesses": status_weaknesses,
            "base_health": (m.get("baseHealth") or {}).get("base") if isinstance(m.get("baseHealth"), dict) else m.get("baseHealth"),
        })
    return processed

def sync_main(locale: str = "en"):
    global LOCALE, BASE_URL
    LOCALE = locale
    BASE_URL = f"https://wilds.mhdb.io/{LOCALE}"
    print(f"=== Sincronizando Dados com MHDB ({LOCALE}) ===\n")

    raw_version = fetch_json("../version")
    raw_data = {
        "version": raw_version,
        "ailments": fetch_json("ailments"),
        "armor": fetch_json("armor"),
        "armor_sets": fetch_json("armor/sets"),
        "charms": fetch_json("charms"),
        "decorations": fetch_json("decorations"),
        "items": fetch_json("items"),
        "locations": fetch_json("locations"),
        "monsters": fetch_json("monsters"),
        "motion_values": fetch_json("motion-values"),
        "skills": fetch_json("skills"),
        "weapons": fetch_json("weapons"),
    }

    processed_data = {
        "weapons": process_weapons(raw_data["weapons"]),
        "armors": process_armors(raw_data["armor"]),
        "decorations": process_decorations(raw_data["decorations"]),
        "talismans": process_charms(raw_data["charms"]),
        "monsters": process_monsters(raw_data["monsters"]),
        "skills": raw_data["skills"],
        "items": raw_data["items"],
        "locations": raw_data["locations"],
        "armor_sets": raw_data["armor_sets"],
        "ailments": raw_data["ailments"],
        "motion_values": raw_data["motion_values"],
        "api_version": raw_data["version"],
    }

    # A interface usa `pt`, enquanto a API identifica o português do Brasil
    # como `pt-BR`. Mantemos os nomes de arquivo antigos para compatibilidade.
    suffix = "" if LOCALE == "en" else "_pt" if LOCALE == "pt-BR" else f"_{LOCALE}"
    with open(f"app/game_data{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    with open(f"app/mhdb_raw_data{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    print("\n[+] Sincronização concluída com sucesso!")
    print(f"    - Armas: {len(processed_data['weapons'])}")
    print(f"    - Armaduras: {len(processed_data['armors'])}")
    print(f"    - Joias: {len(processed_data['decorations'])}")
    print(f"    - Talismãs: {len(processed_data['talismans'])}")
    print(f"    - Grandes Monstros: {len(processed_data['monsters'])}")
    print(f"    - Itens: {len(processed_data['items'])}")
    print(f"    - Habilidades: {len(processed_data['skills'])}")
    print(f"    - Locais: {len(processed_data['locations'])}")
    print(f"    - Arquivos gerados: app/game_data{suffix}.json e app/mhdb_raw_data{suffix}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=["en", "pt-BR"], default="en")
    args = parser.parse_args()
    sync_main(args.locale)

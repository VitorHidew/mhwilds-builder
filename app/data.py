import os
import json
from app.models import (
    ArmorPiece, Decoration, Hitzone, MonsterProfile, Talisman, Weapon
)
from app.rotations import ROTATIONS_DB

GAME_DATA_PATH = os.path.join(os.path.dirname(__file__), "game_data.json")

WEAPONS_DB: list[Weapon] = []
ARMORS_DB: list[ArmorPiece] = []
DECORATIONS_DB: list[Decoration] = []
TALISMANS_DB: list[Talisman] = []
MONSTERS_DB: list[MonsterProfile] = []
EXTRA_GAME_DATA: dict = {}

def load_data():
    global WEAPONS_DB, ARMORS_DB, DECORATIONS_DB, TALISMANS_DB, MONSTERS_DB, EXTRA_GAME_DATA

    if not os.path.exists(GAME_DATA_PATH):
        print(f"[AVISO] Arquivo {GAME_DATA_PATH} não encontrado. Execute: python sync_mhdb.py")
        return

    with open(GAME_DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    EXTRA_GAME_DATA = {
        key: raw_data.get(key, [])
        for key in [
            "skills", "items", "locations", "armor_sets",
            "ailments", "motion_values", "api_version"
        ]
    }

    # Carregar Armas
    for w in raw_data.get("weapons", []):
        try:
            WEAPONS_DB.append(Weapon(**w))
        except Exception:
            continue

    # Carregar Armaduras
    for a in raw_data.get("armors", []):
        try:
            ARMORS_DB.append(ArmorPiece(**a))
        except Exception:
            continue

    # Carregar Decorações
    for d in raw_data.get("decorations", []):
        try:
            DECORATIONS_DB.append(Decoration(**d))
        except Exception:
            continue

    # Carregar Talismãs
    for t in raw_data.get("talismans", []):
        try:
            TALISMANS_DB.append(Talisman(**t))
        except Exception:
            continue

    # Carregar Monstros
    for m in raw_data.get("monsters", []):
        try:
            MONSTERS_DB.append(MonsterProfile(**m))
        except Exception:
            continue

    print(f"[+] Dados Carregados: {len(WEAPONS_DB)} Armas | {len(ARMORS_DB)} Armaduras | {len(DECORATIONS_DB)} Jóias | {len(MONSTERS_DB)} Monstros")

load_data()

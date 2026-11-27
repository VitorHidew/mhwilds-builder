"""Conservative legality checks. No damage, score or optimizer dependency.

Unknown acquisition/roll tables never turn into a positive recommendation.
Availability declarations describe access to an item, not material quantities.
"""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError

from app.data import ARMORS_DB, DECORATIONS_DB, TALISMANS_DB, WEAPONS_DB
from app.equipment_rules import transcended_slots_for_armor
from app.models import BuildEquipment, BuildLegality, LegalityIssue, ProgressionContext

MHDB = "https://docs.wilds.mhdb.io/"
TU1 = "https://blog.playstation.com/?p=403133"
TU2 = "https://blog.playstation.com/2025/06/26/monster-hunter-wilds-second-free-title-update-brings-fierce-new-monsters-and-more-june-30/"
TU3 = "https://blog.playstation.com/2025/09/24/monster-hunter-wilds-free-title-update-3-out-sep-29-includes-final-fantasy-xiv-content/"
TU4 = "https://blog.playstation.com/?p=412869"
FEB = "https://blog.playstation.com/2026/02/09/monster-hunter-wilds-new-content-update-and-arch-tempered-arkveld-arrive-february-18/"
ARTIAN = "https://www.phantombrawlers.com/mhwilds/Artian"
CHARMS = "https://www.phantombrawlers.com/mhwilds/Talismans_RNG"
TRANSCEND = "https://game8.co/games/Monster-Hunter-Wilds/archives/571459"
SLOTS = ("helm", "chest", "arms", "waist", "legs")
WEAPONS = {item.id: item for item in WEAPONS_DB}
ARMORS = {item.id: item for item in ARMORS_DB}
TALISMANS = {item.id: item for item in TALISMANS_DB}
DECORATIONS = {item.id: item for item in DECORATIONS_DB}


@lru_cache(maxsize=1)
def metadata():
    try:
        raw = json.loads(Path(__file__).with_name("mhdb_raw_data.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, {}
    items = {f"arm_{item['id']}": item for item in raw.get("armor", [])}
    items.update({f"wpn_{item['id']}": item for item in raw.get("weapons", [])})
    items.update({f"charm_{rank['id']}": rank for item in raw.get("charms", []) for rank in item.get("ranks", [])})
    return items, {item["name"]: item for item in raw.get("skills", [])}


@lru_cache(maxsize=4096)
def recipe_names(item_id):
    items, _ = metadata()
    visited, names = set(), []
    while item_id and item_id not in visited:
        visited.add(item_id)
        item = items.get(item_id, {})
        names.append(item.get("name", ""))
        names.append(item.get("armorSet", {}).get("name", ""))
        recipe = item.get("crafting") or {}
        # When direct crafting is possible, upgrade ancestors are not required.
        keys = ("materials", "craftingMaterials") if recipe.get("craftable") else ("materials", "upgradeMaterials", "craftingMaterials")
        for key in keys:
            names.extend(material.get("item", {}).get("name", "") for material in recipe.get(key, []))
        previous = recipe.get("previous")
        item_id = f"wpn_{previous['id']}" if previous and not recipe.get("craftable") else None
    return " | ".join(names).casefold()


def preset_context(preset):
    """The category entry checkpoint, NOT a claim about the player's unlocks."""
    return ProgressionContext(hunter_rank=preset.hunter_rank_min,
                              unlocks={"high_rank": preset.profile != "progressao_inicio"})


def validate_build(equipment, *, context=None, expected_weapon_type=None,
                   required_skills=None, context_basis=None):
    report = BuildLegality()

    def issue(code, severity, field, pt, en, source=MHDB):
        report.issues.append(LegalityIssue(code=code, severity=severity, field=field,
                                          message=pt, message_en=en, source=source))

    def finish():
        levels = {item.severity for item in report.issues}
        report.status = "invalid" if "error" in levels else "unverified" if "unverified" in levels else "valid"
        report.recommendation_eligible = report.status == "valid"
        return report

    try:
        equip = equipment if isinstance(equipment, BuildEquipment) else BuildEquipment.model_validate(equipment)
        ctx = context if isinstance(context, ProgressionContext) else ProgressionContext.model_validate(context) if context is not None else equip.progression
    except ValidationError as exc:
        for error in exc.errors(include_url=False):
            field = ".".join(map(str, error["loc"]))
            issue("schema", "error", field, f"Configura\u00e7\u00e3o malformada: {field} ({error['type']}).", f"Malformed configuration: {field} ({error['type']}).")
        return finish()
    report.context_basis = context_basis or ("user_declared" if ctx.model_dump() != ProgressionContext().model_dump() else "unknown")
    raw, skill_meta = metadata()
    available = set(ctx.available_items)
    skills = Counter()
    pools = {"weapon": [], "armor": []}
    unknown_equipment = False

    def require(rank, unlocks, field, source):
        if rank:
            if ctx.hunter_rank is None:
                issue("rank_unknown", "unverified", field, f"RC n\u00e3o informado; requisito RC{rank}+.", f"HR unknown; requires HR{rank}+.", source)
            elif ctx.hunter_rank < rank:
                issue("rank_gate", "error", field, f"Requer RC{rank}+; contexto RC{ctx.hunter_rank}.", f"Requires HR{rank}+; context HR{ctx.hunter_rank}.", source)
        for key in unlocks:
            value = ctx.unlocks.get(key)
            if value is not True:
                issue("unlock_missing" if value is False else "unlock_unknown", "error" if value is False else "unverified", field,
                      f"Desbloqueio {'n\u00e3o conclu\u00eddo' if value is False else 'n\u00e3o verificado'}: {key}.",
                      f"Unlock {'not completed' if value is False else 'unverified'}: {key}.", source)

    def availability(item, field):
        if item.id.endswith("_none"):
            return
        record = raw.get(item.id, {})
        if record.get("rank") == "high":
            require(None, ("high_rank",), field, MHDB)
        names = recipe_names(item.id)
        gates = []
        if "gogma" in names:
            gates.append((100, ("a_first_cry", "gog_defeated"), TU4))
        if "zoh shia" in names:
            gates.append((50, ("zoh_shia_high_rank",), TU1))
        if "mizutsune" in names:
            gates.append((21, ("mizutsune_unlocked",), TU1))
        if "seregios" in names:
            gates.append((31, ("a_world_turned_upside_down", "seregios_unlocked"), TU2))
        if "lagiacrus" in names:
            gates.append((31, ("a_world_turned_upside_down", "forest_doshaguma", "lagiacrus_unlocked"), TU2))
        # Certificates propagate AT requirements into charms as well as armor.
        for name, rank, key, source in (
            ("rey", 50, "at_rey_dau_materials", TU1),
            ("uth", 50, "at_uth_duna_materials", TU2),
            ("udra", 100, "at_nu_udra_materials", TU3),
            ("jin", 100, "at_jin_dahaad_materials", TU4),
            ("arkveld", None, "at_arkveld_materials", FEB),
        ):
            if any(name in part and "\u03b3" in part for part in names.split(" | ")):
                gates.append((rank, (key,), source))
        for rank, unlocks, source in gates:
            require(rank, unlocks, field, source)
        if item.id not in available:
            issue("acquisition_unknown", "unverified", field,
                  f"Disponibilidade da receita, materiais ou evento n\u00e3o verificada: {item.name}.",
                  f"Recipe, material or event availability unverified: {item.name}.")

    def add_slots(sizes, kinds, field):
        for index, size in enumerate(sizes):
            kind = kinds[index] if index < len(kinds) else "armor"
            if kind not in pools or size not in (0, 1, 2, 3):
                issue("slot_definition", "error", field, "Tipo ou n\u00edvel de slot inv\u00e1lido (limite 3).", "Invalid slot kind or level (maximum 3).")
            elif size:
                pools[kind].append((size, field, index))

    def add_skills(values):
        skills.update(values)

    def custom_skills(custom, field, gog=False):
        seen, kinds = set(), []
        for index in range(1, 4):
            name, level = getattr(custom, f"skill_{index}"), getattr(custom, f"skill_{index}_lvl")
            if not name or not level:
                continue
            meta = skill_meta.get(name)
            if name in seen:
                issue("duplicate_custom_skill", "unverified", field, "Habilidade repetida no editor; combina\u00e7\u00e3o n\u00e3o verificada.", "Repeated editor skill; combination unverified.")
            seen.add(name)
            if not meta:
                issue("skill_unknown", "unverified", field, f"Habilidade n\u00e3o verificada: {name}.", f"Unverified skill: {name}.")
                continue
            kind = meta.get("kind")
            kinds.append(kind)
            if gog:
                if kind not in {"set", "group"} or level != 1:
                    issue("gog_skill_kind", "error", field, "Gog recebe uma habilidade de set e uma de grupo, um ponto de cada.", "Gog receives one set and one group skill, one point each.", TU4)
            elif kind in {"set", "group"}:
                issue("charm_set_skill", "error", field, "Habilidade de set/grupo n\u00e3o pertence aos rolls de talism\u00e3.", "Set/group skills are not charm rolls.", CHARMS)
            elif level > max((rank.get("level", 0) for rank in meta.get("ranks", [])), default=0):
                issue("skill_level", "error", field, f"N\u00edvel acima do limite de {name}.", f"Level exceeds the limit of {name}.")
        if gog and (len(kinds) > 2 or kinds.count("set") > 1 or kinds.count("group") > 1):
            issue("gog_skill_pair", "error", field, "Gog n\u00e3o admite dois sets, dois grupos ou tr\u00eas habilidades.", "Gog cannot have two sets, two groups or three skills.", TU4)

    weapon = WEAPONS.get(equip.weapon_id)
    if equip.weapon_id == "custom_gog_weapon":
        custom = equip.custom_weapon
        if not custom:
            issue("missing_custom_weapon", "error", "weapon_id", "Arma Gog personalizada ausente.", "Missing custom Gog weapon.")
        else:
            weapon = custom.to_weapon()
            require(100, ("a_first_cry", "gog_defeated"), "custom_weapon", TU4)
            if custom.slots != [3, 3, 3]:
                issue("gog_slots", "error", "custom_weapon.slots", "Gog R8 usa tr\u00eas slots de n\u00edvel 3.", "R8 Gog uses three level-three slots.", ARTIAN)
            base = WEAPONS.get(custom.base_weapon_id)
            if base is None:
                issue("gog_base_unknown", "unverified", "custom_weapon.base_weapon_id", "Arma Artiana de origem n\u00e3o verificada.", "Base Artian weapon unverified.", TU4)
            elif base.weapon_type != custom.weapon_type or base.rarity != 8:
                issue("gog_base", "error", "custom_weapon.base_weapon_id", "Base Gog precisa ser R8 e da mesma classe.", "Gog base must be R8 and of the same class.", TU4)
            else:
                issue("gog_origin_unknown", "unverified", "custom_weapon.base_weapon_id", "Origem das tr\u00eas pe\u00e7as Artianas n\u00e3o registrada.", "Origin of the three Artian parts is not recorded.", ARTIAN)
            custom_skills(custom, "custom_weapon", gog=True)
            issue("gog_rolls_unverified", "unverified", "custom_weapon", "Atributos base, pool/par de habilidades, tipo de frasco e sequ\u00eancia de refor\u00e7os n\u00e3o certificados por tabela completa.", "Base stats, skill pool/pair, phial type and reinforcement sequence are not certified against a complete table.", ARTIAN)
    elif equip.custom_weapon:
        issue("unused_custom_weapon", "warning", "custom_weapon", "Editor Gog ignorado: arma do cat\u00e1logo selecionada.", "Gog editor ignored: a catalog weapon is selected.")
    if weapon:
        if expected_weapon_type and weapon.weapon_type != expected_weapon_type:
            issue("weapon_class", "error", "weapon_id", "Classe da arma diferente da solicitada.", "Weapon class differs from the requested class.")
        add_slots(weapon.slots, ["weapon"] * len(weapon.slots), "weapon_id")
        add_skills(weapon.skills)
        if equip.weapon_id != "custom_gog_weapon":
            availability(weapon, "weapon_id")
    else:
        unknown_equipment = True
        issue("weapon_unknown", "unverified", "weapon_id", "Arma n\u00e3o encontrada no cat\u00e1logo local.", "Weapon absent from the local catalog.")

    for slot in SLOTS:
        field = f"{slot}_id"
        armor = ARMORS.get(getattr(equip, field))
        if not armor:
            unknown_equipment = True
            issue("armor_unknown", "unverified", field, "Armadura n\u00e3o encontrada no cat\u00e1logo local.", "Armor absent from the local catalog.")
            continue
        if armor.slot_type != slot:
            issue("armor_position", "error", field, "Pe\u00e7a de armadura na posi\u00e7\u00e3o errada.", "Armor in the wrong equipment position.")
        sizes = armor.slots
        if slot in equip.transcended_armor:
            if armor.rarity < 5 or raw.get(armor.id, {}).get("rank") == "low":
                issue("transcend_low_rank", "error", field, "Armadura de ranque baixo n\u00e3o pode transcender.", "Low-rank armor cannot transcend.", TRANSCEND)
            else:
                sizes = transcended_slots_for_armor(armor)
            require(100, ("transcendence_materials",), field, TU4)
        add_slots(sizes, ["armor"] * len(sizes), field)
        add_skills(armor.skills)
        availability(armor, field)

    talisman = TALISMANS.get(equip.talisman_id)
    if equip.talisman_id == "custom_talisman":
        if equip.custom_talisman:
            talisman = equip.custom_talisman.to_talisman()
            custom_skills(equip.custom_talisman, "custom_talisman")
            layout = sorted((kind, size) for kind, size in zip(talisman.slot_kinds, talisman.slots) if size)
            allowed = [[("armor", 1)], [("armor", 1), ("armor", 1)], [("armor", 2)],
                       [("armor", 1), ("armor", 2)], [("armor", 3)], [("weapon", 1)],
                       [("armor", 1), ("weapon", 1)], [("armor", 1), ("armor", 1), ("weapon", 1)]]
            if layout and layout not in allowed:
                issue("charm_slots", "error", "custom_talisman.slots", "Combina\u00e7\u00e3o de slots fora dos layouts de talism\u00e3 documentados.", "Slots do not match documented charm layouts.", CHARMS)
            issue("charm_rolls_unverified", "unverified", "custom_talisman", "Combina\u00e7\u00e3o e obten\u00e7\u00e3o dos rolls do talism\u00e3 n\u00e3o verificadas.", "Charm roll combination and acquisition unverified.", CHARMS)
        else:
            issue("missing_custom_charm", "error", "custom_talisman", "Talism\u00e3 personalizado ausente.", "Missing custom charm.")
    if talisman:
        add_slots(talisman.slots, talisman.slot_kinds, "talisman_id")
        add_skills(talisman.skills)
        if equip.talisman_id != "custom_talisman":
            availability(talisman, "talisman_id")
    else:
        unknown_equipment = True
        issue("charm_unknown", "unverified", "talisman_id", "Talism\u00e3 n\u00e3o verificado no cat\u00e1logo.", "Charm not verified in the catalog.")

    jewels = []
    for index, item_id in enumerate(equip.decorations):
        jewel = DECORATIONS.get(item_id)
        if not jewel:
            issue("decoration_unknown", "unverified", f"decorations.{index}", "Adorno n\u00e3o encontrado no cat\u00e1logo.", "Decoration absent from the catalog.")
        else:
            jewels.append((index, jewel))
    for index, jewel in sorted(jewels, key=lambda pair: pair[1].level, reverse=True):
        field = f"decorations.{index}"
        pool = pools[jewel.kind]
        fit = next((slot for slot in sorted(pool) if slot[0] >= jewel.level), None)
        if fit:
            pool.remove(fit)
            report.slot_assignments.append({"decoration_index": index, "decoration_id": jewel.id, "equipment_field": fit[1], "slot_index": fit[2], "slot_level": fit[0], "kind": jewel.kind})
            add_skills(jewel.skills or {jewel.skill: jewel.points})
        else:
            issue("decoration_capacity", "unverified" if unknown_equipment else "error", field,
                  f"Sem slot compat\u00edvel comprovado para {jewel.name} ({jewel.kind} {jewel.level}).",
                  f"No verified compatible slot for {jewel.name} ({jewel.kind} {jewel.level}).")
        availability(jewel, field)

    for name, count in skills.items():
        meta = skill_meta.get(name, {})
        if meta.get("kind") not in {"set", "group"}:
            continue
        thresholds = sorted({rank["setPiecesRequired"] for rank in meta.get("ranks", []) if rank.get("setPiecesRequired")})
        if not thresholds:
            issue("set_threshold_unknown", "unverified", "skills", f"Limiar n\u00e3o verificado: {name}.", f"Unverified threshold: {name}.")
            continue
        active = [value for value in thresholds if count >= value]
        report.set_activation[name] = {"points": count, "thresholds": thresholds, "active_threshold": max(active, default=0)}
        if not active:
            issue("set_inactive", "warning", "skills", f"{name}: {count}/{thresholds[0]}, b\u00f4nus inativo.", f"{name}: {count}/{thresholds[0]}, bonus inactive.")
    for name, requested in (required_skills or {}).items():
        meta = skill_meta.get(name)
        if not meta:
            issue("requirement_unknown", "unverified", "required_skills", f"Requisito n\u00e3o verificado: {name}.", f"Unverified requirement: {name}.")
        elif skills[name] < requested:
            issue("required_skill", "error", "required_skills", f"{name}: {skills[name]}/{requested} solicitado.", f"{name}: {skills[name]}/{requested} requested.")
        elif name in report.set_activation and not report.set_activation[name]["active_threshold"]:
            issue("required_set_inactive", "error", "required_skills", f"Set exigido inativo: {name}.", f"Required set inactive: {name}.")
    return finish()

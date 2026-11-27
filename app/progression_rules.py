"""Curated progression constraints transcribed from the community weapon guides."""

from dataclasses import dataclass

from app.models import WeaponType


@dataclass(frozen=True)
class ProgressionRule:
    weapon_series: tuple[str, ...]
    armor_requirements: tuple[tuple[str, int], ...]
    talisman_skills: tuple[tuple[str, int], ...] = ()
    note: str = ""


GUIDE_URLS: dict[WeaponType, str] = {
    WeaponType.GREAT_SWORD: "https://docs.google.com/document/d/1e7Z7SZbc1QFCGQOES_wnOL5K1k8_7oyAN776YSXLZL4/edit",
    WeaponType.LONG_SWORD: "https://docs.google.com/document/d/1IfcJdOknpuDxI_6GL7gqbePsgU0s0kPvDQD5vgb_56E/edit",
    WeaponType.SWORD_AND_SHIELD: "https://docs.google.com/document/d/1Bb0z44s8fO0iQS0ArxUft8qeswWapb2VBiBIInTfrII/edit",
    WeaponType.DUAL_BLADES: "https://docs.google.com/document/d/1ZZRF8XJASyNwRbHiCKMiXrIyIMS-yedOwL87pi1NK44/edit",
    WeaponType.HAMMER: "https://docs.google.com/document/d/19WNuDeDHTWFkhtaVlD32JgueJiugjNGW6LCT9Hi49Mg/edit",
    WeaponType.HUNTING_HORN: "https://docs.google.com/document/d/1GWb532e9Pd97Shsr9ULl6AqN3TBtAoqYWUSleLjSthw/edit",
    WeaponType.LANCE: "https://docs.google.com/document/d/1XkvxdFM2bCsFzffJQn-vR2Cwdc-iReYMSN8Qpq3eCZs/edit",
    WeaponType.GUNLANCE: "https://docs.google.com/document/d/1_DtbNNpVg_KJTJuY5WZkL2cE7HRJR4KSIe2Oe68fBus/edit",
    WeaponType.SWITCH_AXE: "https://docs.google.com/document/d/14iacEFiYckdrw-SgtLdQR3C_KhNWVGhcQOLUiB8x5Hs/edit",
    WeaponType.CHARGE_BLADE: "https://docs.google.com/document/d/1ybFbirrFtKdkEXejuFi_j4ZJGEBfMbmHF8hgs4NTH4A/edit",
    WeaponType.INSECT_GLAIVE: "https://docs.google.com/document/d/1IgkcmrRylLAeEiv1hHAlwCvJosNSQQOKKcGxi6a1yMw/edit",
    WeaponType.LIGHT_BOWGUN: "https://docs.google.com/document/d/1jRiN2Sl2tF3vjOkQQ2n2R3DLQcZCagHbqaTkaAKN7SQ/edit",
    WeaponType.HEAVY_BOWGUN: "https://docs.google.com/document/d/1fizikibjkJjpFjDMizNTn0TiQLtehUzhH2UgSTIfcGU/edit",
    WeaponType.BOW: "https://docs.google.com/document/d/1X_zLE-9IT08s7PKF9PeGaN5hz2YQ0Yt10OT_ett4BaY/edit",
}


def _r(series, armor, charm=(), note=""):
    return ProgressionRule(tuple(series), tuple(armor), tuple(charm), note)


# Profile order follows the five checkpoints shared by the guides:
# Low Rank, start of High Rank, HR21+, HR31+ and HR41+.
PROGRESSION_RULES: dict[tuple[WeaponType, str], ProgressionRule] = {
    (WeaponType.GREAT_SWORD, "progressao_inicio"): _r(("Nu Udra Tree", "Quematrice Tree"), (("Doshaguma", 4), ("Hope", 1))),
    (WeaponType.GREAT_SWORD, "progressao_lr_final"): _r(("Quematrice Tree", "Doshaguma Tree"), (("Doshaguma", 4), ("Conga", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.GREAT_SWORD, "progressao_hr_inicio"): _r(("Doshaguma Tree",), (("Guardian Fulgur", 2), ("Doshaguma", 2), ("Blango", 1)), (("Counterstrike", 2),)),
    (WeaponType.GREAT_SWORD, "progressao_hr_avancado"): _r(("Nu Udra Tree",), (("Guardian Fulgur", 2), ("Gore", 3)), (("Agitator", 1),)),
    (WeaponType.GREAT_SWORD, "progressao_hr_41"): _r(("Arkveld Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Weakness Exploit", 2),)),

    (WeaponType.LONG_SWORD, "progressao_inicio"): _r(("G. Rathalos Tree",), (("Guardian Rathalos", 2), ("Guardian Ebony", 1), ("Balahara", 1), ("Alloy", 1)), (("Quick Sheathe", 1),)),
    (WeaponType.LONG_SWORD, "progressao_lr_final"): _r(("Rathian Tree",), (("Guardian Arkveld", 2), ("Guardian Ebony", 1), ("Alloy", 2)), (("Quick Sheathe", 1),)),
    (WeaponType.LONG_SWORD, "progressao_hr_inicio"): _r(("Rathalos Tree",), (("Xu Wu", 1), ("Guardian Ebony", 1), ("Guardian Fulgur", 2), ("Alloy", 1)), (("Quick Sheathe", 2),)),
    (WeaponType.LONG_SWORD, "progressao_hr_avancado"): _r(("Lala Barina Tree",), (("Alloy", 1), ("Gore", 3), ("Guardian Ebony", 1)), (("Quick Sheathe", 2),)),
    (WeaponType.LONG_SWORD, "progressao_hr_41"): _r(("Gore Magala Tree",), (("Guardian Ebony", 1), ("Arkveld", 1), ("Guardian Arkveld", 1), ("Gore", 2)), (("Weakness Exploit", 2),)),

    (WeaponType.SWORD_AND_SHIELD, "progressao_inicio"): _r(("G. Rathalos Tree", "Balahara Tree"), (("Guardian Ebony", 2), ("Guardian Rathalos", 3))),
    (WeaponType.SWORD_AND_SHIELD, "progressao_lr_final"): _r(("Balahara Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.SWORD_AND_SHIELD, "progressao_hr_inicio"): _r(("Ajarakan Tree",), (("Guardian Rathalos", 2), ("Guardian Fulgur", 1), ("Blango", 1), ("Conga", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.SWORD_AND_SHIELD, "progressao_hr_avancado"): _r(("Lala Barina Tree",), (("Guardian Fulgur", 2), ("Rey Dau", 1), ("Gore", 2)), (("Burst", 1),)),
    (WeaponType.SWORD_AND_SHIELD, "progressao_hr_41"): _r(("Ajarakan Tree",), (("Gore", 4), ("Arkveld", 1)), (("Weakness Exploit", 2),)),

    (WeaponType.DUAL_BLADES, "progressao_inicio"): _r(("G. Rathalos Tree", "Doshaguma Tree"), (("Guardian Ebony", 4), ("Guardian Rathalos", 1))),
    (WeaponType.DUAL_BLADES, "progressao_lr_final"): _r(("Quematrice Tree", "Lala Barina Tree"), (("Guardian Ebony", 4), ("Conga", 1)), (("Burst", 1),)),
    (WeaponType.DUAL_BLADES, "progressao_hr_inicio"): _r(("Uth Duna Tree", "Yian Kut-Ku Tree", "Mizutsune Tree", "Doshaguma Tree", "Blangonga Tree"), (("Guardian Ebony", 4), ("Rathalos", 1)), (("Adrenaline Rush", 1),)),
    (WeaponType.DUAL_BLADES, "progressao_hr_avancado"): _r(("Uth Duna Tree", "Yian Kut-Ku Tree", "Mizutsune Tree", "Doshaguma Tree", "Blangonga Tree"), (("Guardian Ebony", 2), ("Gore", 3)), (("Burst", 1),)),
    (WeaponType.DUAL_BLADES, "progressao_hr_41"): _r(("Arkveld Tree", "Mizutsune Tree"), (("Guardian Ebony", 2), ("Rathalos", 1), ("Gore", 2)), (("Adrenaline Rush", 2),)),

    (WeaponType.HAMMER, "progressao_inicio"): _r(("Xu Wu Tree",), (("Guardian Ebony", 2), ("Guardian Rathalos", 3))),
    (WeaponType.HAMMER, "progressao_lr_final"): _r(("Rathalos Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.HAMMER, "progressao_hr_inicio"): _r(("Xu Wu Tree",), (("Guardian Fulgur", 3), ("Blango", 1), ("Conga", 1)), (("Maximum Might", 1),)),
    (WeaponType.HAMMER, "progressao_hr_avancado"): _r(("Xu Wu Tree",), (("Guardian Fulgur", 2), ("Blango", 1), ("Gore", 2)), (("Maximum Might", 1),)),
    (WeaponType.HAMMER, "progressao_hr_41"): _r(("Xu Wu Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Agitator", 2),)),

    (WeaponType.HUNTING_HORN, "progressao_inicio"): _r(("Ore Tree",), (("Rey Dau", 1), ("Nu Udra", 2), ("Guardian Rathalos", 2))),
    (WeaponType.HUNTING_HORN, "progressao_lr_final"): _r(("Ore Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.HUNTING_HORN, "progressao_hr_inicio"): _r(("Ore Tree",), (("Guardian Rathalos", 4), ("Conga", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.HUNTING_HORN, "progressao_hr_avancado"): _r(("Ore Tree",), (("Guardian Rathalos", 2), ("Guardian Ebony", 1), ("Gore", 2)), (("Weakness Exploit", 1),)),
    (WeaponType.HUNTING_HORN, "progressao_hr_41"): _r(("Ore Tree",), (("Arkveld", 1), ("Gore", 4)), (("Weakness Exploit", 2),)),

    (WeaponType.LANCE, "progressao_inicio"): _r(("Balahara Tree",), (("Guardian Rathalos", 3), ("Guardian Ebony", 2))),
    (WeaponType.LANCE, "progressao_lr_final"): _r(("Balahara Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.LANCE, "progressao_hr_inicio"): _r(("Rathalos Tree",), (("Guardian Fulgur", 3), ("Blango", 1), ("Conga", 1)), (("Maximum Might", 1),)),
    (WeaponType.LANCE, "progressao_hr_avancado"): _r(("Balahara Tree",), (("Guardian Fulgur", 2), ("Guardian Ebony", 1), ("Dahaad", 2)), (("Agitator", 1),)),
    (WeaponType.LANCE, "progressao_hr_41"): _r(("G. Rathalos Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Weakness Exploit", 2),)),

    (WeaponType.GUNLANCE, "progressao_inicio"): _r(("Quematrice Tree",), (("Guardian Ebony", 4), ("Nerscylla", 1))),
    (WeaponType.GUNLANCE, "progressao_lr_final"): _r(("Quematrice Tree",), (("Guardian Ebony", 4), ("Conga", 1)), (("Burst", 1),)),
    (WeaponType.GUNLANCE, "progressao_hr_inicio"): _r(("Quematrice Tree",), (("Guardian Ebony", 4), ("Conga", 1))),
    (WeaponType.GUNLANCE, "progressao_hr_avancado"): _r(("Quematrice Tree",), (("Guardian Ebony", 4), ("Dahaad", 1)), (("Agitator", 1),)),
    (WeaponType.GUNLANCE, "progressao_hr_41"): _r(("G. Arkveld Tree",), (("Guardian Ebony", 4), ("Blango", 1)), (("Agitator", 1),)),

    (WeaponType.SWITCH_AXE, "progressao_inicio"): _r(("Xu Wu Tree",), (("Guardian Rathalos", 3), ("Guardian Ebony", 2))),
    (WeaponType.SWITCH_AXE, "progressao_lr_final"): _r(("Rathalos Tree",), (("Guardian Arkveld", 2), ("Guardian Ebony", 1), ("Rathalos", 2)), (("Weakness Exploit", 1),)),
    (WeaponType.SWITCH_AXE, "progressao_hr_inicio"): _r(("Rathalos Tree",), (("Guardian Fulgur", 2), ("Blango", 1), ("Guardian Rathalos", 2)), (("Weakness Exploit", 1),)),
    (WeaponType.SWITCH_AXE, "progressao_hr_avancado"): _r(("Gore Magala Tree",), (("Guardian Fulgur", 2), ("Gore", 3)), (("Agitator", 1),)),
    (WeaponType.SWITCH_AXE, "progressao_hr_41"): _r(("Rathalos Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Agitator", 2),)),

    (WeaponType.CHARGE_BLADE, "progressao_inicio"): _r(("G. Rathalos Tree",), (("Guardian Rathalos", 3), ("Guardian Ebony", 2))),
    (WeaponType.CHARGE_BLADE, "progressao_lr_final"): _r(("Rathian Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.CHARGE_BLADE, "progressao_hr_inicio"): _r(("G. Rathalos Tree",), (("Guardian Rathalos", 4), ("Conga", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.CHARGE_BLADE, "progressao_hr_avancado"): _r(("Rathian Tree", "Gore Magala Tree"), (("Guardian Ebony", 1), ("Gore", 4)), (("Weakness Exploit", 1),)),
    (WeaponType.CHARGE_BLADE, "progressao_hr_41"): _r(("G. Rathalos Tree",), (("Arkveld", 1), ("Gore", 4)), (("Weakness Exploit", 2),)),

    (WeaponType.INSECT_GLAIVE, "progressao_inicio"): _r(("G. Rathalos Tree",), (("Guardian Ebony", 4), ("Guardian Rathalos", 1))),
    (WeaponType.INSECT_GLAIVE, "progressao_lr_final"): _r(("Rathalos Tree",), (("Guardian Ebony", 4), ("Conga", 1)), (("Burst", 1),)),
    (WeaponType.INSECT_GLAIVE, "progressao_hr_inicio"): _r(("Rathalos Tree",), (("Guardian Ebony", 4), ("Blango", 1)), (("Agitator", 1),)),
    (WeaponType.INSECT_GLAIVE, "progressao_hr_avancado"): _r(("Rey Dau Tree",), (("Guardian Ebony", 2), ("Gore", 3)), (("Burst", 1),)),
    (WeaponType.INSECT_GLAIVE, "progressao_hr_41"): _r(("Rathalos Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Weakness Exploit", 2),)),

    (WeaponType.LIGHT_BOWGUN, "progressao_inicio"): _r(("Rey Dau Tree",), (("Guardian Ebony", 2), ("Guardian Rathalos", 3))),
    (WeaponType.LIGHT_BOWGUN, "progressao_lr_final"): _r(("Rey Dau Tree",), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.LIGHT_BOWGUN, "progressao_hr_inicio"): _r(("Rey Dau Tree",), (("Guardian Fulgur", 3), ("Blango", 1), ("Conga", 1)), (("Maximum Might", 1),)),
    (WeaponType.LIGHT_BOWGUN, "progressao_hr_avancado"): _r(("Rey Dau Tree",), (("Guardian Fulgur", 2), ("Blango", 1), ("Gore", 2)), (("Maximum Might", 1),)),
    (WeaponType.LIGHT_BOWGUN, "progressao_hr_41"): _r(("Rey Dau Tree",), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Agitator", 2),)),

    (WeaponType.HEAVY_BOWGUN, "progressao_inicio"): _r(("Congalala Tree", "Bone Tree"), (("Guardian Ebony", 2), ("Guardian Rathalos", 3))),
    (WeaponType.HEAVY_BOWGUN, "progressao_lr_final"): _r(("Congalala Tree", "Bone Tree"), (("Bulaqchi", 1), ("Chatacabra", 2), ("Guardian Rathalos", 1), ("Guardian Ebony", 1)), (("Weakness Exploit", 1),)),
    (WeaponType.HEAVY_BOWGUN, "progressao_hr_inicio"): _r(("Congalala Tree", "Bone Tree"), (("Guardian Fulgur", 3), ("Blango", 1), ("Conga", 1)), (("Maximum Might", 1),)),
    (WeaponType.HEAVY_BOWGUN, "progressao_hr_avancado"): _r(("Congalala Tree", "Bone Tree"), (("Guardian Fulgur", 2), ("Blango", 1), ("Gore", 2)), (("Maximum Might", 1),)),
    (WeaponType.HEAVY_BOWGUN, "progressao_hr_41"): _r(("Congalala Tree", "Bone Tree"), (("Guardian Fulgur", 2), ("Arkveld", 1), ("Gore", 2)), (("Agitator", 2),)),

    (WeaponType.BOW, "progressao_inicio"): _r(("Bone Tree",), (("Rey Dau", 3), ("Guardian Rathalos", 2)), (("Constitution", 1),)),
    (WeaponType.BOW, "progressao_lr_final"): _r(("Bone Tree",), (("Gypceros", 3), ("Rathalos", 1), ("Conga", 1)), (("Constitution", 1),)),
    (WeaponType.BOW, "progressao_hr_inicio"): _r(("G. Arkveld Tree",), (("Kut-Ku", 1), ("Guardian Rathalos", 3), ("Guardian Fulgur", 1)), (("Constitution", 1),)),
    (WeaponType.BOW, "progressao_hr_avancado"): _r(("Quematrice Tree",), (("Kut-Ku", 1), ("Gore", 4)), (("Burst", 1),)),
    (WeaponType.BOW, "progressao_hr_41"): _r(("Seregios Tree",), (("Gore", 4), ("Arkveld", 1)), (("Weakness Exploit", 2),)),
}


def progression_rule_for(weapon_type: WeaponType, profile: str) -> ProgressionRule | None:
    return PROGRESSION_RULES.get((weapon_type, profile))


def guide_url_for(weapon_type: WeaponType) -> str:
    return GUIDE_URLS[weapon_type]

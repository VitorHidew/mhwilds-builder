from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


ELEMENT_DISPLAY_MULTIPLIER = 10.0

GOG_REINFORCEMENT_VALUES = {
    "attack_i": (5.0, 0.0, 0.0, 0),
    "attack_ii": (6.0, 0.0, 0.0, 0),
    "attack_iii": (9.0, 0.0, 0.0, 0),
    "attack_ex": (12.0, 0.0, 0.0, 0),
    "affinity_i": (0.0, 5.0, 0.0, 0),
    "affinity_ii": (0.0, 6.0, 0.0, 0),
    "affinity_iii": (0.0, 8.0, 0.0, 0),
    "affinity_ex": (0.0, 10.0, 0.0, 0),
    # Element values here match the in-game display; the damage engine uses true element.
    "element_i": (0.0, 0.0, 50.0, 0),
    "element_ii": (0.0, 0.0, 60.0, 0),
    "element_ex": (0.0, 0.0, 90.0, 0),
    "sharpness_i": (0.0, 0.0, 0.0, 30),
    "sharpness_ex": (0.0, 0.0, 0.0, 50),
    "capacity_i": (0.0, 0.0, 0.0, 0),
    "capacity_ex": (0.0, 0.0, 0.0, 0),
}


class WeaponType(str, Enum):
    GREAT_SWORD = "Great Sword"
    LONG_SWORD = "Long Sword"
    SWORD_AND_SHIELD = "Sword & Shield"
    DUAL_BLADES = "Dual Blades"
    HAMMER = "Hammer"
    HUNTING_HORN = "Hunting Horn"
    LANCE = "Lance"
    GUNLANCE = "Gunlance"
    SWITCH_AXE = "Switch Axe"
    CHARGE_BLADE = "Charge Blade"
    INSECT_GLAIVE = "Insect Glaive"
    LIGHT_BOWGUN = "Light Bowgun"
    HEAVY_BOWGUN = "Heavy Bowgun"
    BOW = "Bow"


class ElementType(str, Enum):
    NONE = "None"
    FIRE = "Fire"
    WATER = "Water"
    THUNDER = "Thunder"
    ICE = "Ice"
    DRAGON = "Dragon"
    POISON = "Poison"
    PARALYSIS = "Paralysis"
    SLEEP = "Sleep"
    BLAST = "Blast"


class SharpnessLevel(str, Enum):
    RED = "Red"
    ORANGE = "Orange"
    YELLOW = "Yellow"
    GREEN = "Green"
    BLUE = "Blue"
    WHITE = "White"
    PURPLE = "Purple"


class Weapon(BaseModel):
    id: str
    name: str
    weapon_type: WeaponType
    rarity: int = Field(default=8, ge=1, le=8)
    series: str = ""
    raw: float = Field(ge=0)
    affinity: float = Field(ge=-100, le=100)
    element_type: ElementType = ElementType.NONE
    element_val: float = Field(default=0.0, ge=0)
    element_display: float = Field(default=0.0, ge=0)
    sharpness: SharpnessLevel = SharpnessLevel.WHITE
    sharpness_hits: int = Field(default=50, ge=1)
    prev_sharpness: SharpnessLevel = SharpnessLevel.BLUE
    sharpness_segments: Dict[str, int] = Field(default_factory=dict)
    slots: List[int] = Field(default_factory=list)
    skills: Dict[str, int] = Field(default_factory=dict)
    coatings: List[str] = Field(default_factory=list)
    ammo: List[Dict[str, Any]] = Field(default_factory=list)
    special_ammo: Optional[str] = None
    shell_type: Optional[str] = None
    shell_level: int = 0
    phial: Optional[str] = None
    kinsect_level: int = 0
    melody: List[str] = Field(default_factory=list)
    weapon_features: Dict[str, Any] = Field(default_factory=dict)
    defense_bonus: int = 0
    craftable: bool = True
    crafting_materials: List[Dict[str, Any]] = Field(default_factory=list)
    crafting_cost: int = 0
    is_custom: bool = False

    @model_validator(mode="after")
    def fill_element_display(self):
        if self.element_val > 0 and self.element_display <= 0:
            self.element_display = self.element_val * ELEMENT_DISPLAY_MULTIPLIER
        return self


class CustomGogWeapon(BaseModel):
    name: str = "Arma Gog Personalizada"
    weapon_type: WeaponType = WeaponType.GREAT_SWORD
    raw: float = Field(default=220.0, ge=50, le=500)
    affinity: float = Field(default=0.0, ge=-100, le=100)
    element_nature: str = "element"  # none, element, status
    element_type: ElementType = ElementType.FIRE
    element_val: float = Field(default=20.0, ge=0, le=200)
    element_display: Optional[float] = Field(default=None, ge=0, le=2000)
    gog_focus: str = "none"  # none, attack, affinity, element
    reinforcements: List[str] = Field(default_factory=list)
    base_weapon_id: Optional[str] = None
    shell_type: Optional[str] = None
    shell_level: int = Field(default=3, ge=0, le=4)
    phial: Optional[str] = None
    ammo: List[Dict[str, Any]] = Field(default_factory=list)
    coatings: List[str] = Field(default_factory=list)
    melody: List[str] = Field(default_factory=list)
    slots: List[int] = Field(default=[3, 2, 1])
    best_sharpness: SharpnessLevel = SharpnessLevel.WHITE
    sharpness_units: int = Field(default=40, ge=10, le=120)
    prev_sharpness: SharpnessLevel = SharpnessLevel.BLUE
    skill_1: Optional[str] = Field(default=None, max_length=100)
    skill_1_lvl: int = Field(default=0, ge=0, le=5)
    skill_2: Optional[str] = Field(default=None, max_length=100)
    skill_2_lvl: int = Field(default=0, ge=0, le=5)
    skill_3: Optional[str] = Field(default=None, max_length=100)
    skill_3_lvl: int = Field(default=0, ge=0, le=5)

    @field_validator("slots")
    @classmethod
    def validate_slots(cls, v):
        if len(v) > 3:
            raise ValueError("Uma arma pode ter no máximo 3 slots.")
        for s in v:
            if s < 0 or s > 4:
                raise ValueError("Os slots devem ter nível entre 0 e 4.")
        return v

    @field_validator("gog_focus")
    @classmethod
    def validate_gog_focus(cls, v):
        if v not in {"none", "attack", "affinity", "element"}:
            raise ValueError("O foco Gog deve ser none, attack, affinity ou element.")
        return v

    @field_validator("reinforcements")
    @classmethod
    def validate_reinforcements(cls, v):
        if len(v) > 5:
            raise ValueError("Uma arma Gog pode ter no máximo 5 reforços.")
        invalid = [item for item in v if item not in GOG_REINFORCEMENT_VALUES]
        if invalid:
            raise ValueError(f"Reforços Gog inválidos: {', '.join(invalid)}")
        if any(v.count(roll) > 2 for roll in set(v)):
            raise ValueError("No máximo dois reforços Gog do mesmo tipo e nível.")
        return v

    def reinforcement_totals(self) -> tuple[float, float, float, int]:
        from app.artian_rules import element_roll
        raw = affinity = element_display = 0.0
        sharpness = 0
        for reinforcement in self.reinforcements:
            raw_bonus, affinity_bonus, element_bonus, sharpness_bonus = GOG_REINFORCEMENT_VALUES[reinforcement]
            if reinforcement.startswith("element_"):
                element_bonus = element_roll(self.weapon_type.value, reinforcement)
            if self.weapon_type == WeaponType.INSECT_GLAIVE and reinforcement == "sharpness_i":
                sharpness_bonus = 20
            raw += raw_bonus
            affinity += affinity_bonus
            element_display += element_bonus
            sharpness += sharpness_bonus
        return raw, affinity, element_display, sharpness

    def to_weapon(self) -> Weapon:
        from app.artian_rules import focus_element
        skills = {}
        if self.skill_1 and self.skill_1_lvl > 0:
            skills[self.skill_1] = self.skill_1_lvl
        if self.skill_2 and self.skill_2_lvl > 0:
            skills[self.skill_2] = self.skill_2_lvl
        if self.skill_3 and self.skill_3_lvl > 0:
            skills[self.skill_3] = self.skill_3_lvl

        ele_type = self.element_type if self.element_nature in ("element", "status") else ElementType.NONE
        base_display = self.element_display if self.element_display is not None else self.element_val * ELEMENT_DISPLAY_MULTIPLIER
        raw_bonus, affinity_bonus, element_bonus_display, sharpness_bonus = self.reinforcement_totals()
        focus_raw, focus_affinity, focus_element_display = {
            "none": (0.0, 0.0, 0.0),
            "attack": (10.0, -15.0, 0.0),
            "affinity": (-10.0, 10.0, -20.0),
            "element": (0.0, -5.0, 50.0),
        }[self.gog_focus]
        focus_element_display = focus_element(
            self.weapon_type.value, self.gog_focus,
            status=ele_type in {ElementType.POISON, ElementType.PARALYSIS, ElementType.SLEEP, ElementType.BLAST},
        )
        ele_display = max(0.0, base_display + focus_element_display + element_bonus_display) if ele_type != ElementType.NONE else 0.0
        ele_val = ele_display / ELEMENT_DISPLAY_MULTIPLIER

        return Weapon(
            id="custom_gog_weapon",
            name=f"ARMA GOG :: {self.name}",
            weapon_type=self.weapon_type,
            raw=self.raw + focus_raw + raw_bonus,
            affinity=max(-100.0, min(100.0, self.affinity + focus_affinity + affinity_bonus)),
            element_type=ele_type,
            element_val=ele_val,
            element_display=ele_display,
            sharpness=self.best_sharpness,
            sharpness_hits=max(1, self.sharpness_units + sharpness_bonus - (10 if self.gog_focus == "affinity" else 0)),
            prev_sharpness=self.prev_sharpness,
            slots=[s for s in self.slots if s > 0],
            skills=skills,
            shell_type=self.shell_type,
            shell_level=self.shell_level if self.weapon_type == WeaponType.GUNLANCE else 0,
            phial=self.phial,
            ammo=self.ammo,
            coatings=self.coatings,
            melody=self.melody,
            is_custom=True
        )


class ArmorPiece(BaseModel):
    id: str
    name: str
    slot_type: str  # helm, chest, arms, waist, legs
    rarity: int = Field(default=0, ge=0, le=8)
    defense: int = 60
    defense_max: int = 60
    elemental_resistances: Dict[str, int] = Field(default_factory=dict)
    skills: Dict[str, int] = Field(default_factory=dict)
    slots: List[int] = Field(default_factory=list)
    set_bonus_group: Optional[str] = None
    crafting_materials: List[Dict[str, Any]] = Field(default_factory=list)
    crafting_cost: int = 0


class Decoration(BaseModel):
    id: str
    name: str
    level: int = Field(ge=1, le=4)
    kind: Literal["weapon", "armor"] = "armor"
    skill: str
    points: int = 1
    skills: Dict[str, int] = Field(default_factory=dict)


class Talisman(BaseModel):
    id: str
    name: str
    skills: Dict[str, int] = Field(default_factory=dict)
    slots: List[int] = Field(default_factory=list)
    slot_kinds: List[Literal["weapon", "armor"]] = Field(default_factory=list)
    is_custom: bool = False

    @model_validator(mode="after")
    def normalize_slot_kinds(self):
        kinds = list(self.slot_kinds[:len(self.slots)])
        kinds.extend(["armor"] * (len(self.slots) - len(kinds)))
        self.slot_kinds = kinds
        return self


class CustomTalisman(BaseModel):
    name: str = "Talismã Personalizado"
    skill_1: Optional[str] = Field(default=None, max_length=100)
    skill_1_lvl: int = Field(default=0, ge=0, le=5)
    skill_2: Optional[str] = Field(default=None, max_length=100)
    skill_2_lvl: int = Field(default=0, ge=0, le=5)
    skill_3: Optional[str] = Field(default=None, max_length=100)
    skill_3_lvl: int = Field(default=0, ge=0, le=5)
    slots: List[int] = Field(default=[0, 0, 0])
    slot_kinds: List[Literal["weapon", "armor"]] = Field(
        default=["armor", "armor", "armor"]
    )

    @field_validator("slots")
    @classmethod
    def validate_slots(cls, v):
        if len(v) > 3:
            raise ValueError("Um talismã pode ter no máximo 3 slots.")
        for s in v:
            if s < 0 or s > 4:
                raise ValueError("Os slots devem ter nível entre 0 e 4.")
        return v

    @model_validator(mode="after")
    def normalize_slot_kinds(self):
        kinds = list(self.slot_kinds[:len(self.slots)])
        kinds.extend(["armor"] * (len(self.slots) - len(kinds)))
        self.slot_kinds = kinds
        return self

    def to_talisman(self) -> Talisman:
        skills = {}
        if self.skill_1 and self.skill_1_lvl > 0:
            skills[self.skill_1] = self.skill_1_lvl
        if self.skill_2 and self.skill_2_lvl > 0:
            skills[self.skill_2] = self.skill_2_lvl
        if self.skill_3 and self.skill_3_lvl > 0:
            skills[self.skill_3] = self.skill_3_lvl
        active_slots = [
            (slot, self.slot_kinds[index])
            for index, slot in enumerate(self.slots) if slot > 0
        ]
        return Talisman(
            id="custom_talisman",
            name=f"TALISMÃ :: {self.name}",
            skills=skills,
            slots=[slot for slot, _ in active_slots],
            slot_kinds=[kind for _, kind in active_slots],
            is_custom=True
        )


class Hitzone(BaseModel):
    part_name: str
    sever: float
    blunt: float
    shot: float
    fire: float
    water: float
    thunder: float
    ice: float
    dragon: float
    is_wound: bool = False


class MonsterProfile(BaseModel):
    id: str
    name: str
    description: str
    weighted_hitzone: Hitzone
    hitzones: List[Hitzone] = Field(default_factory=list)
    status_weaknesses: Dict[str, int] = Field(default_factory=dict)
    base_health: Optional[float] = None


class HitDetail(BaseModel):
    hit_name: str
    motion_value: float
    element_mult: float = 1.0
    sharpness_consumed: int = 1
    hit_count: int = Field(default=1, ge=1, le=60)
    damage_kind: Literal["weapon", "sever", "blunt", "shot", "shell", "impact_phial", "element_phial"] = "weapon"
    can_crit: bool = True
    uses_sharpness: bool = True
    charged: bool = False
    fixed_fire: float = Field(default=0, ge=0)
    ammo_kind: Optional[Literal["normal", "pierce", "spread"]] = None
    rapid_fire: bool = False
    special_ammo: bool = False
    airborne: bool = False


class Rotation(BaseModel):
    id: str
    name: str
    weapon_type: WeaponType
    cycle_time_seconds: float = 5.0
    hits: List[HitDetail] = Field(default_factory=list)
    category: str = "sustained"
    source_url: Optional[str] = None
    timing_is_estimate: bool = True


class ProgressionContext(BaseModel):
    hunter_rank: Optional[int] = Field(default=None, ge=1, le=999)
    # Missing keys mean unknown, not false. Item availability is user-declared.
    unlocks: Dict[str, bool] = Field(default_factory=dict)
    available_items: List[str] = Field(default_factory=list, max_length=3000)


class LegalityIssue(BaseModel):
    code: str
    severity: Literal["error", "unverified", "warning"]
    field: str
    message: str
    message_en: str
    source: str = ""


class BuildLegality(BaseModel):
    version: str = "2026.09.26.1"
    status: Literal["valid", "invalid", "unverified"] = "unverified"
    recommendation_eligible: bool = False
    context_basis: str = "unknown"
    issues: List[LegalityIssue] = Field(default_factory=list)
    slot_assignments: List[Dict[str, Any]] = Field(default_factory=list)
    set_activation: Dict[str, Any] = Field(default_factory=dict)


class BuildEquipment(BaseModel):
    progression: ProgressionContext = Field(default_factory=ProgressionContext)
    weapon_id: str
    helm_id: str
    chest_id: str
    arms_id: str
    waist_id: str
    legs_id: str
    talisman_id: str
    decorations: List[str] = Field(default_factory=list)
    transcended_armor: List[str] = Field(default_factory=list)
    custom_weapon: Optional[CustomGogWeapon] = None
    custom_talisman: Optional[CustomTalisman] = None

    @field_validator("transcended_armor")
    @classmethod
    def validate_transcended_armor(cls, value):
        valid_slots = {"helm", "chest", "arms", "waist", "legs"}
        invalid = set(value) - valid_slots
        if invalid:
            raise ValueError(f"Partes de armadura inválidas: {', '.join(sorted(invalid))}")
        return list(dict.fromkeys(value))


class ScenarioSettings(BaseModel):
    monster_id: str = "mon_20"
    target_part: str = "Media_Ponderada"
    wound_active: bool = False
    wound_hitzone_bonus: float = Field(default=0.0, ge=0.0, le=30.0)
    custom_monster: Optional[MonsterProfile] = None
    agitator_uptime: float = Field(default=0.8, ge=0.0, le=1.0)
    burst_uptime: float = Field(default=0.9, ge=0.0, le=1.0)
    weakness_exploit_uptime: float = Field(default=0.85, ge=0.0, le=1.0)
    maximum_might_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    peak_performance_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    offensive_guard_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    counterstrike_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    coalescence_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    latent_power_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    frenzy_antivirus_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    might_seed_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    demon_powder_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    mantle_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    resentment_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    elemental_absorption_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    elemental_absorption_hits: int = Field(default=1, ge=1, le=3)
    adrenaline_rush_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    foray_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    ambush_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    heroics_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    sharpness_management_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    critical_element_uptime: float = Field(default=1.0, ge=0.0, le=1.0)
    charge_master_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    status_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    food_attack_bonus: float = Field(default=0.0, ge=0.0, le=50.0)
    food_defense_bonus: float = Field(default=0.0, ge=0.0, le=100.0)
    fortify_stacks: int = Field(default=0, ge=0, le=2)
    hunting_horn_attack_uptime: float = Field(default=0.0, ge=0.0, le=1.0)
    hunt_duration_seconds: float = Field(default=600.0, ge=30.0, le=3600.0)
    rotation_id: Optional[str] = None
    custom_motion_value: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)


class HitAudit(BaseModel):
    hit_name: str
    motion_value: float
    physical_damage: float
    elemental_damage: float
    crit_physical_damage: float
    expected_damage: float
    hit_count: int = 1


class SkillSource(BaseModel):
    kind: str
    name: str
    slot_type: Optional[str] = None
    level: int = 1


class ActiveSkillDetail(BaseModel):
    name: str
    level: int
    kind: str = "armor"
    active: bool = True
    required_pieces: Optional[int] = None
    next_required_pieces: Optional[int] = None
    active_rank_name: Optional[str] = None
    active_rank_level: int = 0
    sources: List[SkillSource] = Field(default_factory=list)


class BuildResult(BaseModel):
    legality: Optional[BuildLegality] = None
    engine_version: str = "legacy"
    calculation_status: str = "estimated"
    rule_sources: List[str] = Field(default_factory=list)
    total_raw: float
    effective_raw: float
    total_affinity: float
    capped_affinity: float
    total_element: float
    effective_element: float
    total_element_display: float = 0.0
    effective_element_display: float = 0.0
    element_capped: bool = False
    element_cap_display: float = 0.0
    wound_hitzone_applied: float = 0.0
    target_part_name: str = "Media_Ponderada"
    physical_hitzone: float = 0.0
    elemental_hitzone: float = 0.0
    physical_damage_per_cycle: float = 0.0
    elemental_damage_per_cycle: float = 0.0
    crit_multiplier: float
    sharpness_raw_mult: float
    sharpness_ele_mult: float
    average_sharpness_raw_mult: float = 1.0
    average_sharpness_ele_mult: float = 1.0
    sharpness_consumed_per_cycle: float = 0.0
    top_sharpness_cycles: float = 0.0
    total_defense: int = 0
    max_defense: int = 0
    total_resistances: Dict[str, int] = Field(default_factory=dict)
    survivability_score: float = 0.0
    status_buildup_per_cycle: float = 0.0
    estimated_status_damage_per_cycle: float = 0.0
    status_damage_modeled: bool = False
    sustained_model: str = "sharpness_only_no_recovery"
    motion_values_verified: bool = False
    modeled_skills: List[str] = Field(default_factory=list)
    informational_skills: List[str] = Field(default_factory=list)
    weapon_mechanics: List[str] = Field(default_factory=list)
    active_skills: Dict[str, int]
    skill_details: List[ActiveSkillDetail] = Field(default_factory=list)
    damage_per_cycle: float
    practical_dps: float
    damage_per_min: float
    sustained_damage_per_cycle: float = 0.0
    sustained_dps: float = 0.0
    sustained_damage_per_min: float = 0.0
    combined_score: float
    hits_breakdown: List[HitAudit] = Field(default_factory=list)
    slot_warnings: List[str] = Field(default_factory=list)
    audit_notes: List[str] = Field(default_factory=list)
    rotation_id: str = ""
    rotation_name: str = ""
    cycle_time_seconds: float = 0.0


class OwnedSavedRecord(BaseModel):
    owner_id: str = Field(default="", max_length=128, exclude=True, repr=False)


class SavedBuild(OwnedSavedRecord):
    legality: Optional[BuildLegality] = None
    id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1200)
    equipment: BuildEquipment
    scenario: ScenarioSettings
    result: BuildResult
    provenance: Dict[str, Any] = Field(default_factory=dict)
    search_stats: Dict[str, Any] = Field(default_factory=dict)


class InventoryTalisman(OwnedSavedRecord):
    id: str = Field(min_length=1, max_length=128)
    talisman: CustomTalisman


class SavedDamage(OwnedSavedRecord):
    id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=180)
    build_name: str = Field(default="", max_length=120)
    equipment: BuildEquipment
    scenario: ScenarioSettings
    result: BuildResult


class OptimizerSettings(BaseModel):
    progression: Optional[ProgressionContext] = None
    verified_only: bool = False
    weapon_type: WeaponType
    weapon_id: Optional[str] = None
    target_skills: Dict[str, int] = Field(default_factory=dict)
    preferred_skills: Dict[str, int] = Field(default_factory=dict)
    monster_id: str = "mon_20"
    rotation_id: Optional[str] = None
    scenario: Optional[ScenarioSettings] = None
    preset_id: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=30)
    sort_by: str = "practical_dps"
    talismans: List[InventoryTalisman] = Field(default_factory=list)
    search_limit: int = Field(default=1200, ge=100, le=12000)
    armor_pool_limit: int = Field(default=10, ge=4, le=30)
    weapon_pool_limit: int = Field(default=3, ge=1, le=20)
    talisman_pool_limit: int = Field(default=8, ge=1, le=40)
    use_transcendence: bool = True


class RotationCompareRequest(BaseModel):
    equipment: BuildEquipment
    scenario: ScenarioSettings


class BuildCompareRequest(BaseModel):
    builds: List[SavedBuild] = Field(min_length=1, max_length=30)
    scenario: ScenarioSettings
    rotation_mode: Literal["saved", "best", "selected"] = "saved"


class RotationComparison(BaseModel):
    rotation: Rotation
    result: BuildResult


class MetaBuildPreset(BaseModel):
    id: str
    weapon_type: WeaponType
    profile: str
    name: str
    description: str
    monster_id: str
    target_skills: Dict[str, int] = Field(default_factory=dict)
    preferred_skills: Dict[str, int] = Field(default_factory=dict)
    rotation_category: str = "sustained"
    library_group: str = "endgame"
    max_rarity: Optional[int] = Field(default=None, ge=1, le=8)
    use_transcendence: bool = True
    uptime_preset: str = "realistic"
    hunter_rank_min: int = Field(default=100, ge=1)
    # Progression recommends a craftable tree weapon; endgame recommends Gog.
    weapon_recommendation_mode: str = "gog"
    source_urls: List[str] = Field(default_factory=list)


class GogRecommendationRequest(BaseModel):
    weapon_type: WeaponType
    monster_id: str
    rotation_id: Optional[str] = None
    preset_id: Optional[str] = None
    target_part: str = "Media_Ponderada"


class GogWeaponOption(BaseModel):
    id: str
    label: str
    rng_level: str
    weapon: CustomGogWeapon
    focus: str
    base_artian: str
    artian_reinforcements: List[str] = Field(default_factory=list)
    desired_skills: List[str] = Field(default_factory=list)
    acceptable_second_skill: str = "Qualquer uma"
    crafting_steps: List[str] = Field(default_factory=list)
    rationale: str


class GogWeaponRecommendation(BaseModel):
    weapon_type: WeaponType
    monster_id: str
    monster_name: str
    best_element: ElementType
    target_part: str = "Media_Ponderada"
    element_hitzone: float = 0.0
    situation: str
    perfect: GogWeaponOption
    accessible: GogWeaponOption
    source_urls: List[str] = Field(default_factory=list)


def rank_saved_builds(builds: List[SavedBuild], metric: str = "combined_score") -> List[SavedBuild]:
    valid_metrics = {
        "combined_score", "practical_dps", "damage_per_min",
        "damage_per_cycle", "effective_raw", "capped_affinity", "effective_element"
    }
    if metric not in valid_metrics:
        raise ValueError(f"Métrica de ranking inválida: {metric}")
    return sorted(builds, key=lambda b: getattr(b.result, metric), reverse=True)

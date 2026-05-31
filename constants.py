from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass(frozen=True)
class BuildingBlueprint:
    label: str
    icon: str
    food_cost: int = 0
    wood_cost: int = 0
    gold_cost: int = 0
    slots: int = 0

    house_component: Optional[BuildingHouseComponent] = None
    barrack_component: Optional[BuildingBarrackComponent] = None
    research_component: Optional[BuildingResearchComponent] = None
    production_component: Optional[BuildingProductionComponent] = None
    defense_component: Optional[BuildingDefenseComponent] = None

    @property
    def is_house(self) -> bool:
        return self.house_component is not None
    
    @property
    def is_military(self) -> bool:
        return self.barrack_component is not None
    
    @property
    def searches_techs(self) -> bool:
        return self.research_component is not None

    @property
    def produces_resources(self) -> bool:
        return self.production_component is not None
    
    @property
    def is_defensive(self) -> bool:
        return self.defense_component is not None
@dataclass(frozen=True)
class BuildingHouseComponent:
    slots_provided: int = 0

@dataclass(frozen=True)
class BuildingBarrackComponent:
    can_train_units: bool = False

@dataclass(frozen=True)
class BuildingResearchComponent:
    can_research_techs: bool = False

@dataclass(frozen=True)
class BuildingProductionComponent:
    resources_per_turn: Dict[str, int] = field(default_factory = dict)

@dataclass(frozen=True)
class BuildingDefenseComponent:
    is_a_wall: bool = False

@dataclass(frozen=True)
class UnitBlueprint:
    label: str
    icon: str
    food_cost: int
    wood_cost: int
    gold_cost: int
    defense: int
    line: str

    infantry_component: Optional[UnitInfantryComponent] = None
    ranged_component: Optional[UnitRangedComponent] = None
    cavalry_component: Optional[UnitCavalryComponent] = None
    anti_cavalry_component: Optional[UnitAntiCavalryComponent] = None
    siege_component: Optional[UnitSiegeComponent] = None

    @property
    def is_infantry(self) -> bool:
        return self.infantry_component is not None
    
    @property
    def is_ranged(self) -> bool:
        return self.ranged_component is not None
    
    @property
    def is_cavalry(self) -> bool:
        return self.cavalry_component is not None
    
    @property
    def is_anti_cavalry(self) -> bool:
        return self.anti_cavalry_component is not None
    
    @property
    def is_siege(self) -> bool:
        return self.siege_component is not None

@dataclass(frozen=True)
class UnitInfantryComponent:
    infantry_power: int

@dataclass(frozen=True)
class UnitRangedComponent:
    ranged_power: int

@dataclass(frozen=True)
class UnitCavalryComponent:
    cavalry_power: int

@dataclass(frozen=True)
class UnitAntiCavalryComponent:
    anti_cavalry_power: int

@dataclass(frozen=True)
class UnitSiegeComponent:
    siege_power: int

@dataclass(frozen=True)
class TechBlueprint:
    label: str
    icon: str
    description: str = ""
    root_building: Set[str] = field(defaut_factory = set)
    gold_cost: int = 0
    hidden: bool = False
    
    mod_component: Optional[TechModComponent] = None
    unit_provision_component: Optional[TechUnitProvisionComponent] = None

    @property
    def makes_mods(self) -> bool:
        return self.mod_component is not None
    
    @property
    def sends_units(self) -> bool:
        return self.unit_provision_component is not None

@dataclass(frozen=True)
class TechModComponent:
    mods: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class TechUnitProvisionComponent:
    units: Dict[str, int] = field(default_factory=dict)

#Código antigo


CIVS = {
    "Teresópolis": {
        "label": "Teresópolis 🏔️",
        "bonus": "Cerco de Montanhas: Muralhas 50% mais resistentes.",
        "mods": {
            "wall_defense": 1.5,
        }
    },
    "Petrópolis": {
        "label": "Petrópolis 🏰",
        "bonus": "Tropas Reais: Soldados são 30% mais baratos.",
        "mods": {
            "army_cost": 0.7,
        }
    },
    "Volta Redonda": {
        "label": "Volta Redonda 🏭",
        "bonus": "Fábricas: Produção de comida 25% maior.",
        "mods": {
            "food_production": 1.25,
        }
    },
    "Rio de Janeiro": {
        "label": "Rio de Janeiro 🏖️",
        "bonus": "Cidade Maravilhosa: Invasores dão metade do dano às cidades",
        "mods": {
            "pilhage_damage": 0.5,
        }
    }
}

INITIAL_LIFE = 200
INITIAL_FOOD = 60
INITIAL_WOOD = 25
INITIAL_GOLD = 0
INITIAL_ARMY = 0
INITIAL_BUILDINGS = {
    'casa' : 1,
    'fazenda' : 1,
    'serraria' : 0,
    'quartel' : 0,
    'muro' : 5,
    'mercado': 0,
    'moinho': 0,
    'arsenal': 0,
    'casa de construção': 0,
}
INITIAL_SLOTS = 0

DEFENSE_PER_WALL = 5
TRAIN_CAP_PER_QUARTEL = 6
SLOTS_PER_HOUSE = 3
ARMY_COST = 2
FOOD_PRODUCTION_PER_FARM = 2
WOOD_PRODUCTION_PER_LUMBERMILL = 3
GOLD_PRODUCTION_PER_MARKET = 5

FEW_WOOD = 25
MUCH_WOOD = 40
LOTS_OF_WOOD = 80
FEW_FOOD = 40
MUCH_FOOD = 70
LOTS_OF_FOOD = 100
FEW_SLOTS = 3
MUCH_SLOTS = 10
FEW_BARRACKS = 2
MUCH_BARRACKS = 5
FEW_ARMY = 35
MUCH_ARMY = 60
LOTS_OF_ARMY = 100

TOO_LITTLE = 0.5
TOO_MUCH = 0.8

BUILDINGS = {
    "casa": {
        "label": "🏠 Casa",
        "wood_cost": 0,
        "food_cost": 40,
        "description": f"Expande a vila. Libera +{SLOTS_PER_HOUSE} slots de construção.",
        "effect_value": SLOTS_PER_HOUSE,
        "slots": 0,
    },
    "fazenda": {
        "label": "🌱 Fazenda",
        "wood_cost": 6,
        "food_cost": 0,
        "description": f"Garante o sustento. Produz +{FOOD_PRODUCTION_PER_FARM} comida a cada turno.",
        "effect_value": FOOD_PRODUCTION_PER_FARM,
        "slots": 1,
    },
    "serraria": {
        "label": "🪚 Serraria",
        "wood_cost": 6,
        "food_cost": 0,
        "description": f"Essencial para obras. Produz +{WOOD_PRODUCTION_PER_LUMBERMILL} madeira a cada turno.",
        "effect_value": WOOD_PRODUCTION_PER_LUMBERMILL,
        "slots": 1,
    },
    "mercado": {
        "label": "🛒 Mercado",
        "wood_cost": 30,
        "food_cost": 0,
        "description": f"Faz o comércio girar. Produz +{GOLD_PRODUCTION_PER_MARKET} ouro a cada turno.",
        "effect_value": GOLD_PRODUCTION_PER_MARKET,
        "slots": 1,
    },
    "muro": {
        "label": "🧱 Muro",
        "wood_cost": 12,
        "food_cost": 0,
        "description": f"Proteção física. Aumenta a defesa base em +{DEFENSE_PER_WALL}.",
        "effect_value": DEFENSE_PER_WALL,
        "slots": 0,
    },
    "quartel": {
        "label": "⚔️ Quartel",
        "wood_cost": 30,
        "food_cost": 0,
        "description": f"Treinamento militar. Permite treinar até {TRAIN_CAP_PER_QUARTEL} soldados por turno. Cada soldado custa {ARMY_COST} comida.",
        "effect_value": TRAIN_CAP_PER_QUARTEL,
        "slots": 1,
    },
    "casa de construção": {
        "label": "🏗️ Casa de Construção",
        "wood_cost": 60,
        "food_cost": 0,
        "description": f"Libera tecnologias de construção e engenharia.",
        "effect_value": None,
        "slots": 3,
    },
    "moinho": {
        "label": "🌾 Moinho",
        "wood_cost": 60,
        "food_cost": 0,
        "description": f"Libera tecnologias para as fazendas.",
        "effect_value": None,
        "slots": 3,
    },
    "arsenal": {
        "label": "🛡️ Arsenal",
        "wood_cost": 60,
        "food_cost": 0,
        "description": f"Libera tecnologias para benefício do exército.",
        "effect_value": None,
        "slots": 3,
    }
}

TECHNOLOGIES = {
    "fertilizante": {
        "label": "🪱 Fertilizante",
        "description": "Aumenta a produção de comida em 20%",
        "gold_cost": 20,
        "mods": {
            "food_production": 1.2,
        },
        "requisities": [],
        "root_building": 'moinho',
    },
    "muralhas reforçadas": {
        "label": "🛡️ Muralhas reforçadas",
        "description": "Aumenta a defesa das muralhas em 50%",
        "gold_cost": 20,
        "mods": {
            "wall_defense": 1.5,
        },
        "requisities": [],
        "root_building": 'casa de construção',
    },
    "milícia da cidade": {
        "label": "👥 Milícia da Cidade",
        "description": "Diminui o dano de pilhagem em 25%",
        "gold_cost": 20,
        "mods": {
            "pilhage_damage": 0.75,
        },
        "requisities": [],
        "root_building": 'casa de construção',
    },
    "aço leve": {
        "label": "⚔️ Aço Leve",
        "description": "Reduz os custos de treinamento de soldados em 50%",
        "gold_cost": 20,
        "mods": {
            "army_cost": 0.5,
        },
        "requisities": [],
        "root_building": 'arsenal',
    },
    "legião de combate": {
        "label": "⚔️ Legião de Combate",
        "description": "Reduz os custos de treinamento de soldados em 50%",
        "gold_cost": 20,
        "mods": {
            "army_cost": 0.5,
        },
        "requisities": ["aço leve"],
        "root_building": 'arsenal',
    }
}

OPEN_BASELOSS = 0.7
OPEN_RESIDUALLOSS = 0.2
OPEN_CRITICALRATIO = 2
OPEN_DOMINANCERATIO = 3

SIEGE_BLOCKLOSS = 0.1
SIEGE_ATTACKERLOSS = 0.5
SIEGE_LOWBLOCKFACTOR = 0.1
SIEGE_HIGHBLOCKFACTOR = 0.5

PILHAGE_BASELOSS = 0.7
PILHAGE_DOMINANCERATIO = 3
PILHAGE_DAMAGEFACTOR = 0.4
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
        "bonus": "Tropas Reais: Soldados são 20% mais baratos.",
        "mods": {
            "army_cost": 0.8,
        }
    },
    "Volta Redonda": {
        "label": "Volta Redonda 🏭",
        "bonus": "Fábricas: Produção de recursos 25% maior.",
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
INITIAL_FOOD = 25
INITIAL_WOOD = 25
INITIAL_ARMY = 0
INITIAL_BUILDINGS = {
    'casa' : 1,
    'fazenda' : 1,
    'serraria' : 0,
    'quartel' : 0,
    'muro' : 5,
}
INITIAL_SLOTS = 0

DEFENSE_PER_WALL = 5
TRAIN_CAP_PER_QUARTEL = 6
SLOTS_PER_HOUSE = 3
ARMY_COST = 1
FOOD_PRODUCTION_PER_FARM = 4
WOOD_PRODUCTION_PER_LUMBERMILL = 4

FEW_WOOD = 25
MUCH_WOOD = 40
LOTS_OF_WOOD = 80
FEW_FOOD = 15
MUCH_FOOD = 40
LOTS_OF_FOOD = 80
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
        "food_cost": 10,
        "description": f"Expande a vila. Libera +{SLOTS_PER_HOUSE} slots de construção.",
        "effect_value": SLOTS_PER_HOUSE,
        "slots": 0,
    },
    "fazenda": {
        "label": "🌱 Fazenda",
        "wood_cost": 0,
        "food_cost": 5,
        "description": f"Garante o sustento. Produz +{FOOD_PRODUCTION_PER_FARM} comida a cada turno.",
        "effect_value": FOOD_PRODUCTION_PER_FARM,
        "slots": 1,
    },
    "serraria": {
        "label": "🪚 Serraria",
        "wood_cost": 5,
        "food_cost": 0,
        "description": f"Essencial para obras. Produz +{WOOD_PRODUCTION_PER_LUMBERMILL} madeira a cada turno.",
        "effect_value": WOOD_PRODUCTION_PER_LUMBERMILL,
        "slots": 1,
    },
    "muro": {
        "label": "🧱 Muro",
        "wood_cost": 20,
        "food_cost": 0,
        "description": f"Proteção física. Aumenta a defesa base em +{DEFENSE_PER_WALL}.",
        "effect_value": DEFENSE_PER_WALL,
        "slots": 0,
    },
    "quartel": {
        "label": "⚔️ Quartel",
        "wood_cost": 5,
        "food_cost": 0,
        "description": f"Treinamento militar. Permite treinar até {TRAIN_CAP_PER_QUARTEL} soldados por turno.",
        "effect_value": TRAIN_CAP_PER_QUARTEL,
        "slots": 1,
    }
}

OPEN_BASELOSS = 0.7
OPEN_RESIDUALLOSS = 0.2
OPEN_CRITICALRATIO = 2
OPEN_DOMINANCERATIO = 3

SIEGE_BLOCKLOSS = 0.2
SIEGE_ATTACKERLOSS = 0.2
SIEGE_LOWBLOCKFACTOR = 0.1
SIEGE_HIGHBLOCKFACTOR = 0.4

PILHAGE_BASELOSS = 0.7
PILHAGE_DOMINANCERATIO = 3
PILHAGE_DAMAGEFACTOR = 0.2
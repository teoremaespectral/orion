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

FORMATIONS = {
    "phalanx": {
        "label": "Falanque (Defensiva)",
        "description": "Formação defensiva, ideal para proteger muralhas e resistir a ataques frontais",
        "mods": {
            'fire_power': 1.3,
            'front_power': 1.3,
            'mobile_power': 0.7,
        },
    },
    "wedge": {
        "label": "Cuneiforme (Ofensiva)",
        "description": "Formação ofensiva, ideal para atacar inimigos em grupo",
        "mods": {
            'fire_power': 0.5,
            'front_power': 1.6,
        },
    },
    "skirmish": {
        "label": "Guerrilha (Móvel)",
        "description": "Formação dispersa, focada em mobilidade, ideal para manobras",
        "mods": {
            'front_power': 0.5,
            'mobile_power': 1.6,
        },
    },
    "square": {
        "label": "Quadrado (Protetora)",
        "description": "Formação de proteção total das unidades frágeis, ideal para evitar flancos e permitir foco máximo de fogo",
        "mods": {
            'fire_power': 1.6,
            'mobile_power': 0.5,
        },
    },
    "pincer": {
        "label": "Pinça (Tática)",
        "description": "Formação de ataque tático, ideal para flanquear o inimigo e derrotar suas unidades frágeis",
        "mods": {
            'front_power': 1.3,
            'fire_power': 0.7,
            'mobile_power': 1.3,
        },
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
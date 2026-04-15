CIVS = {
    "Teresópolis": {
        "label": "Teresópolis 🏔️",
        "bonus": "Cerco de Montanhas: Muralhas 40% mais resistentes.",
        "mods": {
            "wall_defense": 1.4,
        }
    },
    "Petrópolis": {
        "label": "Petrópolis 🏰",
        "bonus": "Tropas Reais: Treinamento gera 20% mais soldados com a mesma comida.",
        "mods": {
            "army_cost": 1.2,
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
INITIAL_FARMS = 1
INITIAL_FOOD = 5
INITIAL_ARMY = 0

FARM_COST = 5
FARM_PROD_BONUS = 5
DEFENSE = 25

OPEN_BASELOSS = 0.7
OPEN_RESIDUALLOSS = 0.2
OPEN_CRITICALRATIO = 1.5
OPEN_DOMINANCERATIO = 2.5

SIEGE_BLOCKLOSS = 0.4
SIEGE_ATTACKERLOSS = 0.5
SIEGE_LOWBLOCKFACTOR = 0.2
SIEGE_HIGHBLOCKFACTOR = 0.6

PILHAGE_BASELOSS = 0.7
PILHAGE_DOMINANCERATIO = 1.5
PILHAGE_DAMAGEFACTOR = 0.1
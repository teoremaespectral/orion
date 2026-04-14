from random import choices

# Pesos de decisão: [FARM, ARMY, ATTACK]
STRATEGIES = {
    "rusher": [30, 40, 30],    # Foca em exército e ataque constante
    "greedy": [85, 10, 5],    # Foca quase tudo em economia
    "turtle": [50, 45, 5],    # Prioriza exército mas raramente ataca
    "dumb": [34, 34, 33]  # O "Bot Burro"
}

def get_ai_decision(strategy_name, ai_kingdom):
    weights = STRATEGIES.get(strategy_name, STRATEGIES["dumb"])
    
    # Escolha baseada nos pesos
    choice = choices(["farm", "army", "attack"], weights=weights)[0]
        
    return choice
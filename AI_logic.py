from random import choice, choices
import constants as c

# --- SENSORES ---

def needs_wood(ai, amount = c.FEW_WOOD):
    ''' Se a madeira estiver abaixo de amount, é um sinal de alerta para construir uma serraria ou coletar mais madeira. '''
    return ai.resources['wood'] < amount

def needs_food(ai, amount = c.FEW_FOOD):
    ''' Se a comida estiver abaixo de amount, é um sinal de alerta para construir uma fazenda ou coletar mais comida. '''
    return ai.resources['food'] < amount

def needs_slots(ai, amount = c.FEW_SLOTS):
    ''' Se os slots estiverem quase todos ocupados, é necessário construir mais casas. '''
    return (ai.total_slots - ai.occupied_slots) <= amount

def has_few_barracks(ai, amount = c.FEW_BARRACKS):
    ''' Se o número de quartéis for baixo, é um sinal de alerta para construir mais quartéis. '''
    return ai.buildings['quartel'] < amount 

def has_little_army(ai, amount = c.FEW_ARMY):
    ''' Se o exército estiver abaixo de amount, é um sinal de alerta para treinar mais soldados. '''
    return ai.army < amount

def out_of_army(ai):
    ''' Se o exército estiver zerado, é um sinal de alerta para treinar mais soldados. '''
    return ai.army <= 0

# --- TÁTICAS DE CONSTRUÇÃO ---

TACTICS = {
    'first_moves': [
        [('build', 'fazenda'), ('build', 'serraria')],
        [('build', 'serraria'), ('build', 'fazenda')],
    ],
    'early_food': [[('build', 'casa'), ('build', 'fazenda'), ('build', 'fazenda'), ('build', 'fazenda')]],
    'early_wood': [[('build', 'casa'), ('build', 'serraria'), ('build', 'serraria'), ('build', 'serraria')]],
    'build_walls': [
        [('build', 'muro'), ('build', 'muro'), ('build', 'muro')],
        [('build', 'muro'), ('build', 'muro'), ('build', 'muro'), ('build', 'muro')],
    ],
    'build_a_house': [[('build', 'casa')]],
    'build_a_farm': [[('build', 'fazenda')]],
    'build_a_sawmill': [[('build', 'serraria')]],
    'build_a_market': [[('build', 'mercado')]],
    'build_a_barrack': [[('build', 'quartel')]],
    'train_soldiers': [
        [('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers')],
        [('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers'), ('army', 'soldiers')],
    ],
    'attack': [
        [('attack', 'attack')],
        [('attack', 'attack'), ('attack', 'attack')],
    ],
    'casa de construção': [[('build', 'casa'),('build', 'casa de construção')]],
    'moinho de vento': [[('build', 'casa'), ('build', 'moinho')]],
    'arsenal': [[('build', 'casa'), ('build', 'arsenal')]],
    'research walls': [[('research', 'muralhas reforçadas')]],
    'research_army': [[('research', 'aço leve'), ('research', 'legião de combate')]],
}

def get_tactic(tactic_name):
    ''' Retorna uma tática pré-definida, que é uma sequência de ações a serem tomadas. '''
    options = TACTICS.get(tactic_name, [[('build', 'casa')]])
    return choice(options).copy()

#BUILD ORDERS

def dumb_strategy(count):
    ''' Estratégia simples que segue uma ordem fixa de construção. '''
    if count == 1:
        return get_tactic('first_moves')
    elif count == 2:
        return get_tactic('early_food')
    elif count == 3:
        return get_tactic('early_wood')
    elif count == 4:
        return get_tactic('build_a_house')
    else:
        return get_tactic(choice(list(TACTICS.keys())))
    
def turtle_strategy(count):
    ''' Estratégia defensiva que prioriza a construção de muros e o fortalecimento das defesas. '''

    build_order = {
        1: 'first_moves',
        2: 'early_wood',
        3: 'build_walls',
        4: 'early_food',
        5: 'build_a_house',
        6: 'build_a_barrack',
        7: 'train_soldiers',
        8: 'attack',
        9: 'build_a_market',
        10: 'build_a_market',
        11: 'build_walls',
        12: 'casa de construção',
        13: 'research walls',
        14: 'build_a_house',
        15: 'build_a_farm',
        16: 'build_a_barrack',
    }

    if count in build_order.keys():
        return get_tactic(build_order[count])

    late_game_cycle = {
        0: 'attack',
        1: 'train_soldiers',
        2: 'train_soldiers',
    }
    
    return get_tactic(late_game_cycle[count % 3])

def rusher_strategy(count):
    ''' Estratégia agressiva que prioriza o ataque e o treinamento de soldados. '''

    build_order = {
        1: 'first_moves',
        2: 'early_food',
        3: 'early_wood',
        4: 'build_a_house',
        5: 'build_a_barrack',
        6: 'train_soldiers',
        7: 'attack',
        8: 'build_a_farm',
        9: 'build_a_barrack',
    }

    if count in build_order.keys():
        return get_tactic(build_order[count])

    late_game_cycle = {
        0: 'train_soldiers',
        1: 'attack',
    }
    
    return get_tactic(late_game_cycle[count % 2])

def greedy_strategy(count):
    ''' Estratégia que prioriza a construção de edifícios que aumentam a produção de recursos, como fazendas e serrarias. '''

    build_order = {
        1: 'first_moves',
        2: 'early_food',
        3: 'early_wood',
        4: 'build_a_house',
        5: 'build_a_market',
        6: 'build_walls',
        7: 'arsenal',
        8: 'research_army',
        9: 'build_a_farm',
        10: 'build_a_barrack',
        11: 'train_soldiers',
        12: 'build_a_house',
        13: 'build_a_barrack',
    }

    if count in build_order.keys():
        return get_tactic(build_order[count])

    late_game_cycle = {
        0: 'attack',
        1: 'train_soldiers',
        2: 'train_soldiers',
    }
    
    return get_tactic(late_game_cycle[count % 3])
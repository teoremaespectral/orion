from random import choice, choices
from utils import is_too_little, is_too_much
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

BUILD_TACTICS = {
    'make_a_house': [
        ['casa'],
    ],
    'make_some_houses': [
        ['casa', 'casa'],
        ['casa', 'casa', 'casa'],
    ],
    'make_some_farms': [
        ['fazenda', 'fazenda'],
        ['fazenda', 'fazenda', 'fazenda'],
    ],
    'make_lots_of_farms': [
        ['fazenda', 'fazenda', 'fazenda', 'fazenda'],
        ['fazenda', 'fazenda', 'fazenda', 'fazenda', 'fazenda'],
    ],
    'make_some_sawmills': [
        ['serraria', 'serraria'],
        ['serraria', 'serraria', 'serraria'],
    ],
    'make_lots_of_sawmills': [
        ['serraria', 'serraria', 'serraria', 'serraria'],
        ['serraria', 'serraria', 'serraria', 'serraria', 'serraria'],
    ],
    'make_some_barracks': [
        ['quartel', 'quartel'],
        ['quartel', 'quartel', 'quartel'],
    ],
    'make_lots_of_barracks': [
        ['quartel', 'quartel', 'quartel', 'quartel'],
        ['quartel', 'quartel', 'quartel', 'quartel', 'quartel'],
    ],
    'make_a_wall': [
        ['muro'],
    ],
}

ARMY_TACTICS = {
    'train_some_soldiers': [
        ['train_army'],
        ['train_army', 'train_army'],
    ],
    'train_lots_of_soldiers': [
        ['train_army', 'train_army', 'train_army'],
        ['train_army', 'train_army', 'train_army', 'train_army'],
    ],
}

ATTACK_TACTICS = {
    'make_a_attack': [
        ['attack'],
    ],
    'make_some_attacks': [
        ['attack', 'attack'],
        ['attack', 'attack', 'attack'],
    ],
}

def get_tactic_sequence(category, tactic_name):
    '''
    Busca uma sequência de ações baseada na categoria (BUILD, ARMY, ATTACK)
    e no nome da tática escolhida pela estratégia.
    '''
    categories = {
        'build': BUILD_TACTICS,
        'army': ARMY_TACTICS,
        'attack': ATTACK_TACTICS
    }
    
    # Busca a categoria, depois a tática. Se não achar, retorna uma lista padrão segura.
    tactic_dict = categories.get(category, BUILD_TACTICS)
    sequence = choice(tactic_dict.get(tactic_name, [["casa"]])).copy()
    return category, sequence

def dumb_strategy(ai):
    ''' Uma estratégia "burra" que prioriza a construção de casas quando os slots estão baixos, depois serrarias se a madeira estiver baixa, e depois escolhe aleatoriamente entre construir, treinar ou atacar. '''
    # Sensores de sobrevivência (O cérebro reptiliano da IA)
    if needs_slots(ai):
        return get_tactic_sequence('build', 'make_a_house')
    if needs_wood(ai):
        return get_tactic_sequence('build', 'make_some_sawmills')
    
    # Decisão aleatória (A parte "Burra")
    category = choice(['build', 'army', 'attack'])
    
    if category == 'build':
        tactic = choice(list(BUILD_TACTICS.keys()))
    elif category == 'army':
        tactic = choice(list(ARMY_TACTICS.keys()))
    else:
        tactic = choice(list(ATTACK_TACTICS.keys()))
        
    return get_tactic_sequence(category, tactic)

def rusher_strategy(ai):
    '''Uma estratégia agressiva que prioriza o ataque constante, mas ainda tenta manter um mínimo de exército e economia para sustentar a ofensiva. '''

    if has_little_army(ai):
        if needs_slots(ai):
            return get_tactic_sequence('build', 'make_a_house')
        
        if needs_wood(ai):
            return get_tactic_sequence('build', 'make_some_sawmills')
    
        if needs_food(ai):
            return get_tactic_sequence('build', 'make_some_farms')
    
        if has_few_barracks(ai):
            return get_tactic_sequence('build', 'make_some_barracks')
    
        if out_of_army(ai):
            return get_tactic_sequence('army', 'train_some_soldiers')
        
        tactic_type, tactic_name = choice([
            ['build','make_some_barracks'], 
            ['army','train_some_soldiers'],
            ['attack','make_a_attack']
            ])
        return get_tactic_sequence(tactic_type, tactic_name)
    
    else:
        tactic_type, tactic_name = choices([
            ['army','train_some_soldiers'],
            ['build', 'make_some_barracks'],
            ['attack','make_a_attack'],
            ['attack','make_some_attacks'],
            ], weights=[10, 10, 50, 30]
            )[0]
        return get_tactic_sequence(tactic_type, tactic_name)
    
def turtle_strategy(ai):
    '''Uma estratégia defensiva que prioriza a construção de defesas e o fortalecimento do exército antes de considerar ataques.'''

    if has_little_army(ai, c.MUCH_ARMY):
        if needs_slots(ai):
            return get_tactic_sequence('build', 'make_a_house')
        if needs_wood(ai, c.MUCH_WOOD):
            return get_tactic_sequence('build', 'make_some_sawmills')
    
        if needs_food(ai):
            return get_tactic_sequence('build', 'make_some_farms')
    
        if has_few_barracks(ai):
            return get_tactic_sequence('build', 'make_some_barracks')
    
        if out_of_army(ai):
            return get_tactic_sequence('army', 'train_some_soldiers')
        
        tactic_type, tactic_name = choice([
            ['build','make_some_barracks'], 
            ['army','train_some_soldiers'],
            ['army','train_lots_of_soldiers'],
            ])
        return get_tactic_sequence(tactic_type, tactic_name)
    
    else:
        if needs_food(ai, c.MUCH_FOOD):
            return get_tactic_sequence('build', 'make_some_farms')
        if needs_wood(ai, c.MUCH_WOOD):
            return get_tactic_sequence('build', 'make_some_sawmills')
        tactic_type, tactic_name = choices([
            ['army','train_lots_of_soldiers'],
            ['build', 'make_lots_of_barracks'],
            ['build', 'make_lots_of_sawmills'],
            ['build', 'make_a_wall'],
            ['attack','make_a_attack'],
            ['attack','make_some_attacks'],
            ], weights=[20, 5, 5, 50, 10, 10])[0]
        return get_tactic_sequence(tactic_type, tactic_name)

def greedy_strategy(ai):
    '''Uma estratégia que tenta maximizar a economia e o exército antes de lançar ataques massivos. Pode ser arriscada, mas se funcionar, pode esmagar o oponente com uma ofensiva esmagadora.'''
    
    if needs_food(ai, c.LOTS_OF_FOOD):
        if needs_wood(ai):
            return get_tactic_sequence('build', 'make_some_sawmills')
    
        if needs_slots(ai):
            return get_tactic_sequence('build', 'make_a_house')
    
        if needs_food(ai, c.MUCH_FOOD):
            return get_tactic_sequence('build', 'make_some_farms')
        
        tactic_type, tactic_name = choice([
            ['build','make_some_farms'],
            ['build','make_lots_of_farms'],
            ['build', 'make_some_sawmills'],
            ])
        return get_tactic_sequence(tactic_type, tactic_name)
    
    elif has_little_army(ai, c.LOTS_OF_ARMY):
        if needs_wood(ai, c.MUCH_WOOD):
            return get_tactic_sequence('build', 'make_some_sawmills')
        
        if has_few_barracks(ai):
            return get_tactic_sequence('build', 'make_some_barracks')
        
        if out_of_army(ai):
            return get_tactic_sequence('army', 'train_lots_of_soldiers')
        
        tactic_type, tactic_name = choice([
            ['build','make_some_barracks'],
            ['build','make_lots_of_barracks'],
            ['army','train_some_soldiers'],
            ['army','train_lots_of_soldiers'],
            ])
        return get_tactic_sequence(tactic_type, tactic_name)
    
    else:
        
        tactic_type, tactic_name = choices([
            ['army','train_lots_of_soldiers'],
            ['build', 'make_lots_of_barracks'],
            ['build', 'make_some_farms'],
            ['build', 'make_lots_of_farms'],
            ['attack','make_a_attack'],
            ['attack','make_some_attacks'],
            ], weights=[5, 5, 5, 5, 40, 40])[0]
        return get_tactic_sequence(tactic_type, tactic_name)



def get_ai_tactic(strategy_name, ai):
    '''Dada a escolha da estratégia, retorna a sequência de ações que a IA deve executar.'''
    strategies = {
        'dumb': dumb_strategy,
        'rusher': rusher_strategy,
        'turtle': turtle_strategy,
        'greedy': greedy_strategy,
    }
    strategy_func = strategies.get(strategy_name, dumb_strategy)
    return strategy_func(ai)
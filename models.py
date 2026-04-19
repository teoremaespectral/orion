import constants as c
from math import prod

from orion import AI_logic

class Kingdom:
    '''Representa o estado de um reino, incluindo recursos, construções, exército e vida.'''
    def __init__(self, user_id, user_name, data=None):
        '''Inicializa o reino com dados pré-existentes ou valores padrão para um novo jogo.'''
        self.user_id = user_id
        self.user_name = user_name

        if data:
            self.life = data.get('life', c.INITIAL_LIFE)
            self.civ = data.get('civ', 'Teresópolis')
            
            # AGRUPAMENTO DE RECURSOS
            self.resources = data.get('resources', {
                "food": c.INITIAL_FOOD,
                "wood": c.INITIAL_WOOD,
                "gold": c.INITIAL_GOLD,
            })
            self.buildings = data.get('buildings', c.INITIAL_BUILDINGS.copy())
            self.army = data.get('army', c.INITIAL_ARMY)
            self.searched_techs = data.get('searched_techs', [])

        else:
            # Inicialização para novo jogo
            self.life = c.INITIAL_LIFE
            self.civ = 'Teresópolis'
            self.resources = {
                "food": c.INITIAL_FOOD, 
                "wood": c.INITIAL_WOOD,
                "gold": c.INITIAL_GOLD,
                }
            self.buildings = c.INITIAL_BUILDINGS.copy()
            self.army = c.INITIAL_ARMY
            self.searched_techs = []

    @property
    def occupied_slots(self):
        return sum(
            self.buildings.get(b, 0) * c.BUILDINGS.get(b, {}).get('slots', 0) 
            for b in self.buildings
        )

    @property
    def total_slots(self):
        return c.INITIAL_SLOTS + (self.buildings['casa'] * c.SLOTS_PER_HOUSE)

    def MODIFIER(self, mod_type):
        tech_mod = prod(c.TECHNOLOGIES[t].get('mods', {}).get(mod_type, 1.0) for t in self.searched_techs)
        civ_mod = c.CIVS.get(self.civ, {}).get('mods', {}).get(mod_type, 1.0)
        return tech_mod * civ_mod
    
    @property
    def FARM_PROD_BONUS(self):
        return c.BUILDINGS['fazenda']['effect_value'] * self.MODIFIER('food_production')
    
    @property
    def WOOD_PROD_BONUS(self):
        return c.BUILDINGS['serraria']['effect_value'] * self.MODIFIER('wood_production')
    
    @property
    def ARMY_COST(self):
        return int(c.ARMY_COST * self.MODIFIER('army_cost'))

    @property
    def WALL_DEFENSE(self):
        return c.BUILDINGS['muro']['effect_value'] * self.MODIFIER('wall_defense')

    def to_dict(self):
        """Transforma as informações contidas na instância em um dicionário"""
        return {
            "user_name": self.user_name,
            "life": self.life,
            "buildings": self.buildings,
            "resources": self.resources,
            "army": self.army,
            "civ": self.civ,
            "searched_techs": self.searched_techs,
        }
    
    def produce_resources(self):
        '''Calcula a produção de recursos com base nas construções e bônus civis, e atualiza os recursos do reino.'''
        self.resources['food']+= int(self.buildings['fazenda'] * self.FARM_PROD_BONUS)
        self.resources['wood'] += int(self.buildings['serraria'] * self.WOOD_PROD_BONUS)
        self.resources['gold'] += int(self.buildings['mercado'] * c.GOLD_PRODUCTION_PER_MARKET)

    def build(self, building_type):
        # ... (validações iniciais)
        cost = c.BUILDINGS[building_type]
        needs_slot = cost.get('slots', 0) > 0

        has_food = self.resources["food"] >= cost.get("food_cost", 0)
        has_wood = self.resources["wood"] >= cost.get("wood_cost", 0)
        has_gold = self.resources["gold"] >= cost.get("gold_cost", 0) # NOVO

        if has_food and has_wood and has_gold and not (needs_slot and self.occupied_slots >= self.total_slots):
            self.resources["food"] -= cost.get("food_cost", 0)
            self.resources["wood"] -= cost.get("wood_cost", 0)
            self.resources["gold"] -= cost.get("gold_cost", 0) # NOVO
            self.buildings[building_type] += 1
            return True
        return False

    def train_army(self):
        '''Tenta treinar soldados, verificando o custo total com base na capacidade dos quartéis e aplicando modificadores civis. Retorna True se o treinamento for bem-sucedido, ou False caso contrário.'''
        # Quantidade máxima que os quarteis aguentam
        capacidade = int(c.TRAIN_CAP_PER_QUARTEL * self.buildings['quartel'])
        custo_total = capacidade * self.ARMY_COST
    
        if capacidade > 0 and self.resources["food"] >= custo_total:
            self.army += capacidade
            self.resources["food"] -= custo_total
            return True
        return False

    def research(self, tech_id):
        '''
        Tenta pesquisar uma tecnologia. Verifica requisitos, desconta o ouro 
        e aplica os modificadores permanentemente ao reino.
        Retorna True se a pesquisa foi concluída, False caso contrário.
        '''
        # 1. Usamos o can_research que você criou para validar a transação
        if not self.can_research(tech_id):
            return False

        tech_data = c.TECHNOLOGIES[tech_id]

        # 2. Descontar o custo de ouro
        self.resources['gold'] -= tech_data.get('gold_cost', 0)

        # 3. Adicionar à lista de tecnologias conhecidas
        self.searched_techs.append(tech_id)

        # 4. Aplicar modificadores (Se houver)
        # Nota: A aplicação real dos modificadores (como army_cost) deve ser 
        # refletida nas @properties que você já tem (como self.ARMY_COST).

        return True
    
    def can_build(self, building_type):
        '''Verifica se o reino tem recursos e slots suficientes para construir um edifício do tipo especificado. Retorna True se for possível construir, ou False caso contrário.'''
        if building_type not in c.BUILDINGS:
            return False

        cost = c.BUILDINGS[building_type]
        needs_slot = cost.get('slots', 0) > 0

        if needs_slot and self.occupied_slots >= self.total_slots:
            return False
        
        return (self.resources["food"] >= cost["food_cost"] and
                self.resources["wood"] >= cost["wood_cost"] and
                self.resources["gold"] >= cost["gold_cost"])
    
    def can_research(self, tech_id):
        # 1. Validação básica de existência
        if tech_id not in c.TECHNOLOGIES:
            return False
    
        tech_data = c.TECHNOLOGIES[tech_id]
    
        # 2. Checagens lógicas
        has_not_researched = tech_id not in self.searched_techs
    
        # CORREÇÃO: Checar se as tecnologias de requisito estão em searched_techs
        reqs = tech_data.get('requisities', [])
        has_requisities = all(r in self.searched_techs for r in reqs)
    
        # Checar se a construção raiz existe
        root_b = tech_data.get('root_building')
        has_root_building = self.buildings.get(root_b, 0) > 0
    
        # Checar ouro
        has_resources = self.resources.get("gold", 0) >= tech_data.get('gold_cost', 0)
    
        return has_not_researched and has_requisities and has_root_building and has_resources
    
class Bot:
    '''Representa um bot controlado por IA, com uma civilização, personalidade e táticas de jogo. O bot pode decidir suas ações com base no estado do reino e em sua personalidade, utilizando a lógica definida em AI_logic para determinar suas táticas.'''
    def __init__(self, brain_data = None):
        '''Inicializa o bot com dados pré-existentes ou valores padrão para um novo bot. Se brain_data for fornecido, ele é usado para configurar o estado do bot; caso contrário, os parâmetros civ e personality são usados para definir a civilização e personalidade do bot, com táticas e contagem de turnos iniciando em valores padrão.'''
        if not brain_data:
            self._setup_new_bot()

        else:
            self.name = brain_data['name']
            self.civ = brain_data['civ']
            self.personality = brain_data['personality']
            self.turn_count = brain_data['turn_count']
            self.tactic = brain_data['tactic']
            self.tactic_type = brain_data['tactic_type']

    def _setup_new_bot(self):
        '''Configura um novo bot com uma civilização e personalidade específicas, e inicializa suas táticas e contagem de turnos. Este método é chamado quando não há dados pré-existentes para o bot, garantindo que ele seja criado com uma configuração limpa e consistente.'''
        self.name = "Bot"
        self.civ = 'Teresópolis'
        self.personality = 'dumb'
        self.turn_count = 1
        self.tactic = []
        self.tactic_type = None

    def to_dict(self):
        """Transforma as informações contidas na instância em um dicionário"""
        return {
            "name" : self.name,
            "civ" : self.civ,
            "personality" : self.personality,
            "tactic" : self.tactic,
            "tactic_type" : self.tactic_type,
        }

    def get_next_action(self, kingdom):
        '''Determina a próxima ação do bot com base em sua personalidade e no estado atual do reino. Se o bot não tiver táticas definidas, ele chama a função get_ai_tactic de AI_logic para obter uma nova tática com base em sua personalidade e no estado do reino. Em seguida, ele retorna a próxima ação a ser executada, que inclui o tipo de ação e o alvo da ação.'''
        if self.tactic == []:
            self.tactic_type, self.tactic = AI_logic.get_ai_tactic(self.personality, kingdom)
    
        action_target = self.tactic.pop(0)
        return {"type": self.tactic_type, "target": action_target}

    

class CombatEngine:
    '''Responsável por resolver os combates entre reinos, aplicando as regras de confronto e gerando relatórios detalhados sobre os resultados.'''
    def __init__(self, attacker, defender):
        '''Inicializa o motor de combate com os reinos atacante e defensor, e armazena os dados pré-combate para geração de relatórios.'''
        self.attacker = attacker
        self.defender = defender
        # Cache dos dados ANTES do combate para o relatório
        self.stats_pre = {
            "attacker_army": attacker.army,
            "defender_army": defender.army,
            "defender_life": defender.life,
        }

    def resolve(self, type="invasion"):
        ''''Determina o tipo de combate (campo aberto ou invasão) e chama o método correspondente para resolver o confronto. Retorna um relatório detalhado do resultado do combate.'''
        if type == "open_field":
            return self._open_field_clash()
        return self._invasion_clash()

    def _open_field_clash(self):
        '''Resolve um confronto em campo aberto entre o atacante e o defensor, aplicando as regras de combate baseadas na razão entre os exércitos e gerando um relatório detalhado do resultado.'''

        #Identificando o forte e o fraco
        if self.attacker.army >= self.defender.army:
            strong, weak = self.attacker, self.defender
        else:
            strong, weak = self.defender, self.attacker

        R = strong.army / max(1, weak.army)

        #Possíveis desfechos do combate
        if R == 1:
            s_loss = w_loss = c.OPEN_BASELOSS
            sit = 'draw'
        
        elif R <= c.OPEN_CRITICALRATIO:
            s_loss = (c.OPEN_BASELOSS - c.OPEN_RESIDUALLOSS) * \
                     (c.OPEN_CRITICALRATIO**2 - R**2) / (c.OPEN_CRITICALRATIO**2 - 1) + \
                     c.OPEN_RESIDUALLOSS
            w_loss = (c.OPEN_BASELOSS - 1) * (c.OPEN_CRITICALRATIO**2 - R**2) / \
                     (c.OPEN_CRITICALRATIO**2 - 1) + 1
            sit = 'costly_win'

        else:
            s_loss = max(0, c.OPEN_RESIDUALLOSS * (c.OPEN_DOMINANCERATIO - R) / \
                     (c.OPEN_DOMINANCERATIO - c.OPEN_CRITICALRATIO))
            w_loss = 1.0
            sit = 'true_win'

        # Aplicar as baixas
        strong.army = int(strong.army * (1 - s_loss))
        weak.army = int(weak.army * (1 - w_loss))

        # Determinar o resultado final do combate do ponto de vista do atacante
        attacker_won = strong == self.attacker

        if sit == 'draw':
            final_sit = 'draw'
        elif attacker_won:
            final_sit = sit # 'costly_win' ou 'true_win'
        else:
            # Inverte a narrativa para o ponto de vista do atacante
            final_sit = 'costly_defeat' if sit == 'costly_win' else 'total_defeat'

        # Identificar perdas específicas
        if attacker_won:
            a_loss, d_loss = s_loss, w_loss
        else:
            # Se o defensor (strong) ganhou, a_loss é a perda do fraco
            a_loss, d_loss = w_loss, s_loss

        return self._generate_report(final_sit, a_loss, d_loss)

    def _invasion_clash(self):
        '''Resolve um confronto de invasão entre o atacante e o defensor, aplicando as regras de combate baseadas na defesa do muro, tamanho dos exércitos e possíveis pilhagens, e gerando um relatório detalhado do resultado.'''
        DEFENSE = self.defender.buildings.get('muro', 0)*self.defender.WALL_DEFENSE
        low_t = DEFENSE + self.defender.army * c.SIEGE_LOWBLOCKFACTOR
        high_t = DEFENSE + self.defender.army * c.SIEGE_HIGHBLOCKFACTOR
        
        a_loss, d_loss, sit = 0, 0, ""

        #Fase de cerco: o muro absorve o impacto inicial, podendo causar perdas para o atacante, ou até mesmo permitir uma vitória completa se o atacante for suficientemente forte.
        if self.attacker.army <= low_t:
            a_loss, d_loss, sit = c.SIEGE_ATTACKERLOSS, 0, 'full_block'
        elif self.attacker.army < high_t:
            a_loss = c.SIEGE_ATTACKERLOSS * (high_t - self.attacker.army) / (high_t - low_t)
            d_loss = c.SIEGE_BLOCKLOSS * (self.attacker.army - low_t) / (high_t - low_t)
            sit = 'costly_block'

        #Fase de pilhagem: se o atacante conseguir romper o bloqueio do muro, ele pode causar danos ao defensor. Se o atacante for apenas moderadamente mais forte, ele causará danos limitados (pilhagem). Se for muito mais forte, ele destruirá completamente o defensor.
        else:
            if self.defender.army > 0 and (self.attacker.army / self.defender.army) < c.PILHAGE_DOMINANCERATIO:
                a_loss, d_loss = c.PILHAGE_BASELOSS, c.PILHAGE_BASELOSS
                mod_dmg = c.CIVS.get(self.defender.civ, {}).get('mods', {}).get('pilhage_damage', 1.0)
                damage = c.PILHAGE_DAMAGEFACTOR * self.attacker.army * (1 - a_loss) * mod_dmg
                self.defender.life = int(max(0, self.defender.life - damage))
                sit = 'pilhage'
            else:
                a_loss, d_loss, sit = 0, 1.0, 'complete_destruction'
                self.defender.life = 0

        self.attacker.army = int(self.attacker.army * (1 - a_loss))
        self.defender.army = int(self.defender.army * (1 - d_loss))

        return self._generate_report(sit, a_loss, d_loss, is_invasion=True)

    def _generate_report(self, situation, a_loss, d_loss, is_invasion=False):
        '''Gera um relatório detalhado do combate, incluindo a situação final, perdas para ambos os lados e, no caso de invasão, o impacto na vida do defensor. Retorna um dicionário com todas as informações relevantes para análise posterior.'''
        report = {
            "situation": situation,
            "attacker_start_army": self.stats_pre["attacker_army"],
            "defender_start_army": self.stats_pre["defender_army"],
            "defender_start_life": self.stats_pre["defender_life"],
            "defender_damage_taken": self.stats_pre["defender_life"] - self.defender.life if is_invasion else 0,
            "attacker_loss": a_loss,
            "defender_loss": d_loss,
            "is_invasion": is_invasion,
        }
        if is_invasion: 
            '''Em combates de invasão, o relatório também inclui se o defensor foi derrotado (vida <= 0) e a vida final do defensor após o combate.'''
            report["is_over"] = self.defender.life <= 0
            report["defender_final_life"] = self.defender.life
        return report
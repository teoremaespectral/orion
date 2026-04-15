from models import Kingdom
from db_utils import get_db, save_db
import constants as consts
import AI_logic
from random import choice

class Game:
    def __init__(self, user_id, user_name):
        self.user_id = str(user_id)
        self.user_name = user_name
        self.db_data = get_db('games_data') # Arquivo específico para partidas

        user_data = self.db_data.get(self.user_id)
        ai_data = self.db_data.get(f"{self.user_id}_ai")

        if not user_data:
            self.turn_count = 1
            self.status = "active" # active, player_won, ai_won
            self.ai_strategy = choice(['dumb', 'rusher', 'turtle', 'greedy'])
        else:
            self.turn_count = user_data.get('turn_count', 1)
            self.status = user_data.get('status', 'active')
            self.ai_strategy = user_data.get('ai_strategy', 'dumb')
        
        # Carrega ou cria os reinos
        self.player = Kingdom(self.user_id, self.user_name, user_data)
        self.ai = Kingdom(f"{self.user_id}_ai", "Bot", ai_data)

    def save(self):
        """Atualiza o banco de dados com os estados atuais"""
        player_dict = self.player.to_dict()
        player_dict['turn_count'] = self.turn_count
        player_dict['status'] = self.status
        player_dict['ai_strategy'] = self.ai_strategy
        
        self.db_data[self.user_id] = player_dict
        self.db_data[f"{self.user_id}_ai"] = self.ai.to_dict()
        save_db(self.db_data, 'games_data')

    def reset(self, player_civ="Teresópolis", ai_civ="Petrópolis", strategy="Aleatório"):
        # Garante que criamos reinos limpos com a civ correta
        self.player = Kingdom(self.user_id, self.user_name)
        self.player.civ = player_civ
    
        self.ai = Kingdom(f"{self.user_id}_ai", "Bot")
        self.ai.civ = ai_civ
    
        self.turn_count = 1
        self.status = "active"
    
        # Tratamento da estratégia
        if strategy == "Aleatório":
            self.ai_strategy = choice(['dumb', 'rusher', 'turtle', 'greedy'])
        else:
            self.ai_strategy = strategy.lower()
        
        self.save()

    def play_turn(self, action_type):
        """
        Orquestra o turno:
        1. Executa ação do jogador
        2. Executa ação da IA
        3. Atacar!
        4. Produção para ambos
        """

        #O feedback do que ocorreu no turno

        # 1. Ação do Jogador
        player_action = action_type
        player_result = self.process_player_turn(action_type)

        # 2. Turno da IA (Lógica simples por enquanto)
        ai_action, ai_result = self.process_ai_turn()

        # 3. Checa se há combate
        fight_data = self.process_fight(player_action, ai_action)
    
        # 4. Produção (Turno passa para ambos)
        self.player.produce_resources()
        self.ai.produce_resources()

        # Salvar
        self.turn_count += 1
        self._check_victory_conditions()
        self.save()

        report = {
            "player_action": player_action,
            "player_result": player_result,
            "ai_action": ai_action,
            "ai_result": ai_result,
            "fight_data": fight_data,
        }
        return report
    
    def process_player_turn(self, action_type):
        if action_type == "farm":
            if self.player.build_farm():
                return action_type
        elif action_type == "army":
            if self.player.train_army():
                return action_type
        elif action_type == "attack":
            if self.player.army > 0:
                return action_type
        
        return "fail"

    def process_ai_turn(self):
        """Simula a decisão da IA"""
        action_type = AI_logic.get_ai_decision(self.ai_strategy, self.ai)
        
        if action_type == "farm":
            if self.ai.build_farm():
                return action_type, action_type
        elif action_type == "army":
            if self.ai.train_army():
                return action_type, action_type
        elif action_type == "attack":
            if self.ai.army > 0:
                return action_type, action_type
        
        return action_type, "fail"

    def process_fight(self, player_action, ai_action):
        """Simulação de combate"""
        if player_action == "attack" and ai_action == "attack": #Confronto de exércitos
            return self.openfield_clash()

        elif player_action == "attack": #Se o jogador é o atacante
            return self.invasion_clash(initiative='player')

        elif ai_action == "attack":
            return self.invasion_clash(initiative='ai')

        return None
    
    def _check_victory_conditions(self):
        if self.player.life <= 0:
            self.status = "ai_won"
        elif self.ai.life <= 0:
            self.status = "player_won"
        return
    
    def openfield_clash(self):

        if self.player.army >= self.ai.army:
            strong, weak = self.player, self.ai
        else:
            strong, weak = self.ai, self.player

        R = strong.army/weak.army

        BASELOSS = consts.OPEN_BASELOSS
        RESIDUALLOSS = consts.OPEN_RESIDUALLOSS
        CRITICAL = consts.OPEN_CRITICALRATIO
        DOMINANCE = consts.OPEN_DOMINANCERATIO

        if R <= CRITICAL:
            strong_loss = (BASELOSS - RESIDUALLOSS)*(CRITICAL**2 - R**2)/(CRITICAL**2 - 1) + RESIDUALLOSS
            weak_loss = (BASELOSS - 1)*(CRITICAL**2 - R**2)/(CRITICAL**2 - 1) + 1
            situation = 'costly_win'

        else:
            strong_loss = max(0, RESIDUALLOSS*(DOMINANCE - R)/(DOMINANCE - CRITICAL))
            weak_loss = 1
            situation = 'true_win'

        if R == 1:
            situation = 'draw'

        strong.army = int(strong.army*(1-strong_loss))
        weak.army = int(weak.army*(1-weak_loss))

        return {
            "winner" : strong,
            "situation": situation,
            "winner_final_army" : strong.army, 
            "winner_loss" : strong_loss,
            "weak_final_army" : weak.army,
            "weak_loss" : weak_loss
            }
        


    def invasion_clash(self, initiative):
        
        if initiative == 'player':
            attacker, defender = self.player, self.ai
        else:
            attacker, defender = self.ai, self.player

        #Fase 1: Cerco
        mod = consts.CIVS.get(defender.civ, {}).get('mods', {}).get('wall_defense', 1.0)
        city_defense = consts.DEFENSE*mod
        LOW_THRESHOLD = city_defense + defender.army*consts.SIEGE_LOWBLOCKFACTOR
        HIGH_THRESHOLD = city_defense + defender.army*consts.SIEGE_HIGHBLOCKFACTOR
        situation = None

        if attacker.army <= LOW_THRESHOLD:
            attacker_loss = consts.SIEGE_ATTACKERLOSS
            defender_loss = 0
            situation = 'full_block'
        
        elif attacker.army < HIGH_THRESHOLD:
            attacker_loss = consts.SIEGE_ATTACKERLOSS*(HIGH_THRESHOLD - attacker.army)/(HIGH_THRESHOLD - LOW_THRESHOLD)
            defender_loss = consts.SIEGE_BLOCKLOSS*(attacker.army - LOW_THRESHOLD)/(HIGH_THRESHOLD - LOW_THRESHOLD)
            situation = 'costly_block'

        #Fase 2: Pilhagem

        else:

            if defender.army != 0 and attacker.army/defender.army < consts.PILHAGE_DOMINANCERATIO:
                attacker_loss = consts.PILHAGE_BASELOSS
                defender_loss = consts.PILHAGE_BASELOSS
                mod = consts.CIVS.get(defender.civ, {}).get('mods', {}).get('pilhage_damage', 1.0)
                defender.life = int(max(0, defender.life - consts.PILHAGE_DAMAGEFACTOR*attacker.army*(1-attacker_loss)*mod))
                situation = 'pilhage'

            else:
                attacker_loss = 0
                defender_loss = 1
                defender.life = 0
                situation = 'complete_destruction'
        
        defender_is_alive = (defender.life != 0)
        attacker.army = int(attacker.army*(1-attacker_loss))
        defender.army = int(defender.army*(1-defender_loss))


        return {
            "situation" : situation,
            "is_over" : not defender_is_alive,
            "attacker_final_army" : attacker.army, 
            "attacker_loss" : attacker_loss,
            "defender_final_army" : defender.army,
            "defender_loss" : defender_loss
        }

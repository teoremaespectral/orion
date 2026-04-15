from models import Kingdom, CombatEngine
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

    def setup(self, player_civ="Teresópolis", ai_civ="Petrópolis", strategy="Aleatório"):
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
        if player_action == "attack" and ai_action == "attack":
            # Caso 1: Ambos atacam -> Campo Aberto
            engine = CombatEngine(self.player, self.ai)
            return engine.resolve(type="open_field")
            
        elif player_action == "attack":
            # Caso 2: Só jogador ataca -> Invasão à IA
            engine = CombatEngine(self.player, self.ai)
            return engine.resolve(type="invasion")
            
        elif ai_action == "attack":
            # Caso 3: Só IA ataca -> Invasão ao Jogador
            engine = CombatEngine(self.ai, self.player)
            return engine.resolve(type="invasion")

        return None
    
    def _check_victory_conditions(self):
        if self.player.life <= 0:
            self.status = "ai_won"
        elif self.ai.life <= 0:
            self.status = "player_won"
        return

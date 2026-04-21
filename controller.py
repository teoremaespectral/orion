from models import Kingdom, Bot, CombatEngine
from db_utils import get_db, save_db

class Game:
    def __init__(self, user_id, user_name):
        self.user_id = str(user_id)
        self.user_name = user_name
        self.db_data = get_db('games_data')
        
        self._load_game_data()

    def _load_game_data(self):
        '''Método privado para desafogar o init e centralizar o carregamento de dados.'''
        data = self.db_data.get(self.user_id)
        ai_data = self.db_data.get(f"{self.user_id}_ai")

        if not data:
            self._setup_new_game()
        else:
            self.turn_count = data.get('turn_count', 1)
            self.status = data.get('status', 'active')
            
            self.player_kingdom = Kingdom(self.user_id, self.user_name, data=data)
            self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Inimigo", data=ai_data['kingdom'])
            self.ai_brain = Bot(brain_data= ai_data['brain'])

    def _setup_new_game(self):
        '''Inicializa os valores para um jogo do zero.'''
        self.turn_count = 1
        self.status = "active"
        self.player_kingdom = Kingdom(self.user_id, self.user_name)
        self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Inimigo")
        self.ai_brain = Bot()
    
    def save(self):
        '''Salva o estado atual do jogo no banco de dados, incluindo os dados do jogador, da IA, o número de turnos, a estratégia da IA e a fila de táticas atual. Garante que todas as informações relevantes sejam armazenadas para que o jogo possa ser retomado posteriormente.'''
        player_data = self.player_kingdom.to_dict()
        player_data['turn_count'] = self.turn_count
        player_data['status'] = self.status

        self.db_data[self.user_id] = player_data
        self.db_data[f"{self.user_id}_ai"] = {
            'kingdom': self.ai_kingdom.to_dict(), 
            'brain': self.ai_brain.to_dict()
            }

        save_db(self.db_data, 'games_data')

    def setup(self, player_civ="Teresópolis", ai_civ="Petrópolis", strategy="Aleatório"):
        '''Configura o jogo para um novo usuário, definindo as civilizações do jogador e da IA, bem como a estratégia da IA. Garante que os reinos sejam criados com os bônus e modificadores corretos de acordo com as civilizações escolhidas. Salva o estado inicial do jogo no banco de dados.'''
        # Garante que criamos reinos limpos com a civ correta
        self.player_kingdom = Kingdom(self.user_id, self.user_name)
        self.player_kingdom.civ = player_civ
    
        self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Bot")
        self.ai_kingdom.civ = ai_civ

        self.ai_brain = Bot()
        self.ai_brain.civ = ai_civ
        self.ai_brain.personality = strategy
        self.ai_brain.name = f"Bot {ai_civ}"
        
        self.save()

    def play_turn(self, action):
        """
        Orquestra o turno:
        1. Executa ação do jogador
        2. Executa ação da IA
        3. Atacar!
        4. Produção para ambos
        """

        #O feedback do que ocorreu no turno

        # 1. Ação do Jogador
        player_action = self.process_player_turn(action)

        # 2. Turno da IA (Lógica simples por enquanto)
        ai_action = self.process_ai_turn()

        # 3. Checa se há combate
        fight_data = self.process_fight(player_action, ai_action)
    
        # 4. Produção (Turno passa para ambos)
        self.player_kingdom.produce_resources()
        self.ai_kingdom.produce_resources()

        # Salvar
        self.turn_count += 1
        self._check_victory_conditions()
        self.save()

        report = {
            "player_action": player_action,
            "ai_action": ai_action,
            "fight_data": fight_data,
        }
        return report
    
    def process_player_turn(self, action):
        a_type, a_target = action['type'], action['target']

        action['success'] = False

        if a_type == "build":
            if self.player_kingdom.build(a_target):
                action['success'] = True
        elif a_type == "research":
            if self.player_kingdom.research(a_target):
                action['success'] = True
        elif a_type == "army":
            if self.player_kingdom.train_army():
                action['success'] = True
        elif a_type == "attack":
            if self.player_kingdom.army > 0:
                action['success'] = True
        
        return action

    def process_ai_turn(self):
        """
        Gerencia a fila de táticas da IA. Se não houver plano, pede um novo 
        para a AI_logic baseado na estratégia.
        """

        ai_action = self.ai_brain.get_next_action(self.ai_kingdom).copy()
        a_type, a_target = ai_action['type'], ai_action['target']

        # 3. Tenta executar
        if a_type == "build":
            if self.ai_kingdom.build(a_target):
                ai_action['success'] = True
        elif a_type == "research":
            if self.ai_kingdom.research(a_target):
                ai_action['success'] = True
        elif a_type == "army":
            if self.ai_kingdom.train_army():
                ai_action['success'] = True
        elif a_type == "attack":
            if self.ai_kingdom.army > 0:
                ai_action['success'] = True

        return ai_action

    def process_fight(self, player_action, ai_action):
        """Simulação de combate"""
        p_true_attack = player_action['type'] == "attack" and player_action['success']
        ai_true_attack = ai_action['type'] == "attack" and ai_action['success']

        if p_true_attack and ai_true_attack:
            # Caso 1: Ambos atacam -> Campo Aberto
            engine = CombatEngine(self.player_kingdom, self.ai_kingdom)
            return engine.resolve(type="open_field")
            
        elif p_true_attack:
            # Caso 2: Só jogador ataca -> Invasão à IA
            engine = CombatEngine(self.player_kingdom, self.ai_kingdom)
            return engine.resolve(type="invasion")
            
        elif ai_true_attack:
            # Caso 3: Só IA ataca -> Invasão ao Jogador
            engine = CombatEngine(self.ai_kingdom, self.player_kingdom)
            return engine.resolve(type="invasion")

        return None
    
    def _check_victory_conditions(self):
        if self.player_kingdom.life <= 0:
            self.status = "ai_won"
        elif self.ai_kingdom.life <= 0:
            self.status = "player_won"
        return
